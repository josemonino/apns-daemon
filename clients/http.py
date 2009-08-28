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

from twisted.web import server, resource

class APNSResource(resource.Resource):
    isLeaf = True
    def __init__(self, daemon, **kwds):
        resource.Resource.__init__(self)
        self.apns_daemon = daemon

    def render_GET(self, request):
        parts = request.path.split("/")
        print "Rendering GET Request: ", parts
        return "Please use POST requests"

    def render_POST(self, request):
        parts = request.path.split("/")
        payload = {}
        print "request headers: ", request.args
        print "request path: ", parts
        print "request content: ", request.content.read()
        print "Rendering POST Request: ", parts, dir(request)
        return "OK"

class APNSSite(server.Site):
    def __init__(self, daemon, **kwds):
        self.root_resource  = APNSResource(daemon, **kwds)
        self.apns_daemon    = daemon

        server.Site.__init__(self, self.root_resource)
        daemon.reactor.listenTCP(kwds['port'], self)

