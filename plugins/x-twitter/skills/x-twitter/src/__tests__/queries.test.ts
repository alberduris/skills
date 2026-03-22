import { describe, it, beforeEach, mock } from "node:test";
import assert from "node:assert/strict";
import { mockClient } from "./helpers/mock-client.js";
import { _resetMyIdCache } from "../lib/resolve.js";
import { search } from "../commands/search.js";
import { thread } from "../commands/thread.js";
import { count } from "../commands/count.js";
import { timeline } from "../commands/timeline.js";
import { mentions } from "../commands/mentions.js";
import { TWEET_FIELDS } from "../lib/fields.js";

describe("Pattern D — query commands", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  describe("search", () => {
    it("defaults to searchRecent", async () => {
      const searchRecent = mock.fn(async () => ({
        data: [{ text: "hi" }],
      }));
      const searchAll = mock.fn();
      const client = mockClient({
        posts: { searchRecent, searchAll },
      });

      const result = await search(client, ["cats"]);
      assert.deepEqual(result, [{ text: "hi" }]);
      assert.equal(searchRecent.mock.callCount(), 1);
      assert.equal(searchAll.mock.callCount(), 0);
      assert.equal(searchRecent.mock.calls[0].arguments[0], "cats");
    });

    it("uses searchAll with --all", async () => {
      const searchRecent = mock.fn();
      const searchAll = mock.fn(async () => ({ data: [] }));
      const client = mockClient({
        posts: { searchRecent, searchAll },
      });

      await search(client, ["cats", "--all"]);
      assert.equal(searchAll.mock.callCount(), 1);
      assert.equal(searchRecent.mock.callCount(), 0);
    });

    it("passes --sort, --since-id through", async () => {
      const searchRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { searchRecent } });

      await search(client, [
        "dogs",
        "--sort",
        "recency",
        "--since-id",
        "111",
      ]);

      const opts = searchRecent.mock.calls[0].arguments[1];
      assert.equal(opts.sortOrder, "recency");
      assert.equal(opts.sinceId, "111");
    });

    it("--fields overrides default tweet fields", async () => {
      const searchRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { searchRecent } });

      await search(client, ["q", "--fields", "text,id"]);

      const opts = searchRecent.mock.calls[0].arguments[1];
      assert.deepEqual(opts.tweetFields, ["text", "id"]);
    });

    it("uses default TWEET_FIELDS when --fields not provided", async () => {
      const searchRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { searchRecent } });

      await search(client, ["q"]);

      const opts = searchRecent.mock.calls[0].arguments[1];
      assert.deepEqual(opts.tweetFields, TWEET_FIELDS);
    });

    it("passes temporal flags correctly", async () => {
      const searchRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { searchRecent } });

      await search(client, [
        "q",
        "--start-time",
        "2024-01-01",
        "--end-time",
        "2024-12-31",
      ]);

      const opts = searchRecent.mock.calls[0].arguments[1];
      assert.equal(opts.startTime, "2024-01-01");
      assert.equal(opts.endTime, "2024-12-31");
    });

    it("hints when recent search returns empty results", async () => {
      const searchRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { searchRecent } });

      const result = (await search(client, ["old stuff"])) as {
        hint: string;
        data: unknown[];
      };
      assert.ok(result.hint);
      assert.match(result.hint, /last 7 days/);
      assert.deepEqual(result.data, []);
    });

    it("nudges thread command when query contains conversation_id:", async () => {
      const searchRecent = mock.fn(async () => ({
        data: [{ text: "reply" }],
      }));
      const client = mockClient({ posts: { searchRecent } });

      const result = (await search(client, [
        "conversation_id:123456 from:user",
      ])) as { hint: string; data: unknown[] };
      assert.ok(result.hint);
      assert.match(result.hint, /thread/);
      assert.match(result.hint, /123456/);
    });
  });

  describe("thread", () => {
    it("fetches seed tweet, searches conversation, sorts chronologically", async () => {
      const getById = mock.fn(async () => ({
        data: { id: "200", text: "seed", conversation_id: "100", created_at: "2024-06-02T00:00:00Z" },
      }));
      const searchRecent = mock.fn(async () => ({
        data: [
          { id: "300", text: "reply", conversation_id: "100", created_at: "2024-06-03T00:00:00Z" },
          { id: "100", text: "root", conversation_id: "100", created_at: "2024-06-01T00:00:00Z" },
          { id: "200", text: "seed", conversation_id: "100", created_at: "2024-06-02T00:00:00Z" },
        ],
        meta: {},
      }));
      const client = mockClient({ posts: { getById, searchRecent } });

      const result = (await thread(client, ["200"])) as { id: string }[];
      assert.equal(result.length, 3);
      assert.equal(result[0].id, "100"); // root first
      assert.equal(result[1].id, "200"); // seed second
      assert.equal(result[2].id, "300"); // reply last
    });

    it("includes root tweet even if not in search results", async () => {
      const getById = mock.fn(async (id: string) => ({
        data: id === "200"
          ? { id: "200", text: "seed", conversation_id: "100", created_at: "2024-06-02T00:00:00Z" }
          : { id: "100", text: "root", conversation_id: "100", created_at: "2024-06-01T00:00:00Z" },
      }));
      const searchRecent = mock.fn(async () => ({
        data: [
          { id: "200", text: "seed", conversation_id: "100", created_at: "2024-06-02T00:00:00Z" },
        ],
        meta: {},
      }));
      const client = mockClient({ posts: { getById, searchRecent } });

      const result = (await thread(client, ["200"])) as { id: string }[];
      assert.equal(result.length, 2);
      assert.equal(result[0].id, "100"); // root fetched separately
      assert.equal(result[1].id, "200");
    });

    it("uses searchAll with --all", async () => {
      const getById = mock.fn(async () => ({
        data: { id: "100", text: "root", conversation_id: "100", created_at: "2024-01-01T00:00:00Z" },
      }));
      const searchRecent = mock.fn();
      const searchAll = mock.fn(async () => ({
        data: [{ id: "100", text: "root", conversation_id: "100", created_at: "2024-01-01T00:00:00Z" }],
        meta: {},
      }));
      const client = mockClient({ posts: { getById, searchRecent, searchAll } });

      await thread(client, ["100", "--all"]);
      assert.equal(searchAll.mock.callCount(), 1);
      assert.equal(searchRecent.mock.callCount(), 0);
    });

    it("hints when recent search returns only root tweet", async () => {
      const getById = mock.fn(async () => ({
        data: { id: "100", text: "root", conversation_id: "100", created_at: "2024-01-01T00:00:00Z" },
      }));
      const searchRecent = mock.fn(async () => ({
        data: [],
        meta: {},
      }));
      const client = mockClient({ posts: { getById, searchRecent } });

      const result = (await thread(client, ["100"])) as { hint: string; data: unknown[] };
      assert.ok(result.hint);
      assert.match(result.hint, /7 days/);
      assert.match(result.hint, /--all/);
    });
  });

  describe("count", () => {
    it("defaults to getCountsRecent", async () => {
      const getCountsRecent = mock.fn(async () => ({
        data: [{ count: 42 }],
      }));
      const getCountsAll = mock.fn();
      const client = mockClient({
        posts: { getCountsRecent, getCountsAll },
      });

      const result = await count(client, ["cats"]);
      assert.deepEqual(result, [{ count: 42 }]);
      assert.equal(getCountsRecent.mock.callCount(), 1);
      assert.equal(getCountsAll.mock.callCount(), 0);
    });

    it("uses getCountsAll with --all", async () => {
      const getCountsRecent = mock.fn();
      const getCountsAll = mock.fn(async () => ({ data: [] }));
      const client = mockClient({
        posts: { getCountsRecent, getCountsAll },
      });

      await count(client, ["cats", "--all"]);
      assert.equal(getCountsAll.mock.callCount(), 1);
    });

    it("passes --granularity through", async () => {
      const getCountsRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { getCountsRecent } });

      await count(client, ["q", "--granularity", "day"]);

      const opts = getCountsRecent.mock.calls[0].arguments[1];
      assert.equal(opts.granularity, "day");
    });

    it("uses nextToken (not paginationToken)", async () => {
      const getCountsRecent = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ posts: { getCountsRecent } });

      await count(client, ["q", "--next-token", "tok"]);

      const opts = getCountsRecent.mock.calls[0].arguments[1];
      assert.equal(opts.nextToken, "tok");
      assert.equal(opts.paginationToken, undefined);
    });
  });

  describe("timeline", () => {
    it("resolves myId and returns data", async () => {
      const tweetData = [{ id: "t1", text: "my timeline" }];
      const getTimeline = mock.fn(async () => ({ data: tweetData }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getTimeline, getMe } });

      const result = await timeline(client, []);
      assert.deepEqual(result, tweetData);
      assert.equal(getTimeline.mock.calls[0].arguments[0], "me1");
    });

    it("passes temporal and pagination flags", async () => {
      const getTimeline = mock.fn(async () => ({ data: [] }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getTimeline, getMe } });

      await timeline(client, [
        "--start-time",
        "2024-01-01",
        "--end-time",
        "2024-12-31",
        "--max-results",
        "50",
        "--next-token",
        "tok",
      ]);

      const opts = getTimeline.mock.calls[0].arguments[1];
      assert.equal(opts.startTime, "2024-01-01");
      assert.equal(opts.endTime, "2024-12-31");
      assert.equal(opts.maxResults, 50);
      assert.equal(opts.paginationToken, "tok");
    });

    it("--raw returns full response", async () => {
      const fullResp = { data: [{ id: "t1" }], meta: { next_token: "x" } };
      const getTimeline = mock.fn(async () => fullResp);
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getTimeline, getMe } });

      const result = await timeline(client, ["--raw"]);
      assert.deepEqual(result, fullResp);
    });
  });

  describe("mentions", () => {
    it("resolves myId and returns data", async () => {
      const mentionData = [{ id: "m1", text: "@me hello" }];
      const getMentions = mock.fn(async () => ({ data: mentionData }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getMentions, getMe } });

      const result = await mentions(client, []);
      assert.deepEqual(result, mentionData);
      assert.equal(getMentions.mock.calls[0].arguments[0], "me1");
    });

    it("passes temporal flags", async () => {
      const getMentions = mock.fn(async () => ({ data: [] }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getMentions, getMe } });

      await mentions(client, [
        "--start-time",
        "2024-06-01",
        "--end-time",
        "2024-06-30",
      ]);

      const opts = getMentions.mock.calls[0].arguments[1];
      assert.equal(opts.startTime, "2024-06-01");
      assert.equal(opts.endTime, "2024-06-30");
    });
  });
});
