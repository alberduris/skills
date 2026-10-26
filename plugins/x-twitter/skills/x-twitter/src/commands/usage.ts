import type { Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";

interface UsageFlags {
  days?: number;
  raw: boolean;
}

/**
 * Project consumption against the post-read cap. This is not a credit balance:
 * `project_usage` counts posts read, and stays flat when you create or delete
 * them. The X API exposes no dollar balance — that lives in the Developer
 * Console only.
 */
export async function usage(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<UsageFlags>(args, {
    flags: {
      ...RAW,
      "--days": { key: "days", type: "number" },
    },
  });

  // Accepts only app-only auth
  const response = await client.get("/2/usage/tweets", { days: flags.days }, "app-only");

  return flags.raw ? response : response.data;
}
