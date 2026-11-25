# Maintenance Mode

The buyer owns a car, has just bought one, or is about to. Tell them what it needs and when: the first 30 days, then the maintenance ahead, caught up against its records. Report mode uses this for the recommended car.

## Intake

Ask only what's missing, in one round:
- Year, make, model, and the engine and transmission if they know them. A VIN settles all of it.
- Current miles.
- Service records, if they have them: receipts, a dealer printout, or the history report (ask the buyer to share it, see `references/research-sources.md`). Without records, say every item's history counts as unknown.
- How they drive: miles a year, short trips, towing, extreme heat or cold. These can put the car on the maker's severe schedule.
- Whether they do their own work, use a shop, or both.
- Their state, only if inspections or registration deadlines come up.

## Research

Keep it proportionate (see the method's Research depth). For this exact year, engine and transmission:

1. **The factory schedule** from the maker's owner site or the owner's manual. Cite it. Note whether normal or severe service applies, and why.
2. **Known failure items** for this drivetrain and mileage range: the signs, what to do, and what it costs.
3. **Recalls and service bulletins** by VIN, or by model year without one.
4. **Fluid and part specs:** oil spec and capacity, coolant type, transmission fluid, spark plugs, filters. Each verified against the manual or the maker. Never write a part number that hasn't been checked.
5. **Warranty windows** still open, by date and miles, so covered checks happen inside them.

Load as needed: `references/research-sources.md`, `references/money-math.md`.

## The plan

**First 30 days** (for a car just bought):
- Paperwork the state requires: title, registration, plates or a plate transfer, any local sticker, and insurance. Check the deadlines with one quick lookup.
- Recalls by VIN.
- Inspections the state requires, and their due dates.
- Dealer promises still owed in writing: fixes, a second key, accessories.
- If financed: the first payment set up, no prepayment penalty confirmed, and refinancing revisited if the dealer rate was high.
- Warranty and CPO registration, if the maker asks for it.
- A baseline: miles, tire tread by position, brake pad thickness if known, a battery test, fluid levels and condition, and a fault-code scan. Later checks compare against it.
- Spare keys, the owner's manual and the wheel lock key, if missing.

**The schedule** (first 12 months or 12,000 miles by default, longer if the buyer asks):
- Line the records up against the factory schedule. Mark each item done, due, overdue or unknown.
- Catch up anything overdue or unknown first. An unknown item with a cheap service gets redone, since a cheap redo beats a guess.
- Add the known failure items that fall in this window, with their signs.
- For each item: when (miles or months, whichever comes first), what, why, DIY or shop, a cost range, and the part or fluid spec.
- Label any interval tighter than the factory one as the buyer's own, with the reason, such as 5,000-mile oil changes on a direct-injection turbo that sees short trips.
- Give a total cost range for the period.

## The answer

Lead with what's urgent: anything overdue, any recall, any warning sign. Then the 30-day list and the schedule as a table in time order. Close with the next item due and when.

## In the report

The First year section shows the 30-day list, then the schedule in time order, with a total cost range for the year (`firstYear` in the data, see `references/report.md`).
