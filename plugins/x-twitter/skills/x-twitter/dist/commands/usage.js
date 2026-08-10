import { parseArgs, RAW } from "../lib/args.js";
/**
 * Project consumption against the post-read cap. This is not a credit balance:
 * `projectUsage` counts posts read, and stays flat when you create or delete
 * them. The X API exposes no dollar balance — that lives in the Developer
 * Console only.
 */
export async function usage(client, args) {
    const flags = parseArgs(args, {
        flags: {
            ...RAW,
            "--days": { key: "days", type: "number" },
        },
    });
    const response = await client.usage.get({
        ...(flags.days !== undefined && { days: flags.days }),
    });
    return flags.raw ? response : response.data;
}
