# Event Collapse Map – Decision Authority

## Canonical Authority
- decision.finalised

## Inputs Only (Never Authoritative)
- risk.assessed
- match_completed
- embeddings_ready
- policy.applied
- credit_scored
- aml_checked

## Collapsed Into decision.finalised
- risk evaluation
- policy application
- decision recommendation
- evidence references

## Downstream (References decision_id)
- settlement.authorized
- settlement.blocked
- override.applied (emits new decision.finalised)
