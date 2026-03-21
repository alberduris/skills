import { parseArgs, RAW } from "../lib/args.js";
import { COMMUNITY_FIELDS } from "../lib/fields.js";
export async function community(client, args) {
    const flags = parseArgs(args, {
        positional: { key: "id", label: "A community ID" },
        flags: { ...RAW },
    });
    const options = {
        communityFields: COMMUNITY_FIELDS,
    };
    const response = await client.communities.getById(flags.id, options);
    return flags.raw ? response : response.data;
}
