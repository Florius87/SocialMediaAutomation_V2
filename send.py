import os
import csv
import re
from tracker import mark_post_uploaded  # you must have this function
from config import load_config
cfg = load_config()
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')


TRACKER_FILE = "article_tracker.csv"
LOCAL_ROOT = "post_outputs"

# Platform detection (default: twitter)
if len(sys.argv) > 1:
    PLATFORM = sys.argv[1].lower()
else:
    PLATFORM = "twitter"

TWEET_CHAR_LIMIT = 280
TCO_URL_LENGTH = 23
MASTODON_CHAR_LIMIT = 500  # Default, but some servers have custom limits
BLUESKY_CHAR_LIMIT = 300

# --- Twitter API Setup ---
def tweet_length_with_urls(text):
    url_regex = r"https?://\S+"
    urls = re.findall(url_regex, text)
    len_without_urls = len(re.sub(url_regex, '', text))
    return len_without_urls + len(urls) * TCO_URL_LENGTH

def post_tweet(text: str):
    import tweepy
    TWITTER_API_KEY = cfg.get("TWITTER_API_KEY")
    TWITTER_API_SECRET = cfg.get("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN = cfg.get("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_SECRET = cfg.get("TWITTER_ACCESS_SECRET")

    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET
    )
    response = client.create_tweet(text=text)
    tweet_id = response.data.get("id")
    print(f"✅ Tweet posted! https://x.com/i/web/status/{tweet_id}")
    return tweet_id

# --- Mastodon API Setup ---
def post_mastodon(text: str):
    from mastodon import Mastodon
    MASTODON_ACCESS_TOKEN = cfg.get("MASTODON_ACCESS_TOKEN")
    MASTODON_API_BASE_URL = cfg.get("MASTODON_API_BASE_URL")
    mastodon = Mastodon(
        access_token=MASTODON_ACCESS_TOKEN,
        api_base_url=MASTODON_API_BASE_URL
    )
    status = mastodon.status_post(text)
    print(f"✅ Mastodon post sent! URL: {status['url']}")
    return status

# --- Bluesky API Setup ---
def post_bluesky(text: str):
    from atproto import Client
    BLUESKY_HANDLE = cfg.get("BLUESKY_HANDLE")
    BLUESKY_APP_PASSWORD = cfg.get("BLUESKY_APP_PASSWORD")
    client = Client()
    client.login(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)
    post = client.send_post(text)
    try:
        post_id = post['uri'].split('/')[-1]
        if BLUESKY_HANDLE:
            web_url = f"https://bsky.app/profile/{BLUESKY_HANDLE}/post/{post_id}"
            print(f"✅ Bluesky post sent! URL: {web_url}")
        else:
            print("✅ Bluesky post sent!")
    except Exception as e:
        print(f"✅ Bluesky post sent, but couldn't generate web URL: {e}")
    return post



def main():
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for row in reversed(rows):
        approved = row.get(f"{PLATFORM}_approved", "").strip().upper() == "TRUE"
        uploaded = row.get(f"{PLATFORM}_uploaded", "").strip().upper() == "TRUE"
        post_file = row.get(f"{PLATFORM}_post", "").strip()
        url = row.get("url", "")

        if approved and not uploaded and post_file:
            file_path = os.path.join(LOCAL_ROOT, post_file)
            if not os.path.exists(file_path):
                print(f"⚠️ Skipping: file not found: {file_path}")
                continue

            with open(file_path, encoding="utf-8") as pf:
                post_text = pf.read().strip()

            print(f"\nAbout to send {PLATFORM} post for: {url}\n---\n{post_text}\n---")
            try:
                if PLATFORM == "twitter":
                    tweet_len = tweet_length_with_urls(post_text)
                    if tweet_len > TWEET_CHAR_LIMIT:
                        print(f"❌ Tweet too long ({tweet_len} chars, limit {TWEET_CHAR_LIMIT}). Skipping.")
                        continue
                    post_tweet(post_text)
                elif PLATFORM == "mastodon":
                    if len(post_text) > MASTODON_CHAR_LIMIT:
                        print(f"❌ Mastodon post too long ({len(post_text)} chars, limit {MASTODON_CHAR_LIMIT}). Skipping.")
                        continue
                    post_mastodon(post_text)
                elif PLATFORM == "bluesky":
                    if len(post_text) > BLUESKY_CHAR_LIMIT:
                        print(f"❌ Bluesky post too long ({len(post_text)} chars, limit {BLUESKY_CHAR_LIMIT}). Skipping.")
                        continue
                    post_bluesky(post_text)
                else:
                    print(f"❌ Platform '{PLATFORM}' not supported yet.")
                    continue

                mark_post_uploaded(url, PLATFORM, tracker_file=TRACKER_FILE)
                print("Marked as uploaded in tracker.")

            except Exception as e:
                print(f"❌ Failed to post: {e}")
            break  # Only one post per run

    else:
        print(f"No approved, pending {PLATFORM} posts found.")

if __name__ == "__main__":
    main()
