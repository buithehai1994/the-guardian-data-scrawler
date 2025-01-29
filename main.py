import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar

from functions.py import RSSWebScraper

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

# Instantiate the scraper and get the filtered DataFrame
scraper = RSSWebScraper(world_news)

def main():
    try:
        # Define date
        yesterday = datetime.now().date() - timedelta(days=1)
        
        # Create the DataFrame
        filtered_df = scraper.get_filtered_df()
        
        # Save the filtered DataFrame as a JSON file to be pushed to GitHub
        file_path = f'processed_files/bbc_articles_{yesterday}.json'
        result_dict = filtered_articles.convert_to_json(df_filtered, file_path)

        return result_dict  # Return the dictionary

    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs

if __name__ == '__main__':
    main()
        
