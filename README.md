# HIOP Governed Operations Agent

New Strands Agents application for the **Agents for Humans** hackathon  
**Track: Professional Agents** · Hood Intelligence, Corp. · 2026-09-09

Strands clerk investigates a customer ops request. HIOP governs the consequential action. Only a fresh **PERMIT** executes. **PERMIT_WITH_APPROVAL never dispatches.** Permission Δ stays 0.

This is **not** Studio Cinema Control. See [DISCLOSURE.md](DISCLOSURE.md).

## Demo

```
Customer Request → Strands Agent → Narwhal → Meerkat → CRUSHIA
  → PERMIT | DENY | PERMIT_WITH_APPROVAL
  → (approval is a fact, not a permit)
  → fresh CRUSHIA
  → PERMIT → refund
  → Fossil evidence
```

| Request | CRUSHIA | Money moved? |
|---|---|---|
| Maya charged twice **$20** | PERMIT | yes |
| Jordan charged twice **$750** | PERMIT_WITH_APPROVAL | no until fresh PERMIT |
| Other Tenant LLC | DENY | no |

Ledger is a **demo fixture**, not live card-network money.

## Run

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8787
```

Open http://127.0.0.1:8787

```bash
.venv\Scripts\python -m pytest tests -q
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## License

Apache-2.0. Patents pending.

## Contact

Kenneth Wyche · founder@hoodintelligence.ai · https://hoodintelligence.ai
