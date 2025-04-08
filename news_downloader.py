import newspaper
from datetime import datetime, timedelta
import os
import time

def download_articles(source_url, days_back=1):  # Change days_back to 1
    # Initialize newspaper source with more articles and longer timeout
    paper = newspaper.build(source_url, memoize_articles=False, 
                           number_threads=10, request_timeout=30)
    
    # Calculate date range (set to midnight for accurate day comparison)
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days_back)
    
    print(f"Downloading articles from {source_url} published between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
    
    articles_data = []
    total_articles = len(paper.articles)
    print(f"Found {total_articles} articles to process")
    
    for i, article in enumerate(paper.articles):
        if i % 10 == 0:
            print(f"Processing article {i+1}/{total_articles}")
        try:
            article.download()
            time.sleep(0.5)  # Add delay to avoid being blocked
            article.parse()
            
            # Normalize publish date to midnight for accurate comparison
            if article.publish_date:
                pub_date = article.publish_date.replace(hour=0, minute=0, second=0, microsecond=0)
                if start_date <= pub_date <= end_date:
                    articles_data.append({
                        'title': article.title,
                        'text': article.text,
                        'publish_date': pub_date.strftime('%Y-%m-%d'),
                        'source': source_url,
                        'authors': article.authors,
                        'url': article.url
                    })
                    print(f"Added article: {article.title[:50]}...")
        except Exception as e:
            print(f"Error processing article: {e}")
            continue
    
    return articles_data

def save_articles(articles, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(f"Title: {article['title']}\n")
            f.write(f"Date: {article['publish_date']}\n")
            f.write(f"Source: {article['source']}\n")
            f.write(f"URL: {article['url']}\n")
            f.write(f"Authors: {', '.join(article['authors'])}\n\n")
            f.write(article['text'] + "\n\n")
            f.write("="*50 + "\n\n")  # Separator between articles

if __name__ == "__main__":
    sources = [
        'https://news.google.com',
        'https://edition.cnn.com'
    ]
    
    output_file = "d:\\Interview_Prep\\DBS\\news_articles\\all_articles.txt"
    
    all_articles = []
    for source in sources:
        print(f"\n{'='*50}\nProcessing source: {source}\n{'='*50}")
        articles = download_articles(source, days_back=1)  # Explicitly set to 1 day
        all_articles.extend(articles)
        print(f"Downloaded {len(articles)} articles from {source}")
        time.sleep(2)  # Add delay between sources
    
    save_articles(all_articles, output_file)
    print(f"Saved all articles to {output_file}")