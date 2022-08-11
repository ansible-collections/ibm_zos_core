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

import datetime
import secrets
from enum import Enum
import sys
sys.path.append('..')


class Type(Enum):
    """
    TODO: finish doc
    """
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
    COMMAND = "COMMAND"
    DATA_SET_KSDS = "DATA_SET_KSDS"
    DATA_SET_ESDS = "DATA_SET_ESDS"
    DATA_SET_RRDS = "DATA_SET_RRDS"
    DATA_SET_LDS = "DATA_SET_LDS"
    DATA_SET_SEQ = "DATA_SET_SEQ"
    DATA_SET_PDS = "DATA_SET_PDS"
    DATA_SET_PDSE = "DATA_SET_PDSE"
    DATA_SET_LIBRARY = "DATA_SET_LIBRARY"
    DATA_SET_BASIC = "DATA_SET_BASIC"
    DATA_SET_LARGE = "DATA_SET_LARGE"
    DATA_SET_MEMBER = "DATA_SET_MEMBER"
    DATA_SET_HFS = "DATA_SET_HFS"

class SizeType(Enum):
    """
    Bytes = B
    Kilobye = KB
    Megabyte = MB
    Gigabyte = GB
    Terabyte = TB
    Cylenders = CYL
    Tracks = TRK
    """

    B = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"
    CYL = "CYL"
    TRK = "TRK"


class Request:

    """
    A request object is the contract used by the services to fulfill an
    operation to the underlying connection class.

    Services will make requests to the connection methods. The
    connection methods will serve many different types of services and to avoid
    a complex type or specific args, the request class represents everything
    the connection class will need to do to fullfil the service request.

    Imagine we have file creation service as well as other types such as
    data set creation. If the service to create a file is called, it will
    review what has been requested, eg; file name, size, location, permissions,
    etc and generate a command and insert that into the request, there could be
    other fields added that would be helpful to the connection in the future.

    NOTE: I am considering to update the request to support multiple commands

    Attributes
    ----------
    command : str
        The command to run on the target.

    Methods
    -------
    to_dict()
        Converts the class attributes to a dictionary

    print_args()
        Prints the class attributes
    """

    def __init__(self, command, environment = None):
        """
        Definition of an file artifact

        Parameters
        ----------
        `command` : str
            Command used by the connection to fulfill the service request
        `environment: dict
            Environment variables (optional)
        """
        self.command = command
        self.environment = environment

    def to_dict(self):
        """
        TODO: Doc this
        """
        return {
            "command": self.command,
        }

    def print_args(self):
        """
        TODO: Doc this
        """
        print(self.to_dict())

class Response:
    """
    Response object is the contract returned by the services operations. It
    describes everything that is needed by the caller about the artifact created.

    The response object is a summary of everything it can provide such that the
    caller will not need to perform any additional queries, for example if a file
    is created, the response will contain every attribute known on the file, such
    as permissions bits and more.

    The response object is also used in the managing the objects lifecycle
    meaning that it cached and later can be retrieved with everything it needs
    to reestablish a connection and perform the resource allocation (destroy
    the artifact). There is no point on persisting connections as it would
    require a connetion pool and for a first iteration this model of recreating
    connection based on the response properties should suffice.

    Attributes
    ----------
    name : str
    type : type
    ...
    """
    def __init__(self, name, type, rc, stdout, stderr, attributes):
        self.name = name
        self.type = type
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr
        self.attributes = attributes
        # TODO:
        # Will need to add support for encryption/keyring
        # Will need to add these addeded keys to the constructor above
        # Will be helpful if we create methods that do the encryption in this class
        self.hostname = "ibm.com"
        self.port = 22
        self.username =  "ENCRYPTED_USER"
        self.password = "ENCRYPTED_PASS"
        self.key_filename = "ENCRYPTED_FILENAME"
        self.passphrase ="ENCRYPTED_PHRASE"
        self.time_created = datetime.datetime.now()
        self.key = self.create_key()


    def to_dict(self):
        """
        TODO: Doc this
        """
        return {
            "name": self.name,
            "type": self.type,
            "rc": self.rc,
            "stdout": self.stdout.splitlines(),
            "stderr": self.stderr.splitlines(),
            "attributes": self.attributes,
            "hostname" : self.hostname,
            "port" : self.port,
            "username" : self.username,
            "password" : self.password,
            "key_filename" : self.key_filename,
            "passphrase" : self.passphrase,
            "time_created" : self.time_created,
            "key" : self.key
        }

    def print_args(self):
        """
        TODO: Doc this
        """
        print(self.to_dict())

    def create_key(self):
        """
        TODO: Doc this
        """
        return secrets.token_urlsafe(10)

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
        encoding = "IBM-1047"
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
        self.encoding = encoding


    def to_dict(self):
        """
        TODO: Doc this
        """
        return {
            "name": self.name,
            "path": self.path,
            "size": self.size,
            "size_type": self.size_type,
            "mode": self.mode,
            "status_group": self.status_group,
            "status_owner": self.status_owner,
            "record_length": self.record_length,
            "encoding": self.encoding,
        }

    def get_status_group(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "SOME_GROUP"

    def get_status_owner(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "SOME_OWNER"

    def get_mode_owner(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "RWX"

    def get_mode_group(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "R-X"

    def get_mode_other(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "---"

    def get_record_length(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return 80

    def get_size(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return 100

    def get_size_type(self, results = None):
        """
        TODO: Doc this
        """
        # Place holder to satisfy pylint
        if results is not None:
            print(results)
        return "GB"

class DirectoryAttributes:
    """
    Definition of an directory artifact
    Parameters
    ==========
    `name` : str
        Name of directory
    `path` : str
        Absolute path to ...
      Provide  lots of doc
    """

class DataSetAttributes:
    """
    Definition of an dataset artifact
    Parameters
    ==========
    `name` : str
        Name ....
      Provide  lots of doc
    """
