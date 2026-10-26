import { path, type Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";
import { NEWS_FIELDS } from "../lib/fields.ts";

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

  const response = await client.get(path`/2/news/${flags.id}`, {
    "news.fields": flags.fields ?? NEWS_FIELDS,
  });

  return flags.raw ? response : response.data;
}
