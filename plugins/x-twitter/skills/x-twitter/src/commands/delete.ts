import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { output, type Output } from "./output.ts";

export async function del(
  client: Client,
  args: string[],
): Promise<Output> {
  const { id } = parseArgs<{ id: string }>(args, {
    positional: { key: "id", label: "A post ID" },
  });

  return output(await client.delete(path`/2/tweets/${id}`));
}
