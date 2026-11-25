# The Money Math

All figures are estimates unless a receipt or written quote backs them. Show the assumptions where the buyer can see and change them. Taxes and fees start as a labeled state estimate, as a low-to-high range (see `locale.md`).

**Every dollar figure shown in chat comes from `scripts/calc.py`.** It has the same formulas as the report template (`assets/report-template.html`), so a chat answer and the report always match. Run it, read the numbers back, and write them into the answer. See each section below for the command.

Two terms, used consistently: **registration and plates** is the first-year combined fee (title is separate). **Registration renewals** are the annual fees in the years after the first.

## Out-the-door (OTD)

OTD = selling price + doc fee + taxes + title + registration and plates + any mandatory fees

`python3 scripts/calc.py otd --price P --doc-fee F --tax-rate R --title T --plates L`
Add `--tax-rate-high` for the top of a local tax range to get an OTD range back.

- `calc.py` taxes the price plus the doc fee, the same way the report template does. Where a state's own rules differ (it doesn't tax the doc fee, or it taxes a state valuation rather than the price), say so in the label instead of adjusting the math by hand (see `locale.md`).
- **Cash buyers:** work back from the budget to the highest asking price that fits. max price = (ceiling − title − registration and plates) ÷ (1 + tax rate) − doc fee, where the ceiling is the OTD budget. `calc.py max-price --ceiling C --tax-rate R --title T --plates L --doc-fee F`. The same formula finds the selling price behind any OTD ceiling. `calc.py walk-away` uses it to turn a negotiation walk-away into the selling price `negotiation.cars[].walkAway` stores (see `negotiation.md`).
- **Financed buyers:** show the monthly payment and total interest at the buyer's real rate (see `financing.md`): `calc.py payment --otd O --down D --apr A --months N`. The APR is a percent (6.5 means 6.5%), unlike the tax rate, which is a fraction. Leave `--down` out for $0 down. Never assume a rate. Ask for it or show a range by credit tier.

## Fuel

Fuel per year = miles per year ÷ combined MPG × price per gallon for the required or recommended grade.

- Use AAA's current state or metro averages, with the date.
- When a car is "87 minimum, 91 recommended," price premium and note what running 87 costs in power and MPG.
- For EVs and plug-ins, use kWh per 100 miles and the buyer's electricity rate, plus public charging if they lack home charging. `calc.py total-cost` takes `--electric-share`, `--kwh-per-100` and `--electricity-price` and blends gas and electricity automatically. A pure EV sets `--electric-share 1` and leaves out `--mpg-combined` and `--fuel-price`. A plug-in passes all five.

## Total cost of ownership

5-year cost = OTD + fuel + insurance + maintenance + repairs + registration renewals + property tax + loan interest − resale value at year 5

`python3 scripts/calc.py total-cost --price P --doc-fee F --tax-rate R --title T --plates L --years 5 --miles-per-year M --mpg-combined G --fuel-price PPG --maintenance X --repairs Y --resale-fair-value V --private-sale-discount D --registration-per-year N [--insurance ... --property-tax ... --down ... --apr ... --months ...]`

- **Loan interest:** for a financed buyer, pass `--apr` and `--months` (and `--down`). The total then includes the interest paid inside the 5 years: all of it on a loan of 60 months or less, the first 60 months of it on a longer loan. Without a rate, the total leaves interest out. Say so, and say the financed total will run higher.
- **Insurance:** use the buyer's quotes. Without quotes, leave it out and state the sensitivity: each $100 a year moves the total by $500. Insurance can swing more between models than fuel does, so push for quotes on the finalists.
- **Property or excise tax:** include it where the locale charges it, on the car's declining value each year. The value steps down geometrically from the price to the year-5 fair value, and the rate applies to each year's start-of-year value. `scripts/calc.py property-tax --price P --resale-fair-value V --rate R` builds the 5-year figure this way from a flat rate (see `locale.md`'s state data). Pass that figure to `total-cost` as `--property-tax`, and put it in the report as `propertyTax5yr`. Call the result a rough yearly estimate.
- **Maintenance:** from the factory schedule for those years, at local shop rates unless the buyer does their own work.
- **Repairs:** sum, over the model's known-failure items that fall in the 5-year window, the chance it happens in that window times the midpoint of its cost range. Check the total against published averages (RepairPal and the like) and say when it's higher or lower than average, and why.
- **Resale:** apply a published depreciation curve (for example, CarEdge) to the car's fair value, then take off a private-sale discount. Name the curve and the discount. If CarEdge or the usual source won't load, fall back to the default curve below. Label it a default curve for the segment every time it's used.
- **Registration renewals:** the locale's annual fees for the years after the first.

### Default depreciation curve (fallback only)

Use only when the usual source (CarEdge, Edmunds, KBB) won't load after one try, or for a quick first pass before the full research. Label it a default curve for the segment, separate from this car's own figures.

**By segment, bought new (5-year value retained).** Source: iSeeCars, "Cars That Hold Their Value" study, checked 2026-11-19.

| Segment | 5-year value retained |
|---|---|
| Truck | 66% |
| Hybrid | 65% |
| Small SUV | 58% |
| All vehicles (use for a sedan or any segment not listed) | 58% |
| Midsize SUV | 53% |
| Large SUV | 48% |
| EV | 43% |

Fair value at year 5 ≈ today's fair value × the segment's retention.

**For a car that's already used when bought,** apply the Bureau of Labor Statistics' used-car average instead: about 10% a year, compounded for the years remaining (BLS, Monthly Labor Review, 2024, "Americans' Aging Autos," Chart 1). Fair value after N more years ≈ today's fair value × (0.90 ^ N). This covers new versus used only.

Adjust either estimate down for a model with a known weak point or a bad reliability record, and say so.

## Rules

- **Price at asking** unless the dealer has agreed to less in writing.
- **Use ranges** when sources disagree, and name them.
- **When a number changes,** redo every total that used it with `calc.py` and say what moved.
- **Never compare a lease and a purchase on payment.** Compare total cost over the same period.
