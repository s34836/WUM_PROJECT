import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import os
from datetime import datetime

# Constants
PROGRESS_FILE = '2-3_progress.json'
OUTPUT_FILE = 'otomoto_cars.csv'

def load_progress():
    """Load progress from JSON file or create new if doesn't exist"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress_data = json.load(f)
                print(f"📊 Loaded progress: Last processed index: {progress_data.get('last_processed', -1)}")
                print(f"📅 Started at: {progress_data.get('start_time', 'Unknown')}")
                return progress_data
        except json.JSONDecodeError:
            print("⚠️ Error reading progress file. Starting from beginning.")
            return {'last_processed': -1, 'start_time': datetime.now().isoformat()}
    else:
        print("🆕 No progress file found. Starting fresh.")
        return {'last_processed': -1, 'start_time': datetime.now().isoformat()}

def save_progress(last_processed):
    """Save current progress to JSON file"""
    progress_data = {
        'last_processed': last_processed,
        'start_time': datetime.now().isoformat(),
        'total_urls': len(urls),
        'processed_count': last_processed + 1
    }
    try:
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress_data, f, indent=2)
        print(f"💾 Progress saved: {last_processed + 1}/{len(urls)} URLs processed")
    except Exception as e:
        print(f"❌ Error saving progress: {str(e)}")

def load_or_create_dataframe(urls):
    """Load existing CSV or create new DataFrame with URLs"""
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_csv(OUTPUT_FILE)
            # If we have existing data, merge with new URLs
            new_urls = set(urls) - set(existing_df['url'])
            if new_urls:
                new_df = pd.DataFrame({'url': list(new_urls)})
                new_df['raw_json'] = None
                return pd.concat([existing_df, new_df], ignore_index=True)
            return existing_df
        except Exception as e:
            print(f"Error reading existing CSV: {str(e)}")
            return create_new_dataframe(urls)
    return create_new_dataframe(urls)

def get_processed_urls():
    """Get list of already processed URLs from CSV file"""
    processed_urls = set()
    if os.path.exists(OUTPUT_FILE):
        try:
            df = pd.read_csv(OUTPUT_FILE)
            processed_urls = set(df['url'].tolist())
            print(f"Found {len(processed_urls)} already processed URLs")
        except Exception as e:
            print(f"Error reading processed URLs: {str(e)}")
    return processed_urls

def create_new_dataframe(urls):
    """Create new DataFrame with required columns and URLs"""
    df = pd.DataFrame({'url': urls})
    df['raw_json'] = None
    return df

def save_processed_url(df, idx):
    """Save a single processed URL to CSV"""
    try:
        # Create a DataFrame with just the processed row
        processed_df = pd.DataFrame([df.iloc[idx]])
        
        if os.path.exists(OUTPUT_FILE):
            # Append to existing file without header
            processed_df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
        else:
            # Create new file with header
            processed_df.to_csv(OUTPUT_FILE, index=False)
            
        print(f"Saved URL {idx + 1} to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error saving processed URL: {str(e)}")

def extract_json_data(html_content):
    """Extract JSON data from HTML content"""
    try:
        # Look for the script tag containing the JSON data with nonce attribute
        json_pattern = r'<script id="__NEXT_DATA__" type="application/json" nonce="[^"]*">(.*?)</script>'
        match = re.search(json_pattern, html_content, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            # Parse the JSON string
            json_data = json.loads(json_str)
            return json_data
        return None
    except Exception as e:
        print(f"Error extracting JSON data: {str(e)}")
        return None

def extract_details_from_json(json_data):
    """Extract relevant details from the JSON data for car listings"""
    try:
        if not json_data:
            return None

        # Navigate through the JSON structure to find the car details
        # Try different possible paths for otomoto car data
        car_data = (
            json_data.get('props', {}).get('pageProps', {}).get('ad', {}) or
            json_data.get('props', {}).get('pageProps', {}).get('data', {}) or
            json_data.get('props', {}).get('pageProps', {})
        )
        
        if not car_data:
            return None

        return {
            'raw_json': json.dumps(car_data)  # Store the complete car data
        }
    except Exception as e:
        print(f"Error extracting details from JSON: {str(e)}")
        return None

# Read URLs from the text file
try:
    with open('otomoto_car_urls_unique.txt', 'r') as file:
        urls = file.readlines()
except Exception as e:
    print(f"Error reading URLs file: {str(e)}")
    exit(1)

# Clean URLs (remove whitespace and newlines)
urls = [url.strip() for url in urls if url.strip()]  # Only keep non-empty URLs

if not urls:
    print("No URLs found in the file!")
    exit(1)

print(f"Loaded {len(urls)} URLs from file")

# Function to scrape car details
def scrape_car_details(url):
    try:
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extract JSON data from the page
        json_data = extract_json_data(response.text)
        
        if json_data:
            # Extract details from the JSON data
            details = extract_details_from_json(json_data)
            if details:
                return details
        
        return {'raw_json': None}
    
    except requests.Timeout:
        print(f"Timeout while scraping {url}")
        return None
    except requests.RequestException as e:
        print(f"Request error while scraping {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def process_single_url(url, idx):
    """Process a single URL"""
    try:
        print(f"Processing URL {idx + 1}: {url}")
        details = scrape_car_details(url)
        
        if details:
            # Create result DataFrame
            result_df = pd.DataFrame([{
                'url': url,
                'raw_json': details['raw_json']
            }])
            
            # Save to CSV
            if os.path.exists(OUTPUT_FILE):
                result_df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
            else:
                result_df.to_csv(OUTPUT_FILE, index=False)
            
            # Update progress file
            save_progress(idx)
            print(f"✅ Processed {idx + 1}/{len(urls_to_process)} URLs")
            return True
        else:
            print(f"Failed to extract data from URL {idx + 1}")
            return False
            
    except Exception as e:
        print(f"Error processing URL {idx + 1}: {str(e)}")
        return False

# Load progress and existing data
progress = load_progress()
processed_urls = get_processed_urls()

# Filter out already processed URLs
urls_to_process = []
for i, url in enumerate(urls):
    if url not in processed_urls:
        urls_to_process.append((url, i))

if not urls_to_process:
    print("All URLs have been processed!")
    exit(0)

print(f"Found {len(urls_to_process)} URLs to process out of {len(urls)} total")
print(f"Progress file: {PROGRESS_FILE}")
print(f"Output file: {OUTPUT_FILE}")

# Sequential scraping
try:
    completed = 0
    for url, idx in urls_to_process:
        success = process_single_url(url, idx)
        completed += 1
        
        if completed % 10 == 0:  # Progress update every 10 completed
            print(f"Completed {completed}/{len(urls_to_process)} URLs")
        
        # Add a small delay to be respectful to the server
        #time.sleep(0.1)
    
    print(f"\nSequential scraping completed!")
    print(f"Total URLs processed: {len(urls_to_process)}")
    
    # Load and display results
    if os.path.exists(OUTPUT_FILE):
        result_df = pd.read_csv(OUTPUT_FILE)
        print(f"\nResults saved to {OUTPUT_FILE}")
        print(f"Total records: {len(result_df)}")
        print("\nFirst few entries:")
        print(result_df.head())

except KeyboardInterrupt:
    print("\nScraping interrupted by user!")
    exit(0)
except Exception as e:
    print(f"\nUnexpected error: {str(e)}")
    exit(1)
