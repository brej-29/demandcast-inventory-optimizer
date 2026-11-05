# Verification record

## Measured checks

- Original Python suite: 11 passed, 53 deprecation warnings, Python 3.11; see `docs/BASELINE.md`.
- Core: 14 tests pass. Main-flow, state, accessibility and responsive suite: 7 pass.
- Axe: zero WCAG 2 A/AA and 2.1 AA violations across planner, evidence and method. This is an automated scan, not assistive-technology certification.
- Latest local mobile Lighthouse: 100/100/100/100. Earlier performance scores included 100, 76 and 100; the other three categories remained 100. The 76 run recorded 1,248.9 ms total blocking time; the next full run recorded 0 ms. Variation is reported rather than hidden.
- Screenshots: 390×844, 820×1180, 1440×1080; all three views, reduced motion. No horizontal document overflow. Table overflow is intentional and has keyboard access and labels.
- Independent reviewer scored four material fixes resolved on recapture: phone arithmetic, responsive chart labels, horizontal-scroll cues and page-sized focus outline. Disposition **ship** at that scope.
- Error, empty, offline and recovery are exercised by E2E; local artifacts include state captures. Loading shows a skeleton, a 1.5-second slow-job message and a 15-second Worker timeout. Static deployment has no server cold start.

## Three reference products

Current primary public surfaces reviewed: [Prediko](https://www.prediko.io/), [Inventory Planner](https://www.inventory-planner.com/), and [Shopify's inventory/Stocky help](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky). These references set a task-clarity standard, not an accuracy comparison or endorsement. Public-page captures are retained locally when reachable.

| Reference | Useful standard | Product response | Limit |
| --- | --- | --- | --- |
| Prediko | Demand connected to buying and supply | Demand chart beside pack-rounded order | No store sync, transfers or PO management |
| Inventory Planner | Replenishment distinguished from forecast | Separate target, position and order; explicit incoming units | No delivery schedule or integrated stock ledger |
| Shopify inventory help | Task-first explanations and concrete notices | Native inputs, actionable errors, source labels | CSV boundary rather than commerce integration |

The first mobile render failed readable operational data despite passing automated checks. The fixes make arithmetic vertical, match chart coordinates to the actual container and expose table scrolling. No 3D or motion package was added because it would not clarify the decision.

## Detector triage

Tiny text was a real issue: sub-12px text was raised to at least 12px and scaled SVG labels received responsive coordinates. No tiny-text suppression. The sole dash-frequency advisory was a false positive caused by unavailable-number placeholders. A narrow exception applies to `web/index.html`; no global rule or file was disabled.

## Release controls

The local commit hook rejects prohibited provenance text. The release scanner checks new commit messages, diff and the exact PR-body file before each push and PR. Official tool documentation did not expose a verifiable commit/PR attribution setting, and native settings are unavailable; no unsupported key was invented. Actual release content is inspected directly.

The bounded credential-pattern scan reports filenames and key types, never possible secret values. It cannot prove absence of every credential format. The public app needs no secrets.

## Deployment

GitHub Pages is enabled with workflow publishing, public access and enforced HTTPS. Default-branch publication and live smoke results will be recorded here after the workflow completes.

The initial remote verification run passed every check, including E2E and mobile quality. Browser installation alone took 8 minutes 52 seconds; the run completed successfully just before a cancellation attempt could take effect. Subsequent runs use the runner's preinstalled stable Chrome via Playwright's supported browser channel. Browser and audit jobs have explicit timeouts; all product checks remain required. [Initial green run](https://github.com/brej-29/demandcast-inventory-optimizer/actions/runs/42059530502).
