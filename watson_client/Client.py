#
# Copyright IBM Corp. 2014
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Author: Daniel Bolanos
# Date:   2015

# coding=utf-8
import os  # for listing directories
import Queue  # queue used for thread syncronization
import sys  # system calls
import base64  # necessary to encode in base64 according to the RFC2045 standard
from watson_client.websocket.WSInterfaceProtocol import WSInterfaceProtocol
from watson_client.websocket.WSInterfaceFactory import WSInterfaceFactory
from utils.Utils import Utils
from config.Config import Config
# WebSockets 
from autobahn.twisted.websocket import connectWS
from twisted.python import log
from twisted.internet import ssl, reactor


class Client:
    def __init__(self):
        self.configData = Config.Instance().getWatsonConfig()

    def startStt(self):
        # create output directory if necessary
        if (os.path.isdir(self.configData["dirOutput"])):
            while True:
                answer = raw_input(
                    "the output directory \"" + self.configData["dirOutput"] + "\" already exists, overwrite? (y/n)? ")
                if (answer == "n"):
                    sys.stderr.write("exiting...")
                    sys.exit()
                elif (answer == "y"):
                    break
        else:
            os.makedirs(self.configData["dirOutput"])

        # logging
        log.startLogging(sys.stdout)

        # add audio files to the processing queue
        q = Queue.Queue()
        lines = [line.rstrip('\n') for line in open(self.configData["fileInput"])]
        fileNumber = 0
        for fileName in (lines):
            print fileName
            q.put((fileNumber, fileName))
            fileNumber += 1

        hostname = "stream.watsonplatform.net"
        headers = {}

        # authentication header
        if self.configData["tokenauth"]:
            headers['X-Watson-Authorization-Token'] = Utils.getAuthenticationToken("https://" + hostname,
                                                                                   'speech-to-text',
                                                                                   self.configData["user"],
                                                                                   self.configData["password"])
        else:
            string = self.configData["user"] + ":" + self.configData["password"]
            headers["Authorization"] = "Basic " + base64.b64encode(string)

        # create a WS server factory with our protocol
        url = "wss://" + hostname + "/speech-to-text/api/v1/recognize?model=" + self.configData["model"]
        summary = {}
        factory = WSInterfaceFactory(q, summary,
                                     self.configData["dirOutput"],
                                     self.configData["contentType"],
                                     self.configData["model"],
                                     url,
                                     headers,
                                     debug=False)
        factory.protocol = WSInterfaceProtocol

        for i in range(min(int(self.configData["threads"]), q.qsize())):

            factory.prepareUtterance()

            # SSL client context: default
            if factory.isSecure:
                contextFactory = ssl.ClientContextFactory()
            else:
                contextFactory = None
            connectWS(factory, contextFactory)

        reactor.run()

        # dump the hypotheses to the output file
        fileHypotheses = self.configData["dirOutput"] + "/hypotheses.txt"
        f = open(fileHypotheses, "w")
        counter = 1
        successful = 0
        emptyHypotheses = 0
        for key, value in (sorted(summary.items())):
            if value['status']['successful'] == True:
                print key, ": ", value['status']['code'], " ", value['hypothesis'].encode('utf-8')
                successful += 1
                if value['hypothesis'][0] == "":
                    emptyHypotheses += 1
            else:
                print key + ": ", value['status']['code'], " REASON: ", value['status']['reason']
            f.write(str(counter) + ": " + value['hypothesis'].encode('utf-8') + "\n")
            counter += 1
        f.close()
        print "successful sessions: ", successful, " (", len(summary) - successful, " errors) (" + str(
            emptyHypotheses) + " empty hypotheses)"
