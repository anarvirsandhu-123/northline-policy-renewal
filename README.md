# northline-policy-renewal

Northline Mutual, one slice: migrate BizTalk orchestration PolicyRenewalNotification to one Boomi process. Source is PolicyAdmin canonical XML. Target is POST /v2/renewals. DEV only. Do not copy secrets into the map. Leave gaps as open questions: status R, EffectiveDate timezone, empty BrokerCode, blank premium on cancellations, unmapped Channel.
