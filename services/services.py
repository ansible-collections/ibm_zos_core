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

from operations.connection import Connection
from operations.file import _create
from operations.command import _command

class Services:
    """
    Services offered here are in the context of a high level API that encapsulates
    operataions such as creating an artifact. Artifacts are an object that has
    been requested to be created, for example selecting the appropriate operation
    that can create a file on a remote target.

    The services API intends to simplify the creating of artifacts and also
    managing the artifacts lifecycle.

    Attributes
    ----------
    cache_size : int, optional
        The size the cache should be initialized. (default 10000)

    Methods
    -------
        `hostname` : str
            The node to establish and SSH connection to. Can be either a
            hostname or IP addres.
        `username`: dict
            User associated with the password, username is used as
            a SSH credential.
        `password`: str, optional
            Password associated with the username, password is used as
            a SSH credential. If no password is supplied, a key_filename
            must be supplied.
        `key_filename`: str, optional
            Path to the PEM key
        `passphrase`: str, optional
            Passphrase used to unlock th PEM key if a key was used to manage
            keys.
        `port`: int, optional
            Port to connect to over SSH, default 22
        `environment`: dic, optional
            A dictionary of environment vars needing to be exported on the host
            so commands may successfully run.
    """

    def __init__(self, hostname, username, password = None, key_filename = None,
                    passphrase = None, port=22, environment= None ):
        """
        Constructor for services

        Parameters
        ----------
        `hostname` : str
            The node to establish and SSH connection to. Can be either a
            hostname or IP addres.
        `username`: dict
            User associated with the password, username is used as
            a SSH credential.
        `password`: str, optional
            Password associated with the username, password is used as
            a SSH credential. If no password is supplied, a key_filename
            must be supplied.
        `key_filename`: str, optional
            Path to the PEM key
        `passphrase`: str, optional
            Passphrase used to unlock th PEM key if a key was used to manage
            keys.
        `port`: int, optional
            Port to connect to over SSH, default 22
        `environment`: dic, optional
            A dictionary of environment vars needing to be exported on the host
            so commands may successfully run.

        """

        self.hostname = hostname
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.passphrase = passphrase
        self.port = port
        self.environment = environment
        self.File = self.File(self)
        self.Command = self.Command(self)

    class File:
        """
        File class.....
        """
        def __init__(self, Services):
            self.__connection = Connection(hostname=Services.hostname,
                                    username=Services.username,
                                    password=Services.password,
                                    key_filename=Services.key_filename,
                                    passphrase = Services.passphrase,
                                    port = Services.port,
                                    environment=Services.environment
                                )

        def create(self, name, path):
            """
            Create a file
            """
            return _create(self.__connection, name, path)

    class Command:
        """
        File class.....
        """
        def __init__(self, Services):
            self.__connection = Connection(hostname=Services.hostname,
                                    username=Services.username,
                                    password=Services.password,
                                    key_filename=Services.key_filename,
                                    passphrase = Services.passphrase,
                                    port = Services.port,
                                    environment=Services.environment
                                )

        def command(self, command):
            """
            Run a command
            """
            return _command(self.__connection, command)
# ------------------------------------------------------------------------------
# I'll leave this for now if it helps, but I prefer you test using unit tests
# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#      connection_args = {
#         "hostname": "EC33017A.vmec.svl.ibm.com",
#         "username": "omvsadm",
#         "password": "changeme",
#         "key_filename": os.path.expanduser('~') + "/.ssh/id_dsa",
#         "passphrase": "changeme",
#         "port": 22,
#         "environment": {}
#     }
# services = Services(**connection_args)
# services.File.create("test.txt", "/tmp/")
