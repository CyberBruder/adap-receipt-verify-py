"""python -m adap_receipt_verify receipt.json --public-key SPKI_B64URL"""
import argparse
import json
import sys

from .verify import verify_receipt


def main(argv=None):
    p = argparse.ArgumentParser(prog="adap_receipt_verify")
    p.add_argument("receipt")
    p.add_argument("--public-key", help="issuer Ed25519 public key, base64url SPKI")
    a = p.parse_args(argv)
    with open(a.receipt, encoding="utf-8") as f:
        receipt = json.load(f)
    res = verify_receipt(receipt, a.public_key)
    print("contentHash ok  :", res.content_hash_ok)
    print("signature checked:", res.signature_checked)
    print("signature ok    :", res.signature_ok)
    for e in res.errors:
        print("error:", e)
    if not a.public_key:
        print("NOTE: no --public-key given, so the result is NOT valid (section 5 step 3 incomplete)")
    return 0 if res.valid else 1


if __name__ == "__main__":
    sys.exit(main())
