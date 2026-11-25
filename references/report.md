# The Buyer's Report

One self-contained HTML page. Claude writes the data. The template draws the page and does the math. That keeps every report consistent and keeps the arithmetic out of prose.

The design follows a car's window sticker: white label paper, black rules, boxed sections, and EPA-label teal for data. Change the template only to fix a bug or extend the system.

## When to build it

When the buyer asks for it, or when the shortlist settles and they want something to keep. Rebuild it at each later stage: new listings, the negotiation plan, the purchase, the first-year plan.

Report mode (`modes/report.md`) runs the intake and research. Taxes and fees use the labeled state estimate from `locale.md` unless the buyer asked for exact figures. Gather only what's still missing. State any defaults on the page, in `assumptions.notes`.

## Writing

Every text field in the data follows SKILL.md's Writing rules, since the buyer reads each one on the page. Report text also follows the style list and humanizer check below.

**Style, on top of SKILL.md's Voice rules.**
- Use the fewest words that fully answer the question.
- Give one instruction per sentence.
- Keep the articles: "the car," "a dealer."
- Use one word for one thing. If it's the "walk-away price," don't also call it the "ceiling."
- Pick the common word over the technical one: out-the-door (OTD) price, certified pre-owned (CPO), APR, doc fee, pre-purchase inspection.

**Light humanizer check.** Before sending, read the output once and fix these:
- Filler openers and closers: "Great question," "It's worth noting," "In today's market," "I hope this helps," a recap of what you just said.
- Hype and AI words: delve, robust, seamless, unlock, game-changer, navigate (outside driving), landscape, crucial, elevate, empower.
- Hedging stacks: "it may potentially be possible." Say it once, with the real level of confidence.
- Jargon left unexplained.
- Bold, headers and bullets on a short answer that reads better as two sentences.

One pass is enough. Fix what you find and send. Don't rewrite numbers, sources or the buyer's own words.

## How to build it

1. Run `python3 scripts/build_report.py --init <data.json>` to write a starting data file, then fill in the buyer's data. The schema is below. `assets/sample-data.json` shows a filled-in example. Every price, MPG figure, fee and rating needs a source in that model's `sources` list.
2. Run `python3 scripts/build_report.py <data.json> <report.html>`. The script checks types, units and ranges, and stops with a list of fixes when anything would put a wrong number on the page. Fix the data, not the script. Lines that start with "Check:" are warnings: look at each one before delivering.
3. Open the page and check it: every tab loads, the totals look sane, every link works.
4. Deliver it. When an artifact tool is available, publish the page as an artifact so the buyer gets a link to keep. Otherwise send the file.
5. In chat, give the key trade-offs in a few lines and offer to adjust.

When something changes (a new listing, an agreed price), edit the data file and rebuild. Never hand-edit the HTML.

## Sections

The page has a side rail on wide screens and a scrolling tab bar on phones.

- **Overview.** The stage the buyer is in, the recommendation in one line, a short summary, the side-by-side table, and the live assumptions. Each row shows its 5-year cost on a scale from the cheapest car to the priciest. Cash buyers also see the highest asking price that fits the budget.
- **One section per model.** A sticker header (5-year cost, out-the-door price, MPG, fuel, warranty runway) with the save/spend scale, then the money broken out, strengths, watch-outs, known failure modes with costs, safety, reviews, the inspection checklist and walk-away triggers, and sources.
- **A section named for the real constraint.** Car Seat Fit, Headroom, Dog Cargo, Warranty Runway, or whatever decides it.
- **Listings.** Live cars, with the dealer's pricing model.
- **Negotiate.** Per car: asking, target, walk-away and opening offer, the levers, and a first-message script. An offer input recalculates that car everywhere on the page.
- **First year.** For the recommended or purchased car, from Maintenance mode: the 30-day list and the 12-month schedule with a cost range.
- **Recommendation.** The pick, the reasons, what to skip and why.

## Live assumptions

The overview has inputs for miles a year, regular and premium prices, the tax rate and the private-sale discount, plus the loan terms for financed buyers. The Negotiate section has an offer input per car. Changing any input recalculates every total on the page.

## Data schema

```
title                     Report title
stage                     "needs" | "shortlist" | "listings" | "negotiate" | "first-year"
buyer.location            "City, ST"
buyer.zip                 Optional
buyer.grossMonthlyIncome  Optional. With financing, the report checks the 10% payment guardrail.
buyer.role                The car's role
buyer.budget              { amount, type: "cash" | "financed", otd: true | false }
buyer.criteria            List of short strings
summary                   List of short paragraphs for the overview
prepared                  { date }
assumptions               { years, milesPerYear, regular, premium, taxRate, docFee,
                            title, plates, registrationPerYear, privateSaleDiscount,
                            electricity,
                            localeBasis: "estimate" | "verified",
                            notes: [strings], sources: [{ title, url }] }
                          years is always 5: the cost fields are 5-year totals.
                          taxRate and privateSaleDiscount are fractions (6.25% is 0.0625).
                          electricity is $ per kWh, blended home and public charging.
                          It's required when any model charges.
financing                 { down, months, apr }   apr is a percent (6.5 means 6.5%), or null
                          until there's a rate. A financed budget shows the payment column
                          either way, and the buyer can type the rate on the page.
                          With a rate, each 5-year cost includes the loan interest paid
                          in those 5 years. Without one, the page says interest is left out.
constraint                { name, intro, columns: [strings] }
models[]                  {
  id, name, year, trim, condition ("New" | "CPO" | "Used"),
  spectrum                1 (reliable appliance) to 5 (premium, maintenance tax)
  spectrumNote
  price, priceNote        Asking price and where it came from
  mpg                     { city, hwy, combined }   Not for an electric car.
  fuelGrade               "regular" | "premium" | "premium-recommended" | "electric"
  kwhPer100               kWh per 100 miles. Required for "electric" and for a plug-in hybrid.
  electricShare           Plug-in hybrids only: the share of miles on electricity (0 to 1).
                          Its fuelGrade is the gas the engine takes.
  extraRegistrationPerYear Optional. A yearly EV or hybrid road-use fee, where the state charges one.
  maintenance5yr          Number
  insurance5yr            Optional, all or none. From the buyer's quotes. Set it on every model
                          or on none: a model without it would look cheaper. Without it, the
                          page states the sensitivity.
  insuranceNote           Optional. Where the quotes came from.
  propertyTax5yr          Optional, all or none. Where the locale charges a yearly vehicle tax.
  propertyTaxNote         Optional. The rate and how it was applied.
  repairs5yr              Number (midpoint)
  repairsNote             The range and how it was built
  resaleFairValue5yr      Fair value at year 5, before the private-sale discount
  resaleNote              The curve used
  warranty, warrantyRunway
  story                   List of paragraphs
  strengths, watchouts    Lists of strings
  failureModes            [{ item, why, cost, status }]
  safety                  { nhtsa, iihs }
  reviews                 [{ title, source, url, summary }]
  constraint              List of values, one per constraint column
  inspection, walkAway    Lists of strings
  sources                 [{ title, url, checked }]   Each needs an http(s) url and a checked date.
}
listings                  [{ model (id), dealer, price, miles, pricing, url, checked, notes }]
negotiation               { intro, cars: [{ model (id), target, walkAway, opening,
                            levers: [{ lever, evidence }], script: [strings] }] }
                          opening <= target <= walkAway.
firstYear                 { model (id), intro, first30: [strings],
                            schedule: [{ when, task, why, who ("DIY" | "Shop"), cost, low, high }],
                            sources: [{ title, url, checked }] }
recommendation            { pick (id), paragraphs: [strings], avoid: [strings] }
```

`negotiation`, `firstYear` and `listings` are optional. Their sections appear once the data has them.

Model ids use only letters, digits, `-` and `_`. Every money field is a plain number, never a string like "27,400". Every list field is a list, even with one item: `summary`, `story`, `strengths`, `script` and the rest. The build stops on a bare string.

## How the page labels estimates

Totals that rank cars are estimates, so the page shows them to the nearest $100 and says "About". Cars within $100 of the cheapest count as tied. While `localeBasis` is `"estimate"`, every out-the-door price carries an "est." mark, and a car within 3% of the budget gets a "Just under budget" or "Just over budget" tag instead of a firm one. The money table on each car's page keeps exact figures, so the rows still add up.

If the page fails to draw, it shows an error message instead of a blank sheet. A viewer that blocks scripts sees the summary, the recommendation and each car's asking price.
