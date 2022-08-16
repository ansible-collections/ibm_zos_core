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

from threading import Lock


class SingletonCacheMeta(type):
    """
    This is a thread safe singleton implementation.

    SingletonCacheMeta is Cache meta class that defines a new type which will
    inherit from type that brings with it all the python classes. Overriding
    the __call__ method which is invoked when we call/instantiate it the class.
    This is only instantiated when the instance attribute is not None, else it
    returns a pre-instantiated instance.

    Example usage of the metaclass
    ------------------------------
    class ArtifactCache(metaclass=SingletonCacheMeta)

    """

    _instance = None
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        This is a callable thread safe singleton implementation such
        that when the class is instantiated it will return only a new copy if
        none exist or the one that has already been instantiated.
        """
        with cls._lock:
            if not cls._instance:
                cls._instance = super(SingletonCacheMeta, cls).__call__(*args, **kwargs)
        return cls._instance
