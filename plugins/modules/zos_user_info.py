#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2026
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

DOCUMENTATION = r"""
---
module: zos_user_info
version_added: '2.0.0'
author:
  - "Yogesh Rana (@yrana17)"
short_description: Retrieve user and group profile information from RACF
description:
  - The L(zos_user_info,./zos_user_info.html) module retrieves detailed information
    about RACF user and group profiles.
  - The module executes RACF LISTUSER or LISTGRP TSO commands and parses the output
    into structured data.
  - This is an info module that does not make any changes to the system.
options:
  name:
    description:
      - Name of the RACF profile to retrieve information about.
      - Can be a user ID or group name depending on the I(scope) parameter.
    type: str
    required: true
  scope:
    description:
      - Whether to retrieve information about a user or a group profile.
    type: str
    required: true
    choices:
      - user
      - group
  segments:
    description:
      - List of segments to retrieve from the profile.
      - If not specified, only base profile information is retrieved.
      - For users, valid segments are C(dfp), C(tso), C(omvs), C(operparm), C(lang), C(csdata).
      - For groups, valid segments are C(dfp), C(omvs), C(csdata).
      - C(General) information is always retrieved.
      - Invalid segments for the specified scope will be ignored.
    type: list
    elements: str
    required: false
    choices:
      - dfp
      - tso
      - omvs
      - operparm
      - lang
      - csdata
"""