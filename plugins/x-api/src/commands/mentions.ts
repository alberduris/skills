import type { Client } from "@xdevplatform/xdk";

// XDK: users.getMentions(myId, options)
// Requires resolveMyId()
export async function mentions(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: mentions");
}
