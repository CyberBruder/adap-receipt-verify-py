🇧🇷 [Leia em português](README.md)

# adap-receipt-verify-py

An **independent** Python verifier for ADAP authorization receipts
(`adap.receipt` v1), written from the public spec at
<https://github.com/Hardalion/agent-delegated-authority>.

**This project is not affiliated with, endorsed by, or maintained by Hardalion.**
It does not import or copy code from the reference implementation. It exists to
check that the spec is precise enough for a second implementation, in a different
language, to reach the same results.

Spec: ADAP, © Hardalion, Apache-2.0. This repository contains no code from that project.

## What it does

- RFC 8785 (JCS) canonicalization, including ECMAScript number formatting and
  UTF-16 key ordering (`adap_receipt_verify/jcs.py`)
- `contentHash` check (spec section 5)
- Ed25519 signature check (section 5, step 3)
- Hash-chain check (section 7): sequence, `prevReceiptHash`, same issuer, plus two
  optional inputs the reference verifier does not have: `expected_head` (detects a
  dropped tail) and `first_sequence` (detects a dropped head)

A receipt checked **without** a public key is never reported as valid, because the
spec says that check has not completed step 3.

## Usage

```bash
pip install cryptography pytest
python -m adap_receipt_verify examples/receipt.json --public-key MCowBQYDK2VwAyEAO3ukXVBh31tLC1HPgzy9MHlKtBOde9CTrkHYR55O3-8
python -m pytest -q
```

```python
from adap_receipt_verify import verify_receipt, verify_chain
result = verify_receipt(receipt, public_key_spki_b64url)
result.valid, result.errors
```

## Tests

28 tests: JCS vectors, a differential test against Node's `JSON.stringify` (the
ECMAScript reference), tampering, wrong key, placeholder signature, and chain
omission / reordering / dropped head / dropped tail.

See [FINDINGS.md](FINDINGS.md) for what building this turned up.

License: MIT