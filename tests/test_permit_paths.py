from pathlib import Path

import pytest

from app.agent import bind, build_agent, run_clerk, unwrap
from app.hiop_adapter import AUTO_PERMIT_MAX_CENTS, HiopAuthority
from app.ledger import Ledger


@pytest.fixture
def world(tmp_path: Path):
    plane = HiopAuthority(tmp_path)
    ledger = Ledger()
    bind(plane, ledger)
    return plane, ledger


def test_twenty_dollar_sign_permits_and_issues(world):
    out = run_clerk("Issue the $20 over-the-counter wall sign permit for Harborline at 1400 Industrial Way.")
    d = out["authority"]["decision"]
    assert d["outcome"] == "PERMIT"
    assert d["amount_cents"] == 2000
    assert d["amount_cents"] <= AUTO_PERMIT_MAX_CENTS
    assert out["dispatched"] is True
    assert out["execution"]["result"]["permit_number"].startswith("NH-SGN")
    assert out["permission_delta"] == 0


def test_commercial_7600_requires_approval_and_does_not_issue(world):
    out = run_clerk(
        "Harborline Fabrication needs a commercial building permit for 1400 Industrial Way Building C. Fee is $7,600."
    )
    d = out["authority"]["decision"]
    assert d["outcome"] == "PERMIT_WITH_APPROVAL"
    assert d["amount_cents"] == 760000
    assert d["dispatches"] is False
    assert out["dispatched"] is False
    assert out["execution"] is None
    assert out["investigation"]["application_id"] == "BLD-2026-08441"
    assert out["permission_delta"] == 0


def test_wrong_jurisdiction_denied(world):
    out = run_clerk("Riverside Holdings wants a commercial building permit. Unauthorized. Wrong jurisdiction.")
    d = out["authority"]["decision"]
    assert d["outcome"] == "DENY"
    assert out["dispatched"] is False
    assert out["permission_delta"] == 0


def test_approval_then_fresh_crushia_issues_commercial_permit(world):
    first = run_clerk("commercial building permit $7600 Harborline Industrial Way")
    d = first["authority"]["decision"]
    assert d["outcome"] == "PERMIT_WITH_APPROVAL"
    agent = build_agent()
    approval = unwrap(
        agent.tool.record_human_approval(
            decision_id=d["decision_id"], amount_cents=760000, note="building official approved"
        )
    )
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id="BLD-2026-08441",
            amount_cents=760000,
            reason="commercial_building",
            approval_id=approval.get("approval_id", ""),
        )
    )
    decision = auth["decision"]
    assert decision["outcome"] == "PERMIT"
    assert decision["reason"] == "fresh_permit_after_recorded_approval"
    exe = unwrap(
        agent.tool.execute_issue_permit(
            permit_token=decision["permit_token"],
            application_id="BLD-2026-08441",
            amount_cents=760000,
        )
    )
    assert exe["dispatched"] is True
    assert exe["result"]["ok"] is True
    assert exe["result"]["permit_number"] == "NH-BLD-2026-08441"
    assert exe["result"]["fee_cents"] == 760000


def test_permit_with_approval_never_dispatches(world):
    out = run_clerk("commercial building $7,600")
    assert out["authority"]["decision"].get("permit_token") is None
    assert out["execution"] is None
