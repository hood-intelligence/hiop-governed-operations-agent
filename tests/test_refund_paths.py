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


def _tool(val):
    if isinstance(val, dict):
        return val
    if hasattr(val, "content"):
        return val
    return getattr(val, "result", val)


def test_twenty_dollar_duplicate_permits_and_dispatches(world):
    out = run_clerk("Customer Maya says we charged them twice for $20. Investigate and fix it.")
    d = out["authority"]["decision"]
    assert d["outcome"] == "PERMIT"
    assert d["amount_cents"] == 2000
    assert d["amount_cents"] <= AUTO_PERMIT_MAX_CENTS
    assert out["dispatched"] is True
    assert out["execution"]["dispatched"] is True
    assert out["permission_delta"] == 0
    assert out["execution"]["result"]["ok"] is True


def test_seven_fifty_requires_approval_and_does_not_dispatch(world):
    out = run_clerk("Customer Jordan says we charged them twice for $750. Investigate and fix it.")
    d = out["authority"]["decision"]
    assert d["outcome"] == "PERMIT_WITH_APPROVAL"
    assert d["dispatches"] is False
    assert out["dispatched"] is False
    assert out["execution"] is None
    assert out["permission_delta"] == 0


def test_unauthorized_account_denied(world):
    out = run_clerk("Unauthorized account Other Tenant LLC says we charged them twice.")
    d = out["authority"]["decision"]
    assert d["outcome"] == "DENY"
    assert out["dispatched"] is False
    assert out["permission_delta"] == 0


def test_approval_is_not_a_permit_fresh_crushia_then_execute(world):
    plane, ledger = world
    first = run_clerk("Customer Jordan says we charged them twice for $750.")
    d = first["authority"]["decision"]
    assert d["outcome"] == "PERMIT_WITH_APPROVAL"
    agent = build_agent()
    approval = unwrap(
        agent.tool.record_human_approval(
            decision_id=d["decision_id"], amount_cents=75000, note="operator approved"
        )
    )
    auth = unwrap(
        agent.tool.request_refund_authority(
            customer_id="cust_jordan",
            charge_id="ch_750b",
            amount_cents=75000,
            reason="duplicate_charge",
            approval_id=approval.get("approval_id", ""),
        )
    )
    decision = auth["decision"]
    assert decision["outcome"] == "PERMIT"
    assert decision["reason"] == "fresh_permit_after_recorded_approval"
    exe = unwrap(
        agent.tool.execute_refund(
            permit_token=decision["permit_token"], charge_id="ch_750b", amount_cents=75000
        )
    )
    assert exe["dispatched"] is True
    assert exe["result"]["ok"] is True


def test_permit_with_approval_never_dispatches_even_if_token_missing(world):
    out = run_clerk("Jordan $750 duplicate")
    assert out["authority"]["decision"].get("permit_token") is None
    assert out["execution"] is None
