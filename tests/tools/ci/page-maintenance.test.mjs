import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const { targetsFor } = require("../../../scripts/page-maintenance.js");

test("builds edit and issue links for the current page", () => {
  const targets = targetsFor("/development");

  assert.equal(
    targets.edit,
    "https://github.com/necc-hub/docs/edit/main/development.mdx",
  );

  const issue = new URL(targets.issue);
  assert.equal(issue.origin + issue.pathname, "https://github.com/necc-hub/docs/issues/new");
  assert.equal(issue.searchParams.get("title"), "docs: development");
  assert.match(issue.searchParams.get("body"), /https:\/\/docs\.newenergycoder\.club\/development/);
  assert.equal(issue.searchParams.get("labels"), "documentation");
});

test("maps the homepage to index.mdx", () => {
  assert.equal(targetsFor("/").edit, "https://github.com/necc-hub/docs/edit/main/index.mdx");
});

test("handles nested and percent-encoded page paths", () => {
  const targets = targetsFor("/mechanical/lumenpnp/doc-4/");

  assert.equal(
    targets.edit,
    "https://github.com/necc-hub/docs/edit/main/mechanical/lumenpnp/doc-4.mdx",
  );
  assert.equal(
    targetsFor("/skills/TRAE-debugger").edit,
    "https://github.com/necc-hub/docs/edit/main/skills/TRAE-debugger.mdx",
  );
});