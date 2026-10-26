/**
 * The subtitles X generates for a video, read off its video CDN, since X's
 * API returns no captions: the video's HLS master playlist declares each
 * subtitle track, a track's playlist lists its WebVTT segments, and the
 * segments hold the cues. video.twimg.com needs no auth and is not billed, so
 * this is plain fetch, not the X client.
 */

export interface Subtitles {
  language: string;
  /** X's label for the track, e.g. "en (auto-generated)". */
  name: string;
  /** The cues, one per line, each prefixed with its start time. */
  text: string;
}

/** Every subtitle track of the video whose master playlist is at `playlistUrl`. */
export async function subtitles(playlistUrl: string): Promise<Subtitles[]> {
  const result: Subtitles[] = [];
  for (const { language, name, uri } of subtitleTracks(await fetchText(playlistUrl))) {
    const trackUrl = new URL(uri, playlistUrl);
    const lines: string[] = [];
    for (const segment of segmentUris(await fetchText(trackUrl))) {
      lines.push(...cueLines(await fetchText(new URL(segment, trackUrl))));
    }
    result.push({ language, name, text: lines.join("\n") });
  }
  return result;
}

async function fetchText(url: string | URL): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText} from ${url}`);
  return response.text();
}

/** The `#EXT-X-MEDIA:TYPE=SUBTITLES` tracks of an HLS master playlist. */
export function subtitleTracks(masterPlaylist: string): { language: string; name: string; uri: string }[] {
  return masterPlaylist
    .split("\n")
    .filter((line) => line.startsWith("#EXT-X-MEDIA:"))
    .map((line) => attributes(line.slice("#EXT-X-MEDIA:".length)))
    .filter((media) => media.TYPE === "SUBTITLES")
    .map(({ LANGUAGE, NAME, URI }) => ({ language: LANGUAGE, name: NAME, uri: URI }));
}

/** An HLS attribute list, `KEY=VALUE,KEY="quoted, value"`, quotes removed. */
function attributes(list: string): Record<string, string> {
  return Object.fromEntries(
    [...list.matchAll(/([A-Z0-9-]+)=(?:"([^"]*)"|([^,]*))/g)].map(([, key, quoted, plain]) => [key, quoted ?? plain]),
  );
}

/** The segment URIs of an HLS media playlist: its lines that are not tags. */
export function segmentUris(playlist: string): string[] {
  return playlist.split("\n").filter((line) => line !== "" && !line.startsWith("#"));
}

/**
 * The cues of a WebVTT segment, one line each, prefixed with the cue's start
 * time as `[mm:ss]`, or `[h:mm:ss]` past one hour. X wraps each cue's words in
 * an `<X-word-ms>` tag carrying per-word timings; only the words are kept.
 */
export function cueLines(vtt: string): string[] {
  return vtt.split("\n\n").flatMap((block) => {
    const [timing, ...text] = block.split("\n");
    const start = /^(\d+):(\d\d):(\d\d)\.\d+ -->/.exec(timing);
    if (!start) return []; // the WEBVTT header
    const [, hours, minutes, seconds] = start;
    const time = Number(hours) === 0 ? `${minutes}:${seconds}` : `${Number(hours)}:${minutes}:${seconds}`;
    return [`[${time}] ${text.join(" ").replace(/<[^>]*>/g, "").trim()}`];
  });
}
