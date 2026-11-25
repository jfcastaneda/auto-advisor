# Financing

Financing is a separate deal from the price. Settle the price first, out the door, then let lenders compete for the loan.

## The 10% guardrail

A common rule of thumb: keep the monthly payment, loan or lease, at or below 10% of gross monthly income. The payment is only part of the cost: insurance, fuel, maintenance and any property tax come on top. When a car only fits the guardrail by stretching the loan term, it doesn't fit. Get the payment from `scripts/calc.py payment` (see `money-math.md`), never from mental math.

Check it whenever the buyer finances and shares their income. Say plainly when a car breaks it. The buyer decides.

## Order of operations

1. **Check the maker's promotional rate first.** Look up current offers for the exact model and the buyer's ZIP. Promotional APRs often require top-tier credit and may replace a cash rebate. Compare "low APR" against "rebate plus outside loan" on total cost.
2. **If the maker's rate isn't promotional,** get a pre-approval from a credit union or bank before talking to the dealer. It sets the rate the dealer has to beat.
3. **Shop rates inside 14 days.** Credit scores count multiple auto-loan inquiries in a short window as one. The window runs 14 to 45 days depending on the scoring model, so 14 days is the safe rule. Prequalification with a soft pull doesn't count at all.
4. **Let the dealer try to beat the pre-approval,** after the out-the-door price is agreed.

## Watch for

- **Rate markup.** Dealers can mark up the lender's buy rate and keep the difference. Ask for the rate in writing, and compare it to the pre-approval.
- **Payment framing.** "What payment do you want?" invites a longer term. Answer with the out-the-door price.
- **Longer terms.** 72 and 84 months lower the payment and raise total interest, and leave the buyer owing more than the car is worth for longer.
- **Packed payments.** Add-ons folded into the loan. Read the itemized contract (see `finance-office.md`).
- **Prepayment penalties.** Confirm the loan has none before signing.

## Financing to unlock a discount

Some dealers discount the price only with in-house financing. That can be worth it: take the deal if the math wins, confirm the loan has no prepayment penalty, then refinance with a credit union soon after. Run the numbers both ways first.

## Leases

See `situations.md`'s Lease section for the fees, the money factor, the residual and the capitalized cost.

## In the report

Set `financing` with down payment, months and APR, and `buyer.grossMonthlyIncome` if the buyer shares it. The report shows each car's payment and flags any car over the 10% guardrail. With a rate set, each car's 5-year cost includes the loan interest paid in those 5 years.
