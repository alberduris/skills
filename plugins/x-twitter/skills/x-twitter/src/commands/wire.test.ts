import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { commands } from "./index.ts";
import { fakeClient, type SentRequest } from "../http/fake-client.ts";
import type { AuthMode } from "../http/client.ts";

/**
 * The wire contract: for each command line, every request the CLI sends, in
 * order, exactly as X receives it. Paths and parameter names are X's own, so
 * each line can be checked against X's API reference as written.
 */

const API = "https://api.x.com";
const GET = (url: string, auth: AuthMode = "user"): SentRequest => ({ method: "GET", url: API + url, auth });
const POST = (url: string, body: unknown): SentRequest => ({ method: "POST", url: API + url, auth: "user", body });
const PUT = (url: string, body: unknown): SentRequest => ({ method: "PUT", url: API + url, auth: "user", body });
const DELETE = (url: string): SentRequest => ({ method: "DELETE", url: API + url, auth: "user" });

// Default field sets as they appear in the query string
const TWEETS =
  "tweet.fields=article%2Cauthor_id%2Ccreated_at%2Cconversation_id%2Cpaid_partnership" +
  "%2Cpublic_metrics%2Creferenced_tweets%2Cin_reply_to_user_id%2Ctext" +
  "&expansions=author_id&user.fields=name%2Cusername";
const USERS =
  "user.fields=created_at%2Cdescription%2Cid%2Cname%2Cprofile_image_url" +
  "%2Cpublic_metrics%2Cusername%2Cverified_type";
const USERS_EXTENDED =
  USERS + "%2Cconnection_status%2Clocation%2Cprotected%2Creceives_your_dm%2Curl";
const COMMUNITIES =
  "community.fields=access%2Ccreated_at%2Cdescription%2Cid%2Cjoin_policy%2Cmember_count%2Cname";
const NEWS =
  "news.fields=category%2Ccluster_posts_results%2Ccontexts%2Cdisclaimer%2Chook" +
  "%2Ckeywords%2Cname%2Csummary%2Cupdated_at";

// Lookups that other commands make first: the account is me1, @alice is 42,
// and tweet 200 belongs to conversation 100.
const ROUTES = {
  "GET /2/users/me": { data: { id: "me1" } },
  "GET /2/users/by/username/alice": { data: { id: "42" } },
  "GET /2/tweets/200": { data: { id: "200", conversation_id: "100" } },
};
const ME = GET("/2/users/me");
const ALICE = GET("/2/users/by/username/alice");

const CASES: [string[], SentRequest[]][] = [
  // Core
  [["me"], [GET(`/2/users/me?${USERS_EXTENDED}`)]],
  [["me", "--fields", "id,username"], [GET("/2/users/me?user.fields=id%2Cusername")]],
  [["me", "--pinned-tweet"], [
    GET(`/2/users/me?${USERS_EXTENDED}&expansions=pinned_tweet_id&tweet.fields=created_at%2Ctext%2Cpublic_metrics`),
  ]],
  [["search", 'from:alice "hello world"'], [
    GET(`/2/tweets/search/recent?query=from%3Aalice%20%22hello%20world%22&${TWEETS}`),
  ]],
  [["search", "cats", "--all", "--max-results", "50", "--sort", "recent",
    "--start-time", "2024-01-01T00:00:00Z", "--end-time", "2024-12-31T00:00:00Z",
    "--since-id", "1", "--until-id", "2", "--next-token", "tok", "--fields", "text,id"], [
    GET(
      "/2/tweets/search/all?query=cats&tweet.fields=text%2Cid&expansions=author_id&user.fields=name%2Cusername" +
        "&max_results=50&sort_order=recency&start_time=2024-01-01T00%3A00%3A00Z&end_time=2024-12-31T00%3A00%3A00Z" +
        "&since_id=1&until_id=2&next_token=tok",
      "app-only",
    ),
  ]],
  [["get", "20"], [GET(`/2/tweets/20?${TWEETS}`)]],
  [["get", "20,21"], [GET(`/2/tweets?ids=20%2C21&${TWEETS}`)]],
  [["post", "hello"], [POST("/2/tweets", { text: "hello" })]],
  [["post", "hello", "--reply-to", "20", "--quote", "21", "--reply-settings", "mentioned", "--paid-partnership"], [
    POST("/2/tweets", {
      text: "hello",
      reply: { in_reply_to_tweet_id: "20" },
      quote_tweet_id: "21",
      reply_settings: "mentionedUsers",
      paid_partnership: true,
    }),
  ]],
  [["delete", "20"], [DELETE("/2/tweets/20")]],
  [["thread", "200"], [
    GET(`/2/tweets/200?${TWEETS}`),
    GET(`/2/tweets/search/recent?query=conversation_id%3A100&${TWEETS}&max_results=100`),
    GET(`/2/tweets/100?${TWEETS}`),
  ]],
  [["thread", "200", "--all"], [
    GET(`/2/tweets/200?${TWEETS}`, "app-only"),
    GET(`/2/tweets/search/all?query=conversation_id%3A100&${TWEETS}&max_results=100`, "app-only"),
    GET(`/2/tweets/100?${TWEETS}`, "app-only"),
  ]],

  // Engagement
  [["like", "20"], [ME, POST("/2/users/me1/likes", { tweet_id: "20" })]],
  [["unlike", "20"], [ME, DELETE("/2/users/me1/likes/20")]],
  [["repost", "20"], [ME, POST("/2/users/me1/retweets", { tweet_id: "20" })]],
  [["unrepost", "20"], [ME, DELETE("/2/users/me1/retweets/20")]],

  // Social
  [["user", "@alice"], [GET(`/2/users/by/username/alice?${USERS_EXTENDED}`)]],
  [["user", "42"], [GET(`/2/users/42?${USERS_EXTENDED}`)]],
  [["user", "42,43"], [GET(`/2/users?ids=42%2C43&${USERS_EXTENDED}`)]],
  [["follow", "@alice"], [ME, ALICE, POST("/2/users/me1/following", { target_user_id: "42" })]],
  [["unfollow", "42"], [ME, DELETE("/2/users/me1/following/42")]],
  [["followers", "alice", "--max-results", "10"], [ALICE, GET(`/2/users/42/followers?${USERS}&max_results=10`)]],
  [["following", "42", "--next-token", "tok"], [GET(`/2/users/42/following?${USERS}&pagination_token=tok`)]],

  // Feed
  [["timeline", "--exclude", "replies,rts", "--max-results", "5"], [
    ME,
    GET(`/2/users/me1/timelines/reverse_chronological?${TWEETS}&max_results=5&exclude=replies%2Cretweets`),
  ]],
  [["mentions", "--start-time", "2024-06-01T00:00:00Z", "--next-token", "tok"], [
    ME,
    GET(`/2/users/me1/mentions?${TWEETS}&pagination_token=tok&start_time=2024-06-01T00%3A00%3A00Z`),
  ]],
  [["bookmarks"], [ME, GET(`/2/users/me1/bookmarks?${TWEETS}`)]],

  // Moderation
  [["mute", "alice"], [ME, ALICE, POST("/2/users/me1/muting", { target_user_id: "42" })]],
  [["unmute", "42"], [ME, DELETE("/2/users/me1/muting/42")]],
  [["muted", "--max-results", "5", "--next-token", "tok"], [
    ME,
    GET(`/2/users/me1/muting?${USERS}&max_results=5&pagination_token=tok`),
  ]],
  [["blocked"], [ME, GET(`/2/users/me1/blocking?${USERS}`)]],
  [["hide-reply", "20"], [PUT("/2/tweets/20/hidden", { hidden: true })]],

  // Analytics
  [["likers", "20"], [GET(`/2/tweets/20/liking_users?${USERS}`)]],
  [["reposters", "20"], [GET(`/2/tweets/20/retweeted_by?${USERS}`)]],
  [["quotes", "20", "--max-results", "10"], [GET(`/2/tweets/20/quote_tweets?${TWEETS}&max_results=10`)]],
  [["count", "from:alice", "--granularity", "daily"], [
    GET("/2/tweets/counts/recent?query=from%3Aalice&granularity=day", "app-only"),
  ]],
  [["count", "cats", "--all", "--next-token", "tok"], [
    GET("/2/tweets/counts/all?query=cats&next_token=tok", "app-only"),
  ]],
  [["reposts-of-me", "--max-results", "10"], [GET(`/2/users/reposts_of_me?${TWEETS}&max_results=10`)]],

  // Discovery
  [["search-users", "ada", "--next-token", "tok"], [GET(`/2/users/search?query=ada&${USERS}&next_token=tok`)]],
  [["trending"], [GET("/2/trends/by/woeid/1", "app-only")]],
  [["trending", "--personalized"], [GET("/2/users/personalized_trends")]],

  // Communities and news
  [["community", "99"], [GET(`/2/communities/99?${COMMUNITIES}`)]],
  [["search-communities", "rust", "--max-results", "10"], [
    GET(`/2/communities/search?query=rust&${COMMUNITIES}&max_results=10`),
  ]],
  [["news", "77"], [GET(`/2/news/77?${NEWS}`)]],
  [["search-news", "ai", "--max-age-hours", "24", "--fields", "name,summary"], [
    GET("/2/news/search?query=ai&news.fields=name%2Csummary&max_age_hours=24"),
  ]],

  // Account
  [["usage", "--days", "7"], [GET("/2/usage/tweets?days=7", "app-only")]],
];

describe("wire contract", () => {
  for (const [[name, ...args], expected] of CASES) {
    it([name, ...args].join(" "), async () => {
      const { client, requests } = fakeClient(ROUTES);
      await commands[name](client, args);
      assert.deepEqual(requests, expected);
    });
  }

  it("covers every command", () => {
    const covered = new Set(CASES.map(([[name]]) => name));
    assert.deepEqual(Object.keys(commands).filter((name) => !covered.has(name)), []);
  });
});
