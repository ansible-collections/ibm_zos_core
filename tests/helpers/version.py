# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2022, 2025
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

import re

__metaclass__ = type


def get_zoau_version(ansible_zos_module):
    """
    Fetches the current ZOAU version from the z/OS system using the `zoaversion` command.

    This function runs the `zoaversion` command on the z/OS system and parses the output 
    to extract the version number in the format `vX.Y.Z.W`, where X, Y, Z, and W are numerical digits.

    Parameters
    ----------
    ansible_zos_module : ansible.module_utils.basic.AnsibleModule
        The Ansible z/OS module that provides the `all.shell()` method to run shell commands.

    Returns
    -------
    str
        The ZOAU version number (e.g., "1.2.3.4") extracted from the command output.
        Returns `"1.2.0"` if no valid version is found.
    """
    cmd_str = "zoaversion"
    version_results = ansible_zos_module.all.shell(cmd=cmd_str)
    zoa_version = "0.0.0"  # Default version if not found

    # Iterate through all contacted hosts and check the result output
    for result in version_results.contacted.values():
        output = result.get("stdout")
        if output:
            # Search for the version in the format "vX.Y.Z.W"
            match = re.search(r'v?(\d+\.\d+\.\d+(?:\.\d+)?)', output)
            if match:
                zoa_version = match.group(1)

    return zoa_version

def is_zoau_version_higher_than(ansible_zos_module,min_version_str):
    """Reports back if ZOAU version is high enough.

    Parameters
    ---------- 
    min_version_str : str
        The minimal desired ZOAU version '#.#.#'.

    Returns
    -------
    bool
        Whether ZOAU version found was high enough.
    """
    if is_valid_version_string(min_version_str):
        # check zoau version on system (already a list)
        system_version_list = get_zoau_version_str(ansible_zos_module)

        # convert input to list format
        min_version_list = min_version_str.split('.')

        # convert list of strs to list of ints
        system_version_list = [int(i) for i in system_version_list]
        min_version_list = [int(i) for i in min_version_list]

        # compare major
        if system_version_list[0] > min_version_list[0]:
            return True
        if system_version_list[0] < min_version_list[0]:
            return False

        # majors are equal, compare minor
        if system_version_list[1] > min_version_list[1]:
            return True
        if system_version_list[1] < min_version_list[1]:
            return False

        # majors and minors are equal, compare patch
        if system_version_list[2] > min_version_list[2]:
            return True
        if system_version_list[2] < min_version_list[2]:
            return False

        # check for a 4th level if system and min_version provided it
        if len(system_version_list) < 4:
            system_version_list.append(0)
        if len(min_version_list) < 4:
            min_version_list.append(0)

        #  return result of comparison of 4th levels.
        return system_version_list[3] >= min_version_list[3]

    # invalid version string
    return False


def is_valid_version_string(version_str):
    """Reports back if string is in proper version format. Expected format is a
        series of numbers (major) followed by a dot(.) followed by another
        series of numbers (minor) followed by another dot(.) followed by a
        series of numbers (patch) i.e. "#.#.#" where '#' can be any integer.
        There is a provision for a 4th level to this eg "v1.2.0.1".

    Parameters
    ----------
    min_version_str : str
        String to be verified is in correct format.

    Returns
    -------
    bool
        Whether provided str is in correct format.
    """

    # split string into [major, minor, patch]
    version_list = version_str.split('.')

    # check each element in list isnumeric()
    for ver in version_list:
        if not ver.isnumeric():
            return False

    return True

def get_zoau_version_str(ansible_zos_module):
    """Attempts to call zoaversion on target and parses out version string.

    Returns
    -------
    Union[int, int, int]
        ZOAU version found in format [#,#,#]. There is a
        provision for a 4th level eg "v1.2.0.1".
    """
    ZOAU_API_VERSION = get_zoau_version(ansible_zos_module)
    version_list = (
        ZOAU_API_VERSION.split('.')
    )

    return version_list
