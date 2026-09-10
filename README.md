# HIOP Governed Operations Agent

New Strands Agents application for the **Agents for Humans** hackathon  
**Track: Professional Agents** · Hood Intelligence, Corp. · 2026-09-09

Strands clerk investigates a **commercial building permit**. HIOP governs issuance. Only a fresh **PERMIT** executes. **PERMIT_WITH_APPROVAL never dispatches.** Permission Δ stays 0.

This is **not** Studio Cinema Control. See [DISCLOSURE.md](DISCLOSURE.md).

## Demo

```
Customer Request → Strands Agent → Narwhal → Meerkat → CRUSHIA
  → PERMIT | DENY | PERMIT_WITH_APPROVAL
  → (approval is a fact, not a permit)
  → fresh CRUSHIA
  → PERMIT → issue permit
  → Fossil evidence
```

| Request | Fee | CRUSHIA | Issued? |
|---|---|---|---|
| OTC wall sign, Harborline | **$20** | PERMIT | yes |
| Commercial building TI BLD-2026-08441 | **$7,600** | PERMIT_WITH_APPROVAL | no until official + fresh PERMIT |
| Riverside Holdings, wrong jurisdiction | $7,600 | DENY | no |

Registry is a **demo fixture**, not a live city permitting system.

Approval is bound to the exact application + amount + effect. A PERMIT token is bound to that same fingerprint. Wrong application, wrong amount, replay, or using an approval as a permit does **not** dispatch.

## Run

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8787
```

Open http://127.0.0.1:8787

**Live demo (Cloud Run, not AgentCore, not production):**  
https://hiop-governed-operations-agent-483518734142.us-central1.run.app

Rebuild that URL (optional, needs `gcloud` auth):

```powershell
.\scripts\deploy-cloud-run.ps1
```

```bash
.venv\Scripts\python -m pytest tests -q
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## License

Apache-2.0. Patents pending.

## Contact

Kenneth Wyche · founder@hoodintelligence.ai · https://hoodintelligence.ai
