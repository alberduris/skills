import { parseArgs, PAGINATION, RAW } from "../lib/args.js";
export async function posts(client, args, pubId) {
    const flags = parseArgs(args, {
        flags: {
            ...PAGINATION,
            ...RAW,
            "--status": { key: "status", type: "string" },
            "--content-tags": { key: "contentTags", type: "string[]" },
            "--authors": { key: "authors", type: "string[]" },
            "--audience": { key: "audience", type: "string" },
            "--platform": { key: "platform", type: "string" },
            "--order-by": { key: "orderBy", type: "string" },
            "--direction": { key: "direction", type: "string" },
            "--expand": { key: "expand", type: "string[]" },
            "--slugs": { key: "slugs", type: "string[]" },
            "--hidden-from-feed": { key: "hiddenFromFeed", type: "string" },
        },
    });
    const params = {};
    if (flags.status !== undefined)
        params.status = flags.status;
    if (flags.contentTags !== undefined)
        params.content_tags = flags.contentTags;
    if (flags.authors !== undefined)
        params.authors = flags.authors;
    if (flags.audience !== undefined)
        params.audience = flags.audience;
    if (flags.platform !== undefined)
        params.platform = flags.platform;
    if (flags.orderBy !== undefined)
        params.order_by = flags.orderBy;
    if (flags.direction !== undefined)
        params.direction = flags.direction;
    if (flags.limit !== undefined)
        params.limit = String(flags.limit);
    if (flags.page !== undefined)
        params.page = String(flags.page);
    if (flags.expand !== undefined)
        params.expand = flags.expand;
    if (flags.slugs !== undefined)
        params.slugs = flags.slugs;
    if (flags.hiddenFromFeed !== undefined)
        params.hidden_from_feed = flags.hiddenFromFeed;
    const response = await client.get(`/publications/${pubId}/posts`, params);
    if (flags.raw)
        return response;
    return response.data ?? [];
}
