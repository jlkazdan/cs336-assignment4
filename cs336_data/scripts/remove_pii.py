import os
from xopen import xopen
from cs336_data.extract_text import extract, mask_emails, mask_ip, mask_phone_numbers
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
        text, num_emails = mask_emails(text)
        print(f'the number of removed emails is {num_emails}')
        text, num_phones = mask_phone_numbers(text)
        print(f'the number of phones removed is {num_phones}')
        text, num_ips = mask_ip(text)
        print(f'the number of ip addresses removed is {num_ips}')
        with open(output_file, 'a') as f:
            f.write(text)

if __name__ == '__main__':
    input_file = '/data/CC/example.warc.gz'
    output_file = 'cs336_data/outputs/masking.txt'
    main(input_file, output_file)