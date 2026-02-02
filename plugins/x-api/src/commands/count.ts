import type { Client } from "@xdevplatform/xdk";

// XDK: posts.getCountsRecent(query, options) — last 7 days
// Flag --all → posts.getCountsAll(query, options) — full archive
export async function count(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: count");
}
