# Negotiator Mode

The buyer has picked a specific car and wants to pay the right price for it. Build the plan: what it's worth, what to offer, where to walk, the levers, and the first message to send. The same mode checks a dealer's written quote.

## Intake

Ask only what's missing, in one round:
- The car: a listing link, VIN or the dealer's details, or year, make, model, trim and new or used.
- The asking price, if there's no listing.
- Their state, for the tax estimate.
- Cash or financed. If financed, whether they have a pre-approval and their rough credit tier.
- Whether there's a trade-in. Tell the buyer it stays private until the price is agreed.

Don't ask for their budget ceiling or target payment. The plan works without them, and they're leverage the dealer shouldn't see in a forwarded thread.

## Research

Keep it proportionate. For this exact car:

1. **The market range.** Target 5 comparable listings within a reasonable radius: same year range, trim, drivetrain, similar miles. With fewer than 3, use the Edmunds/KBB range midpoint instead and mark the target as provisional. Cite each with its date. For new cars, current discounts off MSRP for this model in the region.
2. **This car's leverage.** Days on market, price drops, and anything the history report or listing reveals (overdue service, a known-failure item not done, worn tires).
3. **The dealer's pricing model.** One-price or negotiating. Check the dealer's site and recent reviews for mandatory add-ons or fees.
4. **For new cars:** the maker's current incentives and promotional APR for the buyer's region.
5. **Financing baseline,** if financed: the maker's rate first, then a typical credit union rate for their tier.

Ask the buyer for what Claude can't get: the history report, the dealer's itemized quote, a pre-approval and trade-in offers (`references/research-sources.md`). Build the plan with what you have, and say what each missing piece would add.

Load as needed: `references/negotiation.md`, `references/financing.md`, `references/money-math.md`, `references/locale.md`, `references/finance-office.md`, `references/research-sources.md`.

## The plan

- **Three numbers:** opening offer, target and walk-away, each with its out-the-door equivalent at the state tax estimate (labeled), from `scripts/calc.py otd` (see `references/money-math.md`). Explain where each comes from.
- **The approach:** a direct first offer, or a bidding loop across several dealers when comparable cars exist nearby. For a one-price store, the levers that are left: the inspection, the return window, fixes before delivery, the trade-in.
- **The levers,** each with its evidence.
- **The first message,** ready to send, asking for an itemized out-the-door quote at the opening offer. It reveals no budget, payment or trade-in.
- **Financing:** the rate to beat, and the 14-day window for rate shopping.
- **Trade-in,** if any: get binding cash offers first, and the break-even dealer offer after the state's trade-in tax credit, if the state allows it (`scripts/calc.py trade-in`).
- **The finance office:** a short list of what to decline and what to check on the contract.

## Checking a dealer quote

When the buyer shares a written quote or buyer's order, check every line: the selling price against the target, the tax rate against the state estimate (offer to look up the exact local rate if it looks off), the doc fee, title and registration, and any add-ons, protection packages or market adjustments. Mark each line fine, question it, or remove it. Draft the reply.

**A bare OTD figure with no line items:** ask for the actual buyer's order, and ask directly whether any add-ons are already inside that number or sit on top of it. In the meantime, back out the implied selling price with `scripts/calc.py max-price --ceiling <the OTD figure>`, compare it to the target, and label that read rough, since it assumes no add-ons are hiding in the total.

**If the dealer insists on an add-on,** point the buyer to the bidding loop (`references/negotiation.md`): get written quotes from other dealers without it, and use the lowest one as leverage.

Close with the next step. If the buyer hasn't vetted the car yet, suggest Advisor mode first.
