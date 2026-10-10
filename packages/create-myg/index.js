#!/usr/bin/env node
/**
 * `npm create myg` → delegates to the Python `myg` CLI via uvx/pipx/PATH.
 * Keeps one source of truth for the scaffolder instead of reimplementing in JS.
 */
const { spawnSync } = require("node:child_process");

const args = ["init", ...process.argv.slice(2)];

const candidates = [
  ["uvx", ["myg", ...args]],
  ["pipx", ["run", "myg", ...args]],
  ["myg", args],
];

for (const [cmd, argv] of candidates) {
  const probe = spawnSync(cmd, ["--version"], { stdio: "ignore", shell: true });
  if (probe.error) continue;
  const result = spawnSync(cmd, argv, { stdio: "inherit", shell: true });
  process.exit(result.status ?? 1);
}

console.error(`
myg needs one of these to run:

  uv     → https://docs.astral.sh/uv/getting-started/installation/   (recommended)
  pipx   → pip install pipx
  python → pip install myg

then run this command again.
`);
process.exit(1);
