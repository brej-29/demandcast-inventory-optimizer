# DemandCast

**A browser-local replenishment workbench for retailers who work from daily sales CSVs.** Import one item, enter stock and supplier assumptions, inspect historical evidence, and export an explainable order. Sales files stay on your device. No account or API key.

[Open the workbench](https://brej-29.github.io/demandcast-inventory-optimizer/) · [Why this exists and 15 hard questions](docs/WHY.md) · [Architecture](docs/ARCHITECTURE.md) · [Evaluation contract](docs/EVALUATION_PLAN.md)

## The problem

A forecast is not a purchase quantity. An operator needs stock for supplier lead time **and** the interval before the next review, less inventory already available, with an allowance for errors. The prior implementation measured uncertainty from the spread of future point forecasts: flat predictions implied zero safety stock despite volatile observations. [`reproduce_legacy_failure.py`](scripts/reproduce_legacy_failure.py) demonstrates it.

[Inventory Planner's documentation](https://help.inventory-planner.com/en/articles/589017-replenishment) confirms the distinction between forecasts and replenishment. [Shopify's Stocky transition](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/inventory-management/stocky), effective August 31, 2026, makes portable planning workflows timely. This establishes an operational problem, not adoption or willingness to pay; the audience remains an unvalidated product hypothesis.

## What the experiment found

The protocol and thresholds were written before implementation. Eight items selected using the first 120 days of [UCI Online Retail](https://doi.org/10.24432/C5BW33) produce **184 held-out weekly decisions**. Every decision sees only earlier observations.

| Method | Sales-cycle coverage | Mean target stock | Shortfall units |
| --- | ---: | ---: | ---: |
| Last week repeated, no buffer | 51.6% | 555.2 | 39,547 |
| 28-day mean, no buffer | 58.2% | 533.3 | 35,210 |
| 28-day mean, legacy forecast-spread buffer | 58.2% | 533.3 | 35,210 |
| 28-day mean, historical period-error buffer | **96.2%** | **1,624.5** | **9,018** |

**The overall hypothesis failed.** Coverage improved by **38.0 percentage points**, but mean target stock was **3.05×** the point forecast, exceeding the declared **2×** guardrail. The >=90% coverage and >=15-point improvement thresholds passed. The evidence lab prominently displays the failure and per-item differences.

Point WAPE stayed **59.0%** with or without the buffer. The weekday-mean ablation had identical weekly totals, so its redundant runtime selector was removed. The descriptive Wilson coverage interval is **92.4%–98.1%**; dependent items and periods prevent interpreting it as a future guarantee. [Results JSON](web/data/evaluation.json), [every prediction](web/data/cycles.csv), [provenance](web/data/provenance.json), and [limits](docs/WHY.md) are committed.

This tests observed gross-sales coverage, not warehouse operations, actual stockouts, costs or profit. The source is one retailer in 2010–2011 with no availability or delivery history. Cancellation lines are excluded without reconciling their original purchases; bulk orders and recording errors can inflate the buffer. Difficult items stayed in the cohort and thresholds were not relaxed.

## The product

- Import complete daily `date,sales` CSVs; explore labeled synthetic examples or one historical public item.
- Adjust on-hand stock, incoming stock, backorders, supplier lead time, review interval, pack size and requested coverage.
- Inspect target = forecast + historical error buffer; position = on hand + incoming − backorders; order = nonnegative difference rounded up to packs.
- Examine actual historical check cycles, assumptions and the forecast chart; export a decision CSV matching the screen.
- Invalid dates, gaps, duplicates, negative/nonfinite sales, invalid settings and inadequate history block recommendations. A Worker keeps calculations responsive, ignores stale jobs and times out long jobs.
- Read the mechanism, negative benchmark and limitations inside the product. No automatic purchasing or hidden model services.

The UI uses a spruce rail, mineral work surface, petrol demand chart and citrus accents. A neighboring order sheet exposes the arithmetic; phones place it before the chart. Self-hosted Manrope, SVG icons, keyboard access, named scrollable tables, states and reduced motion are recorded in [DESIGN.md](DESIGN.md).

## Run locally

Requires **Node 24**. Python is only needed for retained research or reconstructing the benchmark aggregate.

```sh
npm ci
npm run dev
```

Open **http://127.0.0.1:4187/**. `npm run build` creates static `dist/` files. No environment file or runtime secrets are needed.

CSV format:

```csv
date,sales
2025-01-01,24
2025-01-02,18
```

This excerpt shows the format; a usable file needs **120–3650 consecutive daily rows**, with longer history for longer protection periods. One item, YYYY-MM-DD dates, nonnegative sales <=1,000,000, file under 2 MB. Resolve gaps explicitly: never substitute zero for a stockout. The planner downloads a complete synthetic example.

## Reproduce and verify

```sh
npm test
npm run evaluate
npx playwright install chromium
npm run test:e2e
npm run build
```

`npm run audit` audits a running local preview. Set `SMOKE_URL` to a deployment URL with a trailing slash and run `npm run test:e2e -- --grep 'core job'` for the live core flow.

Local evidence: **14 core tests, 7 browser tests, zero Axe WCAG AA violations** across the three views. Screenshots cover **390px phone, 820px tablet and 1440px desktop**. Independent review found and resolved mobile arithmetic wrapping, scaled chart labels, hidden horizontal table comparisons and route-focus outlines. Latest mobile Lighthouse: **100 performance / 100 accessibility / 100 best practices / 100 SEO**. Earlier local performance varied **76–100**; these are lab observations, not field guarantees. [Audit JSON](docs/verification/lighthouse.json) · [Verification record](docs/verification/REVIEW.md) · [Baseline audit](docs/BASELINE.md).

CI reproduces evaluation artifacts byte-for-byte, runs core/E2E/accessibility checks and mobile Lighthouse >=90, builds static assets, deploys only `main`, then runs a live main-flow smoke test. The retained Python suite uses a frozen Python 3.11 environment.

Reconstruct licensed data:

```sh
python -m venv .venv
# Activate .venv using your platform's command.
python -m pip install -r requirements-research.lock.txt
python scripts/prepare_benchmark.py
npm run evaluate
```

Raw data is cached in git-ignored `data/raw/`. Only anonymous daily aggregates are published; provenance records the source hash and filters. The older `src/demandcast`, notebooks, scripts and Streamlit pages are retained **research**, not the live product. The original 11 Python tests pass with 53 deprecation warnings; see [starting-state findings](docs/BASELINE.md).

## Free deployment and limits

**https://brej-29.github.io/demandcast-inventory-optimizer/** — GitHub Pages serves this public, noncommercial open-source workbench from `main`. No new signup, credit card, model API, database or sleeping service. Publication and smoke-test evidence are recorded in [the release record](docs/verification/REVIEW.md).

[Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits): 1 GB published site, soft 100 GB/month bandwidth, 10-minute deployment timeout, possible rate limiting and no SLA. Custom Actions publishing is exempt from the soft 10-build/hour limit. Pages is not commercial SaaS hosting; the tool has no accounts, payments or transactions.

Loaded data and calculations work after disconnecting. Offline reload and new benchmark fetches require connectivity. Imported sales are memory-only and disappear on reload. Scope: one item, fixed lead time, protection period <=42 days, >=20 calibration windows. Check exact arrivals, stock availability, promotions, cash and expiry before buying.

## Next experiment

The efficient-buffer claim is unsupported. Obtain consented availability, reconciled transactions, promotions and actual delivery history; freeze a multi-retailer holdout and compare methods at equal stock budgets. A simpler spreadsheet workflow should win if it produces the same decisions with less work.

Code: [MIT](LICENSE). Aggregate data: [Daqing Chen, UCI Online Retail, CC BY 4.0](https://doi.org/10.24432/C5BW33). Typeface: [Manrope, SIL Open Font License](web/fonts/OFL.txt).
