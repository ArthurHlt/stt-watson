# coding=utf-8
import json  # json
import os  # for listing directories
# WebSockets
from autobahn.twisted.websocket import WebSocketClientProtocol, connectWS
from twisted.internet import ssl
from config.Config import Config


# WebSockets interface to the STT service
# note: an object of this class is created for each WebSocket connection, every time we call connectWS
class WSInterfaceProtocol(WebSocketClientProtocol):
    def __init__(self, factory, audioFd, summary, contentType):
        self.listeners = []
        self.audioFd = audioFd
        self.factory = factory
        self.summary = summary
        self.contentType = contentType
        self.packetRate = 20
        self.listeningMessages = 0
        self.timeFirstInterim = -1
        self.bytesSent = 0
        self.chunkSize = Config.Instance().getAudioChunk()  # in bytes
        super(self.__class__, self).__init__()
        print "contentType: " + str(self.contentType)

    def setListeners(self, listeners):
        self.listeners = listeners

    def getListeners(self):
        return self.listeners

    def setUtterance(self):

        self.summary = {"hypothesis": "",
                        "status": {"code": "", "reason": ""}}

    # helper method that sends a chunk of audio if needed (as required what the specified pacing is)
    def maybeSendChunk(self):

        def sendChunk(chunk, final=False):
            self.sendMessage(chunk, isBinary=True)

        chunk = os.read(self.audioFd, self.chunkSize)
        sendChunk(chunk)
        self.factory.reactor.callLater(0.01, self.maybeSendChunk)
        return

    def onConnect(self, response):
        print "onConnect, server connected: {0}".format(response.peer)

    def onOpen(self):
        print "onOpen"
        data = {"action": "start", "content-type": str(self.contentType), "continuous": True, "interim_results": True,
                "inactivity_timeout": 600}
        data['word_confidence'] = True
        data['timestamps'] = True
        data['max_alternatives'] = 3
        print "sendMessage(init)"
        # send the initialization parameters
        self.sendMessage(json.dumps(data).encode('utf8'))
        # start sending audio right away (it will get buffered in the STT service)
        self.bytesSent = 0
        self.maybeSendChunk()
        print "onOpen ends"

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            # print(u"Text message received: {0}".format(payload.decode('utf8')))

            # if uninitialized, receive the initialization response from the server
            jsonObject = json.loads(payload.decode('utf8'))
            if 'state' in jsonObject:
                self.listeningMessages += 1
                if (self.listeningMessages == 2):
                    print "sending close 1000"
                    # close the connection
                    self.sendClose(1000)

            # if in streaming
            elif 'results' in jsonObject:
                jsonObject = json.loads(payload.decode('utf8'))
                hypothesis = ""
                # empty hypothesis
                if (len(jsonObject['results']) == 0):
                    print "empty hypothesis!"
                # regular hypothesis
                else:
                    hypothesis = jsonObject['results'][0]['alternatives'][0]['transcript']
                    bFinal = (jsonObject['results'][0]['final'] == True)
                    transcripts = self.extractTranscripts(jsonObject['results'][0]['alternatives'])

                    if bFinal:
                        self.notifyListeners(payload.decode('utf8'), transcripts)
                        # print "final hypothesis: \"" + hypothesis + "\""
                        self.summary['hypothesis'] += hypothesis
                    else:
                        self.notifyListeners(payload.decode('utf8'), None, transcripts)
                        # print "interim hyp: \"" + hypothesis + "\""

    def extractTranscripts(self, alternatives):
        transcripts = []
        for alternative in alternatives:
            transcript = {}
            if 'confidence' in alternative:
                transcript['confidence'] = alternative['confidence']
            transcript['transcript'] = alternative['transcript']
            transcripts.append(transcript)
        return transcripts

    def notifyListeners(self, payload, hypothesis=None, interimHypothesis=None):
        for listener in self.listeners:
            listener.listenPayload(payload)
            if hypothesis is not None:
                listener.listenHypothesis(hypothesis)
            if interimHypothesis is not None:
                listener.listenInterimHypothesis(interimHypothesis)

    def onClose(self, wasClean, code, reason):

        print("onClose")
        print(
            "WebSocket connection closed: {0}".format(reason), "code: ", code, "clean: ", wasClean, "reason: ", reason)
        self.summary['status']['code'] = code
        self.summary['status']['reason'] = reason
        if (code == 1000):
            self.summary['status']['successful'] = True

        if self.factory.prepareUtterance() == False:
            return

        # SSL client context: default
        if self.factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(self.factory, contextFactory)
