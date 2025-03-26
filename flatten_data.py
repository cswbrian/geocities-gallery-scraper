import json
import os
import time
import gzip
from typing import List, Dict, Set
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def flatten_geocities_data(input_dir: str, output_file: str, chunk_size: int = 10000):
    """Flatten all hood JSON files into compressed chunks optimized for random selection"""
    all_pages = []
    hood_names = set()
    
    # Read all JSON files from the input directory
    for filename in os.listdir(input_dir):
        if not filename.endswith('.json'):
            continue
            
        hood_name = filename[:-5]  # Remove .json extension
        hood_names.add(hood_name)
        
        input_path = os.path.join(input_dir, filename)
        logger.info(f"Processing {input_path}")
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                hood_data = json.load(f)
                
            # Add hood pages with minimal data
            for card in hood_data['cards']:
                all_pages.append({
                    'title': card['title'],
                    'url': card['url'],
                    'has_sound': card.get('has_sound', False),
                    'source': {
                        't': 'h',  # shortened 'type': 'hood'
                        'h': hood_name  # shortened 'hood_name'
                    }
                })
                
            # Add burb pages with minimal data
            for burb in hood_data['burbs']:
                for card in burb['cards']:
                    all_pages.append({
                        'title': card['title'],
                        'url': card['url'],
                        'has_sound': card.get('has_sound', False),
                        'source': {
                            't': 'b',  # shortened 'type': 'burb'
                            'h': hood_name,  # shortened 'hood_name'
                            'b': burb['name']  # shortened 'burb_name'
                        }
                    })
                    
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            continue
    
    # Calculate number of chunks
    total_chunks = (len(all_pages) + chunk_size - 1) // chunk_size
    
    # Create metadata
    metadata = {
        'total_pages': len(all_pages),
        'total_hoods': len(hood_names),
        'hoods': sorted(list(hood_names)),
        'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'chunks': total_chunks
    }
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save metadata
    metadata_file = output_file.replace('.json', '_metadata.json.gz')
    with gzip.open(metadata_file, 'wt', encoding='utf-8') as f:
        json.dump(metadata, f)
    logger.info(f"Saved metadata to {metadata_file}")
    
    # Save data in chunks
    base_name = os.path.splitext(output_file)[0]
    for i in range(total_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(all_pages))
        chunk = all_pages[start_idx:end_idx]
        
        chunk_file = f"{base_name}_chunk_{i}.json.gz"
        with gzip.open(chunk_file, 'wt', encoding='utf-8') as f:
            json.dump(chunk, f)
        logger.info(f"Saved chunk {i + 1}/{total_chunks} to {chunk_file}")
    
    logger.info(f"Data saved in {total_chunks} compressed chunks")
    logger.info(f"Total pages: {len(all_pages)}")
    logger.info(f"Total hoods: {len(hood_names)}")

def main():
    input_dir = 'geocities_data'
    output_file = 'geocities_flattened.json'
    
    if not os.path.exists(input_dir):
        logger.error(f"Input directory {input_dir} does not exist")
        return
        
    flatten_geocities_data(input_dir, output_file)

if __name__ == "__main__":
    main()