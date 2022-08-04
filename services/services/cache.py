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

# The idea behind this cache is that since a callback into the target to destroy
# the artifact created for the caller might be a bit unnecessary or even difficult
# to maintain and author, so a simple cache that can keep track of artifacts that
# need to be destroyed.

# The most straight forward way is that when the service creates an artifact
# that it also place an object/class containing the process of destoring it.
# for example a cache of randome keys assigned by each creation artifact so
# the value can later be found and run, where value might be:
# {command = rm -rf /some/file, name: foo, id: same as key, client: ssh }
# thus the above would mean we keep a client open the entire time or we pass the
# clients credentials around which could also be tricky if we are managing passwords

# Some optional thirdparty and native solutions for a cache are:
# - expiringdict: https://pypi.org/project/expiringdict/
# - cachetools: https://cachetools.readthedocs.io/en/latest/
# - homegrown as below


import datetime
import secrets

class ArtifactCache:

    def __init__(self, cache_size = 10000):
        self.cache = {}
        # Seems rather large default but lets be generous to start with
        self.cache_size = cache_size

    def __contains__(self, key):
        """
        Return True if the key is in the cache otherwise False
        """
        return key in self.cache

    def create_key(self):
        return secrets.token_urlsafe(10)

    def update(self, key, value):
        """
        Update the cache entry with a new key and value, if the cache is full;
        the oldest cached entry will be removed silently and the artifacts
        destruction will occur assuming the artifact is no longer in use.
        """
        if key not in self.cache and len(self.cache) >= self.cache_size:
            self._destroy_oldest_entry()

        self.cache[key] = {'date_accessed': datetime.datetime.now(),
                           'value': value}

    def _destroy_oldest_entry(self):
        """
        Remove the oldest entry based on the date_accessed, before removing
        ensure the artifact destruction is executed then silently return.
        """

        oldest_entry = None
        for key in self.cache:
            if oldest_entry == None:
                oldest_entry = key
            elif self.cache[key]['date_accessed'] < self.cache[oldest_entry][
                'date_accessed']:
                oldest_entry = key
        self.cache.pop(oldest_entry)

    def peek(self, key):
        """
        Return the item value corresponding to the key from the cache but don't
        remove it from the cache.
        """
        return self.cache.get(key)

    def get(self,key):
        """
        Get the item value corresponding to the key from the cache and remove
        it from the cache.
        """
        value = self.cache.get(key)
        self.cache.pop(key)
        return value

    @property
    def size(self):
        """
        Return the size of the cache
        """
        return self.cache_size