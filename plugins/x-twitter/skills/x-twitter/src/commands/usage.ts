import type { Client } from "@xdevplatform/xdk";
import { parseArgs, RAW } from "../lib/args.js";

interface UsageFlags {
  days?: number;
  raw: boolean;
}

/**
 * Project consumption against the post-read cap. This is not a credit balance:
 * `projectUsage` counts posts read, and stays flat when you create or delete
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

  const response = await client.usage.get({
    ...(flags.days !== undefined && { days: flags.days }),
  });

  return flags.raw ? response : response.data;
}
