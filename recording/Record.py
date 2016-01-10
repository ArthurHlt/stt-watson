"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio
import wave
import os
import threading
import StringIO
from config.Config import Config


class Record(threading.Thread):
    FORMAT = pyaudio.paInt16
    stopper = None

    def __init__(self, stopper):
        threading.Thread.__init__(self)
        self.p = pyaudio.PyAudio()
        self.writer = None
        self.stopper = stopper
        self.channels = Config.Instance().getChannels()
        self.rate = Config.Instance().getAudioRate()
        self.chunk = Config.Instance().getAudioChunk()

    def recording(self):
        if self.writer is None:
            raise Exception("You need to pass a fd to write data")
        stream = self.p.open(format=self.FORMAT,
                             channels=self.channels,
                             rate=self.rate,
                             input=True,
                             frames_per_buffer=self.chunk)

        print("* recording")
        while not self.stopper.is_set():
            os.write(self.writer, stream.read(self.chunk, False))
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        print 'finished recording'

    def setWriter(self, writer):
        self.writer = writer

    def getWriter(self):
        return self.writer

    def run(self):
        self.recording()
