import { readFile } from "node:fs/promises";
import path from "node:path";
import postcss from "postcss";

const root = process.cwd();
let config;

try {
  config = JSON.parse(await readFile(path.join(root, "docs.json"), "utf8"));
} catch (error) {
  console.error(`[ERROR] Unable to read docs.json: ${error.message}`);
  process.exit(1);
}

const styles = Array.isArray(config.styles) ? config.styles : [];
let failed = false;

for (const stylesheet of styles) {
  if (typeof stylesheet !== "string" || /^https?:\/\//.test(stylesheet)) {
    continue;
  }

  const filePath = path.resolve(root, stylesheet.replace(/^\/+/, ""));
  try {
    const source = await readFile(filePath, "utf8");
    postcss.parse(source, { from: filePath });
    console.log(`CSS parsed successfully: ${stylesheet}`);
  } catch (error) {
    failed = true;
    console.error(`[ERROR] ${stylesheet}: ${error.message}`);
  }
}

if (failed) {
  process.exitCode = 1;
}
