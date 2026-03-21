import { parseArgs, RAW } from "../lib/args.js";
import { NEWS_FIELDS } from "../lib/fields.js";
export async function searchNews(client, args) {
    const flags = parseArgs(args, {
        positional: { key: "query", label: "A news search query" },
        flags: {
            ...RAW,
            "--max-results": { key: "maxResults", type: "number" },
            "--max-age-hours": { key: "maxAgeHours", type: "number" },
            "--fields": { key: "fields", type: "string[]" },
        },
    });
    const newsFields = flags.fields ?? NEWS_FIELDS;
    const response = await client.news.search(flags.query, {
        newsFields,
        ...(flags.maxResults !== undefined && { maxResults: flags.maxResults }),
        ...(flags.maxAgeHours !== undefined && { maxAgeHours: flags.maxAgeHours }),
    });
    return flags.raw ? response : (response.data ?? []);
}
