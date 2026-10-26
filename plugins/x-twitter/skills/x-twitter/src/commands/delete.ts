import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";

export async function del(
  client: Client,
  args: string[],
): Promise<unknown> {
  const { id } = parseArgs<{ id: string }>(args, {
    positional: { key: "id", label: "A post ID" },
  });

  return client.delete(path`/2/tweets/${id}`);
}
