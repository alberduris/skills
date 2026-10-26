import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { parseArgs, PAGINATION, TEMPORAL, type FlagDef } from "./args.ts";

const ALL: Record<string, FlagDef> = { "--all": { key: "all", type: "boolean" } };

describe("parseArgs", () => {
  describe("positional arguments", () => {
    it("extracts positional arg", () => {
      const result = parseArgs<{ query: string }>(["hello"], {
        positional: { key: "query", label: "A query" },
      });
      assert.equal(result.query, "hello");
    });

    it("throws when positional arg is missing", () => {
      assert.throws(
        () =>
          parseArgs([], {
            positional: { key: "query", label: "A query" },
          }),
        /A query is required as the first argument/,
      );
    });

    it("throws when positional arg starts with --", () => {
      assert.throws(
        () =>
          parseArgs(["--foo"], {
            positional: { key: "query", label: "A query" },
          }),
        /A query is required as the first argument/,
      );
    });
  });

  describe("boolean flags", () => {
    it("defaults boolean flags to false", () => {
      const result = parseArgs<{ all: boolean }>([], {
        flags: ALL,
      });
      assert.equal(result.all, false);
    });

    it("sets boolean flag to true when present", () => {
      const result = parseArgs<{ all: boolean }>(["--all"], {
        flags: ALL,
      });
      assert.equal(result.all, true);
    });
  });

  describe("string flags", () => {
    it("parses string flag", () => {
      const result = parseArgs<{ nextToken?: string }>(
        ["--next-token", "abc123"],
        { flags: { "--next-token": { key: "nextToken", type: "string" } } },
      );
      assert.equal(result.nextToken, "abc123");
    });

    it("throws when string flag missing value", () => {
      assert.throws(
        () =>
          parseArgs(["--next-token"], {
            flags: { "--next-token": { key: "nextToken", type: "string" } },
          }),
        /--next-token requires a value/,
      );
    });
  });

  describe("number flags", () => {
    it("parses number flag", () => {
      const result = parseArgs<{ maxResults?: number }>(
        ["--max-results", "10"],
        { flags: { "--max-results": { key: "maxResults", type: "number" } } },
      );
      assert.equal(result.maxResults, 10);
    });

    it("throws on non-numeric value", () => {
      assert.throws(
        () =>
          parseArgs(["--max-results", "abc"], {
            flags: { "--max-results": { key: "maxResults", type: "number" } },
          }),
        /--max-results requires a numeric value, got "abc"/,
      );
    });
  });

  describe("string[] flags", () => {
    it("parses comma-separated values", () => {
      const result = parseArgs<{ fields: string[] }>(
        ["--fields", "text, author_id, created_at"],
        { flags: { "--fields": { key: "fields", type: "string[]" } } },
      );
      assert.deepEqual(result.fields, ["text", "author_id", "created_at"]);
    });
  });

  describe("unknown flags", () => {
    it("throws on unknown flag", () => {
      assert.throws(
        () => parseArgs(["--bogus"], { flags: { ...ALL } }),
        /Unknown flag: --bogus/,
      );
    });
  });

  describe("composable flag sets", () => {
    it("composes PAGINATION + ALL", () => {
      const result = parseArgs<{
        maxResults?: number;
        nextToken?: string;
        all: boolean;
      }>(["--max-results", "5", "--all"], {
        flags: { ...PAGINATION, ...ALL },
      });
      assert.equal(result.maxResults, 5);
      assert.equal(result.all, true);
    });

    it("composes PAGINATION + TEMPORAL + ALL", () => {
      const result = parseArgs<{
        maxResults?: number;
        startTime?: string;
        endTime?: string;
        all: boolean;
      }>(["--start-time", "2024-01-01", "--end-time", "2024-12-31"], {
        flags: { ...PAGINATION, ...TEMPORAL, ...ALL },
      });
      assert.equal(result.startTime, "2024-01-01");
      assert.equal(result.endTime, "2024-12-31");
      assert.equal(result.all, false);
    });
  });

  describe("defaults", () => {
    it("applies defaults", () => {
      const result = parseArgs<{ fields: string[] }>([], {
        flags: { "--fields": { key: "fields", type: "string[]" } },
        defaults: { fields: ["text", "id"] },
      });
      assert.deepEqual(result.fields, ["text", "id"]);
    });

    it("overrides defaults with explicit flag", () => {
      const result = parseArgs<{ fields: string[] }>(
        ["--fields", "author_id"],
        {
          flags: { "--fields": { key: "fields", type: "string[]" } },
          defaults: { fields: ["text", "id"] },
        },
      );
      assert.deepEqual(result.fields, ["author_id"]);
    });
  });

  describe("empty args with no positional", () => {
    it("returns defaults only", () => {
      const result = parseArgs<{ all: boolean }>([], {
        flags: { ...ALL },
      });
      assert.equal(result.all, false);
    });
  });

  describe("positional + flags together", () => {
    it("extracts both positional and flags", () => {
      const result = parseArgs<{
        query: string;
        maxResults?: number;
        all: boolean;
      }>(["cats", "--max-results", "25", "--all"], {
        positional: { key: "query", label: "A query" },
        flags: { ...PAGINATION, ...ALL },
      });
      assert.equal(result.query, "cats");
      assert.equal(result.maxResults, 25);
      assert.equal(result.all, true);
    });
  });
});
