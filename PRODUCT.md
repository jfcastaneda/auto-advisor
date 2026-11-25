# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

A person shopping for a car for themselves. They run the skill in Claude and use it as their own car-shopping advisor from first question to the first year of ownership. They may or may not be a car person.

## Product Purpose

Auto Advisor is a car-buying advisor. It asks what the buyer needs, researches models, finds listings, helps negotiate, and advises on the first year of maintenance for the car they buy. The buyer's report is the durable output: one page that holds the comparison, the money math, the risks, and the recommendation.

Success: the buyer picks a car with the total cost and the known risks in view, pays a fair price, and knows what the car needs in its first year.

## Positioning

Every changing fact is verified and cited with a check date. Known failure modes are priced into the cost. The 5-year cost of ownership, not the sticker, drives the comparison. Claude writes the facts; code does the math and the layout, so no total depends on a language model's arithmetic. The skill also carries a short file of enthusiast opinions, each labeled and paired with its counter, which never decide a verdict.

## Operating Context

The buyer reads the report on screen, on a phone or a laptop. It is a single self-contained HTML page built from a JSON data file and a fixed template, usually published as a Claude artifact link. The buyer changes live assumptions (miles a year, fuel prices, tax, loan rate) and every total updates. The report gets rebuilt as the search moves: new listings, a negotiated price, a purchase.

## Capabilities and Constraints

- Stack: static HTML, CSS, and vanilla JavaScript in one file. No build step, no framework, no external requests at view time.
- Data comes from `assets/sample-data.json` against the schema in `references/report.md`. The template must render any number of models (typically 2 to 5).
- Sections: Overview, one per model, a section named for the buyer's real constraint, Listings, Negotiate, First year, and the recommendation.
- The money math also ships as `scripts/calc.py`, with the same formulas as the template. Tests in `tests/` hold the two together.
- Screen only. Print is a basic fallback.
- Voice is a neutral tool. No personal sign-off.

## Evidence on Hand

Only the sample data, which is fictional and labeled as such. Do not invent real model names, prices, ratings, reviews, or dealer claims in samples.

## Product Principles

1. The total cost decides, not the sticker.
2. Every number shows its source and its date.
3. Risks are named and priced, never hidden.
4. The buyer can test their own assumptions without asking.
5. The recommendation is clear and arguable.
