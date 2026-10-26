# Multirisk Gate — local restaking risk policy prototype

This repository now contains a **real, deterministic local loss-threshold policy CLI**, but it is **not a production restaking risk monitor**, a validator oracle, an on-chain contract, or a security-certified system. No live RPC, PQC, treasury, slashing event, x402 or deployment integration has been implemented or verified.

## Local policy and scope

The CLI accepts exposure to restaking, assumed slashing severity, and maximum acceptable loss, each in integer basis points (0–10,000). It computes a conservative ceiling of exposure × slash / 10,000, then emits ALLOW when the estimated loss is at or below the threshold, otherwise BLOCK. This is a **single-scenario arithmetic threshold**, not a probabilistic risk model or financial advice.

Example (local only):

    cargo run -- --exposure-bps 7500 --slash-bps 1000 --max-loss-bps 800

Expected output includes LOSS_BPS=750 and POLICY_DECISION=ALLOW. Invalid, missing, duplicated, negative, and out-of-range inputs fail closed with exit status 2. A valid BLOCK is a decision, not a process error.

## Real regression gates

    cargo test --all-targets
    python -m compileall -q tests
    python -m unittest discover -s tests -p 'reality_*.py' -v

Tests execute the actual Rust CLI and compare outcomes against independently stated expected cases, including malformed input. Python CodeQL is configured separately. Passing these checks establishes only local policy behavior at the tested commit, **not security approval**.

## Unimplemented and required acceptance

No chain state, operator exposure feed, validator identity attestation, correlated slashing analysis, liquidity risk, withdrawal delay, price oracle, audit, or production monitoring is present. Real implementations must be specified, threat-modeled, independently reviewed and tested against adversarial live-data scenarios before any production claims.

The approved QMOOSA-1000 manifest requests private repositories; this repository is currently public. Visibility was not changed. Owner review is required before any sensitive information is added.

Status: IMPLEMENTATION=PARTIAL_LOCAL_POLICY; SECURITY_APPROVED=NO; DEPLOYMENT_READY=NO.
