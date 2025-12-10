import os

def remove_duplicate_urls(input_file, output_file):
    """
    Read URLs from input file, remove duplicates, and save unique URLs to output file.
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            return False
        
        # Read all URLs from input file
        with open(input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"Total URLs read from {input_file}: {len(urls)}")
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen_urls = set()
        
        for url in urls:
            if url not in seen_urls:
                unique_urls.append(url)
                seen_urls.add(url)
        
        print(f"Unique URLs found: {len(unique_urls)}")
        print(f"Duplicate URLs removed: {len(urls) - len(unique_urls)}")
        
        # Write unique URLs to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for url in unique_urls:
                f.write(f"{url}\n")
        
        print(f"Unique URLs saved to '{output_file}'")
        return True
        
    except Exception as e:
        print(f"Error processing files: {e}")
        return False

def main():
    input_file = 'otomoto_car_urls.txt'
    output_file = 'otomoto_car_urls_unique.txt'
    
    print("Starting URL deduplication process...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print("-" * 50)
    
    success = remove_duplicate_urls(input_file, output_file)
    
    if success:
        print("-" * 50)
        print("URL deduplication completed successfully!")
    else:
        print("-" * 50)
        print("URL deduplication failed!")

if __name__ == "__main__":
    main()
