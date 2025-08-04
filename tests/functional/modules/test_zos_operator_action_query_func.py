# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2025
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


def test_zos_operator_action_query_no_options(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query()
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass

    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_option_msg_id(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(msg_id="IEE094D")
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass

    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_option_msg_id_invalid_abbreviation(
    ansible_zos_module
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(msg_id="IEE")
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions") is not None
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("msg_id", ["IEE*", "*"])
def test_zos_operator_action_query_option_msg_id_regex(
    ansible_zos_module,
    msg_id
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(msg_id=msg_id)
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_option_system(ansible_zos_module):
    hosts = ansible_zos_module
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = ""
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "").strip()
    results = hosts.all.zos_operator_action_query(system=system_name)
    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_option_system_invalid_abbreviation(
    ansible_zos_module
):
    hosts = ansible_zos_module
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = ""
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "").strip()
    results = hosts.all.zos_operator_action_query(system=system_name[:-1])
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("msg_id", ["IEE*", "IEE094D", "*"])
def test_zos_operator_action_query_option_system_and_msg_id(
    ansible_zos_module,
    msg_id
):
    hosts = ansible_zos_module
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = ""
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "").strip()
    results = hosts.all.zos_operator_action_query(
        system=system_name, msg_id=msg_id
    )
    for result in results.contacted.values():
        assert result.get("actions")

def test_zos_operator_action_query_option_system_regex(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = "   "
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "   ").strip()
    results = hosts.all.zos_operator_action_query(
        system=system_name[:3] + "*")
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("msg_id", ["IEE*", "IEE094D", "*"])
def test_zos_operator_action_query_option_system_regex_and_msg_id(
    ansible_zos_module,
    msg_id
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = "   "
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "   ").strip()
    results = hosts.all.zos_operator_action_query(
        system=system_name[:3] + "*", msg_id=msg_id
    )
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("system", ["", "OVER8CHARS", "--BADNM", "invalid-system"])
def test_zos_operator_action_query_invalid_option_system(
    ansible_zos_module,
    system
):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(system=system)
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("msg_id", ["IEE*", "IEE094D", "*"])
def test_zos_operator_action_query_valid_msg_id_invalid_option_system(
    ansible_zos_module,
    msg_id
):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(
        system="invalid-system", msg_id=msg_id
    )
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize("msg_id", ["", "--BADNM", "invalid-message"])
def test_zos_operator_action_query_invalid_option_msg_id(
    ansible_zos_module,
    msg_id
):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(msg_id=msg_id)
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_valid_option_system_invalid_option_msg_id(
    ansible_zos_module
):
    hosts = ansible_zos_module
    sysinfo = hosts.all.shell(cmd="uname -n")
    system_name = ""
    for result in sysinfo.contacted.values():
        system_name = result.get("stdout", "").strip()
    results = hosts.all.zos_operator_action_query(
        system=system_name, msg_id="invalid-message"
    )
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_invalid_option_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(
        job_name="invalid-job-name")
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize(
    "msg_filter",
    [
        {"filter": "DUMP"},
        {"filter": "DUMP", "literal": True},
        {"filter": "^.*DUMP.*$", "literal": False},
        {"filter": "^.*OPERAND\\(S\\).*$", "literal": False}
    ]
)
def test_zos_operator_action_query_option_msg_filter_one_match(
    ansible_zos_module,
    msg_filter
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(
        msg_filter=msg_filter)
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions")
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize(
    "msg_filter",
    [
        {"filter": "DUMP"},
        {"filter": "DUMP", "literal": True},
        {"filter": "^.*DUMP.*$", "literal": False},
        {"filter": "^.*OPERAND\\(S\\).*$", "literal": False}
    ]
)
def test_zos_operator_action_query_option_msg_filter_multiple_matches(
    ansible_zos_module,
    msg_filter
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(
        msg_filter=msg_filter)
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions")
        assert len(result.get("actions")) > 1
        assert result.get("count") is not None
        assert result.get("changed") is not None

@pytest.mark.parametrize(
    "msg_filter",
    [
        {"filter": "IMS"},
        {"filter": "IMS", "literal": True},
        {"filter": "^.*IMS.*$", "literal": False},
    ]
)
def test_zos_operator_action_query_option_msg_filter_no_match(
    ansible_zos_module,
    msg_filter
):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(
        msg_filter=msg_filter)
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("msg_text", ""):
                hosts.all.zos_operator(
                    cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None

def test_zos_operator_action_query_invalid_option_msg_filter(
    ansible_zos_module
):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(
        msg_filter={"filter": "*DUMP", "literal": False})
    for result in results.contacted.values():
        assert result.get("actions") == []
        assert result.get("count") is not None
        assert result.get("changed") is not None
