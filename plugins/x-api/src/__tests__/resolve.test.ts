import { describe, it, beforeEach, mock } from "node:test";
import assert from "node:assert/strict";
import {
  resolveMyId,
  resolveUserId,
  _resetMyIdCache,
} from "../lib/resolve.js";
import { mockClient } from "./helpers/mock-client.js";

describe("resolveMyId", () => {
  beforeEach(() => {
    _resetMyIdCache();
  });

  it("calls getMe and returns the id", async () => {
    const getMe = mock.fn(async () => ({ data: { id: "123" } }));
    const client = mockClient({ users: { getMe } });

    const id = await resolveMyId(client);
    assert.equal(id, "123");
    assert.equal(getMe.mock.callCount(), 1);
  });

  it("caches the id on subsequent calls", async () => {
    const getMe = mock.fn(async () => ({ data: { id: "123" } }));
    const client = mockClient({ users: { getMe } });

    await resolveMyId(client);
    await resolveMyId(client);
    assert.equal(getMe.mock.callCount(), 1);
  });

  it("throws when response.data.id is missing", async () => {
    const getMe = mock.fn(async () => ({ data: {} }));
    const client = mockClient({ users: { getMe } });

    await assert.rejects(
      () => resolveMyId(client),
      /Could not resolve authenticated user ID/,
    );
  });

  it("_resetMyIdCache clears the cache", async () => {
    const getMe = mock.fn(async () => ({ data: { id: "456" } }));
    const client = mockClient({ users: { getMe } });

    await resolveMyId(client);
    _resetMyIdCache();
    await resolveMyId(client);
    assert.equal(getMe.mock.callCount(), 2);
  });
});

describe("resolveUserId", () => {
  it("returns numeric input as-is without API call", async () => {
    const getByUsername = mock.fn();
    const client = mockClient({ users: { getByUsername } });

    const id = await resolveUserId(client, "12345");
    assert.equal(id, "12345");
    assert.equal(getByUsername.mock.callCount(), 0);
  });

  it("strips @ and calls getByUsername", async () => {
    const getByUsername = mock.fn(async () => ({
      data: { id: "789" },
    }));
    const client = mockClient({ users: { getByUsername } });

    const id = await resolveUserId(client, "@testuser");
    assert.equal(id, "789");
    assert.equal(getByUsername.mock.callCount(), 1);
    assert.equal(getByUsername.mock.calls[0].arguments[0], "testuser");
  });

  it("calls getByUsername for bare username", async () => {
    const getByUsername = mock.fn(async () => ({
      data: { id: "789" },
    }));
    const client = mockClient({ users: { getByUsername } });

    const id = await resolveUserId(client, "testuser");
    assert.equal(id, "789");
    assert.equal(getByUsername.mock.calls[0].arguments[0], "testuser");
  });

  it("throws when user not found", async () => {
    const getByUsername = mock.fn(async () => ({ data: {} }));
    const client = mockClient({ users: { getByUsername } });

    await assert.rejects(
      () => resolveUserId(client, "nobody"),
      /Could not resolve user "nobody" to an ID/,
    );
  });
});
