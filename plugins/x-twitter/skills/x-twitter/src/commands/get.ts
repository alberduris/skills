import { path, type Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";

function articleHint(tweet: Record<string, unknown>): string | undefined {
  const article = tweet.article as Record<string, unknown> | undefined;
  if (!article) return undefined;
  if (article.plain_text) return undefined;
  return "Hint: this tweet is an article (long-form post). The full content is in `article.plain_text` but it was not returned because `article` is missing from --fields. Re-fetch with default fields or add `article` to --fields.";
}

export async function get(
  client: Client,
  args: string[],
): Promise<unknown> {
  // The positional arg is comma-separated IDs; we parse it as a string then split
  const flags = parseArgs<{ idsRaw: string; tweetFields: string[]; raw: boolean }>(
    args,
    {
      positional: { key: "idsRaw", label: "At least one post ID" },
      flags: {
        ...RAW,
        "--fields": { key: "tweetFields", type: "string[]" },
      },
      defaults: { tweetFields: TWEET_FIELDS },
    },
  );

  const ids = flags.idsRaw.split(",").map((id) => id.trim());

  const query = {
    "tweet.fields": flags.tweetFields,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
  };

  if (ids.length === 1) {
    const response = await client.get(path`/2/tweets/${ids[0]}`, query);
    const data = flags.raw ? response : response.data;
    const hint = !flags.raw && data ? articleHint(data as Record<string, unknown>) : undefined;
    if (hint) return { hint, data };
    return data;
  }

  const response = await client.get("/2/tweets", { ids, ...query });
  return flags.raw ? response : (response.data ?? []);
}
