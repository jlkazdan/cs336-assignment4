import os
from xopen import xopen
from cs336_data.extract_text import extract, NSFW, hate_speech
from fastwarc.warc import ArchiveIterator, WarcRecordType


def read_warc(file):
    with xopen(file, 'rb') as f:
        for record in ArchiveIterator(f, record_types = WarcRecordType.response):
            yield record.reader.read()

def main(input_file):
    texts = read_warc(input_file)
    count = 0
    for text in texts:
        if count >19:
            break
        count += 1
        text = extract(text)
        print(f'Is NSFW: {NSFW(text)}')
        print(f'Is HateSpeech: {hate_speech(text)}')

if __name__ == '__main__':
    input_file = '/data/CC/example.warc.gz'
    main(input_file)