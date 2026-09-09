"""Disclosed HIOP authority surface for this contest app.

This is not a second HIOP kernel. It is a new, narrow adapter that applies
pre-existing HIOP effect-authority semantics:

  Narwhal  — bind actor identity
  Meerkat  — verify request + operating context
  CRUSHIA  — decide the requested effect against current authority
  Fossil   — durable evidence of request, decision, approval, execution, result

Hard rules (same as HIOP P1):
  PERMIT_WITH_APPROVAL never dispatches.
  Approval is a fact, not unlimited authority.
  After approval, CRUSHIA must decide again.
  Only a fresh PERMIT may execute.
  Permission delta stays 0.
"""
from __future__ import annotations

import hashlib
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUTO_PERMIT_MAX_CENTS = 2500  # $25.00 — $20 refund PERMITs; $750 requires approval
ACTOR_ID = "strands-ops-agent-1"
TENANT_ID = "hood-ops"


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class Fossil:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def write(self, event: dict[str, Any]) -> dict[str, Any]:
        rec = dict(event)
        rec.setdefault("receipt_id", _rid("fossil"))
        rec.setdefault("ts", _utcnow())
        rec["permission_delta"] = 0
        line = json.dumps(rec, sort_keys=True)
        rec["sha256"] = hashlib.sha256(line.encode("utf-8")).hexdigest()
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        out = [json.loads(x) for x in lines if x.strip()]
        return out[-limit:]


class HiopAuthority:
    """Narwhal → Meerkat → CRUSHIA → (gate) → Fossil."""

    def __init__(self, runtime_dir: Path):
        self.runtime_dir = Path(runtime_dir)
        self.fossil = Fossil(self.runtime_dir / "fossil.jsonl")
        self._lock = threading.Lock()
        self._spent: set[str] = set()
        self._approvals: dict[str, dict[str, Any]] = {}
        self._permits: dict[str, dict[str, Any]] = {}

    def narwhal(self, actor_id: str) -> dict[str, Any]:
        ok = actor_id == ACTOR_ID
        return {
            "engine": "Narwhal",
            "actor_id": actor_id,
            "identity_bound": ok,
            "tenant_id": TENANT_ID if ok else None,
        }

    def meerkat(self, *, tenant_id: str, customer_id: str, customer_tenant: str | None) -> dict[str, Any]:
        ctx_ok = tenant_id == TENANT_ID and customer_tenant == TENANT_ID and bool(customer_id)
        return {
            "engine": "Meerkat",
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "context_verified": ctx_ok,
            "reason": None if ctx_ok else "customer_not_in_operating_tenant",
        }

    def crushia(
        self,
        *,
        effect: str,
        amount_cents: int,
        identity: dict[str, Any],
        context: dict[str, Any],
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        if not identity.get("identity_bound"):
            outcome, reason = "DENY", "actor_identity_not_bound"
        elif not context.get("context_verified"):
            outcome, reason = "DENY", context.get("reason") or "context_unverified"
        elif effect != "issue_refund":
            outcome, reason = "DENY", "effect_not_in_policy"
        elif amount_cents <= 0:
            outcome, reason = "DENY", "non_positive_amount"
        elif amount_cents <= AUTO_PERMIT_MAX_CENTS:
            outcome, reason = "PERMIT", "within_auto_permit_ceiling"
        else:
            if approval_id and approval_id in self._approvals:
                outcome, reason = "PERMIT", "fresh_permit_after_recorded_approval"
            else:
                outcome, reason = "PERMIT_WITH_APPROVAL", "amount_exceeds_auto_permit_ceiling"

        decision_id = _rid("crushia")
        decision = {
            "engine": "CRUSHIA",
            "decision_id": decision_id,
            "effect": effect,
            "amount_cents": amount_cents,
            "outcome": outcome,
            "reason": reason,
            "approval_id": approval_id,
            "dispatches": outcome == "PERMIT",
            "permission_delta": 0,
        }
        if outcome == "PERMIT":
            token = _rid("permit")
            self._permits[token] = {
                "token": token,
                "decision_id": decision_id,
                "effect": effect,
                "amount_cents": amount_cents,
                "spent": False,
            }
            decision["permit_token"] = token
        self.fossil.write({"kind": "authority_decision", **decision})
        return decision

    def record_approval(self, *, decision_id: str, amount_cents: int, note: str) -> dict[str, Any]:
        approval_id = _rid("approval")
        rec = {
            "kind": "human_approval",
            "approval_id": approval_id,
            "prior_decision_id": decision_id,
            "amount_cents": amount_cents,
            "note": note,
            "unlimited_authority": False,
        }
        self._approvals[approval_id] = rec
        return self.fossil.write(rec)

    def execute(self, *, permit_token: str, effector) -> dict[str, Any]:
        """PERMIT-only. Token is spent before the effector runs."""
        with self._lock:
            tok = self._permits.get(permit_token)
            if not tok:
                rec = self.fossil.write(
                    {"kind": "execution_refused", "gate": "G1", "reason": "permit_token_unknown"}
                )
                return {"ok": False, "dispatched": False, "receipt": rec}
            if tok["spent"]:
                rec = self.fossil.write(
                    {"kind": "execution_refused", "gate": "G3", "reason": "permit_token_already_spent"}
                )
                return {"ok": False, "dispatched": False, "receipt": rec}
            tok["spent"] = True
            self._spent.add(permit_token)

        result = effector()
        rec = self.fossil.write(
            {
                "kind": "execution",
                "permit_token": permit_token,
                "decision_id": tok["decision_id"],
                "effect": tok["effect"],
                "amount_cents": tok["amount_cents"],
                "dispatched": True,
                "result": result,
            }
        )
        return {"ok": True, "dispatched": True, "receipt": rec, "result": result}

    def authorize_effect(
        self,
        *,
        actor_id: str,
        tenant_id: str,
        customer_id: str,
        customer_tenant: str | None,
        effect: str,
        amount_cents: int,
        approval_id: str | None = None,
    ) -> dict[str, Any]:
        identity = self.narwhal(actor_id)
        context = self.meerkat(
            tenant_id=tenant_id, customer_id=customer_id, customer_tenant=customer_tenant
        )
        decision = self.crushia(
            effect=effect,
            amount_cents=amount_cents,
            identity=identity,
            context=context,
            approval_id=approval_id,
        )
        return {
            "identity": identity,
            "context": context,
            "decision": decision,
            "permission_delta": 0,
        }
