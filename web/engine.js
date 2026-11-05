export const CONFIG = Object.freeze({
  maxBytes: 2_000_000,
  maxDays: 3650,
  minDays: 120,
  calibrationDays: 180,
  minCalibration: 20,
  maxPeriod: 42,
});
export const sum = (a) => a.reduce((s, x) => s + x, 0);
export const mean = (a) => (a.length ? sum(a) / a.length : 0);
export const sd = (a) =>
  a.length > 1
    ? Math.sqrt(sum(a.map((x) => (x - mean(a)) ** 2)) / (a.length - 1))
    : 0;

export function parseCSV(text) {
  if (new TextEncoder().encode(text).length > CONFIG.maxBytes)
    throw new Error("CSV is too large. Use a file smaller than 2 MB.");
  const rows = [];
  let row = [],
    cell = "",
    quoted = false,
    closed = false;
  text = text.replace(/^\uFEFF/, "");
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        cell += '"';
        i++;
      } else if (c === '"') {
        quoted = false;
        closed = true;
      } else cell += c;
    } else if (c === '"' && !cell && !closed) quoted = true;
    else if (c === "," || c === "\n" || c === "\r") {
      row.push(cell.trim());
      cell = "";
      closed = false;
      if (c !== ",") {
        if (row.some(Boolean)) rows.push(row);
        row = [];
        if (c === "\r" && text[i + 1] === "\n") i++;
      }
    } else {
      if ((closed && c.trim()) || c === '"')
        throw new Error(
          "CSV contains an invalid quote. Export it again as standard CSV.",
        );
      cell += c;
    }
  }
  if (quoted) throw new Error("CSV has an unclosed quoted field.");
  row.push(cell.trim());
  if (row.some(Boolean)) rows.push(row);
  if (!rows.length)
    throw new Error("This file is empty. Add date and sales columns.");
  const header = rows.shift().map((x) => x.toLowerCase());
  const di = header.indexOf("date"),
    yi = header.indexOf("sales");
  if (di < 0 || yi < 0 || new Set(header).size !== header.length)
    throw new Error("Use unique column names including date and sales.");
  const data = rows
    .map((r, i) => {
      if (r.length !== header.length)
        throw new Error(
          `Row ${i + 2} has ${r.length} fields; expected ${header.length}.`,
        );
      const date = r[di],
        sales = Number(r[yi]);
      if (
        !/^\d{4}-\d{2}-\d{2}$/.test(date) ||
        !Number.isFinite(Date.parse(date)) ||
        new Date(date).toISOString().slice(0, 10) !== date
      )
        throw new Error(`Row ${i + 2}: use a real date in YYYY-MM-DD format.`);
      if (!r[yi] || !Number.isFinite(sales) || sales < 0 || sales > 1_000_000)
        throw new Error(
          `Row ${i + 2}: sales must be a number from 0 to 1,000,000. Record returns separately.`,
        );
      return { date, sales };
    })
    .sort((a, b) => a.date.localeCompare(b.date));
  if (data.length < CONFIG.minDays || data.length > CONFIG.maxDays)
    throw new Error(
      `Use ${CONFIG.minDays}–${CONFIG.maxDays} days of history. This file has ${data.length}.`,
    );
  for (let i = 1; i < data.length; i++) {
    const gap =
      (Date.parse(data[i].date) - Date.parse(data[i - 1].date)) / 86400000;
    if (gap === 0)
      throw new Error(
        `Duplicate date ${data[i].date}. Aggregate to one item and one row per day.`,
      );
    if (gap !== 1)
      throw new Error(
        `Missing days before ${data[i].date}. Add explicit zero sales only if the item was available but did not sell.`,
      );
  }
  return data;
}

export function forecast(y, horizon, method = "mean") {
  const last = y.slice(-28);
  if (!last.length || last.some((x) => !Number.isFinite(x) || x < 0))
    throw new Error("Forecast needs finite, nonnegative sales.");
  return Array.from({ length: horizon }, (_, i) => {
    if (method === "naive") return y[y.length - 7 + (i % 7)] ?? mean(last);
    if (method === "weekday")
      return mean(
        [7, 14, 21, 28]
          .map((k) => y[y.length - k + (i % 7)])
          .filter(Number.isFinite),
      );
    return mean(last);
  });
}

export function quantile(values, p) {
  if (!values.length) throw new Error("No historical errors are available.");
  const sorted = [...values].sort((a, b) => a - b);
  const rank = Math.ceil((sorted.length + 1) * p);
  return {
    value: sorted[Math.min(rank, sorted.length) - 1],
    rank,
    limited: rank > sorted.length,
  };
}

export function targetAt(y, horizon = 7, coverage = 0.95) {
  const start = Math.max(84, y.length - CONFIG.calibrationDays - horizon + 1);
  const method = "mean";
  const residuals = [];
  for (let t = start; t + horizon <= y.length; t++)
    residuals.push(
      sum(y.slice(t, t + horizon)) -
        sum(forecast(y.slice(0, t), horizon, method)),
    );
  if (residuals.length < CONFIG.minCalibration)
    throw new Error(
      `Need more history for ${horizon} days of protection. At least ${84 + horizon + CONFIG.minCalibration - 1} daily rows are required.`,
    );
  const daily = forecast(y, horizon, method),
    point = sum(daily),
    q = quantile(residuals, coverage);
  const buffer = Math.max(0, q.value);
  return {
    method,
    daily,
    point,
    buffer,
    target: Math.ceil(point + buffer),
    residuals,
    limited: q.limited,
  };
}

export function validateSettings(s) {
  for (const key of [
    "onHand",
    "incoming",
    "backorders",
    "lead",
    "review",
    "pack",
    "coverage",
  ]) {
    if (typeof s[key] !== "number" || !Number.isFinite(s[key]))
      throw new Error(`Enter a valid number for ${key}.`);
  }
  if (
    [s.onHand, s.incoming, s.backorders].some(
      (x) => x < 0 || x > 1_000_000 || !Number.isInteger(x),
    )
  )
    throw new Error(
      "Stock quantities must be whole units from 0 to 1,000,000.",
    );
  if (
    ![s.lead, s.review, s.pack].every(Number.isInteger) ||
    s.lead < 1 ||
    s.review < 0 ||
    s.lead + s.review > CONFIG.maxPeriod ||
    s.pack < 1 ||
    s.pack > 10000
  )
    throw new Error(
      "Use whole days: lead time at least 1, review at least 0, total at most 42; pack size 1–10,000.",
    );
  if (![0.8, 0.9, 0.95].includes(s.coverage))
    throw new Error("Choose 80%, 90%, or 95% coverage.");
}

export function analyze(data, settings) {
  validateSettings(settings);
  const y = data.map((x) => x.sales),
    horizon = settings.lead + settings.review;
  const result = targetAt(y, horizon, settings.coverage);
  const position = settings.onHand + settings.incoming - settings.backorders;
  const order = Math.max(
    0,
    Math.ceil((result.target - position) / settings.pack) * settings.pack,
  );
  const cycles = [];
  for (
    let t = Math.max(84 + horizon + 19, y.length - horizon * 12);
    t + horizon <= y.length;
    t += horizon
  ) {
    const past = targetAt(y.slice(0, t), horizon, settings.coverage),
      actual = sum(y.slice(t, t + horizon));
    cycles.push({
      date: data[t].date,
      actual,
      point: past.point,
      target: past.target,
      covered: actual <= past.target,
    });
  }
  const warnings = [];
  if (y.filter((x) => x === 0).length / y.length > 0.3)
    warnings.push(
      "More than 30% zero-sales days: check closures, stockouts, and intermittent demand before ordering.",
    );
  if (
    mean(y.slice(-28)) > mean(y.slice(-84, -28)) * 1.5 &&
    mean(y.slice(-84, -28)) > 0
  )
    warnings.push(
      "Recent sales increased sharply. Historical error buffers may lag a change in demand.",
    );
  if (result.buffer > result.point)
    warnings.push(
      "The buffer exceeds the point forecast. Investigate bulk orders and demand changes before committing cash.",
    );
  if (result.limited)
    warnings.push(
      "There are too few historical errors for this quantile rank. The maximum observed error is used.",
    );
  if (cycles.length < 8)
    warnings.push(
      "Fewer than eight non-overlapping historical check cycles are available. Treat the coverage estimate as weak evidence.",
    );
  const arrivalPoint = sum(result.daily.slice(0, settings.lead));
  return {
    ...result,
    order,
    position,
    horizon,
    cycles,
    warnings,
    preArrivalRisk: settings.onHand - settings.backorders < arrivalPoint,
    arrivalPoint,
    coverage: cycles.length ? mean(cycles.map((x) => Number(x.covered))) : null,
    zeroShare: y.filter((x) => x === 0).length / y.length,
  };
}

export function decisionCSV(data, settings, r) {
  const rows = [
    ["field", "value"],
    ["history_start", data[0].date],
    ["history_end", data.at(-1).date],
    ...Object.entries(settings),
    ["method", r.method],
    ["protection_days", r.horizon],
    ["forecast_units", r.point],
    ["buffer_units", r.buffer],
    ["target_units", r.target],
    ["inventory_position", r.position],
    ["order_units", r.order],
    ["historical_coverage", r.coverage ?? "unavailable"],
    ["check_cycles", r.cycles.length],
    [
      "warning",
      "Observed sales coverage is not a guarantee of future service. Check delivery dates, stockouts, and assumptions.",
    ],
    ...r.warnings.map((w) => ["warning", w]),
  ];
  return rows
    .map((row) =>
      row.map((x) => `"${String(x).replaceAll('"', '""')}"`).join(","),
    )
    .join("\r\n");
}
