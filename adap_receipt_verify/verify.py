"""Verification of adap.receipt v1 (spec section 5) and of receipt chains (section 7)."""
import base64
import binascii
import hashlib
import re
from dataclasses import dataclass, field

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .jcs import canonicalize

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX_SIG = re.compile(r"^[0-9a-fA-F]{128}$")


@dataclass
class VerifyResult:
    content_hash_ok: bool = False
    signature_checked: bool = False  # False means section 5 step 3 was NOT completed
    signature_ok: bool = False
    errors: list = field(default_factory=list)

    @property
    def valid(self):
        """True only if the hash matches AND the signature was checked and good."""
        return self.content_hash_ok and self.signature_checked and self.signature_ok and not self.errors


@dataclass
class ChainResult:
    valid: bool
    errors: list
    head: str | None = None  # contentHash of the last receipt presented


def _unsigned(receipt):
    body = {k: v for k, v in receipt.items() if k != "signature"}
    return body


def compute_content_hash(receipt):
    """SHA-256 over the canonical body with integrity.contentHash set to ''."""
    body = _unsigned(receipt)
    body["integrity"] = dict(body.get("integrity") or {}, contentHash="")
    return hashlib.sha256(canonicalize(body).encode("utf-8")).hexdigest()


def load_public_key(spki_b64url):
    """Load an Ed25519 public key from base64url SPKI (DER). Raises ValueError if unusable."""
    try:
        der = base64.urlsafe_b64decode(spki_b64url + "=" * (-len(spki_b64url) % 4))
        key = load_der_public_key(der)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"invalid public key: {e}") from None
    if not isinstance(key, Ed25519PublicKey):
        raise ValueError("public key is not Ed25519")
    return key


def verify_receipt(receipt, public_key_spki=None):
    """Verify one receipt. Without public_key_spki the signature is NOT checked and
    the result is never `valid` (a check without the key has not completed step 3)."""
    r = VerifyResult()
    try:
        if receipt.get("kind") != "adap.receipt" or receipt.get("v") != 1:
            r.errors.append("kind must be adap.receipt and v must be 1")
        stored = (receipt.get("integrity") or {}).get("contentHash")
        if not isinstance(stored, str) or not HEX64.match(stored):
            r.errors.append("integrity.contentHash must be 64 lowercase hex chars")
        sig = receipt.get("signature")
        if not isinstance(sig, str) or not HEX_SIG.match(sig):
            r.errors.append("signature must be 128 hex chars")
        if r.errors:
            return r
        r.content_hash_ok = compute_content_hash(receipt) == stored
        if not r.content_hash_ok:
            r.errors.append("contentHash does not match the body")
        if public_key_spki is not None:
            key = load_public_key(public_key_spki)
            r.signature_checked = True
            try:
                key.verify(bytes.fromhex(sig), canonicalize(_unsigned(receipt)).encode("utf-8"))
                r.signature_ok = True
            except InvalidSignature:
                r.errors.append("ed25519 signature invalid")
    except (ValueError, TypeError, AttributeError) as e:
        r.errors.append(f"malformed receipt: {e}")
    return r


def verify_chain(receipts, public_key_spki, prev_receipt_hash=None, expected_head=None,
                 first_sequence=None):
    """Verify an ordered list of receipts (section 7).

    expected_head: contentHash the LAST receipt must have, obtained from outside the
        emitter. Without it a dropped tail is undetectable (the spec says so too).
    first_sequence: sequence the first receipt must carry (catches a dropped head
        when prev_receipt_hash is not known).
    """
    errors = []
    if not receipts:
        return ChainResult(False, ["chain is empty"])
    expected_prev = prev_receipt_hash
    expected_seq = first_sequence
    issuer = receipts[0].get("issuerKeyId")
    for i, rc in enumerate(receipts):
        res = verify_receipt(rc, public_key_spki)
        if not res.valid:
            errors += [f"receipt[{i}]: {e}" for e in res.errors] or [f"receipt[{i}]: not valid"]
        if rc.get("issuerKeyId") != issuer:
            errors.append(f"receipt[{i}]: issuerKeyId differs from chain issuer")
        seq = rc.get("sequence")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 0:
            errors.append(f"receipt[{i}]: sequence missing or invalid")
            expected_seq = None
        else:
            if expected_seq is not None and seq != expected_seq:
                errors.append(f"receipt[{i}]: sequence {seq}, expected {expected_seq}")
            expected_seq = seq + 1
        if "prevReceiptHash" not in rc:
            errors.append(f"receipt[{i}]: prevReceiptHash missing")
        elif rc["prevReceiptHash"] != expected_prev:
            errors.append(f"receipt[{i}]: prevReceiptHash does not link to the previous receipt")
        expected_prev = (rc.get("integrity") or {}).get("contentHash")
    head = expected_prev
    if expected_head is not None and head != expected_head:
        errors.append("chain head does not match expected_head (tail dropped or replaced)")
    return ChainResult(not errors, errors, head)
