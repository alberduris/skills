import type { Client } from "../http/client.ts";
import { parseArgs, TEMPORAL, RAW } from "../lib/args.ts";
import { resolveEnum } from "../lib/enums.ts";

interface CountFlags {
  query: string;
  all: boolean;
  startTime?: string;
  endTime?: string;
  granularity?: string;
  nextToken?: string;
  raw: boolean;
}

export async function count(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<CountFlags>(args, {
    positional: { key: "query", label: "A search query" },
    flags: {
      ...TEMPORAL,
      ...RAW,
      "--all": { key: "all", type: "boolean" },
      "--granularity": { key: "granularity", type: "string" },
      "--next-token": { key: "nextToken", type: "string" },
    },
  });

  if (flags.granularity !== undefined) {
    flags.granularity = resolveEnum("granularity", flags.granularity);
  }

  // Both counts endpoints accept only app-only auth
  const response = await client.get(
    flags.all ? "/2/tweets/counts/all" : "/2/tweets/counts/recent",
    {
      query: flags.query,
      start_time: flags.startTime,
      end_time: flags.endTime,
      granularity: flags.granularity,
      next_token: flags.nextToken,
    },
    "app-only",
  );

  return flags.raw ? response : (response.data ?? []);
}
