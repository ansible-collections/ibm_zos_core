#!/usr/bin/python
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

DOCUMENTATION = r"""
---
module: zos_ping
version_added: 2.9
short_description: Ping z/OS and check dependencies.
description:
  - M(zos_ping) verifies the presence of z/OS Web Client Enablement Toolkit,
    iconv, and Python.
  - M(zos_ping) returns C(pong) when the target host is not missing any required
    dependencies.
  - If the target host is missing optional dependencies, the M(zos_ping) will
    return one or more warning messages.
  - If a required dependency is missing from the target host, an explanatory
    message will be returned with the module failure.
author:
  - "Vijay Katoch (@vijayka)"
  - "Blake Becker (@blakeinate)"
  - "Demetrios Dimatos (@ddimatos)"
options: {}
"""

EXAMPLES = r"""
- name: Ping the z/OS host and perform resource checks
  zos_ping:
  register: result
"""

RETURN = r"""
ping:
  description: Should contain the value "pong" on success.
  returned: always
  type: str
  sample: pong
warnings:
  description: List of warnings returned from stderr when performing resource checks.
  returned: failure
  type: list
  elements: str
"""
