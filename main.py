#!/bin/env python2.5
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
import constants, errors, daemon

def read_config_file(daemon, config_file):
    """
    Reads the config file and loads config data about all the apps we want
    to support.
    """
    import os
    if not os.path.isfile(config_file):
        raise errors.ConfigFileError(config_file, "File not found")

    configs = eval(open(config_file).read())
    if 'clients' not in configs:
        raise errors.ConfigFileError(config_file, "'clients' section not found")

    if 'apps' not in configs:
        raise errors.ConfigFileError(config_file, "'apps' section not found")

    clients = configs['clients']
    for client_name in clients:
        client = clients[client_name]
        client_class = client['class']
        print "Loading client: ", client_class
        
def parse_options(daemon):
    from optparse import OptionParser

    parser = OptionParser(version = "%prog 0.1")
    parser.add_option("-c", "--config", dest = "configfile",
                      help="Config file to read application info from.", metavar = "CONFIG-FILE")

    (options, args) = parser.parse_args()

    if not options.configfile:
        parser.error("Please specify a valid config filename with the -c option")
        
    read_config_file(daemon, options.configfile)

    # register all apps here
    """
    daemon.registerApp("metjungle", "8K9U92BL7X.com.metjungle.pickmeup",
                       os.path.abspath("certs/CertificateFile.pem"),
                       os.path.abspath("certs/PrivateKeyFile.pem"),
                       constants.DEFAULT_APNS_DEV_HOST,
                       constants.DEFAULT_APNS_DEV_PORT,
                       constants.DEFAULT_FEEDBACK_DEV_HOST,
                       constants.DEFAULT_FEEDBACK_DEV_PORT)
    """

def main():
    dmon = daemon.APNSDaemon()
    parse_options(dmon)
    dmon.run()

if __name__ == "__main__":
    main()

