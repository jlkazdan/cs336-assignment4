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

# Split the input file into 100 chunks silently
split -l $URLS_PER_CHUNK $INPUT_FILE $OUTPUT_DIR/chunk_

# Process all chunks in parallel with minimal output
find $OUTPUT_DIR -name "chunk_*" | xargs -I{} -P 20 bash -c '
    chunk_file="$1"
    output_dir="$2"
    output_base="$output_dir/$(basename "$chunk_file")"
    
    # Process the URLs in this chunk
    # Create a counter file for tracking overall progress
    count_file="$output_dir/progress_count.txt"
    
    # Process URLs silently
    wget --timeout=2 \
         --tries=1 \
         --connect-timeout=2 \
         --read-timeout=5 \
         -i "$chunk_file" \
         --warc-file="$output_base" \
         -O /dev/null \
         --quiet
    
    # Atomic update of the counter
    (
        flock -x 200
        current_count=$(cat "$count_file" 2>/dev/null || echo "0")
        urls_in_chunk=$(wc -l < "$chunk_file")
        new_count=$((current_count + urls_in_chunk))
        echo "$new_count" > "$count_file"
        
        # Print progress every 1000 files
        if [ $((new_count / 1000)) -gt $((current_count / 1000)) ]; then
            echo "Processed $new_count files out of $TOTAL_URLS"
        fi
    ) 200>"$output_dir/progress.lock"
' _ {} $OUTPUT_DIR $TOTAL_URLS

# Wait for all wget processes to complete
wait

# Count the generated WARC files
WARC_COUNT=$(find $OUTPUT_DIR -name "*.warc.gz" | wc -l)
echo "Processed all $TOTAL_URLS URLs"
echo "Found $WARC_COUNT WARC.GZ files to combine"

# Combine the WARC.GZ files without extra output
echo "Combining WARC.GZ files..."
find $OUTPUT_DIR -name "*.warc.gz" | xargs cat > $FINAL_OUTPUT

echo "All downloads completed and combined into $FINAL_OUTPUT"
echo "Final file size: $(du -h $FINAL_OUTPUT | cut -f1)"

# Clean up temporary counter files
rm -f "$OUTPUT_DIR/progress_count.txt" "$OUTPUT_DIR/progress.lock"