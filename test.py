import importlib
import json
import nltk
import os
import pypdf
import re
import spellchecker
from typing import List

import model

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

def shrink_whitespace(*args, **kwargs):
    return " "
WHITESPACE_RE = re.compile(r"[\n\s]+")
def profile_to_dict(profile: model.Profile):
    def _to_dict(obj):
        if isinstance(obj, list):
            return [_to_dict(x) for x in obj]
        if hasattr(obj, "__annotations__"):
            result = {k: _to_dict(v) for k, v in obj.__dict__.items()}
            if hasattr(obj, "TYPE"):
                result["TYPE"] = obj.TYPE
            return result
        if isinstance(obj, str):
            obj = WHITESPACE_RE.sub(shrink_whitespace, obj)
        return obj
    return _to_dict(profile)

def test_input(profile_path: str):
    module_path = profile_path[:-3].replace(os.path.sep, ".")
    profile_module = importlib.import_module(module_path)
    profile_obj = profile_module.PROFILE
    profile_dict = profile_to_dict(profile_obj)
    profile_json = json.dumps(profile_dict)
    if False:
        yield "Some error"

def test_html(html_path: str):
    if False:
        yield "Some error"

def test_pdf(pdf_path: str):
    file_size = os.path.getsize(pdf_path)
    if file_size > 1024 * 512:  # 500 KiB
        yield f"File size is {file_size / 1024 / 1024:.2f} MiB"

    reader = pypdf.PdfReader(pdf_path)

    pages_count = len(reader.pages)
    if pages_count > 1:
        yield f"More than one page ({pages_count})"

    whole_text = " ".join([p.extract_text() for p in reader.pages])
    words = nltk.word_tokenize(whole_text)
    words = [w for w in words if w.isalpha()]
    words = [w for w in words if w not in STOPWORDS]
    words = [w for w in words if len(w) > 2]
    words = set(words)
    misspelled = spellcheck(words)
    if misspelled:
        yield f"Misspelled words: {len(misspelled)}"
        for w, correct in misspelled.items():
            if correct:
                yield f"\t{w} ({correct}*)"
            else:
                yield f"\t{w}"

def run_all(profile: str):
    print(f"[{profile}] Testing... (this may take a while)")
    tests = [
        (test_input, os.path.join("input", profile + ".py")),
        (test_html, os.path.join("output", profile + ".html")),
        (test_pdf, os.path.join("output", profile + ".pdf")),
    ]
    any_problems = False
    for test, path in tests:
        for problem in test(path):
            any_problems = True
            print(problem)
    if not any_problems:
        print("OK")
