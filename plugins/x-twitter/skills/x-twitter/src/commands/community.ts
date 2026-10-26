import { path, type Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";
import { COMMUNITY_FIELDS } from "../lib/fields.ts";

export async function community(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{ id: string; raw: boolean }>(args, {
    positional: { key: "id", label: "A community ID" },
    flags: { ...RAW },
  });

  const response = await client.get(path`/2/communities/${flags.id}`, {
    "community.fields": COMMUNITY_FIELDS,
  });
  return flags.raw ? response : response.data;
}
