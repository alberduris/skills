import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { resolveMyId, resolveUserId } from "./resolve.ts";
import { fakeClient } from "../http/fake-client.ts";

describe("resolveMyId", () => {
  it("asks /2/users/me for the account's ID", async () => {
    const { client, requests } = fakeClient({ "GET /2/users/me": { data: { id: "123" } } });
    assert.equal(await resolveMyId(client), "123");
    assert.equal(requests[0].url, "https://api.x.com/2/users/me");
  });

  it("throws when the response has no ID", async () => {
    const { client } = fakeClient({ "GET /2/users/me": { data: {} } });
    await assert.rejects(() => resolveMyId(client), /Could not resolve authenticated user ID/);
  });
});

describe("resolveUserId", () => {
  it("returns numeric input as-is without a request", async () => {
    const { client, requests } = fakeClient();
    assert.equal(await resolveUserId(client, "12345"), "12345");
    assert.equal(requests.length, 0);
  });

  it("looks up a username, with or without @", async () => {
    const { client, requests } = fakeClient({
      "GET /2/users/by/username/testuser": { data: { id: "789" } },
    });
    assert.equal(await resolveUserId(client, "@testuser"), "789");
    assert.equal(await resolveUserId(client, "testuser"), "789");
    assert.equal(requests[0].url, "https://api.x.com/2/users/by/username/testuser");
  });

  it("throws when the user does not exist", async () => {
    const { client } = fakeClient({ "GET /2/users/by/username/nobody": { data: {} } });
    await assert.rejects(
      () => resolveUserId(client, "nobody"),
      /Could not resolve user "nobody" to an ID/,
    );
  });
});
