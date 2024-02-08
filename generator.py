import argparse
import base64
import importlib
import os
import selenium
import selenium.webdriver
from selenium.webdriver.common.print_page_options import PrintOptions
import time
from typing import Dict, Tuple
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


class Generator:
    _profiles: Dict[str, Tuple[model.Profile, float]]

    def __init__(self):
        self._profiles = {}

    def all_profiles(self):
        return [f[:-3] for f in os.listdir("input") if f.endswith(".py") and "template" not in f]
    
    def _read_profile(self, profile: str) -> model.Profile:
        src_module = importlib.import_module("input." + profile)
        src_module = importlib.reload(src_module)
        return src_module.PROFILE

    def get_profile(self, profile: str) -> model.Profile:
        data, read_time = self._profiles.get(profile, (None, 0))
        if data is None or read_time < os.path.getmtime(f"input/{profile}.py"):
            data = self._read_profile(profile)
            self._profiles[profile] = (data, time.time())
        return data

    def needs_update(self, profile: str|None = None):
        if profile is None:
            return any(self.needs_update(p) for p in self.all_profiles())
        profile_data = self.get_profile(profile)
        template_max_mtime = 0.0
        for root, _, files in os.walk(f"templates/{profile_data.template}"):
            for file in files:
                if file.endswith(".html"):
                    mtime = os.path.getmtime(os.path.join(root, file))
                    if mtime > template_max_mtime:
                        template_max_mtime = mtime
        profile_mtime = os.path.getmtime(f"input/{profile}.py")
        output_path = f"output/{profile}.html"
        output_mtime = os.path.getmtime(output_path) if os.path.exists(output_path) else 0.0
        return profile_mtime > output_mtime or template_max_mtime > output_mtime

    def generate_html(self, profile: str|None = None):
        if profile is None:
            for profile in self.all_profiles():
                self.generate_html(profile)
            return
        print(f"[{profile}] Generating HTML...")
        profile_data = self.get_profile(profile)
        template_path = f"templates/{profile_data.template}"
        try:
            html = template.generate(template_path, profile_data)
        except Exception as e:
            print(f"[{profile}] Failed to generate HTML:", e)
            return
        os.makedirs("output", exist_ok=True)
        output_path = f"output/{profile}.html"
        with open(output_path, "wt", encoding="utf-8") as fh:
            fh.write(html)

    def generate_pdf(self, profile: str|None = None):
        if profile is None:
            for profile in self.all_profiles():
                self.generate_pdf(profile)
            return
        print(f"[{profile}] Converting to PDF...")
        with selenium.webdriver.Edge() as driver:
            html_path = f"output/{profile}.html"
            driver.get("file://" + os.path.abspath(html_path))
            options = PrintOptions()
            options.orientation = "portrait"
            # A4 in cm
            options.page_width = 21.0
            options.page_height = 29.7
            # cm
            options.margin_bottom = 0.0
            options.margin_top = 0.0
            options.margin_left = 0.0
            options.margin_right = 0.0
            options.scale = 1.0
            pdf = driver.print_page(options)
        pdf_bytes = base64.b64decode(pdf)
        os.makedirs("output", exist_ok=True)
        pdf_path = f"output/{profile}.pdf"
        with open(pdf_path, "wb") as fh:
            fh.write(pdf_bytes)


class GenerateHandler(watchdog.events.FileSystemEventHandler):
    gen: Generator

    def __init__(self, gen: Generator):
        self.gen = gen

    def on_modified(self, event):
        if self.gen.needs_update():
            self.gen.generate_html()


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--continuous", action="store_true")
    args = args.parse_args()

    gen = Generator()

    if args.continuous:
        gen.generate_html()
        observer = watchdog.observers.Observer()
        handler = GenerateHandler(gen)
        observer.schedule(handler, ".", recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    elif gen.needs_update():
        gen.generate_html()
        gen.generate_pdf()
    else:
        print("No changes detected...")
    print("Done.")
