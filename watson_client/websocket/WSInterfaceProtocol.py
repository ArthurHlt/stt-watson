# coding=utf-8
import json  # json
import os  # for listing directories
# WebSockets
from autobahn.twisted.websocket import WebSocketClientProtocol, connectWS
from twisted.internet import ssl


# WebSockets interface to the STT service
# note: an object of this class is created for each WebSocket connection, every time we call connectWS
class WSInterfaceProtocol(WebSocketClientProtocol):
    def __init__(self, factory, queue, summary, dirOutput, contentType):
        self.factory = factory
        self.queue = queue
        self.summary = summary
        self.dirOutput = dirOutput
        self.contentType = contentType
        self.packetRate = 20
        self.listeningMessages = 0
        self.timeFirstInterim = -1
        self.bytesSent = 0
        self.chunkSize = 2000  # in bytes
        super(self.__class__, self).__init__()
        print dirOutput
        print "contentType: " + str(self.contentType) + " queueSize: " + str(self.queue.qsize())

    def setUtterance(self, utt):

        self.uttNumber = utt[0]
        self.uttFilename = utt[1]
        self.summary[self.uttNumber] = {"hypothesis": "",
                                        "status": {"code": "", "reason": ""}}
        self.fileJson = self.dirOutput + "/" + str(self.uttNumber) + ".json.txt"
        try:
            os.remove(self.fileJson)
        except OSError:
            pass

    # helper method that sends a chunk of audio if needed (as required what the specified pacing is)
    def maybeSendChunk(self, data):

        def sendChunk(chunk, final=False):
            self.bytesSent += len(chunk)
            self.sendMessage(chunk, isBinary=True)
            if final:
                self.sendMessage(b'', isBinary=True)

        if (self.bytesSent + self.chunkSize >= len(data)):
            if (len(data) > self.bytesSent):
                sendChunk(data[self.bytesSent:len(data)], True)
                return
        sendChunk(data[self.bytesSent:self.bytesSent + self.chunkSize])
        self.factory.reactor.callLater(0.01, self.maybeSendChunk, data=data)
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
        print self.uttFilename
        f = open(str(self.uttFilename), 'rb')
        self.bytesSent = 0
        dataFile = f.read()
        self.maybeSendChunk(dataFile)
        print "onOpen ends"

    def onMessage(self, payload, isBinary):

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print(u"Text message received: {0}".format(payload.decode('utf8')))

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
                    # dump the message to the output directory
                    jsonObject = json.loads(payload.decode('utf8'))
                    f = open(self.fileJson, "a")
                    f.write(json.dumps(jsonObject, indent=4, sort_keys=True))
                    f.close()

                    hypothesis = jsonObject['results'][0]['alternatives'][0]['transcript']
                    bFinal = (jsonObject['results'][0]['final'] == True)
                    if bFinal:
                        print "final hypothesis: \"" + hypothesis + "\""
                        self.summary[self.uttNumber]['hypothesis'] += hypothesis
                    else:
                        print "interim hyp: \"" + hypothesis + "\""

    def onClose(self, wasClean, code, reason):

        print("onClose")
        print(
            "WebSocket connection closed: {0}".format(reason), "code: ", code, "clean: ", wasClean, "reason: ", reason)
        self.summary[self.uttNumber]['status']['code'] = code
        self.summary[self.uttNumber]['status']['reason'] = reason
        if (code == 1000):
            self.summary[self.uttNumber]['status']['successful'] = True

        # create a new WebSocket connection if there are still utterances in the queue that need to be processed
        self.queue.task_done()

        if self.factory.prepareUtterance() == False:
            return

        # SSL client context: default
        if self.factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(self.factory, contextFactory)
