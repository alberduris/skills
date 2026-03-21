import { parseArgs, PAGINATION, RAW } from "../lib/args.js";
export async function publications(client, args, _pubId) {
    const flags = parseArgs(args, {
        flags: {
            ...PAGINATION,
            ...RAW,
            "--direction": { key: "direction", type: "string" },
            "--order-by": { key: "orderBy", type: "string" },
            "--expand": { key: "expand", type: "string[]" },
        },
    });
    const params = {};
    if (flags.limit !== undefined)
        params.limit = String(flags.limit);
    if (flags.page !== undefined)
        params.page = String(flags.page);
    if (flags.direction !== undefined)
        params.direction = flags.direction;
    if (flags.orderBy !== undefined)
        params.order_by = flags.orderBy;
    if (flags.expand !== undefined)
        params.expand = flags.expand;
    const response = await client.get("/publications", params);
    if (flags.raw)
        return response;
    return response.data ?? [];
}
