# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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

import time

import ansible.constants
import ansible.errors
import ansible.utils
import pytest
from pprint import pprint

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
        assert result.get("changed") is False
        assert result.get("exception") is not None


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
    #startmod = time.time()
    results = hosts.all.zos_operator(
        cmd="d u,all", verbose=True, wait_time_s=wait_time_s
    )
    # endmod = time.time()
    # timediff = endmod - startmod
    # assert timediff < 15

    for result in results.contacted.values():
        pprint(result)
        assert result["rc"] == 0
        assert result.get("changed") is True
        assert result.get("content") is not None
        # Account for slower network
        assert result.get('elapsed') <= (2 * wait_time_s)
