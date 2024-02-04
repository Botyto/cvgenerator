import argparse
import base64
from dataclasses import dataclass
import importlib
import markdown
import os
import selenium
import selenium.webdriver
import time
import tornado.template
import watchdog.observers
import watchdog.events

import model
import test

def data_to_dict(profile: model.Profile):
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


@dataclass
class Config:
    template_path: str
    profile_path: str
    output_base_path: str

    @property
    def template_mtime(self):
        return os.path.getmtime(self.template_path)
    
    @property
    def profile_mtime(self):
        return os.path.getmtime(self.profile_path)
    
    def output_path(self, ext: str):
        return self.output_base_path + ext
    
    def output_mtime(self, ext: str):
        return os.path.getmtime(self.output_path(ext))
    
    def needs_update(self, output_ext: str):
        output_mtime = self.output_mtime(output_ext)
        return self.profile_mtime > output_mtime or self.template_mtime > output_mtime
    
    @property
    def profile(self):
        src_module = importlib.import_module(self.profile_path)
        src_module = importlib.reload(src_module)
        return src_module.PROFILE

    def generate_html(self):
        with open(self.template_path, "rt", encoding="utf-8") as fh:
            template = tornado.template.Template(fh.read())
        html = template.generate(profile=self.profile)
        html_path = self.output_path(".html")
        if "markdown.html" in self.template_path:
            with open(html_path, "rt", encoding="utf-8") as fh:
                html = fh.read()
            html = markdown.markdown(html)
        with open(html_path, "wt", encoding="utf-8") as fh:
            fh.write(html)

    def generate_pdf(self):
        with selenium.webdriver.Edge() as driver:
            html_path = self.output_path(".html")
            driver.get("file://" + os.path.abspath(html_path))
            pdf = driver.print_page()
        pdf_bytes = base64.b64decode(pdf)
        with open(self.output_path(".pdf"), "wb") as fh:
            fh.write(pdf_bytes)


class GenerateHandler(watchdog.events.FileSystemEventHandler):
    config: Config

    def __init__(self, config: Config):
        self.config = config

    def generate(self):
        try:
            self.config.generate_html()
        except Exception as e:
            print("Failed to generate HTML:", e)

    def on_modified(self, event):
        for path in [self.config.template_path, self.config.profile_path]:
            if path in event.src_path:
                self.generate()
                break


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--profile", type=str, default="bisser")
    args.add_argument("--template", type=str, default="markdown")
    args.add_argument("--continuous", action="store_true")
    args = args.parse_args()

    config = Config(
        template_path=os.path.join("templates", args.template + ".html"),
        profile_path=os.path.join("input", args.profile + ".py"),
        output_base_path=os.path.join("output", args.profile),
    )

    if args.continuous:
        observer = watchdog.observers.Observer()
        handler = GenerateHandler(args.src, args.template)
        observer.schedule(handler, ".", recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    elif config.needs_update(".html"):
        print("Generating HTML...")
        config.generate_html()
        print("Converting to PDF...")
        config.generate_pdf()
        test.test(config.output_path(".pdf"))
    else:
        print("No changes detected...")
    print("Done.")
