import { parseArgs, PAGINATION, TEMPORAL, RAW } from "../lib/args.js";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.js";
import { resolveEnum } from "../lib/enums.js";
export async function search(client, args) {
    const flags = parseArgs(args, {
        positional: { key: "query", label: "A search query" },
        flags: {
            ...PAGINATION,
            ...TEMPORAL,
            ...RAW,
            "--all": { key: "all", type: "boolean" },
            "--sort": { key: "sortOrder", type: "string" },
            "--since-id": { key: "sinceId", type: "string" },
            "--until-id": { key: "untilId", type: "string" },
            "--fields": { key: "tweetFields", type: "string[]" },
        },
        defaults: { tweetFields: TWEET_FIELDS },
    });
    const MIN_RESULTS = 10;
    const hints = [];
    if (flags.maxResults !== undefined && flags.maxResults < MIN_RESULTS) {
        hints.push(`Hint: maxResults was raised to ${MIN_RESULTS} (Twitter API minimum). You requested ${flags.maxResults}.`);
        flags.maxResults = MIN_RESULTS;
    }
    // Nudge: conversation_id: in search query → suggest thread command
    if (/conversation_id:\d+/.test(flags.query)) {
        const match = flags.query.match(/conversation_id:(\d+)/);
        hints.push(`Hint: to read a full thread, use the \`thread\` command instead: \`thread ${match?.[1] ?? "<tweet_id>"}\`. It auto-resolves the conversation, paginates, and sorts chronologically.`);
    }
    if (flags.sortOrder !== undefined) {
        flags.sortOrder = resolveEnum("sortOrder", flags.sortOrder);
    }
    const options = {
        tweetFields: flags.tweetFields,
        expansions: TWEET_EXPANSIONS,
        userFields: TWEET_USER_FIELDS,
        ...(flags.maxResults !== undefined && { maxResults: flags.maxResults }),
        ...(flags.sortOrder !== undefined && { sortOrder: flags.sortOrder }),
        ...(flags.startTime !== undefined && { startTime: flags.startTime }),
        ...(flags.endTime !== undefined && { endTime: flags.endTime }),
        ...(flags.sinceId !== undefined && { sinceId: flags.sinceId }),
        ...(flags.untilId !== undefined && { untilId: flags.untilId }),
        ...(flags.nextToken !== undefined && { nextToken: flags.nextToken }),
    };
    const response = flags.all
        ? await client.posts.searchAll(flags.query, options)
        : await client.posts.searchRecent(flags.query, options);
    const data = flags.raw ? response : (response.data ?? []);
    // Nudge: empty results on recent search → 7-day limitation
    if (!flags.all && Array.isArray(data) && data.length === 0) {
        hints.push("Hint: recent search only covers the last 7 days. Use --all (requires X_API_BEARER_TOKEN) to search the full archive.");
    }
    if (hints.length)
        return { hint: hints.join(" "), data };
    return data;
}
