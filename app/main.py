"""HIOP Governed Operations Agent — FastAPI demo surface."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from .agent import bind, run_clerk
from .hiop_adapter import ACTOR_ID, TENANT_ID, HiopAuthority
from .ledger import Ledger

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime"
STATIC = Path(__file__).resolve().parent / "static"

plane = HiopAuthority(RUNTIME)
ledger = Ledger()
bind(plane, ledger)

app = FastAPI(title="HIOP Governed Operations Agent", version="2026.09.09")


class RunBody(BaseModel):
    request: str = Field(..., min_length=3)


class ApproveBody(BaseModel):
    decision_id: str
    amount_cents: int
    customer_id: str
    charge_id: str
    note: str = "operator approved"


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/runtime")
def runtime():
    return {
        "product": "HIOP Governed Operations Agent",
        "track": "Professional Agents",
        "hackathon": "Agents for Humans 2026",
        "strands": True,
        "actor_id": ACTOR_ID,
        "tenant_id": TENANT_ID,
        "permission_delta": 0,
        "production_certified": False,
        "payments": "demo_ledger_not_live_money",
        "engines": ["Narwhal", "Meerkat", "CRUSHIA", "Fossil"],
        "rule": "PERMIT_WITH_APPROVAL never dispatches",
    }


@app.get("/api/samples")
def samples():
    return {
        "permit": "Customer Maya says we charged them twice for $20. Investigate and fix it.",
        "approval": "Customer Jordan says we charged them twice for $750. Investigate and fix it.",
        "deny": "Unauthorized account Other Tenant LLC says we charged them twice. Investigate and fix it.",
    }


@app.post("/api/run")
def run(body: RunBody):
    return run_clerk(body.request)


@app.post("/api/approve-and-retry")
def approve_and_retry(body: ApproveBody):
    from .agent import build_agent, unwrap

    agent = build_agent()
    approval = unwrap(
        agent.tool.record_human_approval(
            decision_id=body.decision_id, amount_cents=body.amount_cents, note=body.note
        )
    )
    auth = unwrap(
        agent.tool.request_refund_authority(
            customer_id=body.customer_id,
            charge_id=body.charge_id,
            amount_cents=body.amount_cents,
            reason="duplicate_charge",
            approval_id=approval.get("approval_id") or "",
        )
    )
    execution = None
    decision = auth.get("decision") or {}
    if decision.get("outcome") == "PERMIT" and decision.get("permit_token"):
        execution = unwrap(
            agent.tool.execute_refund(
                permit_token=decision["permit_token"],
                charge_id=body.charge_id,
                amount_cents=body.amount_cents,
            )
        )
    return {
        "approval": approval,
        "fresh_authority": auth,
        "execution": execution,
        "permission_delta": 0,
        "note": "Approval is a fact. CRUSHIA decided again. Only the fresh PERMIT dispatched.",
    }


@app.get("/api/fossil")
def fossil():
    return {"receipts": plane.fossil.list(80), "permission_delta": 0}


@app.get("/healthz")
def healthz():
    return JSONResponse({"ok": True, "permission_delta": 0})


@app.post("/api/reset")
def reset():
    global plane, ledger
    if RUNTIME.exists():
        for p in RUNTIME.glob("*"):
            p.unlink()
    plane = HiopAuthority(RUNTIME)
    ledger = Ledger()
    bind(plane, ledger)
    return {"ok": True}
