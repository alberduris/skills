import { parseArgs, PAGINATION, RAW } from "../lib/args.js";
export async function templates(client, args, pubId) {
    const flags = parseArgs(args, {
        flags: {
            ...PAGINATION,
            ...RAW,
        },
    });
    const params = {};
    if (flags.limit !== undefined)
        params.limit = String(flags.limit);
    if (flags.page !== undefined)
        params.page = String(flags.page);
    const response = await client.get(`/publications/${pubId}/post_templates`, params);
    if (flags.raw)
        return response;
    return response.data ?? [];
}
