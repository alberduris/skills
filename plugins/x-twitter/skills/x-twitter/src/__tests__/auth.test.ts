import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { authModeFor, assertCredentials } from "../lib/auth.js";
import { formatError } from "../lib/errors.js";
import type { Config } from "../config.js";

const CONFIG: Config = {
  apiKey: "k",
  apiSecret: "s",
  accessToken: "t",
  accessTokenSecret: "ts",
  bearerToken: "bearer",
};

const NO_BEARER: Config = { ...CONFIG, bearerToken: undefined };

describe("authModeFor", () => {
  it("routes bearer-only endpoints to app-only", () => {
    for (const command of ["count", "trending", "usage"]) {
      assert.equal(authModeFor(command, []), "app-only", command);
    }
  });

  it("keeps user context for everything else, so user-context fields survive", () => {
    for (const command of ["user", "me", "search", "thread", "timeline", "post"]) {
      assert.equal(authModeFor(command, []), "user", command);
    }
  });

  it("switches search and thread to app-only only under --all", () => {
    assert.equal(authModeFor("search", []), "user");
    assert.equal(authModeFor("search", ["query", "--all"]), "app-only");
    assert.equal(authModeFor("thread", ["123"]), "user");
    assert.equal(authModeFor("thread", ["123", "--all"]), "app-only");
  });

  it("leaves search-news on user context (xdk 0.6.6 accepts OAuth 1.0a)", () => {
    assert.equal(authModeFor("search-news", []), "user");
  });

  it("keeps personalized trending on user context, the only scheme its endpoint accepts", () => {
    assert.equal(authModeFor("trending", []), "app-only");
    assert.equal(authModeFor("trending", ["--personalized"]), "user");
    const mode = authModeFor("trending", ["--personalized"]);
    assert.doesNotThrow(() => assertCredentials("trending", mode, NO_BEARER));
  });
});

describe("assertCredentials", () => {
  it("rejects bookmark writes, which need OAuth 2.0 user context", () => {
    for (const command of ["bookmark", "unbookmark"]) {
      assert.throws(
        () => assertCredentials(command, "user", CONFIG),
        /OAuth 2\.0 user context/,
        command,
      );
    }
  });

  it("lets bookmark reads through: the API accepts OAuth 1.0a for them", () => {
    assert.doesNotThrow(() => assertCredentials("bookmarks", "user", CONFIG));
  });

  it("names the missing bearer instead of failing inside the SDK", () => {
    assert.throws(
      () => assertCredentials("count", "app-only", NO_BEARER),
      /X_API_BEARER_TOKEN/,
    );
  });

  it("passes when the required credential is present", () => {
    assert.doesNotThrow(() => assertCredentials("count", "app-only", CONFIG));
    assert.doesNotThrow(() => assertCredentials("user", "user", NO_BEARER));
  });
});

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
    const apiError = Object.assign(new Error("HTTP 402"), {
      status: 402,
      data: { title: "Payment Required", detail: "credits depleted" },
    });
    assert.deepEqual(formatError(apiError), [
      "Error: Payment Required – credits depleted",
    ]);
  });

  it("lists nested API errors under the headline", () => {
    const apiError = Object.assign(new Error("HTTP 400"), {
      status: 400,
      data: { title: "Invalid Request", errors: [{ message: "bad field" }] },
    });
    assert.deepEqual(formatError(apiError), [
      "Error: Invalid Request",
      "  - bad field",
    ]);
  });

  it("handles non-Error throws", () => {
    assert.deepEqual(formatError("boom"), ["Error: boom"]);
  });
});
