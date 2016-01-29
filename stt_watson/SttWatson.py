import os
import signal
import threading

from config.Config import Config
from recording.Record import Record
from stt_watson.SttWatsonAbstractListener import SttWatsonAbstractListener
from utils.SignalHandler import SignalHandler
from watson_client.Client import Client


class SttWatson:
    default_config = {
        'audio-chunk': 8000,
        'audio-rate': 44100,
        'channels': 1,
        'watson-stt': {
            'user': None,
            'password': None,
            'model': 'en-US_BroadbandModel',
            'tokenauth': None,
        }
    }

    def __init__(self, user, password, model=None, rate=None, chunk=None, channels=None):
        if not Config.Instance().getConfig():
            Config.Instance().setConfig(self.default_config)
        watsonConfig = Config.Instance().getWatsonConfig()
        watsonConfig["user"] = user
        watsonConfig["password"] = password
        if model is not None:
            watsonConfig["model"] = model
        if chunk is not None:
            Config.Instance().setAudioChunk(chunk)
        if rate is not None:
            Config.Instance().setAudioRate(rate)
        if channels is not None:
            Config.Instance().setChannels(channels)
        Config.Instance().setWatsonConfig(watsonConfig)
        self.listeners = []
        self.stopper = threading.Event()
        self.record = Record(self.stopper)
        self.workers = [self.record]
        self.watsonClient = Client()
        self.handler = SignalHandler(self.stopper, self.workers)
        signal.signal(signal.SIGINT, self.handler)

    def addListener(self, listener):
        if not isinstance(listener, SttWatsonAbstractListener):
            raise Exception("Listener added is not a derived class from SttWatsonAbstractListener")
        self.listeners.append(listener)

    def pauseRecord(self):
        self.record.pauseRecord()

    def continuRecord(self):
        self.record.continuRecord()

    def setListeners(self, listeners):
        if listeners is not list:
            listeners = [listeners]
        for listener in listeners:
            self.addListener(listener)

    def getListeners(self):
        return self.listeners

    def run(self):
        audioFd, writer = os.pipe()
        self.record.setWriter(writer)
        self.record.start()
        self.watsonClient.setListeners(self.listeners)
        self.watsonClient.startStt(audioFd)
