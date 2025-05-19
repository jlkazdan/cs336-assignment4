import torch
import os
import numpy as np
import multiprocessing as mp
from multiprocessing import Pool, Process, Queue
from xopen import xopen
from cs336_data.extract_text import extract, gopher, NSFW, hate_speech, identify_language
from fastwarc.warc import ArchiveIterator, WarcRecordType
import gzip


def read_warc(file, queue):
    i = 0
    with xopen(file, 'rb') as f:
        for record in ArchiveIterator(f, record_types = WarcRecordType.response):
            i+=1
            queue.put(record.reader.read())
            if i%1000 == 0:
                print(f'{i } examples processed')
    
def consumer(output_file, queue):
    while True:
        try:
            text = queue.get(timeout = 30)
        except:
            return
        if text is None:
            return

        text = extract(text)
        hate_speech_label, _ = hate_speech(text)
        nsfw_label, _ = NSFW(text)
        language, _ = identify_language(text) 
        # print(f'Gopher: {gopher(text)}')
        # print(f'Hate Speech: {hate_speech_label}')
        # print(f'NSFW: {nsfw_label}')
        # print(f'Language label: {language}')
        if gopher(text) and hate_speech_label == 'non-toxic' and nsfw_label == 'non-nsfw' and language == 'en':
            with open(output_file, 'a') as f:
                f.write(f'Good, {text.replace('\n', '')}\n')

def main(input_file, output_file, workers):
    queue = Queue(maxsize = 1000)
    p = Process(target = read_warc, args = (input_file, queue))
    p.start()

    consumers = []
    for j in range(workers):
        c = Process(target = consumer, args = (output_file, queue))
        consumers.append(c)
        c.start()
    p.join()
    for c in consumers:
        c.join()

    

if __name__ == '__main__':
    input_file = '/data/c-jkazdan/combined_urls.warc.gz'
    output_file = '/data/c-jkazdan/positive.txt'
    workers = mp.cpu_count() - 2
    main(input_file, output_file, workers)