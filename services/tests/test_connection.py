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
import unittest
import os

from services.connection import *


class TestConnectionUnitTests(unittest.TestCase):
    """
    Test suite is used to test both unit and functional tests. Note that
    there seems to be a limitation of the type of key used if you are connecting
    with a key_filename, they must be of type PEM.

    Private keys in RFC4716 format are not supported by paramiko, while PEM
    formatted keys are. MacOS, ssh-keygen defaults to RFC4716 format which ends
    up having an error that looks like:
      `paramiko ValueError: q must be exactly 160, 224, or 256 bits long`

    To avoid this, at least on our infra, generate PEM formated keys (your
    current RSA keys won't be lost):
        $ ssh-keygen -t rsa -m PEM  # You will be promoted for a key file name
                                    # use id_dsa
        $ Enter file in which to save the key (/Users/ddimatos/.ssh/id_rsa):
            /Users/<username>/.ssh/id_dsa

    PyTest Usage:
        cd {project}/ibm_zos_core/services/tests
        pytest test_connection.py -s # For verbosity like print(..) statements
        pytest test_connection.py    # No verbosity
    """

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
        print("\nStarting UNIT tests for connection class.")
        self.hostname = self.kwargs.get('hostname')
        self.port = self.kwargs.get('port')
        self.username = self.kwargs.get('username') or 'username'
        self.password = self.kwargs.get('password') or 'changeme'
        self.key_filename = self.kwargs.get('key_filename')
        self.passphrase = self.kwargs.get('passphrase') or 'changeme'

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestConnectionUnitTests")


    def tearDown(self):
        print("Completed unit tets for connection class.")


    def test_connection_args(self):
        """
        Test that the args are correctly passing in this test suite from the
        initialized kwargs. Should result in what ever self.kwargs defined with.
        """
        connection = Connection(self.hostname, self.port, self.username,
                        self.password, self.key_filename, self.passphrase)
        assert connection is not None, f"ASSERTION-FAILURE: Connection is None"

        arg_len = len(connection.to_dic())
        assert arg_len == 6, \
            f"ASSERTION-FAILURE: Connection args expected 6 not equal to = [{arg_len}]"


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_hostname(self):
        """
        Test the connection with an invalid hostname, negative test case.
        """
        assert True


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_port(self):
        """
        Test the connection with an invalid port, negative test case.
        """
        assert True


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_user(self):
        """
        Test the connection with an invalid user, negative test case.
        """
        assert True


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_password(self):
        """
        Test the connection with an invalid password, negative test case.
        """
        assert True


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_key_filename(self):
        """
        Test the connection with an invalid key_filename, negative test case.
        """
        assert True


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_invalid_passphrase(self):
        """
        Test the connection with an invalid passphrase, negative test case.
        """
        assert True


class TestConnectionFunctionalTests(unittest.TestCase):

    # Default args used for a connection, ensure password not shared in Git
    kwargs = {
        "hostname": "EC33018A.vmec.svl.ibm.com",
        "port": 22,
        "username": "omvsadm",
        "password": "xxxxxx",
        "key_filename": os.path.expanduser('~') + "/.ssh/id_dsa",
        "passphrase": "changeme"
    }

    def setUp(self):
        print("\nStarting FVT tests for connection class.")
        self.hostname = self.kwargs.get('hostname')
        self.port = self.kwargs.get('port')
        self.username = self.kwargs.get('username') or 'username'
        self.password = self.kwargs.get('password') or 'changeme'
        self.key_filename = self.kwargs.get('key_filename')
        self.passphrase = self.kwargs.get('passphrase') or 'changeme'

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestConnectionFunctionalTests")


    def tearDown(self):
        print("Completed FVT tets for connection class.")

    def test_connection_host_user_pass(self):
        """
        Test the connection with a valid host, user and password
        """
        request = {"command": "hostname"}
        connection = Connection(hostname=self.hostname, username=self.username, password=self.password)
        assert connection is not None, f"ASSERTION-FAILURE: Connection is None"

        client = connection.connect()
        assert client is not None, f"ASSERTION-FAILURE: client is None"

        result = connection.execute(client, request)
        assert result is not None, f"ASSERTION-FAILURE: Executing a command returned None"


    def test_connection_host_user_key_filename(self):
        """
        Test the connection with a valid host, user and key_filename
        """
        # Mock request object, this will need to be updated when the request
        # objects are done
        request = {"command": "hostname"}

        connection = Connection(hostname=self.hostname, username=self.username, key_filename=self.key_filename)
        assert connection is not None, f"ASSERTION-FAILURE: Connection is None"

        client = connection.connect()
        assert client is not None, f"ASSERTION-FAILURE: client is None"

        result = connection.execute(client, request)
        assert result is not None, f"ASSERTION-FAILURE: Executing a command returned None"
        _hostname = result.get('stdout')
        assert _hostname == self.hostname, f"ASSERTION-FAILURE: Hostname {_hostname} does not match expected {self.hostname}"


    @unittest.skip('TODO - IMPLEMENT')
    def test_connection_host_user_key_filename_passphrase(self):
        assert True