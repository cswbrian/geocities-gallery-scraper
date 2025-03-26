import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
import argparse
from typing import List, Dict, Optional, Set
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeocitiesScraper:
    def __init__(self, config_path: str):
        """Initialize the scraper with configuration"""
        self.config = self._load_config(config_path)
        self.base_url = self.config['base_url']
        self.output_dir = 'geocities_data'
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def get_burb_cards(self, url: str) -> List[Dict]:
        """Scrape individual cards from a page (neighborhood or burb)"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            cards = []
            
            # Find all card elements
            card_elements = soup.find_all('div', class_='card')
            
            for card in card_elements:
                try:
                    # Get the card title
                    title_element = card.find('div', class_='card-title')
                    title = title_element.find('a').text if title_element and title_element.find('a') else "Untitled"
                    
                    # Get the URL and last modified date from the subtitle
                    subtitle_element = card.find('div', class_='card-subtitle')
                    if subtitle_element:
                        subtitle_text = subtitle_element.get_text()
                        # Split the subtitle text into URL and last modified
                        parts = subtitle_text.split('Last modified:')
                        url = parts[0].strip() if len(parts) > 0 else ""
                        # Remove 'www.geocities.com/' prefix from URL
                        url = url.replace('www.geocities.com/', '')
                        last_modified = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Check for sound icon in the title
                        has_sound = '🔊' in title
                        
                        cards.append({
                            'title': title,
                            'url': url,
                            'last_modified': last_modified,
                            'has_sound': has_sound
                        })
                except Exception as e:
                    logger.warning(f"Error processing card: {str(e)}")
                    continue
                    
            return cards
            
        except Exception as e:
            logger.error(f"Error scraping page {url}: {str(e)}")
            return []

    def scrape_burb(self, hood_name: str, burb_name: str) -> Dict:
        """Scrape a specific burb"""
        burb_url = f"{self.base_url}/{hood_name}/{burb_name}"
        logger.info(f"Scraping burb: {burb_url}")
        
        cards = self.get_burb_cards(burb_url)
        
        return {
            'name': burb_name,
            'url': burb_url,
            'cards': cards,
            'total_pages': len(cards)
        }

    def save_hood_data(self, hood_data: Dict):
        """Save individual hood data to a JSON file"""
        hood_name = hood_data['name']
        output_file = os.path.join(self.output_dir, f"{hood_name}.json")
        
        # Add metadata to the hood data
        hood_data['metadata'] = {
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'base_url': self.base_url
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hood_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved hood data to {output_file}")

    def get_scraped_hoods(self) -> Set[str]:
        """Get list of already scraped hoods"""
        scraped_hoods = set()
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.json'):
                hood_name = filename[:-5]  # Remove .json extension
                scraped_hoods.add(hood_name)
        return scraped_hoods

    def scrape_hood(self, hood_name: str, burbs: Optional[List[str]] = None) -> Dict:
        """Scrape a specific neighborhood and its burbs"""
        if hood_name not in self.config['neighborhoods']:
            raise ValueError(f"Hood {hood_name} not found in config")
            
        hood_info = self.config['neighborhoods'][hood_name]
        hood_url = f"{self.base_url}/{hood_name}"
        
        # First scrape the neighborhood page itself
        logger.info(f"Scraping neighborhood page: {hood_url}")
        hood_cards = self.get_burb_cards(hood_url)
        
        # If no burbs specified, use all from config
        burbs_to_scrape = burbs or hood_info['burbs']
        
        scraped_burbs = []
        for burb_name in burbs_to_scrape:
            if burb_name in hood_info['burbs']:
                burb_data = self.scrape_burb(hood_name, burb_name)
                scraped_burbs.append(burb_data)
                time.sleep(1)  # Be nice to the server
            else:
                logger.warning(f"Burb {burb_name} not found in hood {hood_name}")
        
        hood_data = {
            'name': hood_name,
            'description': hood_info['description'],
            'url': hood_url,
            'cards': hood_cards,
            'total_pages': len(hood_cards),
            'burbs': scraped_burbs,
            'total_burbs': len(scraped_burbs)
        }
        
        # Save the hood data immediately after scraping
        self.save_hood_data(hood_data)
        
        return hood_data

def main():
    parser = argparse.ArgumentParser(description='Geocities Archive Scraper')
    parser.add_argument('--config', default='geocities_config.json', help='Path to config file')
    parser.add_argument('--hood', help='Specific neighborhood to scrape')
    parser.add_argument('--burbs', nargs='*', help='Specific burbs to scrape (optional)')
    parser.add_argument('--resume', action='store_true', help='Resume scraping from where it left off')
    
    args = parser.parse_args()
    
    scraper = GeocitiesScraper(args.config)
    
    try:
        if args.hood:
            # Scrape specific hood
            results = scraper.scrape_hood(args.hood, args.burbs)
        else:
            # Get list of already scraped hoods if resuming
            scraped_hoods = scraper.get_scraped_hoods() if args.resume else set()
            
            # Scrape all neighborhoods that haven't been scraped yet
            for hood_name in scraper.config['neighborhoods']:
                if hood_name not in scraped_hoods:
                    try:
                        scraper.scrape_hood(hood_name)
                    except Exception as e:
                        logger.error(f"Error scraping hood {hood_name}: {str(e)}")
                        # Continue with next hood even if one fails
                        continue
                else:
                    logger.info(f"Skipping already scraped hood: {hood_name}")
            
            logger.info("Scraping completed")
            
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 