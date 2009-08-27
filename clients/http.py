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

from twisted.web import http

class APNSRequestChannel(http.HTTPChannel):
    """
    def __init__(self, daemon, **kwds):
        self.daemon = daemon
        self.reactor.listenTCP(kwds["port"], self)
    """
    def requestDone(self, request):
        print "Request: ", request
        super(APNSRequestChannel

from twisted.internet.protocol import ClientFactory
class APNSRequestChannelFactory(ClientFactory):
    protocol = APNSRequestChannel

from twisted.internet import reactor
reactor.listenTCP(90, APNSRequestChannelFactory())
reactor.run()
