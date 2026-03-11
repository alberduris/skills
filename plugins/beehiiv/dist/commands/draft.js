import { readFileSync } from "fs";
import { extname } from "path";
import { marked } from "marked";
import { parseArgs, RAW } from "../lib/args.js";
function readContentFile(filePath) {
    const raw = readFileSync(filePath, "utf-8");
    const ext = extname(filePath).toLowerCase();
    if (ext === ".md" || ext === ".markdown") {
        return marked.parse(raw, { async: false });
    }
    return raw;
}
function readStdin() {
    return new Promise((resolve, reject) => {
        const chunks = [];
        process.stdin.on("data", (chunk) => chunks.push(chunk));
        process.stdin.on("end", () => resolve(Buffer.concat(chunks).toString("utf-8")));
        process.stdin.on("error", reject);
    });
}
export async function draft(client, args, pubId) {
    const flags = parseArgs(args, {
        positional: { key: "title", label: "Post title" },
        flags: {
            ...RAW,
            "--subtitle": { key: "subtitle", type: "string" },
            "--content": { key: "content", type: "string" },
            "--content-file": { key: "contentFile", type: "string" },
            "--content-tags": { key: "contentTags", type: "string[]" },
            "--template-id": { key: "templateId", type: "string" },
            "--slug": { key: "slug", type: "string" },
        },
    });
    let bodyContent;
    if (flags.contentFile) {
        bodyContent = readContentFile(flags.contentFile);
    }
    else if (flags.content === "-") {
        const stdin = await readStdin();
        bodyContent = stdin;
    }
    else if (flags.content) {
        bodyContent = flags.content;
    }
    const body = {
        title: flags.title,
        status: "draft",
    };
    if (bodyContent)
        body.body_content = bodyContent;
    if (flags.subtitle)
        body.subtitle = flags.subtitle;
    if (flags.templateId)
        body.post_template_id = flags.templateId;
    if (flags.slug)
        body.web_settings = { slug: flags.slug };
    if (flags.contentTags)
        body.content_tags = flags.contentTags;
    const response = await client.post(`/publications/${pubId}/posts`, body);
    if (flags.raw)
        return response;
    return response.data;
}
