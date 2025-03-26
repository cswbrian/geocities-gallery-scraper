import requests
from bs4 import BeautifulSoup
import json
import re
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeocitiesConfigScraper:
    def __init__(self):
        self.base_url = "https://geocities.restorativland.org"
        
    def clean_text(self, text: str) -> str:
        """Clean text by removing escape characters and extra whitespace"""
        # Replace newlines and tabs with spaces
        text = re.sub(r'[\n\t]+', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Strip leading/trailing whitespace
        return text.strip()
        
    def scrape_main_page(self):
        """Scrape the main page to get all neighborhoods and their details"""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            neighborhoods = {}
            
            # Find all h2 elements that contain neighborhood names
            hood_elements = soup.find_all('h2')
            
            for hood_element in hood_elements:
                try:
                    # Get the hood name from the link
                    hood_link = hood_element.find('a')
                    if not hood_link:
                        continue
                        
                    hood_name = self.clean_text(hood_link.text)
                    
                    # Get the description from the next h5 element
                    description_element = hood_element.find_next('h5')
                    description = ""
                    if description_element:
                        # Get all text except the image alt text
                        description_parts = []
                        for text in description_element.stripped_strings:
                            if not text.startswith('Geocities Icon'):
                                description_parts.append(self.clean_text(text))
                        description = ' '.join(description_parts)
                    
                    # Get all burbs from the table
                    burbs = []
                    table = hood_element.find_next('table')
                    if table:
                        burb_links = table.find_all('a')
                        burbs = [self.clean_text(link.text) for link in burb_links]
                    
                    # Add to neighborhoods dictionary
                    neighborhoods[hood_name] = {
                        'description': description,
                        'burbs': burbs
                    }
                    
                    logger.info(f"Scraped neighborhood: {hood_name}")
                    
                except Exception as e:
                    logger.warning(f"Error processing neighborhood: {str(e)}")
                    continue
            
            return neighborhoods
            
        except Exception as e:
            logger.error(f"Error scraping main page: {str(e)}")
            raise

    def save_config(self, neighborhoods: dict, output_file: str = 'geocities_config.json'):
        """Save the scraped data to a config file"""
        config = {
            'base_url': self.base_url,
            'neighborhoods': neighborhoods
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Config saved to {output_file}")

def main():
    scraper = GeocitiesConfigScraper()
    
    try:
        neighborhoods = scraper.scrape_main_page()
        scraper.save_config(neighborhoods)
        logger.info(f"Successfully scraped {len(neighborhoods)} neighborhoods")
        
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 