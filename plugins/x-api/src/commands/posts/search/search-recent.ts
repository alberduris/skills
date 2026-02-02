import type { Client } from "@xdevplatform/xdk";
import { parseSearchFlags } from "./parse-flags.js";

const DEFAULT_EXPANSIONS = ["author_id"];
const DEFAULT_USER_FIELDS = ["name", "username"];

export async function searchRecent(
  client: Client,
  args: string[],
): Promise<void> {
  const flags = parseSearchFlags(args);

  const response = await client.posts.searchRecent(flags.query, {
    tweetFields: flags.tweetFields,
    expansions: DEFAULT_EXPANSIONS,
    userFields: DEFAULT_USER_FIELDS,
    ...(flags.maxResults && { maxResults: flags.maxResults }),
    ...(flags.sortOrder && { sortOrder: flags.sortOrder }),
    ...(flags.startTime && { startTime: flags.startTime }),
    ...(flags.endTime && { endTime: flags.endTime }),
    ...(flags.sinceId && { sinceId: flags.sinceId }),
    ...(flags.untilId && { untilId: flags.untilId }),
    ...(flags.nextToken && { nextToken: flags.nextToken }),
  });

  if (flags.raw) {
    console.log(JSON.stringify(response, null, 2));
  } else {
    console.log(JSON.stringify(response.data ?? [], null, 2));
  }
}
