This project automates the process of generating, reviewing, and uploading social media posts for articles and images (figures) from your website. Posts are generated using GPT models and pushed to platforms like Twitter, LinkedIn, Mastodon, Bluesky, Facebook, and Pinterest.

---

## 🚀 Features

- **Article Support**  
  - Crawl your sitemap for article URLs  
  - Extract and format article content  
  - Generate social media posts using GPT  
  - Approve or deny posts via GUI or CLI  
  - Auto-upload to supported platforms  

- **Figure Support (Pinterest)**  
  - Read image URLs and match to articles  
  - Generate AI-based image descriptions  
  - Create Pinterest-optimized post text  
  - Approve pins and upload via Pinterest API  

- **Workflow GUI**  
  - PyQt-based desktop app to manage everything  
  - Inline image preview and approval buttons  
  - Platform-specific posting controls  

---

## 📁 Project Structure

- **Approve.py** – CLI for approving article-based posts  
- **FigureApprove.py** – CLI approval for Pinterest pins  
- **FigureParsing.py** – Parses images and links them to articles  
- **FigureSend.py** – Posts approved Pinterest pins  
- **FigureTracker.py** – Tracker for Pinterest-related data  
- **Figure_prep.py** – Generates Pinterest captions via AI  
- **GUI.py** – PyQt5 GUI for full workflow control  
- **PinterestTokenGenerator.py** – Pinterest token exchange tool  
- **apiclient.py** – GPT API wrapper  
- **config.py** – Loads API keys and platform list from config.txt  
- **crawler.py** – Sitemap crawler for article URLs  
- **main.py** – Generates social media posts  
- **send.py** – Uploads approved posts to social platforms  
- **socialmedia.py** – Platform-specific prompt templates  
- **tracker.py** – Manages article tracker CSV  
- **webparsing.py** – Extracts content from web pages  
- **figure_input.txt** – Input list of image URLs and captions  
- **config.txt** – API credentials and platform settings (user-provided)  
- **post_outputs/** – Folder for generated post files per platform  
- **bin/** – Folder for denied or discarded post files  

---

## ⚙️ Setup

1. **Install requirements**  
   Create a `requirements.txt` with these:
   ```txt
   requests
   beautifulsoup4
   PyQt5
   Pillow
   tweepy
   mastodon.py
   atproto

Then install:

Always show details

pip install -r requirements.txt

    Prepare your config.txt
    Example:

Always show details

    SITEMAP_URL=https://florisera.com/sitemap.xml
    API_URL=https://your-openai-endpoint
    API_KEY=your_openai_api_key
    PLATFORMS=twitter,linkedin,mastodon,bluesky,facebook

    TWITTER_API_KEY=...
    TWITTER_API_SECRET=...
    TWITTER_ACCESS_TOKEN=...
    TWITTER_ACCESS_SECRET=...

    MASTODON_ACCESS_TOKEN=...
    MASTODON_API_BASE_URL=https://your.instance

    BLUESKY_HANDLE=yourname.bsky.social
    BLUESKY_APP_PASSWORD=your_bluesky_password

    PINTEREST_CLIENT_ID=...
    PINTEREST_CLIENT_SECRET=...
    PINTEREST_CODE=...       # Get via OAuth
    PINTEREST_ACCESS_TOKEN=...
    PINTEREST_BOARD_ID=...

🧠 Workflow
📰 Article Posts

Always show details

# Crawl your site and extract article URLs
python crawler.py

# Generate social posts for articles
python main.py 3

# Review and approve posts
python Approve.py

# Upload to Twitter (or others)
python send.py twitter

🖼️ Pinterest (Image Posts)

Always show details

# Add images to figure_input.txt
# Format: image_url, article_url, caption

# Parse and match images to articles
python FigureParsing.py

# Generate AI descriptions and pin captions
python Figure_prep.py

# Approve via CLI
python FigureApprove.py

# Upload to Pinterest
python FigureSend.py

🖥 GUI Mode (Recommended)

Always show details

python GUI.py

✅ Notes

    All data is tracked in article_tracker.csv and figure_tracker.csv

    Each platform has character-specific post prompts

    Posts are only uploaded after manual approval

    GPT calls can be routed to OpenAI, Azure, etc.

📜 License

MIT License — feel free to modify and adapt.
✍️ Author

Built by Florisera.com
For developers automating social outreach from their own content.
"""
Save the file

readme_path = "/mnt/data/README.md"
with open(readme_path, "w", encoding="utf-8") as f:
f.write(readme_content)

readme_path

Always show details
