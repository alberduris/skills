import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";

export async function searchUsers(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{
    query: string;
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, {
    positional: { key: "query", label: "A search query" },
    flags: { ...PAGINATION, ...RAW },
  });

  const response = await client.get("/2/users/search", {
    query: flags.query,
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    next_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
