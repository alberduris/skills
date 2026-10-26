import type { Client } from "../http/client.ts";
import type { Output } from "./output.ts";
import { me } from "./me.ts";
import { search } from "./search.ts";
import { get } from "./get.ts";
import { post } from "./post.ts";
import { del } from "./delete.ts";
import { like, unlike } from "./like.ts";
import { repost, unrepost } from "./repost.ts";
import { hideReply } from "./hide-reply.ts";
import { searchUsers } from "./search-users.ts";
import { count } from "./count.ts";
import { trending } from "./trending.ts";
import { timeline } from "./timeline.ts";
import { mentions } from "./mentions.ts";
import { bookmarks } from "./bookmarks.ts";
import { blocked } from "./blocked.ts";
import { mute, unmute, muted } from "./mute.ts";
import { repostsOfMe } from "./reposts-of-me.ts";
import { user } from "./user.ts";
import { follow, unfollow } from "./follow.ts";
import { followers, following } from "./followers.ts";
import { likers } from "./likers.ts";
import { reposters } from "./reposters.ts";
import { quotes } from "./quotes.ts";
import { community } from "./community.ts";
import { searchCommunities } from "./search-communities.ts";
import { searchNews } from "./search-news.ts";
import { news } from "./news.ts";
import { thread } from "./thread.ts";
import { replies } from "./replies.ts";
import { transcript } from "./transcript.ts";
import { usage } from "./usage.ts";

export type Command = (client: Client, args: string[]) => Promise<Output>;

export const commands: Record<string, Command> = {
  me,
  search,
  get,
  post,
  delete: del,
  like,
  unlike,
  repost,
  unrepost,
  "hide-reply": hideReply,
  "search-users": searchUsers,
  count,
  trending,
  timeline,
  mentions,
  bookmarks,
  blocked,
  mute,
  unmute,
  muted,
  "reposts-of-me": repostsOfMe,
  user,
  follow,
  unfollow,
  followers,
  following,
  likers,
  reposters,
  quotes,
  community,
  "search-communities": searchCommunities,
  "search-news": searchNews,
  news,
  thread,
  replies,
  transcript,
  usage,
};
