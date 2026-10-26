Retrieves the transcript of the video(s) attached to a post, from the subtitle track X generates for each video. Invoke via `node <base_directory>/x.ts transcript <tweet_id>`. Output is JSON to stdout.

[!HOW-IT-WORKS] 1) Looks up the post. 2) For each video attached to it, reads from X's video CDN (video.twimg.com) the HLS playlist, which declares the video's subtitle tracks, then each track's WebVTT; X's API itself returns no captions. Nothing is downloaded or transcribed locally, so a video X published no subtitle track for has no transcript.

[!FLAGS] No flags.

[!OUTPUT-SHAPE] `data` is an array with one entry per subtitle track of each video: `media_key` of the video, `language`, `name` as X labels the track (`"en (auto-generated)"` for X's automatic captions), and `text`, the cues one per line, each prefixed with its start time: `[00:07] So you build a cage of steel bars`, or `[1:02:03] ...` past one hour. A video with no subtitle track has no entry, and `hints` says so. When the post has no video of its own, `data` is empty and `hints` says so, naming the quoted or reposted post when that one has a video: run `transcript` on that ID.

[!COST] One billed read: the post lookup. The subtitles come from X's video CDN, which needs no credentials and is not billed.
