import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import csv
import shutil
from tracker import set_post_approval, clear_post

print("Script started!")

TRACKER_FILE = "article_tracker.csv"
PLATFORMS = ["twitter", "linkedin", "mastodon", "bluesky", "facebook"]  # Update this as needed
LOCAL_ROOT = "post_outputs"
BIN_ROOT = "bin"

def get_unique_path(dest_folder, filename):
    # Only use the basename for the bin (so bin/twitter/twitter_xxx.txt, not bin/twitter/twitter/twitter_xxx.txt)
    base_filename = os.path.basename(filename)
    base, ext = os.path.splitext(base_filename)
    counter = 1
    candidate = os.path.join(dest_folder, base_filename)
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base}_{counter}{ext}")
        counter += 1
    return candidate


def ensure_bin_folder(platform):
    folder = os.path.join(BIN_ROOT, platform)
    os.makedirs(folder, exist_ok=True)
    return folder

print(f"About to open tracker file: {TRACKER_FILE}")
# STEP 1: Interactive CLI approval (bottom-up)
with open(TRACKER_FILE, "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

quit_flag = False

for row in reversed(rows):
    url = row["url"]
    for platform in PLATFORMS:
        post_file = row.get(f"{platform}_post", "").strip()
        approved = row.get(f"{platform}_approved", "").strip().upper() == "TRUE"
        uploaded = row.get(f"{platform}_uploaded", "").strip().upper() == "TRUE"
        if post_file and not approved and not uploaded:
            local_path = os.path.join(LOCAL_ROOT, post_file)
            print(f"\nArticle: {url}")
            print(f"  Platform: {platform}")
            if os.path.exists(local_path):
                print(f"Opening: {local_path}")
                with open(local_path, encoding="utf-8") as f:
                    content = f.read().strip()
                print(f"  Content: {content}")
            else:
                print(f"  Content: [File not found: {local_path}]")
            print("Approve, Deny, Skip, or Quit? [a/d/s/q]:")
            action = input().strip().lower()

            if action == "a":
                set_post_approval(url, platform, True, tracker_file=TRACKER_FILE)
                print("  Approved.")
            
            elif action == "d":
                bin_folder = ensure_bin_folder(platform)
                if os.path.exists(local_path):
                    dest_path = get_unique_path(bin_folder, post_file)
                    shutil.move(local_path, dest_path)
                    print(f"  Denied and moved to {dest_path}")
                else:
                    print(f"  Warning: file not found to deny: {local_path}")
                clear_post(url, platform, tracker_file=TRACKER_FILE)

            elif action == "q":
                print("  Quitting approval loop.")
                quit_flag = True
                break
            else:
                print("  Skipped.")
    if quit_flag:
        break

print("\nAll done! Approved posts are marked, denied posts are binned, tracker updated.")
