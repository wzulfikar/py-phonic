import os
import time
from typing import NamedTuple
from logging import debug, error, info
from concurrent.futures import ThreadPoolExecutor

# import pipelines
from pipelines.gcloud_uploader import GCloudUploader, GCloudUploaderArgs
from pipelines.recorder import Recorder, RecorderArgs
from pipelines.playback import Playback, PlaybackArgs
from pipelines.speech import Speech
from pipelines.pyaudio import Pyaudio


class PipelineException(Exception):
    pass


class ProcessorArgs(NamedTuple):
    conns: dict
    # the minimum audio clip that will be used
    CLIP_MIN_FRAMES: int

    # ms duration of each frame in the stream
    MS_PER_FRAME: int


class Processor(object):
    def __init__(self, conf: dict, args: ProcessorArgs):
        self.args = args

        default_pool = ThreadPoolExecutor()

        """initialize pipelines"""
        info('registering pipelines..')
        self.p = {
            'recorder': Recorder(conf['app']['storage'], pool=default_pool),
            'gc_uploader': GCloudUploader(conf['gcloud'], pool=default_pool),
            'playback': Playback(pool=default_pool),
            'speech': Speech(),
            'pyaudio': Pyaudio(),
        }

        """initialize deferred_threads"""
        self.deferred_threads = {}

    def safe_pipelines(self, names: list):
        """validate given names with available pipelines"""
        for name in names:
            if name not in self.p:
                raise PipelineException('invalid pipeline name:', name)

        return names

    def pipelines(self,
                  pipelines: list,
                  count: int,
                  payload: bytes,
                  cli: str):
        """put your pipelines here"""

        duration_ms = count * self.args.MS_PER_FRAME
        duration_secs = round(duration_ms / 1000, 1)
        debug('- processing pipeline: %d frames of %dms per frame (%.1f) secs)',
              count,
              self.args.MS_PER_FRAME,
              duration_secs)

        if 'speech' in pipelines:
            self.p['speech'].process(count,
                                     payload,
                                     cli)

        if 'pyaudio' in pipelines:
            self.p['pyaudio'].process(count,
                                      payload,
                                      cli)

        file = None
        if 'recorder' in pipelines:
            file = self.p['recorder'].process(count,
                                              payload,
                                              cli,
                                              RecorderArgs(self.args.CLIP_MIN_FRAMES))

        if 'gc_uploader' in pipelines:
            if file is None:
                error('pipeline skipped: gc_uploader file is empty')
            else:
                self.p['gc_uploader'].process(count,
                                              payload,
                                              cli,
                                              GCloudUploaderArgs(file, 'call_objects'))

        if 'playback' in pipelines and cli in self.args.conns:
            self.p['playback'].process(count,
                                       payload,
                                       cli,
                                       PlaybackArgs(self.args.conns[cli]))
