#!/bin/bash

# Parameters
OUTPUT_FILE="/data/c-jkazdan/commoncrawl_urls.txt"
DOMAIN="*"        # Replace with your target domain or use "*" for all URLs

# Find the latest Common Crawl dataset
echo "Finding the latest Common Crawl dataset..."
LATEST_CRAWL=$(curl -s https://index.commoncrawl.org/collinfo.json | grep -o '"id":"CC-MAIN-[^"]*' | head -1 | cut -d'"' -f4)

echo "Using latest crawl: $LATEST_CRAWL"
echo "Downloading all Common Crawl URLs for domain: $DOMAIN"
echo "Results will be saved to: $OUTPUT_FILE"

# Create/clear output file
> "$OUTPUT_FILE"

# Use the CDX API to get all URLs in one go (this might take a while for large domains)
echo "Downloading URLs... (this may take some time depending on the number of results)"
curl -s "https://index.commoncrawl.org/${LATEST_CRAWL}-index?url=${DOMAIN}&output=json&fl=url" | grep -o '"url":"[^"]*' | sed 's/"url":"//' > "$OUTPUT_FILE"

# Count the total URLs downloaded
TOTAL_URLS=$(wc -l < "$OUTPUT_FILE")
echo "Download complete! Saved $TOTAL_URLS URLs to $OUTPUT_FILE"