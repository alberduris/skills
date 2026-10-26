import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { COMMUNITY_FIELDS } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

export async function community(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{ id: string }>(args, {
    positional: { key: "id", label: "A community ID" },
  });

  const response = await client.get(path`/2/communities/${flags.id}`, {
    "community.fields": COMMUNITY_FIELDS,
  });
  return output(response);
}
