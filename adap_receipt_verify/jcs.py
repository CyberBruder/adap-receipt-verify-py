"""RFC 8785 (JSON Canonicalization Scheme), implemented from the RFC text.

Two places where Python's json module differs from JCS, and why this file exists:
  * numbers: JCS uses ECMAScript Number-to-String (500.0 -> 500, 1e-7 -> 1e-7)
  * key order: JCS sorts by UTF-16 code units, Python sorts by code point
"""
import json
import math
from decimal import Decimal


def es_number(x):
    """ECMAScript Number::toString for a finite IEEE-754 double."""
    if isinstance(x, bool):
        raise TypeError("bool is not a number")
    if isinstance(x, int):
        x = float(x)  # JSON numbers are doubles; ints above 2**53 are rounded
    if math.isnan(x) or math.isinf(x):
        raise ValueError("non-finite number")
    if x == 0:
        return "0"  # also covers -0
    sign = "-" if x < 0 else ""
    _, digits, exp = Decimal(repr(abs(x))).as_tuple()
    s = "".join(map(str, digits))
    stripped = s.rstrip("0")
    exp += len(s) - len(stripped)
    s = stripped or "0"
    k = len(s)
    n = k + exp
    if k <= n <= 21:
        out = s + "0" * (n - k)
    elif 0 < n <= 21:
        out = s[:n] + "." + s[n:]
    elif -6 < n <= 0:
        out = "0." + "0" * (-n) + s
    else:
        e = n - 1
        out = s[0] + ("." + s[1:] if k > 1 else "") + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + out


def _string(s):
    if any(0xD800 <= ord(c) <= 0xDFFF for c in s):
        raise ValueError("lone surrogate (not valid I-JSON)")
    return json.dumps(s, ensure_ascii=False)


def canonicalize(value):
    """Return the RFC 8785 canonical JSON text for a parsed JSON value."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, (int, float)):
        return es_number(value)
    if isinstance(value, list):
        return "[" + ",".join(canonicalize(i) for i in value) + "]"
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise TypeError("object keys must be strings")
        keys = sorted(value, key=lambda k: k.encode("utf-16-be", "surrogatepass"))
        return "{" + ",".join(_string(k) + ":" + canonicalize(value[k]) for k in keys) + "}"
    raise TypeError(f"unsupported type {type(value).__name__}")
