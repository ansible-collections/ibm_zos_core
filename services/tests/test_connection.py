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



import os
import re
import unittest
import sys
import yaml
from socket import error
from paramiko import AuthenticationException, ssh_exception 
sys.path.append('..')

from operations.connection import Connection, ServicesConnectionException
from operations.types import Request


class TestConnectionUnitTests(unittest.TestCase):
    """
    Test suite is used to drive connection functional tests. Note that there
    seems to be a limitation of the type of key used if you are connecting with
    a key_filename, they must be of type PEM.

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
        pytest test_connection.py -s # For verbosity like print(..) statements
        pytest test_connection.py    # No verbosity
    """

    # Environment vars used to configure ZOAU
    environment = {
            "_BPXK_AUTOCVT":"ON",
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
        print("\nCompleted test suite TestConnectionUnitTests")


    def tearDown(self):
        print("Completed unit test for connection class.")


    def test_connection_args_6(self):
        """
        Test that the args are correctly passing in this test suite from the
        initialized kwargs. Should result in what ever self.kwargs defined with.
        """
        connection = Connection(hostname=self.hostname, username=self.username,
                        password=self.password, key_filename=self.key_filename,
                        passphrase=self.passphrase, port=66)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        arg_len = connection.args_length()
        assert arg_len == 6, \
            f"ASSERTION-FAILURE: Connection args expected 6 not equal to = [{arg_len}]"


    def test_connection_args_4(self):
        """
        Test that the args count
        """
        connection = Connection(hostname=self.hostname, username=self.username,
                        key_filename=self.key_filename, port=66)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        arg_len = connection.args_length()
        assert arg_len == 4, \
            f"ASSERTION-FAILURE: Connection args expected 4 not equal to = [{arg_len}]"

    def test_connection_invalid_hostname_type(self): 
        """
        Test the connection with an invalid hostname type, negative test case.
        """
        invalid_hostname = 1 
        try:
            connection = Connection(hostname=invalid_hostname, username=self.username, 
                            password=self.password)
            connection.connect()
        except TypeError as e:
            assert re.match(r'^TypeError', repr(e))
      

    def test_connection_invalid_hostname(self):
        """
        Test the connection with an invalid hostname, negative test case.
        """
        invalid_hostname = "invalid hostname"
        try:
            connection = Connection(hostname=invalid_hostname, username=self.username, 
                            password=self.password)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))
 

    def test_connection_invalid_port_range(self):
        """
        Test the connection with an invalid port range, negative test case.
        """
        invalid_port = -1 
        try:
            connection = Connection(hostname=self.hostname, username=self.username, 
                            password=self.password, port=invalid_port)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))
 

    def test_connection_invalid_port(self):
        """
        Test the connection with an invalid port, negative test case.
        """
        invalid_port = 0 
        try:
            connection = Connection(hostname=self.hostname, username=self.username, 
                            password=self.password, port=invalid_port)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))
            

    def test_connection_invalid_user_type(self):
        """
        Test the connection with an invalid user type, negative test case.
        """
        invalid_username = 1 
        try:
            connection = Connection(hostname=self.hostname, username=invalid_username,
                            password=self.password)
            connection.connect()
        except TypeError as e:
            assert re.match(r'^TypeError', repr(e))


    def test_connection_invalid_user(self):
        """
        Test the connection with an invalid user, negative test case.
        """
        invalid_username = "invalid username"
        try:
            connection = Connection(hostname=self.hostname, username=invalid_username, 
                            password=self.password)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))


    def test_connection_invalid_password_type(self):
        invalid_password = 1 
        try:
            connection = Connection(hostname=self.hostname, username=self.username,
                            password=invalid_password)
            connection.connect()
        except TypeError as e:
            assert re.match(r'^TypeError', repr(e))


    def test_connection_invalid_password(self):
        """
        Test the connection with an invalid password, negative test case.
        """
        invalid_password = "invalid password"
        try:
            connection = Connection(hostname=self.hostname, username=self.username,
                            password=invalid_password)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))


    def test_connection_invalid_key_filename_type(self):
        """
        Test the connection with an invalid key_filename type, negative test case.
        """
        invalid_key_filename = 1 
        try:
            connection = Connection(hostname=self.hostname, username=self.username,
                            key_filename=invalid_key_filename)
            connection.connect()
        except TypeError as e:
            assert re.match(r'^TypeError', repr(e))
           

    def test_connection_invalid_key_filename(self):
        """
        Test the connection with an invalid key_filename, negative test case.
        """
        invalid_key_filename = "invalid key filename"
        try:
            connection = Connection(hostname=self.hostname, username=self.username, 
                            key_filename=invalid_key_filename)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))
           

    @unittest.skip('TODO - TRY AGAIN') 
    def test_connection_invalid_passphrase(self):
        """
        Test the connection with an invalid passphrase, negative test case.
        """
        invalid_passphrase = "invalid passphrase"
        try:
            connection = Connection(hostname=self.hostname, username=self.username,
                            key_filename=self.key_filename,passphrase=invalid_passphrase)
            connection.connect()
        except ServicesConnectionException as e:
            assert re.match(r'^ServicesConnectionException', repr(e))
            

class TestConnectionFunctionalTests(unittest.TestCase):
    """
    Functional tests for connection
    """
    # Default args used for a connection, ensure password not shared in Git
    kwargs = {
        "hostname": "EC01140A.vmec.svl.ibm.com",
        "port": 22,
        "username": "omvsadm",
        "password": "changeme",
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
        request = Request("hostname")
        connection = Connection(hostname=self.hostname, username=self.username,
                        password=self.password)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        client = connection.connect()
        assert client is not None, "ASSERTION-FAILURE: client is None"

        result = connection.execute(client, request)
        assert result is not None, "ASSERTION-FAILURE: Executing a command returned None"


    @unittest.skip('TODO - TRY AGAIN') 
    def test_connection_host_user_key_filename(self):
        """
        Test the connection with a valid host, user and key_filename
        """
        # Mock request object, this will need to be updated when the request
        # objects are done
        #request = {"command": "hostname"}
        request = Request("hostname")
        connection = Connection(hostname=self.hostname, username=self.username,
                        key_filename=self.key_filename)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        client = connection.connect()
        assert client is not None, "ASSERTION-FAILURE: client is None"

        result = connection.execute(client, request)
        assert result is not None, "ASSERTION-FAILURE: Executing a command returned None"
        _hostname = result.get('stdout')
        assert _hostname == self.hostname, f"ASSERTION-FAILURE: Hostname {_hostname} \
                                does not match expected {self.hostname}"

    @unittest.skip('TODO - TRY AGAIN') 
    def test_connection_environment_vars(self):
        """
        Test the connection with a valid set of environment vars
        """
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
        request = Request("zoaversion")
        connection = Connection(hostname=self.hostname, username=self.username,
                                    key_filename=self.key_filename, environment=env)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        client = connection.connect()
        assert client is not None, "ASSERTION-FAILURE: client is None"

        connection.set_environment_variable(**env)
        result = connection.execute(client, request)
        assert re.match(r'.*CUT.*', result.get('stdout'))



    @unittest.skip('TODO - TRY AGAIN')
    def test_connection_host_user_key_filename_passphrase(self):
        """
        Test the connection with a valid passphrase
        """
        connection = Connection(hostname=self.hostname, username=self.username,
                            key_filename=self.key_filename,passphrase=self.passphrase)
        client = connection.connect()
        assert client is not None, "ASSERTION-FAILURE: client is None"
        
