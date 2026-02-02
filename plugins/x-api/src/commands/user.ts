import type { Client } from "@xdevplatform/xdk";

// XDK: users.getByUsername(username) | users.getById(id) | users.getByIds(ids)
export async function user(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: user");
}
