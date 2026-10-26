import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { NEWS_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

interface SearchNewsFlags {
  query: string;
  maxResults?: number;
  maxAgeHours?: number;
  fields?: string[];
}

export async function searchNews(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<SearchNewsFlags>(args, {
    positional: { key: "query", label: "A news search query" },
    flags: {
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

  return output(response, response.data ?? []);
}
