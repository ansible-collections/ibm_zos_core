# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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

import pytest
__metaclass__ = type

TMP_DIRECTORY = "/tmp/pytest-support-mode-output"

def assert_module_did_not_fail(results):
    for result in results.contacted.values():
        assert (
            result.get("failed", False) is not True
            and not result.get("exception", "")
            and "error" not in result.get("msg", "").lower()
            )

def assert_controller_file_exists(hosts, path):
    results = hosts.localhost.stat(path=path)
    for result in results.contacted.values():
        assert result.get("stat").get("exists") is True

def assert_controller_file_does_not_exist(hosts, path):
    results = hosts.localhost.stat(path=path)
    for result in results.contacted.values():
        assert result.get("stat").get("exists") is False

def setup_test_directory(hosts, path):
    hosts.localhost.file(path=path, state="absent")
    hosts.localhost.file(path=path, state="directory")


def cleanup_test_directory(hosts, path):
    hosts.localhost.file(path=path, state="absent")


def test_support_mode_role_default(ansible_zos_module):
    hosts = ansible_zos_module
    controller_report = f"{TMP_DIRECTORY}/support_mode_report_controller.yml"
    managed_report = f"{TMP_DIRECTORY}/support_mode_report_managed_node.yml"
    try:
        setup_test_directory(hosts, TMP_DIRECTORY)
        hosts.all.set_fact(
            support_mode_output_dir=TMP_DIRECTORY
        )
        results = hosts.all.include_role(
            name="support_mode"
        )
        assert_module_did_not_fail(results)
        assert_controller_file_exists(hosts, controller_report)
        assert_controller_file_exists(hosts, managed_report)
    finally:
        cleanup_test_directory(hosts, TMP_DIRECTORY)

def test_support_mode_role_with_syslog_false(ansible_zos_module):
    hosts = ansible_zos_module
    controller_report = f"{TMP_DIRECTORY}/support_mode_report_controller.yml"
    managed_report = f"{TMP_DIRECTORY}/support_mode_report_managed_node.yml"
    try:
        setup_test_directory(hosts, TMP_DIRECTORY)
        hosts.all.set_fact(
            support_mode_output_dir=TMP_DIRECTORY,
            support_mode_gather_syslog=False
        )
        results = hosts.all.include_role(
            name="support_mode"
        )
        assert_module_did_not_fail(results)
        assert_controller_file_exists(hosts, controller_report)
        assert_controller_file_exists(hosts, managed_report)

    finally:
        cleanup_test_directory(hosts, TMP_DIRECTORY)

def test_support_mode_role_with_log_false(ansible_zos_module):
    hosts = ansible_zos_module
    controller_report = f"{TMP_DIRECTORY}/support_mode_report_controller.yml"
    managed_report = f"{TMP_DIRECTORY}/support_mode_report_managed_node.yml"
    try:
        setup_test_directory(hosts, TMP_DIRECTORY)
        hosts.all.set_fact(
            support_mode_output_dir=TMP_DIRECTORY,
            controller_node_log_file=False,
            managed_node_log_file=False
        )
        results = hosts.all.include_role(
            name="support_mode"
        )
        assert_module_did_not_fail(results)
        assert_controller_file_does_not_exist(hosts, controller_report)
        assert_controller_file_does_not_exist(hosts, managed_report)

    finally:
        cleanup_test_directory(hosts, TMP_DIRECTORY)