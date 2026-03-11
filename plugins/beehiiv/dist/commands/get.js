import { parseArgs, RAW } from "../lib/args.js";
export async function get(client, args, pubId) {
    const flags = parseArgs(args, {
        positional: { key: "postId", label: "A post ID" },
        flags: {
            ...RAW,
            "--expand": { key: "expand", type: "string[]" },
        },
        defaults: { expand: ["free_web_content"] },
    });
    const params = {};
    if (flags.expand !== undefined)
        params.expand = flags.expand;
    const response = await client.get(`/publications/${pubId}/posts/${flags.postId}`, params);
    if (flags.raw)
        return response;
    return response.data;
}
