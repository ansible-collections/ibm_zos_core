# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2024
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

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

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
    results = hosts.all.shell(cmd="echo $USER")
    for result in results.contacted.values():
        user = result.get("stdout")
    command_string = [
        (
            "send 'Hello, this is a test message from zos_tso_command module. "
            "Im sending a command exceed 80 chars. Thank you.' user({0})".format(user)
        )
    ]
    results = hosts.all.zos_tso_command(commands=command_string)
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True


def test_zos_tso_command_allocate_listing_delete(ansible_zos_module):
    hosts = ansible_zos_module
    default_temp_dataset = get_tmp_ds_name()
    command_string = [
        f"alloc da('{default_temp_dataset}') "+
        "catalog lrecl(133) blksize(13300) recfm(f b) dsorg(po) cylinders space(5,5) dir(5)"
    ]
    results_allocate = hosts.all.zos_tso_command(commands=command_string)
    # Validate the correct allocation of dataset
    for result in results_allocate.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate listds of datasets and validate LISTDS using alias param 'command' of auth command
    results = hosts.all.zos_tso_command(commands=[f"LISTDS '{default_temp_dataset}'"])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate LISTDS using alias param 'command'
    results = hosts.all.zos_tso_command(command=f"LISTDS '{default_temp_dataset}'")
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate LISTCAT command and an unauth command
    results = hosts.all.zos_tso_command(
        commands=[f"LISTCAT ENT('{default_temp_dataset}')"]
    )
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Validate remove dataset
    results = hosts.all.zos_tso_command(commands=[f"delete '{default_temp_dataset}'"])
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") == 0
        assert result.get("changed") is True
    # Expect the tso_command to fail here because
    # the previous command will have already deleted the data set
    # Validate data set was removed by previous call
    results = hosts.all.zos_tso_command(commands=[f"delete '{default_temp_dataset}'"])
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
    results = hosts.all.shell(cmd="echo $USER")
    for result in results.contacted.values():
        user = result.get("stdout")
    commands_list = ["LU {0}".format(user), "LISTGRP"]
    results = hosts.all.zos_tso_command(commands=commands_list)
    for result in results.contacted.values():
        for item in result.get("output"):
            if item.get("command") == "LU {0}".format(user):
                assert item.get("rc") == 0
            if item.get("command") == "LISTGRP":
                assert item.get("rc") == 0
        assert result.get("changed") is True


# The positive test
# The command that kicks off rc>0 which is allowed
def test_zos_tso_command_maxrc(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(
        commands=["LISTDSD DATASET('HLQ.DATA.SET') ALL GENERIC"],
        max_rc=4
    )
    for result in results.contacted.values():
        for item in result.get("output"):
            assert item.get("rc") < 5
        assert result.get("changed") is True


def test_zos_tso_command_gds(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name(3, 3, symbols=True)
        hosts.all.shell(cmd="dtouch -tGDG -L2 '{0}'".format(default_data_set))
        hosts.all.shell(cmd="dtouch -tseq '{0}(+1)' ".format(default_data_set))
        hosts.all.shell(cmd="dtouch -tseq '{0}(+1)' ".format(default_data_set))
        print(f"data set name {default_data_set}")
        hosts = ansible_zos_module
        results = hosts.all.zos_tso_command(
            commands=["""LISTDSD DATASET('{0}(0)') ALL GENERIC""".format(default_data_set)],
            max_rc=4
        )
        for result in results.contacted.values():
            for item in result.get("output"):
                assert result.get("changed") is True
        results = hosts.all.zos_tso_command(
            commands=["""LISTDSD DATASET('{0}(-1)') ALL GENERIC""".format(default_data_set)],
            max_rc=4
        )
        for result in results.contacted.values():
            for item in result.get("output"):
                assert result.get("changed") is True
        results = hosts.all.zos_tso_command(
            commands=["""LISTDS '{0}(-1)'""".format(default_data_set)]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        None
        # hosts.all.shell(cmd="drm ANSIBLE.*".format(default_data_set))