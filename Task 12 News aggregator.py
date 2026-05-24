import requests
import json
import csv
import os
import xml.etree.ElementTree as ET

# --- CONFIG ---
with open("config.json", "r") as f:
    config = json.load(f)
API_KEY = config["api_key"]

BASE_URL = "https://newsapi.org/v2/top-headlines"
SEARCH_URL = "https://newsapi.org/v2/everything"
# Second Source: BBC RSS Feed (Public endpoint, no API key required)
RSS_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"

HISTORY_FILE = "saved_news.csv"
BOOKMARK_FILE = "bookmarks.json"
CATEGORIES = ["technology", "sports", "business", "entertainment"]


# --- FETCH FROM RSS (SOURCE 2) ---
def fetch_rss_news():
    try:
        res = requests.get(RSS_URL, timeout=10)
        if res.status_code != 200:
            return []

        root = ET.fromstring(res.content)
        rss_articles = []

        # Parse XML structure to extract top 5 news items
        for item in root.findall(".//item")[:5]:
            title = item.find("title").text if item.find("title") is not None else ""
            desc = item.find("description").text if item.find("description") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            url = item.find("link").text if item.find("link") is not None else ""

            rss_articles.append({
                "title": title,
                "source": {"name": "BBC RSS Feed"},
                "publishedAt": pub_date[:16],  # Standardizing date format substring
                "description": desc,
                "url": url
            })
        return rss_articles
    except Exception:
        return []  # Return empty list if RSS feed parsing fails


# --- FETCH NEWS (MAIN FUNCTION) ---
def fetch_news(category=None, keyword=None):
    articles = []

    # 1. Fetch data from NewsAPI primary source
    if keyword:
        params = {"q": keyword, "apiKey": API_KEY, "pageSize": 5, "language": "en"}
        url = SEARCH_URL
    else:
        params = {"apiKey": API_KEY, "pageSize": 5, "language": "en", "country": "us"}
        if category:
            params["category"] = category
        url = BASE_URL

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if data.get("status") == "ok":
            articles.extend(data.get("articles", []))
    except requests.exceptions.ConnectionError:
        print("  No internet connection!")
        return []
    except Exception as e:
        print(f"  NewsAPI Error: {e}")

    # 2. Fetch data from RSS Feed secondary source (Multi-Source Integration)
    # Generic RSS news is appended only when no specific keyword or category is requested
    if not keyword and not category:
        rss_data = fetch_rss_news()
        articles.extend(rss_data)

    # De-duplicate incoming articles based on unique titles
    seen = set()
    unique = []
    for a in articles:
        title = a.get("title", "")
        if title and title not in seen:
            seen.add(title)
            unique.append(a)

    return unique


# --- DISPLAY ARTICLES ---
def display_articles(articles):
    if not articles:
        print("\n  No articles found.\n")
        return
    print("\n" + "=" * 60)
    for i, a in enumerate(articles, 1):
        title = a.get("title") or "No Title"
        source = a.get("source", {}).get("name") or "Unknown"
        pub_date = a.get("publishedAt", "")[:10]
        desc = a.get("description") or "No description available."

        # Enforce short descriptions layout constraint
        if len(desc) > 120:
            desc = desc[:120] + "..."
        print(f"\n  [{i}] {title}")
        print(f"      Source : {source}")
        print(f"      Date   : {pub_date}")
        print(f"      Info   : {desc}")
    print("\n" + "=" * 60)


# --- SAVE TO CSV ---
def save_to_csv(articles):
    if not articles:
        print("  Nothing to save.")
        return
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "source", "date", "description", "url"])
        if not file_exists:
            writer.writeheader()
        for a in articles:
            writer.writerow({
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
                "date": a.get("publishedAt", "")[:10],
                "description": a.get("description", ""),
                "url": a.get("url", "")
            })
    print(f"  Saved {len(articles)} articles to {HISTORY_FILE}")


# --- BOOKMARK ---
def load_bookmarks():
    if os.path.isfile(BOOKMARK_FILE):
        with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_bookmarks(bookmarks):
    with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)


def add_bookmark(articles):
    try:
        choice = int(input("  Enter article number to bookmark: ")) - 1
        if 0 <= choice < len(articles):
            bookmarks = load_bookmarks()
            article = articles[choice]
            titles = [b.get("title") for b in bookmarks]
            if article.get("title") in titles:
                print("  Already bookmarked!")
            else:
                bookmarks.append(article)
                save_bookmarks(bookmarks)
                print("  Bookmarked!")
        else:
            print("  Invalid number.")
    except ValueError:
        print("  Enter a valid number.")


def view_bookmarks():
    bookmarks = load_bookmarks()
    if not bookmarks:
        print("\n  No bookmarks saved yet.")
        return
    print("\n  --- YOUR BOOKMARKS ---")
    display_articles(bookmarks)


# --- BASIC SUMMARIZER ---
def summarize_headlines(articles):
    if not articles:
        print("  No articles to summarize.")
        return
    print("\n  --- QUICK HEADLINES ---")
    for i, a in enumerate(articles, 1):
        print(f"  {i}. {a.get('title', 'No Title')}")
    print()


# --- MENU ---
def show_menu():
    print("\n" + "=" * 60)
    print("        MULTI-SOURCE NEWS AGGREGATOR")
    print("=" * 60)
    print("  1. View Latest News (All Sources)")
    print("  2. Search News by Keyword")
    print("  3. Browse by Category")
    print("  4. View Bookmarks")
    print("  5. Exit")
    print("=" * 60)


def category_menu():
    print("\n  Select Category:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i}. {cat.capitalize()}")
    try:
        pick = int(input("  Enter number: ")) - 1
        if 0 <= pick < len(CATEGORIES):
            return CATEGORIES[pick]
        else:
            print("  Invalid choice.")
            return None
    except ValueError:
        print("  Enter a valid number.")
        return None


# --- MAIN LOOP ---
def main():
    print("\n  Fetching news... checking API & RSS feeds...")
    while True:
        show_menu()
        choice = input("  Your choice: ").strip()

        if choice == "1":
            articles = fetch_news()
            display_articles(articles)

            action = input("  Save to CSV? (y/n): ").strip().lower()
            if action == "y":
                save_to_csv(articles)
            action2 = input("  Bookmark an article? (y/n): ").strip().lower()
            if action2 == "y":
                add_bookmark(articles)
            action3 = input("  Show quick summary? (y/n): ").strip().lower()
            if action3 == "y":
                summarize_headlines(articles)

        elif choice == "2":
            keyword = input("  Enter keyword to search: ").strip()
            if keyword:
                articles = fetch_news(keyword=keyword)
                display_articles(articles)
                action = input("  Save to CSV? (y/n): ").strip().lower()
                if action == "y":
                    save_to_csv(articles)
            else:
                print("  Keyword cannot be empty.")

        elif choice == "3":
            cat = category_menu()
            if cat:
                articles = fetch_news(category=cat)
                display_articles(articles)
                action = input("  Save to CSV? (y/n): ").strip().lower()
                if action == "y":
                    save_to_csv(articles)

        elif choice == "4":
            view_bookmarks()

        elif choice == "5":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid option. Choose 1-5.")


if __name__ == "__main__":
    main()