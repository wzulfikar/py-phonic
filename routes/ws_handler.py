from typing import NamedTuple, List

from logging import debug, info
import tornado
import json

from lib.BufferedPipe import BufferedPipe
from pipeline_processor import Processor, PipelineException


class WSHandlerArgs(NamedTuple):
    processor: Processor
    pipeline_frames: List[BufferedPipe]
    conns: dict
    clients: dict
    MAX_SILENCE_FRAMES: int
    MS_PER_FRAME: int


class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, args: WSHandlerArgs):
        self.args = args

        self.client_id = None

        self.processor = args.processor
        self.pipeline_frames = args.pipeline_frames

        # Setup the Voice Activity Detector
        self.tick = None
        self.cli = None

    def check_origin(self, origin):
        return True

    def open(self):
        self.client_id = 'client_{}'.format(len(self.args.clients) + 1)
        self.args.clients[self.client_id] = self
        info("new client connection: %s", self.client_id)
        info("total clients connected: %d", len(self.args.clients))

        # Add the connection to the list of connections
        self.args.conns[self.client_id] = self

    def on_message(self, message):
        # handle string message
        if type(message) is str:
            if self.request.path == "/echo":
                info('echo from %s: %s', self.client_id, message)
                self.write_message(message)
                return

            info("new websocket string message: %s", message)
            # Here we should be extracting the meta data
            # that was sent and attaching it to the connection object
            try:
                data = json.loads(message)
                self.cli = data['cli']
                self.args.conns[self.cli] = self
                self.write_message('ok')
            except Exception as e:
                self.write_message('something went wrong: {}'.format(e))
            return

        """handle binary message"""

        # TODO: adjust for client
        if self.cli not in self.args.conns:
            self.args.conns[self.cli] = self

        # append message to frame buffer
        for frame_buffer in self.pipeline_frames:
            frame_buffer.append(message, self.cli)

    def on_close(self):
        # Remove the connection from the list of connections
        if self.cli in self.args.conns:
            del self.args.conns[self.cli]

        del self.args.clients[self.client_id]
        print("closing connection from ", self.client_id, ":")

        for buffered_pipe in self.pipeline_frames:
            if buffered_pipe.count > 0:
                print("- processing frame buffer residue:", buffered_pipe.name)
                buffered_pipe.process(self.cli)

        # close pipelines if method `close()` is found
        print("- executing pipeline `closer` method..")
        for pipeline_name, pipeline in self.processor.p.items():
            if hasattr(pipeline, 'closer') and callable(getattr(pipeline, 'closer')):
                pipeline.closer()
                print("pipeline closed:", pipeline_name)

        if len(self.processor.deferred_threads) > 0:
            dthreads = len(self.processor.deferred_threads)
            print("- processing deferred threads ({})".format(len(dthreads)))
            for i, t in dthreads.items():
                t.start()
                del self.processor.deferred_threads[i]

        print("-", self.client_id, "disconnected")
