import type { Client } from "@xdevplatform/xdk";

// XDK: users.likePost(myId, { body: { tweet_id } })
export async function like(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: like");
}

// XDK: users.unlikePost(myId, tweetId)
export async function unlike(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: unlike");
}
