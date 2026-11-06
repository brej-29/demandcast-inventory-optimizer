# DemandCast — Ink & Copper

The public workbench is an operating surface for retail purchasing, designed for sustained reading in a normally lit workspace. Warm paper keeps charts and forms readable; charcoal navigation and decision sheets establish a clear hierarchy. Copper identifies actions, while apricot highlights the proposed purchase.

## Implementation

The shared presentation layer is in web/style.css. Existing markup, copy, routes, computation, imports, exports, and data remain unchanged. Manrope is locally hosted; no external fonts or animation libraries are required.

## Tokens and composition

Paper #f3f1eb; ink #252b30; muted #606460; navigation #20282d; decision sheet #29363b; copper #854329; apricot #efbc8c. Semantic warning and error colors and blue chart observations retain their existing roles. Panels use 12px corners; controls use 5–6px corners. Shadows are restrained and offset.

Headings use light-to-medium Manrope with tight tracking; purchasing quantities use large tabular figures. Desktop pairs the chart with a contrasting decision ledger. Tablet retains the compact workbench; phone places the decision before the chart and preserves readable tables through horizontal scrolling. Methodology and evidence use the same type, materials, and controls.

## Interaction and accessibility

Route entrances use a short opacity and translation transition. Buttons have tactile pressed states; fields and table rows provide local feedback. No continuous decorative animation is introduced. Reduced motion disables transitions and animation. Keyboard focus, labels, source qualifications, calculation arithmetic, and error states remain visible. Keep future changes presentation-only unless explicitly authorized.
