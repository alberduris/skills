import type { Client } from "@xdevplatform/xdk";

// XDK: users.getTimeline(myId, options)
// Requires resolveMyId() for authenticated user's ID
export async function timeline(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: timeline");
}
