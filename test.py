from enum import Enum
import importlib
import json
import nltk
import openai
from openai_functions import Conversation
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

if os.path.exists("openai_api_key.txt"):
    with open("openai_api_key.txt", "rt", encoding="utf-8") as fh:
        openai.api_key = fh.read().strip()
else:
    print("No OpenAI API key found")

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
            result = {k: _to_dict(v) for k, v in obj.__dict__.items() if v is not None}
            if hasattr(obj, "TYPE"):
                result["TYPE"] = obj.TYPE
            return result
        if isinstance(obj, str):
            obj = WHITESPACE_RE.sub(shrink_whitespace, obj)
        return obj
    result = _to_dict(profile)
    result = {
        "name": result["name"],
        "title": result["title"],
        "sections": result["sections"],
    }
    return result

class Problem(Enum):
    RECOMMENDATION = "Recommendation"
    READABILITY = "Readability"
    GRAMMAR = "Grammar"
    BRAVITY = "Bravity"

def test_input(profile_path: str):
    module_path = profile_path[:-3].replace(os.path.sep, ".")
    profile_module = importlib.import_module(module_path)
    profile_obj = profile_module.PROFILE
    if openai.api_key:
        profile_dict = profile_to_dict(profile_obj)
        profile_json = json.dumps(profile_dict)
        problems, revisions = 0, 0
        def report_problem(expression: str, problem: Problem, recommendation: str, revised: str):
            nonlocal problems, revisions
            print(f"Problem with {problem.value} in {expression}: {recommendation}")
            problems += 1
            try:
                value = eval(expression, {"cv": profile_dict})
                print(f"Value: {value}")
                try:
                    expression += " = \"" + revised.replace("\"", "\\\"") + "\""
                    print(expression)
                    eval(expression, {"cv": profile_dict})
                    revisions += 1
                except Exception as e:
                    print(f"Error applying the revision: {e}")
            except:
                pass
            print(f"Revised value: {revised}")
        chat = Conversation(model="gpt-4")
        chat.add_function(report_problem)
        result = chat.ask(f"""Review the following CV from a highly critical recruiter's perspective.
Point out any flaws in the texts, addressing the problematic value using python expressions beginning with the variable `cv`.
Don't report issues on missing information, texts with no issues or the JSON format - focus on the quality of the texts.
Be concise and clear. Call the `report_problem` function for each issue, instead of explaining it.
When revising the text, keep the tone of the original text, the information it conveys and don't change the length too drastically.
Here's the CV represented as a JSON:
{profile_json}""")
        if problems > 0:
            print(f"Found {problems} problems")
            if revisions > 0:
                print(f"Revised {revisions} values")
        elif result:
            print(result)

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
