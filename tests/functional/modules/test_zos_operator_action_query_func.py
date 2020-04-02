# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def test_zos_operator_action_query_goldenpath(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query()
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("message_text", ""):
                hosts.all.zos_operator(cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert not result.get("actions") is None


def test_zos_operator_action_query_a_message(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(message_id="IEE094D")
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("message_text", ""):
                hosts.all.zos_operator(cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert not result.get("actions") is None


def test_zos_operator_action_query_some_messages(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_operator(cmd="DUMP COMM=('test dump')")
    results = hosts.all.zos_operator_action_query(message_id="IEE*")
    try:
        for action in results.get("actions"):
            if "SPECIFY OPERAND(S) FOR DUMP" in action.get("message_text", ""):
                hosts.all.zos_operator(cmd="{0}cancel".format(action.get("number")))
    except Exception:
        pass
    for result in results.contacted.values():
        assert not result.get("actions") is None


def test_zos_operator_action_query_invalid_message(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator_action_query(message_id="invalid-message")
    for result in results.contacted.values():
        assert result.get("actions") is None


# * The below tests appear to be repeats of the above

# def test_zos_operator_action_query_from_special_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(system="tbd")
#     for result in results.contacted.values():
#         assert not result.get("actions") is None


# def test_zos_operator_action_query_from_some_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(system="tbd*")
#     for result in results.contacted.values():
#         assert not result.get("actions") is None


# def test_zos_operator_action_query_from_invalid_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(system="invalid-system")
#     for result in results.contacted.values():
#         assert result.get("actions") is None


# def test_zos_operator_action_query_from_special_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(job_name="tbd")
#     for result in results.contacted.values():
#         assert not result.get("actions") is None


# def test_zos_operator_action_query_from_some_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(job_name="tbd*")
#     for result in results.contacted.values():
#         assert not result.get("actions") is None


# def test_zos_operator_action_query_from_invalid_system(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_operator_action_query(job_name="invalid-jobname")
#     for result in results.contacted.values():
#         assert result.get("actions") is None
