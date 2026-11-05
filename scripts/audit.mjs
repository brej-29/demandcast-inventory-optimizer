import lighthouse from "lighthouse";
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { writeFile, mkdir } from "node:fs/promises";
const browser = spawn(
  chromium.executablePath(),
  [
    "--headless",
    "--no-sandbox",
    "--remote-debugging-port=9223",
    "--user-data-dir=" +
      new URL("../.cache/lighthouse", import.meta.url).pathname.replace(
        /^\/([A-Z]:)/,
        "$1",
      ),
  ],
  { stdio: "ignore" },
);
try {
  let up = false;
  for (let i = 0; i < 40; i++) {
    try {
      await fetch("http://127.0.0.1:9223/json/version");
      up = true;
      break;
    } catch {
      await new Promise((r) => setTimeout(r, 200));
    }
  }
  if (!up) throw new Error("Audit browser did not start");
  const url = process.env.SMOKE_URL || "http://127.0.0.1:4187/";
  const result = await lighthouse(url, {
    port: 9223,
    output: "json",
    onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
    logLevel: "error",
  });
  await mkdir("docs/verification", { recursive: true });
  const scores = Object.fromEntries(
    Object.entries(result.lhr.categories).map(([k, v]) => [
      k,
      Math.round(v.score * 100),
    ]),
  );
  await writeFile(
    "docs/verification/lighthouse.json",
    JSON.stringify(
      {
        url,
        formFactor: "mobile",
        scores,
        metrics: {
          fcp: result.lhr.audits["first-contentful-paint"].numericValue,
          lcp: result.lhr.audits["largest-contentful-paint"].numericValue,
          tbt: result.lhr.audits["total-blocking-time"].numericValue,
          cls: result.lhr.audits["cumulative-layout-shift"].numericValue,
        },
        failures: Object.entries(result.lhr.audits)
          .filter(
            ([, v]) =>
              v.score !== null &&
              v.score < 0.9 &&
              v.scoreDisplayMode !== "informative",
          )
          .map(([k, v]) => ({ id: k, title: v.title, score: v.score })),
      },
      null,
      2,
    ) + "\n",
  );
  console.log(scores);
  if (Object.values(scores).some((n) => n < 90)) process.exitCode = 1;
} finally {
  browser.kill();
}
