import type { Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";
import { NEWS_FIELDS } from "../lib/fields.ts";

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

  const response = await client.get("/2/news/search", {
    query: flags.query,
    "news.fields": flags.fields ?? NEWS_FIELDS,
    max_results: flags.maxResults,
    max_age_hours: flags.maxAgeHours,
  });

  return flags.raw ? response : (response.data ?? []);
}
