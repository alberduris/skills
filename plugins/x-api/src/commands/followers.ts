import type { Client } from "@xdevplatform/xdk";

// XDK: users.getFollowers(userId, options)
// Input: username → resolve to userId first
export async function followers(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: followers");
}

// XDK: users.getFollowing(userId, options)
export async function following(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: following");
}
