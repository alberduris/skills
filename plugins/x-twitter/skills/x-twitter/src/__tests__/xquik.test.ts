import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { xquikSearch } from "../commands/xquik-search.js";

const config = {
  apiKey: "test-api-key",
  baseUrl: "https://example.test",
};

describe("xquik-search", () => {
  it("maps search flags and returns tweets", async () => {
    let requestedUrl = "";
    let apiKeyHeader = "";
    let requestSignal: AbortSignal | null = null;
    const fetchImpl: typeof fetch = async (input, init) => {
      requestedUrl = String(input);
      apiKeyHeader = new Headers(init?.headers).get("x-api-key") ?? "";
      requestSignal = init?.signal ?? null;
      return new Response(
        JSON.stringify({ tweets: [{ id: "1", text: "result" }] }),
        { status: 200 },
      );
    };

    const result = await xquikSearch(
      config,
      [
        "AI agents",
        "--max-results",
        "12",
        "--sort",
        "top",
        "--start-time",
        "2026-07-01T00:00:00Z",
      ],
      fetchImpl,
    );

    const url = new URL(requestedUrl);
    assert.equal(url.pathname, "/api/v1/x/tweets/search");
    assert.equal(url.searchParams.get("q"), "AI agents");
    assert.equal(url.searchParams.get("limit"), "12");
    assert.equal(url.searchParams.get("queryType"), "Top");
    assert.equal(url.searchParams.get("sinceTime"), "2026-07-01T00:00:00Z");
    assert.equal(apiKeyHeader, "test-api-key");
    assert.ok(requestSignal instanceof AbortSignal);
    assert.deepEqual(result, [{ id: "1", text: "result" }]);
  });

  it("returns the full response with --raw", async () => {
    const payload = {
      tweets: [{ id: "1" }],
      has_next_page: true,
      next_cursor: "cursor",
    };
    const fetchImpl: typeof fetch = async () =>
      new Response(JSON.stringify(payload), { status: 200 });

    const result = await xquikSearch(config, ["agents", "--raw"], fetchImpl);

    assert.deepEqual(result, payload);
  });

  it("passes a pagination cursor", async () => {
    let requestedUrl = "";
    const fetchImpl: typeof fetch = async (input) => {
      requestedUrl = String(input);
      return new Response(JSON.stringify({ tweets: [] }), { status: 200 });
    };

    await xquikSearch(
      config,
      ["agents", "--next-token", "cursor-2"],
      fetchImpl,
    );

    assert.equal(new URL(requestedUrl).searchParams.get("cursor"), "cursor-2");
  });

  it("surfaces status without exposing API error details", async () => {
    const fetchImpl: typeof fetch = async () =>
      new Response(JSON.stringify({ error: "sensitive upstream detail" }), {
        status: 402,
      });

    await assert.rejects(
      xquikSearch(config, ["agents"], fetchImpl),
      (error: Error) => {
        assert.equal(error.message, "Xquik request failed (402)");
        return true;
      },
    );
  });

  it("rejects unsupported sort values before fetching", async () => {
    let called = false;
    const fetchImpl: typeof fetch = async () => {
      called = true;
      return new Response();
    };

    await assert.rejects(
      xquikSearch(config, ["agents", "--sort", "popular"], fetchImpl),
      /--sort must be either/,
    );
    assert.equal(called, false);
  });
});
