import { spawnSync } from "node:child_process";

const command = process.platform === "win32" ? "py" : "python3";
const args = process.platform === "win32" ? ["-3", ...process.argv.slice(2)] : process.argv.slice(2);
const result = spawnSync(command, args, { stdio: "inherit" });

if (result.error?.code === "ENOENT") {
  const installHint = process.platform === "win32"
    ? "Install Python 3 and its py launcher from https://www.python.org/downloads/."
    : "Install Python 3. On macOS, run: brew install python";
  console.error(`Python 3 is required, but ${command} was not found. ${installHint}`);
  process.exit(1);
}

if (result.error) {
  console.error(`Unable to start Python 3: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status ?? 1);
