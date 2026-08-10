import type {
  CommunitiesClient,
  NewsClient,
  PostsClient,
  UsersClient,
} from "@xdevplatform/xdk";

/**
 * Field and expansion names are literal string unions in the SDK, not plain
 * strings. Deriving them from the client signatures keeps one source of truth:
 * when the SDK adds or drops a field, tsc flags the lists below instead of
 * letting a bad name reach the API at runtime.
 *
 * Values coming from `--fields` on the command line stay untyped until
 * `parseArgs` hands them back as the command's flag type — that single cast in
 * lib/args.ts is the only place dynamic input crosses into these types.
 */
type PostOptions = NonNullable<Parameters<PostsClient["searchRecent"]>[1]>;
export type TweetField = NonNullable<PostOptions["tweetFields"]>[number];
export type TweetExpansion = NonNullable<PostOptions["expansions"]>[number];
export type TweetUserField = NonNullable<PostOptions["userFields"]>[number];

type UserOptions = NonNullable<Parameters<UsersClient["getByUsername"]>[1]>;
export type UserField = NonNullable<UserOptions["userFields"]>[number];

type CommunityOptions = NonNullable<Parameters<CommunitiesClient["getById"]>[1]>;
export type CommunityField = NonNullable<
  CommunityOptions["communityFields"]
>[number];

type NewsOptions = NonNullable<Parameters<NewsClient["search"]>[1]>;
export type NewsField = NonNullable<NewsOptions["newsFields"]>[number];

export const TWEET_FIELDS: TweetField[] = [
  "article",
  "author_id",
  "created_at",
  "conversation_id",
  "paid_partnership",
  "public_metrics",
  "referenced_tweets",
  "in_reply_to_user_id",
  "text",
];

export const TWEET_EXPANSIONS: TweetExpansion[] = ["author_id"];
export const TWEET_USER_FIELDS: TweetUserField[] = ["name", "username"];

export const USER_FIELDS: UserField[] = [
  "created_at",
  "description",
  "id",
  "name",
  "profile_image_url",
  "public_metrics",
  "username",
  "verified_type",
];

export const USER_FIELDS_EXTENDED: UserField[] = [
  ...USER_FIELDS,
  "connection_status",
  "location",
  "protected",
  "receives_your_dm",
  "url",
];

export const COMMUNITY_FIELDS: CommunityField[] = [
  "access",
  "created_at",
  "description",
  "id",
  "join_policy",
  "member_count",
  "name",
];

export const NEWS_FIELDS: NewsField[] = [
  "category",
  "cluster_posts_results",
  "contexts",
  "disclaimer",
  "hook",
  "keywords",
  "name",
  "summary",
  "updated_at",
];
