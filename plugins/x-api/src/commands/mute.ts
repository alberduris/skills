import type { Client } from "@xdevplatform/xdk";

// XDK: users.muteUser(myId, { body: { target_user_id } })
// Requires resolveMyId() + resolving username → userId
export async function mute(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: mute");
}

// XDK: users.unmuteUser(myId, targetUserId)
export async function unmute(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: unmute");
}

// XDK: users.getMuting(myId, options)
export async function muted(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: muted");
}
