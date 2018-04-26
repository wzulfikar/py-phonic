from logging import debug, info
from concurrent.futures import ThreadPoolExecutor

import webrtcvad


class Speech:
    def __init__(self, pool: ThreadPoolExecutor = None):
        info('pipeline initialized: %s', self.__class__.__name__)
        self.pool = pool

        self.SAMPLE_RATE = 16000
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1)  # Level of sensitivity

    def process(self, count, payload, cli, args: None = None) -> None:
        debug('speech pipeline is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            self._process(*args)
        else:
            self.pool.submit(self._process, *args)

    def _process(self, count, payload, cli, args: None = None) -> None:
        try:
            if self.vad.is_speech(payload, self.SAMPLE_RATE):
                print("got speech from {}".format(cli))
            else:
                print("got silence from {}".format(cli))

        except Exception as e:
            debug("error checking vad.is_speech: %s", e)
