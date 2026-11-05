import { readFile, writeFile } from "node:fs/promises";
import { forecast, targetAt, sum, mean, sd } from "../web/engine.js";
const root = new URL("../web/data/", import.meta.url);
const lines = (await readFile(new URL("retail.csv", root), "utf8"))
  .trim()
  .split(/\r?\n/)
  .map((l) => l.split(","));
const codes = lines.shift().slice(1),
  provenance = JSON.parse(
    await readFile(new URL("provenance.json", root), "utf8"),
  );
const results = [],
  items = [];
const labels = {
  naive: "Last week repeated · no buffer",
  mean: "28-day mean · no buffer",
  weekday: "4-week weekday mean · no buffer",
  point: "28-day mean · no buffer",
  legacy: "28-day mean · legacy spread buffer",
  calibrated: "28-day mean · historical error buffer",
};
function wilson(wins, n) {
  const z = 1.96,
    p = wins / n,
    a = 1 + (z * z) / n,
    b = p + (z * z) / (2 * n),
    c = z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n));
  return [(b - c) / a, (b + c) / a];
}
function summarize(rows) {
  const wins = rows.filter((x) => x.actual <= x.target).length,
    actual = sum(rows.map((x) => x.actual)),
    point = sum(rows.map((x) => x.point));
  return {
    n: rows.length,
    coverage: wins / rows.length,
    interval: wilson(wins, rows.length),
    meanTarget: mean(rows.map((x) => x.target)),
    shortfall: sum(rows.map((x) => Math.max(0, x.actual - x.target))),
    wape: actual
      ? sum(rows.map((x) => Math.abs(x.actual - x.point))) / actual
      : 0,
    stockRatio: point ? sum(rows.map((x) => x.target)) / point : null,
  };
}
for (let c = 0; c < codes.length; c++) {
  const y = lines.map((l) => Number(l[c + 1]));
  for (let t = 210; t + 7 <= y.length; t += 7) {
    const history = y.slice(0, t),
      actual = sum(y.slice(t, t + 7)),
      calibrated = targetAt(history, 7, 0.95);
    for (const method of Object.keys(labels)) {
      let daily, point, target;
      if (["mean", "weekday", "naive"].includes(method)) {
        daily = forecast(history, 7, method);
        point = sum(daily);
        target = Math.ceil(point);
      } else {
        daily = calibrated.daily;
        point = calibrated.point;
        target =
          method === "calibrated"
            ? calibrated.target
            : Math.ceil(
                point +
                  (method === "legacy" ? 1.645 * sd(daily) * Math.sqrt(7) : 0),
              );
      }
      results.push({
        code: codes[c],
        date: lines[t][0],
        method,
        actual,
        point,
        target,
      });
    }
  }
  const chosen = results.filter(
      (x) => x.code === codes[c] && x.method === "calibrated",
    ),
    point = results.filter((x) => x.code === codes[c] && x.method === "point");
  const stats = summarize(chosen);
  items.push({
    code: codes[c],
    name: provenance.items.find((i) => i.code === codes[c]).name,
    coverage: stats.coverage,
    pointCoverage: summarize(point).coverage,
    stockRatio: stats.stockRatio,
  });
}
const summary = Object.fromEntries(
  Object.keys(labels).map((m) => [
    m,
    { label: labels[m], ...summarize(results.filter((x) => x.method === m)) },
  ]),
);
const r = summary.calibrated,
  b = summary.point,
  passed =
    r.coverage >= 0.9 && r.coverage - b.coverage >= 0.15 && r.stockRatio <= 2;
const conclusion = passed
  ? "Historical errors improved sales-cycle coverage within the declared stock guardrail. This is limited offline evidence, not demonstrated inventory savings."
  : "Historical errors improved sales-cycle coverage, but at least one predeclared threshold failed. The method needs stronger data or a different buffer before claiming efficient replenishment.";
const report = {
  protocol: "docs/EVALUATION_PLAN.md",
  requestedCoverage: 0.95,
  horizon: 7,
  cyclesPerItem: summary.calibrated.n / codes.length,
  passed,
  conclusion,
  summary,
  items,
};
await writeFile(
  new URL("evaluation.json", root),
  JSON.stringify(report, null, 2) + "\n",
);
await writeFile(
  new URL("cycles.csv", root),
  "code,date,method,actual,point,target\n" +
    results
      .map((r) =>
        [r.code, r.date, r.method, r.actual, r.point, r.target].join(","),
      )
      .join("\n") +
    "\n",
);
console.log(JSON.stringify({ passed, summary, items }, null, 2));
