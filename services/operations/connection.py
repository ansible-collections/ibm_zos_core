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


from distutils.util import execute
from socket import error
from sqlite3 import connect
from urllib import request
from paramiko import SSHClient, AutoAddPolicy, BadHostKeyException, \
    AuthenticationException, SSHException, ssh_exception
from operations.types import Request
from operations.exceptions import ServicesConnectionException


class Connection:
    """
    Connection class wrapping paramiko for use with our infrastructure.
    This is designed to operate with our tested infrastructure and some limited
    flexibility. The wrapper connection class receives the exected requests
    and delivers the anticipated responses. Additionally it provides methods
    allowing for remote environment variables be set up so that they can interact
    with ZOAU.
    """

    def __init__(self, hostname, username, password = None, key_filename = None,
                    passphrase = None, port=22, environment= None ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.passphrase = passphrase
        self.environment = environment

        self.os = None
        self.env_str = ""
        if self.environment is not None:
            self.env_str = self.set_environment_variable(**self.environment)

    def __to_dict(self):
        """
        Method returns constructor agrs to a dictionary, must remain private to
        protect credentials.
        """
        temp = {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_filename": self.key_filename,
            "passphrase": self.passphrase,
        }

        for k, v in dict(temp).items():
            if v is None:
                del temp[k]
        return temp

    def args_length(self):
        """
        Returns the length of the args pass
        """
        return len(self.__to_dict())

    def connect(self):
        """
        TODO: Doc this
        """
        client = None
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(**self.__to_dict(), disabled_algorithms=
                            {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
        except BadHostKeyException as e:
            #if the server’s host key could not be verified
            print(e)
            raise ServicesConnectionException('Host key could not be verified.') # parentheses?
        except AuthenticationException as e:
            # authentication failed
            print(e)
            raise ServicesConnectionException('Authentication failed.')
        except ssh_exception.SSHException as e:
            print(e)
            raise ServicesConnectionException('SSH Error.')
        except FileNotFoundError as e:
            # Missing key filename
            print(e)
            raise ServicesConnectionException('Missing key filename.')
        except error as e:
            # if a socket error occurred while connecting
            print(e)
            raise ServicesConnectionException('Socket error occurred.')

        return client

    def execute(self, client, request):
        """
        Parameters
        ----------
        client : object, paramiko SSHClient
            SSH Client created through connection.connect()
        request: object, Request class
            Request class instance

        Returns
        -------
        dict
            a dictionary with stdout, stderr and command executed

        Raises
        ------
        TBD

        """

        cmd = request.to_dict().get("command")
        response = None
        get_pty_bool = True
        try:
            # We may need to create a channel and make this synchronous
            # but get_pty should help avoid having to do that
            (stdin, stdout, stderr) = client.exec_command(self.env_str+cmd, get_pty=get_pty_bool)

            if get_pty_bool is True:
                out = stdout.read().decode().strip('\r\n')
                error = stderr.read().decode().strip('\r\n')
            else:
                out = stdout.read().decode().strip('\n')
                error = stderr.read().decode().strip('\n')

            # Don't shutdown stdin, we are reusing this connection in the services instance
            # client.get_transport().open_session().shutdown_write()

            response = {'stdout': out,
                        'stderr': error,
                        'command': cmd
                        }

        except SSHException as e:
            # if there was any other error connecting or establishing an SSH session
            print(e)
        finally:
            client.close()

        return response

    def set_environment_variable(self, **kwargs):
        """
        TODO: Doc this
        """
        env_vars = ""
        export = "export"
        if kwargs is not None:
            for key, value in kwargs.items():
                env_vars = f"{env_vars}{export} {key}=\"{value}\";"

        return env_vars
