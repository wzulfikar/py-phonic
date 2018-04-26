from logging import info, debug
from concurrent.futures import ThreadPoolExecutor

import pyaudio


class Pyaudio:
    def __init__(self, pool: ThreadPoolExecutor = None):
        info('pipeline initialized: %s', self.__class__.__name__)

        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.pool = pool

    def process(self, count, payload, cli, args: None = None) -> None:
        debug('pyaudio pipeline is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            self._process(*args)
        else:
            self.pool.submit(self._process, *args)

    def _process(self, count, payload, cli, args: None = None) -> None:
        if not self.stream:
            fmt = self.pyaudio.get_format_from_width(2)
            self.stream = self.pyaudio.open(format=fmt,
                                            channels=1,
                                            rate=16000,
                                            output=True)

        # uncomment to play voice onlye if speech is detected
        # if self.vad.is_speech(payload, 16000):
            # self.stream.write(payload)

        self.stream.write(payload)

    def closer(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def on_exit(self):
        """run clean-up codes when app exit"""
        self.pyaudio.terminate()
