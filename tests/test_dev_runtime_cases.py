"""DEV cases from fixtures/runtime.log. Do not invent defaults for open questions."""

from __future__ import annotations

from pathlib import Path

from northline_renewal.process import run_process

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


def _xml(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_pn_1008_success_status_a():
    result = run_process(_xml("PN-1008.xml"))

    assert result.outcome == "success"
    assert result.http_status == 200
    assert result.payload == {
        "policyNumber": "PN-1008",
        "status": "ACTIVE",
        "effectiveDate": "2026-09-01",
        "premium": 1250.0,
        "broker": {"id": "B19"},
    }
    assert "Channel" not in result.payload
    assert "channel" not in result.payload


def test_pn_1009_status_r_map_reject():
    result = run_process(_xml("PN-1009.xml"))

    assert result.outcome == "map_reject"
    assert result.policy_number == "PN-1009"
    assert result.reason == "code not in table"
    assert result.payload is None
    assert result.http_status is None


def test_pn_1010_missing_broker_id_target_422():
    result = run_process(_xml("PN-1010.xml"))

    assert result.outcome == "target_422"
    assert result.http_status == 422
    assert result.reason == "broker.id missing"
    assert result.payload is not None
    assert result.payload["policyNumber"] == "PN-1010"
    assert "broker" not in result.payload


def test_channel_is_never_mapped():
    for name in ("PN-1008.xml", "PN-1010.xml"):
        result = run_process(_xml(name))
        if result.payload is not None:
            assert "Channel" not in result.payload
            assert "channel" not in result.payload
