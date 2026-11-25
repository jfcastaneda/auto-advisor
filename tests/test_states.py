"""Checks assets/states.json for the same class of unit mistakes build_report.py
guards against: a rate given as a percent instead of a fraction, a missing source,
a stale or missing checked date."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

STATES_PATH = ROOT / "assets" / "states.json"


def load():
    return json.loads(STATES_PATH.read_text())


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def test_file_has_top_level_checked_date():
    data = load()
    assert "checked" in data and data["checked"], "states.json needs a top-level checked date"


def test_every_rate_is_a_fraction_not_a_percent():
    data = load()
    for code, row in data["states"].items():
        for key in ("stateRate", "combinedLow", "combinedHigh"):
            v = row[key]
            assert is_num(v), f"{code}.{key} must be a number, not {v!r}"
            assert 0 <= v <= 0.15, f"{code}.{key} is {v}, outside 0 to 0.15 (a fraction: 7% is 0.07)"
        rate = row["yearlyValueTax"]["roughRate"]
        if rate is not None:
            assert is_num(rate) and 0 <= rate <= 0.15, (
                f"{code}.yearlyValueTax.roughRate is {rate!r}, outside 0 to 0.15"
            )


def test_rate_ordering_state_le_low_le_high():
    data = load()
    for code, row in data["states"].items():
        s, lo, hi = row["stateRate"], row["combinedLow"], row["combinedHigh"]
        assert s <= lo <= hi, f"{code}: expected stateRate <= combinedLow <= combinedHigh, got {s}, {lo}, {hi}"


def test_every_row_has_a_source_with_url_and_checked_date():
    data = load()
    for code, row in data["states"].items():
        src = row.get("source")
        assert isinstance(src, dict), f"{code}: missing source"
        assert str(src.get("url", "")).lower().startswith(("http://", "https://")), (
            f"{code}: source needs an http(s) url"
        )
        assert src.get("title"), f"{code}: source needs a title"
        assert src.get("checked"), f"{code}: source needs a checked date"


def test_regime_is_a_known_value():
    data = load()
    known = {"sales", "title-excise-highway-use", "none"}
    for code, row in data["states"].items():
        assert row.get("regime") in known, f"{code}: regime {row.get('regime')!r} not in {known}"


def test_trade_in_credit_is_a_known_value_or_null():
    data = load()
    known = {"yes", "no", "dealer-only", "capped", None}
    for code, row in data["states"].items():
        assert row.get("tradeInCredit") in known, (
            f"{code}: tradeInCredit {row.get('tradeInCredit')!r} not in {known}"
        )


def test_state_codes_are_two_uppercase_letters():
    data = load()
    for code in data["states"]:
        assert len(code) == 2 and code.isupper() and code.isalpha(), f"bad state code: {code!r}"


REQUIRED_KEYS = {
    "name", "regime", "stateRate", "combinedLow", "combinedHigh", "docFeeTaxed",
    "rebateTaxed", "docFeeCap", "tradeInCredit", "yearlyValueTax", "privatePartyRule",
    "specialLineItems", "source", "note",
}


def test_every_row_has_every_schema_key():
    data = load()
    for code, row in data["states"].items():
        missing = REQUIRED_KEYS - set(row)
        assert not missing, f"{code}: missing keys {missing}"


def test_yearly_value_tax_applies_is_a_bool():
    data = load()
    for code, row in data["states"].items():
        applies = row["yearlyValueTax"]["applies"]
        assert isinstance(applies, bool), f"{code}: yearlyValueTax.applies must be true/false, not {applies!r}"


def test_doc_fee_cap_is_null_or_a_number():
    data = load()
    for code, row in data["states"].items():
        cap = row["docFeeCap"]
        assert cap is None or is_num(cap), f"{code}: docFeeCap must be null or a number, not {cap!r}"


def test_doc_fee_and_rebate_taxed_are_bool_or_null():
    data = load()
    for code, row in data["states"].items():
        for key in ("docFeeTaxed", "rebateTaxed"):
            v = row[key]
            assert v is None or isinstance(v, bool), f"{code}: {key} must be true, false or null, not {v!r}"


if __name__ == "__main__":
    import traceback
    mod = sys.modules[__name__]
    tests = [(n, fn) for n, fn in vars(mod).items() if n.startswith("test_") and callable(fn)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
