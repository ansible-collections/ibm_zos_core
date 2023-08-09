# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2023
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

import ansible.constants
import ansible.errors
import ansible.utils

DEFAULT_TEMP_DATASET="imstestl.ims1.temp.ps"

def test_zos_tso_command_run_help(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(commands=["help"])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True


# The happy path test
# Run a long tso command to allocate a dataset.
def test_zos_tso_command_long_command_128_chars(ansible_zos_module):
    hosts = ansible_zos_module
    command_string = [
        (
            "send 'Hello, this is a test message from zos_tso_command module. "
            "Im sending a command exceed 80 chars. Thank you.' user(omvsadm)"
        )
    ]
    results = hosts.all.zos_tso_command(commands=command_string)
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True


def test_zos_tso_command_allocate_listing_delete(ansible_zos_module):
    hosts = ansible_zos_module
    command_string = [
        "alloc da('{0}') catalog lrecl(133) blksize(13300) recfm(f b) dsorg(po) cylinders space(5,5) dir(5)".format(DEFAULT_TEMP_DATASET)
    ]
    results_allocate = hosts.all.zos_tso_command(commands=command_string)
    # Validate the correct allocation of dataset
    for result in results_allocate.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate listds of datasets and validate LISTDS using alias param 'command' of auth command
    results = hosts.all.zos_tso_command(commands=["LISTDS '{0}'".format(DEFAULT_TEMP_DATASET)])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate LISTDS using alias param 'command'
    results = hosts.all.zos_tso_command(command="LISTDS '{0}'".format(DEFAULT_TEMP_DATASET))
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate LISTCAT command and an unauth command
    results = hosts.all.zos_tso_command(
        commands=["LISTCAT ENT('{0}')".format(DEFAULT_TEMP_DATASET)]
    )
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate remove dataset
    results = hosts.all.zos_tso_command(commands=["delete '{0}'".format(DEFAULT_TEMP_DATASET)])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Expect the tso_command to fail here because the previous command will have already deleted the data set
    # Validate data set was removed by previous call
    results = hosts.all.zos_tso_command(commands=["delete '{0}'".format(DEFAULT_TEMP_DATASET)])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 8
        assert result.get("changed") is False


# The failure test
# The input command is empty.
def test_zos_tso_command_empty_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(commands=[""])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 255
        assert result.get("changed") is False


# The failure test
# The input command is no-existing command, the module return rc 255.
def test_zos_tso_command_invalid_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(commands=["xxxxxx"])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 255
        assert result.get("changed") is False


# The positive test
# The multiple commands
def test_zos_tso_command_multiple_commands(ansible_zos_module):
    hosts = ansible_zos_module
    commands_list = ["LU omvsadm", "LISTGRP"]
    results = hosts.all.zos_tso_command(commands=commands_list)
    for result in results.contacted.values():
        for item in result.get("output"):
            if item.get("command") == "LU omvsadm":
                assert item.get("rc") == 0
            if item.get("command") == "LISTGRP":
                assert item.get("rc") == 0
        assert result.get("changed") is True


# The positive test
# The command that kicks off rc>0 which is allowed
def test_zos_tso_command_maxrc(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(commands=["LISTDSD DATASET('HLQ.DATA.SET') ALL GENERIC"],max_rc=4)
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") < 5
        assert result.get("changed") is True


# The positive test
# The command that kicks off rc>0 which is allowed
def test_zos_tso_command_maxrc(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(commands=["LISTDSD DATASET('HLQ.DATA.SET') ALL GENERIC"],max_rc=4)
    for result in results.contacted.values():
        for item in result.get("output"):
            print( item )
            assert item.get("rc") < 5
        assert result.get("changed") is True
