import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";

export async function repostsOfMe(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, { flags: { ...PAGINATION, ...RAW } });

  const response = await client.get("/2/users/reposts_of_me", {
    "tweet.fields": TWEET_FIELDS,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
