import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";

export async function reposters(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{
    tweetId: string;
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
    flags: { ...PAGINATION, ...RAW },
  });

  const response = await client.get(path`/2/tweets/${flags.tweetId}/retweeted_by`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
