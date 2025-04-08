import pandas as pd
from googleapiclient.discovery import build
from newspaper import Article, Config
import time
import requests

# Configuration
API_KEY = "AIzaSyByz5htHH_FNlVmn-2qvPuoIDdie3ihsB0"  # Replace with actual key
CSE_ID = "c74b8852eb6d34593"    # Replace with actual CSE ID
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 15

def google_search(query, num=10):
    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        results = service.cse().list(
            q=query,
            cx=CSE_ID,
            num=num
        ).execute().get('items', [])
        
        # Debugging: Print each URL returned by the API
        for result in results:
            print(f"API returned URL: {result.get('link', '')}")
        
        return results
    except Exception as e:
        print(f"Google Search API Error: {e}")
        return []

def extract_articles(query, num_articles=10):
    results = google_search(query, num_articles)
    
    if not results:
        print("No results returned. Possible issues:")
        print("1. Verify API_KEY and CSE_ID")
        print("2. Check Google Cloud billing setup")
        print("3. Ensure CSE is configured for web search")
        return pd.DataFrame()

    articles = []
    for result in results[:num_articles]:
        initial_url = result.get('link', '')
        if not initial_url:
            continue

        try:
            # Direct Selenium implementation with proper wait
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument(f"user-agent={USER_AGENT}")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(initial_url)
            
            # Wait for potential JavaScript redirects
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            final_url = driver.current_url
            driver.quit()
            
            print(f"Initial URL: {initial_url}")
            print(f"Final URL: {final_url}")
            print("-" * 80)

            article = Article(final_url, config=config)
            article.download()
            article.parse()
            
            articles.append({
                'title': article.title,
                'text': article.text,
                'publish_date': str(article.publish_date),
                'source': final_url
            })
            time.sleep(1)

        except Exception as e:
            print(f"Failed to process {initial_url}: {str(e)[:100]}...")
    
    return pd.DataFrame(articles)

if __name__ == "__main__":
    # Test with simple query first
    test_query = "financial news"
    df = extract_articles(test_query, num_articles=10)
    
    if not df.empty:
        df.to_csv('D:\\Interview_Prep\\DBS\\financial_news.csv', index=False)
        print(f"Successfully saved {len(df)} articles")
        print("Sample article:", df.iloc[0]['title'][:50] + "...")
    else:
        print("No articles collected. Check:")
        print("- API key permissions")
        print("- CSE configuration (must search entire web)")
        print("- Network/firewall settings")
