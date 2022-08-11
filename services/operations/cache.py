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


import time
import secrets
from threading import Thread
from operations.types import Response



class ArtifactCache:
    """
    A class used to manage the lifecycle of artifacts created by the services.
    It is the responsibility of this framework to ensure that objects are
    destroyed if they are not done so by the caller.

    This is a cache is not thread safe, it is meant to be instantiated once
    in a init calls and accessed during the course of its time in use.

    Parameters
    ----------
    cache_size : int, optional
        The size the cache should be initialized. (default 10000)

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

    def __init__(self, cache_size = 100):
        """
        Parameters
        ----------
        cache_size : int, optional
            The size the cache should be initialized. (default 10000)
        """

        self.cache = {}
        # Seems rather large default but lets be generous to start with
        self.cache_size = cache_size

        self.thread = Thread(name='non-daemon', target=self.monitor_cache, daemon=True)
        self.thread_stop = False
        self.thread_running = False

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

        if key not in self.cache and len(self.cache) >= self.cache_size:
            self.__destroy_oldest_entry()

        self.cache[key] = value

        if not self.thread_running:
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

    def get(self,key):
        """
        Parameters
        ----------
        key : str
            Key used to insert the entry into the cache.

        Get the entries value corresponding to the key from the cache and remove
        it from the cache.
        """
        value = self.cache.get(key)
        self.cache.pop(key).to_dict()
        return value

    def get_object(self,key):
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

    # Incomplete monitor, should be tied into update and stop when cache size is 0
    def monitor_cache(self):
        """
        TODO: Doc this
        """
        self.thread_running = True
        while len(self.cache) >0 and not self.thread_stop:
            print("Thread running in background")
            # TODO Implement eviction strategy based on time accessed
            # because maybe some have not finished. Basically just call
            # __destroy_oldest_entry
            time.sleep(5)

        self.thread_running = False
        # self.thread.join()

    def monitor_stop(self):
        """
        TODO: Doc this
        """
        self.thread_stop = True
