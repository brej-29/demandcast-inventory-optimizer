import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";
const paths = execFileSync("git", ["ls-files", "-z"], { encoding: "utf8" })
  .split("\0")
  .filter(Boolean);
const patterns = [
  ["private-key", /-----BEGIN (?:RSA |EC |ED25519 |OPENSSH )?PRIVATE KEY-----/],
  ["access-token", /gh[pousr]_[A-Za-z0-9]{30,}/],
  ["cloud-access-key", /AKIA[A-Z0-9]{16}/],
  ["service-key", /\bsk-[A-Za-z0-9]{32,}/],
];
let hits = 0;
for (const path of paths) {
  if (/\.(png|jpg|ttf|woff2|pkl|zip)$/.test(path)) continue;
  const data = readFileSync(path, "utf8");
  for (const [name, p] of patterns)
    if (p.test(data)) {
      console.error(`${path}: potential ${name}`);
      hits++;
    }
}
if (hits) process.exitCode = 1;
else
  console.log(
    `No supported secret patterns found in ${paths.length} tracked files. This is a bounded scan, not a proof of absence.`,
  );
