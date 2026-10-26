import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate, type Post } from "../posts/hydrate.ts";
import { subtitles, type Subtitles } from "../transcript/subtitles.ts";
import { output, type Output } from "./output.ts";

/** A media item as X describes it, in the fields this command reads. */
interface Media {
  media_key: string;
  type?: string;
  variants?: { content_type: string; url: string }[];
}

/**
 * The transcript of the videos attached to a post, from the subtitle tracks X
 * generates for them. Only the post lookup is a billed read. A video without
 * a subtitle track has no transcript: the video itself is never downloaded.
 */
export async function transcript(client: Client, args: string[]): Promise<Output> {
  const { id } = parseArgs<{ id: string }>(args, {
    positional: { key: "id", label: "A post ID" },
  });

  const response = await client.get("/2/tweets", { ids: id, ...POST_FIELDS });
  const [post] = hydrate(response);
  if (!post) return output(response, []);

  const ownVideos = videos(post);
  if (ownVideos.length === 0) return output(response, [], [noVideoHint(post)]);

  const data: ({ media_key: string } & Subtitles)[] = [];
  const hints: string[] = [];
  for (const { media_key, variants } of ownVideos) {
    const playlist = variants?.find((variant) => variant.content_type === "application/x-mpegURL");
    const tracks = playlist ? await subtitles(playlist.url) : [];
    if (tracks.length === 0) hints.push(`X published no subtitle track for video ${media_key}.`);
    data.push(...tracks.map((track) => ({ media_key, ...track })));
  }
  return output(response, data, hints);
}

function videos(post: Post): Media[] {
  return ((post.media ?? []) as Media[]).filter((media) => media.type === "video");
}

/** Names the quoted or retweeted post when the video is in that one. */
function noVideoHint(post: Post): string {
  const embedded = post.referenced_tweets?.find((ref) => "media" in ref && videos(ref).length > 0);
  return embedded
    ? `Post ${post.id} has no video of its own; the ${embedded.type} post ${embedded.id} has one: run transcript ${embedded.id}.`
    : `Post ${post.id} has no video.`;
}
