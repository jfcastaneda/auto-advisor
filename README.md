# Auto Advisor

A Claude skill that works as your car-shopping advisor, from the first question to the first year of ownership. It shops the way a good analyst runs a vendor selection: criteria first, verified facts, total cost over the life of the decision, known risks priced in, and a clear recommendation you can argue with.

I built it from the method I use when friends ask me for help buying a car. It started as a set of rules for Claude and a spreadsheet. This version produces a web page you can keep.

## Four modes, one method

The method always loads: the principles for how to think about a car purchase, plus a short file of enthusiast opinions. Then Claude picks one of four modes and loads only what that mode needs.

- **Advisor.** Share a link, a VIN, or a year, make and model with new, CPO or used. You get a verdict on that buy: known failure modes, recalls, price against the market, a rough 5-year cost, warranty runway, and what to check before buying.
- **Negotiator.** Name the car you want. You get an opening offer, a target and a walk-away price from real comparable listings, the levers, and a first message to send. It also checks a dealer's written quote line by line.
- **Maintenance.** Name the car you own or just bought, with its miles and any records. You get what's urgent, the first 30 days, and a maintenance schedule caught up against its records, with costs and DIY or shop for each job.
- **Report.** Answer a couple of quick rounds of questions about what you need and your budget. You get a short text summary of the cars that fit. Say yes to the full report, and it researches each car in parallel, running Advisor, Negotiator and Maintenance, and builds one page you can keep.

## What it does

- **Starts with you.** It asks what it needs based on how you start: a vague "help me buy a car," a pasted listing, a dealer quote, or a car you just bought. It asks a few questions at a time and states its defaults.
- **Estimates your taxes and fees by state.** Every estimate is a labeled range. Ask, and it looks up the exact local figures from official sources.
- **Verifies, never recalls.** Prices, rates, incentives, MPG, fuel grade, recalls and warranty terms get a source and a check date. It knows where to look for each one.
- **Prices the risk.** Each model's known failure modes come with why they happen and what they cost.
- **Compares on total cost.** Out-the-door price, fuel, insurance, maintenance, repairs, registration, property tax and loan interest, minus resale. Financed buyers see each payment against a 10% of income guardrail.
- **Vets real cars.** Reads history reports line by line and insists on an independent inspection, certified pre-owned included.
- **Negotiates your way.** Shop in person, buy from home. Out-the-door quotes in writing, leverage kept private, a walk-away price set before talking, and trade-ins and financing handled as separate deals.
- **Gets you through the finance office.** Checks the contract against the quote and declines the add-ons.
- **Plans the first year.** The 30-day paperwork and checks, then the maintenance due in the first 12 months for the car you buy.
- **Builds the report.** One HTML page with an overview, a section per car, a section named for your real constraint, listings, negotiation, the first year and the recommendation.
- **Has a point of view.** It knows what enthusiasts believe: skip the first year of a redesign, buy the owner, slow car fast. Each take comes labeled, with its counter, and never decides a verdict.
- **Covers the edge cases.** A signed contract, a spot-delivery call-back, a lease, a private-party sale, bad credit, an EV, or a trade-in with no new car yet: each has its own playbook.

## The design

The report is designed like a car's window sticker: white label paper, black rules, boxed sections, and EPA-label teal for data. Each car's 5-year cost sits on a ruled scale from the cheapest car on the shortlist to the priciest, with a "you save" or "you spend" line, the way the EPA label compares fuel costs. It was designed with the [Impeccable](https://github.com/pbakaus/impeccable) skill.

## How the report is built

Claude writes the facts into a JSON file. A small script checks the data and merges it into a fixed template. The template draws the page and does the arithmetic in the browser.

The same money math backing that template also ships as a command-line script, `scripts/calc.py`. Chat answers and the report page run the same formulas, so they never disagree. It computes the OTD price, the max price for a budget, loan payments, the trade-in break-even, the walk-away price, 5-year total cost, property tax, and a state's tax row.

That split matters. The language model handles research and judgment. Code handles the math and the layout. Every report looks the same, and no total depends on a model adding numbers in its head.

```
auto-advisor/
  SKILL.md                         The method and the mode router (always loads)
  modes/
    advisor.md                     Analyze one car: a link, a VIN or a year/make/model
    negotiator.md                  Plan the negotiation for a car you want, or check a quote
    maintenance.md                 What a car needs and when, caught up against its records
    report.md                      Options summary, then the full research and buyer's report
  references/                      Loaded only when a step needs them, except the first
    enthusiast-opinions.md         What enthusiasts believe, each take with its counter (always loads)
    intake.md                      The full intake for Report mode
    locale.md                      Taxes and fees as a labeled state estimate
    locale-detailed.md             Exact local figures, only on request
    research-sources.md            Where to look up each kind of fact
    money-math.md                  OTD, fuel, 5-year cost
    due-diligence.md               Listings, history reports, inspections
    negotiation.md                 Targets, walk-away prices, levers, trade-ins
    financing.md                   The 10% guardrail and rates
    finance-office.md              The contract and the add-ons
    situations.md                  Already signed, spot delivery, leases, private-party, bad credit, trade-in only, EVs
    report.md                      How to build the report, and the data schema
  assets/
    report-template.html           The page
    sample-data.json               Example data
    states.json                    Tax and fee reference for the states that have been researched
    fonts/                         Archivo (SIL Open Font License), embedded at build time
  scripts/
    build_report.py                Checks the data and builds the page
    calc.py                        The skill's money math, as a command line tool
```

## Install

- **Claude Code:** copy the `auto-advisor` folder into `~/.claude/skills/`.
- **Claude apps:** zip the folder and upload it as a skill in Claude's settings.

Then ask things like "help me shop for a used AWD wagon under $30k out the door," or "build the report for the three we picked."

## Any state

The skill ships a sourced tax and fee reference for seven states, chosen for a range of tax regimes rather than for population. For every other state, it starts with a labeled one-search estimate. Either way, it looks up exact local figures from official sources only when you ask.

## License

MIT for the skill. The embedded Archivo font is under the SIL Open Font License (`assets/fonts/ARCHIVO-OFL.txt`).
