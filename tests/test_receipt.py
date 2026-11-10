import base64
import copy
import hashlib
import json
import pathlib

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from adap_receipt_verify import canonicalize, compute_content_hash, verify_chain, verify_receipt

EXAMPLE = pathlib.Path(__file__).parent.parent / "examples" / "receipt.json"
EXAMPLE_KEY = "MCowBQYDK2VwAyEAO3ukXVBh31tLC1HPgzy9MHlKtBOde9CTrkHYR55O3-8"


def make_key():
    priv = Ed25519PrivateKey.generate()
    der = priv.public_key().public_bytes(serialization.Encoding.DER,
                                         serialization.PublicFormat.SubjectPublicKeyInfo)
    return priv, base64.urlsafe_b64encode(der).decode().rstrip("=")


def sign_receipt(priv, body):
    body = copy.deepcopy(body)
    body["integrity"] = {"contentHash": ""}
    body["integrity"]["contentHash"] = hashlib.sha256(canonicalize(body).encode()).hexdigest()
    body["signature"] = priv.sign(canonicalize(body).encode()).hex()
    # signature is over the body without `signature`, so recompute that way
    unsigned = {k: v for k, v in body.items() if k != "signature"}
    body["signature"] = priv.sign(canonicalize(unsigned).encode()).hex()
    return body


def make_chain(n=3):
    priv, pub = make_key()
    out, prev = [], None
    for i in range(n):
        r = sign_receipt(priv, {"v": 1, "kind": "adap.receipt", "receiptId": f"r{i}",
                                "issuerKeyId": "k1", "sequence": i, "prevReceiptHash": prev})
        prev = r["integrity"]["contentHash"]
        out.append(r)
    return out, pub


def example():
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


# ---- single receipt -----------------------------------------------------
def test_example_receipt_verifies():
    r = verify_receipt(example(), EXAMPLE_KEY)
    assert r.valid, r.errors


def test_without_public_key_is_never_valid():
    r = verify_receipt(example())
    assert r.content_hash_ok and not r.signature_checked and not r.valid


def test_tampered_body_is_detected():
    rc = example()
    rc["intent"]["argsRedacted"]["amount"] = 999
    r = verify_receipt(rc, EXAMPLE_KEY)
    assert not r.valid and not r.content_hash_ok


def test_tampered_body_with_fixed_hash_still_fails_signature():
    rc = example()
    rc["intent"]["argsRedacted"]["amount"] = 999
    rc["integrity"]["contentHash"] = compute_content_hash(rc)
    r = verify_receipt(rc, EXAMPLE_KEY)
    assert r.content_hash_ok and r.signature_checked and not r.signature_ok and not r.valid


def test_placeholder_signature_is_rejected():
    rc = example()
    rc["signature"] = "ab" * 64  # what the reference emitter ships as DEMO_SIGNATURE
    assert not verify_receipt(rc, EXAMPLE_KEY).valid


def test_wrong_key_rejected():
    _, other = make_key()
    assert not verify_receipt(example(), other).valid


def test_garbage_public_key_does_not_crash():
    r = verify_receipt(example(), "not-a-key")
    assert not r.valid


# ---- chains -------------------------------------------------------------
def test_good_chain():
    chain, pub = make_chain()
    res = verify_chain(chain, pub, first_sequence=0)
    assert res.valid, res.errors
    assert res.head == chain[-1]["integrity"]["contentHash"]


def test_omitted_middle_receipt():
    chain, pub = make_chain()
    assert not verify_chain([chain[0], chain[2]], pub).valid


def test_reordered_receipts():
    chain, pub = make_chain()
    assert not verify_chain([chain[1], chain[0], chain[2]], pub).valid


def test_dropped_tail_needs_expected_head():
    chain, pub = make_chain()
    short = chain[:2]
    assert verify_chain(short, pub).valid  # the spec's documented blind spot
    assert not verify_chain(short, pub, expected_head=chain[2]["integrity"]["contentHash"]).valid


def test_dropped_head_needs_first_sequence_or_prev_hash():
    chain, pub = make_chain()
    tail = chain[1:]
    assert not verify_chain(tail, pub, prev_receipt_hash=None).valid  # first link must be null
    assert not verify_chain(tail, pub, first_sequence=0).valid
    assert verify_chain(tail, pub, prev_receipt_hash=chain[0]["integrity"]["contentHash"],
                        first_sequence=1).valid


def test_mixed_issuer():
    chain, pub = make_chain()
    chain[1]["issuerKeyId"] = "other"
    assert not verify_chain(chain, pub).valid


def test_empty_chain():
    _, pub = make_key()
    assert not verify_chain([], pub).valid
