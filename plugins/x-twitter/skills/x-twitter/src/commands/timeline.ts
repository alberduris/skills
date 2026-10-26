import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, TEMPORAL, type FlagDef } from "../lib/args.ts";
import { resolveMyId } from "../lib/resolve.ts";
import { resolveEnum } from "../lib/enums.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

const EXCLUDE: Record<string, FlagDef> = {
  "--exclude": { key: "exclude", type: "string[]" },
};

export async function timeline(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    startTime?: string;
    endTime?: string;
    exclude?: string[];
  }>(args, { flags: { ...PAGINATION, ...TEMPORAL, ...EXCLUDE } });

  if (flags.exclude) {
    flags.exclude = flags.exclude.map((v) => resolveEnum("exclude", v));
  }

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/timelines/reverse_chronological`, {
    ...POST_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
    start_time: flags.startTime,
    end_time: flags.endTime,
    exclude: flags.exclude,
  });
  return output(response, hydrate(response));
}
