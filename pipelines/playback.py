import time
from typing import NamedTuple
from logging import debug, info
from concurrent.futures import ThreadPoolExecutor

import tornado


class PlaybackArgs(NamedTuple):
    conn: tornado.websocket.WebSocketHandler


class Playback:
    def __init__(self, pool: ThreadPoolExecutor = None):
        """playback the stream to given websocket connection"""

        info('pipeline initialized: %s', self.__class__.__name__)

        self.pool = pool
        pass

    def process(self, count, payload, cli, args: PlaybackArgs = None) -> None:
        # TODO: complete the pipeline
        print('[SKIP] playback pipeline is still WIP')
        return

        debug('playback pipeline is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            self._process(*args)
        else:
            self.pool.submit(self._process, *args)

    def _process(self, count, payload, cli, args: PlaybackArgs) -> None:
        BYTES_PER_FRAME = 640  # Bytes in a frame

        frames = len(payload) // BYTES_PER_FRAME
        debug("playing {} frames to {}".format(frames, cli))
        pos = 0
        for x in range(0, frames + 1):
            newpos = pos + BYTES_PER_FRAME
            debug("writing bytes {} to {} to socket for {}".format(pos,
                                                                   newpos,
                                                                   cli))
            data = payload[pos:newpos]
            args.conn.write_message(data, binary=True)

            # wait the frame stream to finish
            # time.sleep(0.018)

            pos = newpos
