import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { parseArgs, PAGINATION, RAW } from "../lib/args.js";

describe("parseArgs", () => {
  it("parses a positional argument", () => {
    const result = parseArgs<{ title: string }>(["My Post"], {
      positional: { key: "title", label: "Post title" },
    });
    assert.equal(result.title, "My Post");
  });

  it("throws when positional is missing", () => {
    assert.throws(
      () => parseArgs([], { positional: { key: "title", label: "Post title" } }),
      /Post title is required/,
    );
  });

  it("throws when positional looks like a flag", () => {
    assert.throws(
      () => parseArgs(["--foo"], { positional: { key: "title", label: "Post title" } }),
      /Post title is required/,
    );
  });

  it("parses string flags", () => {
    const result = parseArgs<{ status: string }>(["--status", "draft"], {
      flags: { "--status": { key: "status", type: "string" } },
    });
    assert.equal(result.status, "draft");
  });

  it("parses number flags", () => {
    const result = parseArgs<{ limit: number }>(["--limit", "50"], {
      flags: { "--limit": { key: "limit", type: "number" } },
    });
    assert.equal(result.limit, 50);
  });

  it("throws on non-numeric number flag", () => {
    assert.throws(
      () =>
        parseArgs(["--limit", "abc"], {
          flags: { "--limit": { key: "limit", type: "number" } },
        }),
      /requires a numeric value/,
    );
  });

  it("parses boolean flags", () => {
    const result = parseArgs<{ raw: boolean }>(["--raw"], {
      flags: { "--raw": { key: "raw", type: "boolean" } },
    });
    assert.equal(result.raw, true);
  });

  it("defaults boolean flags to false", () => {
    const result = parseArgs<{ raw: boolean }>([], {
      flags: { "--raw": { key: "raw", type: "boolean" } },
    });
    assert.equal(result.raw, false);
  });

  it("parses string[] flags", () => {
    const result = parseArgs<{ tags: string[] }>(["--tags", "a,b,c"], {
      flags: { "--tags": { key: "tags", type: "string[]" } },
    });
    assert.deepEqual(result.tags, ["a", "b", "c"]);
  });

  it("applies defaults", () => {
    const result = parseArgs<{ limit: number }>([], {
      flags: { "--limit": { key: "limit", type: "number" } },
      defaults: { limit: 10 },
    });
    assert.equal(result.limit, 10);
  });

  it("overrides defaults with explicit flags", () => {
    const result = parseArgs<{ limit: number }>(["--limit", "25"], {
      flags: { "--limit": { key: "limit", type: "number" } },
      defaults: { limit: 10 },
    });
    assert.equal(result.limit, 25);
  });

  it("throws on unknown flags", () => {
    assert.throws(
      () => parseArgs(["--unknown"], { flags: {} }),
      /Unknown flag: --unknown/,
    );
  });

  it("composes PAGINATION and RAW flag sets", () => {
    const result = parseArgs<{ limit: number; page: number; raw: boolean }>(
      ["--limit", "20", "--page", "3", "--raw"],
      { flags: { ...PAGINATION, ...RAW } },
    );
    assert.equal(result.limit, 20);
    assert.equal(result.page, 3);
    assert.equal(result.raw, true);
  });

  it("combines positional with flags", () => {
    const result = parseArgs<{ postId: string; raw: boolean }>(
      ["post_123", "--raw"],
      {
        positional: { key: "postId", label: "A post ID" },
        flags: { ...RAW },
      },
    );
    assert.equal(result.postId, "post_123");
    assert.equal(result.raw, true);
  });
});
