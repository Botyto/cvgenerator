import argparse
import importlib
import os
import tornado.template

import data

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
    template_path = os.path.join("templates", template)
    with open(template_path, "rt", encoding="utf-8") as fh:
        template = tornado.template.Template(fh.read())
    html = template.generate(profile=profile)
    with open(output, "wb") as fh:
        fh.write(html)
    return output

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--src", type=str, default="details")
    args.add_argument("--template", type=str, default="markdown.html")
    args = args.parse_args()
    out = generate(args.src, args.template)
