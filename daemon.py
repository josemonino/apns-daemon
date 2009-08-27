###############################################################################
#
# Copyright 2009, Sri Panyam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

import threading, Queue, optparse
from twisted.internet.protocol import ClientFactory, Protocol
import constants, errors

class APNSProtocol(Protocol):
    def __init__(self, messageQueue):
        """ Initialises the protocol with the message queue. """
        self.messageQueue = messageQueue

    # 
    # After a connection is made we send out messages in our queue
    #
    def connectionMade(self):
        # dispatch any buffered messages
        while not self.messageQueue.empty():
            deviceToken, payload = self.messageQueue.get()
            self.sendMessage(deviceToken, payload)

    def dataReceived(self, data):
        print "APNS Data [(%d) bytes] Received: " % len(data), str(data)


    def formatMessage(self, deviceToken, payload):
        # notification messages are binary messages in network order 
        # using the following format: 
        # <1 byte command> <2 bytes length><token> <2 bytes length><payload>
        import struct
        fmt = "!h32sh%ds" % len(payload) 
        command     = 0
        if len(deviceToken) == 64:
            # decode it then
            deviceToken = "".join([ chr(int(deviceToken[2*i] + deviceToken[1 + 2*i], 16)) for i in xrange(0, 32) ])
        tokenLength = len(deviceToken)
        return '\x00' + struct.pack(fmt, tokenLength, deviceToken, len(payload), payload)

    def sendMessage(self, deviceToken, payload):
        msg = self.formatMessage(deviceToken, payload)
        print "Length: ", len(msg)
        # print "Msg: ", [ (ord(m), chr(ord(m))) for m in msg ]
        # self.transport.write(msg)
        self.transport.write(msg)

class APNSFactory(ClientFactory):
    def __init__(self):
        self.currProtocol = None
        self.messageQueue = Queue.Queue()

    def startedConnecting(self, connector):
        print "Started to connect...", connector

    def buildProtocol(self, addr):
        print "Building APNS Protocol to APNS Server %s:%u" % (addr.host, addr.port)
        self.currProtocol = APNSProtocol(self.messageQueue)

        return self.currProtocol

    def clientConnectionLost(self, connector, reason):
        print "Lost Connection, Reason: ", reason
        self.currProtocol = None
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Failed Connection, Reason: ", reason
        self.currProtocol = None

    def getProtocol(self):
        """ Get the current protocol. """
        print "Getting Protocol Object..."
        return self.currProtocol

    def sendMessage(self, deviceToken, payload):
        if self.currProtocol:
            self.currProtocol.sendMessage(deviceToken, payload)
        else:
            # queue it so when the protocol is built we can dispatch the
            # message
            print "Protocol not yet created.  Messaged queued..."
            self.messageQueue.put((deviceToken, payload))

class APNSDaemon(threading.Thread):
    """ 
    Maintains a list of connections to the main APNS server.
    """

    def __init__(self, reactor):
        self.reactor        = reactor
        self.connections    = {}

    def registerApp(self, app_name, certificate_file, privatekey_file,
                    apns_host       = constants.DEFAULT_APNS_DEV_HOST,
                    apns_port       = constants.DEFAULT_APNS_DEV_PORT,
                    feedback_host   = constants.DEFAULT_FEEDBACK_DEV_HOST,
                    feedback_port   = constants.DEFAULT_FEEDBACK_DEV_PORT):
        """
        Initialises a new app's connection with the APNS server so when
        time comes for requests it can be used.
        """

        if app_name in self.connections:
            raise errors.AppRegistrationError(app_name, "Application already registered")

        print "Registering Application: %s, Bundle ID: %s" % (app_name)
        from twisted.internet.ssl import DefaultOpenSSLContextFactory as SSLContextFactory
        self.connections[app_name] = {
            'num_connections':          0,
            'apns_host':                apns_host,
            'apns_port':                apns_port,
            'feedback_host':            feedback_host,
            'feedback_port':            feedback_port,
            'certificate_file':         certificate_file,
            'privatekey_file':          privatekey_file,
            'client_factory':           APNSFactory(),
            'client_context_factory':   SSLContextFactory(privatekey_file, certificate_file)
        }

    def sendMessage(self, orig_app, target_device, payload):
        """ 
        Sends a message/payload from a given app to a target device.
        """
        if orig_app not in self.connections:
            raise errors.AppRegistrationError(orig_name, "Application not registered")
        
        if len(payload) > constants.MAX_PAYLOAD_LENGTH:
            raise errors.PayloadLengthError()

        connection  = self.connections[orig_app]
        factory     = connection['client_factory']
        if connection['num_connections'] == 0:
            print "Connecting to APNS Server, App: ", orig_app
            context_factory = connection['client_context_factory']
            self.reactor.connectSSL(connection['apns_host'],
                               connection['apns_port'],
                               factory, context_factory)
            connection['num_connections'] = connection['num_connections'] + 1

        factory.sendMessage(target_device, payload)

    def run(self):
        # start the reactor
        # note we are not connecting to APN server here.  We will do this
        # the first time a notification needs to be sent.  But instead we
        # listen to connection on the local network as we are the
        # standalone daemon.  When requests arrive, 
        self.reactor.run()

