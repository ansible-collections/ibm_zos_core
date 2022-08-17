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

# Notes:
# Some optional thirdparty and native solutions for a cache are:
# - expiringdict: https://pypi.org/project/expiringdict/
# - cachetools: https://cachetools.readthedocs.io/en/latest/

import time
import secrets
from threading import Thread
from operations.types import Response
from operations.SingletonCacheMeta import SingletonCacheMeta


class ArtifactCache(metaclass=SingletonCacheMeta):
    """
    A thread safe class used to manage the lifecycle of artifacts created by
    the services. It is the responsibility of this framework to ensure that
    objects are destroyed if they are not done so by the caller.

    Instantiation will initialize the cache with a limit of 10,000 objects,
    anything more than that will be automatically pruned starting with the
    oldest cache entry.

    Methods
    -------
    create_key() //Note: this will likely be moved to a response type
        Generate a random key of length 10
    update(key, value)
        ...
    peek(self, key)
        ...
    get(self,key)
        ...
    size(self)
        ...
    """

    def __init__(self):
        """
        Initialize the cache
        """
        # Dict to manage cache objects
        self.cache = {}
        self.cache_max_size = 10000

        self.thread = Thread(name='daemon', target=self.monitor_cache, daemon=True)

    def __contains__(self, key):
        """
        Return True if the key is in the cache otherwise False
        """
        return key in self.cache

    def create_key(self):
        """
        TODO: document this
        """
        return secrets.token_urlsafe(10)

    def update(self, key, value):
        """
        Update the cache entry with a new key and value, if the cache is full;
        the oldest cached entry will be removed silently and the artifacts
        destruction will occur assuming the artifact is no longer in use.
        """
        # Because __setitem__ does not function as expected, isinstance() is used
        if not isinstance(key, str):
            raise ValueError(f"Incorrect `key` type used in update(key, value), \
                    type =[{type(key)}], must be type str")
        if not isinstance(value, Response):
            raise ValueError(f"Incorrect `value` type used in update(key, value), \
                    type =[{type(value)}], must be type services.types.Response")

        if key not in self.cache and len(self.cache) >= self.cache_max_size:
            self.__destroy_oldest_entry()

        self.cache[key] = value

        if self.thread.ident is None:
            self.thread.start()

    def __destroy_oldest_entry(self):
        """
        Remove the oldest entry based on the time_created, before removing
        ensure the artifact destruction is executed then silently return.
        """

        oldest = None
        for key in self.cache:
            if oldest is None:
                oldest = key
            elif self.peek(key).get('time_created') < self.peek(oldest).get('time_created'):
                oldest = key
        self.cache.pop(oldest)

    def peek(self, key):
        """
        Return the item value corresponding to the key from the cache but don't
        remove it from the cache.
        """
        return self.cache.get(key).to_dict()

    def get(self, key):
        """
        Parameters
        ----------
        key : str
            Key used to insert the entry into the cache.

        Get the entries value corresponding to the key from the cache and
        remove it from the cache.
        """
        value = self.cache.get(key)
        self.cache.pop(key).to_dict()
        return value

    def get_object(self, key):
        """
        Get the item value corresponding to the key from the cache and remove
        it from the cache.
        """
        value = self.cache.get(key)
        self.cache.pop(key)
        return value

    @property
    def get_max_cache_size(self):
        """
        Return the max size of the cache
        """
        return self.cache_max_size

    # Incomplete monitor, should be tied into update and stop when cache size is 0
    def monitor_cache(self):
        """
        TODO: Doc this
        """

        while len(self.cache) > 0 and self.thread.ident is not None:
            print("Thread running in background")
            # TODO Implement eviction strategy based on time accessed
            # because maybe some have not finished. Basically just call
            # __destroy_oldest_entry
            time.sleep(5)

        # self.thread.join()
