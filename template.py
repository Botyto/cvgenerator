import base64
import math
import os
import re
import time
import tornado.web
import tornado.template
from typing import Callable, List, Tuple


class B64Module(tornado.web.UIModule):
    def render(self, path: str, **kwargs):
        with open(os.path.join("includes", path), "rb") as fh:
            return base64.b64encode(fh.read()).decode("utf-8")


class MarkdownModule(tornado.web.UIModule):
    MDLINK_RE = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
    MDBOLD_RE = re.compile(r"\*\*([^\*]+)\*\*")
    MDITALIC_RE = re.compile(r"\*([^\*]+)\*")
    MDUNDERLINE_RE = re.compile(r"__([^\_]+)__")
    URL_RE = re.compile(r"(https?://|www.)[^\s]+")
    EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_RE = re.compile(r"\+?\s*(?:\d\s*){10,}")
    WHITESPACE_RE = re.compile(r"[\n\s]+")

    @staticmethod
    def mdlinkify(match: re.Match[str]):
        text = match.group(1)
        url = match.group(2)
        return f"<a href=\"{url}\" target=\"_blank\">{text}</a>"

    @staticmethod
    def linkify(match: re.Match[str]):
        url = match.group(0)
        proto_end = url.find("://")
        if proto_end != -1:
            text = url[proto_end + 3:]
        else:
            text = url
            url = "https://" + url
        if text.endswith("/"):
            text = text[:-1]
        return f"<a href=\"{url}\" target=\"_blank\">{text}</a>"
    
    @staticmethod
    def emailify(match: re.Match[str]):
        email = match.group(0)
        return f"<a href=\"mailto:{email}\">{email}</a>"
    
    @staticmethod
    def phonify(match: re.Match[str]):
        phone_text = match.group(0)
        phone_num = phone_text.replace(" ", "")
        return f"<a href=\"tel:{phone_num}\">{phone_text}</a>"

    @staticmethod
    def shrink_whitespace(match: re.Match[str]):
        return " "

    TRANSFORMERS: List[Tuple[re.Pattern, str|Callable[[re.Match[str]], str]]] = [
        (MDLINK_RE, mdlinkify),
        (MDBOLD_RE, r"<strong>\1</strong>"),
        (MDITALIC_RE, r"<em>\1</em>"),
        (MDUNDERLINE_RE, r"<u>\1</u>"),
        (URL_RE, linkify),
        (EMAIL_RE, emailify),
        (PHONE_RE, phonify),
        (WHITESPACE_RE, shrink_whitespace),
    ]

    def render(self, text: str, **kwargs):
        result = []
        while text:
            for pattern, repl in self.TRANSFORMERS:
                match = pattern.search(text)
                if match:
                    result.append(text[:match.start()])
                    if isinstance(repl, str):
                        result.append(pattern.sub(repl, text, 1))
                    else:
                        result.append(repl(match))
                    text = text[match.end():]
                    break
            else:
                result.append(text)
                text = ""
        return "".join(result)



class StylizedTemplateModule(tornado.web.TemplateModule):
    NEWLINES_RE = re.compile(rb"[\n]+")
    def render(self, path: str, **kwargs) -> bytes:
        result = super().render(path, math=math, **kwargs)
        if result.startswith(b"<style>"):
            css_end = result.find(b"</style>")
            css = result[7:css_end]
            result = result[css_end + 8:]
            if path not in self._resource_dict:
                resource = {"embedded_css": css.decode("utf-8")}
                self._resource_list.append(resource)
                self._resource_dict[path] = resource
        result = self.NEWLINES_RE.sub(b"\n", result)
        return result


class MockTornadoApplication(tornado.web.Application):
    def __init__(self, path: str):
        self.ui_methods = {}
        self.ui_modules = {}
        self.settings = {
            "template_path": path,
            "compiled_template_cache": False,
            "debug": True,
        }
        self.ui_modules = {
            "Template": StylizedTemplateModule,
            "b64": B64Module,
            "md": MarkdownModule,
        }


class MockTornadoConnection:
    content: bytes = b""

    def set_close_callback(*args, **kwargs):
        pass

    def write_headers(self, start_line, headers, chunk: bytes):
        self.content = chunk

    def finish(*args, **kwargs):
        pass


class MockTornadoRequest(tornado.httputil.HTTPServerRequest):
    def __init__(self):
        self.connection = MockTornadoConnection()
        self.headers = {}
        self.method = "GET"
        self.uri = "localhost"
        self.remote_ip = "127.0.0.1"
        self._finish_time = None
        self._start_time = time.time()


def include_b64(path: str):
    with open(os.path.join("includes", path), "rb") as fh:
        raw = fh.read()
        b64 = base64.b64encode(raw)
        return b64.decode("utf-8")


def generate(path: str, profile):
    tornado.web.RequestHandler._template_loaders.clear()
    handler = tornado.web.RequestHandler(
        MockTornadoApplication(path),
        MockTornadoRequest(),
    )
    handler._transforms = []
    namespace = {
        "profile": profile,
    }
    handler.render("index.html", **namespace)
    return handler.request.connection.content.decode("utf-8")
