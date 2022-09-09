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

from operations.types import Request, Response, Type


def _command(connection, command):
    """
    Run commands on the target
    """

    # Prepare the Request to pass to the connection class
    request = Request(command)

    # Use the connection
    client = connection.connect()

    result = connection.execute(client, request)

    response = Response(name="raw", type=Type.COMMAND.name, rc=0,
                        stdout=result.get('stdout'), stderr=result.get('stderr'),
                        attributes=None)

    return response
