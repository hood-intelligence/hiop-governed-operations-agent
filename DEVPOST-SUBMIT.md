# Agents for Humans — paste-ready Devpost fields

**Hackathon:** https://agentsforhumans.devpost.com/  
**Deadline:** 14 September 2026, 5:00pm PDT  
**Track:** Professional Agents  
**Builder ID:** add yours on the form (profile.aws.amazon.com)

Do **not** claim live city permitting, production certification, or AgentCore unless you added it.

---

## Project name

HIOP Governed Operations Agent

## Tagline (≤120 chars)

A Strands clerk for commercial building permits. CRUSHIA decides. Only a fresh PERMIT issues.

## Built with

Strands Agents SDK, Python, FastAPI, HIOP (Narwhal / Meerkat / CRUSHIA / Fossil — disclosed pre-existing)

## Track

Professional Agents

## GitHub URL

https://github.com/hood-intelligence/hiop-governed-operations-agent

(paste after the public repo exists — no trailing `|`)

## Video URL

(YouTube/Vimeo public, English, ≤5 min — paste after upload)

## Live demo (optional)

http://127.0.0.1:8787 after `uvicorn app.main:app --host 127.0.0.1 --port 8787`  
Hosted URL only if you deploy. Do not invent a URL.

## Text description (paste)

HIOP Governed Operations Agent is a new Strands Agents application for a building-department clerk.

People who issue permits still do the same loop every day: look up the application, decide if this office can issue it, stop when the fee is over auto-issue authority, wait for a building official, then issue — or refuse the wrong jurisdiction. This agent takes that loop end to end. It does not chat about permits. It investigates, asks HIOP for authority, and only prints a permit when CRUSHIA returns a fresh PERMIT.

Three real paths in the demo ledger (not a live city system):

- $20 OTC wall sign (SGN-2026-01102) → PERMIT → issues NH-SGN-2026-01102
- $7,600 commercial building TI (BLD-2026-08441, 1400 Industrial Way) → PERMIT_WITH_APPROVAL → no issue until a human approval fact and a fresh CRUSHIA PERMIT → NH-BLD-2026-08441
- Riverside Holdings, wrong jurisdiction → DENY → no issue

Hard rules: PERMIT_WITH_APPROVAL never dispatches. Approval is a fact, not unlimited authority. After approval, CRUSHIA decides again. Only a fresh PERMIT executes. Permission delta stays 0.

Approvals and PERMIT tokens are bound to the exact application, amount, and effect. Reusing a token on another application, replaying it, or treating an approval as a permit is refused and written to Fossil.

This application is new for the 2026 Agents for Humans submission period. HIOP engines (Narwhal, Meerkat, CRUSHIA, Fossil) are disclosed pre-existing components. This is not Studio Cinema Control and not a second HIOP kernel. production_certified = false.

Run: pip install -r requirements.txt && uvicorn app.main:app --host 127.0.0.1 --port 8787  
Tests: pytest tests -q

## How it works (short)

Strands Agent with four tools: investigate_permit_application, request_permit_authority, record_human_approval, execute_issue_permit. Tools propose. HIOP decides. The execution tool will not issue without a bound PERMIT token.

## Who it's for

Building officials and permit clerks who cannot let an agent auto-issue a $7,600 commercial permit the same way it issues a $20 sign.

## Why it matters

Professional agents that change records need an authority gate, not a chatbot. This shows a clerk that stops, waits for a human, then continues only with a fresh permit.

## AWS Builder ID

(your Builder ID — required)

## Additional info / disclosures

See DISCLOSURE.md in the repo. Pre-existing HIOP effect-authority semantics. New work: Strands clerk, demo permit registry, FastAPI UI, tests, fingerprint binding, packaging.
