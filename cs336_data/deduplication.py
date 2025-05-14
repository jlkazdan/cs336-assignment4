import regex as re
import resiliparse
from resiliparse.parse import encoding
from resiliparse.extract.html2text import extract_plain_text
import fasttext

def exact_deduplicate(paths, output_dir):
    lines = set()
    for path in paths:
        output = output_dir / path.name  
        
        with open(output, 'w') as o:
            with open(path, 'r') as f:
                for line in f:
                    h = hash(line)
                    if h not in lines:
                        o.write(line)
                        lines.add(h)



    



