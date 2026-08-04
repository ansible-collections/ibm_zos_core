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
version_added: '2.1.0'
author:
  - "Yogesh Rana (@yrana17)"
short_description: Retrieve user and group profile information from RACF
description:
  - Retrieve detailed information about RACF user and group profiles.
  - The module runs the RACF LISTUSER or LISTGRP TSO commands and parses the output into structured data.
  - This module does not make any changes to the system.
options:
  name:
    description:
      - The RACF profile name to retrieve.
      - For I(profile_type=user), this must be a single user ID.
      - For I(profile_type=group), this must be a single group name.
      - The name is case-insensitive and is normalized to uppercase before execution.
      - The name is a single continuous string with no spaces or blank characters.
    type: str
    required: true
  profile_type:
    description:
      - Specifies the type of RACF profile to retrieve information about.
      - When I(profile_type=user), retrieves user profile information using the LISTUSER command.
      - When I(profile_type=group), retrieves group profile information using the LISTGRP command.
    type: str
    required: true
    choices:
      - user
      - group
  segments:
    description:
      - List of RACF segments to retrieve from the profile.
      - If not specified, only the base profile information (C(base_segment)) is retrieved.
      - When I(profile_type=user), valid segments are C(dfp), C(tso), C(omvs), C(operparm), C(lang), C(csdata),
        C(cics), C(dce), C(eim), C(ovm), C(netview), C(nds), C(lnotes), C(workattr), C(proxy), and C(kerb).
      - When I(profile_type=group), valid segments are C(dfp), C(omvs), C(ovm), and C(csdata).
      - The C(base_segment) section is always retrieved regardless of this parameter.
      - Segments that do not apply to the requested I(profile_type) are ignored.
      - For example, user-only segments are ignored for group profiles.
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
      - cics
      - dce
      - eim
      - ovm
      - netview
      - nds
      - lnotes
      - workattr
      - proxy
      - kerb
"""

RETURN = r"""
changed:
  description: Indicates whether any changes were made to the system. Always C(false) for info modules.
  returned: always
  type: bool
  sample: false
cmd:
  description: The RACF command that was run with the tsocmd command.
  returned: always
  type: str
  sample: "LISTUSER TESTU01 TSO OMVS"
rc:
  description: >
    Return code from the RACF command execution.
    Returns 0 on success, or a non-zero value on failure (for example, 8 when the profile is not found).
  returned: always
  type: int
  sample: 0
stdout:
  description: Standard output from the RACF command execution.
  returned: always
  type: str
  sample: "USER=TESTU01  NAME=TEST USER 01  OWNER=ADMIN01  CREATED=2025/01/10"
stderr:
  description: >
    Standard error from the RACF command execution. The TSO command itself
    is not included; it is available in the C(cmd) field.
  returned: always
  type: str
  sample: ""
msg:
  description: >
    Error message describing the failure.
  returned: failure
  type: str
  sample: "Profile 'TESTU01' not found in RACF database"
segments:
  description:
    - Dictionary of RACF profile information organized by segment.
    - Always includes C(base_segment) and C(group) or C(users). Additional segments are only present if specified in the I(segments) option.
    - Keys and values are dynamic based on RACF output. Segments with no data are returned as empty dictionaries.
  returned: success
  type: dict
  contains:
    base_segment:
      description:
        - Base profile information, always returned regardless of the I(segments) parameter.
        - When I(profile_type=user), contains user attributes such as C(USER-ID), C(NAME), C(DEFAULT-GROUP), C(OWNER), C(CREATED),
          C(PASSDATE), C(PASS-INTERVAL), and C(ATTRIBUTES).
        - When I(profile_type=group), contains group attributes such as C(OWNER), C(CREATED), C(SUPERIOR GROUP), C(INSTALLATION DATA),
          C(SUBGROUP(S)), C(TERMUACC), and C(UNIVERSAL).
        - The exact keys present depend on the profile's RACF configuration.
        - C(ATTRIBUTES) and C(CLASS AUTHORIZATIONS) are always returned as lists.
      returned: always
      type: dict
      sample:
        USER: "TESTU01"
        NAME: "TEST USER 01"
        DEFAULT-GROUP: "TSTGRP01"
        PASSDATE: "2026/04/15"
        PASS-INTERVAL: "90"
        ATTRIBUTES: ["SPECIAL", "OPERATIONS"]
        OWNER: "ADMIN01"
        CREATED: "2025/01/10"
    group:
      description:
        - Group connection information for user profiles, keyed by group name.
        - Each value contains connection attributes such as C(AUTH), C(CONNECT-OWNER), C(CONNECT-DATE), C(LAST-CONNECT),
          C(REVOKE DATE), C(RESUME DATE), and C(CONNECT ATTRIBUTES).
        - Only returned when I(profile_type=user).
      returned: when profile_type=user
      type: dict
      sample:
        TSTGRP01:
          CONNECT-OWNER: "ADMIN01"
          CONNECT-DATE: "2025/01/10"
          LAST-CONNECT: "2026/04/29"
          REVOKE DATE: "NONE"
          RESUME DATE: "NONE"
    users:
      description:
        - Connected user information for group profiles, keyed by username.
        - Each value contains connection attributes such as C(ACCESS), C(ACCESS COUNT), C(UNIVERSAL ACCESS),
          C(REVOKE DATE), C(RESUME DATE), and C(CONNECT ATTRIBUTES).
        - Only returned when I(profile_type=group).
      returned: when profile_type=group
      type: dict
      sample:
        TESTU01:
          ACCESS: "JOIN"
          ACCESS COUNT: "000047"
          UNIVERSAL ACCESS: "READ"
          REVOKE DATE: "NONE"
          RESUME DATE: "NONE"
        TESTU02:
          ACCESS: "USE"
          ACCESS COUNT: "000012"
          UNIVERSAL ACCESS: "NONE"
    TSO:
      description:
        - TSO segment information for user profiles.
        - Contains dynamic key-value pairs such as C(ACCTNUM), C(PROC), C(SIZE), C(MAXSIZE), C(JOBCLASS), C(MSGCLASS), C(SYSOUTCLASS),
          C(USERDATA), C(COMMAND), etc.
        - The exact keys present depend on the user's TSO configuration in RACF.
        - Only returned when I(profile_type=user) and C(tso) is included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies tso
      type: dict
      sample:
        ACCTNUM: "33000"
        HOLDCLASS: "H"
        JOBCLASS: "A"
        MSGCLASS: "X"
    OMVS:
      description:
        - OMVS segment information for user and group profiles.
        - Contains dynamic key-value pairs such as C(UID), C(HOME), C(PROGRAM), C(CPUTIMEMAX), C(ASSIZEMAX), C(FILEPROCMAX), C(PROCUSERMAX), etc.
        - The exact keys present depend on the OMVS configuration in RACF.
        - Only returned when C(omvs) is included in the I(segments) parameter.
      returned: when segments specifies omvs
      type: dict
      sample:
        UID: "0000000201"
        HOME: "/u/testu01"
        PROGRAM: "/bin/sh"
        CPUTIMEMAX: "NONE"
        ASSIZEMAX: "NONE"
    DFP:
      description:
        - DFP (Data Facility Product) segment information for user and group profiles.
        - Contains dynamic key-value pairs related to data management such as C(MGMTCLAS), C(STORCLAS), C(DATACLAS), etc.
        - The exact keys present depend on the DFP configuration in RACF.
        - Only returned when C(dfp) is included in the I(segments) parameter.
      returned: when segments specifies dfp
      type: dict
      sample:
        MGMTCLAS: "STANDARD"
        STORCLAS: "SCPERM"
        DATACLAS: "DCEXTL"
    OPERPARM:
      description:
        - OPERPARM segment information for user profiles.
        - Contains operator parameters such as C(STORAGE), C(AUTH), C(ALTGRP), C(AUTO), C(HC), C(INTIDS), C(LEVEL), C(LOGCMDRESP), C(MIGID), etc.
        - C(MONITOR), C(MSCOPE), C(MFORM), and C(ROUTCODE) are always returned as lists.
        - The exact keys present depend on the operator configuration in RACF.
        - Only returned when I(profile_type=user) and C(operparm) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies operparm
      type: dict
      sample:
        STORAGE: "YES"
        ALTGRP: "YES"
        MIGID: "NO"
        MONITOR: [ "JOBNAMES", "SESS" ]
        MSCOPE: [ "ALL" ]
        MFORM: [ "M", "T" ]
        ROUTCODE: [ "1:2", "11" ]
    LANGUAGE:
      description:
        - LANGUAGE segment information for user profiles.
        - Contains language-related settings such as C(PRIMARY) and C(SECONDARY) language codes.
        - The exact keys present depend on the language configuration in RACF.
        - Only returned when I(profile_type=user) and C(lang) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies lang
      type: dict
      sample:
        PRIMARY LANGUAGE: "ENU"
        SECONDARY LANGUAGE: "JPN"
    CSDATA:
      description:
        - CSDATA (Custom Data) segment information for user and group profiles.
        - Contains custom application-specific data defined in RACF.
        - The exact keys present depend on what custom data has been configured for the profile.
        - Only returned when C(csdata) is included in the I(segments) parameter.
      returned: when segments specifies csdata
      type: dict
    CICS:
      description:
        - CICS segment information for user profiles.
        - Contains CICS-related configuration and resource limits.
        - Only returned when I(profile_type=user) and C(cics) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies cics
      type: dict
    DCE:
      description:
        - DCE (Distributed Computing Environment) segment information for user profiles.
        - Contains DCE-related configuration and identifiers.
        - Only returned when I(profile_type=user) and C(dce) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies dce
      type: dict
    EIM:
      description:
        - EIM (Enterprise Identity Mapping) segment information for user profiles.
        - Contains EIM-related configuration and mappings.
        - Only returned when I(profile_type=user) and C(eim) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies eim
      type: dict
    OVM:
      description:
        - OVM (OpenExtensions VM) segment information for user and group profiles.
        - Contains OVM-related configuration and settings.
        - Only returned when C(ovm) is included in the I(segments) parameter.
      returned: when segments specifies ovm
      type: dict
    NETVIEW:
      description:
        - NETVIEW segment information for user profiles.
        - Contains NetView-related configuration and authorities.
        - Only returned when I(profile_type=user) and C(netview) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies netview
      type: dict
    NDS:
      description:
        - NDS (Network Directory Services) segment information for user profiles.
        - Contains NDS-related configuration and identifiers.
        - Only returned when I(profile_type=user) and C(nds) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies nds
      type: dict
    LNOTES:
      description:
        - LNOTES (Lotus Notes) segment information for user profiles.
        - Contains Lotus Notes-related configuration and settings.
        - Only returned when I(profile_type=user) and C(lnotes) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies lnotes
      type: dict
    WORKATTR:
      description:
        - WORKATTR (Work Attributes) segment information for user profiles.
        - Contains work-related attributes and organizational information.
        - Only returned when I(profile_type=user) and C(workattr) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies workattr
      type: dict
    PROXY:
      description:
        - PROXY segment information for user profiles.
        - Contains proxy-related configuration and authorities.
        - Only returned when I(profile_type=user) and C(proxy) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies proxy
      type: dict
    KERB:
      description:
        - KERB (Kerberos) segment information for user profiles.
        - Contains Kerberos-related configuration, principals, and encryption settings.
        - Only returned when I(profile_type=user) and C(kerb) are included in the I(segments) parameter.
      returned: when profile_type is user and segments specifies kerb
      type: dict
"""

EXAMPLES = r"""
- name: Get basic user profile information
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    profile_type: user

- name: Get user profile information with TSO and OMVS segment
  ibm.ibm_zos_core.zos_user_info:
    name: "TESTU01"
    profile_type: user
    segments:
      - tso
      - omvs

- name: Get user profile with multiple segments
  ibm.ibm_zos_core.zos_user_info:
    name: "TESTU01"
    profile_type: user
    segments:
      - tso
      - omvs
      - dfp
      - lang
      - operparm

- name: Get user profile with all segments
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    profile_type: user
    segments:
      - dfp
      - tso
      - omvs
      - operparm
      - lang
      - csdata
      - cics
      - dce
      - eim
      - ovm
      - netview
      - nds
      - lnotes
      - workattr
      - proxy
      - kerb

- name: Get basic group profile information
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    profile_type: group

- name: Get group profile with multiple segments
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    profile_type: group
    segments:
      - dfp
      - omvs
      - ovm
      - csdata
"""


import re
from typing import Dict, Any

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dependency_checker import (
    validate_dependencies,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger


# Fields that contain space-separated lists in RACF output
# These fields will be split into Python lists by whitespace
SPLIT_BY_SPACE = {
    "MONITOR",
    "MSCOPE",
    "ATTRIBUTES",
    "CLASS AUTHORIZATIONS",
    "MFORM",
    "KEY ENCRYPTION TYPE"
}

# Fields that contain comma-separated lists in RACF output
# These fields will be split into Python lists by commas
SPLIT_BY_COMMA = {
    "ROUTCODE"
}

# Regex patterns for parsing RACF output
RACF_HEADER_PATTERN = r'^(NO )?([A-Z]+) INFORMATION'
RACF_KV_PATTERN = r'^\s*([A-Z0-9\s]+?)\s*[=:]\s*(.*)'
RACF_HEADER_RE = re.compile(RACF_HEADER_PATTERN)
RACF_KV_RE = re.compile(RACF_KV_PATTERN)

# Compiled key-value pattern for LISTUSER base section parsing
_USER_RACF_KEYS = r'(?:REVOKE DATE|RESUME DATE|CLASS AUTHORIZATIONS|CONNECT ATTRIBUTES|[A-Z0-9-]+)'
USER_KV_PATTERN = re.compile(rf'\b({_USER_RACF_KEYS})=(.*?)(?=\s+{_USER_RACF_KEYS}=|$)')

# Compiled key-value pattern for LISTGRP base section parsing
_GROUP_RACF_KEYS = r'(?:SUPERIOR GROUP|INSTALLATION DATA|MODEL DATA SET|SUBGROUP\(S\)|CONNECT ATTRIBUTES|REVOKE DATE|RESUME DATE|[A-Z0-9-]+)'
GROUP_KV_PATTERN = re.compile(rf'\b({_GROUP_RACF_KEYS})=(.*?)(?=\s+{_GROUP_RACF_KEYS}=|$)')

# Prefixes to skip when parsing RACF output
SKIP_PREFIXES = ('---', 'LISTUSER ', 'LISTGRP ', 'INFORMATION FOR GROUP')


def extract_generic_segment(output_text: str, target_segment_name: str) -> Dict[str, Any]:
    """
    Extract and parse a specific RACF segment from command output.

    Handles both 'KEY=VALUE' and 'KEY: VALUE' formats. Automatically splits
    fields listed in SPLIT_BY_SPACE or SPLIT_BY_COMMA into lists.

    Args:
        output_text: Raw RACF LISTUSER or LISTGRP command output.
        target_segment_name: Segment name to extract (e.g., 'TSO', 'OMVS', 'DFP').

    Returns:
        Dictionary with parsed segment data. Empty dict if segment not found or has no data.
    """
    segment_data = {}
    in_target_segment = False

    lines = output_text.strip().split('\n')

    for line in lines:
        line = line.strip()

        if not line or line.startswith(SKIP_PREFIXES):
            continue

        # Check if the line is a segment header
        header_match = RACF_HEADER_RE.match(line)
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
            kv_match = RACF_KV_RE.match(line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()

                # Split fields based on their delimiter type
                if key in SPLIT_BY_COMMA:
                    segment_data[key] = [v.strip() for v in value.split(',') if v.strip()]
                elif key in SPLIT_BY_SPACE:
                    segment_data[key] = [v.strip() for v in value.split() if v.strip()]
                else:
                    segment_data[key] = value

    return segment_data


def parse_base_user_info(output_text: str) -> Dict[str, Any]:
    """
    Parse base user profile information from RACF LISTUSER output.

    Extracts user attributes and group connections from the base section
    (before segment headers like "TSO INFORMATION").

    Args:
        output_text: Raw RACF LISTUSER command output.

    Returns:
        Dictionary containing 'base_segment' (user attributes) and 'group'
        (group connection details for each connected group).
    """
    # Initialize the clean, split structure immediately
    base_data = {
        "base_segment": {},
        "group": {}
    }

    KEYS_TO_SPLIT = {"ATTRIBUTES", "CLASS AUTHORIZATIONS"}

    lines = output_text.strip().split('\n')

    parsing_logon = False
    ignoring_category = False
    last_key = None
    current_group = None

    for line in lines:
        original_line = line
        line = line.strip()

        if not line or line.startswith(SKIP_PREFIXES):
            continue

        # ==========================================
        # If we hit an optional segment header, the base section is over. Stop looping.
        # ==========================================
        if RACF_HEADER_RE.match(line):
            break

        if line.startswith('SECURITY-LEVEL=') or line.startswith('SECURITY-LABEL='):
            last_key = None
            current_group = None
            continue

        if line.startswith('CATEGORY-AUTHORIZATION'):
            ignoring_category = True
            last_key = None
            current_group = None
            continue

        if ignoring_category:
            ignoring_category = False
            continue

        # Target routing for non-standard lines
        target_dict = base_data["group"][current_group] if current_group else base_data["base_segment"]

        if line.startswith('LOGON ALLOWED'):
            parsing_logon = True
            target_dict['LOGON_SCHEDULE'] = []
            last_key = None
            continue

        if parsing_logon:
            if '=' in line:
                parsing_logon = False
            else:
                target_dict['LOGON_SCHEDULE'].append(line)
                continue

        if line.startswith('NO-') and '=' not in line:
            actual_key = line[3:]
            target_dict[actual_key] = "NONE"
            last_key = actual_key
            continue

        matches = USER_KV_PATTERN.findall(line)

        if matches:
            for key, value in matches:
                key = key.strip()
                value = value.strip()

                if key == "GROUP":
                    current_group = value
                    base_data["group"][current_group] = {}
                    last_key = key
                    continue

                # Route to specific group, OR the base_segment dictionary
                target_dict = base_data["group"][current_group] if current_group else base_data["base_segment"]

                if key in KEYS_TO_SPLIT:
                    new_items = value.split()
                else:
                    new_items = [value]

                if key in target_dict:
                    if not isinstance(target_dict[key], list):
                        target_dict[key] = [target_dict[key]]
                    target_dict[key].extend(new_items)
                else:
                    if key in KEYS_TO_SPLIT or len(new_items) > 1:
                        target_dict[key] = new_items
                    else:
                        target_dict[key] = new_items[0]

                last_key = key

        elif last_key:
            target_dict = base_data["group"][current_group] if current_group else base_data["base_segment"]
            if isinstance(target_dict[last_key], list):
                target_dict[last_key][-1] += original_line.strip()
            else:
                target_dict[last_key] += original_line.strip()

    return base_data


def parse_base_group_info(output_text: str) -> Dict[str, Any]:
    """
    Parse base group profile information from RACF LISTGRP output.

    Extracts group attributes and connected users from the base section
    (before segment headers).

    Args:
        output_text: Raw RACF LISTGRP command output.

    Returns:
        Dictionary containing 'base_segment' (group attributes) and 'users'
        (connection details for each connected user).
    """
    base_data = {
        "base_segment": {},
        "users": {}  # Houses all the nested users
    }

    lines = output_text.strip().split('\n')

    parsing_users = False
    current_user = None
    last_key = None

    for line in lines:
        original_line = line
        line = line.strip()

        # Skip headers and empty lines
        if not line or line.startswith(SKIP_PREFIXES):
            continue

        # ==========================================
        # 1. THE STOP CONDITION
        # ==========================================
        if RACF_HEADER_RE.match(line):
            break

        # ==========================================
        # 2. BOOLEANS & "NO " FLAGS
        # ==========================================
        if line in ['TERMUACC', 'NOTERMUACC', 'UNIVERSAL']:
            base_data['base_segment'][line] = True
            last_key = None
            continue

        if line == 'NO INSTALLATION DATA':
            base_data['base_segment']['INSTALLATION DATA'] = "NONE"
            last_key = None
            continue

        if line == 'NO MODEL DATA SET':
            base_data['base_segment']['MODEL DATA SET'] = "NONE"
            last_key = None
            continue

        if line == 'NO SUBGROUPS':
            base_data['base_segment']['SUBGROUP(S)'] = []
            last_key = None
            continue

        # ==========================================
        # 3. USER TABLE NESTING
        # ==========================================
        if line.startswith('USER(S)='):
            parsing_users = True
            last_key = None
            continue

        if parsing_users:
            if '=' not in line:
                # It's a new user row (e.g. "TSTUSER  JOIN  000047  READ")
                parts = line.split()
                if len(parts) >= 4:
                    current_user = parts[0]
                    base_data['users'][current_user] = {
                        "ACCESS": parts[1],
                        "ACCESS COUNT": parts[2],
                        "UNIVERSAL ACCESS": parts[3]
                    }
                last_key = None
            else:
                # It's a nested attribute for the current user (e.g. "REVOKE DATE=NONE")
                matches = GROUP_KV_PATTERN.findall(line)
                for key, value in matches:
                    key = key.strip()
                    value = value.strip()
                    if current_user:
                        base_data['users'][current_user][key] = value
            continue  # We handled the user row, skip the general processing below

        # ==========================================
        # 4. GENERAL KEY EXTRACTION & CONTINUATION
        # ==========================================
        matches = GROUP_KV_PATTERN.findall(line)

        if matches:
            for key, value in matches:
                key = key.strip()
                value = value.strip()

                # Auto-split SUBGROUP(S) into an array right away
                if key == "SUBGROUP(S)":
                    base_data['base_segment'][key] = value.split()
                else:
                    base_data['base_segment'][key] = value

                last_key = key

        elif last_key:
            # Special Continuation for SUBGROUP(S)
            # Since subgroups are just space-separated words wrapping lines, we use .extend()
            if last_key == "SUBGROUP(S)":
                base_data['base_segment'][last_key].extend(line.split())
            else:
                # Standard continuation gluing
                if isinstance(base_data['base_segment'][last_key], list):
                    base_data['base_segment'][last_key][-1] += original_line.strip()
                else:
                    base_data['base_segment'][last_key] += original_line.strip()

    return base_data


# Segment name mapping: maps input segment names to RACF segment names
# Used for both TSO command construction and output parsing
SEGMENT_NAME_MAP = {
    'tso': 'TSO',
    'omvs': 'OMVS',
    'dfp': 'DFP',
    'operparm': 'OPERPARM',
    'lang': 'LANGUAGE',
    'csdata': 'CSDATA',
    'cics': 'CICS',
    'dce': 'DCE',
    'eim': 'EIM',
    'ovm': 'OVM',
    'netview': 'NETVIEW',
    'nds': 'NDS',
    'lnotes': 'LNOTES',
    'workattr': 'WORKATTR',
    'proxy': 'PROXY',
    'kerb': 'KERB'
}

# Valid segments for group profiles — subset of SEGMENT_NAME_MAP keys
VALID_GROUP_SEGMENTS = frozenset(['dfp', 'omvs', 'ovm', 'csdata'])


def run_module():
    """
    Execute the zos_user_info module.

    Retrieves RACF user or group profile information by executing LISTUSER or
    LISTGRP commands and parsing the output into structured data.
    """

    module_args = {
        'name': {
            'type': 'str',
            'required': True
        },
        'profile_type': {
            'type': 'str',
            'required': True,
            'choices': ['user', 'group']
        },
        'segments': {
            'type': 'list',
            'elements': 'str',
            'required': False,
            'choices': ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata',
                        'cics', 'dce', 'eim', 'ovm', 'netview', 'nds',
                        'lnotes', 'workattr', 'proxy', 'kerb']
        }
    }

    result = {
        'changed': False,
        'rc': 0,
        'cmd': ''
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    validate_dependencies(module)

    args_def = {
        'name': {
            'arg_type': 'str',
            'required': True
        },
        'profile_type': {
            'arg_type': 'str',
            'required': True
        },
        'segments': {
            'arg_type': 'list',
            'elements': 'str',
            'required': False
        }
    }

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    # Initialize logging module
    module_verbosity_level = module._verbosity
    SingletonLogger().get_logger(module_verbosity_level)

    name = module.params.get("name", "").strip()
    name_parts = name.split()
    if len(name_parts) > 1:
        module.fail_json(
            msg="Invalid value for parameter 'name': '{0}'. "
                "Expected a single RACF profile name with no spaces or blank characters.".format(name)
        )
    name = name.upper()
    profile_type = module.params['profile_type']
    segments = list(module.params.get('segments') or [])

    # Build the appropriate TSO command based on profile_type and segments
    if profile_type == 'user':
        # Filter segments to valid ones for user (all SEGMENT_NAME_MAP keys are valid)
        filtered_segments = [s for s in segments if s in SEGMENT_NAME_MAP]

        # Build command - start with LISTUSER and user name
        cmd = f'LISTUSER {name}'

        # Add segments if specified
        if filtered_segments:
            segment_keywords = [SEGMENT_NAME_MAP[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"
    else:
        # Filter segments to valid ones for group
        filtered_segments = [s for s in segments if s in VALID_GROUP_SEGMENTS]

        # Build command - start with LISTGRP and group name
        cmd = f'LISTGRP {name}'

        # Add segments if specified
        if filtered_segments:
            segment_keywords = [SEGMENT_NAME_MAP[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"

    result['cmd'] = cmd

    # Execute the TSO command
    rc, stdout, stderr = module.run_command(['tsocmd', cmd])

    # Set command output in result dict immediately after execution
    result['rc'] = rc
    result['stdout'] = stdout
    # Only include stderr if it contains something other than the command echo
    result['stderr'] = '' if stderr.strip() == cmd else stderr

    # Check if the profile was not found
    if rc != 0:
        # On failure: surface RACF error in stderr, blank stdout for a clean response
        result['stdout'] = ''
        result['stderr'] = stdout.strip()
        stdout_upper = stdout.upper()
        if ('NAME NOT FOUND IN RACF DATA SET' in stdout_upper
                or f'INVALID {profile_type.upper()} NAME' in stdout_upper
                or 'INVALID USERID' in stdout_upper
                or 'UNABLE TO LOCATE' in stdout_upper):
            result['msg'] = f"Profile '{name}' not found in RACF database"
        else:
            result['msg'] = f"RACF command failed with rc={rc}"
        module.fail_json(**result)

    # Parse segments based on profile_type
    try:
        if profile_type == 'user':
            base_data = parse_base_user_info(stdout)
            final_user_profile = {**base_data}

            # Only include segments that were explicitly requested
            if filtered_segments:
                for seg in filtered_segments:
                    if seg in SEGMENT_NAME_MAP:
                        segment_name = SEGMENT_NAME_MAP[seg]
                        final_user_profile[segment_name] = extract_generic_segment(stdout, segment_name)

        else:  # profile_type == 'group'
            base_data = parse_base_group_info(stdout)
            final_user_profile = {**base_data}

            # Only include segments that were explicitly requested
            if filtered_segments:
                for seg in filtered_segments:
                    if seg in VALID_GROUP_SEGMENTS:
                        segment_name = SEGMENT_NAME_MAP[seg]
                        final_user_profile[segment_name] = extract_generic_segment(stdout, segment_name)

        result['segments'] = final_user_profile

        module.exit_json(**result)

    except (KeyError, IndexError, AttributeError) as parse_err:
        result['msg'] = f"Failed to parse RACF output: {str(parse_err)}"
        module.fail_json(**result)
    except Exception as err:
        result['msg'] = f"Unexpected error during parsing: {str(err)}"
        module.fail_json(**result)


if __name__ == '__main__':
    run_module()
