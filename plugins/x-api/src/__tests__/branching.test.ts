import { describe, it, beforeEach, mock } from "node:test";
import assert from "node:assert/strict";
import { mockClient } from "./helpers/mock-client.js";
import { _resetMyIdCache } from "../lib/resolve.js";
import { user } from "../commands/user.js";
import { me } from "../commands/me.js";
import { get } from "../commands/get.js";
import { trending } from "../commands/trending.js";
import { post } from "../commands/post.js";

describe("Pattern E — branching commands", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  describe("user", () => {
    it("comma-separated IDs → getByIds, returns array", async () => {
      const data = [{ id: "1" }, { id: "2" }];
      const getByIds = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getByIds } });

      const result = await user(client, ["1,2"]);
      assert.deepEqual(result, data);
      assert.deepEqual(getByIds.mock.calls[0].arguments[0], ["1", "2"]);
    });

    it("all digits → getById, returns single object", async () => {
      const data = { id: "12345", username: "test" };
      const getById = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getById } });

      const result = await user(client, ["12345"]);
      assert.deepEqual(result, data);
    });

    it("bare string → getByUsername, returns single object", async () => {
      const data = { id: "1", username: "alice" };
      const getByUsername = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getByUsername } });

      const result = await user(client, ["alice"]);
      assert.deepEqual(result, data);
      assert.equal(getByUsername.mock.calls[0].arguments[0], "alice");
    });

    it("@handle strips @ prefix", async () => {
      const data = { id: "1", username: "bob" };
      const getByUsername = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getByUsername } });

      const result = await user(client, ["@bob"]);
      assert.deepEqual(result, data);
      assert.equal(getByUsername.mock.calls[0].arguments[0], "bob");
    });

    it("--raw returns full response", async () => {
      const fullResp = { data: { id: "1" }, includes: {} };
      const getById = mock.fn(async () => fullResp);
      const client = mockClient({ users: { getById } });

      const result = await user(client, ["12345", "--raw"]);
      assert.deepEqual(result, fullResp);
    });
  });

  describe("me", () => {
    it("returns response.data by default", async () => {
      const data = { id: "me1", username: "myuser" };
      const getMe = mock.fn(async () => ({ data }));
      const client = mockClient({ users: { getMe } });

      const result = await me(client, []);
      assert.deepEqual(result, data);
    });

    it("--pinned-tweet returns full response", async () => {
      const fullResp = { data: { id: "me1" }, includes: { tweets: [] } };
      const getMe = mock.fn(async () => fullResp);
      const client = mockClient({ users: { getMe } });

      const result = await me(client, ["--pinned-tweet"]);
      assert.deepEqual(result, fullResp);

      const opts = getMe.mock.calls[0].arguments[0];
      assert.deepEqual(opts.expansions, ["pinned_tweet_id"]);
    });

    it("--raw returns full response", async () => {
      const fullResp = { data: { id: "me1" }, meta: {} };
      const getMe = mock.fn(async () => fullResp);
      const client = mockClient({ users: { getMe } });

      const result = await me(client, ["--raw"]);
      assert.deepEqual(result, fullResp);
    });

    it("--fields overrides default user fields", async () => {
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { getMe } });

      await me(client, ["--fields", "id,username"]);

      const opts = getMe.mock.calls[0].arguments[0];
      assert.deepEqual(opts.userFields, ["id", "username"]);
    });
  });

  describe("get", () => {
    it("single ID → getById", async () => {
      const data = { id: "t1", text: "hello" };
      const getById = mock.fn(async () => ({ data }));
      const client = mockClient({ posts: { getById } });

      const result = await get(client, ["t1"]);
      assert.deepEqual(result, data);
      assert.equal(getById.mock.calls[0].arguments[0], "t1");
    });

    it("multiple IDs → getByIds", async () => {
      const data = [{ id: "t1" }, { id: "t2" }];
      const getByIds = mock.fn(async () => ({ data }));
      const client = mockClient({ posts: { getByIds } });

      const result = await get(client, ["t1,t2"]);
      assert.deepEqual(result, data);
      assert.deepEqual(getByIds.mock.calls[0].arguments[0], ["t1", "t2"]);
    });

    it("--raw returns full response for single", async () => {
      const fullResp = { data: { id: "t1" }, includes: {} };
      const getById = mock.fn(async () => fullResp);
      const client = mockClient({ posts: { getById } });

      const result = await get(client, ["t1", "--raw"]);
      assert.deepEqual(result, fullResp);
    });
  });

  describe("trending", () => {
    it("default → getByWoeid(1)", async () => {
      const data = [{ name: "#test" }];
      const getByWoeid = mock.fn(async () => ({ data }));
      const getPersonalized = mock.fn();
      const client = mockClient({
        trends: { getByWoeid, getPersonalized },
      });

      const result = await trending(client, []);
      assert.deepEqual(result, data);
      assert.equal(getByWoeid.mock.callCount(), 1);
      assert.equal(getByWoeid.mock.calls[0].arguments[0], 1);
      assert.equal(getPersonalized.mock.callCount(), 0);
    });

    it("--personalized → getPersonalized()", async () => {
      const data = [{ name: "#personal" }];
      const getByWoeid = mock.fn();
      const getPersonalized = mock.fn(async () => ({ data }));
      const client = mockClient({
        trends: { getByWoeid, getPersonalized },
      });

      const result = await trending(client, ["--personalized"]);
      assert.deepEqual(result, data);
      assert.equal(getPersonalized.mock.callCount(), 1);
      assert.equal(getByWoeid.mock.callCount(), 0);
    });

    it("--raw returns full response", async () => {
      const fullResp = { data: [{ name: "#test" }], meta: {} };
      const getByWoeid = mock.fn(async () => fullResp);
      const client = mockClient({ trends: { getByWoeid } });

      const result = await trending(client, ["--raw"]);
      assert.deepEqual(result, fullResp);
    });
  });

  describe("post", () => {
    it("creates a post with text", async () => {
      const create = mock.fn(async () => ({
        data: { id: "new1", text: "hello world" },
      }));
      const client = mockClient({ posts: { create } });

      const result = await post(client, ["hello world"]);
      assert.deepEqual(result, { data: { id: "new1", text: "hello world" } });
      assert.deepEqual(create.mock.calls[0].arguments[0], {
        text: "hello world",
      });
    });

    it("--reply-to adds reply.inReplyToTweetId", async () => {
      const create = mock.fn(async () => ({ data: { id: "r1" } }));
      const client = mockClient({ posts: { create } });

      await post(client, ["my reply", "--reply-to", "parent123"]);

      const body = create.mock.calls[0].arguments[0];
      assert.equal(body.text, "my reply");
      assert.deepEqual(body.reply, { inReplyToTweetId: "parent123" });
    });

    it("--quote adds quoteTweetId", async () => {
      const create = mock.fn(async () => ({ data: { id: "q1" } }));
      const client = mockClient({ posts: { create } });

      await post(client, ["quoting this", "--quote", "orig456"]);

      const body = create.mock.calls[0].arguments[0];
      assert.equal(body.text, "quoting this");
      assert.equal(body.quoteTweetId, "orig456");
    });

    it("--reply-settings adds replySettings", async () => {
      const create = mock.fn(async () => ({ data: { id: "p1" } }));
      const client = mockClient({ posts: { create } });

      await post(client, ["limited", "--reply-settings", "mentionedUsers"]);

      const body = create.mock.calls[0].arguments[0];
      assert.equal(body.replySettings, "mentionedUsers");
    });

    it("combines all flags", async () => {
      const create = mock.fn(async () => ({ data: { id: "c1" } }));
      const client = mockClient({ posts: { create } });

      await post(client, [
        "complex post",
        "--reply-to",
        "parent1",
        "--quote",
        "orig1",
        "--reply-settings",
        "following",
      ]);

      const body = create.mock.calls[0].arguments[0];
      assert.equal(body.text, "complex post");
      assert.deepEqual(body.reply, { inReplyToTweetId: "parent1" });
      assert.equal(body.quoteTweetId, "orig1");
      assert.equal(body.replySettings, "following");
    });
  });
});
