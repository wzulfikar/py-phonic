from logging import info, debug
from concurrent.futures import ThreadPoolExecutor


class PipelineName:
    def __init__(self, pool: ThreadPoolExecutor = None):
        info('PipelineName pipeline initialized: %s', self.__class__.__name__)

        # initialize pipeline
        pass

    def process(self, count, payload, cli, args: None = None) -> str:
        debug('pipeline PipelineName is processing. thread: %s', self.pool)
        args = (count, payload, cli, args)
        if self.pool is None:
            return self._process(*args)
        else:
            future = self.pool.submit(self._process, *args)
            return future

    def _process(self, count, payload, cli, args: None = None) -> str:
        # code to process the pipeline
        pass

    def closer(self):
        """run clean-up codes when connection is closed (optional)"""
        pass

    def on_exit(self):
        """run clean-up codes when app exit (optional)"""
        self.pyaudio.terminate()
