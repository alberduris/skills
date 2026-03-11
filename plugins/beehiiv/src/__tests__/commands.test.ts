import { describe, it, mock } from "node:test";
import assert from "node:assert/strict";
import { mockClient } from "./helpers/mock-client.js";
import { publications } from "../commands/publications.js";
import { publication } from "../commands/publication.js";
import { posts } from "../commands/posts.js";
import { get } from "../commands/get.js";
import { templates } from "../commands/templates.js";

const PUB_ID = "pub_test-123";

describe("publications", () => {
  it("calls GET /publications and returns data", async () => {
    const pubs = [{ id: "pub_1", name: "My Newsletter" }];
    const getFn = mock.fn(async () => ({ data: pubs }));
    const client = mockClient({ get: getFn });

    const result = await publications(client, [], undefined);
    assert.deepEqual(result, pubs);
    assert.equal(getFn.mock.callCount(), 1);
    assert.equal(getFn.mock.calls[0].arguments[0], "/publications");
  });

  it("passes limit and page params", async () => {
    const getFn = mock.fn(async () => ({ data: [] }));
    const client = mockClient({ get: getFn });

    await publications(client, ["--limit", "5", "--page", "2"], undefined);
    const params = getFn.mock.calls[0].arguments[1];
    assert.equal(params.limit, "5");
    assert.equal(params.page, "2");
  });

  it("returns full envelope with --raw", async () => {
    const envelope = { data: [], page: 1, limit: 10, total_results: 0 };
    const getFn = mock.fn(async () => envelope);
    const client = mockClient({ get: getFn });

    const result = await publications(client, ["--raw"], undefined);
    assert.deepEqual(result, envelope);
  });
});

describe("publication", () => {
  it("calls GET /publications/{pubId} with stats expanded", async () => {
    const pub = { id: PUB_ID, name: "Test" };
    const getFn = mock.fn(async () => ({ data: pub }));
    const client = mockClient({ get: getFn });

    const result = await publication(client, [], PUB_ID);
    assert.deepEqual(result, pub);
    assert.equal(getFn.mock.calls[0].arguments[0], `/publications/${PUB_ID}`);
    assert.deepEqual(getFn.mock.calls[0].arguments[1]?.expand, ["stats"]);
  });
});

describe("posts", () => {
  it("calls GET /publications/{pubId}/posts and returns data", async () => {
    const postsList = [{ id: "post_1", title: "Hello" }];
    const getFn = mock.fn(async () => ({ data: postsList }));
    const client = mockClient({ get: getFn });

    const result = await posts(client, [], PUB_ID);
    assert.deepEqual(result, postsList);
    assert.equal(
      getFn.mock.calls[0].arguments[0],
      `/publications/${PUB_ID}/posts`,
    );
  });

  it("passes filter params", async () => {
    const getFn = mock.fn(async () => ({ data: [] }));
    const client = mockClient({ get: getFn });

    await posts(
      client,
      ["--status", "draft", "--content-tags", "ai,tech", "--limit", "50"],
      PUB_ID,
    );
    const params = getFn.mock.calls[0].arguments[1];
    assert.equal(params.status, "draft");
    assert.deepEqual(params.content_tags, ["ai", "tech"]);
    assert.equal(params.limit, "50");
  });
});

describe("get", () => {
  it("calls GET /publications/{pubId}/posts/{postId} with content expanded", async () => {
    const post = { id: "post_1", title: "Test", content: { free: { web: "<p>hi</p>" } } };
    const getFn = mock.fn(async () => ({ data: post }));
    const client = mockClient({ get: getFn });

    const result = await get(client, ["post_1"], PUB_ID);
    assert.deepEqual(result, post);
    assert.equal(
      getFn.mock.calls[0].arguments[0],
      `/publications/${PUB_ID}/posts/post_1`,
    );
    assert.deepEqual(getFn.mock.calls[0].arguments[1]?.expand, [
      "free_web_content",
    ]);
  });

  it("throws when post ID is missing", async () => {
    const client = mockClient();
    await assert.rejects(() => get(client, [], PUB_ID), /A post ID is required/);
  });
});

describe("templates", () => {
  it("calls GET /publications/{pubId}/post_templates", async () => {
    const tpls = [{ id: "tpl_1", name: "Default" }];
    const getFn = mock.fn(async () => ({ data: tpls }));
    const client = mockClient({ get: getFn });

    const result = await templates(client, [], PUB_ID);
    assert.deepEqual(result, tpls);
    assert.equal(
      getFn.mock.calls[0].arguments[0],
      `/publications/${PUB_ID}/post_templates`,
    );
  });
});
