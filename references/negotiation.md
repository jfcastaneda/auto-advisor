# Negotiation and Trade-ins

## Two phases

- **Shopping phase, in person.** Test drives, sitting in cars, checking car seat fit. Tell the salesperson up front that no numbers will be discussed on this visit.
- **Buying phase, from home.** Quotes and negotiation by email, text or phone, in writing. Nobody negotiates well under a sales manager's clock.

## Before the first contact

- **Know the pricing model.** One-price stores don't negotiate on price. There, the levers are the inspection, the return window, fixes before delivery and the trade-in.
- **Build the market range.** Target 5 comparable listings (same year range, trim, drivetrain, similar miles) within the buyer's search radius, plus current discounts off MSRP for new cars. With fewer than 3, use the Edmunds/KBB range midpoint instead and mark the range provisional. Cite each with its date.
- **Ignore invoice.** Invoice isn't the dealer's cost: holdback, marketing allowances and volume bonuses sit underneath it. Anchor to real transaction prices, days on market and the out-the-door total. On high-supply models, dealers often sell below invoice. Check this month's transaction prices before assuming it.
- **Set three selling prices per car.** The report's `opening`, `target` and `walkAway` fields hold selling prices, and the template adds tax and fees on top.
  - **Target:** a price the comparables support.
  - **Walk-away:** the lowest of (a) the top of the comparable range plus fees, (b) the buyer's budget, and (c) the next-best car's equivalent price plus what the buyer says the preference is worth. If there is no next-best car, use (a) and (b). Run `scripts/calc.py walk-away` (see `money-math.md`): it works all three out the door and hands back the selling price to store. For (c), pass both cars' 5-year totals on the same basis: both with loan interest, or both without. Set it before any contact, and keep it.
  - **Opening offer:** below the target by enough to leave room. On high-supply new models, current market discounts often run several percent off MSRP. Use this month's data, not a rule of thumb.
  - **If the walk-away comes out below the target,** the car costs more than the buyer will pay. Say so, then either lower the target to the walk-away or drop the car. Never raise the walk-away to clear the target.

## Two ways to run it

- **Make the first offer.** Send an assertive opening offer, backed by the comparables, and ask for an itemized out-the-door quote at that price.
- **Run a bidding loop.** Ask several dealers for written, itemized out-the-door quotes on the same car (same trim, options, color flexibility). Share the lowest written quote with the others and ask them to beat it. Repeat until no one moves.
- **If a dealer won't quote remotely,** don't negotiate on their terms. Get a printed buyer's order in person, photograph it, and leave without negotiating. Compare it against the market range from outside the building.

## Rules

- **Negotiate the out-the-door price.** Require an itemized breakdown: selling price, tax at the buyer's local rate, title and registration, the doc fee, and zero mandatory add-ons. Check each line against the state estimate, and look up the exact local rate if a line looks off (see `locale.md`).
- **Keep leverage private.** Don't share the target payment, the budget ceiling, the down payment or the trade-in until the out-the-door price is agreed.
- **Never negotiate the monthly payment.** It moves with the term.
- **Treat suspiciously low listings as unverified.** A listing priced thousands under the local market usually hides a high doc fee, mandatory add-ons, or a financing requirement. Get the itemized out-the-door quote before driving anywhere.
- **Get every promise in writing:** the price, fixes before delivery, the return window, CPO terms, included accessories.
- **Be willing to walk.** No single car is worth breaking the walk-away price. There's always another one.
- **Never count a target as agreed** in the money math until the dealer agrees in writing.

## Trade-ins

- **A separate deal.** Bring it up only after the out-the-door price is settled.
- **Get binding cash offers,** not estimates. Written offers from online buyers (Carvana, CarMax and others) are the baseline. Valuation guides aren't offers.
- **Count the trade-in tax credit,** where the buyer's state taxes only the price minus the trade (check `locale.md`). A dealer trade saves the tax on the trade value, so a dealer offer matches an outside offer at: outside offer ÷ (1 + tax rate). Show that break-even (`scripts/calc.py trade-in`, see `money-math.md`).
- **Still push the dealer to match the outside offer on top of the tax credit.** The credit is the buyer's, not the dealer's concession.
- **Know the payoff.** If the buyer owes more than the trade is worth, show the negative equity separately. Never roll it in silently.

## In the report

The Negotiate section lists each car's asking price, target, walk-away and opening offer, the levers with their evidence, and a first message. The buyer can type an offer and see its out-the-door price and 5-year cost update.
