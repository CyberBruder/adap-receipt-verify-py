"""Generates examples/receipt.json signed with a throwaway demo key (fixed seed, public, NOT secret).
Run: python examples/make_example.py"""
import base64, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from adap_receipt_verify import canonicalize

priv = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"adap-receipt-verify-py demo key").digest())
der = priv.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
pub = base64.urlsafe_b64encode(der).decode().rstrip("=")
body = {
    "v": 1, "kind": "adap.receipt", "receiptId": "rcpt_demo_1", "issuer": "demo-issuer",
    "decidedAt": "2026-11-10T12:00:00.000Z",
    "intent": {"toolName": "transfer", "argsHash": "0" * 64, "argsRedacted": {"amount": 500.5}},
    "identity": {"agentId": "agt_demo", "actorType": "non_human_agent", "principalId": "prn_demo"},
    "decision": {"action": "REQUIRE_HUMAN", "outcome": "pending_human", "reason": "demo", "matched": True},
    "issuerKeyId": "ed25519:demo", "integrity": {"contentHash": ""},
}
body["integrity"]["contentHash"] = hashlib.sha256(canonicalize(body).encode()).hexdigest()
body["signature"] = priv.sign(canonicalize({k: v for k, v in body.items() if k != "signature"}).encode()).hex()
out = pathlib.Path(__file__).with_name("receipt.json")
out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
print("public key:", pub)
