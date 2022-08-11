# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ------------------------------------------------------------------------------
# Demonstrates how to use the various services from a script
#
# Usage:
#     python3 command_service_.py
# ------------------------------------------------------------------------------

import os
import sys
sys.path.append('..')

from pprint import pprint
from services import Services

if __name__ == '__main__':
    # --------------------------------------------------------------------------
    # Example (1)
    # --------------------------------------------------------------------------

    print("(1) EXAMPLE")
    print("(1.1) Create a dictionary representing the targeted host.")

    connection_args = {
        "hostname": "EC33017A.vmec.svl.ibm.com",
        "username": "omvsadm",
        "password": "changeme",
        "key_filename": os.path.expanduser('~') + "/.ssh/id_dsa",
        "passphrase": "changeme",
        "port": 22,
        "environment": {}
    }
    pprint(connection_args)

    print("\n(1.2) Initialize the services with dictionary.")
    services = Services(**connection_args)

    print("\n(1.3) Run a command on the targeted host.")
    # TODO: Complete this

    print("\n(1.3) Result dictionary returned.")
    # TODO: Complete this

    # --------------------------------------------------------------------------
    # Example (2)
    # --------------------------------------------------------------------------
    print("(2) EXAMPLE")
    print("\n(2.1) Initialize the services with host arguments.")
    services = Services(hostname="EC33017A.vmec.svl.ibm.com",username="omvsadm",
                key_filename=os.path.expanduser('~') + "/.ssh/id_dsa")

    print("\n(2.3) Run a command on the targeted host")
    # TODO: Complete this

    print("\n(2.3) Result returned.")
    # TODO: Complete this
