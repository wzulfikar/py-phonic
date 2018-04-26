from typing import NamedTuple
import datetime
import wave
import os
import string
import random
from logging import debug, info
from concurrent.futures import ThreadPoolExecutor


class RecorderArgs(NamedTuple):
    CLIP_MIN_FRAMES: int


class Recorder:
    def __init__(self, storage_path: str, pool: ThreadPoolExecutor = None):
        info('pipeline initialized: %s', self.__class__.__name__)

        self.storage_path = storage_path
        self.pool = pool

    def _randseq(self, n):
        return ''.join(random.choice(string.ascii_letters) for x in range(n))

    def process(self, count, payload, cli, args: RecorderArgs) -> str:
        debug('recorder pipeline is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            return self._process(*args)
        else:
            future = self.pool.submit(self._process, *args)
            debug('recorder future: %s', future)
            return future

    def _process(self, count, payload, cli, args: RecorderArgs) -> str:
        # ignore if the buffer is less than CLIP_MIN_FRAMES
        if count >= args.CLIP_MIN_FRAMES:
            debug('Processing %d frames from %s', count, cli)
            recording_path = '{}/recordings'.format(self.storage_path)
            if not os.path.exists(recording_path):
                debug("- creating recordings storage at %s", recording_path)
                os.makedirs(recording_path)

            now = datetime.datetime.now()
            filename = "{}/{}-{}-{}.wav".format(recording_path,
                                                now.strftime("%Y%m%dT%H%M%S"),
                                                cli,
                                                self._randseq(5))

            output = wave.open(filename, 'wb')
            output.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
            output.writeframes(payload)
            output.close()
            debug('File written {}'.format(filename))

            return filename
        else:
            debug('Discarding {} frames'.format(str(count)))
            return
