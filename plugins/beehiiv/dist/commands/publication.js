import { parseArgs, RAW } from "../lib/args.js";
export async function publication(client, args, pubId) {
    const flags = parseArgs(args, {
        flags: {
            ...RAW,
            "--expand": { key: "expand", type: "string[]" },
        },
        defaults: { expand: ["stats"] },
    });
    const params = {};
    if (flags.expand !== undefined)
        params.expand = flags.expand;
    const response = await client.get(`/publications/${pubId}`, params);
    if (flags.raw)
        return response;
    return response.data;
}
