import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

class RSSParser:
    def __init__(self, rss_url, category):
        self.rss_url = rss_url
        self.category = category
        self.rss_data = None
        self.items = []

    def fetch_rss_data(self):
        """Fetch the RSS feed from the provided URL."""
        try:
            response = requests.get(self.rss_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.rss_data = response.text
            print(f"Successfully fetched RSS data from {self.rss_url}")
        except requests.RequestException as e:
            print(f"Failed to fetch RSS feed from {self.rss_url}. Error: {e}")

    def parse_rss_data(self):
        """Parse the RSS data to extract article URLs and assign categories."""
        if self.rss_data:
            # Parse the XML data from the fetched RSS feed
            root = ET.fromstring(self.rss_data)

            # Find all the 'item' elements in the RSS feed
            for item in root.findall(".//item"):
                link = item.find("link").text
                if link:
                    # Append the URL and category to the items list
                    self.items.append({
                        "url": link,
                        "category": self.category,  # Add category
                        "rss": self.rss_url
                    })
            print(f"Parsed {len(self.items)} article URLs from {self.rss_url}")
    
    def get_articles(self):
        """Return the list of article URLs and their corresponding categories."""
        return pd.DataFrame(self.items)  # Return as a DataFrame

    def scrape_url(self, url, source, category):
        """
        Scrapes a single webpage to extract title, meta description, 
        author, published time, headline, and main content.

        Args:
        url (str): The URL of the webpage to scrape.
        source (str): The source of the article (full RSS link).
        category (str): The category of the article (e.g., "UK", "World").

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
            author_name = json_data[0]['author'][0]['name'] if 'author' in json_data[0] else None

            # If the JSON-LD author is missing, try extracting from meta tags
            if not author_name:
                author_tag = soup.find('meta', attrs={'name': 'author'})
                author_name = author_tag['content'] if author_tag else "No author found"

            # Extract published time
            meta_time_tag = soup.find('meta', property='article:published_time')
            published_time = meta_time_tag['content'] if meta_time_tag else "No time found"

            # Extract headline
            meta_headline_tag = soup.find('meta', property='og:description')
            headline = meta_headline_tag['content'] if meta_headline_tag else "No headline found"

            # Extract main content
            main_content = soup.find('article')  # Find main content of article
            text_content = main_content.get_text(strip=True) if main_content else "No main content found."

            # Return extracted data as a dictionary, ensuring a single author column
            return {
                'url': url,
                'source': source,
                'type': category,  # Include the category
                'title': title,
                'description': meta_content,
                'Author': author_name,  # Use only one 'Author' column
                'Date Published': published_time,
                'Headline': headline,
                'Content': text_content
            }

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'source': source,
                'type': category,  # Include category even in error case
                'title': "Error",
                'description': "Error",
                'author': "Error",
                'Date Published': "Error",
                'Headline': "Error",
                'Content': "Error"
            }
        
    @staticmethod
    def filter_by_date(df):
        # Replace invalid date entries with NaT
        df['Date Published'] = pd.to_datetime(
        df['Date Published'], 
            errors='coerce',  # This will convert invalid dates to NaT
            format='%Y-%m-%dT%H:%M:%S.%f%z'  # Adjust the format if necessary
        )
        
        # Get today's date and subtract one day
        today = datetime.now().date() - timedelta(days=1)
        
        # Filter articles published today, ignoring NaT
        filtered_df = df[df['Date Published'].dt.date == today]
        
        return filtered_df

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
                if 'Date Published' in record:
                    record['Date Published'] = record['Date Published'].strftime('%Y-%m-%d %H:%M:%S')
    
            # Save the dictionary as a JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)
    
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"Failed to save data as JSON: {e}")  
