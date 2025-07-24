from FigureTracker import load_figure_tracker, save_figure_tracker, FIGURE_FIELDNAMES
from FigureAPI import ask_figure_api
from webparsing import extract_page_data
import os
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


OUTPUT_DIR = "post_outputs/pinterest"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_true(val):
    return (val or "").strip().lower() == "true"

def has_image_url(row):
    val = row.get("image_url")
    return isinstance(val, str) and val.strip() != ""

def get_main_text(article_url):
    data = extract_page_data(article_url)
    return data.get("main_text", "") if data else ""

def main():
    import time

    MAX_PER_PASS = 3  # default value
    if len(sys.argv) > 1:
        try:
            MAX_PER_PASS = max(1, int(sys.argv[1]))
        except Exception:
            print("Invalid number argument, using default MAX_PER_PASS = 3")
    rows = load_figure_tracker()
    print(f"Loaded {len(rows)} rows")
    changed = False

    # --- First pass: AI descriptions ---
    desc_needed_indices = [
        i for i, row in enumerate(rows)
        if is_true(row.get("parsed"))
        and not (row.get("ai_description") or "").strip()
        and has_image_url(row)
    ]
    if not desc_needed_indices:
        print("No rows need AI descriptions.")
    desc_to_process = desc_needed_indices[:MAX_PER_PASS] if desc_needed_indices else []

    for idx in desc_to_process:
        row = rows[idx]
        prompt = "Describe this image for a general audience. Be detailed, clear, and objective. Use up to 700 characters."
        t0 = time.time()
        desc = ask_figure_api(prompt, image_url=row.get("image_url"))
        elapsed = time.time() - t0
        if desc:
            row["ai_description"] = desc.strip()
            changed = True
            print(f"✅ AI description generated for image: {row['image_url']} ({elapsed:.1f}s)")
        else:
            print(f"⚠️ AI description generation failed for image: {row['image_url']}")

    # --- Second pass: Pinterest posts ---
    pin_needed_indices = [
        i for i, row in enumerate(rows)
        if is_true(row.get("parsed"))
        and (row.get("ai_description") or "").strip()
        and not (row.get("pinterest_post") or "").strip()
        and has_image_url(row)
    ]
    if not pin_needed_indices:
        print("No rows need Pinterest posts.")
    pin_to_process = pin_needed_indices[:MAX_PER_PASS] if pin_needed_indices else []

    for idx in pin_to_process:
        row = rows[idx]
        main_text = get_main_text(row.get("article_url", ""))
        pinterest_prompt = (
            "You are a Pinterest expert. Write a catchy Pinterest Pin description for this image, based on:\n\n"
            f"Image description: {row['ai_description']}\n\n"
            f"Article content: {main_text}\n\n"
            f"Caption: {row.get('caption', '')}\n\n"
            "Use up to 500 characters, encourage viewers to click through for more details."
        )
        t0 = time.time()
        result = ask_figure_api(pinterest_prompt)
        elapsed = time.time() - t0
        if result:
            base = os.path.splitext(os.path.basename(row["image_url"] or row["article_url"] or "pin"))[0]
            fname = f"pinterest_{base}.txt"
            fpath = os.path.join(OUTPUT_DIR, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(result.strip())
            row["pinterest_post"] = fname
            changed = True
            print(f"✅ Pinterest post created: {fname} ({elapsed:.1f}s)")
        else:
            print(f"⚠️ Pinterest post generation failed for image/article: {row.get('image_url') or row.get('article_url')}")

    if changed:
        for row in rows:
            for f in FIGURE_FIELDNAMES:
                if f not in row:
                    row[f] = ""
        save_figure_tracker(rows)
        print("AI descriptions and Pinterest posts updated.")
    else:
        print("No updates needed. All rows already have AI descriptions and Pinterest posts.")

    # Optionally: Warn about rows with missing image_url
    missing = [i for i, row in enumerate(rows) if not has_image_url(row)]
    if missing:
        print(f"⚠️ {len(missing)} row(s) missing image_url: {missing}")

if __name__ == "__main__":
    main()
