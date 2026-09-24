"""DEV cases from fixtures/runtime.log. Do not invent defaults for open questions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from northline_renewal.process import run_process  # noqa: E402

FIXTURES = ROOT / "fixtures"


def _xml(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class DevRuntimeCases(unittest.TestCase):
    def test_pn_1008_success_status_a(self):
        result = run_process(_xml("PN-1008.xml"))

        self.assertEqual(result.outcome, "success")
        self.assertEqual(result.http_status, 200)
        self.assertEqual(
            result.payload,
            {
                "policyNumber": "PN-1008",
                "status": "ACTIVE",
                "effectiveDate": "2026-09-01",
                "premium": 1250.0,
                "broker": {"id": "B19"},
            },
        )
        assert result.payload is not None
        self.assertNotIn("Channel", result.payload)
        self.assertNotIn("channel", result.payload)

    def test_pn_1009_status_r_map_reject(self):
        result = run_process(_xml("PN-1009.xml"))

        self.assertEqual(result.outcome, "map_reject")
        self.assertEqual(result.policy_number, "PN-1009")
        self.assertEqual(result.reason, "code not in table")
        self.assertIsNone(result.payload)
        self.assertIsNone(result.http_status)

    def test_pn_1010_missing_broker_id_target_422(self):
        result = run_process(_xml("PN-1010.xml"))

        self.assertEqual(result.outcome, "target_422")
        self.assertEqual(result.http_status, 422)
        self.assertEqual(result.reason, "broker.id missing")
        self.assertIsNotNone(result.payload)
        assert result.payload is not None
        self.assertEqual(result.payload["policyNumber"], "PN-1010")
        self.assertNotIn("broker", result.payload)

    def test_channel_is_never_mapped(self):
        for name in ("PN-1008.xml", "PN-1010.xml"):
            result = run_process(_xml(name))
            if result.payload is not None:
                self.assertNotIn("Channel", result.payload)
                self.assertNotIn("channel", result.payload)


if __name__ == "__main__":
    unittest.main()
