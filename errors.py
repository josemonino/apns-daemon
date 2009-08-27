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

import constants

class AppRegistrationError(Exception):
    """
    Class of application registration error.
    """
    def __init__(self, app_name, app_mesg = "Generic Application Error"):
        self.app_name   = app_name
        self.app_mesg   = app_mesg

    def __str__(self):
        return "%s: %s" % (self.app_mesg, self.app_name)

class ConfigFileError(Exception):
    """
    Error thrown when the config file is not found.
    """
    def __init__(self, config_file, message):
        self.config_file    = config_file
        self.message        = message;
    
    def __str__(self):
        return "Config file error: %s - %s" % (self.config_file, self.message)

    
class PayloadLengthError(Exception):
    """
    Error thrown when payload being sent is greater than the what is
    allowed by APNS.
    """
    def __init__(self, max_payload_length = constants.MAX_PAYLOAD_LENGTH):
        self.max_payload_length = max_payload_length
    
    def __str__(self):
        return "Payload cannot exceed %d bytes" % self.max_payload_length

