"""PolicyRenewal_to_BrokerNotify map (canonical XML fields → POST /v2/renewals JSON).

Known fields only. Open questions are left unresolved — no invented defaults.
See boomi/maps/PolicyRenewal_to_BrokerNotify.map.json.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from northline_renewal.parse import PolicyRenewal

# Spec table only. Code R appears in DEV logs (PN-1009) and is not listed.
# OPEN QUESTION status-R: do not invent ACTIVE/REJECTED/other. Reject until owners confirm.
STATUS_TABLE = {
    "A": "ACTIVE",
    "C": "CANCELLED",
    "L": "LAPSED",
    "P": "PENDING",
}

_YYYYMMDD = re.compile(r"^\d{8}$")


@dataclass(frozen=True)
class MapSuccess:
    payload: dict[str, Any]


@dataclass(frozen=True)
class MapReject:
    reason: str
    policy_number: str


MapResult = MapSuccess | MapReject


def map_policy_renewal(source: PolicyRenewal) -> MapResult:
    status = _map_status(source.status_code)
    if isinstance(status, MapReject):
        return MapReject(reason=status.reason, policy_number=source.policy_number)

    premium = _map_premium(source.premium_amount, status)
    if isinstance(premium, MapReject):
        return MapReject(reason=premium.reason, policy_number=source.policy_number)

    effective_date = _map_effective_date(source.effective_date)
    if isinstance(effective_date, MapReject):
        return MapReject(reason=effective_date.reason, policy_number=source.policy_number)

    payload: dict[str, Any] = {
        "policyNumber": source.policy_number,
        "status": status,
        "effectiveDate": effective_date,
        "premium": premium,
    }

    # OPEN QUESTION empty-BrokerCode: required on target; no default documented.
    # Omit broker.id when BrokerCode is empty. Target returns 422 (PN-1010).
    broker_id = source.broker_code.strip()
    if broker_id:
        payload["broker"] = {"id": broker_id}

    # OPEN QUESTION Channel: values DIR/AGG/WHL. No target field.
    # Unknown fields are rejected — do not map source.channel.
    return MapSuccess(payload=payload)


def _map_status(code: str) -> str | MapReject:
    mapped = STATUS_TABLE.get(code)
    if mapped is None:
        return MapReject(reason="code not in table", policy_number="")
    return mapped


def _map_premium(raw: str, status: str) -> float | None | MapReject:
    stripped = raw.replace(",", "").strip()
    if stripped == "":
        # Target stub: premium is nullable only when status is CANCELLED.
        if status == "CANCELLED":
            return None
        return MapReject(reason="blank premium not allowed", policy_number="")
    try:
        return float(stripped)
    except ValueError:
        return MapReject(reason="premium is not a number", policy_number="")


def _map_effective_date(raw: str) -> str | MapReject:
    """yyyyMMdd → ISO-8601 date.

    OPEN QUESTION effectiveDate-timezone: UTC vs local is unspecified.
    Emit date-only (yyyy-MM-dd). Do not append T00:00:00 or Z.
    """
    value = raw.strip()
    if not _YYYYMMDD.match(value):
        return MapReject(reason="EffectiveDate is not yyyyMMdd", policy_number="")
    try:
        parsed = datetime.strptime(value, "%Y%m%d")
    except ValueError:
        return MapReject(reason="EffectiveDate is not yyyyMMdd", policy_number="")
    return parsed.strftime("%Y-%m-%d")
