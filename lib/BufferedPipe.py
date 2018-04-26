from logging import debug


class BufferedPipe(object):
    def __init__(self,
                 max_frames: int,
                 sink,
                 pipelines: list,
                 name: str = None):
        """
        Create a buffer which will call the provided `sink` when full.
        It will call `sink` with the number of frames and the accumulated
        bytes when it reaches `max_buffer_size` frames.

        pass list of `pipelines` as arg to process this buffer
        using specified pipelines only (not all pipelines)
        """
        self.max_frames = max_frames
        self.sink = sink
        self.pipelines = pipelines
        self.name = name

        self.count = 0
        self.payload = b''

    def append(self, data, cli):
        """
        Add another data to the buffer. `data` should be a `bytes` object.
        """

        self.count += 1
        self.payload += data

        debug('BufferedPipe count: {}, max frames: {}'.format(
            self.count, self.max_frames))

        if self.count == self.max_frames:
            debug("BufferedPipe is full. Executing pipelines..")
            self.process(cli)

    def process(self, cli):
        """ Process and clear the buffer. """
        self.sink(self.pipelines, self.count, self.payload, cli)
        self.count = 0
        self.payload = b''
