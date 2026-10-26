import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";

export async function quotes(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<{
    tweetId: string;
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
    flags: { ...PAGINATION, ...RAW },
  });

  const response = await client.get(path`/2/tweets/${flags.tweetId}/quote_tweets`, {
    "tweet.fields": TWEET_FIELDS,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
