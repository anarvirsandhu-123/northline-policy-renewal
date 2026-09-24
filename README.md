# northline-policy-renewal

Northline Mutual, one slice: migrate BizTalk orchestration PolicyRenewalNotification to one Boomi process. Source is PolicyAdmin canonical XML. Target is POST /v2/renewals. DEV only. Do not copy secrets into the map. Leave gaps as open questions: status R, EffectiveDate timezone, empty BrokerCode, blank premium on cancellations, unmapped Channel.

## First slice (this PR)

Reviewable Boomi scaffold plus an executable map stand-in:

| Path | Role |
| --- | --- |
| `boomi/PolicyRenewalNotification.process.json` | Process graph: listen `PolicyAdmin.Renewals` → map → POST `/v2/renewals` |
| `boomi/maps/PolicyRenewal_to_BrokerNotify.map.json` | Field map (known fields only) |
| `boomi/connections/BrokerNotify-DEV.json` | DEV host only. Auth is an environment extension — **no secrets** |
| `src/northline_renewal/` | Runnable map + target stub used by unit tests |
| `fixtures/` | Logged DEV cases PN-1008 / PN-1009 / PN-1010 |
| `legacy/` | Source notes from BizTalk |
| `target/renewals-stub.md` | Required JSON for POST `/v2/renewals` |

Credentials stay in BizTalk SSO. The HTTP connection records the DEV host (`broker-notify.dev.northline.example`) and points at an environment extension. Do not put passwords, tokens, or SSO tickets in the map or this repo.

## Mapped fields

| Source | Target | Rule |
| --- | --- | --- |
| PolicyNumber | policyNumber | Direct |
| StatusCode | status | A/C/L/P → ACTIVE/CANCELLED/LAPSED/PENDING |
| EffectiveDate | effectiveDate | yyyyMMdd → date-only ISO-8601 (`yyyy-MM-dd`) |
| PremiumAmount | premium | Strip commas. Blank → `null` only when status is CANCELLED |
| BrokerCode | broker.id | Direct when present |
| Channel | *(none)* | Not mapped. Unknown fields are rejected |

## Open questions (unresolved — no defaults invented)

1. **Status code R** — Appears in DEV logs (`PN-1009`) and is not in the spec table. The map rejects with `code not in table`. Do not map R to a status until PolicyAdmin / broker-notify owners confirm.
2. **EffectiveDate timezone** — Source is `yyyyMMdd` with no zone. Target wants ISO-8601. UTC vs local is unspecified. The map emits a date-only value and does **not** append `T00:00:00` or `Z`.
3. **Empty BrokerCode** — `broker.id` is required on the target. Source is sometimes empty. No default is documented. The map omits `broker.id`; the target returns HTTP 422 (`PN-1010`).
4. **Channel** — Source values DIR / AGG / WHL. There is no target field. Channel is dropped so the API does not 422 on an unknown field.

`legacy/PolicyRenewal_to_BrokerNotify.map.json` also notes blank premium on cancellations. The target stub already allows `premium: null` only when status is CANCELLED; that rule is implemented. Whether blank should mean null vs omit vs `0` is still worth a product check if cancellations ever send non-empty junk.

## Tests

Three logged DEV cases:

| Policy | Log | Expected |
| --- | --- | --- |
| PN-1008 | `map ok` status A, premium `1,250.00`, broker B19 | SUCCESS, status ACTIVE, premium `1250.0` |
| PN-1009 | `map reject` status R | Map reject, `code not in table` |
| PN-1010 | `target 422` broker.id missing | Payload has no `broker`; HTTP 422 |

Uses the stdlib only (`unittest`). No extra packages.

```bash
python3 -m unittest discover -s tests -v
```
