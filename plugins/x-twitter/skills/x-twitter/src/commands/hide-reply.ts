import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { output, type Output } from "./output.ts";

export async function hideReply(
  client: Client,
  args: string[],
): Promise<Output> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  return output(await client.put(path`/2/tweets/${tweetId}/hidden`, { hidden: true }));
}
