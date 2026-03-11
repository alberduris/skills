import type { BeehiivClient } from "../client.js";
import { parseArgs, PAGINATION, RAW } from "../lib/args.js";

interface TemplatesFlags {
  limit?: number;
  page?: number;
  raw: boolean;
}

export async function templates(
  client: BeehiivClient,
  args: string[],
  pubId: string,
): Promise<unknown> {
  const flags = parseArgs<TemplatesFlags>(args, {
    flags: {
      ...PAGINATION,
      ...RAW,
    },
  });

  const params: Record<string, string | string[]> = {};
  if (flags.limit !== undefined) params.limit = String(flags.limit);
  if (flags.page !== undefined) params.page = String(flags.page);

  const response = await client.get(
    `/publications/${pubId}/post_templates`,
    params,
  );
  if (flags.raw) return response;
  return (response as { data: unknown }).data ?? [];
}
