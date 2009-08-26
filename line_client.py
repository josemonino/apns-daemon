
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory, Protocol

class LineProtocol(LineReceiver):
    """
    This is the actual receiver of payload from local applications (or
    anywhere really) and forwards the received messages to the APNS daemon
    to be sent off to APNS land.
    """
    def __init__(self, daemon):
        self.apns_daemon    = daemon

    def lineReceived(self, line):
        print "Received Line: ", line
        # each line will have 3 thinsgs - appname,deviceToken,payload
        coma1 = line.find(",")
        coma2 = line.find(",", coma1 + 1)

        if coma1 <= 0 or coma2 <= 0:
            print "Disconnecting.  Invalid line: ", line
            self.transport.loseConnection()
            return 

        app_name        = line[ : coma1]
        device_token    = line[coma1 + 1 : coma2]
        payload         = line[coma2 + 1 : ]
        self.apns_daemon.sendMessage(app_name, device_token, payload)

class LineProtocolFactory(Factory):
    """
    Factory responsible for handling life cycle of LineProtocol objects.
    """
    def __init__(self, daemon):
        self.apns_daemon = daemon

    def startedConnecting(self, connector):
        print "Started LineClient connection..."

    def buildProtocol(self, addr):
        print "Building LineProtocol Server %s:%u" % (addr.host, addr.port)
        return LineProtocol(self.apns_daemon)

    def clientConnectionLost(self, connector, reason):
        print "Lost Connection, Reason: ", reason

    def clientConnectionFailed(self, connector, reason):
        print "Failed Connection, Reason: ", reason

class LineClient(object):
    """
    A helper class used by applications for sending messages to the line
    protocol server, instead of having to manage socket connections and
    data formatting manually.
    """
    def __init__(self, port = 90):
        print "Creating Servers"
        self.serverPort = port
        self.servers = {}

    def sendMessage(self, app, devtoken, payload):
        if app not in self.servers:
            print "Adding app to list: ", app
            self.servers[app] = {'socket': None}

        if not self.servers[app]['socket']:
            import socket
            print "Connecting to app: ", app
            newsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newsocket.connect(("localhost", self.serverPort))
            self.servers[app]['socket'] = newsocket
            # connect

        line = str(app) + "," + devtoken + "," + payload.replace("\n", " ")
        self.servers[app]['socket'].send(line + "\r\n")
        return 0, "Successful"
