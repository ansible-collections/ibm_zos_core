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

    print("\n(1.2) Initialize the services with dictionary.")
    services = Services(**connection_args)

    print("\n(1.3) Run a command on the targeted host.")
    result = services.Command.command("ls -la")

    print("\n(1.4) Result dictionary returned.")
    pprint(result.to_dict())


    # --------------------------------------------------------------------------
    # Example (2)
    # --------------------------------------------------------------------------
    print("(2) EXAMPLE")
    print("\n(2.1) Initialize the services with host arguments.")
    services = Services(hostname="EC33017A.vmec.svl.ibm.com",username="omvsadm",
                key_filename=os.path.expanduser('~') + "/.ssh/id_dsa")

    print("\n(2.2) Run a command on the targeted host.")
    result = services.Command.command("echo \"command 1\";ls -la;echo \"command \
                2\";ls /;echo \"command 3\";date")

    print("\n(2.3) Result dictionary returned.")
    pprint(result.to_dict())

    # --------------------------------------------------------------------------
    # Example (3)
    # --------------------------------------------------------------------------
    print("(3) EXAMPLE")

    environment = {
            "_BPXK_AUTOCVT":"ON",
            "ZOAU_HOME":"/zoau/v1.2.0f",
            "PATH":"/zoau/v1.2.0f/bin:/python/usr/lpp/IBM/cyp/v3r8/pyz/bin:/bin:.",
            "LIBPATH":"/zoau/v1.2.0f/lib:/lib:/usr/lib:.",
            "PYTHONPATH":"/zoau/v1.2.0f/lib",
            "_CEE_RUNOPTS":"FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)",
            "_TAG_REDIR_ERR":"txt",
            "_TAG_REDIR_IN":"txt",
            "_TAG_REDIR_OUT":"txt",
            "LANG":"C"
    }

    print("\n(3.1) Initialize the services with dictionary and environment variables.")
    connection_args.update({"environment": environment})
    services = Services(**connection_args)

    print("\n(3.2) Run a command on the targeted host.")
    result = services.Command.command("zoaversion")

    print("\n(4.4) Result dictionary returned.")
    pprint(result.to_dict())

    # --------------------------------------------------------------------------
    # Example (4)
    # --------------------------------------------------------------------------
    print("(3) EXAMPLE")

    environment = {
            "_BPXK_AUTOCVT":"ON",
            "ZOAU_HOME":"/zoau/v1.2.0f",
            "PATH":"/zoau/v1.2.0f/bin:/python/usr/lpp/IBM/cyp/v3r8/pyz/bin:/bin:.",
            "LIBPATH":"/zoau/v1.2.0f/lib:/lib:/usr/lib:.",
            "PYTHONPATH":"/zoau/v1.2.0f/lib",
            "_CEE_RUNOPTS":"FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)",
            "_TAG_REDIR_ERR":"txt",
            "_TAG_REDIR_IN":"txt",
            "_TAG_REDIR_OUT":"txt",
            "LANG":"C"
    }

    print("\n(3.1) Initialize the services with dictionary and environment variables.")
    connection_args.update({"environment": environment})
    services = Services(**connection_args)

    print("\n(3.2) Run a command on the targeted host.")
    result = services.Command.command("jls")

    print("\n(3.4) Result dictionary returned.")
    pprint(result.to_dict())
    