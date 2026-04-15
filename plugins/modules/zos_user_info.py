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

EXAMPLES = r"""
- name: Get basic user profile info
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    scope: user

- name: Get user profile info with segments
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    scope: user
    segments:
      - dfp
      - tso
      - omvs
      - operparm
      - lang
      - csdata

- name: Get basic group profile info
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    scope: group

- name: Get group profile info with DFP and OMVS segments
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    scope: group
    segments:
      - dfp
      - omvs
"""

import re
from ansible.module_utils.basic import AnsibleModule

# Define the fields you know are space-separated lists
FIELDS_TO_SPLIT = {
    "MONITOR",
    "MSCOPE",
    "ROUTCODE",  # (ROUTCODE is comma-separated)
    "ATTRIBUTES",
    "CLASS AUTHORIZATIONS"
}


def extract_generic_segment(output_text, target_segment_name):
    """
    A reusable engine that parses a specific segment from RACF LISTUSER output.
    Handles both 'KEY= VALUE' and 'KEY: VALUE' formats.
    """
    segment_data = {}
    in_target_segment = False

    # Matches ANY segment header, capturing if it starts with "NO " and the name
    header_pattern = re.compile(r'^(NO )?([A-Z]+) INFORMATION')

    # Matches keys and values separated by EITHER '=' or ':'
    kv_pattern = re.compile(r'^\s*([A-Z0-9\s]+?)\s*[=:]\s*(.*)')

    lines = output_text.strip().split('\n')

    for line in lines:
        line = line.strip()

        if not line or line.startswith('---') or line.startswith('LU ') or line.startswith('LG '):
            continue

        # Check if the line is a segment header
        header_match = header_pattern.match(line)
        if header_match:
            is_no_info = header_match.group(1)  # e.g., "NO "
            current_header = header_match.group(2)  # e.g., "OMVS", "LANGUAGE"

            if current_header == target_segment_name:
                if is_no_info:
                    return {}  # Returns empty dict if "NO [SEGMENT] INFORMATION"
                in_target_segment = True
            else:
                in_target_segment = False  # Turn off if we hit a different header
            continue

        # Extract data if we are inside the requested segment
        if in_target_segment:
            kv_match = kv_pattern.match(line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                # segment_data[key] = value
                # --- THE NEW LIST LOGIC ---
                if key in FIELDS_TO_SPLIT:
                    if key == "ROUTCODE":
                        # Routcodes use commas (e.g., "1:2,11")
                        segment_data[key] = [v.strip() for v in value.split(',') if v.strip()]
                    else:
                        # Split by space for things like MONITOR or MSCOPE
                        segment_data[key] = [v.strip() for v in value.split() if v.strip()]
                else:
                    segment_data[key] = value

    return segment_data


def parse_tso(output_text):
    return extract_generic_segment(output_text, "TSO")


def parse_omvs(output_text):
    return extract_generic_segment(output_text, "OMVS")


def parse_dfp(output_text):
    return extract_generic_segment(output_text, "DFP")


def parse_operparm(output_text):
    return extract_generic_segment(output_text, "OPERPARM")


def parse_language(output_text):
    return extract_generic_segment(output_text, "LANGUAGE")


def parse_csdata(output_text):
    return extract_generic_segment(output_text, "CSDATA")


def run_module():
    """Main module execution function."""

    module_args = {
        'name': {
            'type': 'str',
            'required': True
        },
        'scope': {
            'type': 'str',
            'required': True,
            'choices': ['user', 'group']
        },
        'segments': {
            'type': 'list',
            'elements': 'str',
            'required': False,
            'choices': ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata']
        }
    }

    result = {
        'changed': False,
        'rc': 0,
        'stdout': '',
        'stderr': '',
        'cmd': '',
        'msg': ''
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    name = module.params['name']
    scope = module.params['scope'].lower()
    segments = [s.lower() for s in (module.params.get('segments') or [])]

    # Build the appropriate TSO command based on scope and segments
    if scope == 'user':
        # Valid segments for user: dfp, tso, omvs, operparm, lang, csdata
        valid_user_segments = ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata']

        # Filter segments to only valid ones for user
        filtered_segments = [s for s in segments if s in valid_user_segments]

        # Build command - start with LU and user name
        cmd = f'LU {name}'

        # Add segments if specified
        if filtered_segments:
            # Map segment names to TSO command keywords
            segment_map = {
                'dfp': 'DFP',
                'tso': 'TSO',
                'omvs': 'OMVS',
                'operparm': 'OPERPARM',
                'lang': 'LANG',
                'csdata': 'CSDATA'
            }
            segment_keywords = [segment_map[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"
    else:
        # Valid segments for group: dfp, omvs, csdata
        valid_group_segments = ['dfp', 'omvs', 'csdata']

        # Filter segments to only valid ones for group
        filtered_segments = [s for s in segments if s in valid_group_segments]

        # Build command - start with LG and group name
        cmd = f'LG {name}'

        # Add segments if specified
        if filtered_segments:
            # Map segment names to TSO command keywords
            segment_map = {
                'dfp': 'DFP',
                'omvs': 'OMVS',
                'csdata': 'CSDATA'
            }
            segment_keywords = [segment_map[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"

    result['cmd'] = cmd

    # Execute the TSO command
    rc, stdout, stderr = module.run_command(f'tsocmd "{cmd}"')

    # Check if the profile was not found
    if rc != 0 or 'NAME NOT FOUND IN RACF DATA SET' in stdout.upper() or f'INVALID {scope.upper()} NAME' in stdout.upper():
        result['rc'] = rc
        result['stdout'] = stdout
        result['stderr'] = stderr
        result['msg'] = f"Profile '{name}' not found in RACF database"
        module.fail_json(**result)

    # Parse segments based on scope
    if scope == 'user':
        final_user_profile = {
            "TSO": parse_tso(stdout),
            "OMVS": parse_omvs(stdout),
            "DFP": parse_dfp(stdout),
            "OPERPARM": parse_operparm(stdout),
            "LANGUAGE": parse_language(stdout),
            "CSDATA": parse_csdata(stdout)
        }
    else:  # scope == 'group'
        final_user_profile = {
            "OMVS": parse_omvs(stdout),
            "DFP": parse_dfp(stdout),
            "CSDATA": parse_csdata(stdout)
        }

    result['rc'] = rc
    result['stdout'] = stdout
    result['stderr'] = stderr
    result['profile'] = final_user_profile

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
