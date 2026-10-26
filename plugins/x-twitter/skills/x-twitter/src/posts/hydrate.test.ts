import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { hydrate } from "./hydrate.ts";

/**
 * Fixtures are real responses from GET /2/tweets?ids=... with POST_FIELDS,
 * recorded on 2026-10-26.
 */
function fixture(name: string) {
  return JSON.parse(readFileSync(resolve(import.meta.dirname, "fixtures", `${name}.json`), "utf8"));
}

describe("hydrate", () => {
  it("shows a long post with its video and the article it quotes, all inline", () => {
    const response = fixture("long-post-video-quoted-article");
    const [raw] = response.data;
    const [quoted] = response.includes.tweets;
    const [ernesto] = response.includes.users;

    assert.deepEqual(hydrate(response), [
      {
        id: "2114523620026282002",
        author: { id: "1890388644273258496", name: "Ernesto Lopez", username: "ErnestoSOFTWARE" },
        created_at: raw.created_at,
        text: raw.note_tweet.text,
        media: response.includes.media,
        referenced_tweets: [
          {
            type: "quoted",
            id: "2112940887806296269",
            author: ernesto,
            created_at: quoted.created_at,
            text: "https://x.com/i/article/2112939307782508544",
            conversation_id: quoted.conversation_id,
            article: quoted.article,
            edit_history_tweet_ids: quoted.edit_history_tweet_ids,
            paid_partnership: true,
            public_metrics: quoted.public_metrics,
          },
        ],
        conversation_id: raw.conversation_id,
        edit_history_tweet_ids: raw.edit_history_tweet_ids,
        paid_partnership: false,
        public_metrics: raw.public_metrics,
      },
    ]);
    assert.match(raw.note_tweet.text, /99% are not performing, < 1000 views/);
    assert.equal(quoted.article.title, "How we automated a slideshow farm 10M+ views/mo ran by AI agents ");
  });

  it("without note_tweet, decodes text and drops the media link and the trailing link to the quoted post", () => {
    const response = fixture("long-post-video-quoted-article");
    delete response.data[0].note_tweet;

    const [post] = hydrate(response);
    assert.match(post.text, /99% are not performing, < 1000 views/);
    assert.match(post.text, /The new moat is being a good$/);
  });

  it("expands t.co links using the entities of note_tweet when its text is the one shown", () => {
    const [post] = hydrate(fixture("long-post-with-links"));
    assert.match(post.text, /lunar landings https:\/\/go\.nasa\.gov\/4jzartX and/);
    assert.match(post.text, /on the lunar surface https:\/\/go\.nasa\.gov\/4zV3TLc\.$/);
    assert.doesNotMatch(post.text, /t\.co/);
    assert.deepEqual(post.media?.map((m) => (m as { type: string }).type), ["video"]);
  });

  it("embeds a retweeted post with its author and media", () => {
    const response = fixture("retweet");
    const [post] = hydrate(response);
    const [retweeted] = post.referenced_tweets as { type: string; author: object; media: object[]; text: string }[];

    assert.match(post.text, /^RT @NASASpox: .*Texas A&M/s);
    assert.equal(retweeted.type, "retweeted");
    assert.deepEqual(retweeted.author, { id: "1907894348319973378", name: "NASA Spox", username: "NASASpox" });
    assert.deepEqual(retweeted.media, response.includes.media);
    assert.doesNotMatch(retweeted.text, /t\.co/);
  });

  it("keeps a replied-to post as a reference and names who it replies to", () => {
    const [post] = hydrate(fixture("reply-with-link"));

    assert.deepEqual(post.referenced_tweets, [{ type: "replied_to", id: "2112963120083931597" }]);
    assert.deepEqual(post.in_reply_to_user, { id: "1632237073565642754", name: "ThisMightWork", username: "ThisMightWrk" });
    assert.equal(
      post.text,
      "@ThisMightWrk It did well! We just released an update last week: " +
        "https://www.nasa.gov/missions/artemis/artemis-2/rigorous-analysis-confirms-nasas-artemis-ii-heat-shield-performance/",
    );
    assert.equal(post.entities, undefined);
  });

  it("leaves references X did not include as they are", () => {
    const [post] = hydrate({
      data: [
        {
          id: "2",
          text: "look",
          author_id: "9",
          attachments: { media_keys: ["3_1"] },
          referenced_tweets: [{ type: "quoted", id: "1" }],
        },
      ],
      errors: [{ message: "Could not find tweet with referenced_tweets.id: [1]." }],
    });

    assert.deepEqual(post.author, { id: "9" });
    assert.deepEqual(post.media, [{ media_key: "3_1" }]);
    assert.deepEqual(post.referenced_tweets, [{ type: "quoted", id: "1" }]);
  });

  it("returns [] when X sends no data", () => {
    assert.deepEqual(hydrate({ meta: { result_count: 0 } }), []);
  });
});
