import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from tqdm import tqdm  # Import tqdm for the progress bar

class WebScraper:
    def __init__(self, df):
        """
        Initializes the WebScraper class.
        
        Args:
        df (pandas.DataFrame): DataFrame containing URLs to scrape.
        """
        self.df = df
        self.scraped_data = []

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

            # Check if the page has an article section
            main_content = soup.find('article')  # This might change based on the site you're scraping
            if not main_content:
                print(f"Skipping {url}: No article found.")
                return {
                    'url': url,
                    'title': "No article found",
                    'meta_description': "No article found",
                    'author': "No article found",
                    'published_time': "No article found",
                    'headline': "No article found",
                    'main_content': "No article found"
                }

            # Extract the title
            title = soup.title.string.strip() if soup.title else "No title found"

            # Extract the meta description
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
        """
        Scrapes all URLs from the DataFrame and stores the results.

        Returns:
        pandas.DataFrame: DataFrame with extracted content for each URL.
        """
        for idx, row in tqdm(self.df.iterrows(), total=self.df.shape[0], desc="Scraping URLs"):
            url = row['url']
            print(f"Scraping URL: {url}")
            data = self.scrape_url(url)
            self.scraped_data.append(data)
        
        # Convert the collected data into a DataFrame
        return pd.DataFrame(self.scraped_data)

    @staticmethod
    def extract_df(df):
        """
        Filters the DataFrame to only include articles published yesterday.
        
        Args:
        df (pandas.DataFrame): The DataFrame containing scraped data.

        Returns:
        pandas.DataFrame: The filtered DataFrame containing only yesterday's articles.
        """
        yesterday = datetime.now().date() - timedelta(days=1)
        df['published_time'] = pd.to_datetime(df['published_time'], errors='coerce')
        filtered_df = df[df['published_time'].dt.date == yesterday]

        return filtered_df
