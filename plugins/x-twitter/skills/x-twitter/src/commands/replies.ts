import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import type { Output } from "./output.ts";
import { searchPosts } from "./search.ts";

/**
 * The direct replies to a post, one page at a time: replies to a popular post
 * run into thousands, and every one is a billed read.
 */
export async function replies(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<{ id: string; all: boolean; maxResults?: number; nextToken?: string }>(args, {
    positional: { key: "id", label: "A post ID" },
    flags: { ...PAGINATION, "--all": { key: "all", type: "boolean" } },
  });

  return searchPosts(client, {
    query: `in_reply_to_tweet_id:${flags.id}`,
    all: flags.all,
    maxResults: flags.maxResults,
    nextToken: flags.nextToken,
  });
}
