# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2023
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

import pytest

from ibm_zos_core.plugins.module_utils import (
    zoau_version_checker,
)


__metaclass__ = type


def test_zos_operator_various_command(ansible_zos_module):
    test_data = [
        ("d a", 0, True),
        ("k s", 0, True),
        ("d r,l", 0, True),
        ("d parmlib", 0, True),
        ("SEND 'list ready',NOW", 0, True),
    ]
    for item in test_data:
        command = item[0]
        expected_rc = item[1]
        changed = item[2]
        hosts = ansible_zos_module
        results = hosts.all.zos_operator(cmd=command)
        for result in results.contacted.values():
            assert result["rc"] == expected_rc
            assert result.get("changed") is changed


def test_zos_operator_invalid_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="invalid,command", verbose=False)
    for result in results.contacted.values():
        assert result.get("changed") is True


def test_zos_operator_invalid_command_to_ensure_transparency(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="DUMP COMM=('ERROR DUMP')", verbose=False)
    for result in results.contacted.values():
        assert result.get("changed") is True
    transparency = False
    if any('DUMP COMMAND' in str for str in result.get("content")):
        transparency = True
    assert transparency


def test_zos_operator_positive_path(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="d u,all", verbose=False)
    for result in results.contacted.values():
        assert result["rc"] == 0
        assert result.get("changed") is True
        assert result.get("content") is not None


def test_zos_operator_positive_path_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="d u,all", verbose=True)
    for result in results.contacted.values():
        assert result["rc"] == 0
        assert result.get("changed") is True
        assert result.get("content") is not None
        # Traverse the content list for a known verbose keyword and track state
        if any('BGYSC0804I' in str for str in result.get("content")):
            is_verbose = True
        assert is_verbose


def test_zos_operator_positive_verbose_with_full_delay(ansible_zos_module):
    "Long running command should take over 30 seconds"
    hosts = ansible_zos_module
    wait_time = 10
    results = hosts.all.zos_operator(
        cmd="RO *ALL,LOG 'dummy syslog message'", verbose=True, wait_time_s=wait_time
    )

    for result in results.contacted.values():
        assert result["rc"] == 0
        assert result.get("changed") is True
        assert result.get("content") is not None
        assert result.get("elapsed") > wait_time


def test_zos_operator_positive_verbose_with_quick_delay(ansible_zos_module):
    hosts = ansible_zos_module
    wait_time_s=10
    results = hosts.all.zos_operator(
        cmd="d u,all", verbose=True, wait_time_s=wait_time_s
    )

    for result in results.contacted.values():
        assert result["rc"] == 0
        assert result.get("changed") is True
        assert result.get("content") is not None
        # Account for slower network
        assert result.get('elapsed') <= (2 * wait_time_s)


def test_zos_operator_positive_verbose_blocking(ansible_zos_module):
    if zoau_version_checker.is_zoau_version_higher_than("1.2.4.5"):
        hosts = ansible_zos_module
        wait_time_s=5
        results = hosts.all.zos_operator(
            cmd="d u,all", verbose=True, wait_time_s=wait_time_s
        )

        for result in results.contacted.values():
            assert result["rc"] == 0
            assert result.get("changed") is True
            assert result.get("content") is not None
            # Account for slower network
            assert result.get('elapsed') >= wait_time_s



def test_response_come_back_complete(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="\\$dspl")
    res = {}
    res["stdout"] = []
    for result in results.contacted.values():
        stdout = result.get('content')
        # HASP646 Only appears in the last line that before did not appears
        last_line = len(stdout)
        assert "HASP646" in stdout[last_line - 1]
