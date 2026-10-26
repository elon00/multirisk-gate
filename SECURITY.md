# Security policy — local prototype

This repository is **not independently audited**, is not security-approved or deployment-ready, and contains **no cryptographic implementation** or FIPS-validated module.

## Threat boundaries

The CLI performs deterministic integer arithmetic on caller-provided basis-point inputs. It does not authenticate inputs, fetch validator data, verify oracle signatures, manage secrets, enforce any on-chain policy, or settle transactions. It cannot establish economic safety, validator solvency, collateral coverage, or live slashing exposure.

Input parser rejects missing, duplicate, unknown, non-decimal, and out-of-range values. The policy rounds loss upward to avoid underestimating fractional basis points; this does not account for correlated or adversarial risk.

## Security acceptance prerequisites

1. Specify threat model, trust boundaries, authenticated data sources, and loss semantics.
2. Implement live restaking exposure/slashing sources with signed evidence and negative tests.
3. Test adversarial and correlated-loss scenarios, replay, stale data, overflow, and outage fail-closed behavior.
4. Obtain independent review and commit-specific CI evidence before production approval.
5. Do not commit secrets, spend gas/cycles, or deploy before separate authorization.
