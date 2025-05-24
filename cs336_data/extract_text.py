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


def identify_language(text, model_path = '/data/classifiers/lid.176.bin', model= None):
    if model is None:
        model = fasttext.load_model(model_path)
    if type(text) == str:
        language, confidence = model.predict(text.replace('\n', ""))
        return language[0].split('__')[-1], confidence[0]
    elif type(text) == list:
        classifications, _ = model.predict(text)
        ret_classifications = [classification[0].split('_')[-1] == 'en' for classification in classifications]
        return ret_classifications   

def mask_emails(text):
    num_emails = len(re.findall(EMAIL_PATTERN, text))
    return re.sub(EMAIL_PATTERN, '|||EMAIL_ADDRESS|||', text), num_emails

def mask_phone_numbers(text):
    num_phone = len(re.findall(PHONE_PATTERN, text))
    return re.sub(PHONE_PATTERN, '|||PHONE_NUMBER|||', text), num_phone

def mask_ip(text):
    num_ips = len(re.findall(IP_PATTERN, text))
    return re.sub(IP_PATTERN, '|||IP_ADDRESS|||', text), num_ips

def NSFW(text, model_path = '/data/classifiers/dolma_fasttext_nsfw_jigsaw_model.bin', model=None):
    if model is None:
        model = fasttext.load_model(model_path)
    if type(text) == str:
        classification, confidence=  model.predict(text.replace('\n', ""))
        return classification[0].split('_')[-1], confidence[0]
    elif type(text) == list:
        classifications, _ = model.predict(text)
        ret_classifications = [classification[0].split('_')[-1] == 'non-nsfw' for classification in classifications]
        return ret_classifications

def hate_speech(text, model_path = '/data/classifiers/dolma_fasttext_hatespeech_jigsaw_model.bin', model = None):
    if model is None:
        model = fasttext.load_model(model_path)
    if type(text) == str:
        classification, confidence=  model.predict(text.replace('\n', ""))
        return classification[0].split('_')[-1], confidence[0]
    elif type(text) == list:
        classifications, _ = model.predict(text)
        ret_classifications = [classification[0].split('_')[-1] == 'non-toxic' for classification in classifications]
        return ret_classifications    

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

def classify_quality(text, model_path='/data/c-jkazdan/fasttext_quality_model.bin', quality_model= None):
    if type(text) == list:
        classifications, _ = quality_model.predict(text)
        ret_classifications = [classification[0] == '__label__good' for classification in classifications]
        return ret_classifications
    if quality_model is None:
        quality_model = fasttext.load_model(model_path)
    #text = extract(text)
    text = text.replace('\n', '')
    hate_speech_label, _ = hate_speech(text)
    nsfw_label, _ = NSFW(text)
    language, _ = identify_language(text) 
    # print(f'Gopher: {gopher(text)}')
    # print(f'Hate Speech: {hate_speech_label}')
    # print(f'NSFW: {nsfw_label}')
    # print(f'Language label: {language}')
    if gopher(text) and hate_speech_label == 'non-toxic' and nsfw_label == 'non-nsfw' and language == 'en':
        label, confidence = quality_model.predict(text)
        if label[0] == '__label__good':
            return 'wiki', confidence[0]
        else:
            return 'cc', confidence [0]
    
    else:
        return 'cc', 1.0    
    
if __name__ == '__main__':

    text = test_string = """Dr. Raymer has done it again! This new seventh edition of his classic aircraft design textbook is updated, extensively rewritten, and adds new material on low R# flight, UAVs, electric aircraft, and even flight on Mars (see the cover). As always, Raymer’s textbook presents the entire process of aircraft conceptual design, from requirements definition through initial sizing, configuration layout, analysis, sizing, and trade studies, in the same manner seen in industry aircraft design groups.
Interesting and easy to read, AIRCRAFT DESIGN: A Conceptual Approach is the number one selling AIAA technical book (over 100,000 copies to date). Widely used in industry and government aircraft design groups, it has received the Aviation/Space Writers’ Association Award of Excellence and the prestigious AIAA Summerfield Book Award. A virtual encyclopedia of aircraft design engineering, it is known for its completeness, easy-to-read style, and real-world approach to the process of design.
In his monthly column, Peter Garrison of Flying Magazine recommended it as the best book for learning how to design an airplane. The book is in university use throughout the world, and is also a favorite of practicing design engineers who find it a trusty reference for a wide range of design information. As one measure of its utility and acceptance – well-worn copies are commonly seen at designers’ desks and in government aerospace offices."""
    print(classify_quality(text))

