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
from operations.cache import ArtifactCache
from operations.types import Response, FileAttributes, Type

import re
import unittest
import secrets
import datetime
import sys
sys.path.append('..')


class TestCacheFunctionalTests(unittest.TestCase):
    """
    Test suite is used to drive cache unit tests. These tests simply exercise
    the cache ensuring there are no lost entries, ivalid types and
    accountability for all entries remain.

    PyTest Usage:
        cd {project}/ibm_zos_core/services/tests
        pytest test_cache.py -s # For verbosity like print(..) statements
        pytest test_cache.py    # No verbosity
    """

    def create_key(self):
        """
        TOOD: Doc this
        """
        return secrets.token_urlsafe(10)

    def setUp(self):
        print("\nStarting FVT tests for services class.")
        self.artifact_cache = ArtifactCache()

        # Reduce the cache size down to 100 over the default 10000
        self.artifact_cache.cache_max_size = 100

    @classmethod
    def tearDownClass(cls):
        print("\nCompleted test suite TestServicesFunctionalTests")

    def tearDown(self):
        print("Completed FVT tests for services class.")

    # --------------------------------------------------------------------------
    # Mock request to use for testing
    # --------------------------------------------------------------------------

    _mode = {"owner": "rwx",
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
                        # attributes = _mode
                    )

    response = Response(name=file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        stdout="This is STDOUT",
                        stderr='',
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
        assert self.artifact_cache is not None, "ASSERTION-FAILURE: artifact_cache is None"

    def test_cache_update(self):
        """
        Test adding values to the cache within the allowed cache size
        """
        _size = self.artifact_cache.cache_max_size

        for i in range(_size):
            print(f"Number of iterations made are = [{i+1}], number of entries \
                    successfully cached are = [{len(self.artifact_cache.cache)}]")

            # Calling response here will create a new unique key (response.key)
            response = Response(
                        name=self.file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        stdout="This is STDOUT",
                        stderr='',
                        attributes=self.file_attributes.to_dict()
                    )
            self.artifact_cache.update(response.key, response)

        assert _size == len(self.artifact_cache.cache), \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, \
                inserted = [{len(self.artifact_cache.cache)}], expected = [{_size}]"

    def test_cache_create_update_over_max_cache_size(self):
        """
        Test inserting more values than the allowed cache size
        """

        _size = self.artifact_cache.cache_max_size
        for i in range(_size+20):
            print(f"Number of iterations made are = [{i+1}], number of entries \
                        successfully cached are = [{len(self.artifact_cache.cache)}]")

            # Calling response here will create a new unique key (response.key)
            response = Response(
                        name=self.file_attributes.name,
                        type=Type.FILE.name,
                        rc=0,
                        stdout="This is STDOUT",
                        stderr='',
                        attributes=self.file_attributes.to_dict()
                    )
            self.artifact_cache.update(response.key, response)

        assert i + 1 == _size+20, \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, \
                    inserted = [{i}], expected = [{_size+20}]"
        assert _size == len(self.artifact_cache.cache), \
            f"ASSERTION-FAILURE: cache did not insert the expected entries, \
                inserted = [{len(self.artifact_cache.cache)}], expected = [{_size}]"

    def test_cache_update_invalid_key_type(self):
        """
        Test inserting a key that is not a permitted type, only permitted types
        are str (URL-safe text string, in Base64 encoding)
        """
        try:
            self.artifact_cache.update(1234567890, self.response)

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
                    "name": "test_file_name.txt",
                    "time_created": datetime.datetime.now(),
                    "key": self.response.create_key()
            }

            key = invalid_type.get('key')
            self.artifact_cache.update(key, invalid_type)

        except ValueError as e:
            print(repr(e))
            assert re.match(r'^ValueError', repr(e))

    def test_cache_is_singleton(self):
        """
        Test if the cache is a singleton by comparing instances, changing
        cache sizes and comparing and looking at the object reference id's
        """

        cache_size = 101
        cache_temp_1 = ArtifactCache()
        cache_temp_2 = ArtifactCache()
        cache_temp_1.cache_max_size = cache_size

        assert cache_temp_1 is cache_temp_2, "ASSERTION-FAILURE: \
            Singleton comparison failure, instances do not match."

        assert cache_temp_1.get_max_cache_size == cache_temp_2.get_max_cache_size,\
            f"ASSERTION-FAILURE: Singleton comparison failure, \
                expected max_cache size of {cache_size}."

        assert hex(id(cache_temp_1)) == hex(id(cache_temp_2)), \
            f"ASSERTION-FAILURE:  Singleton comparison failure, instance \
                id's do not match, {hex(id(cache_temp_1))} not equal to\
                    {hex(id(cache_temp_2))}"
