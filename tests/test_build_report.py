"""Edge-case suite for scripts/build_report.py. Run: python3 -m pytest tests/ -q
(or: python3 -I tests/test_build_report.py to run without pytest)."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_report as br  # noqa: E402


def valid_model(mid="car1", **overrides):
    m = {
        "id": mid,
        "name": "Test Car",
        "condition": "Used",
        "spectrum": 3,
        "price": 25000,
        "mpg": {"combined": 30},
        "fuelGrade": "regular",
        "maintenance5yr": 2000,
        "repairs5yr": 1000,
        "resaleFairValue5yr": 12000,
        "sources": [{"title": "Edmunds", "url": "https://edmunds.com/x", "checked": "2026-11-01"}],
    }
    m.update(overrides)
    return m


def base_data(**overrides):
    d = {
        "title": "Test Report",
        "buyer": {"location": "Austin, TX", "role": "commuter"},
        "assumptions": {
            "years": 5, "milesPerYear": 12000, "regular": 3.0, "premium": 3.5,
            "taxRate": 0.0625, "docFee": 150, "title": 75, "plates": 100,
            "registrationPerYear": 80, "privateSaleDiscount": 0.1,
        },
        "models": [valid_model()],
    }
    d.update(overrides)
    return d


def assert_fails(data, needle=None):
    errors, _ = br.check(data)
    assert errors, "expected check() to report errors, got none"
    if needle:
        assert any(needle.lower() in e.lower() for e in errors), (
            f"expected an error containing {needle!r}, got {errors}"
        )
    return errors


def assert_builds(data):
    errors, warnings = br.check(data)
    assert not errors, f"unexpected build errors: {errors}"
    page = br.render(data)
    return page, warnings


# ---------- must fail ----------

def test_price_as_string_fails():
    d = base_data(models=[valid_model(price="25000")])
    assert_fails(d, "price")


def test_price_as_bool_fails():
    d = base_data(models=[valid_model(price=True)])
    assert_fails(d, "price")


def test_null_resale_fails():
    d = base_data(models=[valid_model(resaleFairValue5yr=None)])
    assert_fails(d, "resaleFairValue5yr")


def test_negative_price_fails():
    d = base_data(models=[valid_model(price=-100)])
    assert_fails(d, "price")


def test_non_numeric_mpg_fails():
    d = base_data(models=[valid_model(mpg={"combined": "thirty"})])
    assert_fails(d, "mpg")


def test_tax_rate_as_percent_fails():
    d = base_data()
    d["assumptions"]["taxRate"] = 6.25
    assert_fails(d, "taxRate")


def test_private_sale_discount_as_percent_fails():
    d = base_data()
    d["assumptions"]["privateSaleDiscount"] = 10
    assert_fails(d, "privateSaleDiscount")


def test_years_other_than_5_fails():
    d = base_data()
    d["assumptions"]["years"] = 3
    assert_fails(d, "years")


def test_constraint_without_columns_fails():
    d = base_data()
    d["constraint"] = {"name": "Cargo"}
    assert_fails(d, "constraint")


def test_insurance_on_one_model_only_fails():
    d = base_data(models=[
        valid_model("car1", insurance5yr=6000),
        valid_model("car2"),
    ])
    assert_fails(d, "insurance5yr")


def test_apr_as_fraction_fails():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "financed", "amount": 25000}})
    d["financing"] = {"down": 2000, "months": 60, "apr": 0.065}
    assert_fails(d, "apr")


def test_apr_as_string_fails():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "financed", "amount": 25000}})
    d["financing"] = {"down": 2000, "months": 60, "apr": "6.5%"}
    assert_fails(d, "apr")


def test_down_above_price_fails():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "financed", "amount": 25000}})
    d["financing"] = {"down": 30000, "months": 60, "apr": 6.5}
    assert_fails(d, "down")


def test_opening_above_walkaway_fails():
    d = base_data()
    d["negotiation"] = {"cars": [{"model": "car1", "opening": 20000, "target": 17000, "walkAway": 15000}]}
    assert_fails(d, "opening")


def test_missing_buyer_role_fails():
    d = base_data(buyer={"location": "Austin, TX"})
    assert_fails(d, "role")


def test_models_as_object_fails():
    d = base_data()
    d["models"] = {"car1": valid_model()}
    assert_fails(d, "models")


def test_source_without_url_fails():
    d = base_data(models=[valid_model(sources=[{"title": "Edmunds"}])])
    assert_fails(d, "url")


def test_ev_without_kwh_fails():
    d = base_data(models=[valid_model(fuelGrade="electric", mpg=None)])
    assert_fails(d, "kwhPer100")


def test_ev_without_electricity_price_fails():
    d = base_data(models=[valid_model(fuelGrade="electric", mpg=None, kwhPer100=28)])
    assert_fails(d, "electricity")


# ---------- must build ----------

def test_sample_data_builds():
    data = json.loads((ROOT / "assets" / "sample-data.json").read_text())
    assert_builds(data)


def test_one_model_builds():
    assert_builds(base_data())


def test_two_way_tie_builds():
    d = base_data(models=[
        valid_model("car1", price=20000, resaleFairValue5yr=10000),
        valid_model("car2", price=20000, resaleFairValue5yr=10000),
    ])
    assert_builds(d)


def test_financed_with_null_apr_builds():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "financed", "amount": 25000}})
    d["financing"] = {"down": 2000, "months": 60, "apr": None}
    assert_builds(d)


def test_financed_with_apr_and_income_builds():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "financed", "amount": 25000},
                          "grossMonthlyIncome": 6000})
    d["financing"] = {"down": 2000, "months": 60, "apr": 6.5}
    assert_builds(d)


def test_ev_plus_plugin_builds():
    d = base_data(models=[
        valid_model("ev1", fuelGrade="electric", mpg=None, kwhPer100=28, electricShare=1),
        valid_model("phev1", fuelGrade="regular", electricShare=0.6, kwhPer100=30),
    ])
    d["assumptions"]["electricity"] = 0.15
    assert_builds(d)


def test_verified_locale_builds():
    d = base_data()
    d["assumptions"]["localeBasis"] = "verified"
    assert_builds(d)


def test_script_tags_in_text_are_escaped():
    baseline = br.TEMPLATE.read_text().count("</script")
    d = base_data()
    d["summary"] = ["<script>alert(1)</script>", "Normal paragraph."]
    d["models"][0]["story"] = ["Watch for </script> tricks in pasted listing text."]
    page, _ = assert_builds(d)
    assert page.count("</script") == baseline, (
        "text from the data leaked a literal </script> into the page"
    )


def test_state_tax_rate_in_range_warns_nothing():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter"})
    d["assumptions"]["taxRate"] = 0.0625  # TX's combinedLow/High in states.json
    errors, warnings = br.check(d)
    assert not errors
    assert not any("taxRate" in w and "falls outside" in w for w in warnings)


def test_state_tax_rate_out_of_range_warns():
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter"})
    d["assumptions"]["taxRate"] = 0.09  # above TX's known range
    errors, warnings = br.check(d)
    assert not errors
    assert any("TX" in w and "falls outside" in w for w in warnings)


def test_state_tax_rate_unknown_state_warns_nothing():
    d = base_data(buyer={"location": "Nowhere, ZZ", "role": "commuter"})
    d["assumptions"]["taxRate"] = 0.0625
    errors, warnings = br.check(d)
    assert not errors
    assert not any("falls outside" in w for w in warnings)


def test_close_to_budget_under_builds():
    # car1's OTD is 26,896.88 (price 25000, doc fee 150, tax 0.0625, title 75, plates 100).
    # A budget about 2% above the OTD puts the car about 2% under budget, inside the
    # page's 3% "near budget" band.
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "cash", "amount": 27435, "otd": True}})
    d["assumptions"]["localeBasis"] = "estimate"
    assert_builds(d)


def test_close_to_budget_over_builds():
    # same OTD; a budget about 1.5% below it puts the car about 1.5% over budget.
    d = base_data(buyer={"location": "Austin, TX", "role": "commuter",
                          "budget": {"type": "cash", "amount": 26500, "otd": True}})
    d["assumptions"]["localeBasis"] = "estimate"
    assert_builds(d)


# ---------- --init skeleton ----------

def test_init_skeleton_fails_until_filled():
    errors, _ = br.check(br.skeleton())
    assert errors, "the skeleton must fail check() until every FILL IN is replaced"


def test_init_cli_writes_a_skeleton_that_fails_check(tmp_path):
    out = tmp_path / "skeleton.json"
    proc = subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts" / "build_report.py"), "--init", str(out)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert out.exists()
    data = json.loads(out.read_text())
    errors, _ = br.check(data)
    assert errors, "the skeleton written by --init must fail check() until filled in"

    build_proc = subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts" / "build_report.py"), str(out), str(tmp_path / "out.html")],
        capture_output=True, text=True,
    )
    assert build_proc.returncode != 0, "building the unfilled skeleton must not succeed"


# ---------- a string where a list belongs, or a non-object section ----------

def test_string_where_a_list_belongs_fails():
    for key in ("story", "strengths", "watchouts", "inspection", "walkAway", "reviews", "failureModes"):
        assert_fails(base_data(models=[valid_model(**{key: "one string"})]), key)
    assert_fails(base_data(summary="one string"), "summary")
    assert_fails(base_data(recommendation={"pick": "car1", "paragraphs": "x"}), "paragraphs")
    assert_fails(base_data(recommendation={"pick": "car1", "avoid": "x"}), "avoid")
    d = base_data()
    d["assumptions"]["notes"] = "a note"
    assert_fails(d, "notes")
    d = base_data()
    d["buyer"]["criteria"] = "AWD"
    assert_fails(d, "criteria")


def test_negotiation_text_fields_must_be_lists():
    car = {"model": "car1", "opening": 20000, "target": 21000, "walkAway": 22000}
    assert_fails(base_data(negotiation={"cars": [dict(car, script="hello")]}), "script")
    assert_fails(base_data(negotiation={"cars": [dict(car, levers="x")]}), "levers")
    assert_fails(base_data(negotiation={"cars": [dict(car, levers=["x"])]}), "levers")
    assert_builds(base_data(negotiation={"cars": [dict(car, script=["hello"], levers=[{"lever": "a", "evidence": "b"}])]}))


def test_first_year_fields_must_be_lists():
    assert_fails(base_data(firstYear={"model": "car1", "first30": "x"}), "first30")
    assert_fails(base_data(firstYear={"model": "car1", "schedule": "x"}), "schedule")
    assert_fails(base_data(firstYear={"model": "car1", "schedule": ["x"]}), "schedule")


def test_non_object_sections_fail_cleanly():
    d = base_data()
    d["buyer"]["budget"] = "30000"
    assert_fails(d, "budget")
    assert_fails(base_data(listings=["x"]), "listings")
    assert_fails(base_data(listings="x"), "listings")
    assert_fails(base_data(negotiation=[]), "negotiation")
    assert_fails(base_data(negotiation={"cars": ["x"]}), "negotiation")
    assert_fails(base_data(firstYear="x"), "firstYear")
    assert_fails(base_data(models=[valid_model(mid=["a"])]), "id")
    assert_fails(base_data(models=[valid_model(reviews=["x"])]), "reviews")
    assert_fails(base_data(models=[valid_model(sources="x")]), "source")


if __name__ == "__main__":
    # Minimal runner for `python3 -I tests/test_build_report.py` without pytest installed.
    import inspect
    import traceback

    mod = sys.modules[__name__]
    tests = [(n, f) for n, f in vars(mod).items() if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in tests:
        try:
            if "tmp_path" in inspect.signature(fn).parameters:
                import tempfile
                with tempfile.TemporaryDirectory() as d:
                    fn(pathlib.Path(d))
            else:
                fn()
            passed += 1
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    print(f"{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
