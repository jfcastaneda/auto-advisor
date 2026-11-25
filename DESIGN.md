---
name: Auto Advisor
description: The buyer's car report, set as an honest window sticker that leads with the 5-year cost.
colors:
  paper: "#ffffff"
  ground: "#e9eeed"
  ink: "#111417"
  ink-2: "#374044"
  muted: "#57626a"
  hair: "#cdd5d4"
  teal: "#0a6a76"
  teal-ink: "#08535c"
  teal-tint: "#dcefef"
  amber: "#c98a12"
  amber-ink: "#7d4b00"
  amber-tint: "#fbeccc"
  red-ink: "#9d2219"
  red-tint: "#f9e0dc"
  green-ink: "#1c6234"
  green-tint: "#dff0e3"
typography:
  display:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "46px"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "-0.01em"
    fontFeature: "tnum, lnum"
    fontVariation: "'wdth' 72"
  headline:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "30px"
    fontWeight: 800
    lineHeight: 1.1
    letterSpacing: "-0.005em"
    fontVariation: "'wdth' 75"
  title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "22px"
    fontWeight: 800
    lineHeight: 1.15
    fontVariation: "'wdth' 78"
  title-band:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 800
    letterSpacing: "0.01em"
    fontVariation: "'wdth' 80"
  figure:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 800
    fontFeature: "tnum, lnum"
    fontVariation: "'wdth' 85"
  shell-title:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    fontVariation: "'wdth' 85"
  body:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
    fontVariation: "'wdth' 100"
  body-table:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tnum, lnum"
  body-sm:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  button:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "13.5px"
    fontWeight: 700
  section-head:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "12.5px"
    fontWeight: 700
    letterSpacing: "0.08em"
    fontVariation: "'wdth' 75"
  tag:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 700
    fontVariation: "'wdth' 85"
  label:
    fontFamily: "Archivo, Helvetica Neue, Arial, sans-serif"
    fontSize: "11.5px"
    fontWeight: 700
    letterSpacing: "0.07em"
    fontVariation: "'wdth' 75"
rounded:
  none: "0px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "14px"
  lg: "18px"
  gap: "24px"
  xl: "32px"
  rail: "228px"
components:
  shell:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.shell-title}"
    height: "54px"
    padding: "0 20px"
  sample-banner:
    backgroundColor: "{colors.amber-tint}"
    textColor: "{colors.amber-ink}"
    typography: "{typography.body-sm}"
    padding: "6px 20px"
  sheet:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "0"
  section-head:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.section-head}"
    padding: "6px 14px 5px"
  section-body:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: "16px 18px 18px"
  label-cell:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    padding: "10px 14px 11px"
  band:
    backgroundColor: "{colors.teal}"
    textColor: "{colors.paper}"
    typography: "{typography.title-band}"
    padding: "8px 18px"
  table-head:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    typography: "{typography.label}"
    padding: "9px 12px"
  table-total-row:
    backgroundColor: "{colors.teal-tint}"
    textColor: "{colors.ink}"
    typography: "{typography.body-table}"
    padding: "9px 12px"
  button:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "7px 12px"
  button-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    padding: "7px 0"
  button-ghost-hover:
    textColor: "{colors.teal-ink}"
  input:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.none}"
    padding: "7px 9px"
  input-invalid:
    backgroundColor: "{colors.red-tint}"
    textColor: "{colors.ink}"
  tag-good:
    backgroundColor: "{colors.green-tint}"
    textColor: "{colors.green-ink}"
    typography: "{typography.tag}"
    padding: "1px 7px 2px"
  tag-warn:
    backgroundColor: "{colors.amber-tint}"
    textColor: "{colors.amber-ink}"
    typography: "{typography.tag}"
    padding: "1px 7px 2px"
  tag-bad:
    backgroundColor: "{colors.red-tint}"
    textColor: "{colors.red-ink}"
    typography: "{typography.tag}"
    padding: "1px 7px 2px"
  tag-info:
    backgroundColor: "{colors.teal-tint}"
    textColor: "{colors.teal-ink}"
    typography: "{typography.tag}"
    padding: "1px 7px 2px"
  rail-link:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    typography: "{typography.body}"
    padding: "7px 20px"
  rail-link-hover:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
  rail-link-active:
    backgroundColor: "{colors.teal-tint}"
    textColor: "{colors.teal-ink}"
  tab:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink-2}"
    padding: "11px 13px 10px"
  tab-active:
    textColor: "{colors.ink}"
  scale-track:
    backgroundColor: "{colors.paper}"
    height: "12px"
  scale-track-lg:
    backgroundColor: "{colors.paper}"
    height: "18px"
  scale-fill:
    backgroundColor: "{colors.teal-tint}"
  spectrum-step:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.muted}"
    height: "26px"
  spectrum-step-on:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  offer-out:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.figure}"
    padding: "8px 12px"
  script:
    backgroundColor: "{colors.ground}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: "12px 14px"
---

# Design System: Auto Advisor

## Overview

**Creative North Star: "The Honest Window Sticker"**

The report reads like the window sticker every buyer already trusts. It fuses two real labels. The Monroney price label gives it white paper, black frames, ruled cells and reversed black heading bars. The EPA fuel economy label gives it teal, the big condensed figures and a ruled scale. The sticker here tells the full 5-year cost, not just the price.

This is an Operate surface. It is dense and quiet. White sheets sit on a pale cool ground. Black 2px frames box each sheet. Every section opens with a black bar in condensed capitals. Facts sit in ruled cells with a small label above a firm value. Figures use tabular numerals so columns line up. Teal is the one working color. It marks data, selection and the scale. Amber, red and green only report status.

The direction contract names one confirmed anti-reference. The report refuses soft rounded comparison cards with a single blue accent.

**Key Characteristics:**
- White label paper on a pale cool ground, framed in 2px black.
- Reversed black section bars with condensed uppercase titles.
- Ruled label cells: small condensed label over a 600-weight value.
- One Archivo variable face. Condensed for headings, labels and big figures. Normal width for reading.
- Tabular, lining figures for every number.
- Square corners everywhere.
- Teal carries data, selection and the save/spend scale.
- Status colors come as ink-on-tint pairs with a 1px border.

## Colors

A black-and-white label palette with one EPA teal and three status pairs.

### Primary
- **EPA Label Teal** (`teal`): Carries data and selection. It fills the model band, the stage meter, the scale marker and the focus ring. Text selection uses it too.
- **Deep Label Teal** (`teal-ink`): Teal as text. Links, the active rail item, the combined MPG figure and the "you save" amounts use it.
- **Teal Wash** (`teal-tint`): The quiet teal surface. It fills the active rail item, the info tag, the total rows in money tables and the scale fill up to the marker.

### Neutral
- **Label Paper** (`paper`): Every sheet, input, button and table head. Also the text color on black bars and the teal band.
- **Cool Ground** (`ground`): The page behind the sheets. Also the rail hover and the negotiation script box.
- **Sticker Ink** (`ink`): Body text, the shell header, section bars, all frames and rules, and the selected spectrum step.
- **Second Ink** (`ink-2`): Secondary text, table header labels, field labels and resting rail links.
- **Fine Print** (`muted`): Cell labels, scale end labels, metadata and footnotes.
- **Hairline** (`hair`): Light rules between table rows and list items. Also the empty stage segments.

### Status
- **Watch-out Amber** (`amber`): Only the diamond mark on watch-out lists. It is a shape fill, never text.
- **Amber Ink / Amber Tint** (`amber-ink`, `amber-tint`): The warn tag, the sample banner, and the payment tag when it's over the 10% income guardrail. The guardrail is a common rule of thumb, so a payment over it reads as a caution, in the same tone as the near-budget tag.
- **Over-budget Red Ink / Red Tint** (`red-ink`, `red-tint`): The bad tag, the walk-away marks, field errors and the invalid input fill.
- **Under-budget Green Ink / Green Tint** (`green-ink`, `green-tint`): The good tag and the copy confirmation.

### Named Rules
**The One Working Color Rule.** Teal is the only hue that carries data or selection. Amber, red and green report status and nothing else. No second accent joins them.

**The Status Pair Rule.** A status color always arrives as its ink on its tint, with a 1px border in the ink. Status is never a lone colored word.

**The Ink Frame Rule.** Structure is drawn in black. Sheets, section seams and scale tracks use `ink`. `hair` only separates rows inside a section.

## Typography

**Display Font:** Archivo variable (with Helvetica Neue, Arial, sans-serif)
**Body Font:** Archivo variable, same file, normal width
**Label Font:** Archivo variable, condensed to 75% width

**Character:** One grotesque does all the work, as on a real sticker. The width axis separates the roles. Condensed and heavy for names, figures and labels. Normal width and regular weight for reading.

The template embeds Archivo as a base64 WOFF2 at build time (`assets/fonts/archivo-latin-wdth-normal.woff2`, SIL OFL). It declares weights 100 to 900 and widths 62% to 125%. The page makes no font request at view time.

### Hierarchy
- **Display** (800, 46px, line-height 1, 72% width): The 5-year cost on a model sticker. Drops to 40px below 860px.
- **Headline** (800, 30px, line-height 1.1, 75% width): The view title. Balanced wrapping. Drops to 26px below 860px.
- **Title** (800, 22px, line-height 1.15, 78% width): The recommended car's name. Drops to 19px below 860px.
- **Title band** (800, 18px, 80% width): The car name in the teal band.
- **Figure** (800, 18px, 85% width): Outputs in the offer box. Drops to 16px below 860px.
- **Body** (400, 15px, line-height 1.5, normal width): Reading text. Prose blocks cap at 70ch.
- **Body table** (400, 14px): Table cells.
- **Body small** (400, 13px): Notes, hints, metadata.
- **Section head** (700, 12.5px, 0.08em tracking, uppercase, 75% width): Text in the black section bars.
- **Label** (700, 11.5px, 0.07em tracking, uppercase, 75% width): Cell labels, table headers, field labels, rail group labels.
- **Tag** (700, 12px, 85% width): Status tags.

### Named Rules
**The Width Axis Rule.** Condensed width means "name or label". Normal width means "read this". Do not set a paragraph condensed. Do not set a label at normal width.

**The Tabular Figures Rule.** Every number uses tabular, lining figures. Money right-aligns in its column.

**The Label Owns a Value Rule.** Uppercase condensed text names a field or a section bar. It always sits directly on the value or block it names. It never floats above a headline as a kicker.

## Layout

The page is a sticky black shell, then a rail and a main column.

- **Shell.** A 54px black bar sticks to the top. It holds the brand mark, a thin divider, the report title and the update date.
- **Rail above 860px.** A 228px white rail sits on the left with a 1px hairline edge. It sticks under the shell and scrolls on its own. Links fall into named groups: Decide, Cars, Buy, Own. Each car link shows its 5-year cost in small tabular figures. The rail reorders cars by cost whenever the totals change.
- **Main column.** Padding is 28px 32px 56px. Each view caps at 1180px. Sheets stack with a 24px gap.
- **Overview grid.** At 1260px and wider, the assumptions sheet takes a 300px right column. Below that it stacks under the main sheets.
- **Splits.** Paired sections sit in a two-column split, seamed with 2px black rules.
- **Label cells.** Cells auto-fit at a 150px minimum. Each cell draws its own right and bottom 1px rule and overlaps its neighbor by 1px, so the grid reads as one ruled sheet.
- **At 1100px and below.** The model sticker top stacks. The fuel economy block moves under the cost block with a 2px top rule.
- **At 860px and below.** The rail hides. A white tab bar sticks under the shell and scrolls sideways with no scrollbar. Main padding drops to 18px 14px 40px. Splits go to one column. The comparison and listings tables become stacked rows: each row is a block, and each cell shows its label from `data-label` on the left and its value on the right. The car name and the scale cell span the full width. Label cells drop to two columns. The shell hides the date and divider.
- **Rhythm.** Section bodies pad 16px 18px 18px (14px on phones). Cells pad 10px 14px 11px. Table cells pad 9px 12px.

## Elevation & Depth

The system is flat. It uses no drop shadows. Depth comes from paper on ground, from 2px black frames, and from reversed black bars. The shell and rail stay put on scroll, which gives the only sense of layering. The active rail link draws a 1px inset teal ring (`box-shadow: inset 0 0 0 1px`). That ring works as a border, not a shadow.

### Named Rules
**The Printed Label Rule.** Surfaces are flat paper. A frame, a bar or a tint shows hierarchy. Nothing lifts or floats.

## Shapes

Every corner is square (`rounded.none`). Inputs and buttons reset the browser radius to 0. Borders come in three weights. 2px black frames sheets and seams sections. 1.5px black outlines inputs, buttons, the scale track, the spectrum, the offer box and the script box. 1px draws cell rules, tag borders and hairline row dividers. List marks are small solid squares. The watch-out mark is the same square turned 45 degrees into a diamond. The scale marker is a small downward teal triangle.

## Components

### Sticker Sheet
The base container. A white sheet with a 2px black frame. It holds a stack of sections. Each section after the first opens with a 2px black top rule. A sheet never has padding of its own; its sections and cells pad themselves.

### Section Bar
A reversed black bar that heads every section. White condensed capitals at 12.5px, padded 6px 14px 5px. An optional aside on the right gives a short instruction in a lighter, wider, sentence-case style. The aside hides below 860px.

### Label Cells
A ruled grid of facts, like the boxes on a price label. Each cell has a condensed uppercase label in `muted` over a 600-weight value. The overview header uses it for budget, price ceiling, role, location and stage. The stage cell carries a five-segment meter: teal segments up to the current stage, hairline gray after.

### Save/Spend Scale (signature)
Each car's 5-year cost sits on a ruled scale from the cheapest to the priciest car in the set.
- **Track:** 12px tall (18px on the model sticker), white, 1.5px black outline.
- **Ticks:** nine real 1px black tick elements at 10% steps, drawn above the fill.
- **Fill:** teal tint from the left edge up to the marker.
- **Marker:** a teal triangle pointing down at the track. In the comparison table it carries the total above it in 800-weight tabular figures. The marker clamps 28px inside each end so its label never clips.
- **Ends:** the cheapest and priciest totals in small muted figures. In the comparison table only the first row shows them.
- **Line:** under the scale, a delta reads "Lowest 5-year cost" (or "Tied for lowest 5-year cost") in teal ink, or "+$X vs. the cheapest". On the model sticker a full sentence reads "About $X less" or "About $X more" with the amount in teal ink. Totals round to $100, and cars within $100 of the cheapest count as tied.
- **Motion:** marker and fill glide over 480ms on `cubic-bezier(0.16, 1, 0.3, 1)` when assumptions change. Reduced motion turns this off.
- **Access:** each scale carries `role="img"` and a label with the cost and the range.

### Model Band
A teal bar at the top of each car's sticker and negotiation sheet. The car name in condensed 800 white on the left, condition and fuel grade on the right. It wraps on narrow screens. When the band is a link, it keeps white text with a half-white underline.

### Spectrum
A five-step ruled strip from "Reliable appliance" to "Premium, with a maintenance tax". Steps are 26px tall with 1.5px black seams. The car's step fills black with white text. End labels sit below in small muted text.

### Tables
Full width, collapsed borders, 14px text. Header labels are condensed uppercase over a 1.5px black rule. Rows divide with hairlines. Money columns right-align with tabular figures. Total rows go 800 weight on a teal tint, boxed by 2px black rules above and below. Below 860px, tables marked to stack become labeled rows.

### Status Tags
Small inline labels: 12px, 700, 85% width, padded 1px 7px 2px, square, with a 1px border in the text color.
- **Good:** green ink on green tint. "Under budget".
- **Warn:** amber ink on amber tint.
- **Bad:** red ink on red tint. "Over budget".
- **Info:** teal ink on teal tint. "At your offer".
- **Near budget:** the warn tag reads "Just under budget" or "Just over budget" when an estimated out-the-door price is within 3% of the budget.

### Estimate Mark
A small "est." after an out-the-door price while taxes and fees are a state estimate: 11px, 700, 85% width, amber ink, no box. It's lighter than a tag because it repeats on every price. The ranking totals say "About" in their sentences and "est." in their headers instead.

### Load Error and No-Script Sheet
If the page fails to draw, the main area shows one bordered sheet: "This report couldn't load," what to do, and the error in small muted text. A viewer that blocks scripts gets the same sheet holding the summary, the recommendation and the asking prices.

### Marks Lists
Unbulleted lists with a small 8px square mark and hairline dividers. The mark color says the list's kind: black for neutral and sources, teal for strengths, an amber diamond for watch-outs, red for walk-away reasons.

### Inputs / Fields
- **Style:** a condensed uppercase label over a full-width input. 1.5px black border, square, white fill, 600-weight tabular figures, padded 7px 9px. Number spinners are hidden.
- **Hover:** the border turns teal.
- **Focus:** a 2px teal outline, offset 1px.
- **Error:** the border turns red ink and the fill turns red tint. The hint below turns red ink and bold, and it states the fix in a full sentence.
- **Hint:** 12px muted text under the field.

### Buttons
- **Shape:** square (0px), 1.5px black border.
- **Default:** white with ink text, 13.5px bold, padded 7px 12px.
- **Hover:** inverts to ink with white text.
- **Focus:** the global 2px teal outline, offset 2px.
- **Disabled:** 45% opacity, no hover change.
- **Ghost:** no border or fill, underlined text, no side padding. Hover turns the text teal ink. Used for "Reset" and "Clear offer".

### Offer Box
A ruled three-cell readout under the offer field: out the door, 5-year cost, and the gap to the walk-away price. 1.5px black outline with 1px black seams. Each cell has a condensed label over an 800-weight figure. Below 860px the cells stack, and each puts its label left and its figure right.

### Script Box
The draft dealer message. Cool ground fill, 1.5px black outline, padded 12px 14px, capped at 70ch. A bordered "Copy message" button sits below with a green status line that confirms the copy.

### Navigation
- **Rail (above 860px):** group labels in condensed uppercase `muted`. Links in 500-weight `ink-2`, padded 7px 20px. Hover fills with ground. The current page fills with teal tint, turns teal ink and bold, and draws a 1px inset teal ring.
- **Tabs (860px and below):** a white sticky bar with a 2px black bottom rule. Tabs are 14px, 600 weight. The current tab goes 800 weight in ink with a 3px teal underline that sits on the bar's rule.

### Shell and Sample Banner
The shell is a 54px black bar. The brand mark is a small white sticker outline with a filled top strip and three ruled lines, next to "Auto Advisor" in condensed uppercase. A sample report adds an amber banner below the shell with a 1.5px amber-ink bottom rule.

## Do's and Don'ts

### Do:
- **Do** frame every content block as a white sheet with a 2px `ink` border, and open each section with a black section bar.
- **Do** set labels in condensed (75%) uppercase at 11.5px with 0.07em tracking, sitting directly on their value.
- **Do** use tabular, lining figures for every number and right-align money.
- **Do** show any total that ranks cars on the save/spend scale, from the cheapest to the priciest car in the set.
- **Do** pair every status color as ink on tint with a 1px border.
- **Do** keep every corner square.
- **Do** keep teal for data, selection, focus and the scale.
- **Do** turn wide tables into labeled stacked rows below 860px.
- **Do** honor reduced motion on every transition.

### Don't:
- **Don't** use soft rounded comparison cards with a single blue accent. The direction contract rejects this as the category default.
- **Don't** add drop shadows or floating cards. Hierarchy comes from frames, bars and tints.
- **Don't** add a second accent hue next to teal.
- **Don't** use amber, red or green for anything but status.
- **Don't** set reading text condensed, or labels at normal width.
- **Don't** put an uppercase kicker above a headline. Uppercase condensed text only labels a value or fills a section bar.
- **Don't** load a font or any asset at view time. The face is embedded.
