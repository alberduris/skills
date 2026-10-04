import { parseArgs, RAW } from "../lib/args.js";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.js";
function articleHint(tweet) {
    const article = tweet.article;
    if (!article)
        return undefined;
    if (article.plainText)
        return undefined;
    return "Hint: this tweet is an article (long-form post). The full content is in `article.plainText` but it was not returned because `article` is missing from --fields. Re-fetch with default fields or add `article` to --fields.";
}
export async function get(client, args) {
    // The positional arg is comma-separated IDs; we parse it as a string then split
    const flags = parseArgs(args, {
        positional: { key: "idsRaw", label: "At least one post ID" },
        flags: {
            ...RAW,
            "--fields": { key: "tweetFields", type: "string[]" },
        },
        defaults: { tweetFields: TWEET_FIELDS },
    });
    const ids = flags.idsRaw.split(",").map((id) => id.trim());
    const options = {
        tweetFields: flags.tweetFields,
        expansions: TWEET_EXPANSIONS,
        userFields: TWEET_USER_FIELDS,
    };
    if (ids.length === 1) {
        const response = await client.posts.getById(ids[0], options);
        const data = flags.raw ? response : response.data;
        const hint = !flags.raw && data ? articleHint(data) : undefined;
        if (hint)
            return { hint, data };
        return data;
    }
    const response = await client.posts.getByIds(ids, options);
    const data = flags.raw ? response : (response.data ?? []);
    return data;
}
