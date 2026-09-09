"""Demo ledger. Not live payments. In-memory duplicate-charge fixtures."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .hiop_adapter import TENANT_ID

# Seeded duplicate charges. Unauthorized customer lives on another tenant.
_SEED: list[dict[str, Any]] = [
    {
        "charge_id": "ch_20a",
        "customer_id": "cust_maya",
        "customer_name": "Maya Chen",
        "tenant_id": TENANT_ID,
        "amount_cents": 2000,
        "status": "captured",
        "note": "monthly seat",
    },
    {
        "charge_id": "ch_20b",
        "customer_id": "cust_maya",
        "customer_name": "Maya Chen",
        "tenant_id": TENANT_ID,
        "amount_cents": 2000,
        "status": "captured",
        "note": "duplicate monthly seat",
    },
    {
        "charge_id": "ch_750a",
        "customer_id": "cust_jordan",
        "customer_name": "Jordan Hale",
        "tenant_id": TENANT_ID,
        "amount_cents": 75000,
        "status": "captured",
        "note": "annual contract",
    },
    {
        "charge_id": "ch_750b",
        "customer_id": "cust_jordan",
        "customer_name": "Jordan Hale",
        "tenant_id": TENANT_ID,
        "amount_cents": 75000,
        "status": "captured",
        "note": "duplicate annual contract",
    },
    {
        "charge_id": "ch_x",
        "customer_id": "cust_other",
        "customer_name": "Other Tenant LLC",
        "tenant_id": "not-hood-ops",
        "amount_cents": 2000,
        "status": "captured",
        "note": "foreign tenant",
    },
]


class Ledger:
    def __init__(self):
        self.charges = deepcopy(_SEED)
        self.refunds: list[dict[str, Any]] = []

    def find_customer(self, query: str) -> dict[str, Any] | None:
        q = query.lower()
        mapping = [
            ("unauthorized", "cust_other"),
            ("wrong account", "cust_other"),
            ("other tenant", "cust_other"),
            ("cust_other", "cust_other"),
            ("jordan", "cust_jordan"),
            ("750", "cust_jordan"),
            ("maya", "cust_maya"),
            ("$20", "cust_maya"),
            (" 20", "cust_maya"),
            ("twice", "cust_maya"),
            ("double", "cust_maya"),
        ]
        cid = None
        for k, v in mapping:
            if k in q:
                cid = v
                break
        if cid is None:
            cid = "cust_unknown"
        rows = [c for c in self.charges if c["customer_id"] == cid]
        if not rows:
            return {
                "customer_id": cid,
                "customer_name": None,
                "tenant_id": None,
                "charges": [],
                "duplicate": False,
            }
        captured = [c for c in rows if c["status"] == "captured"]
        return {
            "customer_id": cid,
            "customer_name": rows[0]["customer_name"],
            "tenant_id": rows[0]["tenant_id"],
            "charges": rows,
            "duplicate": len(captured) >= 2,
            "suggested_refund_cents": captured[-1]["amount_cents"] if captured else 0,
            "suggested_charge_id": captured[-1]["charge_id"] if captured else None,
        }

    def issue_refund(self, charge_id: str, amount_cents: int) -> dict[str, Any]:
        charge = next((c for c in self.charges if c["charge_id"] == charge_id), None)
        if not charge:
            return {"ok": False, "error": "charge_not_found"}
        if charge["status"] == "refunded":
            return {"ok": False, "error": "already_refunded"}
        charge["status"] = "refunded"
        rec = {
            "refund_id": f"re_{charge_id}",
            "charge_id": charge_id,
            "amount_cents": amount_cents,
            "status": "refunded",
        }
        self.refunds.append(rec)
        return {"ok": True, **rec}
