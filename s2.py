import feedparser
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

# Configuration
RSS_URL = "https://news.google.com/rss/search?q=financial+crime&hl=en-US&gl=US&ceid=US:en"
OUTPUT_FILE = "D:\\Interview_Prep\\DBS\\google_financial_news.json"

def fetch_article_content(url):
    """
    Fetch the full text content of an article from its URL
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text from paragraphs (most common content container)
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs])
        
        # If no paragraphs found, try getting the main content
        if not text:
            # Try common content containers
            for container in ['article', 'main', '.content', '#content', '.article-body']:
                content = soup.select(container)
                if content:
                    text = content[0].get_text().strip()
                    break
        
        # If still no text, get the body text
        if not text:
            text = soup.body.get_text().strip()
            
        # Clean up the text
        text = ' '.join(text.split())
        return text if text else "Failed to extract article content"
        
    except Exception as e:
        return f"Error fetching article content: {str(e)}"

def fetch_google_news_rss():
    """
    Fetch and parse financial news from Google News RSS feed
    Returns a list of formatted articles
    """
    articles = []
    
    try:
        # Parse the RSS feed
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            print("No articles found in the feed")
            return articles
        
        # Process each entry
        for i, entry in enumerate(feed.entries):
            print(f"Processing article {i+1}/{len(feed.entries)}: {entry.get('title', 'No title')}")
            
            article_url = entry.get("link", "")
            full_text = ""
            
            if article_url:
                print(f"Fetching full text from: {article_url}")
                full_text = fetch_article_content(article_url)
                # Be nice to the servers - add a delay between requests
                time.sleep(2)
            
            formatted_article = {
                "title": entry.get("title", "No title available"),
                "summary": entry.get("description", "No summary available"),
                "publish_date": entry.get("published", str(datetime.now().date())),
                "source": article_url
            }
            articles.append(formatted_article)
            
    except Exception as e:
        print(f"Error fetching RSS feed: {str(e)}")
        
    return articles
