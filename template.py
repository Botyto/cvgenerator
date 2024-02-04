import os
import time
import tornado.web
import tornado.template


class SvgModule(tornado.web.UIModule):
    def render(self, path: str, **kwargs) -> bytes:
        with open(os.path.join("includes", path), "rb") as fh:
            return fh.read()


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
