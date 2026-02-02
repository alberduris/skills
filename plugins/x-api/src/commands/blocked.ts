import type { Client } from "@xdevplatform/xdk";

// XDK: users.getBlocking(myId, options)
// Requires resolveMyId()
export async function blocked(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: blocked");
}
