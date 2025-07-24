# 📰 Automated Social Media Poster for Articles & Figures

This Python-based automation toolkit streamlines content distribution by generating, approving, and posting social media content across platforms like Twitter, Mastodon, Bluesky, LinkedIn, Facebook, and Pinterest. It supports both article-based posts and image-based Pinterest pins.

## 🔧 Features

- **Website Crawling**: Parses your sitemap to collect all article URLs.
- **Content Extraction**: Extracts title, metadata, and main content using BeautifulSoup.
- **AI-Generated Posts**: Uses a GPT-based API to generate posts for each platform with platform-specific formatting.
- **Post Approval Interface**: CLI and PyQt GUI for manual approval or rejection.
- **Automatic Uploading**: Sends approved posts via relevant APIs (Twitter, Mastodon, Bluesky, Pinterest).
- **Pinterest Support**: Includes image-based Pinterest post generation using AI.
- **Tracker System**: Maintains CSV-based logs for tracking what’s posted, approved, or pending.

## 🗂️ Folder Structure
.
├── Approve.py                  # CLI for approving article-based posts
├── FigureApprove.py            # CLI approval for Pinterest pins
├── FigureParsing.py            # Parses images and links them to articles
├── FigureSend.py               # Posts approved Pinterest pins
├── FigureTracker.py            # Tracker for Pinterest-related data
├── Figure_prep.py              # Generates Pinterest captions via AI
├── GUI.py                      # PyQt5 GUI for full workflow control
├── PinterestTokenGenerator.py  # Pinterest token exchange tool
├── apiclient.py                # GPT API wrapper
├── config.py                   # Loads API keys and platform list from config.txt
├── crawler.py                  # Sitemap crawler for article URLs
├── main.py                     # Generates social media posts
├── send.py                     # Uploads approved posts to social platforms
├── socialmedia.py              # Platform-specific prompt templates
├── tracker.py                  # Manages article tracker CSV
├── webparsing.py               # Extracts content from web pages
├── figure_input.txt            # Input list of image URLs with optional article links/captions
├── config.txt                  # (User-provided) API keys and platform list
├── post_outputs/               # Generated social post files
└── bin/                        # Stores denied posts



## ⚙️ Setup

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt

    Create a config.txt file:
    Example:

SITEMAP_URL=https://florisera.com/sitemap.xml
API_URL=https://your-api-endpoint.com
API_KEY=your_api_key_here
PLATFORMS=twitter,linkedin,mastodon,bluesky,facebook

TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TWITTER_ACCESS_TOKEN=...
TWITTER_ACCESS_SECRET=...

MASTODON_ACCESS_TOKEN=...
MASTODON_API_BASE_URL=https://your.instance

BLUESKY_HANDLE=...
BLUESKY_APP_PASSWORD=...

PINTEREST_CLIENT_ID=...
PINTEREST_CLIENT_SECRET=...
PINTEREST_CODE=...       # Acquired via OAuth flow
PINTEREST_ACCESS_TOKEN=...
PINTEREST_BOARD_ID=...

Run the GUI (recommended):

    python GUI.py

💡 Workflow Summary
Article Posts

    crawler.py → populates article_tracker.csv

    main.py → generates posts using GPT

    Approve.py or GUI → approve/deny each post

    send.py twitter (or platform name) → uploads to social media

Pinterest (Image) Posts

    Place URLs in figure_input.txt

    FigureParsing.py → parses and links figures

    Figure_prep.py → AI descriptions + Pinterest captions

    FigureApprove.py or GUI → approve pins

    FigureSend.py → uploads pins to Pinterest

✅ Example Commands

# Crawl sitemap and initialize tracker
python crawler.py

# Generate 3 new posts
python main.py 3

# Approve posts via CLI
python Approve.py

# Upload to Twitter
python send.py twitter

# Parse figure metadata
python FigureParsing.py

# Generate Pinterest descriptions
python Figure_prep.py

# Approve pins
python FigureApprove.py

# Send pins
python FigureSend.py

🛠 Requirements

    Python 3.7+

    requests, beautifulsoup4, tweepy, mastodon.py, atproto, PyQt5, Pillow

📌 Notes

    All state is tracked in article_tracker.csv and figure_tracker.csv.

    Posts are stored in post_outputs/<platform> and marked once uploaded.

    Denied content is moved to the bin/ folder for review or reuse.

Author: [Your Name]
Website: https://florisera.com


Let me know if you want to split this into multiple files (e.g., `README.md` and `INSTALL.md`) or if y
