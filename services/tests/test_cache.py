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
import secrets
from services.cache import *
import string



class TestCacheFunctionalTests(unittest.TestCase):

    def create_key(self):
        return secrets.token_urlsafe(10)

    def setUp(self):
        print("\nStarting FVT tests for services class.")
        self.artifact_cache = ArtifactCache()

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestServicesFunctionalTests")


    def tearDown(self):
        print("Completed FVT tets for services class.")

    #Mock request to use for testing
    _mode={"owner": "rwx",
                "group": "r--",
                "other": "---"
    }

    file_attributes = FileAttributes(
                        name="test_file_name.txt",
                        path="/tmp",
                        mode=_mode,
                        size=100,
                        size_type="B",
                        status_group="staff",
                        status_owner="root",
                        record_length=125
                        #attributes = _mode
                    )

    response = Response(name=file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        encoding="IBM-1047",
                        stdout="This is STDOUT",
                        stderr=None,
                        attributes=file_attributes.to_dict()
                        # There are more keys but they are auto populated with
                        # defaults for now, this constructor will change eventually
                        # hostname = "ibm.com"
                        # port = 22
                        # username =  root
                        # password = "ENCRYPTED_PASS"
                        # key_filename = "ENCRYPTED_PATH"
                        # passphrase = "ENCRYPTED_PHRASE"
                        # time_created = "date"
                        # key = "key"
                    )

    def test_cache_create(self):
        """
        Test creating the cache
        """
        assert self.artifact_cache is not None, f"ASSERTION-FAILURE: artifact_cache is None"


    def test_cache_update(self):
        """
        Test adding values to the cache within the allowed cache size
        """
        _size = self.artifact_cache.size;

        for i in range(_size):

            # Calling response here will create a new unique key (response.key)
            response = Response(
                        name=self.file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        encoding="IBM-1047",
                        stdout="This is STDOUT",
                        stderr=None,
                        attributes=self.file_attributes.to_dict()
                    )
            self.artifact_cache.update(response.key,response)

        assert _size == len(self.artifact_cache.cache) , \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, inserted = [{len(self.artifact_cache.cache)}], expected = [{_size}]"


    def test_cache_create_update_over_max_cache_size(self):
        """
        Test inserting more values than the allowed cache size
        """

        _size = self.artifact_cache.size;
        for i in range(_size+20):

            # Calling response here will create a new unique key (response.key)
            response = Response(
                        name=self.file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        encoding="IBM-1047",
                        stdout="This is STDOUT",
                        stderr=None,
                        attributes=self.file_attributes.to_dict()
                    )
            self.artifact_cache.update(response.key,response)
            #print(f"Number of iterations made are = [{i+1}], number of entries successfully cached are = [{len(self.artifact_cache.cache)}]")

        assert i + 1 == _size+20, \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, inserted = [{i}], expected = [{_size+20}]"
        assert _size == len(self.artifact_cache.cache) , \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, inserted = [{len(self.artifact_cache.cache)}], expected = [{_size}]"


    def test_cache_update_invalid_key_type(self):
        """
        Test inserting a key that is not a permitted type, only permitted types
        are str (URL-safe text string, in Base64 encoding)
        """
        try:
            # This file_attributes does not represent the correct implementation
            invalid_type = {
                    "name":"test_file_name.txt",
                    "time_created": datetime.datetime.now(),
                    "key": self.response.create_key()
            }

            self.artifact_cache.update(1234567890,self.response)

        except ValueError as e:
            assert re.match(r'^ValueError', repr(e))


    def test_cache_update_invalid_value_type(self):
        """
        Test inserting a value that is not a permitted type, only permitted types
        are Response
        """

        try:
            # This file_attributes does not represent the correct implementation
            invalid_type = {
                    "name":"test_file_name.txt",
                    "time_created": datetime.datetime.now(),
                    "key": self.response.create_key()
            }

            key = invalid_type.get('key')
            self.artifact_cache.update(key,invalid_type)

        except ValueError as e:
            print(repr(e))
            assert re.match(r'^ValueError', repr(e))