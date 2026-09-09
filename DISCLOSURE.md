# Pre-existing components (disclosed)

This repository is a **new** application created on 2026-09-09 for the
Amazon / Devpost **Agents for Humans** hackathon (Professional Agents track).

It is **not** Studio Cinema Control, **not** a resubmit of an existing HIOP
product UI, and **not** a second HIOP kernel or console.

## What is new (built during the submission period)

- Strands Agents SDK operations clerk (`app/agent.py`)
- Demo commercial-permit registry (`app/ledger.py`)
- FastAPI + operator UI (`app/main.py`, `app/static/index.html`)
- Deterministic Strands model provider for offline demo (`app/demo_model.py`)
- This contest packaging, architecture diagram, and tests

## What is pre-existing (disclosed, reused as semantics)

HIOP product engines and effect-authority rules that predate this hackathon:

| Engine | Role in this app |
|---|---|
| Narwhal | Actor identity bind |
| Meerkat | Request + tenant context verify |
| CRUSHIA | Effect authority decision |
| Fossil | Durable evidence |

Hard rules copied from HIOP P1 effect-authority (not invented here):

- `PERMIT_WITH_APPROVAL` **never** dispatches
- Human approval is a **fact**, not unlimited authority
- After approval, CRUSHIA must issue a **fresh** decision
- Only a fresh `PERMIT` may execute
- Permission delta remains **0**

Source-of-truth references (local Hood tree, not this repo):

- `HIOP-COMPLETION-P1-RC3-2026-09-01`
- `HIOP-P1-SELECTION-GRADE-PRODUCT-RC1` `p1_pilot/execution_gate.py`

`app/hiop_adapter.py` is a **new narrow adapter** implementing those published
rules for this commercial building-permit clerk. It is not a replacement HIOP platform.

## What this demo does not claim

- Not a live municipal permitting system or live card-network money movement
- Not Amazon Bedrock AgentCore (optional; not configured in this package)
- Not `production_certified`
- Not a second Console or second HIOP
