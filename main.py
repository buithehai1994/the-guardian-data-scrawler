import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm  
from datetime import datetime, timedelta
from functions import RSSParser

world_news = [
    ("https://www.theguardian.com/uk/rss", "UK"),
    ("https://www.theguardian.com/world/rss", "World"),
    ("https://www.theguardian.com/business/rss", "Business"),
    ("https://www.theguardian.com/sport/rss", "Sport"),
    ("https://www.theguardian.com/technology/rss", "Technology"),
    ("https://www.theguardian.com/commentisfree/rss", "Opinion"),
    ("https://www.theguardian.com/uk/culture/rss", "Culture"),
    ("https://www.theguardian.com/travel/rss", "Travel"),
    ("https://www.theguardian.com/food/rss", "Food")
]

def main():
    try:
        df_list = []  # List to store temporary DataFrames
        
        for rss_url, category in tqdm(world_news, desc="Processing RSS Feeds", unit="feed"):
            rss_parser = RSSParser(rss_url, category)
            rss_parser.fetch_rss_data()
            rss_parser.parse_rss_data()
            temp_df = rss_parser.get_articles()
            df_list.append(temp_df)
        
        df = pd.concat(df_list, ignore_index=True)

        articles_data = []
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Scraping Articles", unit="article"):
            article_info = rss_parser.scrape_url(row['url'], row['rss'], row['category'])
            articles_data.append(article_info)
        
        articles_df = pd.DataFrame(articles_data)
        articles_df = articles_df.drop(columns=['author'], errors='ignore')

        filtered_articles = RSSParser.filter_by_date(articles_df)

        yesterday = datetime.now().date() - timedelta(days=1)
        file_path = f'processed_files/guardian_articles_{yesterday}.json'
        
        result_dict = RSSParser.convert_to_json(filtered_articles, file_path)
        
        return result_dict
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    main()
