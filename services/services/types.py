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

from enum import Enum

class Type(Enum):
    FILE = "file"
    DIRECTORY = "directory"
    DATA_SET = "DATA_SET"


class Request:
    """
    Class represents a request from a service, for example the function
    service.create_file() will populate a request object to be executed
    by the connection class. The service.create_file(...) will take attributes
    such as name, size, path, etc, eventually create a request which really
    maps to a command for connection.execute(request) to run. For now we are
    keeping it simple to a command, but it might be usefull to merge in the
    attributes so they can be passed along to a response, given the generic
    nature of this request object its a bit too soon to figure our if a
    dictionary should also be passed long. 
    """
    def __init__(self, command):
        """
        Definition of an file artifact

        Parameters
        ----------
        `command` : str 
            Command used by the connection to fulfill the service request
        """
        self.command = command

    def to_dic(self):
        return {
            "command": self.command,
        }

    def print_args(self):
        print(self.to_dict())

class Response:

    def __init__(self, name, type, rc, encoding, stdout, stderr, attributes):
        self.name = name
        self.type =type
        self.rc = rc
        self.encoding = encoding
        self.stdout = stdout
        self.stderr = stderr
        self.attributes = attributes

    def to_dic(self):
        return {
            "name": self.name,
            "type": self.type,
            "rc": self.rc,
            "encoding": self.encoding,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "attributes": self.attributes
        }

    def print_args(self):
        print(self.to_dict())

    # def from_dict(artifact_dictionary): #artifact_dictionary is a result of a atrifact such as File converted to a dictionary
    #     return Response(
    #         rc=response['rc'],
    #         stdout=response['stdout_response'],
    #         stderr=response['stderr_response'],
    #         etc...
    #     )

class FileAttributes:
    """
    Definition of an file artifact
    Parameters
    ==========
    `name` : str 
        Name of file 
    `path` : str
        Absolute path to file.....
      Provide  lots of doc 
    """

    def __init__(
        self,
        name,
        path,
        size,
        size_type,
        mode = {"owner": None, "group": None, "other": None},
        status_group=None,
        status_owner=None,
        record_length=None,
        attributes=None
     ):
        """
        FileAttributes
        """
        self.name = name
        self.path = path
        self.size = size
        self.size_type = size_type
        self.mode = mode
        self.status_group = status_group
        self.status_owner = status_owner
        self.record_length = record_length
        self.attributes = attributes

    def to_dict(self):
        return {
            "name": self.name,
            "path": self.path,
            "status_group": self.status_group,
            "size": self.size,
            "size_type": self.size_type,
            "mode": self.mode,
            "status_group": self.status_group,
            "status_owner": self.status_owner,
            "record_length": self.record_length,
            "attributes": self.attributes,
        }

    def get_status_group():
        return "FOO"

    def get_status_owner():
        return "BAR"
   
    def get_mode_owner():
        return "RWX"

    def get_mode_group():
        return "R-X"

    def get_mode_other():
        return "---"

    def get_record_length():
        return 111

    def get_size():
        return 100

    def get_size_type():
        return "GB"
