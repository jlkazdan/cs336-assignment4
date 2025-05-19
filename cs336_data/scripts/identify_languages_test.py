import os
from xopen import xopen
from cs336_data.extract_text import extract, identify_language
from fastwarc.warc import ArchiveIterator, WarcRecordType


def read_warc(file):
    with xopen(file, 'rb') as f:
        for record in ArchiveIterator(f, record_types = WarcRecordType.response):
            yield record.reader.read()

def main(input_file, output_file):
    texts = read_warc(input_file)
    count = 0
    for text in texts:
        if count >19:
            break
        count += 1
        text = extract(text)
        print(identify_language(text))

if __name__ == '__main__':
    input_file = '/data/CC/example.warc.gz'
    output_file = 'cs336_data/outputs/look_at_cc_output.txt'
    main(input_file, output_file)