#!/usr/bin/env python3
"""The skill's money math, in one place. Every dollar figure shown in chat should
come from here, not from arithmetic done in prose, so the same number comes out
every time and matches the report template.

Usage:
  python3 calc.py <command> [--flag value ...]
  python3 calc.py <command> --json '{"price": 25000, ...}'
  python3 calc.py <command> --json data.json
  echo '{"price": 25000, ...}' | python3 calc.py <command> --json -

Commands:
  otd              Out-the-door price (and a range, with --tax-rate-high)
  max-price        Highest selling price that fits an OTD ceiling (a budget or a walk-away)
  payment          Loan payment and total interest
  trade-in         Trade-in break-even: the dealer offer that matches an outside offer
  total-cost       Full 5-year cost of ownership, loan interest included (same formula as the report template)
  walk-away        The walk-away price for a negotiation (see references/negotiation.md)
  property-tax     A rough 5-year yearly value tax, from a flat rate (see money-math.md)
  state            Print one state's row from assets/states.json (see locale.md)

Every command prints its result as labeled lines, and the same numbers as JSON on
the last line (for a script or a subagent to parse).
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
STATES_PATH = HERE.parent / "assets" / "states.json"


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _check_fraction(name, value):
    """A rate or discount is a fraction from 0 up to 1. Catch one passed as a
    percent (6.25) instead of a fraction (0.0625): the same mistake
    build_report.py's ASSUMPTIONS check guards against."""
    if value is None:
        return
    if 1 <= value <= 100:
        raise ValueError(f"{name} is {value:g}. It looks like a percent; use {value / 100:g}.")
    if value < 0 or value > 100:
        raise ValueError(f"{name} is {value:g}. It must be a fraction from 0 to 1 (6.25% is 0.0625).")


def _check_loan(apr, months):
    """apr is a percent from 0 to 36; months is a whole number, 1 or more.
    The same limits build_report.py puts on financing.apr."""
    if apr is None:
        raise ValueError("apr is required to compute a payment")
    if not 0 <= apr <= 36:
        raise ValueError(f"apr is {apr:g}. It must be a percent from 0 to 36 (6.5 means 6.5%).")
    if 0 < apr < 0.5:
        raise ValueError(f"apr is {apr:g}. It's a percent, so 6.5% is 6.5. Use 0 for a 0% offer.")
    if months is None or months < 1 or months != int(months):
        raise ValueError(f"months is {months}. The loan needs a whole number of months, 1 or more.")


def otd(price, doc_fee, tax_rate, title, plates, tax_rate_high=None):
    """OTD = selling price + doc fee + taxes + title + registration and plates."""
    _check_fraction("tax_rate", tax_rate)
    _check_fraction("tax_rate_high", tax_rate_high)

    def at(rate):
        tax = (price + doc_fee) * rate
        return price + doc_fee + tax + title + plates, tax

    value, tax = at(tax_rate)
    out = {"price": price, "tax": tax, "otd": value}
    if tax_rate_high is not None and tax_rate_high != tax_rate:
        value_high, tax_high = at(tax_rate_high)
        lo, hi = sorted((value, value_high))
        out["otdRange"] = [lo, hi]
    return out


def max_price(ceiling, tax_rate, title, plates, doc_fee, tax_rate_high=None):
    """Highest selling price whose OTD still fits a ceiling: a cash budget, or a
    walk-away OTD. max price = (ceiling - title - registration and plates) / (1 + tax rate) - doc fee."""
    _check_fraction("tax_rate", tax_rate)
    _check_fraction("tax_rate_high", tax_rate_high)

    def at(rate):
        return (ceiling - title - plates) / (1 + rate) - doc_fee

    value = at(tax_rate)
    out = {"maxPrice": value}
    if tax_rate_high is not None and tax_rate_high != tax_rate:
        value_high = at(tax_rate_high)
        lo, hi = sorted((value, value_high))
        out["maxPriceRange"] = [lo, hi]
    return out


def payment(otd_amount, down, apr, months, window_months=None):
    """Loan payment and total interest. apr is a percent (6.5 means 6.5%).
    A missing down payment counts as 0, the same as the report page.
    With window_months, also return interestInTotal: the interest paid inside
    that window, which is what a 5-year total counts on a longer loan."""
    _check_loan(apr, months)
    p = max(0.0, otd_amount - (down or 0))
    r = apr / 100 / 12
    n = int(months)
    pay = p / n if r == 0 else p * r / (1 - (1 + r) ** -n)
    interest = pay * n - p
    out = {"payment": pay, "interest": interest, "amountFinanced": p}
    if window_months is not None:
        k = min(n, int(window_months))
        g = (1 + r) ** k
        balance = p - pay * k if r == 0 else p * g - pay * (g - 1) / r
        out["interestInTotal"] = pay * k - (p - balance)
    return out


def trade_in_breakeven(outside_offer, tax_rate):
    """The dealer trade-in offer that matches an outside offer once the trade-in
    tax credit is counted: outside offer / (1 + tax rate)."""
    _check_fraction("tax_rate", tax_rate)
    return {"breakeven": outside_offer / (1 + tax_rate)}


def fuel_year(miles_per_year, mpg_combined, fuel_price, electric_share=0.0,
              kwh_per_100=None, electricity_price=None):
    """Fuel for one year. A pure EV (electric_share 1) needs no MPG or gas price.
    A gas car needs no kWh figure or electricity price. A plug-in needs all four."""
    share = electric_share or 0.0
    if not 0 <= share <= 1:
        raise ValueError(f"electric_share is {share:g}. It must be a fraction from 0 to 1 (1 for a pure EV).")
    gas_year = elec_year = 0.0
    if share < 1:
        if mpg_combined is None or fuel_price is None:
            raise ValueError("a car that burns gas needs mpg_combined and fuel_price "
                             "(for a pure EV, set electric_share to 1)")
        if mpg_combined <= 0:
            raise ValueError(f"mpg_combined is {mpg_combined:g}. It must be above 0.")
        gas_year = miles_per_year * (1 - share) / mpg_combined * fuel_price
    if share > 0:
        if kwh_per_100 is None or electricity_price is None:
            raise ValueError("a car that charges needs kwh_per_100 and electricity_price")
        elec_year = miles_per_year * share * kwh_per_100 / 100 * electricity_price
    return gas_year + elec_year


def registration_total(registration_per_year, years, extra_registration_per_year=0.0):
    """Renewal fees for the years after the first, plus any yearly EV/hybrid road-use fee."""
    return registration_per_year * (years - 1) + (extra_registration_per_year or 0.0) * years


def total_cost(price, doc_fee, tax_rate, title, plates, years, miles_per_year,
                maintenance, repairs, resale_fair_value, private_sale_discount,
                registration_per_year, mpg_combined=None, fuel_price=None, insurance=0.0,
                property_tax=0.0, extra_registration_per_year=0.0, electric_share=0.0,
                kwh_per_100=None, electricity_price=None, down=None, apr=None, months=None):
    """5-year cost = OTD + fuel + insurance + maintenance + repairs + registration
    renewals + property tax + loan interest - resale value at year 5. Loan
    interest counts only when apr and months are given, and only the interest
    paid inside the window (a 72-month loan adds its first 60 months of
    interest). Same formula as the report template's calcAt(), so a chat
    answer and the report never disagree."""
    _check_fraction("private_sale_discount", private_sale_discount)
    o = otd(price, doc_fee, tax_rate, title, plates)
    fuel = fuel_year(miles_per_year, mpg_combined, fuel_price, electric_share,
                      kwh_per_100, electricity_price) * years
    reg = registration_total(registration_per_year, years, extra_registration_per_year)
    resale = resale_fair_value * (1 - private_sale_discount)
    total = o["otd"] + fuel + insurance + maintenance + repairs + reg + property_tax - resale
    out = {"otd": o["otd"], "tax": o["tax"], "fuel": fuel, "registration": reg,
           "resale": resale, "total": total}
    if apr is not None and months is None:
        raise ValueError("apr needs months too. Pass both, or leave apr out for a total without loan interest.")
    if months is not None and apr is not None:
        loan = payment(o["otd"], down, apr, months, window_months=years * 12)
        out.update(loan)
        out["total"] = total + loan["interestInTotal"]
    return out


def walk_away(comparable_top, doc_fee, tax_rate, title, plates, budget=None,
              budget_is_otd=True, next_best_total=None, this_total=None,
              this_otd=None, preference_value=0.0):
    """The walk-away is the lowest of (a) the top of the comparable range plus
    fees, (b) the buyer's budget, and (c) the next-best car's equivalent price
    plus what the preference is worth. All three are compared out the door,
    then converted back to a selling price for negotiation.cars[].walkAway."""
    next_best_fields = (next_best_total, this_total, this_otd)
    if any(v is not None for v in next_best_fields) and not all(v is not None for v in next_best_fields):
        raise ValueError("candidate (c) needs next_best_total, this_total and this_otd together, or none of them")
    candidates = {"comparables": otd(comparable_top, doc_fee, tax_rate, title, plates)["otd"]}
    if budget is not None:
        is_otd = True if budget_is_otd is None else budget_is_otd
        candidates["budget"] = budget if is_otd else otd(budget, doc_fee, tax_rate, title, plates)["otd"]
    if all(v is not None for v in next_best_fields):
        candidates["nextBest"] = next_best_total - (this_total - this_otd) + (preference_value or 0.0)
    binding = min(candidates, key=candidates.get)
    ceiling = candidates[binding]
    price = max_price(ceiling, tax_rate, title, plates, doc_fee)["maxPrice"]
    return {"candidates": candidates, "binding": binding, "walkAwayOtd": ceiling,
            "walkAwaySellingPrice": price}


def property_tax(price, resale_fair_value, rate, years=5):
    """A rough 5-year yearly value tax from a flat rate. The car's value is
    assumed to step down geometrically from price (year 1's start-of-year
    value) to resale_fair_value (what it's worth after `years` years), and the
    tax is rate times the start-of-year value for each of years 1..years.
    Always label this rough: it isn't the locale's real assessment method."""
    _check_fraction("rate", rate)
    if years < 1 or years != int(years):
        raise ValueError(f"years is {years:g}. It must be a whole number, 1 or more.")
    years = int(years)
    if price <= 0:
        raise ValueError("price must be positive")
    if resale_fair_value < 0:
        raise ValueError("resale_fair_value can't be negative")
    ratio = (resale_fair_value / price) ** (1 / years)
    total = sum(price * (ratio ** t) * rate for t in range(years))
    return {"total": total, "yearlyRatio": ratio}


def state_row(code):
    """One state's row from assets/states.json, by its two-letter code."""
    data = json.loads(STATES_PATH.read_text())
    row = data["states"].get(code.upper())
    if row is None:
        raise ValueError(f"no row for {code.upper()} in {STATES_PATH.name}; see locale.md for an unlisted state")
    return {"code": code.upper(), "checked": data.get("checked"), **row}


def _add_json_arg(p):
    p.add_argument("--json", help="a JSON object, a file path, or '-' for stdin, "
                                   "with the same keys as this command's flags")


def _load_json(spec):
    """A JSON object from inline text, a file path, or '-' for stdin."""
    if spec == "-":
        text = sys.stdin.read()
    elif spec.strip()[:1] in ("{", "["):
        text = spec
    else:
        try:
            with open(spec) as f:
                text = f.read()
        except OSError as err:
            raise ValueError(f"--json: can't read the file {spec!r} ({err.strerror})")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise ValueError(f"--json isn't valid JSON: {err}")
    if not isinstance(data, dict):
        raise ValueError("--json must be a JSON object, like {\"price\": 25000}")
    return data


def _parse_bool(s):
    v = str(s).strip().lower()
    if v in ("true", "yes", "y", "1"):
        return True
    if v in ("false", "no", "n", "0"):
        return False
    raise argparse.ArgumentTypeError(f"{s!r} isn't true or false")


TEXT_OR_BOOL_FIELDS = {"code", "budget_is_otd"}


def _merge(args, parser, optional=()):
    """CLI flags win; --json fills in anything not passed on the command line.
    An unknown key in --json is an error, not a silent no-op."""
    values = vars(args)
    values.pop("command", None)
    if values.get("json"):
        try:
            data = _load_json(values.pop("json"))
        except ValueError as err:
            parser.error(str(err))
        for k, v in data.items():
            key = k.replace("-", "_")
            if key not in values:
                parser.error(f"unknown field in --json: {k}")
            if v is not None and key not in TEXT_OR_BOOL_FIELDS and not is_num(v):
                parser.error(f"--json: {k} must be a plain number, not {json.dumps(v)}")
            if key == "budget_is_otd" and v is not None and not isinstance(v, bool):
                parser.error("--json: budget_is_otd must be true or false")
            if values[key] is None:
                values[key] = v
    else:
        values.pop("json", None)
    missing = [k for k, v in values.items() if v is None and k not in optional]
    if missing:
        parser.error("missing: " + ", ".join(missing))
    return values


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    def num(p, name, help):
        p.add_argument(f"--{name}", type=float, default=None, help=help)

    p = sub.add_parser("otd", help="out-the-door price")
    num(p, "price", "selling price")
    num(p, "doc-fee", "dealer documentation fee")
    num(p, "tax-rate", "a fraction: 6.25%% is 0.0625")
    num(p, "title", "title fee")
    num(p, "plates", "registration and plates, first year")
    p.add_argument("--tax-rate-high", type=float, default=None,
                   help="optional: the top of a local tax range, for an OTD range")
    _add_json_arg(p)

    p = sub.add_parser("max-price", help="highest selling price under an OTD ceiling")
    num(p, "ceiling", "an OTD ceiling: a cash budget, or a walk-away OTD")
    num(p, "tax-rate", "a fraction: 6.25%% is 0.0625")
    num(p, "title", "title fee")
    num(p, "plates", "registration and plates, first year")
    num(p, "doc-fee", "dealer documentation fee")
    p.add_argument("--tax-rate-high", type=float, default=None,
                   help="optional: the top of a local tax range, for a max-price range")
    _add_json_arg(p)

    p = sub.add_parser("payment", help="loan payment and total interest")
    num(p, "otd", "out-the-door price")
    p.add_argument("--down", type=float, default=None, help="down payment, default 0")
    num(p, "apr", "a percent: 6.5%% is 6.5")
    num(p, "months", "loan term in months")
    _add_json_arg(p)

    p = sub.add_parser("trade-in", help="trade-in break-even after the tax credit")
    num(p, "outside-offer", "a binding outside cash offer")
    num(p, "tax-rate", "a fraction: 6.25%% is 0.0625")
    _add_json_arg(p)

    p = sub.add_parser("walk-away", help="the walk-away price for a negotiation")
    num(p, "comparable-top", "top of the comparable-listing range, a selling price")
    num(p, "doc-fee", "dealer documentation fee")
    num(p, "tax-rate", "a fraction: 6.25%% is 0.0625")
    num(p, "title", "title fee")
    num(p, "plates", "registration and plates, first year")
    p.add_argument("--budget", type=float, default=None, help="the buyer's budget, optional")
    p.add_argument("--budget-is-otd", type=_parse_bool, default=None,
                   help="true if --budget is an OTD figure (default), false if it's a selling price")
    p.add_argument("--next-best-total", type=float, default=None,
                   help="the next-best car's 5-year total cost, optional")
    p.add_argument("--this-total", type=float, default=None, help="this car's 5-year total cost")
    p.add_argument("--this-otd", type=float, default=None, help="this car's OTD price")
    p.add_argument("--preference-value", type=float, default=None,
                   help="what the buyer says preferring this car is worth, default 0")
    _add_json_arg(p)

    p = sub.add_parser("total-cost", help="5-year total cost of ownership")
    for name, help in [
        ("price", "selling price"), ("doc-fee", "dealer documentation fee"),
        ("tax-rate", "a fraction: 6.25%% is 0.0625"), ("title", "title fee"),
        ("plates", "registration and plates, first year"), ("years", "always 5"),
        ("miles-per-year", "miles driven a year"),
        ("maintenance", "5-year maintenance total"), ("repairs", "5-year repairs midpoint"),
        ("resale-fair-value", "fair value at year 5, before the private-sale discount"),
        ("private-sale-discount", "a fraction: 10%% is 0.1"),
        ("registration-per-year", "annual registration renewal"),
    ]:
        num(p, name, help)
    p.add_argument("--mpg-combined", type=float, default=None, help="combined MPG, omit for a pure EV")
    p.add_argument("--fuel-price", type=float, default=None,
                   help="$/gallon for the grade the car takes, omit for a pure EV")
    p.add_argument("--insurance", type=float, default=None, help="default 0")
    p.add_argument("--property-tax", type=float, default=None, help="default 0")
    p.add_argument("--extra-registration-per-year", type=float, default=None, help="default 0")
    p.add_argument("--electric-share", type=float, default=None, help="0 to 1; 1 for a pure EV; default 0")
    p.add_argument("--kwh-per-100", type=float, default=None)
    p.add_argument("--electricity-price", type=float, default=None, help="$/kWh")
    p.add_argument("--down", type=float, default=None, help="down payment, default 0")
    p.add_argument("--apr", type=float, default=None,
                   help="a percent: 6.5%% is 6.5. With --months, adds the loan interest to the total")
    p.add_argument("--months", type=float, default=None, help="loan term in months")
    _add_json_arg(p)

    p = sub.add_parser("property-tax", help="a rough 5-year yearly value tax")
    num(p, "price", "selling price (year 1's start-of-year value)")
    num(p, "resale-fair-value", "fair value at year 5, before the private-sale discount")
    num(p, "rate", "a fraction: 1%% is 0.01")
    p.add_argument("--years", type=float, default=None, help="default 5")
    _add_json_arg(p)

    p = sub.add_parser("state", help="print one state's row from assets/states.json")
    p.add_argument("--code", default=None, help="two-letter state code, e.g. TX")
    _add_json_arg(p)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    command = args.command

    try:
        if command == "otd":
            values = _merge(args, parser, optional={"tax_rate_high"})
            result = otd(values["price"], values["doc_fee"], values["tax_rate"],
                          values["title"], values["plates"], values.get("tax_rate_high"))
        elif command == "max-price":
            values = _merge(args, parser, optional={"tax_rate_high"})
            result = max_price(values["ceiling"], values["tax_rate"], values["title"],
                                values["plates"], values["doc_fee"], values.get("tax_rate_high"))
        elif command == "payment":
            values = _merge(args, parser, optional={"down"})
            result = payment(values["otd"], values["down"], values["apr"], values["months"])
        elif command == "trade-in":
            values = _merge(args, parser)
            result = trade_in_breakeven(values["outside_offer"], values["tax_rate"])
        elif command == "walk-away":
            optional = {"budget", "budget_is_otd", "next_best_total", "this_total",
                        "this_otd", "preference_value"}
            values = _merge(args, parser, optional=optional)
            result = walk_away(
                values["comparable_top"], values["doc_fee"], values["tax_rate"],
                values["title"], values["plates"], budget=values["budget"],
                budget_is_otd=values["budget_is_otd"],
                next_best_total=values["next_best_total"], this_total=values["this_total"],
                this_otd=values["this_otd"], preference_value=values["preference_value"],
            )
        elif command == "total-cost":
            zero_by_default = {"insurance", "property_tax", "extra_registration_per_year", "electric_share"}
            truly_optional = {"mpg_combined", "fuel_price", "kwh_per_100", "electricity_price", "down", "apr", "months"}
            values = _merge(args, parser, optional=zero_by_default | truly_optional)
            for k in zero_by_default:
                if values[k] is None:
                    values[k] = 0.0
            result = total_cost(**values)
        elif command == "property-tax":
            values = _merge(args, parser, optional={"years"})
            result = property_tax(values["price"], values["resale_fair_value"], values["rate"],
                                  years=5 if values["years"] is None else values["years"])
        elif command == "state":
            values = _merge(args, parser)
            result = state_row(values["code"])
        else:
            parser.error(f"unknown command {command}")
    except ValueError as err:
        parser.error(str(err))

    for k, v in result.items():
        if is_num(v) and -1 < v < 1 and v != 0:
            print(f"{k}: {v:.4g}")  # a fraction (a rate, a ratio), not a dollar amount
        elif is_num(v):
            print(f"{k}: {v:,.2f}")
        else:
            print(f"{k}: {v}")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
