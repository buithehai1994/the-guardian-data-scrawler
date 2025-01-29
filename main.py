import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar
from datetime import datetime, timedelta
from functions import RSSParser

# List of RSS Feed URLs and their corresponding categories
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

# Create an empty DataFrame to store all the article URLs and categories
df = pd.DataFrame(columns=["url", "category"])


def main():
    try:
        # Loop through each RSS feed URL and parse the data with a progress bar using tqdm
        for rss_url, category in tqdm(world_news, desc="Processing RSS Feeds", unit="feed"):
            # Create an instance of the RSSParser for each RSS feed
            rss_parser = RSSParser(rss_url, category)
        
            # Fetch the RSS feed data
            rss_parser.fetch_rss_data()
        
            # Parse the RSS data to extract article URLs and assign categories
            rss_parser.parse_rss_data()
        
            # Get the articles DataFrame and append to the main DataFrame
            temp_df = rss_parser.get_articles()
            
            # Concatenate the temporary DataFrame with the main one
            df = pd.concat([df, temp_df], ignore_index=True)
        
        # Now df contains all article URLs and categories
        # Apply scraping to each URL with a progress bar
        articles_data = []
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Scraping Articles", unit="article"):
            article_info = rss_parser.scrape_url(row['url'], row['rss'], row['category'])
            articles_data.append(article_info)
        
        # Convert the scraped data into a DataFrame
        articles_df = pd.DataFrame(articles_data)
        
        # Optionally, clean up the DataFrame by dropping unnecessary columns if needed
        articles_df = articles_df.drop(columns=['author'], errors='ignore')

        filtered_articles = RSSParser.filter_by_date(articles_df)
        
        # Define date
        yesterday = datetime.now().date() - timedelta(days=1)

        # Save the filtered DataFrame as a JSON file to be pushed to GitHub
        file_path = f'processed_files/guardian_articles_{yesterday}.json'
        result_dict = filtered_articles.convert_to_json(filtered_articles, file_path)
        
        return result_dict  # Return the dictionary

if __name__ == '__main__':
    main()
