POST /v2/renewals
Required JSON: policyNumber (string), status (ACTIVE, CANCELLED, LAPSED, PENDING), effectiveDate (ISO-8601), premium (number, nullable only when status is CANCELLED), broker.id (string).
Unknown fields are rejected. HTTP 422 when broker.id is missing.
