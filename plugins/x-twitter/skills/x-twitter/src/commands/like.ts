import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { resolveMyId } from "../lib/resolve.ts";

export async function like(client: Client, args: string[]): Promise<unknown> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  const myId = await resolveMyId(client);
  return client.post(path`/2/users/${myId}/likes`, { tweet_id: tweetId });
}

export async function unlike(client: Client, args: string[]): Promise<unknown> {
  const { tweetId } = parseArgs<{ tweetId: string }>(args, {
    positional: { key: "tweetId", label: "A tweet ID" },
  });

  const myId = await resolveMyId(client);
  return client.delete(path`/2/users/${myId}/likes/${tweetId}`);
}
