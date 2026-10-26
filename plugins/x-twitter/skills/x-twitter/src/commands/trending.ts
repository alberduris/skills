import type { Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";

export async function trending(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<{ personalized: boolean; raw: boolean }>(args, {
    flags: {
      ...RAW,
      "--personalized": { key: "personalized", type: "boolean" },
    },
  });

  // Trends by place (WOEID 1 is worldwide) accept only app-only auth; the
  // account's personalized trends accept only user context.
  const response = flags.personalized
    ? await client.get("/2/users/personalized_trends")
    : await client.get("/2/trends/by/woeid/1", {}, "app-only");

  return flags.raw ? response : (response.data ?? []);
}
