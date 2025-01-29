import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

class RSSWebScraper:
    def __init__(self, rss_urls):
        """
        Initializes the RSSWebScraper class.
        
        Args:
        rss_urls (list of tuples): List of RSS feed URLs and corresponding categories.
        """
        self.rss_urls = rss_urls
        self.df = pd.DataFrame(columns=["url", "category"])  # Empty DataFrame to store article URLs and categories
        self.scraped_data = []

    def fetch_rss_data(self):
        """Fetch and parse all RSS feeds to extract article URLs and their corresponding categories."""
        for rss_url, category in tqdm(self.rss_urls, desc="Processing RSS Feeds", unit="feed"):
            response = requests.get(rss_url)
            if response.status_code == 200:
                # Parse RSS data
                root = ET.fromstring(response.text)
                new_rows = []
                for item in root.findall(".//item"):
                    link = item.find("link").text
                    if link:
                        new_rows.append({"url": link, "category": category})
                # Concatenate new rows to the existing DataFrame
                if new_rows:
                    self.df = pd.concat([self.df, pd.DataFrame(new_rows)], ignore_index=True)
            else:
                print(f"Failed to fetch RSS feed from {rss_url}. Status code: {response.status_code}")

    def scrape_url(self, url):
        """
        Scrapes a single webpage to extract title, meta description, 
        author, published time, headline, and main content.

        Args:
        url (str): The URL of the webpage to scrape.

        Returns:
        dict: A dictionary with the extracted content.
        """
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.title.string.strip() if soup.title else "No title found"

            # Extract meta description
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            meta_content = meta_tag['content'].strip() if meta_tag and 'content' in meta_tag.attrs else "No meta description found"

            # Extract author from JSON-LD
            script_tag = soup.find('script', type='application/ld+json')
            json_data = json.loads(script_tag.string) if script_tag else {}
            author_name = json_data[0]['author'][0]['name'] if 'author' in json_data[0] else "No author found"

            # Extract published time
            meta_time_tag = soup.find('meta', property='article:published_time')
            published_time = meta_time_tag.get('content', 'No time found')

            # Extract headline
            meta_headline_tag = soup.find('meta', property='og:description')
            headline = meta_headline_tag.get('content', 'No headline found')

            # Extract main content
            main_content = soup.find('article')  # Find main content of article
            text_content = main_content.get_text(strip=True) if main_content else "No main content found."

            # Return extracted data as a dictionary
            return {
                'url': url,
                'title': title,
                'meta_description': meta_content,
                'author': author_name,
                'published_time': published_time,
                'headline': headline,
                'main_content': text_content
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'title': "Error",
                'meta_description': "Error",
                'author': "Error",
                'published_time': "Error",
                'headline': "Error",
                'main_content': "Error"
            }

    def scrape_all_urls(self):
        """Scrapes all URLs from the DataFrame and stores the results."""
        for idx, row in tqdm(self.df.iterrows(), total=self.df.shape[0], desc="Scraping URLs", unit="article"):
            url = row['url']
            print(f"Scraping URL: {url}")
            data = self.scrape_url(url)
            self.scraped_data.append(data)

    def extract_df(self):
        """Filters the DataFrame to only include articles published yesterday."""
        # Filter for yesterday's articles
        yesterday = datetime.now().date() - timedelta(days=1)
        result_df = pd.DataFrame(self.scraped_data)
        result_df['published_time'] = pd.to_datetime(result_df['published_time'], errors='coerce')
        filtered_df = result_df[result_df['published_time'].dt.date == yesterday]

        return filtered_df

    def get_filtered_df(self):
        """Fetch and scrape RSS data, then return the filtered DataFrame."""
        self.fetch_rss_data()  # Fetch the RSS data
        self.scrape_all_urls()  # Scrape all the URLs
        return self.extract_df()  # Filter and return articles from yesterday
    
    @staticmethod
    def convert_to_json(df, file_path):
        """
        Save the dataframe as a JSON file.
        :param file_path: Path to the output JSON file.
        """
        try:
            # Convert dataframe to dictionary
            data_dict = df.to_dict(orient='records')
            
            # Ensure Timestamp objects are converted to strings
            for record in data_dict:
                if 'published_time' in record:
                    record['published_time'] = record['published_time'].strftime('%Y-%m-%d %H:%M:%S')
    
            # Save the dictionary as a JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
    
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Failed to save data as JSON: {e}")  
