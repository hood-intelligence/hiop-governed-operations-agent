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
    application_id: str
    note: str = "building official approved commercial permit"


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
        "permits": "demo_registry_not_a_live_city_system",
        "headline_fee_cents": 760000,
        "engines": ["Narwhal", "Meerkat", "CRUSHIA", "Fossil"],
        "rule": "PERMIT_WITH_APPROVAL never dispatches",
    }


@app.get("/api/samples")
def samples():
    return {
        "permit": "Issue the $20 over-the-counter wall sign permit for Harborline at 1400 Industrial Way.",
        "approval": "Harborline Fabrication needs a commercial building permit for 1400 Industrial Way Building C, 8400 sf tenant improvement. Fee is $7,600. Investigate and issue it.",
        "deny": "Riverside Holdings wants a commercial building permit in this jurisdiction. Unauthorized. Investigate and issue it.",
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
            decision_id=body.decision_id,
            amount_cents=body.amount_cents,
            note=body.note,
            application_id=body.application_id,
        )
    )
    auth = unwrap(
        agent.tool.request_permit_authority(
            application_id=body.application_id,
            amount_cents=body.amount_cents,
            reason="commercial_building",
            approval_id=approval.get("approval_id") or "",
        )
    )
    execution = None
    decision = auth.get("decision") or {}
    if decision.get("outcome") == "PERMIT" and decision.get("permit_token"):
        execution = unwrap(
            agent.tool.execute_issue_permit(
                permit_token=decision["permit_token"],
                application_id=body.application_id,
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
