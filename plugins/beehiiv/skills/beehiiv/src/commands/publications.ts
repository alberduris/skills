import type { BeehiivClient } from "../client.js";
import { parseArgs, PAGINATION, RAW } from "../lib/args.js";

interface PublicationsFlags {
  limit?: number;
  page?: number;
  direction?: string;
  orderBy?: string;
  expand?: string[];
  raw: boolean;
}

export async function publications(
  client: BeehiivClient,
  args: string[],
  _pubId?: string,
): Promise<unknown> {
  const flags = parseArgs<PublicationsFlags>(args, {
    flags: {
      ...PAGINATION,
      ...RAW,
      "--direction": { key: "direction", type: "string" },
      "--order-by": { key: "orderBy", type: "string" },
      "--expand": { key: "expand", type: "string[]" },
    },
  });

  const params: Record<string, string | string[]> = {};
  if (flags.limit !== undefined) params.limit = String(flags.limit);
  if (flags.page !== undefined) params.page = String(flags.page);
  if (flags.direction !== undefined) params.direction = flags.direction;
  if (flags.orderBy !== undefined) params.order_by = flags.orderBy;
  if (flags.expand !== undefined) params.expand = flags.expand;

  const response = await client.get("/publications", params);
  if (flags.raw) return response;
  return (response as { data: unknown }).data ?? [];
}
