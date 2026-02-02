import type { Client } from "@xdevplatform/xdk";

// XDK: users.repostPost(myId, { body: { tweet_id } })
export async function repost(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: repost");
}

// XDK: users.unrepostPost(myId, sourceTweetId)
export async function unrepost(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: unrepost");
}
