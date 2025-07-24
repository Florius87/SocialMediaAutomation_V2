import sys
import os
import csv
import shutil
from FigureTracker import load_figure_tracker, save_figure_tracker, FIGURE_FIELDNAMES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

TRACKER_FILE = "figure_tracker.csv"
LOCAL_ROOT = "post_outputs/pinterest"
BIN_ROOT = "bin/pinterest"

def get_unique_path(dest_folder, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    candidate = os.path.join(dest_folder, filename)
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base}_{counter}{ext}")
        counter += 1
    return candidate

os.makedirs(BIN_ROOT, exist_ok=True)

rows = load_figure_tracker(TRACKER_FILE)
changed = False
quit_flag = False

for row in reversed(rows):
    post_file = row.get("pinterest_post", "").strip()
    approved = row.get("pinterest_approved", "").strip().upper() == "TRUE"
    uploaded = row.get("pinterest_uploaded", "").strip().upper() == "TRUE"
    if post_file and not approved and not uploaded:
        local_path = os.path.join(LOCAL_ROOT, post_file)
        print(f"\nImage: {row.get('image_url', '')}")
        print(f"Article: {row.get('article_url', '')}")
        print(f"Post file: {local_path}")
        if os.path.exists(local_path):
            with open(local_path, encoding="utf-8") as f:
                content = f.read().strip()
            print(f"  Content: {content}")
        else:
            print(f"  Content: [File not found: {local_path}]")
        print("Approve, Deny, Skip, or Quit? [a/d/s/q]:")
        action = input().strip().lower()

        if action == "a":
            row["pinterest_approved"] = "TRUE"
            changed = True
            print("  Approved.")

        elif action == "d":
            if os.path.exists(local_path):
                dest_path = get_unique_path(BIN_ROOT, post_file)
                shutil.move(local_path, dest_path)
                print(f"  Denied and moved to {dest_path}")
            else:
                print(f"  Warning: file not found to deny: {local_path}")
            row["pinterest_post"] = ""
            row["pinterest_approved"] = ""
            changed = True

        elif action == "q":
            print("  Quitting approval loop.")
            quit_flag = True
            break
        else:
            print("  Skipped.")
    if quit_flag:
        break

if changed:
    save_figure_tracker(rows, TRACKER_FILE)
    print("\nAll done! Approved posts are marked, denied posts are binned, tracker updated.")
else:
    print("No posts to approve or changes made.")
