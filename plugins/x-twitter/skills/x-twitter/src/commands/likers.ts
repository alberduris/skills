import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";

export async function likers(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<{
    tweetId: string;
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
    flags: { ...PAGINATION, ...RAW },
  });

  const response = await client.get(path`/2/tweets/${flags.tweetId}/liking_users`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
