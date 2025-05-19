import torch
import os
import numpy as np
from xopen import xopen
from cs336_data.extract_text import extract, gopher, NSFW, hate_speech
from fastwarc.warc import ArchiveIterator, WarcRecordType
import gzip


def read_warc(file, probability):
    with xopen(file, 'rb') as f:
        for record in ArchiveIterator(f, record_types = WarcRecordType.response):
            if np.random.rand()<probability:
                yield record.reader.read()

#this function was written by claude
def sample_urls_from_gz(gz_path, num_texts = 1e6):
    sample_prob = num_texts/43.5e6
    with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
        for line in f:
            if np.random.rand() < sample_prob:
                yield line.strip()
    
def main(input_file, output_file, num_texts):
    with open(output_file, 'a') as f:
        for ele in sample_urls_from_gz(input_file, num_texts):
            f.write(ele + '\n')
        



if __name__ == '__main__':
    input_file = '/data/wiki/enwiki-20240420-extracted_urls.txt.gz'
    num_texts = 1e6
    output_file = 'cs336_data/outputs/good_urls.txt'
    main(input_file, output_file, num_texts)