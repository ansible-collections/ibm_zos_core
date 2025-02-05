# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The helpers/utils.py file contains various utility functions that,
while not fitting into a specific standalone helper module,
are used across multiple test suites and can be reused from one util.
"""
from datetime import datetime

def get_random_file_name(prefix="", suffix="", dir=""):
    """
    Returns a randomly generated USS file name with options to have a specific suffix and prefix
    in it. By default, returns a 8 numeric character name generated by the current seconds + milliseconds
    from the local system.

    It is not guaranteed that the file name won't exist in the remote node, so this function is intended
    for naming temporary files, where the responsibility for creating and deleting it is left to the function
    caller.

    Parameters
    ----------
    prefix : str
        Prefix for the temporary file name.
    suffix : str
        Suffix for the temporary file name, it can be an extension e.g. '.dzp'.
    dir : str
        Parent temporary folder structure e.g. /tmp/temporary-folder/
    """
    if len(dir) > 0 and not dir.endswith('/'):
        dir += '/'

    return dir + prefix + datetime.now().strftime("%S%f") + suffix
