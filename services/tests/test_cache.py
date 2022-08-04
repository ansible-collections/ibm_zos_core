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


    def test_cache_create(self):
        """
        Test creating the cache
        """

        for i in range(100):
            key = self.create_key()
            if key not in self.artifact_cache:
                value = str(i) + ":"+ self.create_key()
                self.artifact_cache.update(key,value)
            else:
                print("DUPLICATE")
            print("#%s iterations, #%s cached entries" % (i+1, self.artifact_cache.size))
        
        assert True
