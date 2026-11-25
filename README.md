# Auto Advisor

A Claude skill for buying a car without getting taken. Think of the friend who knows cars and also keeps a spreadsheet.

I'm that friend. When someone asks me "is this a good deal?", they get the failure modes, the 5-year cost and at least one opinion they didn't ask for. This skill is that habit written down so Claude can do it. It started as a set of rules and a spreadsheet. Now it builds a web page you can keep.

It covers the whole thing, from "help me buy a car" to the first oil change.

## Four ways in

Claude picks the mode from how you start. You can also just name one.

- **Advisor.** Send a link, a VIN, or a year, make and model. You get a verdict: Good, With conditions, or Pass. You also get what breaks on that engine, what it costs when it does, how the price sits against the market, and what to check before any money moves. Ask something vague like "what do you think of a CX-5?" and it asks for the price and the miles first. A verdict without those is a guess.
- **Negotiator.** Name the car you want. You get an opening offer, a target and a walk-away price built from real comparable listings, plus the first message to send. Paste a dealer's quote and it goes through every line. The nitrogen-filled tires don't survive.
- **Maintenance.** Name the car you own or just bought, with its miles and whatever records you have. You get what's urgent, the first 30 days, and a schedule caught up against the records, with a cost and a DIY-or-shop call on each job.
- **Report.** Answer a couple of quick rounds of questions. You get a short list of cars that fit. Say yes to the full report and it researches each car in parallel, then builds one page with the comparison, the negotiation plan and the first year of ownership.

## How it thinks

- **The sticker lies and the 5-year cost doesn't.** It adds up the out-the-door price, fuel, insurance, maintenance, repairs, registration, property tax and loan interest, then subtracts what the car is worth when you sell it. A cheap car with a known four-figure failure isn't cheap.
- **It looks things up.** Prices, rates, incentives, MPG, fuel grade, recalls and warranty terms each get a source and a date. Nothing comes from memory.
- **It names what breaks.** Every model gets its known failure modes: why they happen, when they show up, and what they cost.
- **Out the door or nothing.** A monthly payment is how a price hides behind a loan term. The skill negotiates the total, with no mandatory add-ons.
- **Shop in person, buy from home.** Test drives happen at the dealer, with no numbers discussed. The negotiation happens from your couch, in writing.
- **The walk-away price is set before you talk.** It comes from the math and your next-best option. It never moves in the moment.
- **Every used car gets an independent inspection,** certified pre-owned included. The dealer's checklist was run by the dealer.
- **The finance office is for signing paperwork.** It checks the contract against the quote and declines the extras.
- **Taxes and fees start as a labeled estimate for your state.** Ask, and it looks up the exact local figures from official sources.

## It has opinions

Cars are not a neutral subject, so the skill carries a short file of what enthusiasts believe:

- Skip the first year of a redesign.
- Buy the owner, not the car.
- "Lifetime" fluid is a lie.
- Nothing is more expensive than a cheap German car.
- Miata is always the answer. To a narrow question.

Each take shows up labeled as the enthusiast view and paired with its counter. A take can tell you what to check. It never decides the verdict. That comes from the car in front of you.

## The report

The report looks like a car's window sticker: white label paper, black rules, boxed sections, and EPA-label teal for the data. Each car's 5-year cost sits on a ruled scale from the cheapest car on your shortlist to the priciest, with a "you save" or "you spend" line, the way the EPA label compares fuel costs.

It's live. Change the miles you drive, the gas price, the tax rate or the loan terms and every total moves. Type an offer and watch what it does to the out-the-door price.

It was designed with the [Impeccable](https://github.com/pbakaus/impeccable) skill.

## Why the math is code

I don't trust a language model to add. So it doesn't.

Claude writes the facts into a JSON file. A small script checks the data and merges it into a fixed template. The template draws the page and does the arithmetic in your browser.

The same formulas ship as a command-line script, `scripts/calc.py`, so a chat answer and the report page can't disagree. It computes the out-the-door price, the highest price that fits a budget, loan payments, the trade-in break-even, the walk-away price, the 5-year cost, property tax, and a state's tax row.

Claude does the research and the judgment. Code does the math and the layout.

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

## When it gets weird

Car buying has trapdoors. The skill has a playbook for each of these:

- You already signed and you're having second thoughts.
- The dealer calls three days later to say your financing "fell through."
- You're leasing.
- You're buying from a private seller.
- Your credit is rough.
- You're selling a car and not buying one.
- You're looking at an EV and someone mentioned a tax credit.

## Install

- **Claude Code:** copy the `auto-advisor` folder into `~/.claude/skills/`.
- **Claude apps:** zip the folder and upload it as a skill in Claude's settings.

Then try one of these:

- "Help me shop for a used AWD wagon under $30k out the door."
- "Is this a good buy?" with a listing link.
- "The dealer sent this quote. What's wrong with it?"

## Any state

The skill ships a sourced tax and fee reference for seven states, picked to cover very different tax rules. For every other state, it starts with a labeled estimate from one search. Either way, exact local figures come from official sources when you ask for them.

## License

MIT for the skill. The embedded Archivo font is under the SIL Open Font License (`assets/fonts/ARCHIVO-OFL.txt`).
