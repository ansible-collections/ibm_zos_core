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

def test_support_mode_role_default(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.set_fact(support_mode_gather_syslog= False)
    results = hosts.all.include_role(name="support_mode")
    for result in results.contacted.values():
        assert not result.get("failed", False), "Role failed to execute"

def test_support_mode_role_with_syslog_true(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.set_fact(support_mode_gather_syslog= True)
    results = hosts.all.include_role(name="support_mode")
    for result in results.contacted.values():
        assert not result.get("failed", False), "Role failed with syslog=true"