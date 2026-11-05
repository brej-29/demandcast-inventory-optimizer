---
name: DemandCast
description: A mineral planning room for transparent replenishment decisions.
colors:
  ink: "#1c302e"
  muted: "#52635f"
  paper: "#f4f7f6"
  surface: "#fff"
  rail: "#173d37"
  rail-muted: "#bad0c8"
  brand: "#275e51"
  brand-hover: "#174737"
  brand-active: "#123c30"
  lime: "#d5ed91"
  line: "#dce5e1"
  blue: "#34678c"
  blue-light: "#e1edf5"
  amber: "#785009"
  amber-bg: "#fff7dd"
  danger: "#a43732"
  danger-bg: "#fff0ee"
  order-paper: "#e5eddf"
  source-paper: "#eaf0ed"
  nav-selected: "#31584b"
  nav-selected-text: "#f4ffd9"
  nav-hover: "#294e45"
  focus: "#487ba3"
typography:
  display-desktop:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "42px"
    fontWeight: 750
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  headline:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "17px"
    fontWeight: 750
    lineHeight: 1.4
    letterSpacing: "-0.02em"
  title:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.55
  body:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  body-prose:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.95
  label:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "12px"
    fontWeight: 700
    lineHeight: 1.55
  order-quantity:
    fontFamily: 'Manrope, "Segoe UI", sans-serif'
    fontSize: "55px"
    fontWeight: 650
    lineHeight: 1.15
    letterSpacing: "-0.035em"
rounded:
  cycle: "3px"
  badge: "6px"
  field: "7px"
  control: "8px"
  source: "10px"
  formula: "12px"
  panel: "14px"
spacing:
  compact: "8px"
  control: "12px"
  field-gap: "16px"
  phone-gutter: "18px"
  compact-panel: "20px"
  workspace-gap: "22px"
  panel: "24px"
  section: "28px"
  rail-top: "32px"
  desktop-gutter: "42px"
  wide-gutter: "56px"
components:
  button-primary:
    backgroundColor: "{colors.brand}"
    textColor: "{colors.surface}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 17px"
  button-primary-hover:
    backgroundColor: "{colors.brand-hover}"
  button-primary-active:
    backgroundColor: "{colors.brand-active}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.control}"
    padding: "12px 17px"
  button-text:
    textColor: "{colors.brand}"
    padding: "4px 0"
  field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "8px 11px"
    height: "42px"
  navigation-selected:
    backgroundColor: "{colors.nav-selected}"
    textColor: "{colors.nav-selected-text}"
    rounded: "{rounded.control}"
    padding: "12px 13px"
  panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.panel}"
    padding: "23px 24px"
  order-sheet:
    backgroundColor: "{colors.order-paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "22px"
  warning:
    backgroundColor: "{colors.amber-bg}"
    textColor: "{colors.amber}"
    rounded: "{rounded.control}"
    padding: "13px 16px"
  error:
    backgroundColor: "{colors.danger-bg}"
    textColor: "{colors.danger}"
    rounded: "{rounded.control}"
    padding: "13px 16px"
---

# Design System: DemandCast

## Overview

**Creative North Star: "The Mineral Planning Room"**

A calm purchasing desk built around readable evidence. Deep spruce anchors navigation; a cool mineral work surface holds white analysis panels and a pale green order sheet. Petrol-blue observed sales, a dashed green forecast, and restrained citrus details give each visual mark a job.

The interface is an operating tool: compact labels, generous separation between working sections, and aligned numerical rows. The order quantity has the strongest numerical emphasis, while its arithmetic and qualifications remain visible. Evidence and explanations use the same materials and type as the planner.

**Key Characteristics:**

- A dark spruce frame around a light mineral workspace.
- Flat tonal surfaces with gently rounded rectangular edges.
- Manrope typography and tabular figures for quantities.
- Distinct visual marks for observations, forecasts, buffers, and historical outcomes.
- Short functional motion with a reduced-motion alternative.

## Colors

The palette combines quiet green mineral neutrals with a blue analytical signal and a small citrus accent. Frontmatter is the normative token inventory; `web/style.css` is the implementation source. Sidecar tonal ramps are visual previews, not additional implemented palette tokens.

### Primary

- **Working Green** (`brand`): primary actions, links, forecast dashes, and small structural icons. Its darker hover and pressed variants show interaction.
- **Deep Spruce** (`rail`): the navigation frame. **Rail Mist** (`rail-muted`) supports secondary text within that frame. The selected route uses its own green surface and pale text.

### Secondary

- **Petrol Blue** (`blue`): observed sales, drawn as a solid line. **Buffer Blue** (`blue-light`) identifies the legend's buffer sample; the plotted allocation uses the implemented pale blue-green fill.
- **Citrus** (`lime`): brand mark, selected navigation icon, small rail details, and text selection. It is an attention marker rather than a large content surface.

### Neutral

- **Dark Ink** (`ink`) and **Mineral Gray** (`muted`): primary and supporting text.
- **Mineral Paper** (`paper`), **White Surface** (`surface`), **Source Paper** (`source-paper`), and **Order Paper** (`order-paper`): workspace, analysis, dataset context, and purchase arithmetic respectively.
- **Mineral Line** (`line`): section boundaries, table rows, and panel dividers.

### State colors

- **Amber Ink / Amber Paper** (`amber`, `amber-bg`): warnings and the benchmark verdict badge, including a hypothesis that did not meet its thresholds.
- **Clay Red / Clay Paper** (`danger`, `danger-bg`): blocking errors.
- **Focus Blue** (`focus`): keyboard focus outline, independent of the component's fill.

**The Evidence Marks Rule.** Pair color with a line style, label, or written outcome: solid observations, dashed forecasts, filled buffer allocation, and explicit Covered / Missed table results.

## Typography

**Display and body font:** locally hosted Manrope, with Segoe UI and sans-serif fallbacks. The variable font supports weights 200–800; the interface mostly uses 400, 600, 650, 700, and 750. There is no separate display or numerical font.

The type is direct and compact. Headlines tighten their tracking; normal labels remain sentence case. Tables, calculation rows, form quantities, and the order amount use tabular numerals. The scale is role based, with no fixed modular ratio.

- **Display:** the base page heading uses `clamp(28px, 3vw, 42px)`, weight 750, line height 1.2, and tracking −0.035em. The frontmatter's desktop role records its upper size. At 900px and below the heading is 32px; at 680px and below it is 29px.
- **Headline:** working section headings use the frontmatter headline role. The order heading is 15px; explanatory and benchmark headings reach 21–24px according to context and viewport.
- **Body:** the root is 14px with 1.55 line height. Most supporting interface copy is 12px; introductory copy and field values use 13px. Explanatory prose uses its own 13px role and a maximum width of 73ch.
- **Label:** 12px, with weight 700 for form labels and buttons; navigation uses 600. Do not turn ordinary labels into all-caps tracking.
- **Order quantity:** the frontmatter role is the standard desktop amount. It grows to 62px at 1500px and above, and becomes 48px at 1150px and below. Units and review status remain separate 12px text.
- **Chart:** SVG annotation is 11px Manrope, with 12px tick and forecast labels. Numeric phone inputs become 16px; select text remains 12px.

## Layout

The desktop frame has a fixed full-height rail (216px), an offset shell, and a white topbar (68px). The centered main region has a maximum width of 1600px and standard padding of 36px 42px 20px. The planner pairs a fluid chart with a 310px order sheet and a 22px gap. This is an asymmetric working pair, not a grid of equivalent metric cards.

Spacing is contextual rather than a strict multiple-based scale. Common gaps and padding are recorded in frontmatter; small 4–7px adjustments align labels, icons, and helper text. White analysis panels use roughly 23–24px internal space; the order sheet uses 22px. Section boundaries use fine rules and 24–30px breathing room.

- **1500px and above:** main padding becomes 42px 56px 25px, order column 340px, chart height 265px, and order padding 26px.
- **1150px and below:** rail becomes 190px; horizontal main padding becomes 26px. The order column is 278px, workspace gap 16px, and the third chart signal is hidden. Historical summary becomes two columns with its explanation below.
- **900px and below:** rail becomes a horizontal header; workspace identity and rail notes are hidden. The shell loses its left offset. Topbar becomes 50px; the order column is 280px and chart height 220px. Assumptions use four columns instead of six.
- **680px and below:** navigation forms three equal-purpose route tabs beneath the brand; decorative route icons are hidden while text remains. Main gutters become 18px and topbar 44px. The order sheet stacks before the chart; the final calculation layout is a single vertical ledger with right-aligned, nonwrapping values. The chart is 210px high. Assumptions use two columns and coverage spans both. The method formula sheet moves before prose; evidence metrics stack. Tables keep their columns inside a keyboard-focusable horizontal scroll region with a visible scroll hint.

## Elevation & Depth

There are no box shadows in the implemented interface. Depth comes from the dark navigation frame, the mineral workspace, and distinct flat white and pale green surfaces. Thin rules organize arithmetic and tables; panel boundaries do not rely on heavy outlines or floating effects.

**The Flat Surface Rule.** Use tonal surfaces and dividers to establish hierarchy; retain the shadow-free working desk.

## Shapes

Rectangular working sections have modest rounding: panels use the panel radius, source context the source radius, and controls the control radius. Fields are slightly tighter than buttons. The formula sheet has its own intermediate radius; status dots and the compact help button are circular. Historical cycle marks are short, nearly square-ended blocks with the cycle radius.

Borders are generally 1px. Main buttons have a minimum height of 44px, fields are 42px tall, and ordinary inline icons are 18px. Icons use thin strokes with round caps and joins; the brand mark is solid. Avoid converting working sections into pills.

## Components

### Buttons

Primary buttons use Working Green, white text, control rounding, and 12px 17px padding, with darker hover and pressed fills. Secondary actions use a white fill, a muted green-gray border, and a pale green hover fill. Text actions are green and underlined. Export fills the order sheet width.

Disabled buttons use opacity 0.45 and a not-allowed cursor. Keyboard focus uses a 3px Focus Blue outline with a 4px offset. Most button and navigation background transitions take 150ms. Do not add hover lift.

### Inputs / Fields

Labels sit above white bordered fields; unit hints sit beside labels and explanatory text below. A darker border indicates hover. Focus uses the shared outline. The current implementation reports invalid assumptions through the blocking error region; it has no separate red per-field error or success style.

### Navigation

The selected route has a green inset surface, pale text, and citrus icon. Hover shifts to a nearby dark green with white text. Route selection is carried by `aria-current="page"`. The same three destinations remain text labeled on phone. Main content receives programmatic focus on route changes; a visible-on-focus skip link precedes the frame.

### Cards / Containers

Analysis and history panels are white on Mineral Paper; the order and formula sheets are pale green. They have no hover or selected-card state. Dataset context uses a separate pale strip with a source icon, explicit source label, dates, dataset selector, and Clear action. Synthetic and public historical sources remain visibly distinguished.

### Badges and alerts

The local-computation badge is a compact green-tinted status with a dot and text, not an interactive chip. Benchmark verdicts are amber badges. Warnings and blocking errors use their semantic paper/ink pairs and readable messages. These states must retain their written meaning.

### Order sheet and calculation states

The largest quantity precedes a right-aligned ledger: expected sales, historical error buffer, target stock, inventory position, and pack-rounded order. Lines separate the subtotal and final amount. Pack details and the review instruction follow.

Recalculation invalidates the old quantity, displays em dashes, disables export, and marks the workspace busy. A loading message accompanies a pulsing skeleton; a slower-work message appears after 1.5 seconds. Successful computation restores the values and export. A zero order reads “Target already covered”; a positive order reads “Suggested purchase · review first.” Blocking failure keeps export disabled. Clearing data presents the import/example empty state. Offline status retains its text label.

### Forecast and historical evidence

Observed sales use a solid Petrol Blue path; the point forecast uses dashed Working Green. A vertical dashed boundary and pale future field mark the forecast region. The pale allocation fill is an illustrative spread of the period buffer, not a daily confidence interval; keep that nearby explanation. The SVG has an accessible title and description.

Historical cycles use green filled blocks for covered periods and warm outlined blocks for misses. The expandable table spells out each outcome with tabular figures. Evidence tables preserve comparisons and show a horizontal-scroll hint on phone. Historical coverage and requested coverage remain separately labeled.

View changes use a 220ms blur-to-clear animation; forecast allocation reveals over 700ms. Both use `cubic-bezier(0.16, 1, 0.3, 1)`. The skeleton alternates opacity over 1 second with ease-in-out. Reduced-motion preference disables all animations and transitions and restores automatic scrolling.

## Do's and Don'ts

### Do:

- **Do** preserve the spruce frame, mineral workspace, and pale green decision sheet as distinct functional surfaces.
- **Do** keep quantities tabular and calculation values right aligned, including on phone.
- **Do** pair chart colors and historical outcomes with line styles and explicit labels.
- **Do** keep source identity, dates, historical qualifications, and the period-buffer explanation readable beside the evidence.
- **Do** retain keyboard focus, scrollable comparison tables, and reduced-motion behavior.

### Don't:

- **Don't** replace the operating surface with decorative metric cards, large gradients, or floating shadows.
- **Don't** present the buffer allocation as a daily confidence interval or historical coverage as guaranteed future service.
- **Don't** hide the order arithmetic or collapse comparison columns to make a phone layout fit.
- **Don't** replace labeled phone navigation with icon-only destinations.
- **Don't** use citrus as a dominant panel fill or introduce an unrelated display font.
