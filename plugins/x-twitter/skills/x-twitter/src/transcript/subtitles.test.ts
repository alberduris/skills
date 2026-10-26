import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { cueLines, segmentUris, subtitleTracks } from "./subtitles.ts";

/**
 * Fixtures are the files video.twimg.com served for video
 * 13_2114521224038469632 of post 2114523620026282002, recorded on 2026-10-26:
 * the master playlist, its subtitle track's playlist, and that track's only
 * WebVTT segment.
 */
function fixture(name: string): string {
  return readFileSync(resolve(import.meta.dirname, "fixtures", name), "utf8");
}

describe("subtitleTracks", () => {
  it("reads the subtitle track of a master playlist and skips its audio tracks", () => {
    assert.deepEqual(subtitleTracks(fixture("master.m3u8")), [
      {
        language: "en",
        name: "en (auto-generated)",
        uri: "/amplify_video/2114521224038469632/pl/s0/YqSRUkI-1TA48GYo.m3u8",
      },
    ]);
  });
});

describe("segmentUris", () => {
  it("lists the WebVTT segments of a subtitle playlist", () => {
    assert.deepEqual(segmentUris(fixture("subtitles.m3u8")), [
      "/subtitles/amplify_video/2114521224038469632/0/mS9pEu70DwRWDeoJ.vtt",
    ]);
  });
});

describe("cueLines", () => {
  it("prints each cue as its start time and its words, without X's word-timing tags", () => {
    const lines = cueLines(fixture("segment.vtt"));
    assert.deepEqual(lines.slice(0, 3), [
      "[00:00] If you dig a hole in your yard",
      "[00:01] and fill it with water",
      "[00:02] you have a swimming pool",
    ]);
    assert.equal(lines.length, 39);
    assert.equal(lines.at(-1), "[00:58] somebody's sweat");
    assert.doesNotMatch(lines.join("\n"), /[<>]/);
  });

  it("adds the hour past one hour", () => {
    const vtt = "WEBVTT\n\n01:02:03.500 --> 01:02:04.500\n<X-word-ms ms=400 index=1 character_ranges=0-4>Later</X-word-ms>\n";
    assert.deepEqual(cueLines(vtt), ["[1:02:03] Later"]);
  });
});
