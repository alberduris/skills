import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

export async function reposters(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{
    tweetId: string;
    maxResults?: number;
    nextToken?: string;
  }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
    flags: { ...PAGINATION },
  });

  const response = await client.get(path`/2/tweets/${flags.tweetId}/retweeted_by`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}
