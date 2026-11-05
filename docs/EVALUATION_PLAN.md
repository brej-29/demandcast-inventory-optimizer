# Evaluation contract — written before implementation

This contract was written locally before the engine. It was not separately timestamped in a public registration or committed before implementation; the chronology is a local work record, not an independently registered experiment.

## Claim to test

Using historical protection-period forecast errors should cover more observed sales cycles than a point forecast or the legacy rule that estimates uncertainty from the spread of future point forecasts. This is a sales-coverage experiment, not a simulation of achieved fill rate or inventory savings.

## Predeclared protocol

- Public data: UCI Online Retail, Daqing Chen, DOI 10.24432/C5BW33, CC BY 4.0. Keep UK positive-quantity, positive-price, non-cancelled item lines; aggregate by day. Exclude non-item codes. Never retain customer identifiers.
- Pick the eight highest-volume numeric item codes using only the first 120 calendar days. Fill missing dates with zero sales and disclose that closure/stockout labels are unavailable. Drop incomplete final day.
- Evaluate non-overlapping 7-day cycles beginning at day 210, expanding history, same origins for every method. Freeze cohort/protocol before looking at results.
- Point methods: last week repeated, trailing 28-day mean, and mean by weekday over four weeks. Choose between mean and weekday only on earlier validation origins; report both fixed baselines too.
- Buffer alternatives: no buffer; legacy standard deviation of future daily predictions times sqrt(horizon) times 1.645; historical positive 7-day sum residual quantile at requested 95% coverage. Quantile order is ceil((n+1)*p), bounded to available residuals, with an explicit finite-sample warning.
- Calibration uses only fully observed earlier origins; cap history at 180 days. Report overlapping calibration dependence; do not claim exchangeability or theoretical guarantees.

## Metrics and thresholds

Primary: fraction of held-out cycle demand sums below the target stock, at requested 95% coverage. Shipping hypothesis succeeds only with >=90% pooled coverage and >=15 percentage points improvement over no buffer. Cost guardrail: average target stock <=2 times the point forecast; report failures rather than tune after seeing them.

Report per-item results, pooled shortage units, mean target stock, WAPE of point forecasts, Wilson interval for cycle coverage (descriptive, dependent cycles), and every cycle prediction. A negative result remains in the UI and README. Synthetic stress cases include flat, intermittent, trend, weekly seasonality, and shock series; they verify behavior, not business performance.

## Product and quality gates

Invalid dates, duplicate dates, missing days, negative/nonfinite sales, excessive files, inadequate history, nonfinite settings, and insufficient calibration must prevent a purchase recommendation. Export must reproduce visible quantities. Main-flow E2E must import CSV, change assumptions, inspect evidence and export. Lighthouse goal: >=90 in all four categories on local mobile audit; publish actual scores and any unverified deployment gate.

## Post-evaluation simplification

The two candidate models have identical 7-day sums by construction. After reporting this negative ablation, the redundant selector was removed from the runtime: the planner uses the trailing 28-day mean. A numerical tie tolerance was tested first; removing the selector produces the same targets and coverage. Cohort, origin dates, calibration windows, quantile, thresholds and all acceptance criteria remain unchanged. Fixed weekday and weekly-naive baselines remain in the report.
