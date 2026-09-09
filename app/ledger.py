"""Demo building-permit registry. Not a live city system."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from .hiop_adapter import TENANT_ID

_SEED: list[dict[str, Any]] = [
    {
        "application_id": "BLD-2026-08441",
        "applicant_id": "app_harborline",
        "applicant_name": "Harborline Fabrication LLC",
        "tenant_id": TENANT_ID,
        "permit_type": "commercial_building",
        "address": "1400 Industrial Way, Building C, North Harbor",
        "occupancy": "B — Business / light manufacturing + office",
        "scope": "8,400 sf tenant improvement; new demising walls, HVAC, and 3-phase service",
        "valuation_cents": 38000000,
        "fee_cents": 760000,
        "status": "fee_due",
        "permit_number": None,
    },
    {
        "application_id": "SGN-2026-01102",
        "applicant_id": "app_harborline",
        "applicant_name": "Harborline Fabrication LLC",
        "tenant_id": TENANT_ID,
        "permit_type": "wall_sign_otc",
        "address": "1400 Industrial Way, Building C, North Harbor",
        "occupancy": "B",
        "scope": "24 sq ft non-illuminated wall sign",
        "valuation_cents": 180000,
        "fee_cents": 2000,
        "status": "fee_due",
        "permit_number": None,
    },
    {
        "application_id": "BLD-2026-99999",
        "applicant_id": "app_riverside",
        "applicant_name": "Riverside Holdings",
        "tenant_id": "other-jurisdiction",
        "permit_type": "commercial_building",
        "address": "88 River Rd (outside North Harbor)",
        "occupancy": "F-1",
        "scope": "warehouse addition",
        "valuation_cents": 12000000,
        "fee_cents": 760000,
        "status": "fee_due",
        "permit_number": None,
    },
]


class Ledger:
    def __init__(self):
        self.applications = deepcopy(_SEED)
        self.issued: list[dict[str, Any]] = []

    def find_application(self, query: str) -> dict[str, Any]:
        exact = next((a for a in self.applications if a["application_id"] == query), None)
        if exact:
            return dict(exact)
        q = query.lower()
        aid = None
        mapping = [
            ("riverside", "BLD-2026-99999"),
            ("unauthorized", "BLD-2026-99999"),
            ("wrong jurisdiction", "BLD-2026-99999"),
            ("outside", "BLD-2026-99999"),
            ("sign", "SGN-2026-01102"),
            ("otc", "SGN-2026-01102"),
            ("$20", "SGN-2026-01102"),
            ("7600", "BLD-2026-08441"),
            ("7,600", "BLD-2026-08441"),
            ("$7,600", "BLD-2026-08441"),
            ("commercial", "BLD-2026-08441"),
            ("building permit", "BLD-2026-08441"),
            ("industrial way", "BLD-2026-08441"),
            ("harborline", "BLD-2026-08441"),
            ("bld-2026-08441", "BLD-2026-08441"),
        ]
        for k, v in mapping:
            if k in q:
                aid = v
                break
        if aid is None:
            aid = "BLD-UNKNOWN"
        row = next((a for a in self.applications if a["application_id"] == aid), None)
        if not row:
            return {
                "application_id": aid,
                "applicant_id": "unknown",
                "applicant_name": None,
                "tenant_id": None,
                "permit_type": None,
                "fee_cents": 0,
                "status": "not_found",
            }
        return dict(row)

    def issue_permit(self, application_id: str, amount_cents: int) -> dict[str, Any]:
        app = next((a for a in self.applications if a["application_id"] == application_id), None)
        if not app:
            return {"ok": False, "error": "application_not_found"}
        if app["status"] == "issued":
            return {"ok": False, "error": "already_issued"}
        if int(amount_cents) != int(app["fee_cents"]):
            return {"ok": False, "error": "fee_mismatch"}
        number = f"NH-{application_id}"
        app["status"] = "issued"
        app["permit_number"] = number
        rec = {
            "ok": True,
            "permit_number": number,
            "application_id": application_id,
            "permit_type": app["permit_type"],
            "address": app["address"],
            "fee_cents": amount_cents,
            "status": "issued",
            "note": "Demo issuance. Not a live municipal permit.",
        }
        self.issued.append(rec)
        return rec
