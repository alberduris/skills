import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ApiError, path } from "./client.ts";
import { CREDENTIALS, fakeClient } from "./fake-client.ts";
import { oauth1Header } from "./oauth1.ts";

/** Parses `OAuth k="v", ...` into decoded key/value pairs. */
function oauthFields(header: string): Record<string, string> {
  const fields: Record<string, string> = {};
  for (const [, key, value] of header.matchAll(/(\w+)="([^"]*)"/g)) {
    fields[key] = decodeURIComponent(value);
  }
  return fields;
}

/**
 * Re-signs a sent request the way X verifies it: from the query parameters it
 * actually received, with the nonce and timestamp the header carried.
 */
function expectedSignature(method: string, sentUrl: string, header: string): string {
  const url = new URL(sentUrl);
  const { oauth_nonce, oauth_timestamp } = oauthFields(header);
  const resigned = oauth1Header(
    method,
    url.origin + url.pathname,
    Object.fromEntries(url.searchParams),
    CREDENTIALS,
    oauth_nonce,
    oauth_timestamp,
  );
  return oauthFields(resigned).oauth_signature;
}

describe("client", () => {
  it("sends X's parameter names verbatim, dropping unset ones and joining lists", async () => {
    const { client, requests } = fakeClient();

    await client.get("/2/tweets/search/recent", {
      query: 'from:alice "hello world"',
      "tweet.fields": ["created_at", "public_metrics"],
      max_results: 10,
      next_token: undefined,
    });

    assert.equal(
      requests[0].url,
      "https://api.x.com/2/tweets/search/recent" +
        "?query=from%3Aalice%20%22hello%20world%22" +
        "&tweet.fields=created_at%2Cpublic_metrics&max_results=10",
    );
  });

  it("signs user-context requests over exactly the query it sends", async () => {
    const { client, requests, headers } = fakeClient();

    await client.get("/2/tweets/search/recent", { query: 'a:b "c d" +e!', max_results: 10 });

    const header = headers[0].Authorization;
    assert.match(header, /^OAuth /);
    const fields = oauthFields(header);
    assert.equal(fields.oauth_consumer_key, CREDENTIALS.apiKey);
    assert.equal(fields.oauth_token, CREDENTIALS.accessToken);
    assert.equal(fields.oauth_signature, expectedSignature("GET", requests[0].url, header));
  });

  it("sends JSON bodies unsigned, as RFC 5849 requires", async () => {
    const { client, requests, headers } = fakeClient();

    await client.post("/2/users/1/likes", { tweet_id: "20" });

    assert.deepEqual(requests[0], {
      method: "POST",
      url: "https://api.x.com/2/users/1/likes",
      auth: "user",
      body: { tweet_id: "20" },
    });
    assert.equal(headers[0]["Content-Type"], "application/json");
    const header = headers[0].Authorization;
    assert.equal(oauthFields(header).oauth_signature, expectedSignature("POST", requests[0].url, header));
  });

  it("sends the bearer, and only the bearer, for app-only requests", async () => {
    const { client, headers } = fakeClient();

    await client.get("/2/usage/tweets", {}, "app-only");

    assert.equal(headers[0].Authorization, `Bearer ${CREDENTIALS.bearerToken}`);
  });

  it("fails before sending when an app-only request has no bearer", async () => {
    const { client, requests } = fakeClient({}, { ...CREDENTIALS, bearerToken: undefined });

    await assert.rejects(
      () => client.get("/2/tweets/counts/recent", { query: "cats" }, "app-only"),
      /GET \/2\/tweets\/counts\/recent .*X_API_BEARER_TOKEN.*Keys and tokens > Bearer Token/,
    );
    assert.equal(requests.length, 0);
  });

  it("throws ApiError carrying the status and X's parsed error body", async () => {
    const body = { title: "Unauthorized", detail: "Unauthorized", status: 401 };
    const { client } = fakeClient({
      "GET /2/users/me": Response.json(body, { status: 401, statusText: "Unauthorized" }),
    });

    const error = await client.get("/2/users/me").catch((e: unknown) => e);
    assert.ok(error instanceof ApiError);
    assert.equal(error.status, 401);
    assert.deepEqual(error.data, body);
    assert.equal(error.message, "HTTP 401 Unauthorized from GET /2/users/me");
  });

  it("keeps a non-JSON error body as text", async () => {
    const { client } = fakeClient({
      "GET /2/users/me": new Response("upstream timeout", { status: 503 }),
    });

    const error = await client.get("/2/users/me").catch((e: unknown) => e);
    assert.ok(error instanceof ApiError);
    assert.equal(error.data, "upstream timeout");
  });
});

describe("path", () => {
  it("keeps each interpolated value inside its own segment", () => {
    const built = path`/2/tweets/${"1/../../users/me"}`;
    assert.equal(built, "/2/tweets/1%2F..%2F..%2Fusers%2Fme");
    assert.equal(new URL(`https://api.x.com${built}`).pathname, built);
  });
});
