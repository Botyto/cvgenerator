import argparse
import base64
import importlib
import markdown
import os
import selenium
import selenium.webdriver
import tornado.template

import data
import test

def santize_data(profile: data.Profile):
    def _sanitize(obj):
        if isinstance(obj, list):
            copy = [*obj]
            copy.sort()
            return [_sanitize(x) for x in copy]
        if hasattr(obj, "__annotations__"):
            for k in obj.__annotations__:
                setattr(obj, k, _sanitize(getattr(obj, k)))
        return obj
    return _sanitize(profile)

def data_to_dict(profile: data.Profile):
    def _to_dict(obj):
        if isinstance(obj, list):
            copy = [*obj]
            copy.sort()
            return [_to_dict(x) for x in copy]
        if hasattr(obj, "__annotations__"):
            return {k: _to_dict(v) for k, v in obj.__dict__.items()}
        return obj
    return _to_dict(profile)

def generate(src: str, template: str, output: str = "output.html"):
    src_module = importlib.import_module(src)
    profile = src_module.PROFILE
    santize_data(profile)
    template_path = os.path.join("templates", template)
    with open(template_path, "rt", encoding="utf-8") as fh:
        template = tornado.template.Template(fh.read())
    html = template.generate(profile=profile)
    with open(output, "wb") as fh:
        fh.write(html)
    return output

def generate_pdf(html_path: str, output: str = "output.pdf"):
    with selenium.webdriver.Edge() as driver:
        driver.get("file://" + os.path.abspath(html_path))
        pdf = driver.print_page()
    pdf_bytes = base64.b64decode(pdf)
    with open(output, "wb") as fh:
        fh.write(pdf_bytes)
    return output

HTML_PATH = "output.html"
PDF_PATH = "output.pdf"
if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--src", type=str, default="details")
    args.add_argument("--template", type=str, default="markdown.html")
    args = args.parse_args()
    template_mtime = os.path.getmtime(os.path.join("templates", args.template))
    output_mtime = os.path.getmtime(HTML_PATH) if os.path.exists(HTML_PATH) else 0
    input_mtime = os.path.getmtime(args.src + ".py") if os.path.exists(args.src + ".py") else 0
    if input_mtime < output_mtime and template_mtime < output_mtime:
        print("No changes detected...")
    else:
        print("Generating...")
        generate(args.src, args.template, HTML_PATH)
        if args.template == "markdown.html":
            with open(HTML_PATH, "rt", encoding="utf-8") as fh:
                html = fh.read()
            html = markdown.markdown(html)
            with open(HTML_PATH, "wt", encoding="utf-8") as fh:
                fh.write(html)
        print("Converting to PDF...")
        generate_pdf(HTML_PATH, PDF_PATH)
    print("Testing...")
    test.test(PDF_PATH)
    print("Done.")
