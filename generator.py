import argparse
import base64
from dataclasses import dataclass
import importlib
import markdown
import os
import selenium
import selenium.webdriver
import sys
import time
import watchdog.observers
import watchdog.events

import model
import template

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


@dataclass
class Config:
    profile_path: str
    output_base_path: str

    @property
    def template_path(self):
        return os.path.join("templates", self.profile.template)

    @property
    def template_max_mtime(self):
        max = None
        for root, _, files in os.walk(self.template_path):
            for file in files:
                if file.endswith(".html"):
                    mtime = os.path.getmtime(os.path.join(root, file))
                    if max is None or mtime > max:
                        max = mtime
        return max
    
    @property
    def profile_mtime(self):
        path = self.profile_path + ".py"
        if not os.path.exists(path):
            return 0
        return os.path.getmtime(path)
    
    def output_path(self, ext: str):
        os.makedirs(os.path.dirname(self.output_base_path), exist_ok=True)
        return self.output_base_path + ext
    
    def output_mtime(self, ext: str):
        path = self.output_path(ext)
        if not os.path.exists(path):
            return 0
        return os.path.getmtime(self.output_path(ext))
    
    def needs_update(self, output_ext: str):
        output_mtime = self.output_mtime(output_ext)
        return self.profile_mtime > output_mtime or self.template_max_mtime > output_mtime
    
    @property
    def profile(self) -> model.Profile:
        module_path = self.profile_path.replace(os.path.sep, ".")
        src_module = importlib.import_module(module_path)
        src_module = importlib.reload(src_module)
        return src_module.PROFILE

    def generate_html(self):
        print("Generating HTML...")
        html = template.generate(self.template_path, self.profile)
        if "markdown" in self.template_path:
            html = markdown.markdown(html)
        with open(self.output_path(".html"), "wt", encoding="utf-8") as fh:
            fh.write(html)

    def generate_pdf(self):
        print("Converting to PDF...")
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
            info = sys.exc_info()[2]
            print("Failed to generate HTML:", e)

    def on_modified(self, event):
        for path in [self.config.template_path, self.config.profile_path]:
            if path in event.src_path:
                self.generate()
                break

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--profile", type=str, default="bisser")
    args.add_argument("--continuous", action="store_true")
    args = args.parse_args()

    config = Config(
        profile_path=os.path.join("input", args.profile),
        output_base_path=os.path.join("output", args.profile),
    )

    if args.continuous:
        config.generate_html()
        observer = watchdog.observers.Observer()
        handler = GenerateHandler(config)
        observer.schedule(handler, ".", recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    elif config.needs_update(".html"):
        config.generate_html()
        config.generate_pdf()
        print("Testing...")
        import test
        test.test(config.output_path(".pdf"))
    else:
        print("No changes detected...")
    print("Done.")
