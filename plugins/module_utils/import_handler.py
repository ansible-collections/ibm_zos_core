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

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class MissingZOAUImport(object):
    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise ImportError(
                (
                    "ZOAU is not properly configured for Ansible. Unable to import zoautil_py. "
                    "Ensure environment variables are properly configured in Ansible for use with ZOAU."
                )
            )

        return method


class MissingImport(object):
    def __init__(self, import_name=""):
        self.import_name = import_name

    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise ImportError("Import {0} was not available.".format(self.import_name))

        return method
