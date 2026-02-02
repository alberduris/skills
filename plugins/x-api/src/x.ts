import type { Client } from "@xdevplatform/xdk";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import { loadConfig } from "./config.js";
import { createClient } from "./client.js";
import { me } from "./commands/me.js";
import { searchRecent } from "./commands/posts/search/search-recent.js";
import { searchAll } from "./commands/posts/search/search-all.js";
import { getPost } from "./commands/posts/lookup/get-post.js";
import { getPosts } from "./commands/posts/lookup/get-posts.js";
import { createPost } from "./commands/posts/manage/create-post.js";
import { deletePost } from "./commands/posts/manage/delete-post.js";

type CommandFn = (client: Client, args: string[]) => Promise<void>;

const commands: Record<string, CommandFn> = {
  me,
  "search-recent": searchRecent,
  "search-all": searchAll,
  "get-post": getPost,
  "get-posts": getPosts,
  "create-post": createPost,
  "delete-post": deletePost,
};

const COMMAND_NAMES = Object.keys(commands).join(", ");

function pluginDir(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);

  if (!command || !commands[command]) {
    console.error(`Usage: x <command> [args]\nCommands: ${COMMAND_NAMES}`);
    process.exit(1);
  }

  const config = loadConfig(pluginDir());
  const client = createClient(config);
  await commands[command](client, args);
  process.exit(0);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Error: ${message}`);
  process.exit(1);
});
