"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio
import wave
import os
import threading
import StringIO
from config.Config import Config


class Record(threading.Thread):
    CHUNK = Config.Instance().getAudioChunk()
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = Config.Instance().getAudioRate()
    stopper = None

    def __init__(self, writer, stopper):
        threading.Thread.__init__(self)
        self.p = pyaudio.PyAudio()
        self.writer = writer
        self.stopper = stopper

    def recording(self):
        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)

        print("* recording")
        while not self.stopper.is_set():
            os.write(self.writer, stream.read(self.CHUNK, False))
        stream.stop_stream()
        stream.close()
        self.p.terminate()
        print 'finished recording'

    def write_wav_file(self, data):
        buffer = StringIO.StringIO()
        wf = wave.open(buffer, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(data)
        wf.close()
        buffer.flush()
        return buffer.getvalue()

    def run(self):
        self.recording()
