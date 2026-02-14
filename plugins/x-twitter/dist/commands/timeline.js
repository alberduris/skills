import { parseArgs, PAGINATION, TEMPORAL, RAW } from "../lib/args.js";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.js";
import { resolveMyId } from "../lib/resolve.js";
export async function timeline(client, args) {
    const EXCLUDE = {
        "--exclude": { key: "exclude", type: "string[]" },
    };
    const flags = parseArgs(args, { flags: { ...PAGINATION, ...TEMPORAL, ...EXCLUDE, ...RAW } });
    const myId = await resolveMyId(client);
    const options = {
        tweetFields: TWEET_FIELDS,
        expansions: TWEET_EXPANSIONS,
        userFields: TWEET_USER_FIELDS,
        ...(flags.maxResults !== undefined && { maxResults: flags.maxResults }),
        ...(flags.nextToken !== undefined && { paginationToken: flags.nextToken }),
        ...(flags.startTime !== undefined && { startTime: flags.startTime }),
        ...(flags.endTime !== undefined && { endTime: flags.endTime }),
        ...(flags.exclude !== undefined && { exclude: flags.exclude }),
    };
    const response = await client.users.getTimeline(myId, options);
    return flags.raw ? response : (response.data ?? []);
}
