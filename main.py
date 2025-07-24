from tracker import get_latest_incomplete_row, mark_post_generated, PLATFORMS
from webparsing import extract_page_data
from apiclient import ask_gpt
from socialmedia import get_social_prompt
import os
import sys

OUTPUT_DIR = "post_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Number of articles to process (default: 1, can override with CLI argument)
num_articles = 1
if len(sys.argv) > 1:
    try:
        num_articles = max(1, int(sys.argv[1]))
    except Exception:
        print("Invalid number argument, defaulting to 1.")

articles_processed = 0
while articles_processed < num_articles:
    row, missing_platforms = get_latest_incomplete_row(PLATFORMS)
    if not row:
        print("All posts for all platforms are done!")
        break

    url = row['url']
    print(f"\nProcessing: {url}")
    print(f"Missing for: {', '.join(missing_platforms)}")

    post_data = extract_page_data(url)
    if not post_data:
        print(f"Could not extract data from {url}")
        # Still count as processed so we don't loop forever on a bad row
        articles_processed += 1
        continue

    for platform in missing_platforms:
        prompt, temp = get_social_prompt(platform, post_data['main_text'])
        post_text = ask_gpt(prompt, temperature=temp)
        # Generate a simple filename for the post per platform/article
        # Safe for URLs with trailing /
        url_tail = os.path.basename(url.strip('/'))
        filename = f"{platform}_{url_tail}.txt"
        platform_dir = os.path.join(OUTPUT_DIR, platform)
        os.makedirs(platform_dir, exist_ok=True)
        filepath = os.path.join(platform_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(post_text + "\n" + url)

        mark_post_generated(url, platform, os.path.join(platform, filename))
        print(f"Generated {platform} post for: {url} and saved to {filepath}")

    articles_processed += 1

print(f"\nDone. Processed {articles_processed} article(s).")
