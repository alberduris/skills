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

const post = (id: string, fields: object = {}) => ({
  id,
  text: `post ${id}`,
  author_id: "42",
  conversation_id: id,
  created_at: "2024-06-01T00:00:00.000Z",
  ...fields,
});

describe("the envelope", () => {
  it("passes meta and errors through as X sent them, and drops includes once folded", async () => {
    const response = {
      data: [post("1")],
      includes: { users: [{ id: "42", name: "Alice", username: "alice" }] },
      meta: { result_count: 1, next_token: "abc" },
      errors: [{ message: "Could not find tweet with ids: [2].", resource_id: "2" }],
    };
    const { result } = await run(["get", "1,2"], { "GET /2/tweets": response });

    assert.deepEqual(Object.keys(result), ["data", "meta", "errors"]);
    assert.deepEqual(result.meta, response.meta);
    assert.deepEqual(result.errors, response.errors);
    assert.deepEqual((result.data as { author: object }[])[0].author, response.includes.users[0]);
  });

  it("prints listings as { data }, with [] when X sends none", async () => {
    const users = [{ id: "1", username: "alice" }];
    const response = { data: users, meta: { result_count: 1, next_token: "abc" } };
    assert.deepEqual((await run(["followers", "42"], { "GET /2/users/42/followers": response })).result, response);
    assert.deepEqual((await run(["blocked"], ME)).result, { data: [] });
  });

  it("prints a write as X's whole response", async () => {
    const response = { data: { liked: true } };
    const { result } = await run(["like", "20"], { ...ME, "POST /2/users/me1/likes": response });
    assert.deepEqual(result, response);
  });

  it("prints a single lookup X could not find as its errors alone", async () => {
    const response = { errors: [{ message: "Could not find user with username: [nobody]." }] };
    const { result } = await run(["user", "nobody"], { "GET /2/users/by/username/nobody": response });
    assert.equal(JSON.stringify(result), JSON.stringify(response));
  });
});

describe("get", () => {
  it("prints an array for one ID as for many", async () => {
    const { result } = await run(["get", "20"], { "GET /2/tweets": { data: [post("20")] } });
    assert.deepEqual((result.data as { id: string }[]).map((p) => p.id), ["20"]);
  });
});

describe("search", () => {
  it("raises --max-results to X's minimum of 10 and says so", async () => {
    const { result, requests } = await run(["search", "cats", "--max-results", "5"], {
      "GET /2/tweets/search/recent": { data: [post("1")] },
    });
    assert.match(result.hints?.[0] ?? "", /raised to 10/);
    assert.equal(new URL(requests[0].url).searchParams.get("max_results"), "10");
  });

  it("hints at the 7-day window when recent search finds nothing", async () => {
    const { result } = await run(["search", "old stuff"], {
      "GET /2/tweets/search/recent": { meta: { result_count: 0 } },
    });
    assert.deepEqual(result.data, []);
    assert.deepEqual(result.meta, { result_count: 0 });
    assert.match(result.hints?.[0] ?? "", /last 7 days/);
  });

  it("points conversation_id: queries at thread and replies", async () => {
    const { result } = await run(["search", "conversation_id:123456 from:user"], {
      "GET /2/tweets/search/recent": { data: [post("1")] },
    });
    assert.match(result.hints?.[0] ?? "", /thread 123456.*replies/);
  });

  it("names --sort when its value is invalid", async () => {
    await assert.rejects(run(["search", "cats", "--sort", "oldest"]), /for --sort\./);
  });
});

describe("thread", () => {
  // @alice (42) started conversation 100 and replied to herself twice; 300 is
  // her reply to someone else.
  const root = post("100", { created_at: "2024-06-01T00:00:00.000Z" });
  const self = (id: string, day: number, to = "42") =>
    post(id, { conversation_id: "100", in_reply_to_user_id: to, created_at: `2024-06-0${day}T00:00:00.000Z` });

  const routes = {
    "GET /2/tweets": (url: URL) =>
      url.searchParams.get("ids") === "100" ? { data: [root] } : { data: [self("200", 2)] },
    "GET /2/tweets/search/recent": (url: URL) =>
      url.searchParams.get("next_token") === "page2"
        ? { data: [self("200", 2), root], meta: {} }
        : { data: [self("400", 4), self("300", 3, "77")], meta: { next_token: "page2" } },
  };

  it("orders posts by ID, since a fast thread shares created_at seconds", async () => {
    const sameSecond = (id: string) => self(id, 2);
    const { result } = await run(["thread", "100"], {
      "GET /2/tweets": { data: [root] },
      "GET /2/tweets/search/recent": { data: [sameSecond("1000"), sameSecond("999"), root] },
    });
    assert.deepEqual((result.data as { id: string }[]).map((p) => p.id), ["100", "999", "1000"]);
  });

  it("keeps the root and the author's replies to themselves, oldest first, across pages", async () => {
    const { result, requests } = await run(["thread", "200"], routes);
    assert.deepEqual((result.data as { id: string }[]).map((p) => p.id), ["100", "200", "400"]);
    assert.equal(requests.length, 4);
  });

  it("hints at --all when the thread began more than 7 days ago", async () => {
    const { result } = await run(["thread", "200"], routes);
    assert.match(result.hints?.[0] ?? "", /began on 2024-06-01.*--all/);
  });

  it("hints that the given post is not part of the thread when someone else wrote it", async () => {
    const reply = post("500", { author_id: "77", conversation_id: "100", in_reply_to_user_id: "42" });
    const { result } = await run(["thread", "500"], {
      "GET /2/tweets": (url: URL) =>
        url.searchParams.get("ids") === "100"
          ? { data: [root], includes: { users: [{ id: "42", username: "alice" }] } }
          : { data: [reply] },
      "GET /2/tweets/search/recent": { data: [root] },
    });
    assert.deepEqual((result.data as { id: string }[]).map((p) => p.id), ["100"]);
    assert.equal(result.hints?.at(-1), "Post 500 is not part of @alice's thread; `get 500` reads it.");
  });

  it("prints X's errors and no posts when the post does not exist", async () => {
    const errors = [{ message: "Could not find tweet with ids: [1]." }];
    const { result, requests } = await run(["thread", "1"], { "GET /2/tweets": { errors } });
    assert.deepEqual(result, { data: [], errors });
    assert.equal(requests.length, 1);
  });
});

describe("replies", () => {
  it("prints one page of replies with X's meta, its replied-to post a reference", async () => {
    const reply = post("2", { referenced_tweets: [{ type: "replied_to", id: "1" }], in_reply_to_user_id: "42" });
    const response = { data: [reply], includes: { tweets: [post("1")] }, meta: { next_token: "abc" } };
    const { result } = await run(["replies", "1"], { "GET /2/tweets/search/recent": response });

    const [hydrated] = result.data as { referenced_tweets: object[] }[];
    assert.deepEqual(hydrated.referenced_tweets, [{ type: "replied_to", id: "1" }]);
    assert.deepEqual(result.meta, { next_token: "abc" });
  });
});

describe("me", () => {
  it("folds the pinned post into the user", async () => {
    const { result } = await run(["me", "--pinned-tweet"], {
      "GET /2/users/me": { data: { id: "42", username: "alice", pinned_tweet_id: "9" } },
      "GET /2/tweets": { data: [post("9")], meta: { result_count: 1 } },
    });
    const user = result.data as { pinned_tweet_id?: string; pinned_tweet: { id: string } };
    assert.equal(user.pinned_tweet.id, "9");
    assert.equal(user.pinned_tweet_id, undefined);
    assert.equal(result.meta, undefined);
  });
});
