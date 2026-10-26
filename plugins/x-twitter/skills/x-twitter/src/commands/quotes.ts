import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

export async function quotes(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<{
    tweetId: string;
    maxResults?: number;
    nextToken?: string;
  }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
    flags: { ...PAGINATION },
  });

  const response = await client.get(path`/2/tweets/${flags.tweetId}/quote_tweets`, {
    ...POST_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, hydrate(response));
}
