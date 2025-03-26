# Geocities Archive Scraper

A Python toolkit to scrape and process the Geocities archive website (geocities.restorativland.org). The toolkit includes components for configuration scraping, data collection, and data flattening.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Components

### 1. Configuration Scraper (`scrape_config.py`)
Scrapes the main Geocities page to generate a configuration file containing neighborhoods and burbs:
```bash
python scrape_config.py
```
This generates `geocities_config.json` with neighborhood metadata.

### 2. Main Scraper (`geocities_scraper.py`)
Scrapes website data using several modes:

```bash
# Scrape a specific neighborhood and all its burbs
python geocities_scraper.py --hood Area51

# Scrape a specific neighborhood and selected burbs
python geocities_scraper.py --hood Area51 --burbs Atlantis Aurora

# Scrape everything (all neighborhoods and burbs)
python geocities_scraper.py

# Resume interrupted scraping
python geocities_scraper.py --resume

# Use custom config file
python geocities_scraper.py --config my_config.json
```

### 3. Data Flattener (`flatten_data.py`)
Processes scraped data into compressed, optimized chunks:
```bash
python flatten_data.py
```

## Output Formats

### Scraped Data Format
Each neighborhood generates a JSON file with the following structure:
```json
{
  "name": "Area51",
  "description": "Science Fiction, Fantasy",
  "url": "https://geocities.restorativland.org/Area51",
  "cards": [
    {
      "title": "Page Title",
      "url": "www.geocities.com/Area51/1234",
      "last_modified": "2009-04-28",
      "has_sound": false
    }
  ],
  "total_pages": 50,
  "burbs": [
    {
      "name": "Atlantis",
      "url": "https://geocities.restorativland.org/Area51/Atlantis",
      "cards": [...],
      "total_pages": 123
    }
  ],
  "total_burbs": 1,
  "metadata": {
    "scraped_at": "2024-01-20 12:34:56",
    "base_url": "https://geocities.restorativland.org"
  }
}
```

### Flattened Data Format
The flattener generates:
- A compressed metadata file (`*_metadata.json.gz`)
- Multiple compressed data chunks (`*_chunk_N.json.gz`)

## Features

- Respectful scraping with 1-second delays between requests
- Comprehensive logging and error handling
- Resume capability for interrupted scraping
- Detection of sound icons (🔊) in pages
- Unicode text support
- Compressed data storage
- Progress tracking and statistics

## Requirements

- Python 3.x
- requests==2.31.0
- beautifulsoup4==4.12.2 