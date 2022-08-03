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

from pprint import pprint
from pipes import quote
import re
import unittest
import os
from services.file import *
from services.connection import *


class TestServicesFunctionalTests(unittest.TestCase):

    # Default args used for a connection, ensure password not shared in Git
    kwargs = {
        "hostname": "EC33018A.vmec.svl.ibm.com",
        "port": 22,
        "username": "omvsadm",
        "password": "xxxxxxx",
        "key_filename": os.path.expanduser('~') + "/.ssh/id_dsa",
        "passphrase": "changeme"
    }

    def setUp(self):
        print("\nStarting FVT tests for services class.")
        self.hostname = self.kwargs.get('hostname')
        self.port = self.kwargs.get('port')
        self.username = self.kwargs.get('username') or 'username'
        self.password = self.kwargs.get('password') or 'changeme'
        self.key_filename = self.kwargs.get('key_filename')
        self.passphrase = self.kwargs.get('passphrase') or 'changeme'

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestServicesFunctionalTests")


    def tearDown(self):
        print("Completed FVT tets for services class.")


    def test_connection_host_user_key_filename(self):
        """
        Test the connection with a valid host, user and key_filename
        """
        # Mock request object, this will need to be updated when the request
        # objects are done
        request = {"command": "hostname"}

        connection = Connection(hostname=self.hostname, username=self.username, key_filename=self.key_filename)
        assert connection is not None, f"ASSERTION-FAILURE: Connection is None"

        result = create("test", "/tmp/", connection)
        assert result is not None, f"ASSERTION-FAILURE: file is None"
        print(result.to_dic())
        _encoding = result.to_dic().get('encoding')
        assert _encoding == "IBM-1047", f"ASSERTION-FAILURE: Encoding {_encoding} does not match expected IBM-1047"

