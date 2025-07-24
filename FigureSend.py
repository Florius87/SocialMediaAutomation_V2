import os
import requests
from FigureTracker import load_figure_tracker, save_figure_tracker
from config import load_config

cfg = load_config()
TRACKER_FILE = "figure_tracker.csv"
OUTPUT_DIR = "post_outputs/pinterest"
PINTEREST_ACCESS_TOKEN = cfg.get("PINTEREST_ACCESS_TOKEN")  # Set this in your config.txt!
BOARD_ID = cfg.get("PINTEREST_BOARD_ID")  # Set this in your config.txt!
API_URL = 'https://api.pinterest.com/v5/pins'


def post_pinterest_pin(image_url, link, title, description):
    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "board_id": BOARD_ID,
        "title": title[:100],  # Pinterest Pin title max is 100 chars
        "alt_text": description[:400],  # Alt text (optional, max 400)
        "description": description[:800],  # Pin description max is 800 chars
        "link": link,  # URL to your article
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    resp = requests.post(API_URL, json=payload, headers=headers)
    try:
        resp.raise_for_status()
        print("✅ Pin posted successfully!")
        return resp.json()
    except Exception as e:
        print("❌ Failed to post pin:", resp.text)
        return None

def main():
    rows = load_figure_tracker(TRACKER_FILE)
    changed = False
    SEND_LIMIT = 5  # Set your desired number of posts per run here
    sent_count = 0
    for row in rows:
        if sent_count >= SEND_LIMIT:
            break
        post_file = row.get("pinterest_post", "").strip()
        approved = row.get("pinterest_approved", "").strip().upper() == "TRUE"
        uploaded = row.get("pinterest_uploaded", "").strip().upper() == "TRUE"
        if not post_file or not approved or uploaded:
            continue
        post_path = os.path.join(OUTPUT_DIR, post_file)
        if not os.path.exists(post_path):
            print(f"⚠️ Pinterest post file not found: {post_path}")
            continue
        with open(post_path, encoding="utf-8") as f:
            description = f.read().strip()
        image_url = row.get("image_url", "")
        link = row.get("article_url", "")
        title = row.get("article_title", "") or (description[:80] if description else "Pin")
        resp = post_pinterest_pin(image_url, link, title, description)
        if resp:
            row["pinterest_uploaded"] = "TRUE"
            changed = True
            sent_count += 1
        else:
            print(f"❌ Failed to post for image {image_url}")
            break  # Optional: still stop on error

    if changed:
        save_figure_tracker(rows, TRACKER_FILE)
        print(f"Tracker updated: uploaded {sent_count} pin(s) marked.")
    else:
        print("No new pins sent.")


if __name__ == "__main__":
    main()
