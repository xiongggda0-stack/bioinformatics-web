import assert from "node:assert/strict";
import test from "node:test";

import { formatDisplayDate } from "../lib/dateFormat.mjs";

test("formats display dates in UTC so server and browser agree near midnight", () => {
  assert.equal(formatDisplayDate("2026-05-25T18:11:29.970961Z"), "2026/5/25");
});
