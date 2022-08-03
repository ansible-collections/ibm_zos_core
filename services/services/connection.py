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

from socket import MsgFlag
import paramiko
from pkg_resources import to_filename
import copy
from types import *


class Connection:
    """
    Connection class wrapping paramiko for use with our infrastructure.
    This is designed to operate with our tested infrastructure and some limited
    flexibility. The wrapper connection class receives the exected requests
    and delivers the anticipated responses. Additionally it provides methods
    allowing for remote environment variables be set up so that they can interact
    with ZOAU. 
    """

    def __init__(self, hostname, username, password = None, key_filename = None, passphrase = None, port=22 ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.passphrase = passphrase

    def to_dic(self):
        return {
            "hostname": self.hostname,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "key_filename": self.key_filename,
            "passphrase": self.passphrase
        }
    
    def print_args(self):
        print(self.to_dict())

    def connect(self):
        try:
            client = paramiko.SSHClient();
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(**self.to_dic(), disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']})
            return client;
        except Exception as e:
            print(e)

    def execute(self, client, request):
        #cmd = request.get('command')
        cmd = request.to_dic().get("command")
        try:
            env={'LANG': 'en_GB',
                'LC_COLLATE': 'C'
            }
            
            # We may need to create a channel and make this synchronous
            # but get_pty should help avoid having to do that
            (stdin, stdout, stderr) = client.exec_command(cmd, get_pty=True, environment = env)
            out = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            # Command sent, can shutdown stdin
            # client.get_transport().open_session().shutdown_write()
            response = {'stdout': out,
                        'stderr': error,
                        'command': cmd
            }
            return response
        except Exception as e:
            print(e)
        finally:
            client.close()
