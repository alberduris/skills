import { describe, it, beforeEach, mock } from "node:test";
import assert from "node:assert/strict";
import { mockClient } from "./helpers/mock-client.js";
import { _resetMyIdCache } from "../lib/resolve.js";
import { USER_FIELDS } from "../lib/fields.js";
import { followers } from "../commands/followers.js";
import { searchUsers } from "../commands/search-users.js";
import { bookmarks } from "../commands/bookmark.js";
import { blocked } from "../commands/blocked.js";
import { muted } from "../commands/mute.js";
import { quotes } from "../commands/quotes.js";
import { repostsOfMe } from "../commands/reposts-of-me.js";

describe("Pattern C — listings with pagination", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  describe("followers", () => {
    it("passes USER_FIELDS and returns data array", async () => {
      const userData = [{ id: "1", username: "alice" }];
      const getFollowers = mock.fn(async () => ({ data: userData }));
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { getFollowers, getByUsername },
      });

      const result = await followers(client, ["someuser"]);
      assert.deepEqual(result, userData);

      const opts = getFollowers.mock.calls[0].arguments[1];
      assert.deepEqual(opts.userFields, USER_FIELDS);
    });

    it("returns full response with --raw", async () => {
      const fullResponse = {
        data: [{ id: "1" }],
        meta: { next_token: "abc" },
      };
      const getFollowers = mock.fn(async () => fullResponse);
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { getFollowers, getByUsername },
      });

      const result = await followers(client, ["someuser", "--raw"]);
      assert.deepEqual(result, fullResponse);
    });

    it("passes maxResults and paginationToken", async () => {
      const getFollowers = mock.fn(async () => ({ data: [] }));
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { getFollowers, getByUsername },
      });

      await followers(client, [
        "someuser",
        "--max-results",
        "5",
        "--next-token",
        "tok1",
      ]);

      const opts = getFollowers.mock.calls[0].arguments[1];
      assert.equal(opts.maxResults, 5);
      assert.equal(opts.paginationToken, "tok1");
    });

    it("throws on unknown flag", async () => {
      const client = mockClient({ users: {} });
      await assert.rejects(
        () => followers(client, ["someuser", "--bogus"]),
        /Unknown flag: --bogus/,
      );
    });
  });

  describe("search-users", () => {
    it("uses nextToken (not paginationToken)", async () => {
      const searchFn = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ users: { search: searchFn } });

      await searchUsers(client, ["query", "--next-token", "tok2"]);

      const opts = searchFn.mock.calls[0].arguments[1];
      assert.equal(opts.nextToken, "tok2");
      assert.equal(opts.paginationToken, undefined);
    });
  });

  describe("bookmarks", () => {
    it("resolves myId and passes tweet fields", async () => {
      const getBookmarks = mock.fn(async () => ({
        data: [{ id: "t1", text: "hello" }],
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({
        users: { getBookmarks, getMe },
      });

      const result = await bookmarks(client, []);
      assert.deepEqual(result, [{ id: "t1", text: "hello" }]);
      assert.equal(getBookmarks.mock.calls[0].arguments[0], "me1");
    });
  });

  describe("blocked", () => {
    it("returns empty array when data is null", async () => {
      const getBlocking = mock.fn(async () => ({ data: null }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({
        users: { getBlocking, getMe },
      });

      const result = await blocked(client, []);
      assert.deepEqual(result, []);
    });
  });

  describe("muted", () => {
    it("resolves myId and returns user data", async () => {
      const userData = [{ id: "1", username: "muted_user" }];
      const getMuting = mock.fn(async () => ({ data: userData }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getMuting, getMe } });

      const result = await muted(client, []);
      assert.deepEqual(result, userData);
      assert.equal(getMuting.mock.calls[0].arguments[0], "me1");

      const opts = getMuting.mock.calls[0].arguments[1];
      assert.deepEqual(opts.userFields, USER_FIELDS);
    });
  });

  describe("quotes", () => {
    it("passes tweetId positional and returns data", async () => {
      const quoteData = [{ id: "q1", text: "quote tweet" }];
      const getQuoted = mock.fn(async () => ({ data: quoteData }));
      const client = mockClient({ posts: { getQuoted } });

      const result = await quotes(client, ["tweet123"]);
      assert.deepEqual(result, quoteData);
      assert.equal(getQuoted.mock.calls[0].arguments[0], "tweet123");
    });

    it("--raw returns full response", async () => {
      const fullResp = { data: [{ id: "q1" }], meta: { next_token: "t" } };
      const getQuoted = mock.fn(async () => fullResp);
      const client = mockClient({ posts: { getQuoted } });

      const result = await quotes(client, ["tweet123", "--raw"]);
      assert.deepEqual(result, fullResp);
    });
  });

  describe("reposts-of-me", () => {
    it("takes no positional arg and returns data", async () => {
      const data = [{ id: "r1", text: "reposted" }];
      const getRepostsOfMe = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getRepostsOfMe } });

      const result = await repostsOfMe(client, []);
      assert.deepEqual(result, data);
    });

    it("passes pagination flags", async () => {
      const getRepostsOfMe = mock.fn(async () => ({ data: [] }));
      const client = mockClient({ users: { getRepostsOfMe } });

      await repostsOfMe(client, ["--max-results", "10", "--next-token", "tok"]);

      const opts = getRepostsOfMe.mock.calls[0].arguments[0];
      assert.equal(opts.maxResults, 10);
      assert.equal(opts.paginationToken, "tok");
    });
  });

  describe("falsy zero regression", () => {
    it("maxResults=0 is passed through (not silently dropped)", async () => {
      const getFollowers = mock.fn(async () => ({ data: [] }));
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { getFollowers, getByUsername },
      });

      await followers(client, ["someuser", "--max-results", "0"]);

      const opts = getFollowers.mock.calls[0].arguments[1];
      assert.equal(opts.maxResults, 0);
    });
  });
});
