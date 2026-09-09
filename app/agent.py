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
def investigate_permit_application(request_text: str) -> dict[str, Any]:
    """Look up the building/sign permit application. Read-only. Does not issue a permit."""
    return ledger().find_application(request_text)


@tool
def request_permit_authority(
    application_id: str, amount_cents: int, reason: str, approval_id: str = ""
) -> dict[str, Any]:
    """Ask CRUSHIA whether this permit may be issued. Does not print or record the permit."""
    found = ledger().find_application(application_id)
    aid = found.get("application_id") or application_id
    auth = plane().authorize_effect(
        actor_id=ACTOR_ID,
        tenant_id=TENANT_ID,
        customer_id=found.get("applicant_id") or aid,
        customer_tenant=found.get("tenant_id"),
        effect="issue_permit",
        amount_cents=int(amount_cents),
        approval_id=approval_id or None,
        application_id=aid,
    )
    auth["application_id"] = aid
    auth["permit_type"] = found.get("permit_type")
    auth["reason"] = reason
    return auth


@tool
def record_human_approval(
    decision_id: str,
    amount_cents: int,
    note: str = "building official approved",
    application_id: str = "",
    customer_id: str = "",
) -> dict[str, Any]:
    """Record a human approval fact. This is not a permit and does not dispatch."""
    cid = customer_id
    if application_id and not cid:
        found = ledger().find_application(application_id)
        cid = found.get("applicant_id") or ""
        if not application_id or application_id != found.get("application_id"):
            application_id = found.get("application_id") or application_id
    return plane().record_approval(
        decision_id=decision_id,
        amount_cents=int(amount_cents),
        note=note,
        application_id=application_id,
        customer_id=cid,
    )


@tool
def execute_issue_permit(permit_token: str, application_id: str, amount_cents: int) -> dict[str, Any]:
    """Issue the municipal permit only if HIOP has issued a fresh PERMIT token."""

    def _do():
        return ledger().issue_permit(application_id, int(amount_cents))

    return plane().execute(
        permit_token=permit_token,
        effector=_do,
        application_id=application_id,
        amount_cents=int(amount_cents),
    )


SYSTEM = """You are the HIOP Governed Operations Agent, a Strands clerk for a building department.
Investigate the application first. Then request_permit_authority. Never claim a permit was issued unless execute_issue_permit ran.
A $7,600 commercial building permit exceeds auto-issue authority and requires human approval, then a fresh CRUSHIA PERMIT.
PERMIT_WITH_APPROVAL means stop. DENY means stop. You cannot increase your own authority. Permission delta is always 0.
"""


def build_agent() -> Agent:
    return Agent(
        model=DemoOpsModel(),
        system_prompt=SYSTEM,
        tools=[
            investigate_permit_application,
            request_permit_authority,
            record_human_approval,
            execute_issue_permit,
        ],
        name="hiop-governed-operations-agent",
        description="Strands operations clerk gated by HIOP CRUSHIA",
    )


def unwrap(val: Any) -> Any:
    """Strands tool caller returns {status, content:[{text: json}]}."""
    if not isinstance(val, dict):
        return val
    if "customer_id" in val or "application_id" in val or "decision" in val or "dispatched" in val or "approval_id" in val:
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
    inv = unwrap(agent.tool.investigate_permit_application(request_text=request_text))
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id=inv.get("application_id") or "",
            amount_cents=int(inv.get("fee_cents") or 0),
            reason=inv.get("permit_type") or "permit",
            approval_id=approval_id or "",
        )
    )
    decision = auth["decision"]
    execution = None
    if decision.get("outcome") == "PERMIT" and decision.get("permit_token"):
        execution = unwrap(
            agent.tool.execute_issue_permit(
                permit_token=decision["permit_token"],
                application_id=inv.get("application_id") or "",
                amount_cents=int(inv.get("fee_cents") or 0),
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
