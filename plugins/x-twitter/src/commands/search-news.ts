import type { Client } from "@xdevplatform/xdk";
import { parseArgs, RAW } from "../lib/args.js";
import { NEWS_FIELDS } from "../lib/fields.js";

interface SearchNewsFlags {
  query: string;
  maxResults?: number;
  maxAgeHours?: number;
  fields?: string[];
  raw: boolean;
}

export async function searchNews(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<SearchNewsFlags>(args, {
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
