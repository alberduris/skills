import type { Client } from "@xdevplatform/xdk";
import { parseArgs, RAW } from "../lib/args.js";
import { NEWS_FIELDS } from "../lib/fields.js";

interface NewsFlags {
  id: string;
  fields?: string[];
  raw: boolean;
}

export async function news(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<NewsFlags>(args, {
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
