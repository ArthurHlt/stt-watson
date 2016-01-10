from recording.Record import Record
from watson_client.Client import Client
from utils.SignalHandler import SignalHandler
from stt_watson.SttWatsonAbstractListener import SttWatsonAbstractListener
import os
import signal
import threading
import inspect


class SttWatson:
    def __init__(self):
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
