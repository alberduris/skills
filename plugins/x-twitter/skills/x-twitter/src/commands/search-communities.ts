import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { COMMUNITY_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

export async function searchCommunities(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{
    query: string;
    maxResults?: number;
    nextToken?: string;
  }>(args, {
    positional: { key: "query", label: "A search query" },
    flags: { ...PAGINATION },
  });

  const response = await client.get("/2/communities/search", {
    query: flags.query,
    "community.fields": COMMUNITY_FIELDS,
    max_results: flags.maxResults,
    next_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}
