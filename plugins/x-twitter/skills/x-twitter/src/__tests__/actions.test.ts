import { describe, it, beforeEach, mock } from "node:test";
import assert from "node:assert/strict";
import { mockClient } from "./helpers/mock-client.js";
import { _resetMyIdCache } from "../lib/resolve.js";
import { like, unlike } from "../commands/like.js";
import { follow, unfollow } from "../commands/follow.js";
import { del } from "../commands/delete.js";
import { hideReply } from "../commands/hide-reply.js";
import { repost, unrepost } from "../commands/repost.js";
import { bookmark, unbookmark } from "../commands/bookmark.js";
import { mute, unmute } from "../commands/mute.js";

describe("Pattern A — simple actions", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  describe("like", () => {
    it("calls likePost with correct args and returns response", async () => {
      const likePost = mock.fn(async () => ({ data: { liked: true } }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { likePost, getMe } });

      const result = await like(client, ["tweet1"]);
      assert.deepEqual(result, { data: { liked: true } });
      assert.equal(likePost.mock.callCount(), 1);
      assert.equal(likePost.mock.calls[0].arguments[0], "me1");
      assert.deepEqual(likePost.mock.calls[0].arguments[1], {
        body: { tweetId: "tweet1" },
      });
    });

    it("throws when tweet ID is missing", async () => {
      const client = mockClient({ users: {} });
      await assert.rejects(() => like(client, []), /A tweet ID is required/);
    });
  });

  describe("unlike", () => {
    it("calls unlikePost with positional args", async () => {
      const unlikePost = mock.fn(async () => ({ data: { liked: false } }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { unlikePost, getMe } });

      const result = await unlike(client, ["tweet2"]);
      assert.deepEqual(result, { data: { liked: false } });
      assert.equal(unlikePost.mock.calls[0].arguments[0], "me1");
      assert.equal(unlikePost.mock.calls[0].arguments[1], "tweet2");
    });
  });

  describe("del", () => {
    it("calls posts.delete with the ID", async () => {
      const deleteFn = mock.fn(async () => ({ data: { deleted: true } }));
      const client = mockClient({ posts: { delete: deleteFn } });

      const result = await del(client, ["123"]);
      assert.deepEqual(result, { data: { deleted: true } });
      assert.equal(deleteFn.mock.calls[0].arguments[0], "123");
    });
  });

  describe("hideReply", () => {
    it("calls posts.hideReply with hidden: true", async () => {
      const hideReplyFn = mock.fn(async () => ({
        data: { hidden: true },
      }));
      const client = mockClient({ posts: { hideReply: hideReplyFn } });

      const result = await hideReply(client, ["tweet3"]);
      assert.deepEqual(result, { data: { hidden: true } });
      assert.equal(hideReplyFn.mock.calls[0].arguments[0], "tweet3");
      assert.deepEqual(hideReplyFn.mock.calls[0].arguments[1], {
        body: { hidden: true },
      });
    });
  });

  describe("repost", () => {
    it("calls repostPost with myId and tweetId", async () => {
      const repostPost = mock.fn(async () => ({ data: { retweeted: true } }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { repostPost, getMe } });

      const result = await repost(client, ["tweet1"]);
      assert.deepEqual(result, { data: { retweeted: true } });
      assert.equal(repostPost.mock.calls[0].arguments[0], "me1");
      assert.deepEqual(repostPost.mock.calls[0].arguments[1], {
        body: { tweetId: "tweet1" },
      });
    });
  });

  describe("unrepost", () => {
    it("calls unrepostPost with myId and tweetId", async () => {
      const unrepostPost = mock.fn(async () => ({
        data: { retweeted: false },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { unrepostPost, getMe } });

      const result = await unrepost(client, ["tweet2"]);
      assert.deepEqual(result, { data: { retweeted: false } });
      assert.equal(unrepostPost.mock.calls[0].arguments[0], "me1");
      assert.equal(unrepostPost.mock.calls[0].arguments[1], "tweet2");
    });
  });

  describe("bookmark", () => {
    it("calls createBookmark with myId and tweetId", async () => {
      const createBookmark = mock.fn(async () => ({
        data: { bookmarked: true },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { createBookmark, getMe } });

      const result = await bookmark(client, ["tweet1"]);
      assert.deepEqual(result, { data: { bookmarked: true } });
      assert.equal(createBookmark.mock.calls[0].arguments[0], "me1");
      assert.deepEqual(createBookmark.mock.calls[0].arguments[1], {
        tweetId: "tweet1",
      });
    });
  });

  describe("unbookmark", () => {
    it("calls deleteBookmark with myId and tweetId", async () => {
      const deleteBookmark = mock.fn(async () => ({
        data: { bookmarked: false },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { deleteBookmark, getMe } });

      const result = await unbookmark(client, ["tweet2"]);
      assert.deepEqual(result, { data: { bookmarked: false } });
      assert.equal(deleteBookmark.mock.calls[0].arguments[0], "me1");
      assert.equal(deleteBookmark.mock.calls[0].arguments[1], "tweet2");
    });
  });
});

describe("Pattern B — action with user resolution", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  describe("follow", () => {
    it("resolves both myId and targetUserId", async () => {
      const followUser = mock.fn(async () => ({
        data: { following: true },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { followUser, getMe, getByUsername },
      });

      const result = await follow(client, ["@someuser"]);
      assert.deepEqual(result, { data: { following: true } });
      assert.equal(followUser.mock.calls[0].arguments[0], "me1");
      assert.deepEqual(followUser.mock.calls[0].arguments[1], {
        body: { targetUserId: "target1" },
      });
    });

    it("throws when target is missing", async () => {
      const client = mockClient({ users: {} });
      await assert.rejects(
        () => follow(client, []),
        /A username or user ID is required/,
      );
    });
  });

  describe("unfollow", () => {
    it("resolves and calls unfollowUser", async () => {
      const unfollowUser = mock.fn(async () => ({
        data: { following: false },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { unfollowUser, getMe } });

      const result = await unfollow(client, ["99999"]);
      assert.deepEqual(result, { data: { following: false } });
      assert.equal(unfollowUser.mock.calls[0].arguments[0], "me1");
      assert.equal(unfollowUser.mock.calls[0].arguments[1], "99999");
    });
  });

  describe("mute", () => {
    it("resolves both myId and targetUserId", async () => {
      const muteUser = mock.fn(async () => ({ data: { muting: true } }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const getByUsername = mock.fn(async () => ({
        data: { id: "target1" },
      }));
      const client = mockClient({
        users: { muteUser, getMe, getByUsername },
      });

      const result = await mute(client, ["@annoying"]);
      assert.deepEqual(result, { data: { muting: true } });
      assert.equal(muteUser.mock.calls[0].arguments[0], "me1");
      assert.deepEqual(muteUser.mock.calls[0].arguments[1], {
        body: { targetUserId: "target1" },
      });
    });
  });

  describe("unmute", () => {
    it("resolves and calls unmuteUser", async () => {
      const unmuteUser = mock.fn(async () => ({
        data: { muting: false },
      }));
      const getMe = mock.fn(async () => ({ data: { id: "me1" } }));
      const client = mockClient({ users: { unmuteUser, getMe } });

      const result = await unmute(client, ["99999"]);
      assert.deepEqual(result, { data: { muting: false } });
      assert.equal(unmuteUser.mock.calls[0].arguments[0], "me1");
      assert.equal(unmuteUser.mock.calls[0].arguments[1], "99999");
    });
  });
});
