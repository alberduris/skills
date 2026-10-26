import type { Client } from "../http/client.ts";
import { parseArgs, TEMPORAL } from "../lib/args.ts";
import { resolveEnum } from "../lib/enums.ts";
import { output, type Output } from "./output.ts";

interface CountFlags {
  query: string;
  all: boolean;
  startTime?: string;
  endTime?: string;
  granularity?: string;
  nextToken?: string;
}

export async function count(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<CountFlags>(args, {
    positional: { key: "query", label: "A search query" },
    flags: {
      ...TEMPORAL,
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

  return output(response, response.data ?? []);
}
