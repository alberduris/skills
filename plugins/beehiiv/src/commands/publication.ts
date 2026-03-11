import type { BeehiivClient } from "../client.js";
import { parseArgs, RAW } from "../lib/args.js";

interface PublicationFlags {
  expand?: string[];
  raw: boolean;
}

export async function publication(
  client: BeehiivClient,
  args: string[],
  pubId: string,
): Promise<unknown> {
  const flags = parseArgs<PublicationFlags>(args, {
    flags: {
      ...RAW,
      "--expand": { key: "expand", type: "string[]" },
    },
    defaults: { expand: ["stats"] },
  });

  const params: Record<string, string | string[]> = {};
  if (flags.expand !== undefined) params.expand = flags.expand;

  const response = await client.get(`/publications/${pubId}`, params);
  if (flags.raw) return response;
  return (response as { data: unknown }).data;
}
