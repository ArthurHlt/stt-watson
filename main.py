from recording.Record import Record
from watson_client.Client import Client
from utils.SignalHandler import SignalHandler
import os
import signal
import threading

stopper = threading.Event()
audioFd, writer = os.pipe()
record = Record(writer, stopper)
workers = [record]

handler = SignalHandler(stopper, workers)
signal.signal(signal.SIGINT, handler)
record.start()
# while True:
#    os.read(audioFd, 2000)
watsonClient = Client()
watsonClient.startStt(audioFd)
record.stop()
