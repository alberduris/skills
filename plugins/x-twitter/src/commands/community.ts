import type { Client } from "@xdevplatform/xdk";
import { parseArgs, RAW } from "../lib/args.js";
import { COMMUNITY_FIELDS } from "../lib/fields.js";

export async function community(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{ id: string; raw: boolean }>(args, {
    positional: { key: "id", label: "A community ID" },
    flags: { ...RAW },
  });

  const options: Record<string, unknown> = {
    communityFields: COMMUNITY_FIELDS,
  };

  const response = await client.communities.getById(flags.id, options);
  return flags.raw ? response : response.data;
}
