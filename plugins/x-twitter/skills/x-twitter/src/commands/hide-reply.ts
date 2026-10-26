import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";

export async function hideReply(
  client: Client,
  args: string[],
): Promise<unknown> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  return client.put(path`/2/tweets/${tweetId}/hidden`, { hidden: true });
}
