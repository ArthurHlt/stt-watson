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
    CONTENT_TYPE = 'audio/l16;rate=44100'

    def __init__(self):
        self.configData = Config.Instance().getWatsonConfig()

    def startStt(self, audioFd):

        # logging
        log.startLogging(sys.stdout)

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
        factory = WSInterfaceFactory(audioFd,
                                     summary,
                                     self.CONTENT_TYPE,
                                     self.configData["model"],
                                     url,
                                     headers,
                                     debug=True)
        factory.protocol = WSInterfaceProtocol

        if factory.isSecure:
            contextFactory = ssl.ClientContextFactory()
        else:
            contextFactory = None
        connectWS(factory, contextFactory)

        reactor.run()
