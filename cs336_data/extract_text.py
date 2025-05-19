import regex as re
import resiliparse
from resiliparse.parse import encoding
from resiliparse.extract.html2text import extract_plain_text
import fasttext


EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'(?:\+?1[-.\s]?)?(?:\(?[0-9]{3}\)?[-.\s]?)?[0-9]{3}[-.\s]?[0-9]{4}'
IP_PATTERN = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

def extract(text):
    encoding_type = encoding.detect_encoding(text)
    decoded = text.decode(encoding_type, errors='replace')
    return extract_plain_text(decoded)


def identify_language(text, model_path = '/data/classifiers/lid.176.bin'):
    model = fasttext.load_model(model_path)
    language, confidence = model.predict(text.replace('\n', ""))
    return language[0].split('__')[-1], confidence[0]

def mask_emails(text):
    num_emails = len(re.findall(EMAIL_PATTERN, text))
    return re.sub(EMAIL_PATTERN, '|||EMAIL_ADDRESS|||', text), num_emails

def mask_phone_numbers(text):
    num_phone = len(re.findall(PHONE_PATTERN, text))
    return re.sub(PHONE_PATTERN, '|||PHONE_NUMBER|||', text), num_phone

def mask_ip(text):
    num_ips = len(re.findall(IP_PATTERN, text))
    return re.sub(IP_PATTERN, '|||IP_ADDRESS|||', text), num_ips

def NSFW(text, model_path = '/data/classifiers/dolma_fasttext_nsfw_jigsaw_model.bin'):
    model = fasttext.load_model(model_path)
    classification, confidence=  model.predict(text.replace('\n', ""))
    return classification[0].split('_')[-1], confidence[0]

def hate_speech(text, model_path = '/data/classifiers/dolma_fasttext_hatespeech_jigsaw_model.bin'):
    model = fasttext.load_model(model_path)
    classification, confidence=  model.predict(text.replace('\n', ""))
    return classification[0].split('_')[-1], confidence[0]

def has_alphabetic(string):
    return bool(re.search(r'[a-zA-Z]', string))

def gopher(text):
    words = text.split(' ')
    #length requirement
    if len(words) < 50 or len(words) > 1e5:
        return False
    #mean length requirement
    lengths = [len(word) for word in words]
    mean_length = sum(lengths)/len(lengths)
    if mean_length < 3 or mean_length > 10:
        return False
    #alphabetic constraint
    count = 0
    for word in words:
        if has_alphabetic(word):
            count += 1
    if count/len(words) < 0.8:
        return False
    #elipses requirement
    lines = text.split('\n')
    count = 0
    for line in lines:
        if len(line) >= 3 and line[-3:] == '...':
            count += 1
    if count/len(lines) > 0.3:
        return False
    return True
    
    
if __name__ == '__main__':

    text = test_string = "Feel free to contact me at test@gmail.com if you have any questions"
    print(mask_emails(text))

