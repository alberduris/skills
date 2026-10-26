import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

/** One ID or many, the same lookup, so `data` is always an array. */
export async function get(client: Client, args: string[]): Promise<Output> {
  const { ids } = parseArgs<{ ids: string }>(args, {
    positional: { key: "ids", label: "At least one post ID" },
  });

  const response = await client.get("/2/tweets", {
    ids: ids.split(",").map((id) => id.trim()),
    ...POST_FIELDS,
  });
  return output(response, hydrate(response));
}
