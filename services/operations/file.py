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

from operations.types import  FileAttributes, Request, Response, Type

def _create(connection, name, path):
    """
    Create a file in USS
    """

    command = "touch " + path + name

    # Prepare the Request to pass to the connection class
    request = Request(command)

    # Use the connection that was passed to the create and connect it to the
    # target. Note that it is expected that a connection will have been fully
    # configured even with necessary environment vars
    client = connection.connect()

    # Use the connections excute to run the command we want to fulfill the
    # create operation.
    result = connection.execute(client, request)

    _mode={"owner": FileAttributes.get_mode_owner(result),
                "group": FileAttributes.get_mode_group(result),
                "other": FileAttributes.get_mode_other(result)
    }

    file_attributes = FileAttributes(name=name, path=path, mode=_mode,
                        size=FileAttributes.get_size(result),
                        size_type=FileAttributes.get_size_type(result),
                        status_group=FileAttributes.get_status_group(result),
                        status_owner=FileAttributes.get_status_owner(result),
                        record_length=FileAttributes.get_record_length(result))

    # _mode={"owner": FileAttributes.get_mode_owner(),
    #             "group": FileAttributes.get_mode_group(),
    #             "other": FileAttributes.get_mode_other()
    # }

    # file_attributes = FileAttributes(name=name, path=path, mode=_mode,
    #                     size=FileAttributes.get_size(),
    #                     size_type=FileAttributes.get_size_type(),
    #                     status_group=FileAttributes.get_status_group(),
    #                     status_owner=FileAttributes.get_status_owner(),
    #                     record_length=FileAttributes.get_record_length())

    response = Response(name=name, type=Type.FILE.name, rc=0,
                    stdout=result.get('stdout'), stderr=result.get('stderr'),
                    attributes=file_attributes.to_dict())

    return response
