import type { Client } from "@xdevplatform/xdk";

// XDK: trends.getByWoeid(woeid) — default woeid=1 for worldwide
// Flag --personalized → trends.getPersonalized()
export async function trending(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: trending");
}
