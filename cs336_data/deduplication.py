import os
import re
import mmh3
import unicodedata
from pathlib import Path
from collections import Counter

#question: the hashes might not be unique-- is this okay for the current part of the problem?
def exact_deduplicate(paths, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    line_counts = Counter()
    
    for path in paths:
        with open(path, 'r') as f:
            for line in f:
                line_counts[hash(line)] += 1
    
    for path in paths:
        output_path = output_dir / path.name
        
        with open(path, 'r') as f, open(output_path, 'w') as o:
            for line in f:
                if line_counts[hash(line)] == 1:
                    o.write(line)


def normalize_text(text):
    #make lower case
    text = text.lower()
    #normalize white spaces
    text = re.sub(r'\s+', ' ', text)
    #normalize
    text = unicodedata.normalize('NFD', text)
    #get rid of punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text

def hash_document(document_path, n, num_hashes):
    with open(document_path, 'r') as f:
        document = normalize_text(f.read())
    words = document.split()
    n_grams = set()
    hashes = []
    for i in range(len(words)-n+1):
        n_gram = ''.join(words[i:i+n])
        n_grams.add(n_gram)
    
    #we just use the default hash functions
    for i in range(num_hashes):
        smallest = float('inf')
        for n_gram in n_grams:
            smallest = min(mmh3.hash(n_gram, i), smallest)
        hashes.append(smallest)

    
    return hashes
        
def compute_jaccard_threshold(f_1, f_2, lookup):
    a = lookup[f_1]
    b = lookup[f_2]
    count =0 
    for a_i, b_i in zip(a, b):
        if a_i == b_i:
            count += 1
    return count/len(a)

def LSH_hash(input_files, num_hashes, num_bands, ngrams, jaccard_threshold, output_directory):
    #get the output directory
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    #get the hashes for each of the documents
    doc_to_hash = dict()
    doc_to_equivalences = dict()

    path_count =0 
    for path in input_files:
        computed_hash = hash_document(path, ngrams, num_hashes)
        if path_count < 2:
            path_count += 1
        doc_to_hash[path] = computed_hash
        doc_to_equivalences[path] = set()
    
    candidates = {i:dict() for i in range(num_bands)}
    band_len = int(num_hashes/num_bands)

    duplicates = set()

    for i in range(num_bands):
        band_dict = candidates[i]
        start_index = band_len * i
        end_index = band_len * (i+1)
        for doc in doc_to_hash.keys():
            computed_hash = doc_to_hash[doc]
            band = tuple(computed_hash[start_index:end_index])
            if band not in band_dict:
                band_dict[band] = set()
            band_dict[band].add(doc)
        band_list = list(band_dict.keys())
        for band in band_list:
            band_candidates = list(band_dict[band])
            if len(band_list) > 1:
                for i, ele1 in enumerate(band_candidates):
                    for ele2 in band_candidates[i+1:]:
                        if compute_jaccard_threshold(ele1, ele2, doc_to_hash) > jaccard_threshold:
                            duplicates.add(sorted([ele1, ele2])[1])
            
    for path in input_files:
        if path not in duplicates:
            output_path = output_dir / path.name
            
            with open(path, 'r') as f, open(output_path, 'w') as o:
                o.write(f.read())
                
    
    #let's sort each candidate pair, create a set that contains the second element of 
    #each pair, and then iterate through the documents and only return the ones that 
    #are not in the duplicate set

    
    
