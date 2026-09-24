"""Parse PolicyAdmin canonical XML. Channel is read so callers can prove it is dropped."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyRenewal:
    policy_number: str
    status_code: str
    effective_date: str
    premium_amount: str
    broker_code: str
    channel: str


def parse_canonical_xml(xml_text: str) -> PolicyRenewal:
    root = ET.fromstring(xml_text)
    return PolicyRenewal(
        policy_number=_text(root, "PolicyNumber"),
        status_code=_text(root, "StatusCode"),
        effective_date=_text(root, "EffectiveDate"),
        premium_amount=_text(root, "PremiumAmount"),
        broker_code=_text(root, "BrokerCode"),
        channel=_text(root, "Channel"),
    )


def _text(root: ET.Element, tag: str) -> str:
    node = root.find(tag)
    if node is None or node.text is None:
        return ""
        return node.text.strip()
