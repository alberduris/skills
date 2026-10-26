import { loadConfig } from "./src/config.ts";
import { createClient } from "./src/http/client.ts";
import { commands } from "./src/commands/index.ts";
import { formatError } from "./src/lib/errors.ts";

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);

  if (!command || !Object.hasOwn(commands, command)) {
    console.error(
      `Usage: node x.ts <command> [args]\nCommands: ${Object.keys(commands).join(", ")}`,
    );
    process.exitCode = 1;
    return;
  }

  const client = createClient(loadConfig(import.meta.dirname));
  const result = await commands[command](client, args);
  if (result !== undefined) {
    console.log(JSON.stringify(result, null, 2));
  }
}

main().catch((error: unknown) => {
  for (const line of formatError(error)) console.error(line);
  process.exitCode = 1;
});
