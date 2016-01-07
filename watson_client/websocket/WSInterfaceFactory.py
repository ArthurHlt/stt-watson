# coding=utf-8
import threading  # multi threading
import Queue  # queue used for thread syncronization

# WebSockets
from autobahn.twisted.websocket import WebSocketClientFactory
from WSInterfaceProtocol import WSInterfaceProtocol
from twisted.internet import ssl, reactor


class WSInterfaceFactory(WebSocketClientFactory):
    def __init__(self, queue, summary, dirOutput, contentType, model, url=None, headers=None, debug=None):

        WebSocketClientFactory.__init__(self, url=url, headers=headers, debug=debug)
        self.queue = queue
        self.summary = summary
        self.dirOutput = dirOutput
        self.contentType = contentType
        self.model = model
        self.queueProto = Queue.Queue()

        self.openHandshakeTimeout = 6
        self.closeHandshakeTimeout = 6

        # start the thread that takes care of ending the reactor so the script can finish automatically (without ctrl+c)
        endingThread = threading.Thread(target=self.endReactor, args=())
        endingThread.daemon = True
        endingThread.start()

    def prepareUtterance(self):

        try:
            utt = self.queue.get_nowait()
            self.queueProto.put(utt)
            return True
        except Queue.Empty:
            print "getUtterance: no more utterances to process, queue is empty!"
            return False

    def endReactor(self):

        self.queue.join()
        print "about to stop the reactor!"
        reactor.stop()

    # this function gets called every time connectWS is called (once per WebSocket connection/session)
    def buildProtocol(self, addr):

        try:
            utt = self.queueProto.get_nowait()
            proto = WSInterfaceProtocol(self, self.queue, self.summary, self.dirOutput, self.contentType)
            proto.setUtterance(utt)
            return proto
        except Queue.Empty:
            print "queue should not be empty, otherwise this function should not have been called"
            return None
