import { parseArgs, RAW } from "../lib/args.js";
import { NEWS_FIELDS } from "../lib/fields.js";
export async function news(client, args) {
    const flags = parseArgs(args, {
        positional: { key: "id", label: "A news story ID" },
        flags: {
            ...RAW,
            "--fields": { key: "fields", type: "string[]" },
        },
    });
    const newsFields = flags.fields ?? NEWS_FIELDS;
    const response = await client.news.get(flags.id, { newsFields });
    return flags.raw ? response : response.data;
}
