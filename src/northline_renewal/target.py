"""DEV stand-in for POST /v2/renewals (target/renewals-stub.md). No live HTTP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ALLOWED_STATUS = frozenset({"ACTIVE", "CANCELLED", "LAPSED", "PENDING"})


@dataclass(frozen=True)
class TargetResponse:
    status_code: int
    reason: str | None = None


def post_renewal(payload: dict[str, Any]) -> TargetResponse:
    unknown = set(payload) - {"policyNumber", "status", "effectiveDate", "premium", "broker"}
    if unknown:
        return TargetResponse(status_code=422, reason=f"unknown fields: {sorted(unknown)}")

    if not payload.get("policyNumber"):
        return TargetResponse(status_code=422, reason="policyNumber missing")
    if payload.get("status") not in ALLOWED_STATUS:
        return TargetResponse(status_code=422, reason="status not allowed")
    if not payload.get("effectiveDate"):
        return TargetResponse(status_code=422, reason="effectiveDate missing")

    status = payload["status"]
    if "premium" not in payload:
        return TargetResponse(status_code=422, reason="premium missing")
    premium = payload["premium"]
    if premium is None and status != "CANCELLED":
        return TargetResponse(status_code=422, reason="premium nullable only when CANCELLED")
    if premium is not None and not isinstance(premium, (int, float)):
        return TargetResponse(status_code=422, reason="premium must be a number")

    broker = payload.get("broker")
    broker_id = broker.get("id") if isinstance(broker, dict) else None
    if not broker_id:
        # Matches fixtures/runtime.log PN-1010.
        return TargetResponse(status_code=422, reason="broker.id missing")

    return TargetResponse(status_code=200)
