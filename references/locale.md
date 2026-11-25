# Locale: Estimate by Default

Taxes and fees matter to the out-the-door price, but chasing every county rule costs the buyer time. Start with a quick state-level estimate, as a range. Look up exact local figures only when the buyer asks.

## The default: a labeled state estimate

Use the buyer's state, from their ZIP or city.

- **Run `scripts/calc.py state --code <XX>` first.** It covers a handful of states in `assets/states.json`, chosen for a range of tax regimes, caps and credits rather than for population, so most buyers won't be in it yet. Never recall a rate from memory, verified or not: look it up this way, or with one search.
- **If the state is in the file:** read `combinedLow` and `combinedHigh` as a range, plus `regime`, `docFeeCap`, `tradeInCredit` and `yearlyValueTax`.
- **If the state isn't in the file:** run one search for the state's general vehicle sales (or title/excise) tax rate and whether it adds local rates on top. Show it as a range the same way, and label it unverified rather than sourced.
- **Fees:** one combined placeholder for title, registration and plates. A few hundred dollars covers most states. Say it's a placeholder.
- **Doc fee:** the state's cap from `docFeeCap` if known, otherwise a placeholder.
- **Yearly value tax on vehicles:** where `yearlyValueTax.applies` is true (or a quick search says the state charges one), include a rough figure in the totals, labeled rough, using `scripts/calc.py property-tax` with the state's `roughRate` (or the researched rate). Leave it out of the totals only when there's no rate at all to work from.
- **Trade-in tax credit:** state what `tradeInCredit` says (`yes`, `no`, or `dealer-only`), or flag it as unchecked if the state isn't in the file.

**Route these row facts into the label:**
- **`docFeeTaxed: false`:** say the OTD estimate may run a little high, by about doc fee times the tax rate (usually tens of dollars), since the math here taxes the doc fee by default.
- **`privatePartyRule` describes a state-assessed value rather than the price paid** (Georgia's TAVT, North Carolina's private-party "computer value," Texas's SPV floor on a private sale): say the figure is approximate, since it's priced off the asking price, not the state's own assessment.
- **`yearlyValueTax.applies: true` with a `roughRate` of `null`** (for example North Carolina): say the yearly value tax applies but isn't in the totals, rather than implying a rough figure is already included.
- **A yearly tax billed with registration** (California's VLF, North Carolina's "Tag & Tax Together"): count it once, in `propertyTax5yr`, never also folded into `plates` or `registrationPerYear`.

For the math itself (OTD, the budget-fit tag, the walk-away), **use the top of the range** as `assumptions.taxRate`. Understating the tax is where an estimate does real damage: a car looks like it fits the budget, or clears a walk-away, when the exact local rate would put it over. Carry the full range in `assumptions.notes` so the buyer sees both ends.

Label the estimate every time it appears, in plain words. When `combinedLow` equals `combinedHigh` (a flat state rate, no local add-on), state the one rate instead of a degenerate range like "6.25% to 6.25%":

> Taxes and fees are a state-level estimate: STATE's vehicle tax runs X% to Y% depending on locality (using Y% for the numbers below), plus about $Z for title, registration and doc fee. Exact local fees and the yearly value tax, if any, are rough until you ask me to look up your ZIP.

> Taxes and fees are a state-level estimate: STATE's vehicle tax is a flat X%, plus about $Z for title, registration and doc fee. Exact local fees and the yearly value tax, if any, are rough until you ask me to look up your ZIP.

If the state's row (or the quick search) is more than 12 months old, say so in the label: "This figure is from [month, year] and hasn't been rechecked."

In the report, set `assumptions.localeBasis` to `"estimate"` and put the same sentence in `assumptions.notes`.

## When to go deeper

Look up exact local figures only when:
- the buyer asks ("look up the exact taxes," "what will I really pay out the door"), or
- the buyer is about to sign, or is checking a dealer's written quote line by line.

Then follow `locale-detailed.md`, and keep it proportionate: the official state revenue and DMV pages first, one source per fact, and stop when the figures are found. Set `assumptions.localeBasis` to `"verified"` and cite each figure.

## Never

- Present an estimate as exact.
- Recall a rate instead of checking `states.json` or searching.
- Spend more than a couple of searches on locale in the default case.
