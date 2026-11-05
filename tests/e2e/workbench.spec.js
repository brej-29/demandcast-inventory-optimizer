import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile, mkdir } from "node:fs/promises";

async function ready(page) {
  await expect(page.locator("#export")).toBeEnabled();
  await expect(page.locator("#loading")).toBeHidden();
}
test("core job: import, edit assumptions, inspect checks, export matching decision", async ({
  page,
}) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("./");
  await ready(page);
  const download = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download an example", exact: true })
    .click();
  const csv = await download;
  const path = await csv.path();
  await page.locator("#file").setInputFiles(path);
  await ready(page);
  await expect(page.locator("#source-label")).toContainText("Your CSV");
  await page.getByLabel("On hand units", { exact: true }).fill("0");
  await ready(page);
  await page.getByLabel("Supplier pack units", { exact: true }).fill("24");
  await ready(page);
  const units = Number(
    (await page.locator("#order-qty").innerText()).replaceAll(",", ""),
  );
  expect(units).toBeGreaterThan(0);
  expect(units % 24).toBe(0);
  await page.getByText("Inspect cycle-by-cycle results").click();
  await expect(page.locator("#cycles-body tr")).toHaveCount(12);
  const output = page.waitForEvent("download");
  await page.locator("#export").click();
  const exported = await output;
  const text = await readFile(await exported.path(), "utf8");
  expect(text).toContain(`"order_units","${units}"`);
  expect(text).toContain('"pack","24"');
  await page.getByRole("link", { name: "Evidence lab", exact: true }).click();
  await expect(page.locator("#benchmark")).toContainText("Hypothesis not met");
  await page.getByRole("link", { name: "How it works", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Why this exists", exact: true }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});
test("invalid import and invalid settings remove stale recommendations", async ({
  page,
}) => {
  await mkdir(".impeccable/review", { recursive: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("./");
  await ready(page);
  await page.getByLabel("Supplier lead time days", { exact: true }).fill("0");
  await expect(page.locator("#error")).toBeVisible();
  await expect(page.locator("#export")).toBeDisabled();
  await expect(page.locator("#order-qty")).toHaveText("—");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: ".impeccable/review/mobile-error.png",
    fullPage: true,
  });
  await page.getByLabel("Supplier lead time days", { exact: true }).fill("7");
  await ready(page);
  await page
    .locator("#file")
    .setInputFiles({
      name: "broken.csv",
      mimeType: "text/csv",
      buffer: Buffer.from("date,sales\n2025-01-01,-4"),
    });
  await expect(page.locator("#error")).toBeVisible();
  await expect(page.locator("#empty")).toBeVisible();
  await expect(page.locator("#workspace")).toBeHidden();
  await page
    .getByRole("button", { name: "Explore a synthetic example" })
    .click();
  await ready(page);
  await page.getByRole("button", { name: "Clear", exact: true }).click();
  await expect(page.locator("#empty")).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: ".impeccable/review/mobile-empty.png",
    fullPage: true,
  });
});
test("offline local calculation, empty state and historical retail example", async ({
  page,
  context,
}) => {
  await page.goto("./");
  await ready(page);
  await context.setOffline(true);
  await expect(page.locator("#offline")).toBeVisible();
  await page.getByLabel("On hand units", { exact: true }).fill("100000");
  await ready(page);
  await expect(page.locator("#order-qty")).toHaveText("0");
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: ".impeccable/review/desktop-offline.png",
    fullPage: true,
  });
  await context.setOffline(false);
  await page.getByLabel("Choose a dataset").selectOption("retail");
  await ready(page);
  await expect(page.locator("#series-name")).toContainText("22197");
  await expect(page.locator("#source-label")).toContainText("historical");
});
test("worker failure blocks purchase recommendation", async ({ page }) => {
  await page.route("**/worker.js", (r) => r.abort());
  await page.goto("./");
  await expect(page.locator("#error")).toBeVisible();
  await expect(page.locator("#export")).toBeDisabled();
});
test("benchmark fetch failure has a working retry", async ({ page }) => {
  await page.route("**/evaluation.json", (r) => r.abort());
  await page.goto("./#evidence");
  await expect(page.getByRole("button", { name: "try again" })).toBeVisible();
  await page.unroute("**/evaluation.json");
  await page.getByRole("button", { name: "try again" }).click();
  await expect(page.locator("#benchmark")).toContainText("Hypothesis not met");
});
test("keyboard navigation and WCAG AA scans for every view", async ({
  page,
}) => {
  await page.goto("./");
  await ready(page);
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to workspace" }),
  ).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page.locator("#main")).toBeFocused();
  for (const route of ["planner", "evidence", "method"]) {
    await page.goto(`./#${route}`);
    if (route === "planner") await ready(page);
    if (route === "evidence")
      await expect(page.locator("#benchmark")).toContainText(
        "Hypothesis not met",
      );
    const a = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(
      a.violations.map((x) => ({
        id: x.id,
        description: x.description,
        nodes: x.nodes.map((n) => n.target),
      })),
    ).toEqual([]);
  }
});
test("responsive screenshots: phone, tablet, desktop; no horizontal overflow", async ({
  page,
}) => {
  await mkdir(".impeccable/review", { recursive: true });
  for (const [name, width, height] of [
    ["mobile", 390, 844],
    ["tablet", 820, 1180],
    ["desktop", 1440, 1080],
  ]) {
    await page.setViewportSize({ width, height });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("./");
    await ready(page);
    await page.evaluate(() => document.fonts.ready);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `.impeccable/review/${name}.png`,
      fullPage: true,
    });
    await page.goto("./#evidence");
    await expect(page.locator("#benchmark")).toContainText(
      "Hypothesis not met",
    );
    await page.screenshot({
      path: `.impeccable/review/${name}-evidence.png`,
      fullPage: true,
    });
    await page.goto("./#method");
    await expect(
      page.getByRole("heading", { name: "Why this exists", exact: true }),
    ).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `.impeccable/review/${name}-method.png`,
      fullPage: true,
    });
  }
});
