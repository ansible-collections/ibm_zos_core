from operations import command
from operations.connection import Connection

import os
import re
import unittest
import sys
import yaml
sys.path.append('..')


class TestCommandFunctionalTests(unittest.TestCase):
    """
    Test suite is used to drive command functional tests.

    PyTest Usage:
        cd {project}/ibm_zos_core/services/tests
        pytest test_command.py -s # For verbosity like print(..) statements
        pytest test_command.py    # No verbosity
    """

    def setUp(self):
        print("\nStarting FVT command tests.")
        with open("tests/connection_config.yaml") as stream:
            cfg = yaml.safe_load(stream)
        self.hostname = cfg["hostname"]
        self.port = cfg["port"]
        self.username = cfg["username"]
        self.password = cfg["password"]
        self.key_filename = os.path.expanduser('~') + "/.ssh/id_dsa",
        self.passphrase = cfg["passphrase"]
        self.environment = cfg["environment"]

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestServicesFunctionalTests")

    def tearDown(self):
        print("Completed FVT tets for services class.")

    def test_command_run_command_on_host(self):
        'Test connecting to host and running commands on host'
        # Create a connection to be passed to an operation
        connection = Connection(hostname=self.hostname, username=self.username,
                                key_filename=self.key_filename)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        # Run 'ls' on target host
        result = command._command(connection, "ls")
        assert result.to_dict()['stdout'],\
            "ASSERTION-FAILURE: ls command failed"

        # Run "echo" command on target host
        result = command._command(connection, "echo 'Hello World'")
        assert result.to_dict()['stdout'] == ['Hello World'],\
            "ASSERTION-FAILURE: echo command failed"

        # Run invalid command on target host
        result = command._command(connection, "invalid")
        stdout = result.to_dict()['stdout'][0]
        assert "not found" in stdout,\
            "ASSERTION-FAILURE: invalid command passed"

    def test_command_run_command_on_host_set_enviroment(self):
        'Test connecting to host with enviroment vars and run commands on host'

        # Create a connection to be passed to an operation
        connection = Connection(hostname=self.hostname, username=self.username,
                                key_filename=self.key_filename,
                                environment=self.environment)
        assert connection is not None, "ASSERTION-FAILURE: Connection is None"

        # Run "zoaversion" on target host
        result = command._command(connection, "zoaversion")
        assert result.to_dict()['stdout'],\
            "ASSERTION-FAILURE: zoaversion command failed"

        # Run "jls" on target host
        result = command._command(connection, "jls")
        assert result.to_dict()['stdout'],\
            "ASSERTION-FAILURE: jls command failed"

        # Run invalid command on target host
        result = command._command(connection, "invalid")
        stdout = result.to_dict()['stdout'][0]
        assert "not found" in stdout,\
            "ASSERTION-FAILURE: invalid command passed"
