"""PolicyRenewalNotification process runner (DEV scaffold, no live Atom)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from northline_renewal.map import MapReject, MapSuccess, map_policy_renewal
from northline_renewal.parse import parse_canonical_xml
from northline_renewal.target import post_renewal


@dataclass(frozen=True)
class ProcessResult:
    outcome: Literal["success", "map_reject", "target_422"]
    policy_number: str
    payload: dict[str, Any] | None
    reason: str | None
    http_status: int | None


def run_process(xml_text: str) -> ProcessResult:
    source = parse_canonical_xml(xml_text)
    mapped = map_policy_renewal(source)
    if isinstance(mapped, MapReject):
        return ProcessResult(
            outcome="map_reject",
            policy_number=source.policy_number,
            payload=None,
            reason=mapped.reason,
            http_status=None,
        )

    assert isinstance(mapped, MapSuccess)
    response = post_renewal(mapped.payload)
    if response.status_code == 422:
        return ProcessResult(
            outcome="target_422",
            policy_number=source.policy_number,
            payload=mapped.payload,
            reason=response.reason,
            http_status=422,
        )
    return ProcessResult(
        outcome="success",
        policy_number=source.policy_number,
        payload=mapped.payload,
        reason=None,
        http_status=response.status_code,
    )
