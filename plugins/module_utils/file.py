# Copyright (c) IBM Corporation 2020, 2024
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

import os
from stat import S_IREAD, S_IWRITE, ST_MODE


def _get_dir_mode(path):
    """Get the mode of an existing directory.
    Defaults to 0600 if directory not found.

    Parameters
    ----------
    path : str
        The absolute path to retrieve directory mode from.

    Returns
    -------
    int
        The mode of the directory.
    """
    mask = S_IREAD | S_IWRITE
    if os.path.isdir(path):
        mask = os.stat(path)[ST_MODE]
    elif os.path.isdir(os.path.dirname(path)):
        mask = os.stat(os.path.dirname(path))[ST_MODE]
    return mask


def make_dirs(path, mode_from=None):
    """Create missing directories for path.
    If path does not end in "/", assumes end of path is
    a file.

    Parameters
    ----------
    path : str
        The path to ensure subdirectories are created for.

    Keyword Parameters
    ------------------
    mode_from : str
        Path to existing dir to retrieve the mode from.
        Mode will be used for new directories. (default: {None})
    """
    mode = _get_dir_mode(mode_from) if mode_from is not None else S_IREAD | S_IWRITE
    if path[-1] == "/":
        os.makedirs(path, mode=mode, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(path), mode=mode, exist_ok=True)
    return
