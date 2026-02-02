import type { Client } from "@xdevplatform/xdk";

// XDK: users.createBookmark(myId, { tweet_id })
// Requires resolveMyId()
export async function bookmark(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: bookmark");
}

// XDK: users.deleteBookmark(myId, tweetId)
export async function unbookmark(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: unbookmark");
}

// XDK: users.getBookmarks(myId, options)
export async function bookmarks(client: Client, args: string[]): Promise<void> {
  void client, args;
  throw new Error("Not implemented: bookmarks");
}
