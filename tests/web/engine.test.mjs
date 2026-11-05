import test from "node:test";
import assert from "node:assert/strict";
import {
  parseCSV,
  forecast,
  targetAt,
  analyze,
  decisionCSV,
  quantile,
} from "../../web/engine.js";
const series = Array.from({ length: 365 }, (_, i) => ({
  date: new Date(Date.UTC(2025, 0, i + 1)).toISOString().slice(0, 10),
  sales: 20 + (i % 7 === 0 ? 25 : 0) + (i % 13 === 0 ? 40 : 0),
}));
const csv = (rows) =>
  "date,sales\n" + rows.map((x) => `${x.date},${x.sales}`).join("\n");
const s = {
  onHand: 100,
  incoming: 12,
  backorders: 4,
  lead: 7,
  review: 7,
  pack: 12,
  coverage: 0.95,
};
test("CSV sorts dates and preserves explicit zero sales", () => {
  const d = series.map((x) => ({ ...x }));
  d[2].sales = 0;
  assert.deepEqual(parseCSV("\uFEFF" + csv(d.reverse())), d.reverse());
});
test("CSV rejects gaps, duplicate dates, invalid dates, negatives, empty sales, malformed quotes and oversized files", () => {
  for (const text of [
    csv(series.filter((_, i) => i !== 40)),
    csv([...series, series[0]]),
    csv(series).replace("2025-01-01", "2025-02-30"),
    csv(series).replace(",85", ",-1"),
    csv(series).replace(",85", ","),
    'date,sales\n"unclosed',
    "x".repeat(2_000_001),
  ])
    assert.throws(() => parseCSV(text));
});
test("quoted CRLF CSV with extra metadata columns", () => {
  const text =
    "date,sales,note\r\n" +
    series.map((x) => `"${x.date}",${x.sales},"a,b"`).join("\r\n");
  assert.equal(parseCSV(text).length, 365);
});
test("flat point forecast still receives a buffer when observed errors are volatile", () => {
  const r = targetAt(
    series.map((x) => x.sales),
    14,
    0.95,
  );
  assert.ok(r.buffer > 0);
  assert.ok(r.target > r.point);
});
test("constant sales has zero uncertainty and exact forecast", () => {
  const r = targetAt(Array(365).fill(20), 14, 0.95);
  assert.equal(r.target, 280);
  assert.equal(r.buffer, 0);
});
test("stock accounting and pack rounding reconcile; more incoming cannot increase order", () => {
  const r = analyze(series, s);
  assert.equal(r.position, 108);
  assert.equal(r.order % 12, 0);
  assert.ok(r.position + r.order >= r.target);
  assert.ok(analyze(series, { ...s, incoming: 100 }).order <= r.order);
  assert.equal(analyze(series, { ...s, onHand: 100000 }).order, 0);
});
test("settings fail closed for invalid and nonfinite values", () => {
  for (const change of [
    { lead: 0 },
    { lead: 42, review: 7 },
    { pack: 0 },
    { pack: 1.5 },
    { onHand: -1 },
    { coverage: 0.99 },
    { incoming: NaN },
    { review: Infinity },
    { backorders: 1.2 },
  ])
    assert.throws(() => analyze(series, { ...s, ...change }));
});
test("long protection period with inadequate calibration refuses recommendation", () =>
  assert.throws(
    () => analyze(series.slice(0, 120), { ...s, lead: 35, review: 7 }),
    /more history/,
  ));
test("higher requested coverage cannot decrease the target", () => {
  const y = series.map((x) => x.sales);
  assert.ok(targetAt(y, 14, 0.95).target >= targetAt(y, 14, 0.8).target);
});
test("historical checks are independent of future sales", () => {
  const a = analyze(series, s);
  const changed = series.map((d, i) => ({
    ...d,
    sales: i > 350 ? 99999 : d.sales,
  }));
  const b = analyze(changed, s);
  assert.deepEqual(
    a.cycles.filter((c) => c.date < "2025-12-01"),
    b.cycles.filter((c) => c.date < "2025-12-01"),
  );
});
test("corrected quantile rank is conservative and finite sample is flagged", () => {
  assert.equal(quantile([1, 2, 3, 4], 0.8).value, 4);
  assert.equal(quantile([1, 2, 3, 4], 0.95).limited, true);
});
test("all-zero demand returns finite zero order and an intermittent warning", () => {
  const r = analyze(
    series.map((d) => ({ ...d, sales: 0 })),
    { ...s, onHand: 0, incoming: 0, backorders: 0 },
  );
  assert.equal(r.order, 0);
  assert.ok(r.warnings.some((x) => x.includes("zero-sales")));
});
test("decision export includes actual inputs, results and limits", () => {
  const r = analyze(series, s),
    text = decisionCSV(series, s, r);
  assert.ok(text.includes(`"order_units","${r.order}"`));
  assert.ok(text.includes('"lead","7"'));
  assert.ok(text.includes("not a guarantee"));
});
test("weekly naive repeats last seven observed values", () =>
  assert.deepEqual(
    forecast([1, 2, 3, 4, 5, 6, 7], 9, "naive"),
    [1, 2, 3, 4, 5, 6, 7, 1, 2],
  ));
