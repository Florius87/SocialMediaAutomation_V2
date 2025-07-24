# crawler.py

import requests
from bs4 import BeautifulSoup
from tracker import init_tracker
from config import load_config

cfg = load_config()
SITEMAP_URL = cfg.get("SITEMAP_URL")
if not SITEMAP_URL:
    raise ValueError("SITEMAP_URL not set in config.txt")

TRACKER_FILE = "article_tracker.csv"

def get_article_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    soup = BeautifulSoup(response.content, "xml")
    # Only collect <loc> tags that point to real posts, not media files
    urls = []
    for loc in soup.find_all("loc"):
        url = loc.text.strip()
        # Filter out media/image files
        if "/wp-content/" in url:
            continue
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.pdf', '.mp4', '.zip')):
            continue
        urls.append(url)
    return urls

if __name__ == "__main__":
    print(f"Downloading and parsing sitemap: {SITEMAP_URL}")
    urls = get_article_urls_from_sitemap(SITEMAP_URL)
    print(f"Found {len(urls)} article URLs.")

    # Write or update the tracker CSV
    init_tracker(urls, TRACKER_FILE)
    print(f"Tracker file '{TRACKER_FILE}' updated.")
