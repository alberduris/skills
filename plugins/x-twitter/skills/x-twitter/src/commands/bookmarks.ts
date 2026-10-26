import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";
import { resolveMyId } from "../lib/resolve.ts";

export async function bookmarks(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, { flags: { ...PAGINATION, ...RAW } });

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/bookmarks`, {
    "tweet.fields": TWEET_FIELDS,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
