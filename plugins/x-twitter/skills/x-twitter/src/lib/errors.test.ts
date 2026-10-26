import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { formatError } from "./errors.ts";
import { ApiError } from "../http/client.ts";

describe("formatError", () => {
  it("strips query strings so searches never reach stderr", () => {
    const error = new Error(
      "Authentication required for /2/tweets/search/all?query=confidential&max_results=10.",
    );
    const [line] = formatError(error);
    assert.ok(!line.includes("confidential"), line);
    assert.ok(line.includes("/2/tweets/search/all?<redacted>"), line);
  });

  it("prefers the API's title and detail", () => {
    const apiError = new ApiError(
      402,
      { title: "Payment Required", detail: "credits depleted" },
      "HTTP 402 Payment Required from GET /2/users/me",
    );
    assert.deepEqual(formatError(apiError), [
      "Error: Payment Required – credits depleted",
    ]);
  });

  it("lists nested API errors under the headline", () => {
    const apiError = new ApiError(
      400,
      { title: "Invalid Request", errors: [{ message: "bad field" }] },
      "HTTP 400 Bad Request from GET /2/tweets",
    );
    assert.deepEqual(formatError(apiError), [
      "Error: Invalid Request",
      "  - bad field",
    ]);
  });

  it("falls back to the request line when the body is not JSON", () => {
    const apiError = new ApiError(503, "upstream timeout", "HTTP 503 Service Unavailable from GET /2/users/me");
    assert.deepEqual(formatError(apiError), [
      "Error: HTTP 503 Service Unavailable from GET /2/users/me",
    ]);
  });

  it("handles non-Error throws", () => {
    assert.deepEqual(formatError("boom"), ["Error: boom"]);
  });
});
