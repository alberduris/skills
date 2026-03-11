import type { BeehiivClient } from "../client.js";
import { parseArgs, RAW } from "../lib/args.js";

interface GetFlags {
  postId: string;
  expand?: string[];
  raw: boolean;
}

export async function get(
  client: BeehiivClient,
  args: string[],
  pubId: string,
): Promise<unknown> {
  const flags = parseArgs<GetFlags>(args, {
    positional: { key: "postId", label: "A post ID" },
    flags: {
      ...RAW,
      "--expand": { key: "expand", type: "string[]" },
    },
    defaults: { expand: ["free_web_content"] },
  });

  const params: Record<string, string | string[]> = {};
  if (flags.expand !== undefined) params.expand = flags.expand;

  const response = await client.get(
    `/publications/${pubId}/posts/${flags.postId}`,
    params,
  );
  if (flags.raw) return response;
  return (response as { data: unknown }).data;
}
