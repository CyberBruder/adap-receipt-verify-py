import json
import shutil
import subprocess

import pytest

from adap_receipt_verify.jcs import canonicalize, es_number


@pytest.mark.parametrize("value,expected", [
    (500.0, "500"), (1e-6, "0.000001"), (1e-7, "1e-7"), (1e20, "100000000000000000000"),
    (1e21, "1e+21"), (0.1, "0.1"), (-12.5, "-12.5"), (-0.0, "0"),
    (333333333.33333329, "333333333.3333333"),
])
def test_numbers(value, expected):
    assert es_number(value) == expected


def test_integer_like_keys_sort_as_strings():
    assert canonicalize({"2": 0, "9": 2, "10": 1, "a": 3}) == '{"10":1,"2":0,"9":2,"a":3}'


def test_keys_sort_by_utf16_not_codepoint():
    # U+10000 is the surrogate pair D800 DC00, which sorts BEFORE U+E000 in UTF-16
    assert canonicalize({"": 1, "\U00010000": 2}) == '{"\U00010000":2,"":1}'


def test_rejects_non_finite_and_lone_surrogate():
    with pytest.raises(ValueError):
        canonicalize(float("nan"))
    with pytest.raises(ValueError):
        canonicalize("\ud800")


def test_string_escaping():
    assert canonicalize({"s": 'a"b\\c\n\x01'}) == '{"s":"a\\"b\\\\c\\n\\u0001"}'


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_matches_node_for_numbers():
    nums = [0.1, 1e21, 1e-7, 123456789012345680000.0, 5e-324, 1.7976931348623157e308, 4.35, 1e23]
    js = "const a=JSON.parse(require('fs').readFileSync(0,'utf8'));" \
         "process.stdout.write(JSON.stringify(a.map(x=>JSON.stringify(x))))"
    out = subprocess.run(["node", "-e", js], input=json.dumps(nums), capture_output=True,
                         text=True, check=True).stdout
    assert [es_number(x) for x in nums] == json.loads(out)
