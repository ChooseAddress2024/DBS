# -*- coding: utf-8 -*-
import requests
from newspaper import Article
import pandas as pd
import os
from datetime import datetime, timedelta
import spacy

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load('en_core_web_sm')

# Google News API (example using unofficial python-google-news)
from GoogleNews import GoogleNews

# NewsAPI configuration
NEWSAPI_KEY = 'YOUR_NEWSAPI_KEY'

class NewsScreeningSystem:
    def __init__(self):
        self.news_sources = ['google_news', 'newsapi']

    def fetch_news(self, query="financial crime", timeframe="1m"):
        """Fetch news from multiple sources"""
        all_news = []

        # Google News
        googlenews = GoogleNews(lang='en', period=timeframe)
        googlenews.search(query)
        all_news.extend(googlenews.results())

        # NewsAPI
        if 'newsapi' in self.news_sources:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "from": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                "to": datetime.now().strftime('%Y-%m-%d'),
                "apiKey": NEWSAPI_KEY,
                "pageSize": 100,
                "sortBy": "publishedAt"
            }
            response = requests.get(url, params=params)
            all_news.extend(response.json().get('articles', []))

        return all_news

    def preprocess_article(self, url):
        """Extract and clean article text"""
        article = Article(url)
        article.download()
        article.parse()
        return {
            'title': article.title,
            'text': article.text,
            'publish_date': article.publish_date,
            'source': url
        }

    def extract_entities(self, text):
        """Extract entities using NER"""
        doc = nlp(text)
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': []
        }
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        return entities

    def process_news(self, news_items):
        """Process news articles and extract entities"""
        processed_articles = []
        for item in news_items:
            article = self.preprocess_article(item['link'])
            article['entities'] = self.extract_entities(article['text'])
            processed_articles.append(article)
        return processed_articles

if __name__ == "__main__":
    # Example usage
    screening_system = NewsScreeningSystem()
    news_items = screening_system.fetch_news(timeframe="1m")
    processed_articles = screening_system.process_news(news_items)
    pd.DataFrame(processed_articles).to_csv("data/processed_articles.csv", index=False)