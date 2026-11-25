# Report Mode

The buyer wants the whole picture: what to buy, how the options compare, and how to buy it. This is the heaviest mode. It works in two steps: a quick text summary of the options first, then the full report only if the buyer wants it.

## 1. Intake

**Lead with useful guidance before the questions, when the request already gives enough to offer some.** A teen-driver request, for example, gets IIHS and Consumer Reports' "Safe vehicles for teens" guidance up front: avoid small cars, high-power cars, large SUVs and pickups. Require stability control and good small-overlap crash ratings (`references/research-sources.md`). When the buyer says "safe," make it a filter on the shortlist, not one more line in the pros and cons. When a teen will be on the policy, push for insurance quotes on the finalists before the buyer decides. It can swing the real cost more than the sticker does.

Follow `references/intake.md`. Ask in short rounds, using the question tool when there is one:

1. **Round one:** state (or ZIP), new, CPO or used, what the car is for, and the budget (cash or financed, out the door or not).
2. **Round two, if needed:** must-haves, the real constraint (car seats, a tall driver, a dog, a garage spot), miles a year, and how long they keep cars.

Ask only what the shortlist needs. Fuel preferences, trade-ins, financing details and insurance quotes can wait for the full report.

## 2. The options summary (text, in chat)

Give a short summary of 3 to 5 cars that fit, from what you already know plus a few quick checks. Keep the research light here: this step is for choosing, not proving.

First survey the field from a named list that fits the criteria (IIHS's picks, Consumer Reports' recommended models, or the segment's current top sellers), and say which list. Then narrow it. When an EV or plug-in is on the shortlist, load `references/situations.md` for the federal tax-credit rules before writing anything about incentives.

- Restate the criteria in one or two lines.
- For each car: the year range and trim to target, the typical price for the buyer's condition and budget, one line on why it fits, and its main watch-out. Include at least one reliable-appliance pick. Flag any enthusiast pick as one.
- Say which one or two look strongest, and why.
- List the cars you considered and dropped, one line each with the reason (over budget, no AWD, a known transmission problem). Name any part of the field you didn't check.
- Label prices as typical ranges, not quotes.

Then offer the full report, and set expectations:

> Want the full report? I'll research each car in depth (failure modes, recalls, real listings near you, the 5-year cost, a negotiation plan and the first-year maintenance) and build it into one page you can keep. It takes a few minutes while the research runs.

Let the buyer trim or add cars first. This is the main checkpoint: it keeps the deep research on cars they actually want.

## 3. The full report (only when the buyer says yes)

Tell the buyer the research is starting, which cars it covers, and that it will take a few minutes. Cap it at 5 cars. If the shortlist runs longer, ask the buyer to trim it first.

**The orchestrator (you) owns everything shared across cars before any agent starts:**
- The state tax rate: `scripts/calc.py state --code <XX>` (top of the range), or `locale.md`'s one-search fallback when the state isn't in `states.json`. Same for the other shared assumptions: miles a year, fuel and electricity prices, the resale method.
- One number for how many comparable listings a "price against the market" read uses: target 5, the same number `modes/advisor.md` and `modes/negotiator.md` use. With fewer than 3 found, use the Edmunds/KBB range midpoint and mark that car's price read provisional.
- The per-model schema block from `references/report.md`, pasted into each agent's brief so no agent has to read the template.

**Run the research in parallel when you can.** If subagents are available, start one per car at the same time, at most about 12 searches each. Give each agent:
- The method (`SKILL.md`), for its core voice rules and principles.
- Advisor mode (`modes/advisor.md`), the buyer's criteria and state.
- The car's target year range, trim and typical price from the options summary. Advisor mode asks the buyer when a car has no price, and this is the price it needs.
- The shared assumptions and the per-model schema block above.
- The instruction: run all of advisor.md's research steps, including the ones it marks as depth to offer in chat. The buyer already asked for the full report. Where advisor.md says to ask the buyer for something, add it to a `missing` list instead of asking, and keep going. On a timeout, return whatever was found rather than nothing.
- The instruction: write every text field by `references/report.md`'s Writing rules. Never read the template. The build script checks the data.

Ask it to return its findings as structured data matching that car's entry in the report schema, with sources, plus its `missing` list. Without subagents, research the cars one after another, to the same brief.

**After every agent reports back:** merge the `missing` lists. Build with what you have, list what's still pending (a history report, an itemized quote) in the delivery, and ask the buyer for those items once. Rebuild when they arrive. Strip `missing` itself out before writing the data file. It isn't part of the report schema.

For each car:
- **Advisor research** (`modes/advisor.md`): failure modes, recalls, reliability, safety, fuel, warranty runway, price against the market, 5-year cost.
- **Listings:** 2 to 4 live listings in the buyer's region (`references/due-diligence.md`).

Then, for the cars the buyer would actually buy:
- **Negotiation plan** (`modes/negotiator.md`): target, walk-away, opening offer, levers and the first message.

For the recommended car:
- **Maintenance plan** (`modes/maintenance.md`): the 30-day list and the 12-month schedule.

Taxes and fees use the labeled state estimate unless the buyer asked for exact figures.

Once every agent reports back, run the humanizer check once over the merged text, not once per car: it catches repeated openers and phrasing that only show up across the whole set.

## 4. Build and deliver

Follow `references/report.md`: write the data file, run the build script, check the page, and publish it. Set `assumptions.localeBasis` to `"estimate"` unless exact figures were looked up.

Give the buyer the link with the key trade-offs in a few lines. If a section isn't ready (the negotiation plan, say), deliver the comparison first and add the rest in a rebuild.
