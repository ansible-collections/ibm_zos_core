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
  - The module executes RACF LISTUSER or LISTGRP TSO commands and parses the output into structured data.
  - This is an info module that does not make any changes to the system.
options:
  name:
    description:
      - The name of the RACF profile to retrieve information about.
      - Can be a user ID or group name depending on the I(profile_type) parameter.
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
      - When I(profile_type=group), valid segments are C(dfp), C(omvs), and C(csdata).
      - The C(base_segment) section is always retrieved regardless of this parameter.
      - Invalid segments for the specified I(profile_type) will be silently ignored.
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
  description: Indicates whether any changes were made to the system (always false for info modules).
  returned: always
  type: bool
  sample: false
cmd:
  description: The RACF command that was executed with tsocmd.
  returned: always
  type: str
  sample: "LISTUSER TESTU01 TSO OMVS"
rc:
  description: >
    Return code from the RACF command execution.
    Returns 0 on success.
    Returns non-zero on failure (e.g., 8 when profile not found).
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
    Standard error from the RACF command execution.
    TSO command output is automatically filtered out.
  returned: always
  type: str
  sample: ""
msg:
  description: >
    Error message describing the failure reason.
    Only present when the module fails.
  returned: failure
  type: str
  sample: "Profile 'TESTU01' not found in RACF database"
segments:
  description: >
    Dictionary containing the RACF profile information organized by segments.
    Always includes base profile information (C(base_segment) and C(group)/C(users) sections).
    Additional segments are only included if explicitly requested via the I(segments) parameter.
    Each segment is a dictionary with key-value pairs extracted from RACF output.
    The keys and values within each segment are dynamic and depend on what RACF returns.
    Empty segments (where RACF returns "NO [SEGMENT] INFORMATION") will be empty dictionaries.
  returned: success
  type: dict
  contains:
    base_segment:
      description: >
        Base profile information that is always returned regardless of the I(segments) parameter.
        When I(profile_type=user), contains user attributes such as C(USER-ID), C(NAME), C(DEFAULT-GROUP), C(OWNER), C(CREATED),
        C(PASSDATE), C(PASS-INTERVAL), C(ATTRIBUTES), etc.
        When I(profile_type=group), contains group attributes such as C(OWNER), C(CREATED), C(SUPERIOR GROUP), C(INSTALLATION DATA),
        C(SUBGROUP(S)), C(TERMUACC), C(UNIVERSAL), etc.
        The exact keys present are dynamic and depend on the profile's RACF configuration.
        Some fields like C(ATTRIBUTES) and C(CLASS AUTHORIZATIONS) are returned as lists when they contain multiple values.
      returned: always
      type: dict
      sample:
        USER-ID: "TESTU01"
        NAME: "TEST USER 01"
        DEFAULT-GROUP: "TSTGRP01"
        PASSDATE: "2026/04/15"
        PASS-INTERVAL: "90"
        ATTRIBUTES: ["SPECIAL", "OPERATIONS"]
        OWNER: "ADMIN01"
        CREATED: "2025/01/10"
    group:
      description: >
        Group connection information for user profiles.
        Dictionary where each key is a group name and the value contains connection attributes.
        Contains attributes such as C(AUTH), C(CONNECT-OWNER), C(CONNECT-DATE), C(LAST-CONNECT), C(REVOKE DATE), C(RESUME DATE), C(CONNECT ATTRIBUTES), etc.
        Only returned when I(profile_type=user).
      returned: when profile_type is user
      type: dict
      sample:
        TSTGRP01:
          AUTH: "USE"
          CONNECT-OWNER: "ADMIN01"
          CONNECT-DATE: "2025/01/10"
          LAST-CONNECT: "2026/04/29"
          REVOKE DATE: "NONE"
          RESUME DATE: "NONE"
        SYSADM:
          AUTH: "JOIN"
          CONNECT-OWNER: "ADMIN01"
          CONNECT-DATE: "2025/02/15"
    users:
      description: >
        Connected user information for group profiles.
        Dictionary where each key is a username and the value contains connection attributes.
        Contains attributes such as C(ACCESS), C(ACCESS COUNT), C(UNIVERSAL ACCESS), C(REVOKE DATE), C(RESUME DATE), C(CONNECT ATTRIBUTES), etc.
        Only returned when I(profile_type=group).
      returned: when profile_type is group
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
      description: >
        TSO segment information for user profiles.
        Contains dynamic key-value pairs such as C(ACCTNUM), C(PROC), C(SIZE), C(MAXSIZE), C(JOBCLASS), C(MSGCLASS), C(SYSOUTCLASS),
        C(USERDATA), C(COMMAND), etc.
        The exact keys present depend on the user's TSO configuration in RACF.
        Only returned when I(profile_type=user) and C(tso) is included in the I(segments) parameter.
      returned: when profile_type is user and tso segment is requested
      type: dict
      sample:
        ACCTNUM: "33000"
        HOLDCLASS: "H"
        JOBCLASS: "A"
        MSGCLASS: "X"
        PROC: "IKJACCNT"
        SIZE: "00016384"
        MAXSIZE: "00032768"
        SYSOUTCLASS: "A"
        USERDATA: "E4F1"
        COMMAND: "ISPF PANEL(ISR@390)"
    OMVS:
      description: >
        OMVS segment information for user and group profiles.
        Contains dynamic key-value pairs such as C(UID), C(HOME), C(PROGRAM), C(CPUTIMEMAX), C(ASSIZEMAX), C(FILEPROCMAX), C(PROCUSERMAX), etc.
        The exact keys present depend on the OMVS configuration in RACF.
        Only returned when C(omvs) is included in the I(segments) parameter.
      returned: when omvs segment is requested
      type: dict
      sample:
        UID: "0000000201"
        HOME: "/u/testu01"
        PROGRAM: "/bin/sh"
        CPUTIMEMAX: "NONE"
        ASSIZEMAX: "NONE"
    DFP:
      description: >
        DFP (Data Facility Product) segment information for user and group profiles.
        Contains dynamic key-value pairs related to data management such as C(MGMTCLAS), C(STORCLAS), C(DATACLAS), etc.
        The exact keys present depend on the DFP configuration in RACF.
        Only returned when C(dfp) is included in the I(segments) parameter.
      returned: when dfp segment is requested
      type: dict
      sample:
        MGMTCLAS: "STANDARD"
        STORCLAS: "SCPERM"
        DATACLAS: "DCEXTL"
    OPERPARM:
      description: >
        OPERPARM segment information for user profiles.
        Contains operator parameters such as C(STORAGE), C(AUTH), C(ALTGRP), C(AUTO), C(HC), C(INTIDS), C(LEVEL), C(LOGCMDRESP), C(MIGID), etc.
        Some fields like C(MONITOR), C(MSCOPE), and C(ROUTCODE) are returned as lists when they contain multiple values.
        The exact keys present depend on the operator configuration in RACF.
        Only returned when I(profile_type=user) and C(operparm) is included in the I(segments) parameter.
      returned: when profile_type is user and operparm segment is requested
      type: dict
      sample:
        STORAGE: "YES"
        ALTGRP: "YES"
        AUTO: "NO"
        HC: "NO"
        INTIDS: "NO"
        LEVEL: "00"
        LOGCMDRESP: "NO"
        MIGID: "NO"
        MONITOR:
          - "JOBNAMES"
          - "SESS"
          - "STATUS"
        MSCOPE:
          - "ALL"
        ROUTCODE:
          - "1:2"
          - "11"
    LANGUAGE:
      description: >
        LANGUAGE segment information for user profiles.
        Contains language-related settings such as C(PRIMARY) and C(SECONDARY) language codes.
        The exact keys present depend on the language configuration in RACF.
        Only returned when I(profile_type=user) and C(lang) is included in the I(segments) parameter.
      returned: when profile_type is user and lang segment is requested
      type: dict
      sample:
        PRIMARY: "ENU"
        SECONDARY: "JPN"
    CSDATA:
      description: >
        CSDATA (Custom Data) segment information for user and group profiles.
        Contains custom application-specific data defined in RACF.
        The exact keys present depend on what custom data has been configured for the profile.
        Only returned when C(csdata) is included in the I(segments) parameter.
      returned: when csdata segment is requested
      type: dict
      sample: {}
    CICS:
      description: >
        CICS segment information for user profiles.
        Contains CICS-related configuration and resource limits.
        Only returned when I(profile_type=user) and C(cics) is included in the I(segments) parameter.
      returned: when profile_type is user and cics segment is requested
      type: dict
    DCE:
      description: >
        DCE (Distributed Computing Environment) segment information for user profiles.
        Contains DCE-related configuration and identifiers.
        Only returned when I(profile_type=user) and C(dce) is included in the I(segments) parameter.
      returned: when profile_type is user and dce segment is requested
      type: dict
    EIM:
      description: >
        EIM (Enterprise Identity Mapping) segment information for user profiles.
        Contains EIM-related configuration and mappings.
        Only returned when I(profile_type=user) and C(eim) is included in the I(segments) parameter.
      returned: when profile_type is user and eim segment is requested
      type: dict
    OVM:
      description: >
        OVM (OpenExtensions VM) segment information for user profiles.
        Contains OVM-related configuration and settings.
        Only returned when I(profile_type=user) and C(ovm) is included in the I(segments) parameter.
      returned: when profile_type is user and ovm segment is requested
      type: dict
    NETVIEW:
      description: >
        NETVIEW segment information for user profiles.
        Contains NetView-related configuration and authorities.
        Only returned when I(profile_type=user) and C(netview) is included in the I(segments) parameter.
      returned: when profile_type is user and netview segment is requested
      type: dict
    NDS:
      description: >
        NDS (Network Directory Services) segment information for user profiles.
        Contains NDS-related configuration and identifiers.
        Only returned when I(profile_type=user) and C(nds) is included in the I(segments) parameter.
      returned: when profile_type is user and nds segment is requested
      type: dict
    LNOTES:
      description: >
        LNOTES (Lotus Notes) segment information for user profiles.
        Contains Lotus Notes-related configuration and settings.
        Only returned when I(profile_type=user) and C(lnotes) is included in the I(segments) parameter.
      returned: when profile_type is user and lnotes segment is requested
      type: dict
    WORKATTR:
      description: >
        WORKATTR (Work Attributes) segment information for user profiles.
        Contains work-related attributes and organizational information.
        Only returned when I(profile_type=user) and C(workattr) is included in the I(segments) parameter.
      returned: when profile_type is user and workattr segment is requested
      type: dict
    PROXY:
      description: >
        PROXY segment information for user profiles.
        Contains proxy-related configuration and authorities.
        Only returned when I(profile_type=user) and C(proxy) is included in the I(segments) parameter.
      returned: when profile_type is user and proxy segment is requested
      type: dict
    KERB:
      description: >
        KERB (Kerberos) segment information for user profiles.
        Contains Kerberos-related configuration, principals, and encryption settings.
        Only returned when I(profile_type=user) and C(kerb) is included in the I(segments) parameter.
      returned: when profile_type is user and kerb segment is requested
      type: dict
"""

EXAMPLES = r"""
- name: Get basic user profile info
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    profile_type: user

- name: Get user profile info for multiple segments
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

- name: Get basic group profile info
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    profile_type: group

- name: Get group profile info with DFP and OMVS segments
  ibm.ibm_zos_core.zos_user_info:
    name: TSTGRP01
    profile_type: group
    segments:
      - dfp
      - omvs
"""


import re
from typing import Dict, Any
from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
        better_arg_parser
    )
except ImportError:
    better_arg_parser = None


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

# Prefixes to skip when parsing RACF output
SKIP_PREFIXES = ('---', 'LISTUSER ', 'LISTGRP ')


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

    # Compile regex patterns using module constants
    header_pattern = re.compile(RACF_HEADER_PATTERN)
    kv_pattern = re.compile(RACF_KV_PATTERN)

    lines = output_text.strip().split('\n')

    for line in lines:
        line = line.strip()

        if not line or line.startswith(SKIP_PREFIXES):
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

    racf_keys = r'(?:REVOKE DATE|RESUME DATE|CLASS AUTHORIZATIONS|CONNECT ATTRIBUTES|[A-Z0-9-]+)'
    kv_pattern = re.compile(rf'\b({racf_keys})=(.*?)(?=\s+{racf_keys}=|$)')
    KEYS_TO_SPLIT = {"ATTRIBUTES", "CLASS AUTHORIZATIONS"}

    lines = output_text.strip().split('\n')

    parsing_logon = False
    ignoring_category = False
    last_key = None
    current_group = None

    for line in lines:
        original_line = line
        line = line.strip()

        if not line or line.startswith('---') or line.startswith('LISTUSER '):
            continue

        # ==========================================
        # If we hit an optional segment header, the base section is over. Stop looping.
        # ==========================================
        if re.match(r'^(NO )?([A-Z]+) INFORMATION', line):
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

        matches = kv_pattern.findall(line)

        if matches:
            for key, value in matches:
                key = key.strip()
                value = value.strip()

                if key == "GROUP":
                    current_group = value
                    base_data["group"][current_group] = {}
                    last_key = key
                    continue

                # --- NEW: Route to specific group, OR the base_segment dictionary ---
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

    # Whitelist of RACF group keys
    group_keys = r'(?:SUPERIOR GROUP|INSTALLATION DATA|MODEL DATA SET|SUBGROUP\(S\)|CONNECT ATTRIBUTES|REVOKE DATE|RESUME DATE|[A-Z0-9-]+)'
    kv_pattern = re.compile(rf'\b({group_keys})=(.*?)(?=\s+{group_keys}=|$)')

    lines = output_text.strip().split('\n')

    parsing_users = False
    current_user = None
    last_key = None

    for line in lines:
        original_line = line
        line = line.strip()

        # Skip headers and empty lines
        if not line or line.startswith('---') or line.startswith('LISTGRP ') or line.startswith('INFORMATION FOR GROUP'):
            continue

        # ==========================================
        # 1. THE STOP CONDITION
        # ==========================================
        if re.match(r'^(NO )?([A-Z]+) INFORMATION', line):
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
                matches = kv_pattern.findall(line)
                for key, value in matches:
                    key = key.strip()
                    value = value.strip()
                    if current_user:
                        base_data['users'][current_user][key] = value
            continue  # We handled the user row, skip the general processing below

        # ==========================================
        # 4. GENERAL KEY EXTRACTION & CONTINUATION
        # ==========================================
        matches = kv_pattern.findall(line)

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

    if better_arg_parser:
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

    name = module.params['name']
    profile_type = module.params['profile_type'].lower()
    segments = [s.lower() for s in (module.params.get('segments') or [])]

    # Build the appropriate TSO command based on profile_type and segments
    if profile_type == 'user':
        # Valid segments for user
        valid_user_segments = ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata',
                               'cics', 'dce', 'eim', 'ovm', 'netview', 'nds',
                               'lnotes', 'workattr', 'proxy', 'kerb']

        # Filter segments to only valid ones for user
        filtered_segments = [s for s in segments if s in valid_user_segments]

        # Build command - start with LISTUSER and user name
        cmd = f'LISTUSER {name}'

        # Add segments if specified
        if filtered_segments:
            segment_keywords = [SEGMENT_NAME_MAP[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"
    else:
        # Valid segments for group: dfp, omvs, csdata
        valid_group_segments = ['dfp', 'omvs', 'csdata']

        # Filter segments to only valid ones for group
        filtered_segments = [s for s in segments if s in valid_group_segments]

        # Build command - start with LISTGRP and group name
        cmd = f'LISTGRP {name}'

        # Add segments if specified
        if filtered_segments:
            segment_keywords = [SEGMENT_NAME_MAP[s] for s in filtered_segments]
            cmd = f"{cmd} {' '.join(segment_keywords)}"

    result['cmd'] = cmd

    # Execute the TSO command
    rc, stdout, stderr = module.run_command(f'tsocmd "{cmd}"')

    # Set command output in result dict immediately after execution
    result['rc'] = rc
    result['stdout'] = stdout
    # Only include stderr if it contains something other than the command echo
    result['stderr'] = '' if stderr.strip() == cmd else stderr

    # Check if the profile was not found
    if rc != 0 or 'NAME NOT FOUND IN RACF DATA SET' in stdout.upper() or f'INVALID {profile_type.upper()} NAME' in stdout.upper():
        result['msg'] = f"Profile '{name}' not found in RACF database"
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
            # Valid segments for group profiles
            valid_group_segments = {'dfp', 'omvs', 'csdata'}
            if filtered_segments:
                for seg in filtered_segments:
                    if seg in valid_group_segments and seg in SEGMENT_NAME_MAP:
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
