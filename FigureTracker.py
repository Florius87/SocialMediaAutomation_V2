import csv
import os

TRACKER_FILE = "figure_tracker.csv"

FIGURE_FIELDNAMES = [
    "image_url",
    "article_url",
    "article_title",
    "meta_description",
    "caption",
    "width",
    "height",
    "format",
    "ai_description",
    "pinterest_post",
    "pinterest_approved",
    "pinterest_uploaded",
    "parsed"
]

def load_figure_tracker(tracker_file=TRACKER_FILE):
    if not os.path.exists(tracker_file):
        return []
    with open(tracker_file, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_figure_tracker(rows, tracker_file=TRACKER_FILE):
    # Fill missing fields for each row
    for row in rows:
        for f in FIGURE_FIELDNAMES:
            if f not in row:
                row[f] = ""
    with open(tracker_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIGURE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
