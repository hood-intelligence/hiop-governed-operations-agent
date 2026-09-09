"""Strands operations clerk. Tools propose work; HIOP decides; only PERMIT executes."""
from __future__ import annotations

from typing import Any

from strands import Agent, tool

from .demo_model import DemoOpsModel
from .hiop_adapter import ACTOR_ID, TENANT_ID, HiopAuthority
from .ledger import Ledger

_plane: HiopAuthority | None = None
_ledger: Ledger | None = None


def bind(plane: HiopAuthority, ledger: Ledger) -> None:
    global _plane, _ledger
    _plane, _ledger = plane, ledger


def plane() -> HiopAuthority:
    assert _plane is not None
    return _plane


def ledger() -> Ledger:
    assert _ledger is not None
    return _ledger


@tool
def investigate_customer(request_text: str) -> dict[str, Any]:
    """Look up the customer and charges implied by the request. Read-only."""
    found = ledger().find_customer(request_text)
    return found


@tool
def request_refund_authority(
    customer_id: str, charge_id: str, amount_cents: int, reason: str, approval_id: str = ""
) -> dict[str, Any]:
    """Ask CRUSHIA whether this refund may execute. Does not move money."""
    found = ledger().find_customer(customer_id)
    auth = plane().authorize_effect(
        actor_id=ACTOR_ID,
        tenant_id=TENANT_ID,
        customer_id=customer_id,
        customer_tenant=found.get("tenant_id"),
        effect="issue_refund",
        amount_cents=int(amount_cents),
        approval_id=approval_id or None,
    )
    auth["charge_id"] = charge_id
    auth["reason"] = reason
    return auth


@tool
def record_human_approval(decision_id: str, amount_cents: int, note: str = "operator approved") -> dict[str, Any]:
    """Record a human approval fact. This is not a permit and does not dispatch."""
    return plane().record_approval(decision_id=decision_id, amount_cents=int(amount_cents), note=note)


@tool
def execute_refund(permit_token: str, charge_id: str, amount_cents: int) -> dict[str, Any]:
    """Execute a refund only if HIOP has issued a fresh PERMIT token."""

    def _do():
        return ledger().issue_refund(charge_id, int(amount_cents))

    return plane().execute(permit_token=permit_token, effector=_do)


SYSTEM = """You are the HIOP Governed Operations Agent, a Strands clerk for business ops.
Investigate first. Then request_refund_authority. Never claim you refunded unless execute_refund ran.
PERMIT_WITH_APPROVAL means stop and wait. DENY means stop. Only execute_refund after a PERMIT token.
You cannot increase your own authority. Permission delta is always 0.
"""


def build_agent() -> Agent:
    return Agent(
        model=DemoOpsModel(),
        system_prompt=SYSTEM,
        tools=[
            investigate_customer,
            request_refund_authority,
            record_human_approval,
            execute_refund,
        ],
        name="hiop-governed-operations-agent",
        description="Strands operations clerk gated by HIOP CRUSHIA",
    )


def unwrap(val: Any) -> Any:
    """Strands tool caller returns {status, content:[{text: json}]}."""
    if not isinstance(val, dict):
        return val
    if "customer_id" in val or "decision" in val or "dispatched" in val or "approval_id" in val:
        return val
    content = val.get("content")
    if isinstance(content, list) and content:
        text = content[0].get("text") if isinstance(content[0], dict) else None
        if isinstance(text, str):
            import json

            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"text": text}
    return val


def run_clerk(request_text: str, approval_id: str | None = None) -> dict[str, Any]:
    """End-to-end clerk path using Strands-registered tools."""
    agent = build_agent()
    inv = unwrap(agent.tool.investigate_customer(request_text=request_text))
    auth = unwrap(
        agent.tool.request_refund_authority(
            customer_id=inv["customer_id"],
            charge_id=inv.get("suggested_charge_id") or "",
            amount_cents=int(inv.get("suggested_refund_cents") or 0),
            reason="duplicate_charge",
            approval_id=approval_id or "",
        )
    )
    decision = auth["decision"]
    execution = None
    if decision.get("outcome") == "PERMIT" and decision.get("permit_token"):
        execution = unwrap(
            agent.tool.execute_refund(
                permit_token=decision["permit_token"],
                charge_id=inv.get("suggested_charge_id") or "",
                amount_cents=int(inv.get("suggested_refund_cents") or 0),
            )
        )
    return {
        "request": request_text,
        "investigation": inv,
        "authority": auth,
        "execution": execution,
        "permission_delta": 0,
        "strands_agent": agent.name,
        "dispatched": bool(execution and execution.get("dispatched")),
    }
