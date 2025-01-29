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
    ("https://www.theguardian.com/food/rss","Food")
]

# Instantiate the scraper and get the filtered DataFrame
scraper = RSSWebScraper(world_news)
filtered_df = scraper.get_filtered_df()
