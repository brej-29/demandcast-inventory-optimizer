# Why DemandCast exists

## A specific job

An independent retailer has daily sales in a spreadsheet, stock on hand, and a supplier who takes seven days to deliver. They need to decide how many units to buy today, including the time until the next stock review. A point forecast does not answer that question: an order must account for inventory position and forecast errors over the complete protection period.

This is a product hypothesis, not an interview-backed demand claim. No customers, revenue, savings, or adoption are claimed. The concrete technical problem is reproduced by [`reproduce_legacy_failure.py`](../scripts/reproduce_legacy_failure.py): the prior implementation used dispersion of future point predictions as uncertainty and therefore assigns no buffer to a flat prediction even if observed sales vary.

[Inventory Planner's replenishment documentation](https://help.inventory-planner.com/en/articles/589017-replenishment) explicitly distinguishes forecast units from purchase quantities and accounts for stock on order. Its [troubleshooting checklist](https://help.inventory-planner.com/en/articles/1959457-troubleshooting-the-forecast-and-replenishment) names lead times, days of stock and stockout-affected sales. This establishes the operational problem and available alternatives; it does not establish willingness to adopt this tool.

## Why now

Shopify's [official Stocky notice](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky) says the app is unavailable after August 31, 2026. A documented planning tool transition makes portable explanations and export-based workflows timely; it is not proof that affected merchants need DemandCast. Modern browser Workers can run this bounded computation locally, allowing an open tool with no per-request model bill or sales-data upload.

The stronger reason is the reproducible baseline failure, not fashion. The core decision should remain usable if a model catalog or free inference tier disappears; this product uses neither.

## Named alternatives, same criteria

| Approach | Setup and privacy | Decision explanation | Evaluation evidence | Broader operations |
| --- | --- | --- | --- | --- |
| DemandCast | CSV, no account; calculations on device | Full target/position/pack arithmetic and every historical cycle | Fixed public cohort, outputs and failed guardrail published | Single item; no store sync or POs |
| Excel reorder sheet | Local workbook possible; user builds formulas | Flexible and inspectable if authored carefully | User must build and maintain time-ordered replay | Manual exports; highly flexible |
| Google Sheets reorder sheet | Cloud spreadsheet; manual data entry/export | Flexible formulas | User must build replay | Collaboration; cloud data storage |
| Inventory Planner | Account and connected commerce systems | [Documented replenishment breakdown](https://help.inventory-planner.com/en/articles/589017-replenishment) | Not benchmarked here; no accuracy comparison claimed | [Forecasting, replenishment and POs](https://www.inventory-planner.com/) |
| Prediko | Shopify/cloud account workflow | [Buying and supply-planning experience](https://www.prediko.io/) | Not benchmarked here; no accuracy comparison claimed | Integrations, transfers, purchase orders and multiple locations |
| Shopify inventory / former Stocky | Existing Shopify ecosystem | Integrated stock workflows | Not benchmarked here | Stronger store integration; [Stocky transition](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky) is documented |

DemandCast does not claim to replace these products. Its narrow advantage is a zero-account local decision audit that a stranger can inspect, reproduce, and export. If a retailer needs automatic synchronization, multiple suppliers or budget allocation, an integrated product is a better starting point.

## Why this approach

The [architecture note](ARCHITECTURE.md) records the alternatives. Shipping a Python model server would preserve the old stack but introduce startup delays, dependency management, uploads, and a second deployment. Pure browser modules let the evaluator and live product import identical logic and avoid presenting unverified complex model accuracy as a benefit.

The forecast candidates are deliberately simple. In this 7-day evaluation a four-week weekday mean has the same period sum as the 28-day mean, so the selector brought no meaningful benefit: this is a negative ablation. A numerical tolerance first stabilized floating point ties; then the redundant selector was removed entirely. No cohort, threshold, horizon or quantile was changed, and the simplified runtime reproduces the same reported targets.

## What the numbers show

The [evaluation contract](EVALUATION_PLAN.md) was written before the engine and benchmark. [UCI Online Retail](https://doi.org/10.24432/C5BW33), Daqing Chen, CC BY 4.0, contains 541,909 transaction lines from one UK-based retailer between December 2010 and December 2011. We keep positive-priced positive-quantity UK item lines, exclude cancellation lines and nonnumeric codes, select eight items by first-120-day volume, aggregate by day and drop the partial final day. Customer identifiers are never emitted.

The fixture has 373 days. Eight items × 23 non-overlapping held-out 7-day cycles = **184 decisions**, starting at day 210. Source hash and filters are in [`provenance.json`](../web/data/provenance.json); [every prediction](../web/data/cycles.csv) is committed.

| Method | Sales-cycle coverage | Mean target units | Shortfall units | Point WAPE |
| --- | ---: | ---: | ---: | ---: |
| Last week repeated, no buffer | 51.6% | 555.2 | 39,547 | 71.0% |
| Selected 28-day mean, no buffer | 58.2% | 533.3 | 35,210 | 59.0% |
| Selected forecast, legacy spread buffer | 58.2% | 533.3 | 35,210 | 59.0% |
| Selected forecast, historical error buffer | 96.2% | 1,624.5 | 9,018 | 59.0% |

The buffer covers **177/184** observed sales cycles, an improvement of **38.0 percentage points**, but needs **3.05×** the point forecast in mean target stock. The predeclared >=90% coverage and >=15-point improvement pass; the <=2× stock guardrail fails. **The overall hypothesis is not met.** No threshold was relaxed and no difficult item was removed.

The descriptive Wilson interval is 92.4%–98.1%; cycles and items are dependent, so it is not a valid generalization guarantee. Per-item buffered coverage ranges from 91.3% to 100%; target/point ratios range from 1.91× to 5.96×. This spread is more important than a pooled headline.

Reproduce with `npm ci && npm run evaluate`. The evaluator is deterministic and CI compares its output byte-for-byte with the committed artifacts. Repeating a deterministic run is a reproducibility check, not independent statistical evidence.

## What the numbers cannot show

This is observed gross sales coverage, not latent demand, achieved fill rate, cycle service in a warehouse, or money saved. Missing dates were zero-filled for the public benchmark and may be closures or stockouts. Excluding cancellation lines does not reconcile their original purchases; bulk sales or transaction errors can contaminate the positive-sales series and the top-volume cohort.

No inventory levels, procurement costs, replenishment orders, lead-time variance, expiry dates or promotion calendar are available. Overlapping calibration windows and a changing sales distribution invalidate a distribution-free coverage guarantee. The 95% label is a requested empirical error quantile; the interface separately reports what past held-out cycles achieved.

## Falsification and the next experiment

The current efficient-buffer hypothesis already failed its stock guardrail. The implementation remains useful as a transparent planning aid and a way to expose that tradeoff, not as proof of optimization. Do not automate purchases from this evidence.

Next, collect item availability, reconciled returns/cancellations, promotion labels, and actual supplier delivery dates with consent. Freeze a multi-retailer holdout and compare stock-aware models and simpler direct empirical demand quantiles at equal inventory budgets. If a spreadsheet with explicit fixed days of cover matches outcomes and requires less work, build that simpler workflow instead.

## Fifteen hard questions

### 1. Is this a real customer problem or a portfolio invention?

The operational distinction between forecasts and purchase quantities is documented in Inventory Planner's primary help material, and the old repo contains a reproducible uncertainty error. The target user's adoption need is still a hypothesis; there are no interviews or usage claims. The product makes a concrete CSV-to-decision job possible without claiming market validation.

### 2. Why not use a spreadsheet?

A well-built spreadsheet can implement the same formulas and may be the better choice for a skilled operator. DemandCast ships strict date validation, historical replay, a visible negative benchmark and an export in one zero-account flow. The comparison is workflow packaging and reproducibility, not proprietary mathematics.

### 3. Did you actually beat the old approach?

On the frozen 184-cycle cohort, sales coverage rose from 58.2% to 96.2%. Mean target stock rose from 533.3 to 1,624.5 units, failing the declared efficiency guardrail. Calling this an unqualified win would contradict `web/data/evaluation.json`.

### 4. Is 95% coverage guaranteed?

No: it is the requested rank of historical protection-period errors. Calibration windows overlap and retail sales are not exchangeable, so a finite-sample rank adjustment alone gives no guarantee. The planner shows separate out-of-sample historical checks and warns when evidence is sparse.

### 5. Is there future leakage?

The cohort uses only the first 120 days; evaluation begins at day 210. Every held-out decision receives only its prefix history, and only fully observed windows enter calibration. A core regression test checks that changing later sales does not change earlier historical cycles.

### 6. Why eight products from one old retailer?

They provide a bounded, licensed and reproducible stress test with genuine transactions. They do not represent a modern retailer catalog, and top-volume selection can overrepresent bulk purchases. Generalization requires a new multi-retailer holdout, as specified above.

### 7. Are recorded sales actual demand?

Only when availability and recording are adequate. The source has no availability labels, and filtering cancellation lines does not repair original transactions. The UI names zero-sales and sudden-change risks; the benchmark must be interpreted as gross-sales coverage only.

### 8. Did the model-selection complexity earn its place?

No: the predeclared ablation exposed that the candidate weekly totals coincide. The runtime selector was removed and replaced with a fixed trailing mean; the frozen outputs are unchanged. The weekday comparison remains in the evidence lab so this simplification can be audited.

### 9. Why does the buffer become so expensive?

Large historical period errors require a large empirical quantile to cover them. Seven of eight items exceed the 2× guardrail individually, and the aggregate ratio is 3.05×. That is a reason to investigate transactions and availability, not to remove outliers after inspecting the holdout.

### 10. Does the order formula prevent stockouts before delivery?

No: total inventory position can conceal late incoming orders. The UI separately warns when on-hand stock minus backorders is below the point forecast during supplier lead time and asks the operator to verify exact arrivals. Variable lead times and scheduled deliveries need another model and dataset.

### 11. Why no complex forecasting model or language model?

The benchmark's point WAPE is 59.0%, and the principal failure is uncertainty cost, not absence of a fashionable model. A complex server model would add runtime and operational burdens without measured evidence here. The retained Python package remains available for a properly frozen future comparison.

### 12. Is this really private?

Sales CSVs are parsed into memory and sent only to a same-origin local Worker; there is no upload endpoint, database, analytics, or persistence. Static hosting still receives normal asset requests and network metadata. Closing or reloading the page discards imported sales, so the decision must be exported to keep it.

### 13. What happens when a free tier runs out?

There is no inference or database quota to exhaust. Static hosting can rate limit or become unavailable; an already loaded planner still calculates with loaded data, and the repository runs with `npm run dev`. Offline reload, availability SLA, and commercial SaaS hosting are not promised.

### 14. What proves the UI and arithmetic work together?

The headless main-flow test imports a CSV, changes stock and pack size, inspects historical cycles, and verifies that the exported order matches the visible result. Additional tests cover invalid imports/settings, offline behavior, worker failure, benchmark retry, keyboard access, WCAG AA and three responsive widths. Local Lighthouse scored 100 in all four categories; those are lab results, not a field performance guarantee.

### 15. What would you refuse to ship next?

Automatic purchases would be unjustified while the cost guardrail fails and availability and arrival schedules are unknown. A revenue or savings claim would require a prospectively specified inventory experiment and actual costs. The next investment should be data quality and a simpler equal-budget comparison, not a stronger adjective in the interface.
