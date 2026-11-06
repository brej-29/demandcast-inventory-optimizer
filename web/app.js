import { createDesk } from "./desk.js";
import { parseCSV, decisionCSV, mean, CONFIG } from "./engine.js";

const $ = (id) => document.getElementById(id);
const fmt = (n, d = 0) =>
  Number(n).toLocaleString("en-GB", { maximumFractionDigits: d });
const pct = (n) => `${fmt(n * 100, 1)}%`;
const esc = (text) =>
  String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
const iconPaths = {
  sliders: '<path d="M4 7h16M4 17h16M8 4v6m8 4v6"/>',
  chart: '<path d="M4 4v16h16M8 15l4-5 4 2 4-7"/>',
  book: '<path d="M12 6v15m0-15C9 3 5 3 3 4v15c3-1 6-1 9 2 3-3 6-3 9-2V4c-2-1-6-1-9 2Z"/>',
  shield:
    '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z"/><path d="m8 12 3 3 5-6"/>',
  upload: '<path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5"/>',
  download: '<path d="M12 3v13m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  box: '<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 10v9M3 8l9 5 9-5M8 5l9 5v4"/>',
  receipt:
    '<path d="M5 3h14v18l-3-2-4 2-4-2-3 2V3Z"/><path d="M8 7h8M8 11h8M8 15h4"/>',
};
document.querySelectorAll("[data-icon]").forEach((el) => {
  el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths[el.dataset.icon]}</svg>`;
});

let series = [],
  result = null,
  job = 0,
  timer,
  timeout,
  slowTimer,
  worker,
  currentSource = "steady";
const desk = createDesk({ getSeries: () => series, getResult: () => result, getSettings: settings,
  restore: values => { for (const [id, value] of Object.entries(values)) $(id).value = value; recalculate(); }, download: exportFile });
function createWorker() {
  try {
    worker = new Worker(new URL("./worker.js", import.meta.url), {
      type: "module",
    });
    worker.onmessage = ({ data }) => {
      if (data.id !== job) return;
      clearTimeout(timeout);
      clearTimeout(slowTimer);
      $("loading").hidden = true;
      $("slow").hidden = true;
      $("workspace").setAttribute("aria-busy", "false");
      if (data.error) {
        fail(data.error);
        return;
      }
      result = data.result; desk.update();
      renderResult();
      $("export").disabled = false;
      $("app-status").textContent =
        `Calculation complete. ${fmt(result.order)} units to order. ${result.cycles.length} historical cycles checked.`;
    };
    worker.onerror = () =>
      fail(
        "The local calculation worker could not start. Reload the page in a current browser.",
      );
  } catch {
    fail(
      "This browser cannot run local calculations. Use a current browser and reload.",
    );
  }
}
createWorker();
function settings() {
  return Object.fromEntries(
    [
      "onHand",
      "incoming",
      "backorders",
      "lead",
      "review",
      "pack",
      "coverage",
    ].map((id) => [id, $(id).value === "" ? NaN : Number($(id).value)]),
  );
}
function invalidate() {
  result = null; desk.update();
  $("export").disabled = true;
  $("order-qty").textContent = "—";
  $("order-state").textContent = "Calculation unavailable";
  for (const id of [
    "expected",
    "buffer",
    "target",
    "position",
    "rounded",
    "observed-coverage",
  ])
    $(id).textContent = "—";
  $("cycles-body").replaceChildren();
  $("cycle-chart").replaceChildren();
  $("coverage-count").textContent = "No current result";
  $("pack-note").textContent = "Order calculation needs valid sales and settings.";
  $("warnings").replaceChildren();
}
function fail(message) {
  clearTimeout(timeout);
  clearTimeout(slowTimer);
  $("loading").hidden = true;
  $("slow").hidden = true;
  $("workspace").setAttribute("aria-busy", "false");
  invalidate();
  $("chart").textContent = "Add valid sales and assumptions to calculate a forecast.";
  for (const id of ["daily-mean", "method-name", "protection"]) $(id).textContent = "—";
  $("error").textContent = message;
  $("error").hidden = false;
}
function recalculate() {
  clearTimeout(timer);
  clearTimeout(timeout);
  clearTimeout(slowTimer);
  job++;
  invalidate();
  $("error").hidden = true;
  if (!series.length) return;
  $("loading").hidden = false;
  $("workspace").setAttribute("aria-busy", "true");
  const id = job;
  timer = setTimeout(() => {
    if (!worker) {
      fail("Local calculation is unavailable. Reload to try again.");
      return;
    }
    worker.postMessage({ id, series, settings: settings() });
    slowTimer = setTimeout(() => {
      $("slow").hidden = false;
    }, 1500);
    timeout = setTimeout(() => {
      job++;
      worker.terminate();
      createWorker();
      fail("The calculation took too long. Try a shorter history and reload.");
    }, 15000);
  }, 100);
}

function synthetic(kind = "steady") {
  let seed = 2701;
  const rand = () => {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    return seed / 4294967296;
  };
  return Array.from({ length: 365 }, (_, i) => {
    const date = new Date(Date.UTC(2025, 0, i + 1)).toISOString().slice(0, 10);
    const noise = (rand() + rand() + rand() - 1.5) * 16;
    let sales = Math.round(
      25 + [0, 1, -3, 2, 5, 12, -7][i % 7] + noise + Math.sin(i / 19) * 3,
    );
    if (kind === "intermittent")
      sales = rand() < 0.65 ? 0 : Math.round(rand() * 65);
    if (kind === "shock" && i > 325) sales *= 2.2;
    return { date, sales: Math.max(0, Math.round(sales)) };
  });
}
function loadSeries(data, name, label) {
  series = data; desk.reset();
  $("series-name").textContent = name;
  $("source-label").textContent = label;
  $("date-range").textContent =
    `${data[0].date} – ${data.at(-1).date} · ${data.length} days`;
  $("empty").hidden = true;
  $("workspace").hidden = false;
  $("source-label").classList.toggle("sample-tag", label.includes("Synthetic"));
  recalculate();
}
function exportFile(content, filename, type = "text/csv") {
  const a = document.createElement("a"),
    url = URL.createObjectURL(new Blob([content], { type }));
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function exampleCSV() {
  return (
    "date,sales\n" +
    synthetic()
      .map((d) => `${d.date},${d.sales}`)
      .join("\n")
  );
}
async function loadExample() {
  const value = $("example").value;
  currentSource = value;
  if (value === "retail") {
    invalidate();
    $("loading").hidden = false;
    try {
      const response = await fetch("./data/retail.csv");
      if (!response.ok)
        throw new Error(
          "The public dataset could not be loaded. Import a CSV or choose a synthetic example.",
        );
      const text = await response.text();
      if (currentSource !== value) return;
      const rows = text
          .trim()
          .split(/\r?\n/)
          .map((r) => r.split(",")),
        headers = rows.shift(),
        index = headers.indexOf("22197"),
        code = headers[index];
      const data = rows.map((r) => ({ date: r[0], sales: Number(r[index]) }));
      loadSeries(
        data,
        `Retail item ${code} · Small popcorn holder`,
        "UCI retail · historical 2010–2011",
      );
    } catch (e) {
      if (currentSource === value) fail(e.message);
    }
  } else
    loadSeries(
      synthetic(value),
      {
        steady: "Everyday stoneware",
        intermittent: "Intermittent sales",
        shock: "Sudden demand shift",
      }[value],
      "Synthetic example · not store data",
    );
}
$("example").addEventListener("change", loadExample);
$("settings").addEventListener("input", recalculate);
// The input event covers numeric fields and selects. Avoid recalculating again on blur.
$("settings").addEventListener("submit", (e) => e.preventDefault());
for (const id of ["upload", "empty-upload"])
  $(id).onclick = () => $("file").click();
$("file").onchange = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  currentSource = "import";
  job++;
  invalidate();
  $("error").hidden = true;
  try {
    if (file.size > CONFIG.maxBytes)
      throw new Error("Use a CSV file smaller than 2 MB.");
    const parsed = parseCSV(await file.text());
    loadSeries(parsed, file.name, "Your CSV · processed on this device");
    $("app-status").textContent =
      `Imported ${parsed.length} days of sales from ${file.name}.`;
  } catch (error) {
    series = []; desk.reset();
    $("workspace").hidden = true;
    $("empty").hidden = false;
    $("series-name").textContent = "No valid dataset";
    $("date-range").textContent = "";
    $("source-label").textContent = "Import needs attention";
    fail(error.message);
  }
  e.target.value = "";
};
$("clear").onclick = () => {
  currentSource = "empty";
  job++;
  clearTimeout(timer);
  clearTimeout(timeout);
  clearTimeout(slowTimer);
  series = []; desk.reset();
  invalidate();
  $("workspace").hidden = true;
  $("empty").hidden = false;
  $("series-name").textContent = "No dataset loaded";
  $("source-label").textContent = "Ready for your sales";
  $("date-range").textContent = "";
  $("error").hidden = true;
  $("app-status").textContent = "Sales data cleared from memory.";
};
$("sample").onclick = () => {
  $("example").value = "steady";
  loadExample();
};
for (const id of ["template", "template-bottom"])
  $(id).onclick = () =>
    exportFile(exampleCSV(), "demandcast-synthetic-example.csv");
$("export").onclick = () => {
  if (result) {
    exportFile(
      decisionCSV(series, settings(), result),
      "demandcast-decision.csv",
    );
    $("app-status").textContent =
      "Decision exported with assumptions and historical checks.";
  }
};
$("buffer-info").onclick = () => {
  location.hash = "method";
};

function renderChart() {
  const history = series.slice(-56),
    y = history.map((x) => x.sales),
    future = result.daily;
  const w = Math.max(280, Math.min(650, $("chart").clientWidth)),
    h = 230,
    left = 38,
    right = 12,
    top = 24,
    bottom = 30,
    n = y.length + future.length;
  const max =
    Math.max(
      10,
      ...y,
      ...future.map((x) => x + result.buffer / future.length),
    ) * 1.17;
  const px = (i) => left + (i / (n - 1)) * (w - left - right),
    py = (v) => h - bottom - (v / max) * (h - bottom - top);
  const line = (values) =>
    values
      .map(
        ([i, v], k) =>
          `${k ? "L" : "M"}${px(i).toFixed(1)},${py(v).toFixed(1)}`,
      )
      .join(" ");
  const histPath = line(y.map((v, i) => [i, v])),
    fp = line([
      [y.length - 1, y.at(-1)],
      ...future.map((v, i) => [y.length + i, v]),
    ]);
  const area =
    line(
      future.map((v, i) => [y.length + i, v + result.buffer / future.length]),
    ) +
    " " +
    future
      .map((v, i) => [y.length + i, v])
      .reverse()
      .map(([i, v]) => `L${px(i)},${py(v)}`)
      .join(" ") +
    " Z";
  const boundary = px(y.length - 0.5),
    grid = [0, 0.25, 0.5, 0.75, 1]
      .map(
        (v) =>
          `<line x1="${left}" x2="${w - right}" y1="${py(max * v)}" y2="${py(max * v)}" stroke="#e7eeea"/><text x="${left - 9}" y="${py(max * v) + 4}" text-anchor="end" class="tick">${fmt(max * v)}</text>`,
      )
      .join("");
  const dateLabel = (value) =>
    new Date(value + "T00:00:00Z").toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      timeZone: "UTC",
    });
  const labels = [0, 20, 40]
    .map(
      (i) =>
        `<text x="${px(i)}" y="${h - 7}" text-anchor="middle" class="tick">${dateLabel(history[i].date)}</text>`,
    )
    .join("");
  const endDate = new Date(
    Date.parse(series.at(-1).date) + future.length * 86400000,
  )
    .toISOString()
    .slice(0, 10);
  $("chart").innerHTML =
    `<svg viewBox="0 0 ${w} ${h}" role="img" aria-labelledby="chart-title chart-desc"><title id="chart-title">Observed sales and ${future.length}-day forecast</title><desc id="chart-desc">Last 56 days of observed sales, average ${fmt(mean(y), 1)} units per day. Forecast total ${fmt(result.point, 1)} units plus ${fmt(result.buffer, 1)} period buffer. Target ${fmt(result.target)} units. Future sales are unknown.</desc>${grid}<rect x="${boundary}" y="${top}" width="${w - right - boundary}" height="${h - top - bottom}" fill="#f3f7f2"/><g class="forecast-area"><path d="${area}" fill="#d9e9ed"/><path d="${fp}" fill="none" stroke="#275e51" stroke-width="2" stroke-dasharray="5 4"/></g><path d="${histPath}" fill="none" stroke="#34678c" stroke-width="2" stroke-linejoin="round"/><line x1="${boundary}" x2="${boundary}" y1="${top}" y2="${h - bottom}" stroke="#93ac9f" stroke-dasharray="3 4"/><text x="${boundary + 8}" y="14" style="font-size:12px">Forecast →</text>${labels}<text x="${px(n - 1)}" y="${h - 7}" text-anchor="end" class="tick">${dateLabel(endDate)}</text></svg>`;
}

function renderResult() {
  const s = settings();
  $("order-qty").textContent = fmt(result.order);
  $("rounded").textContent = fmt(result.order);
  $("expected").textContent = fmt(result.point, 1);
  $("buffer").textContent = `+ ${fmt(result.buffer, 1)}`;
  $("target").textContent = fmt(result.target);
  $("position").textContent = `− ${fmt(result.position)}`;
  $("order-state").textContent = result.order
    ? "Suggested purchase · review first"
    : "Target already covered";
  $("pack-note").textContent =
    `${fmt(result.order / s.pack)} packs × ${fmt(s.pack)} units · target rounded up to whole units`;
  $("daily-mean").textContent =
    `${fmt(mean(series.slice(-28).map((x) => x.sales)), 1)} units`;
  $("method-name").textContent =
    result.method === "weekday" ? "4-week weekday mean" : "28-day rolling mean";
  $("protection").textContent =
    `${result.horizon} days · ${s.lead} + ${s.review}`;
  $("chart-subtitle").textContent =
    `56 observed days + ${result.horizon} forecast days · ${result.residuals.length} historical error windows`;
  $("observed-coverage").textContent =
    result.coverage === null ? "N/A" : pct(result.coverage);
  $("coverage-count").textContent =
    `${result.cycles.filter((x) => x.covered).length} of ${result.cycles.length} cycles covered`;
  $("history-subtitle").textContent =
    `Requested ${pct(s.coverage)} · ${result.horizon}-day cycles · past data only at each decision`;
  $("cycle-chart").innerHTML = result.cycles
    .map(
      (c) =>
        `<div class="cycle-block ${c.covered ? "" : "miss"}" title="${c.date}: ${c.covered ? "covered" : "missed"}, ${fmt(c.actual)} actual, ${fmt(c.target)} target" aria-hidden="true"></div>`,
    )
    .join("");
  $("cycles-body").innerHTML = result.cycles
    .map(
      (c) =>
        `<tr><td>${c.date}</td><td>${fmt(c.actual)}</td><td>${fmt(c.point, 1)}</td><td>${fmt(c.target)}</td><td>${c.covered ? "Covered" : "Missed"}</td></tr>`,
    )
    .join("");
  const warnings = [...result.warnings];
  if (result.preArrivalRisk)
    warnings.unshift(
      `Stock may run out before delivery: on-hand stock minus backorders is below ${fmt(result.arrivalPoint, 1)} forecast units during lead time. Incoming stock has no arrival schedule here. Consider expediting.`,
    );
  const staleDays = Math.floor(
    (Date.now() - Date.parse(series.at(-1).date)) / 86400000,
  );
  if (currentSource === "import" && staleDays > 7)
    warnings.push(
      `Your history ends ${staleDays} days ago. Add recent sales and recheck current stock before using this order.`,
    );
  $("warnings").innerHTML = warnings
    .map((w) => `<p class="warning">${esc(w)}</p>`)
    .join("");
  renderChart();
}

let benchmarkLoaded = false;
async function benchmark() {
  if (benchmarkLoaded) return;
  $("benchmark").innerHTML =
    '<div class="loading" role="status"><div class="skeleton"></div>Loading the reproducible benchmark…</div>';
  try {
    const response = await fetch("./data/evaluation.json");
    if (!response.ok) throw new Error("Benchmark unavailable");
    const e = await response.json();
    benchmarkLoaded = true;
    const r = e.summary.calibrated,
      base = e.summary.point;
    $("benchmark").innerHTML =
      `<div class="benchmark-intro"><div><h2>${e.passed ? "The buffer clears the predeclared test." : "The buffer helps. The full test still fails."}</h2><p>${esc(e.conclusion)} Eight items from one UK retailer, ${e.cyclesPerItem} held-out 7-day periods each. No stock availability, supplier history, or inventory costs are present in the data.</p></div><span class="verdict">${e.passed ? "Thresholds passed" : "Hypothesis not met"}</span></div><div class="result-strip"><div><strong>${pct(r.coverage)}</strong><span>observed cycle coverage · 95% requested</span></div><div><strong>+${fmt((r.coverage - base.coverage) * 100, 1)} pp</strong><span>coverage versus no buffer</span></div><div><strong>${fmt(r.stockRatio, 2)}×</strong><span>average target / point forecast</span></div></div><section class="benchmark-section"><h2 id="comparison-title">Same data. Same decisions. Different buffers.</h2><p>All methods see only earlier data. The public test starts at day 210. The runtime uses a trailing 28-day mean; calibration replays fully observed sales windows. Target stock is compared to observed period sales, not to a simulated warehouse.</p><p class="table-hint">Scroll to compare all columns →</p><div class="table-wrap" tabindex="0" role="region" aria-labelledby="comparison-title"><table><caption class="sr-only">Held-out benchmark methods</caption><thead><tr><th scope="col">Method</th><th scope="col">Cycle coverage</th><th scope="col">Mean target</th><th scope="col">Shortfall units</th><th scope="col">WAPE</th></tr></thead><tbody>${Object.entries(
        e.summary,
      )
        .map(
          ([key, v]) =>
            `<tr ${key === "calibrated" ? 'class="metric-highlight"' : ""}><td>${esc(v.label)}</td><td>${pct(v.coverage)}</td><td>${fmt(v.meanTarget, 1)}</td><td>${fmt(v.shortfall)}</td><td>${pct(v.wape)}</td></tr>`,
        )
        .join(
          "",
        )}</tbody></table></div><p>Coverage interval for the buffered method: ${pct(r.interval[0])}–${pct(r.interval[1])} (Wilson, descriptive; periods and items are dependent). WAPE evaluates the underlying point forecast, not the buffer. The selected point forecast and its buffer have the same WAPE.</p></section><section class="benchmark-section"><h2 id="items-title">What the aggregate hides</h2><p class="table-hint">Scroll to compare all columns →</p><div class="table-wrap" tabindex="0" role="region" aria-labelledby="items-title"><table><caption class="sr-only">Per-item buffered performance</caption><thead><tr><th scope="col">Retail item</th><th scope="col">No buffer</th><th scope="col">With buffer</th><th scope="col">Target / point</th></tr></thead><tbody>${e.items.map((v) => `<tr><td>${esc(v.code)} · ${esc(v.name)}</td><td>${pct(v.pointCoverage)}</td><td>${pct(v.coverage)}</td><td>${fmt(v.stockRatio, 2)}×</td></tr>`).join("")}</tbody></table></div><p>The cohort was selected using first-120-day unit volume, before the evaluation period. One early bulk purchase can dominate this selection. It is a fixed, limited test cohort, not representative of a store catalog.</p></section><section class="benchmark-section"><h2>The test was written before the result</h2><ul class="limit-list"><li>Coverage at least 90%: <strong>${r.coverage >= 0.9 ? "passed" : "failed"}</strong> (${pct(r.coverage)}).</li><li>Coverage improvement at least 15 percentage points: <strong>${r.coverage - base.coverage >= 0.15 ? "passed" : "failed"}</strong>.</li><li>Mean target stock at most 2× point forecast: <strong>${r.stockRatio <= 2 ? "passed" : "failed"}</strong> (${fmt(r.stockRatio, 2)}×).</li><li>Missing transaction days are zero-filled in this public benchmark. They may include closures and stockouts. The planner requires users to resolve gaps explicitly.</li><li>These are 2010–2011 observed sales from one retailer. Results do not establish current retailer performance, future service, profit, or actual inventory savings.</li></ul><p>Source: <a href="https://doi.org/10.24432/C5BW33">UCI Online Retail — Daqing Chen, CC BY 4.0</a>. Source archive SHA-256, filters, and cohort are in <a href="./data/provenance.json">data provenance</a>. <a href="https://github.com/brej-29/demandcast-inventory-optimizer/blob/main/docs/EVALUATION_PLAN.md">Read the frozen evaluation contract</a>.</p><p><a href="./data/cycles.csv" download>Download every held-out prediction</a> · <button class="text-button" id="use-retail">Open public retail item in planner</button></p></section>`;
    $("use-retail").onclick = () => {
      $("example").value = "retail";
      loadExample();
      location.hash = "planner";
    };
  } catch {
    $("benchmark").innerHTML =
      '<div class="alert error">The benchmark could not be loaded. Reconnect and <button class="text-button" id="retry-benchmark">try again</button>.</div>';
    $("retry-benchmark").onclick = benchmark;
  }
}
function route(focus = true) {
  const name = ["planner", "evidence", "method"].includes(
    location.hash.slice(1),
  )
    ? location.hash.slice(1)
    : "planner";
  for (const id of ["planner", "evidence", "method"])
    $(id).hidden = id !== name;
  document.querySelectorAll("[data-route]").forEach((a) => {
    if (a.dataset.route === name) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
  });
  $("crumb").textContent = {
    planner: "Order planner",
    evidence: "Evidence lab",
    method: "How it works",
  }[name];
  document.title = `DemandCast — ${$("crumb").textContent}`;
  if (name === "evidence") benchmark();
  if (focus) {
    $("main").focus({ preventScroll: true });
    window.scrollTo({ top: 0 });
  }
}
window.addEventListener("hashchange", () => route());
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (result && !$("planner").hidden) renderChart();
  }, 100);
});
function connection() {
  $("offline").hidden = navigator.onLine;
  $("connection").textContent = navigator.onLine
    ? "Local computation"
    : "Offline · local mode";
}
window.addEventListener("online", connection);
window.addEventListener("offline", connection);
connection();
route(false);
loadExample();
