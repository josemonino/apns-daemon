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

{
    'clients': {
        'line': {
            'class': 'clients.line.LineProtocolFactory',
            'port': 90
        },
        'http': {
            'class': 'clients.http.HttpProtocolFactory',
            'port': 99
        },
    },

    'apps': {
        'app1': {
            'bundle_id':        "App1 BundleID",
            'certificate_file': "path_to_certificate_file_1.pem",
            'privatekey_file':  "path_to_privatekey_file_1.pem"
        },
        'app2': {
            'bundle_id':        "App2 BundleID",
            'certificate_file': "path_to_certificate_file_2.pem",
            'privatekey_file':  "path_to_privatekey_file_2.pem"
        },
    }
}

