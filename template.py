import os
import re
import time
import tornado.web
import tornado.template


class SvgModule(tornado.web.UIModule):
    def render(self, path: str, **kwargs):
        with open(os.path.join("includes", path), "rb") as fh:
            return fh.read()


class MarkdownModule(tornado.web.UIModule):
    URL_RE = re.compile(r"https?://[^\s]+")
    EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    BOLD_RE = re.compile(r"\*\*([^\*]+)\*\*")
    ITALIC_RE = re.compile(r"\*([^\*]+)\*")
    UNDERLINE_RE = re.compile(r"__([^\_]+)__")
    WHITESPACE_RE = re.compile(r"[\n\s]+")

    def linkify(self, match: re.Match[str]):
        url = match.group(0)
        href = url
        proto_end = url.find("://")
        url = url[proto_end + 3:]
        return f"<a href=\"{href}\">{url}</a>"
    
    def emailify(self, match: re.Match[str]):
        email = match.group(0)
        return f"<a href=\"mailto:{email}\">{email}</a>"
    
    def shirnk_whitespace(self, match: re.Match[str]):
        return " "

    def render(self, text: str, **kwargs):
        text = self.URL_RE.sub(self.linkify, text)
        text = self.EMAIL_RE.sub(self.emailify, text)
        text = self.BOLD_RE.sub(r"<strong>\1</strong>", text)
        text = self.ITALIC_RE.sub(r"<em>\1</em>", text)
        text = self.UNDERLINE_RE.sub(r"<u>\1</u>", text)
        text = self.WHITESPACE_RE.sub(self.shirnk_whitespace, text)
        return text


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
            "Template": tornado.web.TemplateModule,
            "Svg": SvgModule,
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
