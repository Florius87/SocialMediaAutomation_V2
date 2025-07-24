from webparsing import extract_page_data
from FigureTracker import load_figure_tracker, save_figure_tracker
import requests
from PIL import Image
from io import BytesIO



INPUT_TXT = "figure_input.txt"
TRACKER_CSV = "figure_tracker.csv"
ARTICLE_TRACKER_CSV = "article_tracker.csv"

def read_input_txt(filename):
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.strip().split(",", 2)]
            while len(parts) < 3:
                parts.append("")
            yield dict(image_url=parts[0], article_url=parts[1], caption=parts[2])

def get_article_urls(tracker_csv):
    import csv, os
    if not os.path.exists(tracker_csv): return []
    with open(tracker_csv, encoding="utf-8") as f:
        return [r["url"].strip() for r in csv.DictReader(f) if r.get("url")]

def find_article(image_url, article_urls):
    for url in article_urls:
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok and image_url in resp.text:
                return url
        except Exception: pass
    return ""

def get_image_info(image_url):
    try:
        img = Image.open(BytesIO(requests.get(image_url, timeout=10).content))
        return dict(width=img.width, height=img.height, format=img.format)
    except Exception: return dict(width="", height="", format="")

def main():
    tracker = { (row.get("image_url"), row.get("article_url")): row for row in load_figure_tracker() }
    article_urls = get_article_urls(ARTICLE_TRACKER_CSV)
    updated = []

    for entry in read_input_txt(INPUT_TXT):
        img, art, cap = entry["image_url"], entry["article_url"], entry["caption"]
        if not img: continue
        # Find parsed tracker row for this image
        parsed_row = next((row for key, row in tracker.items() if key[0] == img and row.get("parsed") == "TRUE"), None)
        if parsed_row:
            updated.append(parsed_row)
            continue
        # Build or update row
        row = next((row for key, row in tracker.items() if key[0] == img), {})  # first matching tracker row
        row["image_url"] = img
        row["caption"] = cap or row.get("caption", "")
        # Article URL: prefer input, then tracker, then lookup
        row["article_url"] = art or row.get("article_url", "") or find_article(img, article_urls)
        if not row["article_url"]:
            print(f"Skipping: No article URL for {img}")
            continue
        # Image info
        for k, v in get_image_info(img).items():
            row[k] = row.get(k) or v
        # Article info
        if not row.get("article_title") or not row.get("meta_description"):
            artinfo = extract_page_data(row["article_url"]) or {}
            row["article_title"] = row.get("article_title", "") or artinfo.get("title", "")
            row["meta_description"] = row.get("meta_description", "") or artinfo.get("meta_description", "")
        # Parsed flag
        row["parsed"] = "TRUE" if all(row.get(f) for f in ("width", "height", "format", "article_url", "article_title")) else ""
        updated.append(row)

    # Add any tracker rows not in updated
    updated_keys = set((row.get("image_url"), row.get("article_url")) for row in updated)
    for key, row in tracker.items():
        if key not in updated_keys:
            updated.append(row)
    save_figure_tracker(updated)
    #print("Done. Updated tracker with", len(updated), "figures.")

if __name__ == "__main__":
    main()
