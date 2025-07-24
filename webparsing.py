import requests
from bs4 import BeautifulSoup
import re
import math

def estimate_reading_time(text, wpm=200):
    word_count = len(text.split())
    return f"{math.ceil(word_count / wpm)} min read"

def extract_page_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Title
    title = soup.title.string.strip() if soup.title and soup.title.string else ''

    # Meta description
    meta_description = ''
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag and meta_tag.get('content'):
        meta_description = meta_tag['content'].strip()

    # Author
    author = ''
    author_tag = soup.find('meta', attrs={'name': 'author'})
    if author_tag and author_tag.get('content'):
        author = author_tag['content'].strip()

    # Category
    category = ''
    cat_container = soup.find('span', class_='cat-links') or soup.find('div', class_='post-categories')
    if cat_container:
        cat_links = cat_container.find_all('a')
        if cat_links:
            category = cat_links[0].get_text(strip=True)

    # Tags
    tags = []
    tag_container = soup.find('span', class_='tags-links') or soup.find('div', class_='post-tags')
    if tag_container:
        tags = [a.get_text(strip=True) for a in tag_container.find_all('a')]

    # Main content with formatted headings
    article = soup.find('article') or soup.find('div', class_='entry-content') or soup.find('main')
    elements = article.find_all(['p', 'h1', 'h2', 'h3', 'li']) if article else []

    lines = []
    for elem in elements:
        tag = elem.name
        text = elem.get_text(strip=True)
        if tag in ['h1', 'h2']:
            lines.append(f"\n## {text}\n")
        elif tag == 'h3':
            lines.append(f"\n### {text}\n")
        else:
            lines.append(text)

    main_text = '\n'.join(lines)
    main_text = re.sub(r'\n{3,}', '\n\n', main_text).strip()

    return {
        'url': url,
        'title': title,
        'meta_description': meta_description,
        'author': author,
        'category': category,
        'tags': tags,
        'estimated_reading_time': estimate_reading_time(main_text),
        'main_text': main_text
    }

def print_post_data(data):
    print(f"URL:\n{data.get('url', '(none)')}\n")
    print(f"Title:\n{data.get('title', '(none)')}\n")
    print(f"Meta Description:\n{data.get('meta_description', '(none)')}\n")
    print(f"Author:\n{data.get('author', '(none)')}\n")
    print(f"Category:\n{data.get('category', '(none)')}\n")
    print(f"Tags:\n{', '.join(data.get('tags', [])) or '(none)'}\n")
    print(f"Estimated Reading Time:\n{data.get('estimated_reading_time', '(unknown)')}\n")
    print("Main Text:\n")
    print(data.get('main_text', '(no content)'))

# Optional test run
if __name__ == "__main__":
    test_url = "https://florisera.com/igbt-vs-mosfet-how-to-choose-the-right-power-switch/"
    data = extract_page_data(test_url)
    if data:
        print_post_data(data)
    else:
        print("Failed to extract data.")
