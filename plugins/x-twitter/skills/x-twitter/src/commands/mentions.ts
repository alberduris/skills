import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, TEMPORAL } from "../lib/args.ts";
import { resolveMyId } from "../lib/resolve.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

export async function mentions(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    startTime?: string;
    endTime?: string;
  }>(args, { flags: { ...PAGINATION, ...TEMPORAL } });

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/mentions`, {
    ...POST_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
    start_time: flags.startTime,
    end_time: flags.endTime,
  });
  return output(response, hydrate(response));
}
