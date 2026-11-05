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

GitHub Pages published from `main` commit `28d5534e4aa0e02c597c2703587de52303af3d21`. [Production workflow](https://github.com/brej-29/demandcast-inventory-optimizer/actions/runs/42061913181) completed successfully on 2026-11-05 at 16:12:54 UTC, including verification, deployment and the public core-flow smoke test. HTTPS GET returned 200. PR #2 is merged. The repository homepage and description contain the live URL and free-hosting limits.

The initial remote verification run passed every check, including E2E and mobile quality. Browser installation alone took 8 minutes 52 seconds; the run completed successfully just before a cancellation attempt could take effect. Subsequent runs use the runner's preinstalled stable Chrome via Playwright's supported browser channel. Browser and audit jobs have explicit timeouts; all product checks remain required. [Initial green run](https://github.com/brej-29/demandcast-inventory-optimizer/actions/runs/42059530502).

## Public verification

The full seven-test browser suite passed against https://brej-29.github.io/demandcast-inventory-optimizer/ in 28.3 seconds. This includes real public CSV import/edit/export, failures and recovery, offline loaded-data calculations, Axe scans and all three screenshot widths. Public mobile Lighthouse: **92 performance / 100 accessibility / 100 best practices / 91 SEO**; all four exceed the declared 90 floor. The committed `lighthouse.json` is the public run; local and remote CI audits previously scored 100 in all four categories.

The public SEO deduction is `robots-txt`: the shared Pages origin serves an invalid account-level robots response. That origin belongs outside this repository, so it was inspected but not modified. Host-controlled cache lifetimes and network behavior also differ from local preview. No field-performance or uptime guarantee is implied.

Following the initial successful deployment, publishing/test action references were refreshed to their official current releases and the runner pinned to Ubuntu 24.04 to remove deprecated runtime and image-migration dependencies. The application files are unchanged in this release-record follow-up.
