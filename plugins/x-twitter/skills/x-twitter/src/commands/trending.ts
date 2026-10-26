import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { output, type Output } from "./output.ts";

export async function trending(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<{ personalized: boolean }>(args, {
    flags: {
      "--personalized": { key: "personalized", type: "boolean" },
    },
  });

  // Trends by place (WOEID 1 is worldwide) accept only app-only auth; the
  // account's personalized trends accept only user context.
  const response = flags.personalized
    ? await client.get("/2/users/personalized_trends")
    : await client.get("/2/trends/by/woeid/1", {}, "app-only");

  return output(response, response.data ?? []);
}
