import type { BeehiivClient } from "./client.js";
import { dirname, resolve } from "path";
import { fileURLToPath } from "url";
import { loadConfig } from "./config.js";
import { createClient } from "./client.js";
import { publications } from "./commands/publications.js";
import { publication } from "./commands/publication.js";
import { posts } from "./commands/posts.js";
import { get } from "./commands/get.js";
import { draft } from "./commands/draft.js";
import { templates } from "./commands/templates.js";

type CommandFn = (
  client: BeehiivClient,
  args: string[],
  pubId: string,
) => Promise<unknown>;

const commands: Record<string, CommandFn> = {
  publications,
  publication,
  posts,
  get,
  draft,
  templates,
};

// Commands that don't require a publication ID
const PUB_ID_OPTIONAL = new Set(["publications"]);

const COMMAND_NAMES = Object.keys(commands).join(", ");

function pluginDir(): string {
  return resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
}

function extractPubId(args: string[]): { pubId: string | undefined; rest: string[] } {
  const idx = args.indexOf("--pub-id");
  if (idx === -1) return { pubId: undefined, rest: args };

  const pubId = args[idx + 1];
  if (!pubId) throw new Error("--pub-id requires a value");

  const rest = [...args.slice(0, idx), ...args.slice(idx + 2)];
  return { pubId, rest };
}

async function main(): Promise<void> {
  const [command, ...rawArgs] = process.argv.slice(2);

  if (!command || !commands[command]) {
    console.error(`Usage: beehiiv <command> [args]\nCommands: ${COMMAND_NAMES}`);
    process.exit(1);
  }

  const config = loadConfig(pluginDir());
  const client = createClient(config);

  const { pubId: flagPubId, rest: args } = extractPubId(rawArgs);
  const pubId = flagPubId ?? config.publicationId ?? "";

  if (!pubId && !PUB_ID_OPTIONAL.has(command)) {
    throw new Error(
      `Publication ID required. Set BEEHIIV_PUBLICATION_ID in .env or pass --pub-id <id>.`,
    );
  }

  const result = await commands[command](client, args, pubId);
  if (result !== undefined) {
    console.log(JSON.stringify(result, null, 2));
  }
  process.exit(0);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Error: ${message}`);
  process.exit(1);
});
