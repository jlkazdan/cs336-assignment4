#!/bin/bash

# Directory paths
INPUT_FILE="cs336_data/outputs/good_urls.txt"
OUTPUT_DIR="/data/c-jkazdan/split_downloads"
FINAL_OUTPUT="cs336_data/outputs/combined_urls.warc.gz"

# Create output directory if it doesn't exist
mkdir -p $OUTPUT_DIR

# Count total number of URLs
TOTAL_URLS=$(wc -l < $INPUT_FILE)
URLS_PER_CHUNK=$(( (TOTAL_URLS + 99) / 100 ))
echo "Total URLs to process: $TOTAL_URLS in chunks of $URLS_PER_CHUNK"

# Split the input file into 100 chunks
split -l $URLS_PER_CHUNK $INPUT_FILE $OUTPUT_DIR/chunk_
echo "Split input file into $(find $OUTPUT_DIR -name "chunk_*" | wc -l) chunks"

# Process all chunks in parallel directly with inline commands
echo "Starting parallel processing with 20 concurrent processes..."
find $OUTPUT_DIR -name "chunk_*" | xargs -I{} -P 20 bash -c '
    chunk_file="$1"
    output_dir="$2"
    output_base="$output_dir/$(basename "$chunk_file")"
    
    wget --timeout=2 \
         --tries=1 \
         --connect-timeout=2 \
         --read-timeout=2 \
         -i "$chunk_file" \
         --warc-file="$output_base" \
         -O /dev/null \
         --no-warc-compression
' _ {} $OUTPUT_DIR

# Wait for all wget processes to complete
wait

# Count the generated WARC files
WARC_COUNT=$(find $OUTPUT_DIR -name "*.warc" | wc -l)
echo "Found $WARC_COUNT WARC files to combine"

# Combine the WARC files and compress the result
echo "Combining WARC files and compressing..."
find $OUTPUT_DIR -name "*.warc" | xargs cat | gzip > $FINAL_OUTPUT

echo "All downloads completed and combined into $FINAL_OUTPUT"
echo "Final file size: $(du -h $FINAL_OUTPUT | cut -f1)"