import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { resolveMyId } from "../lib/resolve.ts";
import { output, type Output } from "./output.ts";

export async function repost(client: Client, args: string[]): Promise<Output> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  const myId = await resolveMyId(client);
  return output(await client.post(path`/2/users/${myId}/retweets`, { tweet_id: tweetId }));
}

export async function unrepost(client: Client, args: string[]): Promise<Output> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  const myId = await resolveMyId(client);
  return output(await client.delete(path`/2/users/${myId}/retweets/${tweetId}`));
}
