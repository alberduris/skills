import type { ApiResponse } from "../http/client.ts";

interface UrlEntity {
  url: string;
  expanded_url: string;
  media_key?: string;
}

interface Entities {
  urls?: UrlEntity[];
}

interface Reference {
  type: string;
  id: string;
}

/** A post as X sends it, in `data` or `includes.tweets`. */
interface RawPost {
  id: string;
  text: string;
  author_id: string;
  created_at: string;
  conversation_id: string;
  attachments?: { media_keys?: string[] };
  entities?: Entities;
  note_tweet?: { text: string; entities?: Entities };
  referenced_tweets?: Reference[];
  in_reply_to_user_id?: string;
  [field: string]: unknown;
}

export interface User {
  id: string;
  name?: string;
  username?: string;
}

/** A self-contained post. Fields not named here are X's own, unchanged. */
export interface Post {
  id: string;
  author: User;
  created_at: string;
  in_reply_to_user?: User;
  text: string;
  media?: object[];
  attachments?: object;
  referenced_tweets?: (Reference | (Reference & Post))[];
  conversation_id: string;
  [field: string]: unknown;
}

/**
 * Turns X's envelope into posts that read as they do on x.com, resolving each
 * reference into the object `includes` holds for it: `author_id` becomes
 * `author`, `in_reply_to_user_id` becomes `in_reply_to_user`,
 * `attachments.media_keys` becomes `media`, and quoted and retweeted posts are
 * embedded in `referenced_tweets`. A replied-to post stays a reference, as
 * x.com shows only "Replying to @user"; so does any reference X did not
 * include, which X's `errors` explains at the top level but not for the posts
 * an embedded post references, since X expands one level only. `note_tweet`
 * and `entities` are consumed into `text`.
 */
export function hydrate({ data, includes = {} }: ApiResponse): Post[] {
  const users = index<User>(includes.users, "id");
  const media = index<object>(includes.media, "media_key");
  const posts = index<RawPost>(includes.tweets, "id");
  const user = (id: string): User => users.get(id) ?? { id };

  function hydratePost(raw: RawPost): Post {
    const {
      id, text, author_id, created_at, conversation_id, attachments, entities,
      note_tweet, referenced_tweets, in_reply_to_user_id, ...fields
    } = raw;
    const quoted = referenced_tweets?.find((ref) => ref.type === "quoted");
    const { media_keys, ...otherAttachments } = attachments ?? {};

    return {
      id,
      author: user(author_id),
      created_at,
      ...(in_reply_to_user_id && { in_reply_to_user: user(in_reply_to_user_id) }),
      text: readable(note_tweet ?? { text: decodeHtml(text), entities }, quoted?.id),
      ...(media_keys && { media: media_keys.map((key) => media.get(key) ?? { media_key: key }) }),
      ...(Object.keys(otherAttachments).length > 0 && { attachments: otherAttachments }),
      ...(referenced_tweets && { referenced_tweets: referenced_tweets.map(embed) }),
      conversation_id,
      ...fields,
    };
  }

  function embed(ref: Reference): Reference | (Reference & Post) {
    const target = ref.type === "replied_to" ? undefined : posts.get(ref.id);
    return target ? { type: ref.type, ...hydratePost(target) } : ref;
  }

  return ((data ?? []) as RawPost[]).map(hydratePost);
}

/**
 * The text a human reads: t.co links replaced by their target, except the
 * ones x.com hides because it shows their target separately, namely links to
 * the post's own media and the trailing link to the quoted post.
 */
function readable({ text, entities }: { text: string; entities?: Entities }, quotedId?: string): string {
  for (const { url, expanded_url, media_key } of entities?.urls ?? []) {
    const hidden =
      media_key !== undefined ||
      (quotedId !== undefined && statusId(expanded_url) === quotedId && text.trimEnd().endsWith(url));
    text = text.replaceAll(url, hidden ? "" : expanded_url);
  }
  return text.trimEnd();
}

/** X escapes these three in `text`, though not in `note_tweet.text`. */
function decodeHtml(text: string): string {
  return text.replaceAll("&lt;", "<").replaceAll("&gt;", ">").replaceAll("&amp;", "&");
}

function statusId(url: string): string | undefined {
  return /\/status\/(\d+)/.exec(url)?.[1];
}

function index<T>(items: unknown[] | undefined, key: string): Map<string, T> {
  return new Map((items ?? []).map((item) => [(item as Record<string, string>)[key], item as T]));
}
