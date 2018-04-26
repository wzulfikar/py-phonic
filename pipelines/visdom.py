from logging import info, debug

import visdom
from concurrent.futures import ThreadPoolExecutor


class Visdom:
    def __init__(self, pool: ThreadPoolExecutor = None):
        """push analytic data to visdom endpoint"""

        info('pipeline initialized: %s', self.__class__.__name__)

        self.SAMPLE_RATE = 16000
        self.v = visdom.Visdom()

    def process(self, count, payload, cli, args: None = None) -> str:
        # TODO: complete the pipeline
        print('[SKIP] visdom pipeline is still WIP')
        return

        debug('processing PipelineName pipeline. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            self._process(*args)
        else:
            self.pool.submit(self._process, *args)

    def _process(self, count, payload, cli, args: None = None) -> str:
        try:
            if self.vad.is_speech(payload, self.SAMPLE_RATE):
                print("SPEECH from {}".format(cli))
            else:
                print("silence from {}".format(cli))

        except Exception as e:
            print("error checking vad.is_speech:", e)
