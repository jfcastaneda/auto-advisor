"""Proves scripts/calc.py matches the report template's math.

The strongest check (test_js_*) runs the template's own calcAt()/maxAsk()
functions, extracted live from assets/report-template.html, in macOS's
built-in JavaScriptCore (via `osascript -l JavaScript`) and compares the
result to calc.py. It's skipped where osascript isn't available.

The other tests re-transcribe calcAt()/maxAsk() by hand (js_calc_at() /
js_max_price() below), independently of calc.py, as a second check that
doesn't need osascript. If the template's math ever changes, update those
two functions to match before trusting them.
"""
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import calc  # noqa: E402

CALC_PY = ROOT / "scripts" / "calc.py"


def run_calc_cli(*args):
    proc = subprocess.run([sys.executable, "-I", str(CALC_PY), *args],
                           capture_output=True, text=True)
    return proc


def js_elec_share(m):
    return 1.0 if m.get("fuelGrade") == "electric" else (m.get("electricShare") or 0.0)


def js_calc_at(m, a, f, price):
    """Transcribed from the template's calcAt(), not calling calc.py."""
    tax = (price + a["docFee"]) * a["taxRate"]
    otd = price + a["docFee"] + tax + a["title"] + a["plates"]
    share = js_elec_share(m)
    ppg = None if m.get("fuelGrade") == "electric" else (a["regular"] if m["fuelGrade"] == "regular" else a["premium"])
    gas_year = a["milesPerYear"] * (1 - share) / m["mpg"]["combined"] * ppg if share < 1 else 0.0
    elec_year = a["milesPerYear"] * share * m["kwhPer100"] / 100 * a["electricity"] if share > 0 else 0.0
    fuel_year = gas_year + elec_year
    fuel = fuel_year * a["years"]
    reg = a["registrationPerYear"] * (a["years"] - 1) + m.get("extraRegistrationPerYear", 0) * a["years"]
    resale = m["resaleFairValue5yr"] * (1 - a["privateSaleDiscount"])
    ins = m.get("insurance5yr") or 0
    ptax = m.get("propertyTax5yr") or 0
    total = otd + fuel + ins + m["maintenance5yr"] + m["repairs5yr"] + reg + ptax - resale
    payment = interest = None
    if f.get("apr") is not None and f.get("months"):
        p = max(0.0, otd - (f.get("down") or 0))
        r = f["apr"] / 100 / 12
        n = f["months"]
        payment = p / n if r == 0 else p * r / (1 - (1 + r) ** -n)
        interest = payment * n - p
        k = min(n, a["years"] * 12)
        g = (1 + r) ** k
        bal = p - payment * k if r == 0 else p * g - payment * (g - 1) / r
        interest_in_total = payment * k - (p - bal)
        total += interest_in_total
    return {"tax": tax, "otd": otd, "fuel": fuel, "reg": reg, "resale": resale,
            "total": total, "payment": payment, "interest": interest}


def js_max_price(budget, a):
    return (budget - a["title"] - a["plates"]) / (1 + a["taxRate"]) - a["docFee"]


def close(x, y, tol=0.01):
    return abs(x - y) <= tol


# ---------- live-JS parity, via macOS's built-in JavaScriptCore ----------

TEMPLATE_JS = (ROOT / "assets" / "report-template.html").read_text()
HAS_OSASCRIPT = shutil.which("osascript") is not None


def extract_js_function(name, text=TEMPLATE_JS):
    """Pull `function name(...) { ... }` out of the template by brace-matching,
    so the test runs the template's real, current source, not a copy of it."""
    start = text.index(f"function {name}(")
    open_brace = text.index("{", start)
    depth, i = 0, open_brace
    while True:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return text[start:i + 1]


def run_js(script):
    proc = subprocess.run(["osascript", "-l", "JavaScript", "-e", script],
                           capture_output=True, text=True, timeout=10)
    if proc.returncode != 0:
        raise RuntimeError(f"osascript failed: {proc.stderr}")
    return json.loads(proc.stdout)


def js_calc_at_live(m, a, f, price):
    js = (
        f"var A = {json.dumps(a)};\n"
        f"var F = {json.dumps(f)};\n"
        f"{extract_js_function('elecShare')}\n"
        f"{extract_js_function('calcAt')}\n"
        f"var m = {json.dumps(m)};\n"
        f"JSON.stringify(calcAt(m, {price}));\n"
    )
    return run_js(js)


def js_max_price_live(budget, a):
    js = (
        f"var A = {json.dumps(a)};\n"
        f"var B = {{type: 'cash', otd: true, amount: {budget}}};\n"
        f"{extract_js_function('maxAsk')}\n"
        "JSON.stringify(maxAsk());\n"
    )
    return run_js(js)


def test_js_sample_models_match_calc_py():
    if not HAS_OSASCRIPT:
        print("SKIP test_js_sample_models_match_calc_py: osascript not available")
        return
    data = json.loads((ROOT / "assets" / "sample-data.json").read_text())
    a = data["assumptions"]
    f = data["financing"]
    for m in data["models"]:
        js = js_calc_at_live(m, a, f, m["price"])
        py = calc.total_cost(
            price=m["price"], doc_fee=a["docFee"], tax_rate=a["taxRate"],
            title=a["title"], plates=a["plates"], years=a["years"],
            miles_per_year=a["milesPerYear"], mpg_combined=m["mpg"]["combined"],
            fuel_price=a["regular"] if m["fuelGrade"] == "regular" else a["premium"],
            maintenance=m["maintenance5yr"], repairs=m["repairs5yr"],
            resale_fair_value=m["resaleFairValue5yr"],
            private_sale_discount=a["privateSaleDiscount"],
            registration_per_year=a["registrationPerYear"],
            insurance=m.get("insurance5yr") or 0,
            property_tax=m.get("propertyTax5yr") or 0,
        )
        assert close(js["otd"], py["otd"]), (m["name"], js["otd"], py["otd"])
        assert close(js["total"], py["total"]), (m["name"], js["total"], py["total"])


def test_js_financed_payment_matches_calc_py():
    if not HAS_OSASCRIPT:
        print("SKIP test_js_financed_payment_matches_calc_py: osascript not available")
        return
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100, "years": 5,
         "milesPerYear": 12000, "regular": 3.2, "premium": 3.8,
         "registrationPerYear": 80, "privateSaleDiscount": 0.1, "electricity": 0.15}
    m = {"mpg": {"combined": 28}, "fuelGrade": "regular", "maintenance5yr": 2500,
         "repairs5yr": 1200, "resaleFairValue5yr": 13000}
    f = {"down": 3000, "months": 60, "apr": 6.9}
    js = js_calc_at_live(m, a, f, 26000)
    py = calc.total_cost(
        price=26000, doc_fee=a["docFee"], tax_rate=a["taxRate"], title=a["title"],
        plates=a["plates"], years=a["years"], miles_per_year=a["milesPerYear"],
        mpg_combined=m["mpg"]["combined"], fuel_price=a["regular"],
        maintenance=m["maintenance5yr"], repairs=m["repairs5yr"],
        resale_fair_value=m["resaleFairValue5yr"],
        private_sale_discount=a["privateSaleDiscount"],
        registration_per_year=a["registrationPerYear"],
        down=f["down"], apr=f["apr"], months=f["months"],
    )
    assert close(js["payment"], py["payment"])
    assert close(js["interest"], py["interest"])


def test_js_ev_and_plugin_fuel_match_calc_py():
    if not HAS_OSASCRIPT:
        print("SKIP test_js_ev_and_plugin_fuel_match_calc_py: osascript not available")
        return
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100, "years": 5,
         "milesPerYear": 12000, "regular": 3.2, "premium": 3.8,
         "registrationPerYear": 80, "privateSaleDiscount": 0.1, "electricity": 0.16}
    f = {}
    ev = {"fuelGrade": "electric", "kwhPer100": 29, "mpg": {"combined": 0},
          "maintenance5yr": 2000, "repairs5yr": 500, "resaleFairValue5yr": 14000}
    phev = {"fuelGrade": "regular", "electricShare": 0.55, "kwhPer100": 27,
            "mpg": {"combined": 32}, "maintenance5yr": 2200, "repairs5yr": 800,
            "resaleFairValue5yr": 13500}
    for m in (ev, phev):
        js = js_calc_at_live(m, a, f, 32000)
        py = calc.total_cost(
            price=32000, doc_fee=a["docFee"], tax_rate=a["taxRate"], title=a["title"],
            plates=a["plates"], years=a["years"], miles_per_year=a["milesPerYear"],
            mpg_combined=None if m["fuelGrade"] == "electric" else m["mpg"]["combined"],
            fuel_price=a["regular"], maintenance=m["maintenance5yr"],
            repairs=m["repairs5yr"], resale_fair_value=m["resaleFairValue5yr"],
            private_sale_discount=a["privateSaleDiscount"],
            registration_per_year=a["registrationPerYear"],
            electric_share=1.0 if m["fuelGrade"] == "electric" else m["electricShare"],
            kwh_per_100=m["kwhPer100"], electricity_price=a["electricity"],
        )
        assert close(js["fuel"], py["fuel"]), (m["fuelGrade"], js["fuel"], py["fuel"])
        assert close(js["total"], py["total"])


def test_js_max_price_matches_calc_py():
    if not HAS_OSASCRIPT:
        print("SKIP test_js_max_price_matches_calc_py: osascript not available")
        return
    a = {"docFee": 378, "taxRate": 0.095, "title": 165, "plates": 151}
    js = js_max_price_live(32000, a)
    py = calc.max_price(32000, a["taxRate"], a["title"], a["plates"], a["docFee"])["maxPrice"]
    assert close(js, py)


def test_sample_models_match_template_math():
    data = json.loads((ROOT / "assets" / "sample-data.json").read_text())
    a = data["assumptions"]
    f = data["financing"]
    for m in data["models"]:
        js = js_calc_at(m, a, f, m["price"])
        py = calc.total_cost(
            price=m["price"], doc_fee=a["docFee"], tax_rate=a["taxRate"],
            title=a["title"], plates=a["plates"], years=a["years"],
            miles_per_year=a["milesPerYear"], mpg_combined=m["mpg"]["combined"],
            fuel_price=a["regular"] if m["fuelGrade"] == "regular" else a["premium"],
            maintenance=m["maintenance5yr"], repairs=m["repairs5yr"],
            resale_fair_value=m["resaleFairValue5yr"],
            private_sale_discount=a["privateSaleDiscount"],
            registration_per_year=a["registrationPerYear"],
            insurance=m.get("insurance5yr") or 0,
            property_tax=m.get("propertyTax5yr") or 0,
            down=f.get("down"), apr=f.get("apr"), months=f.get("months"),
        )
        assert close(js["otd"], py["otd"]), (m["name"], js["otd"], py["otd"])
        assert close(js["total"], py["total"]), (m["name"], js["total"], py["total"])
        # the sample's financing.apr is null, so neither side computes a payment
        assert js["payment"] is None and "payment" not in py


def test_financed_payment_matches_template_math():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100, "years": 5,
         "milesPerYear": 12000, "regular": 3.2, "premium": 3.8,
         "registrationPerYear": 80, "privateSaleDiscount": 0.1, "electricity": 0.15}
    m = {"mpg": {"combined": 28}, "fuelGrade": "regular", "maintenance5yr": 2500,
         "repairs5yr": 1200, "resaleFairValue5yr": 13000}
    f = {"down": 3000, "months": 60, "apr": 6.9}
    js = js_calc_at(m, a, f, 26000)
    py = calc.total_cost(
        price=26000, doc_fee=a["docFee"], tax_rate=a["taxRate"], title=a["title"],
        plates=a["plates"], years=a["years"], miles_per_year=a["milesPerYear"],
        mpg_combined=m["mpg"]["combined"], fuel_price=a["regular"],
        maintenance=m["maintenance5yr"], repairs=m["repairs5yr"],
        resale_fair_value=m["resaleFairValue5yr"],
        private_sale_discount=a["privateSaleDiscount"],
        registration_per_year=a["registrationPerYear"],
        down=f["down"], apr=f["apr"], months=f["months"],
    )
    assert close(js["payment"], py["payment"])
    assert close(js["interest"], py["interest"])


def test_ev_and_plugin_fuel_match_template_math():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100, "years": 5,
         "milesPerYear": 12000, "regular": 3.2, "premium": 3.8,
         "registrationPerYear": 80, "privateSaleDiscount": 0.1, "electricity": 0.16}
    f = {}
    ev = {"fuelGrade": "electric", "kwhPer100": 29, "mpg": {"combined": 0},
          "maintenance5yr": 2000, "repairs5yr": 500, "resaleFairValue5yr": 14000}
    phev = {"fuelGrade": "regular", "electricShare": 0.55, "kwhPer100": 27,
            "mpg": {"combined": 32}, "maintenance5yr": 2200, "repairs5yr": 800,
            "resaleFairValue5yr": 13500}
    for m in (ev, phev):
        js = js_calc_at(m, a, f, 32000)
        py = calc.total_cost(
            price=32000, doc_fee=a["docFee"], tax_rate=a["taxRate"], title=a["title"],
            plates=a["plates"], years=a["years"], miles_per_year=a["milesPerYear"],
            mpg_combined=None if m["fuelGrade"] == "electric" else m["mpg"]["combined"],
            fuel_price=a["regular"], maintenance=m["maintenance5yr"],
            repairs=m["repairs5yr"], resale_fair_value=m["resaleFairValue5yr"],
            private_sale_discount=a["privateSaleDiscount"],
            registration_per_year=a["registrationPerYear"],
            electric_share=1.0 if m["fuelGrade"] == "electric" else m["electricShare"],
            kwh_per_100=m["kwhPer100"], electricity_price=a["electricity"],
        )
        assert close(js["fuel"], py["fuel"]), (m["fuelGrade"], js["fuel"], py["fuel"])
        assert close(js["total"], py["total"])


def test_max_price_matches_template_maxAsk():
    a = {"docFee": 378, "taxRate": 0.095, "title": 165, "plates": 151}
    js = js_max_price(32000, a)
    py = calc.max_price(32000, a["taxRate"], a["title"], a["plates"], a["docFee"])["maxPrice"]
    assert close(js, py)


def test_max_price_inverts_otd():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100}
    ceiling = 25000
    price = calc.max_price(ceiling, a["taxRate"], a["title"], a["plates"], a["docFee"])["maxPrice"]
    back = calc.otd(price, a["docFee"], a["taxRate"], a["title"], a["plates"])["otd"]
    assert close(back, ceiling)


def test_walk_away_picks_lowest_candidate_and_converts_to_selling_price():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100}
    out = calc.walk_away(comparable_top=27400, doc_fee=a["docFee"], tax_rate=a["taxRate"],
                          title=a["title"], plates=a["plates"], budget=28000)
    comparables_otd = calc.otd(27400, a["docFee"], a["taxRate"], a["title"], a["plates"])["otd"]
    assert close(out["candidates"]["comparables"], comparables_otd)
    assert out["candidates"]["budget"] == 28000
    assert out["binding"] == "budget"  # 28000 < comparables_otd here
    assert close(out["walkAwayOtd"], 28000)
    back = calc.otd(out["walkAwaySellingPrice"], a["docFee"], a["taxRate"], a["title"], a["plates"])["otd"]
    assert close(back, 28000)


def test_walk_away_next_best_candidate():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100}
    out = calc.walk_away(comparable_top=40000, doc_fee=a["docFee"], tax_rate=a["taxRate"],
                          title=a["title"], plates=a["plates"],
                          next_best_total=29000, this_total=30000, this_otd=26000,
                          preference_value=500)
    # nextBest = 29000 - (30000 - 26000) + 500 = 25500, the lowest candidate here
    assert close(out["candidates"]["nextBest"], 25500)
    assert out["binding"] == "nextBest"


def test_all_cli_flags_default_to_none():
    """A non-None flag default (like the old --insurance 0.0) lets --json's value for
    that same field get silently dropped by _merge, since _merge only fills a key when
    it's still None. Every flag must default to None except help and --json itself, so
    this guards the whole bug class rather than one field at a time."""
    parser = calc.build_parser()
    for action in parser._subparsers._group_actions[0].choices.values():
        for a in action._actions:
            if a.dest in ("help", "json", "command"):
                continue
            assert a.default is None, f"--{a.dest.replace('_', '-')} defaults to {a.default!r}, not None"


def test_walk_away_partial_next_best_raises():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100}
    try:
        calc.walk_away(comparable_top=27400, doc_fee=a["docFee"], tax_rate=a["taxRate"],
                        title=a["title"], plates=a["plates"], next_best_total=29000)
        raise AssertionError("expected a ValueError for partial candidate (c) inputs")
    except ValueError:
        pass


def test_cli_walk_away_json_applies_budget_is_otd_false_and_preference():
    # budget_is_otd defaults to None in argparse specifically so --json can fill it in;
    # this guards against the same silent-drop bug fixed in total-cost's --json merge.
    payload = {"comparable_top": 27400, "doc_fee": 150, "tax_rate": 0.0625, "title": 75,
               "plates": 100, "budget": 26000, "budget_is_otd": False, "preference_value": 500}
    proc = run_calc_cli("walk-away", "--json", json.dumps(payload))
    assert proc.returncode == 0, proc.stderr
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    expected_budget_otd = calc.otd(26000, 150, 0.0625, 75, 100)["otd"]
    assert close(result["candidates"]["budget"], expected_budget_otd), (
        "budget_is_otd: false from --json was dropped, budget treated as already-OTD"
    )


def test_walk_away_skips_next_best_when_not_given():
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100}
    out = calc.walk_away(comparable_top=27400, doc_fee=a["docFee"], tax_rate=a["taxRate"],
                          title=a["title"], plates=a["plates"])
    assert "nextBest" not in out["candidates"]
    assert "budget" not in out["candidates"]
    assert out["binding"] == "comparables"


def test_trade_in_breakeven():
    out = calc.trade_in_breakeven(8000, 0.0625)
    assert close(out["breakeven"], 8000 / 1.0625)


def test_property_tax_matches_closed_form_geometric_series():
    price, resale, rate, years = 30000, 15000, 0.01, 5
    out = calc.property_tax(price, resale, rate, years)
    k = out["yearlyRatio"]
    assert close(k ** years, resale / price)
    # closed-form sum of a geometric series: price*r*(1-k^years)/(1-k), using
    # k^years = resale/price by construction, independent of calc.py's loop.
    closed_form = price * rate * (1 - resale / price) / (1 - k)
    assert close(out["total"], closed_form)


def test_property_tax_rejects_nonpositive_price():
    try:
        calc.property_tax(0, 1000, 0.01)
        raise AssertionError("expected a ValueError for a non-positive price")
    except ValueError:
        pass


def test_property_tax_rejects_negative_resale():
    try:
        calc.property_tax(30000, -1, 0.01)
        raise AssertionError("expected a ValueError for a negative resale_fair_value")
    except ValueError:
        pass


def test_property_tax_rejects_rate_given_as_percent():
    try:
        calc.property_tax(30000, 15000, 3.5)  # meant 0.035
        raise AssertionError("expected a ValueError for a rate that looks like a percent")
    except ValueError:
        pass


def test_otd_rejects_tax_rate_given_as_percent():
    try:
        calc.otd(25000, 150, 6.25, 75, 100)  # meant 0.0625
        raise AssertionError("expected a ValueError for a tax_rate that looks like a percent")
    except ValueError:
        pass


def test_total_cost_rejects_private_sale_discount_given_as_percent():
    try:
        calc.total_cost(
            price=25000, doc_fee=150, tax_rate=0.0625, title=75, plates=100, years=5,
            miles_per_year=12000, mpg_combined=30, fuel_price=3.2, maintenance=2000,
            repairs=1000, resale_fair_value=12000, private_sale_discount=10,  # meant 0.1
            registration_per_year=80,
        )
        raise AssertionError("expected a ValueError for a private_sale_discount that looks like a percent")
    except ValueError:
        pass


def test_state_row_returns_known_state():
    row = calc.state_row("tx")
    assert row["code"] == "TX"
    assert row["name"] == "Texas"
    assert row["source"]["url"].startswith("https://")


def test_state_row_raises_for_unknown_state():
    try:
        calc.state_row("ZZ")
        raise AssertionError("expected a ValueError for an unknown state code")
    except ValueError:
        pass


def test_cli_property_tax_matches_function():
    proc = run_calc_cli("property-tax", "--price", "30000", "--resale-fair-value", "15000", "--rate", "0.01")
    assert proc.returncode == 0, proc.stderr
    cli_result = json.loads(proc.stdout.strip().splitlines()[-1])
    py_result = calc.property_tax(30000, 15000, 0.01)
    assert close(cli_result["total"], py_result["total"])


def test_cli_state_unknown_code_errors():
    proc = run_calc_cli("state", "--code", "ZZ")
    assert proc.returncode != 0
    assert "no row for ZZ" in proc.stderr


# ---------- CLI-level tests, so a bug in the --json wiring itself is caught ----------

def test_cli_total_cost_json_counts_insurance_and_plugin_share():
    payload = {
        "price": 32000, "doc_fee": 150, "tax_rate": 0.0625, "title": 75, "plates": 100,
        "years": 5, "miles_per_year": 12000, "mpg_combined": 32, "fuel_price": 3.2,
        "maintenance": 2200, "repairs": 800, "resale_fair_value": 13500,
        "private_sale_discount": 0.1, "registration_per_year": 80,
        "insurance": 7000, "electric_share": 0.55, "kwh_per_100": 27,
        "electricity_price": 0.16,
    }
    proc = run_calc_cli("total-cost", "--json", json.dumps(payload))
    assert proc.returncode == 0, proc.stderr
    cli_result = json.loads(proc.stdout.strip().splitlines()[-1])
    py_result = calc.total_cost(**payload)
    assert close(cli_result["total"], py_result["total"])
    # specifically: insurance and the plug-in's electric share must not have been
    # silently dropped by the --json merge (the bug this test guards against)
    no_insurance = calc.total_cost(**{**payload, "insurance": 0})
    assert not close(py_result["total"], no_insurance["total"]), "insurance had no effect"
    all_gas = calc.total_cost(**{**payload, "electric_share": 0})
    assert not close(py_result["fuel"], all_gas["fuel"]), "electric_share had no effect"


def test_cli_total_cost_json_rejects_unknown_key():
    payload = {
        "price": 25000, "doc_fee": 150, "tax_rate": 0.0625, "title": 75, "plates": 100,
        "years": 5, "miles_per_year": 12000, "mpg_combined": 30, "fuel_price": 3.2,
        "maintenance": 2000, "repairs": 1000, "resale_fair_value": 12000,
        "private_sale_discount": 0.1, "registration_per_year": 80,
        "docFee": 999,  # wrong key name (should be doc_fee); must error, not be ignored
    }
    proc = run_calc_cli("total-cost", "--json", json.dumps(payload))
    assert proc.returncode != 0
    assert "unknown field" in proc.stderr


# ---------- loan interest counts in the 5-year total ----------

FIN_KW = dict(price=26000, doc_fee=150, tax_rate=0.0625, title=75, plates=100, years=5,
              miles_per_year=12000, mpg_combined=28, fuel_price=3.2, maintenance=2500,
              repairs=1200, resale_fair_value=13000, private_sale_discount=0.1,
              registration_per_year=80)


def test_total_cost_adds_loan_interest():
    cash = calc.total_cost(**FIN_KW)
    fin = calc.total_cost(**FIN_KW, down=3000, apr=6.9, months=60)
    assert close(fin["total"], cash["total"] + fin["interest"])
    assert close(fin["interestInTotal"], fin["interest"])


def test_total_cost_counts_only_interest_paid_inside_the_window():
    cash = calc.total_cost(**FIN_KW)
    fin = calc.total_cost(**FIN_KW, down=3000, apr=6.9, months=72)
    # Walk the amortization schedule month by month for the first 60 payments.
    bal, r, paid = fin["amountFinanced"], 6.9 / 100 / 12, 0.0
    for _ in range(60):
        i = bal * r
        paid += i
        bal -= fin["payment"] - i
    assert close(fin["interestInTotal"], paid)
    assert fin["interestInTotal"] < fin["interest"]
    assert close(fin["total"], cash["total"] + paid)


def test_total_cost_zero_apr_adds_no_interest():
    cash = calc.total_cost(**FIN_KW)
    fin = calc.total_cost(**FIN_KW, down=3000, apr=0, months=60)
    assert close(fin["total"], cash["total"])


def test_total_cost_rejects_half_a_loan():
    assert _raises(calc.total_cost, **FIN_KW, apr=6.9)
    # Months with no rate yet is the page's "add a loan rate" state: no interest, no error.
    no_rate = calc.total_cost(**FIN_KW, down=3000, months=60)
    assert "payment" not in no_rate and close(no_rate["total"], calc.total_cost(**FIN_KW)["total"])


def test_total_cost_down_defaults_to_zero_like_the_page():
    fin = calc.total_cost(**FIN_KW, apr=6.9, months=60)
    assert close(fin["amountFinanced"], fin["otd"])
    assert fin["payment"] > 0


def test_js_total_includes_loan_interest_and_matches_calc_py():
    if not HAS_OSASCRIPT:
        print("SKIP test_js_total_includes_loan_interest_and_matches_calc_py: osascript not available")
        return
    a = {"docFee": 150, "taxRate": 0.0625, "title": 75, "plates": 100, "years": 5,
         "milesPerYear": 12000, "regular": 3.2, "premium": 3.8,
         "registrationPerYear": 80, "privateSaleDiscount": 0.1, "electricity": 0.15}
    m = {"mpg": {"combined": 28}, "fuelGrade": "regular", "maintenance5yr": 2500,
         "repairs5yr": 1200, "resaleFairValue5yr": 13000}
    for months, apr in ((60, 6.9), (72, 6.9), (48, 0)):
        f = {"down": 3000, "months": months, "apr": apr}
        js = js_calc_at_live(m, a, f, 26000)
        py = calc.total_cost(**FIN_KW, down=3000, apr=apr, months=months)
        assert close(js["total"], py["total"]), (months, apr, js["total"], py["total"])
        assert close(js["interestInTotal"], py["interestInTotal"])
        assert close(js_calc_at(m, a, f, 26000)["total"], py["total"])


# ---------- bad input is refused, with a clean message ----------

def _raises(fn, *args, **kw):
    try:
        fn(*args, **kw)
    except ValueError:
        return True
    return False


def _cli_clean_error(*args):
    proc = run_calc_cli(*args)
    assert proc.returncode == 2, (args, proc.returncode, proc.stderr[-300:])
    assert "Traceback" not in proc.stderr, proc.stderr[-400:]
    return proc.stderr


def test_payment_rejects_apr_given_as_fraction():
    assert _raises(calc.payment, 30000, 5000, 0.065, 60)


def test_payment_rejects_negative_and_absurd_apr():
    assert _raises(calc.payment, 30000, 5000, -2, 60)
    assert _raises(calc.payment, 30000, 5000, 80, 60)


def test_payment_rejects_zero_or_fractional_months():
    assert _raises(calc.payment, 30000, 5000, 6.5, 0)
    assert _raises(calc.payment, 30000, 5000, 6.5, 60.5)


def test_payment_zero_apr_still_works():
    assert close(calc.payment(30000, 6000, 0, 48)["payment"], 500)


def test_cli_payment_down_is_optional():
    proc = run_calc_cli("payment", "--otd", "30000", "--apr", "6.5", "--months", "60")
    assert proc.returncode == 0, proc.stderr
    assert close(json.loads(proc.stdout.strip().splitlines()[-1])["amountFinanced"], 30000)


def test_rates_outside_zero_to_one_are_rejected():
    assert _raises(calc.otd, 25000, 200, 150, 50, 200)
    assert _raises(calc.otd, 25000, 200, -0.05, 50, 200)
    assert _raises(calc.trade_in_breakeven, 15000, 1.5)


def test_electric_share_outside_zero_to_one_is_rejected():
    assert _raises(calc.fuel_year, 12000, 30, 3.2, 50, 30, 0.15)
    assert _raises(calc.fuel_year, 12000, 30, 3.2, -0.1, 30, 0.15)


def test_fuel_year_names_the_missing_input():
    assert _raises(calc.fuel_year, 12000, None, 3.2)           # gas car, no mpg
    assert _raises(calc.fuel_year, 12000, 0, 3.2)              # mpg of 0
    assert _raises(calc.fuel_year, 12000, 30, None)            # gas car, no fuel price
    assert _raises(calc.fuel_year, 12000, 30, 3.2, 0.5)        # plug-in, no kWh
    assert _raises(calc.fuel_year, 12000, 30, 3.2, 0.5, 30)    # plug-in, no electricity price


def test_pure_ev_needs_no_fuel_price_or_mpg():
    assert close(calc.fuel_year(12000, None, None, 1.0, 28, 0.16), 12000 * 0.28 * 0.16)
    args = ["total-cost", "--price", "27400", "--doc-fee", "378", "--tax-rate", "0.095",
            "--title", "165", "--plates", "151", "--years", "5", "--miles-per-year", "12000",
            "--private-sale-discount", "0.1", "--registration-per-year", "151",
            "--electric-share", "1", "--kwh-per-100", "28", "--electricity-price", "0.16",
            "--maintenance", "3200", "--repairs", "600", "--resale-fair-value", "15800"]
    proc = run_calc_cli(*args)
    assert proc.returncode == 0, proc.stderr
    assert close(json.loads(proc.stdout.strip().splitlines()[-1])["fuel"], 2688.0)


def test_property_tax_rejects_zero_or_fractional_years():
    assert _raises(calc.property_tax, 25000, 12000, 0.01, 0)
    assert _raises(calc.property_tax, 25000, 12000, 0.01, 2.7)
    _cli_clean_error("property-tax", "--price", "25000", "--resale-fair-value", "12000",
                     "--rate", "0.01", "--years", "0")


def test_cli_budget_is_otd_reads_no_as_false_and_rejects_junk():
    base = ["walk-away", "--comparable-top", "30000", "--doc-fee", "200", "--tax-rate", "0.0625",
            "--title", "50", "--plates", "200", "--budget", "27000"]
    proc = run_calc_cli(*base, "--budget-is-otd", "no")
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out["candidates"]["budget"] > 27000   # a selling price, so fees were added
    _cli_clean_error(*base, "--budget-is-otd", "maybe")


def test_cli_errors_are_clean_messages_not_tracebacks():
    gas = ["total-cost", "--price", "25000", "--doc-fee", "200", "--tax-rate", "0.0625",
           "--title", "50", "--plates", "200", "--years", "5", "--miles-per-year", "12000",
           "--fuel-price", "3.2", "--maintenance", "3000", "--repairs", "2000",
           "--resale-fair-value", "12000", "--private-sale-discount", "0.1",
           "--registration-per-year", "80"]
    assert "mpg" in _cli_clean_error(*gas)
    _cli_clean_error(*gas, "--mpg-combined", "0")
    _cli_clean_error(*gas, "--mpg-combined", "30", "--electric-share", "0.5")
    _cli_clean_error(*gas, "--mpg-combined", "30", "--electric-share", "50",
                     "--kwh-per-100", "30", "--electricity-price", "0.15")
    _cli_clean_error("payment", "--otd", "30000", "--down", "5000", "--apr", "6.5", "--months", "0")
    _cli_clean_error("payment", "--otd", "30000", "--down", "5000", "--apr", "0.065", "--months", "60")
    assert "percent" in _cli_clean_error("otd", "--price", "25000", "--doc-fee", "200",
                                         "--tax-rate", "6.25", "--title", "50", "--plates", "200")
    _cli_clean_error("trade-in", "--outside-offer", "15000", "--tax-rate", "7")
    _cli_clean_error("max-price", "--ceiling", "30000", "--tax-rate", "7", "--title", "50",
                     "--plates", "200", "--doc-fee", "200")


def test_cli_bad_json_input_is_a_clean_error():
    _cli_clean_error("otd", "--json", "nosuchfile.json")
    _cli_clean_error("otd", "--json", "[1, 2]")
    _cli_clean_error("otd", "--json", "{not json")
    _cli_clean_error("otd", "--json",
                     '{"price": "25000", "doc_fee": 200, "tax_rate": 0.0625, "title": 50, "plates": 200}')


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
