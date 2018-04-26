import tornado


class NCCOHandler(tornado.web.RequestHandler):
    def initialize(self, host, event_url):
        self._host = host
        self._event_url = event_url
        self._template = tornado.template.Loader(".").load("ncco.sample.json")

    def get(self):
        cli = self.get_argument("from", None)
        to = self.get_argument("to", None)

        if to is None:
            self.write('parameter `to` is required')
            return

        if cli is None:
            self.write('parameter `from` is required')
            return

        cli = cli.lstrip("+")
        self.set_header("Content-Type", 'application/json')
        self.write(self._template.generate(
            host=self._host,
            event_url=self._event_url,
            lvn=to,
            cli=cli
        ))
        self.finish()
