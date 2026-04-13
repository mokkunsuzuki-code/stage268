# Stage268 Verification Score

Stage268 computes a deterministic trust score from four dimensions:

- Time Trust
- Integrity Trust
- Execution Trust
- Identity Trust

**Total Trust:** `0.25`

## Component Scores

- **Time Trust:** `0.25`  (bitcoin-evidence-found-but-confirmations-not-parsed)
- **Integrity Trust:** `1.0`  (sha256:yes, ots:yes)
- **Execution Trust:** `1.0`  (workflows:yes, ci_evidence:yes)
- **Identity Trust:** `1.0`  (signatures:yes, public_keys:yes, multi_signer:yes)

## Formula

`Total Trust = Time × Integrity × Execution × Identity`

## Important Meaning

- This is **not** a claim of absolute security.
- This is a **reproducible trust index** based on detected evidence.
- If one component is weak, Total Trust drops multiplicatively.

