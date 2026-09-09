"""Adversarial binding tests. Approval and PERMIT tokens are bound to one request."""
from pathlib import Path

from app.agent import bind, build_agent, unwrap
from app.hiop_adapter import HiopAuthority
from app.ledger import Ledger


def world(tmp_path: Path):
    plane = HiopAuthority(tmp_path)
    ledger = Ledger()
    bind(plane, ledger)
    return plane, ledger


def test_permit_token_cannot_issue_a_different_application(tmp_path):
    plane, _ = world(tmp_path)
    agent = build_agent()
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id="SGN-2026-01102",
            amount_cents=2000,
            reason="sign",
        )
    )
    token = auth["decision"]["permit_token"]
    stolen = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=token,
            application_id="BLD-2026-08441",
            amount_cents=2000,
        )
    )
    assert stolen["dispatched"] is False
    assert stolen["error_code"] == "permit_fingerprint_mismatch"
    assert stolen.get("result") is None


def test_permit_replay_rejected(tmp_path):
    plane, _ = world(tmp_path)
    agent = build_agent()
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id="SGN-2026-01102",
            amount_cents=2000,
            reason="sign",
        )
    )
    token = auth["decision"]["permit_token"]
    first = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=token, application_id="SGN-2026-01102", amount_cents=2000
        )
    )
    assert first["dispatched"] is True
    replay = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=token, application_id="SGN-2026-01102", amount_cents=2000
        )
    )
    assert replay["dispatched"] is False
    assert replay["error_code"] == "permit_token_already_spent"


def test_approval_for_one_application_cannot_permit_another(tmp_path):
    plane, _ = world(tmp_path)
    agent = build_agent()
    first = unwrap(
        agent.tool.request_permit_authority(
            application_id="BLD-2026-08441",
            amount_cents=760000,
            reason="commercial_building",
        )
    )
    assert first["decision"]["outcome"] == "PERMIT_WITH_APPROVAL"
    approval = unwrap(
        agent.tool.record_human_approval(
            decision_id=first["decision"]["decision_id"],
            amount_cents=760000,
            application_id="BLD-2026-08441",
        )
    )
    stolen = unwrap(
        agent.tool.request_permit_authority(
            application_id="SGN-2026-01102",
            amount_cents=760000,
            reason="sign",
            approval_id=approval["approval_id"],
        )
    )
    assert stolen["decision"]["outcome"] == "DENY"
    assert stolen["decision"]["reason"] == "approval_fingerprint_mismatch"
    assert stolen["decision"].get("permit_token") is None


def test_approval_is_not_a_permit_token(tmp_path):
    plane, _ = world(tmp_path)
    agent = build_agent()
    first = unwrap(
        agent.tool.request_permit_authority(
            application_id="BLD-2026-08441",
            amount_cents=760000,
            reason="commercial",
        )
    )
    approval = unwrap(
        agent.tool.record_human_approval(
            decision_id=first["decision"]["decision_id"],
            amount_cents=760000,
            application_id="BLD-2026-08441",
        )
    )
    bogus = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=approval["approval_id"],
            application_id="BLD-2026-08441",
            amount_cents=760000,
        )
    )
    assert bogus["dispatched"] is False
    assert bogus["error_code"] == "permit_token_unknown"


def test_wrong_amount_on_execute_rejected(tmp_path):
    plane, _ = world(tmp_path)
    agent = build_agent()
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id="SGN-2026-01102",
            amount_cents=2000,
            reason="sign",
        )
    )
    stolen = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=auth["decision"]["permit_token"],
            application_id="SGN-2026-01102",
            amount_cents=760000,
        )
    )
    assert stolen["dispatched"] is False
    assert stolen["error_code"] == "permit_fingerprint_mismatch"
