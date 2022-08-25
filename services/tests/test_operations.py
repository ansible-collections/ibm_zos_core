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

import yaml
import os
import unittest
import sys
sys.path.append('..')


class TestOperationsFunctionalTests(unittest.TestCase):
    """
    Test suite is used to drive operation functional tests. These tests directly
    test the operations which are all protected but this is often a good place
    to start to test your operations before invoking them from the services class.

    Note that there seems to be a limitation of the type of key used if you are
    connecting with a key_filename, they must be of type PEM.

    Private keys in RFC4716 format are not supported by paramiko, while PEM
    formatted keys are. MacOS, ssh-keygen defaults to RFC4716 format which ends
    up having an error that looks like:
      `paramiko ValueError: q must be exactly 160, 224, or 256 bits long`

    To avoid this, at least on our infra, generate PEM formated keys (your
    current RSA keys won't be lost), you will be promoted for a key file name,
    use `id_dsa`
        $ ssh-keygen -t rsa -m PEM
        $ Enter file in which to save the key (/Users/ddimatos/.ssh/id_rsa):
            /Users/<username>/.ssh/id_dsa

    PyTest Usage:
        cd {project}/ibm_zos_core/services/tests
        pytest test_operations.py -s # For verbosity like print(..) statements
        pytest test_operations.py    # No verbosity
    """

    def setUp(self):
        print("\nStarting FVT operations tests.", 'r')
        with open("tests/connection_config.yaml") as stream:
            cfg = yaml.safe_load(stream)
        self.hostname = cfg["hostname"]
        self.port = cfg["port"]
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.key_filename = os.path.expanduser('~') + "/.ssh/id_dsa",
        self.passphrase = cfg["passphrase"]

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestServicesFunctionalTests")

    def tearDown(self):
        print("Completed FVT tets for services class.")

    def test_operations_create_file(self):
        """
        Test the operation with a basic file creation, note that this test
        is going directly at protected operations which are normally accessed
        from services parent class. Our preferred path is through services as
        it provies an easier experience for users.
        """
        # Create a connection to be passed to an operation
        connection = Connection(hostname=self.hostname, username=self.username,
                                key_filename=self.key_filename)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        # Invoke an operation to create a file
        result = _create(connection, "test.txt", "/tmp/")
        assert result is not None, "ASSERTION-FAILURE: file is None"

        # TODO: This is a hard coded result, this needs to be rewritten to
        #       ensure the file was created
        _encoding = result.to_dict().get('attributes').get('encoding')
        assert _encoding == "IBM-1047", f"ASSERTION-FAILURE: Encoding {_encoding} \
                                does not match expected IBM-1047"
