"""PyAudio example: Record a few seconds of audio and save to a WAVE file."""

import pyaudio
import wave
import os


class Record:
    CHUNK = 2000
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    def __init__(self):
        self.p = pyaudio.PyAudio()

    def recording(self, writer):

        stream = self.p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             frames_per_buffer=self.CHUNK)

        print("* recording")
        while(True):
            os.write(writer, stream.read(self.CHUNK))
        stream.stop_stream()
        stream.close()
        self.p.terminate()

#    def write_wav_file(self):
#        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
#        wf.setnchannels(self.CHANNELS)
#        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
#        wf.setframerate(self.RATE)
#        wf.writeframes(b''.join(self.frames))
#        wf.close()

    def start(self):
        self.recording()
        self.write_wav_file()
