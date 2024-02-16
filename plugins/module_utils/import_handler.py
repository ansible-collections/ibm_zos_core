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


class ZOAUImportError(object):
    """This class serves as a wrapper for any kind of error when importing
    ZOAU. Since ZOAU is used by both modules and module_utils, we need a way
    to alert the user when they're trying to use a function that couldn't be
    imported properly. If we only had to deal with this in modules, we could
    just validate that imports worked at the start of their main functions,
    but on utils, we don't have an entry point where we can validate this.
    Just raising an exception when trying the import would be better, but that
    introduces a failure on Ansible sanity tests, so we can't do it.

    Instead, we'll replace what would've been a ZOAU library with this class,
    and the moment ANY method gets called, we finally raise an exception.
    """

    def __init__(self, exception_traceback):
        """When creating a new instance of this class, we save the traceback
        from the original exception so that users have more context when their
        task/code fails. The expected traceback is a string representation of
        it, not an actual traceback object. By importing `traceback` from the
        standard library and calling `traceback.format_exc()` we can
        get this string.
        """
        self.traceback = exception_traceback

    def __getattr__(self, name):
        """This code is virtually the same from `MissingZOAUImport`. What we
        do here is hijack all calls to any method from a missing ZOAU library
        and instead return a method that will alert the user that there was
        an error while importing ZOAU.
        """
        def method(*args, **kwargs):
            raise ImportError(
                (
                    "ZOAU is not properly configured for Ansible. Unable to import zoautil_py. "
                    "Ensure environment variables are properly configured in Ansible for use with ZOAU. "
                    "Complete traceback: {0}".format(self.traceback)
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
