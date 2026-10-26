import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { NEWS_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

interface NewsFlags {
  id: string;
  fields?: string[];
}

export async function news(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<NewsFlags>(args, {
    positional: { key: "id", label: "A news story ID" },
    flags: {
      "--fields": { key: "fields", type: "string[]" },
    },
  });

  const response = await client.get(path`/2/news/${flags.id}`, {
    "news.fields": flags.fields ?? NEWS_FIELDS,
  });

  return output(response);
}
