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


class ServicesConnectionException(Exception):
    """
    This is a example, I really don't know till we have more code if we really
    need our own exceptions, if we can normalize on the errors then it would
    be helpful
    """
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"Connection to host , {self.message} failed"
        else:
            return 'Connection to host failed'


class ServicesException(Exception):
    pass


class ServicesArtifactException(Exception):
    pass