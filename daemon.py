#!/bin/env python2.5

import binascii, threading, struct, os, Queue
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.ssl import ClientContextFactory
from twisted.internet.ssl import DefaultOpenSSLContextFactory as SSLContextFactory
import constants

MAX_PAYLOAD_LENGTH = 256

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

# 
# Maintains a list of connections to the main APNS server.
#
class APNSDaemon(threading.Thread):
    def __init__(self):
        self.connections = {}

    # 
    # Initialises a new app's connection with the APNS server so 
    # when time comes for requests it can be used.
    #
    def registerApp(self, app_name, bundle_id, certificate_file, privatekey_file,
                    apns_host, apns_port, feedback_host, feedback_port):
        # TODO: What if the app is already registered and we also have
        # connections open
        print "Registering Application: %s, Bundle ID: %s" % (app_name, bundle_id)
        self.connections[app_name] = {
            'num_connections':          0,
            'apns_host':                apns_host,
            'apns_port':                apns_port,
            'feedback_host':            feedback_host,
            'feedback_port':            feedback_port,
            'bundle_id':                bundle_id,
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
            print "App Not Registered: ", orig_app
            return False
        
        if len(payload) > MAX_PAYLOAD_LENGTH:
            raise ValueError("Payload too large.  Cannot exceed %d bytes" % MAX_PAYLOAD_LENGTH)

        connection  = self.connections[orig_app]
        factory     = connection['client_factory']
        if connection['num_connections'] == 0:
            print "Connecting to APNS Server, App Bundle ID: ", orig_app, connection['bundle_id']
            context_factory = connection['client_context_factory']
            reactor.connectSSL(connection['apns_host'],
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
        import line_client
        reactor.listenTCP(90, line_client.LineProtocolFactory(self))
        reactor.run()

def main():
    daemon = APNSDaemon()
    # register all apps here
    daemon.registerApp("metjungle", "8K9U92BL7X.com.metjungle.pickmeup",
                       os.path.abspath("certs/CertificateFile.pem"),
                       os.path.abspath("certs/PrivateKeyFile.pem"),
                       constants.DEFAULT_APNS_DEV_HOST,
                       constants.DEFAULT_APNS_DEV_PORT,
                       constants.DEFAULT_FEEDBACK_DEV_HOST,
                       constants.DEFAULT_FEEDBACK_DEV_PORT)
    daemon.run()

if __name__ == "__main__":
    main()

