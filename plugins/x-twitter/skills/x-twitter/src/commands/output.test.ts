import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { commands } from "./index.ts";
import { fakeClient } from "../http/fake-client.ts";

/** Runs a command line against canned responses and returns what it printed. */
async function run(argv: string[], routes: Parameters<typeof fakeClient>[0] = {}) {
  const { client, requests } = fakeClient(routes);
  const [name, ...args] = argv;
  return { result: await commands[name](client, args), requests };
}

const ME = { "GET /2/users/me": { data: { id: "me1" } } };

describe("listings", () => {
  it("print the data array, or [] when X sends none", async () => {
    const users = [{ id: "1", username: "alice" }];
    assert.deepEqual((await run(["likers", "20"], { "GET /2/tweets/20/liking_users": { data: users } })).result, users);
    assert.deepEqual((await run(["blocked"], ME)).result, []);
  });

  it("print the whole response with --raw", async () => {
    const response = { data: [{ id: "1" }], meta: { next_token: "abc" } };
    const { result } = await run(["followers", "42", "--raw"], { "GET /2/users/42/followers": response });
    assert.deepEqual(result, response);
  });
});

describe("writes", () => {
  it("print X's whole response", async () => {
    const response = { data: { liked: true } };
    const { result } = await run(["like", "20"], { ...ME, "POST /2/users/me1/likes": response });
    assert.deepEqual(result, response);
  });
});

describe("search", () => {
  it("raises --max-results to X's minimum of 10 and says so", async () => {
    const { result, requests } = await run(["search", "cats", "--max-results", "5"], {
      "GET /2/tweets/search/recent": { data: [{ id: "1" }] },
    });
    assert.match((result as { hint: string }).hint, /raised to 10/);
    assert.equal(new URL(requests[0].url).searchParams.get("max_results"), "10");
  });

  it("hints at the 7-day window when recent search finds nothing", async () => {
    const { result } = await run(["search", "old stuff"]);
    assert.match((result as { hint: string }).hint, /last 7 days/);
    assert.deepEqual((result as { data: unknown }).data, []);
  });

  it("points conversation_id: queries at the thread command", async () => {
    const { result } = await run(["search", "conversation_id:123456 from:user"], {
      "GET /2/tweets/search/recent": { data: [{ id: "1" }] },
    });
    assert.match((result as { hint: string }).hint, /thread 123456/);
  });
});

describe("get", () => {
  it("prints one post as an object and several as an array", async () => {
    const post = { id: "20", text: "hi" };
    assert.deepEqual((await run(["get", "20"], { "GET /2/tweets/20": { data: post } })).result, post);
    assert.deepEqual((await run(["get", "20,21"], { "GET /2/tweets": { data: [post] } })).result, [post]);
  });

  it("hints when an article comes back without its plain_text", async () => {
    const post = { id: "20", article: { title: "T" } };
    const { result } = await run(["get", "20", "--fields", "text"], { "GET /2/tweets/20": { data: post } });
    assert.match((result as { hint: string }).hint, /article\.plain_text/);
  });

  it("does not hint when the article text is there", async () => {
    const post = { id: "20", article: { title: "T", plain_text: "body" } };
    const { result } = await run(["get", "20"], { "GET /2/tweets/20": { data: post } });
    assert.deepEqual(result, post);
  });
});

describe("thread", () => {
  const tweet = (id: string, day: number) => ({
    id,
    conversation_id: "100",
    created_at: `2024-06-0${day}T00:00:00Z`,
  });

  it("follows next_token across pages and sorts the conversation oldest-first", async () => {
    const { result, requests } = await run(["thread", "200"], {
      "GET /2/tweets/200": { data: tweet("200", 2) },
      "GET /2/tweets/search/recent": (url: URL) =>
        url.searchParams.get("next_token") === "page2"
          ? { data: [tweet("100", 1), tweet("200", 2)], meta: {} }
          : { data: [tweet("300", 3), tweet("200", 2)], meta: { next_token: "page2" } },
    });

    assert.deepEqual((result as { id: string }[]).map((t) => t.id), ["100", "200", "300"]);
    assert.equal(requests.length, 3);
  });

  it("fetches the root when search missed it", async () => {
    const { result } = await run(["thread", "200"], {
      "GET /2/tweets/200": { data: tweet("200", 2) },
      "GET /2/tweets/search/recent": { data: [tweet("200", 2), tweet("300", 3)], meta: {} },
      "GET /2/tweets/100": { data: tweet("100", 1) },
    });
    assert.deepEqual((result as { id: string }[]).map((t) => t.id), ["100", "200", "300"]);
  });

  it("hints at --all when recent search found nothing beyond the seed", async () => {
    const { result } = await run(["thread", "100"], { "GET /2/tweets/100": { data: tweet("100", 1) } });
    assert.match((result as { hint: string }).hint, /--all/);
    assert.deepEqual((result as { data: { id: string }[] }).data.map((t) => t.id), ["100"]);
  });

  it("wraps the posts in { data } with --raw", async () => {
    const { result } = await run(["thread", "100", "--raw"], {
      "GET /2/tweets/100": { data: tweet("100", 1) },
      "GET /2/tweets/search/recent": { data: [tweet("100", 1), tweet("300", 3)], meta: {} },
    });
    assert.deepEqual(result, { data: [tweet("100", 1), tweet("300", 3)] });
  });

  it("reports a missing seed instead of searching", async () => {
    const { result, requests } = await run(["thread", "1"]);
    assert.deepEqual(result, { error: "Tweet 1 not found." });
    assert.equal(requests.length, 1);
  });
});

describe("me and user", () => {
  it("me prints the user, and the whole response with --pinned-tweet", async () => {
    const response = { data: { id: "me1" }, includes: { tweets: [{ id: "9" }] } };
    assert.deepEqual((await run(["me"], { "GET /2/users/me": response })).result, response.data);
    assert.deepEqual((await run(["me", "--pinned-tweet"], { "GET /2/users/me": response })).result, response);
  });

  it("user prints one user as an object and several as an array", async () => {
    const one = { id: "42", username: "alice" };
    assert.deepEqual((await run(["user", "42"], { "GET /2/users/42": { data: one } })).result, one);
    assert.deepEqual((await run(["user", "42,43"], { "GET /2/users": { data: [one] } })).result, [one]);
  });
});
