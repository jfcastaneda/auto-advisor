#!/usr/bin/env python3
"""Build the buyer's report: data JSON + template -> one self-contained HTML page.

Usage:
  python3 build_report.py <data.json> <out.html>
  python3 build_report.py --init <data.json>   write a skeleton data file to start from

The template trusts the data, so this script checks types, units and ranges
and refuses to build when anything would put a wrong number on the page.
"""
import base64
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "report-template.html"
FONT = HERE.parent / "assets" / "fonts" / "archivo-latin-wdth-normal.woff2"
STATES_PATH = HERE.parent / "assets" / "states.json"
STAGES = {"needs", "shortlist", "listings", "negotiate", "first-year"}
GRADES = {"regular", "premium", "premium-recommended", "electric"}
CONDITIONS = {"New", "CPO", "Used"}

# Every assumption is a plain number in these units and ranges.
# taxRate and privateSaleDiscount are fractions (0.0625 means 6.25%).
ASSUMPTIONS = {
    "years": (5, 5, "the cost fields are 5-year totals, so years must be 5"),
    "milesPerYear": (1000, 60000, "miles a year"),
    "regular": (1, 10, "dollars per gallon"),
    "premium": (1, 10, "dollars per gallon"),
    "taxRate": (0, 0.15, "a fraction: 6.25% is 0.0625"),
    "docFee": (0, 3000, "dollars"),
    "title": (0, 1000, "dollars"),
    "plates": (0, 5000, "dollars, first-year registration and plates"),
    "registrationPerYear": (0, 5000, "dollars a year"),
    "privateSaleDiscount": (0, 0.5, "a fraction: 10% is 0.1"),
}
MODEL_NUMBERS = {
    "price": (500, 300000),
    "maintenance5yr": (0, 40000),
    "repairs5yr": (0, 40000),
    "resaleFairValue5yr": (0, 300000),
}
# Optional cost fields. When any model has one, every model must have it,
# or the cars without it look cheaper than they are.
ALL_OR_NONE = {"insurance5yr": (0, 60000), "propertyTax5yr": (0, 30000)}


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


def in_range(v, lo, hi):
    return is_num(v) and lo <= v <= hi


def _state_code_from_location(location):
    """The trailing two-letter state abbreviation in "City, ST", or None."""
    m = re.search(r",\s*([A-Za-z]{2})\s*$", str(location or ""))
    return m.group(1).upper() if m else None


def _load_states():
    try:
        return json.loads(STATES_PATH.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def check_source(where, s, need_checked, errors):
    if not isinstance(s, dict) or not s.get("title"):
        errors.append(f"{where}: each source needs a title")
        return
    if not str(s.get("url", "")).lower().startswith(("http://", "https://")):
        errors.append(f"{where}: source '{s.get('title')}' needs an http(s) url")
    if need_checked and not s.get("checked"):
        errors.append(f"{where}: source '{s.get('title')}' needs the date it was checked")


def check_list(where, value, errors, of=str):
    """The page loops over these fields, so a lone string breaks it. `value` may
    be missing. Returns the list to keep checking, or [] when it's unusable."""
    if value is None:
        return []
    kind = "strings" if of is str else "objects"
    if not isinstance(value, list):
        errors.append(f"{where} must be a list of {kind}, not {type(value).__name__}. "
                      f"Wrap a single item in [ ].")
        return []
    if any(not isinstance(v, of) for v in value):
        errors.append(f"{where} must be a list of {kind}")
        return []
    return value


def check(data):
    """Return (errors, warnings). Errors stop the build."""
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ["the data file must be a JSON object"], warnings
    for k in ("title", "buyer", "assumptions", "models"):
        if k not in data:
            errors.append(f"missing top-level field: {k}")

    a = data.get("assumptions")
    if not isinstance(a, dict):
        a = {}
        errors.append("assumptions must be an object")
    for k, (lo, hi, unit) in ASSUMPTIONS.items():
        v = a.get(k)
        if not is_num(v):
            errors.append(f"assumptions.{k} must be a number ({unit})")
        elif not lo <= v <= hi:
            hint = ""
            if k in ("taxRate", "privateSaleDiscount") and 1 <= v <= 100:
                hint = f" It looks like a percent; use {v / 100:g}."
            errors.append(f"assumptions.{k} is {v}, outside {lo} to {hi} ({unit}).{hint}")
    if is_num(a.get("regular")) and is_num(a.get("premium")) and a["premium"] < a["regular"]:
        errors.append("assumptions.premium is below assumptions.regular")
    lb = a.get("localeBasis")
    if lb is not None and lb not in ("estimate", "verified"):
        errors.append('assumptions.localeBasis must be "estimate" or "verified"')

    buyer = data.get("buyer")
    if not isinstance(buyer, dict):
        buyer = {}
        errors.append("buyer must be an object")
    for k in ("location", "role"):
        if not buyer.get(k):
            errors.append(f"buyer.{k} is required")
    budget = buyer.get("budget") or {}
    if not isinstance(budget, dict):
        errors.append("buyer.budget must be an object: { amount, type, otd }")
        budget = {}
    check_list("buyer.criteria", buyer.get("criteria"), errors)
    check_list("summary", data.get("summary"), errors)
    check_list("assumptions.notes", a.get("notes"), errors)
    if budget:
        if budget.get("type") not in ("cash", "financed"):
            errors.append('buyer.budget.type must be "cash" or "financed"')
        if "amount" in budget and not in_range(budget["amount"], 1000, 500000):
            errors.append("buyer.budget.amount must be a number from 1,000 to 500,000")
        if "otd" in budget and not isinstance(budget["otd"], bool):
            errors.append("buyer.budget.otd must be true or false")
    inc = buyer.get("grossMonthlyIncome")
    if inc is not None and not in_range(inc, 1, 1000000):
        errors.append("buyer.grossMonthlyIncome must be a positive monthly figure when present")

    code = _state_code_from_location(buyer.get("location"))
    if code and is_num(a.get("taxRate")):
        states = (_load_states() or {}).get("states", {})
        row = states.get(code)
        lo, hi = (row or {}).get("combinedLow"), (row or {}).get("combinedHigh")
        if is_num(lo) and is_num(hi) and not lo <= a["taxRate"] <= hi:
            warnings.append(
                f"buyer.location is {code}; assumptions.taxRate {a['taxRate']:g} falls outside "
                f"that state's known range {lo:g} to {hi:g} in assets/states.json."
            )

    models = data.get("models")
    if not isinstance(models, list) or not models:
        errors.append("models must be a non-empty list")
        models = []
    if any(not isinstance(m, dict) for m in models):
        errors.append("every entry in models must be an object")
        models = [m for m in models if isinstance(m, dict)]

    c = data.get("constraint")
    columns = None
    if c is not None:
        columns = c.get("columns") if isinstance(c, dict) else None
        if not isinstance(c, dict) or not c.get("name"):
            errors.append("constraint needs a name")
        if not isinstance(columns, list) or not columns:
            errors.append("constraint.columns must be a non-empty list")
            columns = None

    uses_electric = False
    ids = set()
    for i, m in enumerate(models):
        name = m.get("name") or f"models[{i}]"
        mid = m.get("id")
        if not isinstance(mid, str) or not mid:
            errors.append(f"{name}: id must be a non-empty string")
        elif not all(ch.isalnum() or ch in "-_" for ch in mid):
            errors.append(f"{name}: id may use only letters, digits, - and _")
        elif mid in ids:
            errors.append(f"{name}: duplicate id {mid}")
        if isinstance(mid, str):
            ids.add(mid)
        for k in ("story", "strengths", "watchouts", "inspection", "walkAway"):
            check_list(f"{name}: {k}", m.get(k), errors)
        check_list(f"{name}: failureModes", m.get("failureModes"), errors, of=dict)
        if not m.get("name"):
            errors.append(f"models[{i}]: missing name")
        if "condition" in m and m["condition"] not in CONDITIONS:
            errors.append(f"{name}: condition must be one of {sorted(CONDITIONS)}")

        for k, (lo, hi) in MODEL_NUMBERS.items():
            v = m.get(k)
            if not is_num(v):
                errors.append(f"{name}: {k} must be a number, not {json.dumps(v)}")
            elif not lo <= v <= hi:
                errors.append(f"{name}: {k} is {v}, outside {lo} to {hi}")

        grade = m.get("fuelGrade")
        if grade not in GRADES:
            errors.append(f"{name}: fuelGrade must be one of {sorted(GRADES)}")
        share = m.get("electricShare")
        if share is not None and not in_range(share, 0, 1):
            errors.append(f"{name}: electricShare must be a fraction from 0 to 1")
        if grade == "electric" and share is not None and share != 1:
            errors.append(f"{name}: an electric car runs on electricity only; drop electricShare")
        if grade == "electric" and m.get("mpg"):
            errors.append(f"{name}: an electric car takes kwhPer100, not mpg")
        on_electric = grade == "electric" or (is_num(share) and share > 0)
        if on_electric:
            uses_electric = True
            if not in_range(m.get("kwhPer100"), 10, 80):
                errors.append(f"{name}: kwhPer100 must be a number from 10 to 80 (kWh per 100 miles)")
        if grade != "electric":
            combined = (m.get("mpg") or {}).get("combined") if isinstance(m.get("mpg"), dict) else None
            if not in_range(combined, 5, 150):
                errors.append(f"{name}: mpg.combined must be a number from 5 to 150")
        if "extraRegistrationPerYear" in m and not in_range(m["extraRegistrationPerYear"], 0, 1000):
            errors.append(f"{name}: extraRegistrationPerYear must be a number from 0 to 1,000")

        sp = m.get("spectrum")
        if not isinstance(sp, int) or isinstance(sp, bool) or not 1 <= sp <= 5:
            errors.append(f"{name}: spectrum must be a whole number from 1 to 5")

        srcs = m.get("sources")
        if not isinstance(srcs, list) or not srcs:
            errors.append(f"{name}: needs at least one source")
        else:
            for s in srcs:
                check_source(name, s, True, errors)
        for r in check_list(f"{name}: reviews", m.get("reviews"), errors, of=dict):
            if r.get("url"):
                if not str(r["url"]).lower().startswith(("http://", "https://")):
                    errors.append(f"{name}: review '{r.get('title')}' needs an http(s) url")

        if columns is not None:
            vals = m.get("constraint")
            if not isinstance(vals, list) or len(vals) != len(columns):
                errors.append(f"{name}: constraint needs one value per column ({len(columns)})")

        if is_num(m.get("price")) and is_num(m.get("resaleFairValue5yr")):
            if m["resaleFairValue5yr"] > m["price"]:
                warnings.append(f"{name}: resale at year 5 is above the price. Check the depreciation curve.")
        if m.get("condition") == "Used" and m.get("repairs5yr") == 0:
            warnings.append(f"{name}: repairs5yr is 0 on a used car. Build it from the known failure items.")

    for k, (lo, hi) in ALL_OR_NONE.items():
        have = [m for m in models if k in m and m[k] is not None]
        if have and len(have) != len(models):
            missing = ", ".join(str(m.get("name")) for m in models if m.get(k) is None)
            errors.append(f"{k} is set on some models but not on: {missing}. Set it on every model or on none.")
        for m in have:
            if not in_range(m[k], lo, hi):
                errors.append(f"{m.get('name')}: {k} must be a number from {lo} to {hi}")

    if uses_electric and not in_range(a.get("electricity"), 0.03, 1):
        errors.append("assumptions.electricity must be dollars per kWh (0.03 to 1) when a model charges")

    f = data.get("financing")
    financed = budget.get("type") == "financed"
    if f is not None or financed:
        if not isinstance(f, dict):
            errors.append("financing { down, months, apr } is required for a financed budget")
            f = {}
        apr = f.get("apr")
        if apr is not None:
            if not is_num(apr) or not 0 <= apr <= 36:
                errors.append("financing.apr must be a percent from 0 to 36 (6.5 means 6.5%), or null")
            elif 0 < apr < 0.5:
                errors.append(f"financing.apr is {apr}. It's a percent, so 6.5% is 6.5. Use 0 for a 0% offer.")
        if financed or apr is not None:
            if not in_range(f.get("months"), 12, 96):
                errors.append("financing.months must be a number from 12 to 96")
            if not in_range(f.get("down", 0), 0, 500000):
                errors.append("financing.down must be 0 or more")
            prices = [m["price"] for m in models if is_num(m.get("price"))]
            if prices and is_num(f.get("down")) and f["down"] >= min(prices):
                errors.append("financing.down is at or above the cheapest car's price")

    if data.get("stage") and data["stage"] not in STAGES:
        errors.append(f"stage must be one of {sorted(STAGES)}")
    rec = data.get("recommendation")
    if rec is not None and not isinstance(rec, dict):
        errors.append("recommendation must be an object: { pick, paragraphs, avoid }")
    elif rec is not None:
        if not isinstance(rec.get("pick"), str) or rec["pick"] not in ids:
            errors.append(f"recommendation.pick {json.dumps(rec.get('pick'))} matches no model id")
        check_list("recommendation.paragraphs", rec.get("paragraphs"), errors)
        check_list("recommendation.avoid", rec.get("avoid"), errors)

    def model_ok(v):
        return isinstance(v, str) and v in ids

    for j, l in enumerate(check_list("listings", data.get("listings"), errors, of=dict)):
        if not model_ok(l.get("model")):
            errors.append(f"listings[{j}]: model '{l.get('model')}' matches no model id")
        if not in_range(l.get("price"), 500, 300000):
            errors.append(f"listings[{j}]: price must be a number from 500 to 300,000")
        if l.get("miles") is not None and not in_range(l["miles"], 0, 500000):
            errors.append(f"listings[{j}]: miles must be a number from 0 to 500,000")
        if l.get("url") and not str(l["url"]).lower().startswith(("http://", "https://")):
            errors.append(f"listings[{j}]: url must be http(s)")

    neg = data.get("negotiation")
    if neg is not None and not isinstance(neg, dict):
        errors.append("negotiation must be an object: { intro, cars }")
        neg = None
    for j, n in enumerate(check_list("negotiation.cars", (neg or {}).get("cars"), errors, of=dict)):
        check_list(f"negotiation.cars[{j}].script", n.get("script"), errors)
        check_list(f"negotiation.cars[{j}].levers", n.get("levers"), errors, of=dict)
        if not model_ok(n.get("model")):
            errors.append(f"negotiation.cars[{j}]: model '{n.get('model')}' matches no model id")
        nums = [n.get(k) for k in ("opening", "target", "walkAway")]
        for k, v in zip(("opening", "target", "walkAway"), nums):
            if not in_range(v, 500, 300000):
                errors.append(f"negotiation.cars[{j}]: {k} must be a number from 500 to 300,000")
        if all(is_num(v) for v in nums) and not nums[0] <= nums[1] <= nums[2]:
            errors.append(f"negotiation.cars[{j}]: needs opening <= target <= walkAway")

    fy = data.get("firstYear")
    if fy is not None and not isinstance(fy, dict):
        errors.append("firstYear must be an object: { model, intro, first30, schedule, sources }")
        fy = None
    if fy:
        if not model_ok(fy.get("model")):
            errors.append(f"firstYear.model {json.dumps(fy.get('model'))} matches no model id")
        check_list("firstYear.first30", fy.get("first30"), errors)
        for j, r in enumerate(check_list("firstYear.schedule", fy.get("schedule"), errors, of=dict)):
            lo, hi = r.get("low"), r.get("high")
            if not in_range(lo, 0, 20000) or not in_range(hi, 0, 20000):
                errors.append(f"firstYear.schedule[{j}]: low and high must be numbers from 0 to 20,000")
            elif lo > hi:
                errors.append(f"firstYear.schedule[{j}]: low is above high")
        for s in check_list("firstYear.sources", fy.get("sources"), errors, of=dict):
            check_source("firstYear", s, True, errors)
    for s in check_list("assumptions.sources", a.get("sources"), errors, of=dict):
        check_source("assumptions", s, False, errors)

    return errors, warnings


def noscript_html(data):
    """A plain fallback for viewers that block scripts: the words, without the live math."""
    e = html.escape
    by_id = {m.get("id"): m for m in data["models"]}
    out = ['<div class="noscript-body">',
           "<p><strong>This report needs JavaScript for its totals.</strong> "
           "Open it in a regular browser tab to see prices out the door and the 5-year costs.</p>"]
    for p in data.get("summary") or []:
        out.append(f"<p>{e(str(p))}</p>")
    rec = data.get("recommendation")
    if rec:
        pick = by_id.get(rec.get("pick"), {})
        out.append(f"<h2>Recommendation: {e(str(pick.get('name', rec.get('pick'))))}</h2>")
        for p in rec.get("paragraphs") or []:
            out.append(f"<p>{e(str(p))}</p>")
    out.append("<h2>Cars</h2><ul>")
    for m in data["models"]:
        bits = [str(m.get(k)) for k in ("year", "trim", "condition") if m.get(k)]
        out.append(f"<li>{e(str(m.get('name')))} ({e(' · '.join(bits))}): asking ${m['price']:,.0f}</li>")
    out.append("</ul></div>")
    return "\n".join(out)


def skeleton():
    """A minimal data file to start from. It fails check() until every FILL IN is replaced."""
    return {
        "title": "FILL IN: report title",
        "buyer": {"location": "FILL IN: City, ST", "role": "FILL IN: the car's role"},
        "assumptions": {
            "years": 5, "milesPerYear": 12000, "regular": 3.50, "premium": 4.00,
            "taxRate": 0.0625, "docFee": 150, "title": 75, "plates": 150,
            "registrationPerYear": 80, "privateSaleDiscount": 0.1,
            "localeBasis": "estimate",
            "notes": ["FILL IN: the locale-estimate sentence from locale.md"],
        },
        "models": [{
            "id": "car1",
            "name": "FILL IN: car name",
            "condition": "Used",
            "spectrum": "FILL IN: 1 to 5",
            "price": "FILL IN: asking price",
            "priceNote": "FILL IN: where the price came from",
            "mpg": {"combined": "FILL IN: combined mpg"},
            "fuelGrade": "regular",
            "maintenance5yr": "FILL IN: 5-year maintenance total",
            "repairs5yr": "FILL IN: 5-year repairs midpoint",
            "resaleFairValue5yr": "FILL IN: fair value at year 5",
            "sources": [{"title": "FILL IN: source name", "url": "FILL IN: https://...", "checked": "FILL IN: date checked"}],
        }],
    }


def render(data):
    """Turn already-valid data into the finished page. Call check() first."""
    # Escape every "<" so no text in the data can close or confuse the script block.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    font = base64.b64encode(FONT.read_bytes()).decode("ascii")
    return (TEMPLATE.read_text()
            .replace("/*__DATA__*/", payload, 1)
            .replace("<!--__NOSCRIPT__-->", noscript_html(data), 1)
            .replace("__FONT_BASE64__", font, 1))


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--init":
        pathlib.Path(sys.argv[2]).write_text(json.dumps(skeleton(), indent=2) + "\n")
        print(f"Wrote {sys.argv[2]}. Replace every FILL IN, then build it.")
        return
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    try:
        data = json.loads(pathlib.Path(sys.argv[1]).read_text())
    except json.JSONDecodeError as err:
        sys.exit(f"The data file isn't valid JSON: {err}")
    errors, warnings = check(data)
    if errors:
        sys.exit("Fix the data first:\n- " + "\n- ".join(errors))
    page = render(data)
    pathlib.Path(sys.argv[2]).write_text(page)
    for w in warnings:
        print(f"Check: {w}")
    print(f"Wrote {sys.argv[2]} with {len(data['models'])} models.")


if __name__ == "__main__":
    main()
