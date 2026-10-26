/**
 * The fields and expansions every post-returning request sends: what hydrate
 * needs to show a post as x.com does. X adds the referencing fields
 * (author_id, attachments, referenced_tweets, in_reply_to_user_id) on its own
 * once their expansion is requested; they are listed anyway because hydrate
 * and thread read them.
 */
export const POST_FIELDS = {
  "tweet.fields": [
    "article",
    "attachments",
    "author_id",
    "conversation_id",
    "created_at",
    "entities",
    "in_reply_to_user_id",
    "note_tweet",
    "public_metrics",
    "referenced_tweets",
    "paid_partnership",
  ],
  expansions: [
    "author_id",
    "attachments.media_keys",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
    "referenced_tweets.id.attachments.media_keys",
    "in_reply_to_user_id",
  ],
  "media.fields": ["type", "url", "preview_image_url", "duration_ms", "variants", "alt_text"],
  "user.fields": ["name", "username"],
};
