#!/usr/bin/env python

# adapted from https://github.com/nexmo-community/audiosocket_framework

from __future__ import absolute_import, print_function

import argparse
import yaml
import logging
import sys
import os
from logging import info

import tornado.ioloop
import tornado.websocket
import tornado.httpserver
import tornado.template
import tornado.web
from tornado.web import url

from pipeline_processor import Processor, ProcessorArgs
from pipeline_frames import PipelineFrames

from routes import NCCOHandler, EventHandler
from routes.ws_handler import WSHandler, WSHandlerArgs

CLIP_MIN_MS = 200  # 200ms - the minimum audio clip that will be used
# How many continuous frames of silence determines end of a phrase
MAX_SILENCE_FRAMES = 20

# ms duration of audio being sent in each frame of the stream
MS_PER_FRAME = 20

CLIP_MIN_FRAMES = CLIP_MIN_MS // MS_PER_FRAME

# Global variables
conns = {}
clients = {}


def main(argv=sys.argv[1:]):
    try:
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--verbose", action="count", default=0)
        ap.add_argument("-c", "--config", default="./app.yml")

        args = ap.parse_args(argv)

        logging.basicConfig(
            level=logging.INFO if args.verbose < 1 else logging.DEBUG,
            format="%(levelname)7s %(message)s",
        )

        conf = yaml.safe_load(open(args.config))

        info("setting environment for google services")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = conf['gcloud']['cred_file']

        # Pass any config for the processor into this argument.
        pp_args = ProcessorArgs(
            conns=conns,
            CLIP_MIN_FRAMES=CLIP_MIN_FRAMES,
            MS_PER_FRAME=MS_PER_FRAME)
        processor = Processor(conf, pp_args)

        pipeline_frames = PipelineFrames(processor).getframes()

        ws_args = WSHandlerArgs(processor=processor,
                                pipeline_frames=pipeline_frames,
                                MAX_SILENCE_FRAMES=MAX_SILENCE_FRAMES,
                                MS_PER_FRAME=MS_PER_FRAME,
                                conns=conns,
                                clients=clients)
        application = tornado.web.Application([
            url(r"/ncco", NCCOHandler, dict(host=conf['app']['host'],
                                            event_url=conf['app']['event_url'])),
            url(r'/echo', WSHandler, dict(args=ws_args)),
            url(r'/socket', WSHandler, dict(args=ws_args)),
            url(r'/event', EventHandler),
        ])

        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(conf['app']['port'])
        info("Running on port %s", conf['app']['port'])
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass  # Suppress the stack-trace on quit


if __name__ == "__main__":
    main()
