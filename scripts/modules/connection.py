#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Connection class wrapping paramiko. The wrapper provides methods allowing
for remote environment variables be set up so that they can interact with
ZOAU. Generally this is a wrapper to paramiko to be used to write files to
z/OS. For example, consider writing a file that is managed by this load
balancer that can know if there is another test running. The idea was to
update our pytest fixture to look for that file so that a remote pipeline or
other instance does not try to run concurrently until the functional tests
can be properly vetted out for concurrent support.
Usage:
    key_file_name = os.path.expanduser('~') + "/.ssh/id_dsa"
    connection = Connection(hostname="ibm.com", username="root", key_filename=key_file_name)
    client = connection.connect()
    result = connection.execute(client, "ls")
    print(result)
"""

# pylint: disable=too-many-instance-attributes, too-many-arguments

from socket import error
from paramiko import SSHClient, AutoAddPolicy, BadHostKeyException, \
    AuthenticationException, SSHException, ssh_exception

class Connection:
    """
    Connection class wrapping paramiko. The wrapper provides methods allowing
    for remote environment variables be set up so that they can interact with
    ZOAU. Generally this is a wrapper to paramiko to be used to write files to
    z/OS. For example, consider writing a file that is managed by this load
    balancer that can know if there is another test running. The idea was to
    update our pytest fixture to look for that file so that a remote pipeline or
    other instance does not try to run concurrently until the functional tests
    can be properly vetted out for concurrent support.

    Usage:
        key_file_name = os.path.expanduser('~') + "/.ssh/id_dsa"
        connection = Connection(hostname="ibm.com", username="root", key_filename=key_file_name)
        client = connection.connect()
        result = connection.execute(client, "ls")
        print(result)
    """

    def __init__(self, hostname, username, password = None, key_filename = None,
                    passphrase = None, port=22, environment= None ):
        self._hostname = hostname
        self.port = port
        self._username = username
        self.password = password
        self.key_filename = key_filename
        self.passphrase = passphrase
        self.environment = environment
        self.env_str = ""
        if self.environment is not None:
            self.env_str = self.set_environment_variable(**self.environment)


    def __to_dict(self) -> str:
        """
        Method returns constructor arguments to a dictionary, must remain private to
        protect credentials.
        """
        temp =  {
            "hostname": self._hostname,
            "port": self.port,
            "username": self._username,
            "password": self.password,
            "key_filename": self.key_filename,
            "passphrase": self.passphrase,
        }

        for k,v  in dict(temp).items():
            if v is None:
                del temp[k]
        return temp

    def connect(self) -> SSHClient:
        """
        Create the connection after the connection class has been initialized.

        Return
        SSHClient: paramiko SSHClient, client used the execution of commands.

        Raises:
            BadHostKeyException
            AuthenticationException
            SSHException
            FileNotFoundError
            error
        """
        ssh = None

        n = 0
        while n <= 10:
            try:
                ssh = SSHClient()
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                ssh.connect(**self.__to_dict(), disabled_algorithms=
                                {'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
            except BadHostKeyException as e:
                print('Host key could not be verified.', str(e))
                raise e
            except AuthenticationException as e:
                print('Authentication failed.', str(e))
                raise e
            except ssh_exception.SSHException as e:
                print(e, str(e))
                raise e
            except FileNotFoundError as e:
                print('Missing key filename.', str(e))
                raise e
            except error as e:
                print('Socket error occurred while connecting.', str(e))
                raise e
        return ssh

    def execute(self, client, command):
        """
        Parameters:
            client (paramiko SSHClient) SSH Client created through connection.connect()
            command (str): command to run

        Returns:
        dict: a dictionary with stdout, stderr and command executed

        Raises
            SSHException
        """

        response = None
        get_pty_bool = True
        out = ""
        try:
            # We may need to create a channel and make this synchronous
            # but get_pty should help avoid having to do that
            (_, stdout, stderr) = client.exec_command(self.env_str+command, get_pty=get_pty_bool)

            if get_pty_bool is True:
                out = stdout.read().decode().strip('\r\n')
                error_msg = stderr.read().decode().strip('\r\n')
            else:
                out = stdout.read().decode().strip('\n')
                error_msg = stderr.read().decode().strip('\n')

            # Don't shutdown stdin, we are reusing this connection in the services instance
            # client.get_transport().open_session().shutdown_write()

            response = {'stdout': out,
                        'stderr': error_msg,
                        'command': command
            }

        except SSHException as e:
            # if there was any other error connecting or establishing an SSH session
            print(e)
        finally:
            client.close()

        return response

    def set_environment_variable(self, **kwargs):
        """
        Provide the connection with environment variables needed to be exported
        such as ZOAU env vars.

        Example:
            env={"_BPXK_AUTOCVT":"ON",
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
        connection = Connection(hostname="ibm.com", username="root",
                        key_filename=key_filename, environment=env)

        """
        env_vars = ""
        export="export"
        if kwargs is not None:
            for key, value in kwargs.items():
                env_vars = f"{env_vars}{export} {key}=\"{value}\";"
        return env_vars
