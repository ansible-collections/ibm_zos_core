# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest
from pprint import pprint

__metaclass__ = type


# TODO: make commented-out tests generic for use with different z/OS environments (including CI/CD pipeline)
# ? add set-up steps to handle environment configuration so expected values are present?


def test_zos_operator_action_query_goldenpath(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query()
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_a_message(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(message_id="tbd")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_some_messages(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(message_id="tbd*")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_invalid_message(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(message_id="invalid-message")
    for result in results.contacted.values():
        assert result.get('actions') is None


def test_zos_operator_action_query_from_special_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(system="tbd")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_from_some_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(system="tbd*")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_from_invalid_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(system="invalid-system")
    for result in results.contacted.values():
        assert result.get('actions') is None


def test_zos_operator_action_query_from_special_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(job_name="tbd")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_from_some_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(job_name="tbd*")
    for result in results.contacted.values():
        assert not result.get('actions') is None


def test_zos_operator_action_query_from_invalid_system(ansible_zos_module):
    hosts = ansible_zos_module
    passed = True
    results = hosts.all.zos_operator_action_query(job_name="invalid-jobname")
    for result in results.contacted.values():
        assert result.get('actions') is None
