import torch
import os
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool, Process, Queue
from xopen import xopen
from cs336_data.extract_text import extract, gopher, NSFW, hate_speech, identify_language
import gzip


def read_wet(file, queue):
    i = 0
    current_text = ""
    collecting = False
    
    with xopen(file, 'rt', encoding='utf-8') as f:
        for line in f:
            # Start of a new record
            if line.startswith("WARC/1.0"):
                if current_text and collecting:
                    queue.put(current_text)
                    i += 1
                    if i % 1000 == 0:
                        print(f'{i} examples processed')
                current_text = ""
                collecting = False
                
            # Content block starts after an empty line following the headers
            elif line.strip() == "" and not collecting and "WARC-Type: conversion" in current_text:
                collecting = True
                current_text = ""  # Reset to remove the headers
                
            elif collecting:
                current_text += line
                
            else:
                current_text += line  # Collect headers to check for WARC-Type
                
        # Don't forget the last record
        if current_text and collecting:
            queue.put(current_text)
    
def consumer(output_file, queue):
    while True:
        try:
            text = queue.get(timeout=30)
        except:
            return
        if text is None:
            return

        # No need to extract text as WET files already contain extracted text
        # text = extract(text)  # We can remove this line
        
        hate_speech_label, _ = hate_speech(text)
        nsfw_label, _ = NSFW(text)
        language, _ = identify_language(text) 
        
        if gopher(text) and hate_speech_label == 'non-toxic' and nsfw_label == 'non-nsfw' and language == 'en':
            with open(output_file, 'a') as f:
                f.write(f'Bad, {text.replace("\n", "")}\n')

def main(input_folder, output_file, workers):
    queue = Queue(maxsize=1000)
    processes = []
    
    # Get all WET files in the folder
    wet_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.wet.gz')]
    
    # Start a process for each WET file
    for wet_file in wet_files:
        p = Process(target=read_wet, args=(wet_file, queue))
        processes.append(p)
        p.start()

    consumers = []
    for j in range(workers):
        c = Process(target=consumer, args=(output_file, queue))
        consumers.append(c)
        c.start()
    
    for p in processes:
        p.join()
        
    # Signal consumers to exit
    for _ in range(workers):
        queue.put(None)
        
    for c in consumers:
        c.join()

if __name__ == '__main__':
    input_folder = '/data/CC/'  # Folder containing WET.gz files
    output_file = '/data/c-jkazdan/negative.txt'
    workers = mp.cpu_count() - 2
    main(input_folder, output_file, workers)