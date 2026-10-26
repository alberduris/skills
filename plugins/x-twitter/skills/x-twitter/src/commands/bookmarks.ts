import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { resolveMyId } from "../lib/resolve.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

export async function bookmarks(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
  }>(args, { flags: { ...PAGINATION } });

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/bookmarks`, {
    ...POST_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, hydrate(response));
}
