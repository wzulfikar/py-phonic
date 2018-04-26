import tornado
from logging import info


class EventHandler(tornado.web.RequestHandler):
    def post(self):
        info(self.request.body)
        self.set_header("Content-Type", 'text/plain')
        self.write('ok')
        self.finish()
