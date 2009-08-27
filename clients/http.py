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

from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.internet.ssl import ClientContextFactory
from twisted.web import http as oldhttp
from twisted.web2 import http, server, resource, channel

class APNSPage(resource.Resource):
    addSlash = True

    def __init__(self, daemon):
        self.daemon = daemon

    def render(self, ctx):
        print "Rendering: ", ctx, type(ctx), ctx.path
        return http.Response(stream = "<html><body>Hello World</body></html>")

class APNSRequest(oldhttp.Request):
    def process(self):
        print "Processing request", self.path, self.uri
        path = self.path
        if path[0] == '/': path = path[1:]
        parts           = path.split("/")
        app_name        = parts[0]
        device_token    = parts[1]
        payload         = self.post_data

        if app_name not in self.connections:
            print "Cannot find app: ", app_name
            return False
        
        connection  = self.connections[orig_app]
        factory     = connection['client_factory']
        if connection['num_connections'] == 0:
            context_factory = connection['client_context_factory']
            reactor.connectSSL(connection['apns_host'],
                               connection['apns_port'],
                               factory, context_factory)

        protocol = factory.getProtocol()
        protocol.sendMessage(target_device, payload)


class APNSChannel(oldhttp.HTTPChannel):
    requestFactory = APNSRequest

    """
    def requestDone(self, request, version):
        print "Request Done: ", type(request)
        pass
    """

class APNSHttpFactory(oldhttp.HTTPFactory):
    protocol = APNSChannel

    def __init__(self, connections):
        # Global list of connections to the APNS network
        self.connections = connections
