from typing import List
from logging import info

from lib.BufferedPipe import BufferedPipe
from pipeline_processor import Processor, PipelineException


class PipelineFrames:
    def __init__(self, processor: Processor):
        self.processor = processor
        self.MS_PER_FRAME = processor.args.MS_PER_FRAME

        # Create a buffer which will call `process` when it is full:
        live_frame = 1

        # calculate max_frames to process buffer every 2 seconds max
        max_frames_2_secs = int(1000 * 2 / self.MS_PER_FRAME)

        # process long buffer every 60 mins max
        max_frames_60_mins = int(1000 * 60 * 60 / self.MS_PER_FRAME)

        # adjust this code to manage your pipelines
        info('mapping frames with pipelines')
        self.frame_to_pipelines = {
            'live_frame': dict(max_frames=live_frame, pipelines=[
                'playback',
                'pyaudio',
                'speech']),
            '60_mins_frame': dict(max_frames=max_frames_60_mins, pipelines=[
                'recorder',
                'gc_uploader']),
        }

    def getframes(self) -> List[BufferedPipe]:
        frames = []
        try:
            counter = 0
            for frame_name, frame in self.frame_to_pipelines.items():
                counter += 1
                info('pipeline #%d: %s → %s',
                     counter, frame_name, frame['pipelines'])
                buff = BufferedPipe(
                    frame['max_frames'],
                    self.processor.pipelines,
                    self.processor.safe_pipelines(frame['pipelines']),
                    frame_name)
                frames.append(buff)

            return frames

        except PipelineException as e:
            print('invalid pipeline', e)
            return
