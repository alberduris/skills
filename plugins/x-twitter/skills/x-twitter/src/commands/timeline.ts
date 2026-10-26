import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, TEMPORAL, RAW, type FlagDef } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";
import { resolveMyId } from "../lib/resolve.ts";
import { resolveEnum } from "../lib/enums.ts";

const EXCLUDE: Record<string, FlagDef> = {
  "--exclude": { key: "exclude", type: "string[]" },
};

export async function timeline(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    startTime?: string;
    endTime?: string;
    exclude?: string[];
    raw: boolean;
  }>(args, { flags: { ...PAGINATION, ...TEMPORAL, ...EXCLUDE, ...RAW } });

  if (flags.exclude) {
    flags.exclude = flags.exclude.map((v) => resolveEnum("exclude", v));
  }

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/timelines/reverse_chronological`, {
    "tweet.fields": TWEET_FIELDS,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
    start_time: flags.startTime,
    end_time: flags.endTime,
    exclude: flags.exclude,
  });
  return flags.raw ? response : (response.data ?? []);
}
