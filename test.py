import nltk
import os
import pypdf
import spellchecker
from typing import List

nltk.download('words') 
nltk.download('stopwords')
from nltk.corpus import words
from nltk.corpus import stopwords

ALL_WORDS = words.words()
STOPWORDS = set(stopwords.words('english'))

def spellcheck(words: List[str]):
    spell_checker = spellchecker.SpellChecker()
    misspelled = spell_checker.unknown(words)
    if os.path.exists("known_words.txt"):
        with open("known_words.txt", "rt", encoding="utf-8") as fh:
            known_words = set(fh.read().splitlines())
    else:
        known_words = set()
    known_words = {w.lower() for w in known_words if w}
    misspelled = [w for w in misspelled if w.lower() not in known_words]
    return {w: spell_checker.correction(w) for w in misspelled}

def test(pdf_path: str):
    reader = pypdf.PdfReader(pdf_path)
    pages_count = len(reader.pages)
    if pages_count > 1:
        print(f" - More than one page ({pages_count})")
    
    whole_text = " ".join([p.extract_text() for p in reader.pages])
    words = nltk.word_tokenize(whole_text)
    words = [w for w in words if w.isalpha()]
    words = [w for w in words if w not in STOPWORDS]
    words = [w for w in words if len(w) > 2]
    words = set(words)
    misspelled = spellcheck(words)
    if misspelled:
        print(f" - Misspelled words: {len(misspelled)}")
        for w, correct in misspelled.items():
            if correct:
                print(f"   - {w} (*{correct})")
            else:
                print(f"   - {w}")
