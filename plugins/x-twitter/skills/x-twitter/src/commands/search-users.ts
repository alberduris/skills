import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

export async function searchUsers(
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

  const response = await client.get("/2/users/search", {
    query: flags.query,
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    next_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}
