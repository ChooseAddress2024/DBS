import feedparser
from datetime import datetime, timedelta
import pandas as pd
from newspaper import Article
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time

# === Setup headless browser for fallback ===
def setup_browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# === Resolve actual article URL (requests first, fallback to selenium) ===
def resolve_actual_url(rss_url, browser=None):
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        )
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=10, allow_redirects=True)
        if response.url and "news.google.com" not in response.url:
            return response.url
    except Exception:
        print(f"[requests] Failed to resolve {rss_url}, falling back to Selenium.")

    if browser:
        try:
            browser.get(rss_url)
            time.sleep(2)
            return browser.current_url
        except WebDriverException:
            print(f"[selenium] Failed to resolve {rss_url}")
    return rss_url

# === Extract article content using newspaper3k ===
def get_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception:
        print(f"Failed to extract article from {url}")
        return ""

# === Main scraper ===
def scrape_financial_crime_news():
    query = "financial crime"
    rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"

    feed = feedparser.parse(rss_url)
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=30)

    browser = setup_browser()
    articles = []

    for entry in feed.entries:
        # Skip if missing timestamp
        published_parsed = entry.get('published_parsed')
        if not published_parsed:
            continue

        published_date = datetime(*published_parsed[:6])
        if published_date < one_day_ago:
            continue

        title = entry.get('title', '')
        rss_link = entry.get('link', '')

        # Try to resolve actual article URL
        actual_url = resolve_actual_url(rss_link, browser)

        # Get full article content
        contents = get_article_text(actual_url)
        if not contents:
            contents = entry.get('summary', '')

        articles.append({
            "title": title,
            "contents": contents,
            "published_date": published_date.isoformat(),
            "url": actual_url
        })

        time.sleep(0.5)  # polite delay

    browser.quit()
    df = pd.DataFrame(articles)
    return df

# === Run and save output ===
if __name__ == "__main__":
    df = scrape_financial_crime_news()
    print(df.head())
    df.to_csv("D:\\Interview_Prep\\DBS\\financial_crime_news_last_day.csv", index=False)