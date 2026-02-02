import type { Client } from "@xdevplatform/xdk";

// XDK: users.followUser(myId, { body: { target_user_id } })
// Requires resolveMyId() + resolving username → userId
export async function follow(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: follow");
}

// XDK: users.unfollowUser(myId, targetUserId)
export async function unfollow(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: unfollow");
}
