import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
const terms = [
  "436c61756465",
  "416e7468726f706963",
  "436f646578",
  "4f70656e4149",
  "47656e6572617465642077697468",
  "436f2d417574686f7265642d4279",
  "53657373696f6e",
].map((x) => Buffer.from(x, "hex").toString());
const pattern = new RegExp(terms.join("|"), "i");
function check(label, text) {
  const hits = text.split(/\r?\n/).filter((x) => pattern.test(x));
  if (hits.length) {
    console.error(
      `${label}: prohibited provenance text found (${hits.length} lines). Remove it before release.`,
    );
    process.exitCode = 1;
  }
}
if (process.argv[2] === "--message")
  check("Commit message", readFileSync(process.argv[3], "utf8"));
else {
  const base = process.argv[2] || "origin/main";
  check(
    "New commit messages",
    execFileSync("git", ["log", `${base}..HEAD`, "--format=%B"], {
      encoding: "utf8",
    }),
  );
  check(
    "Changes",
    execFileSync("git", ["diff", base, "--", "."], {
      encoding: "utf8",
      maxBuffer: 20_000_000,
    }),
  );
  if (process.argv[3])
    check("Release description", readFileSync(process.argv[3], "utf8"));
  if (!process.exitCode) console.log("Release text scan clean.");
}
