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
  - The L(zos_user_info,./zos_user_info.html) module retrieves detailed information
    about RACF user and group profiles.
  - The module executes RACF LISTUSER or LISTGRP TSO commands and parses the output
    into structured data.
  - This is an info module that does not make any changes to the system.
options:
  name:
    description:
      - Name of the RACF profile to retrieve information about.
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
      - When I(profile_type=user), valid segments are C(dfp), C(tso), C(omvs), C(operparm), C(lang), and C(csdata).
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
"""

RETURN = r"""
cmd:
  description: The TSO command that was executed.
  returned: always
  type: str
  sample: LISTUSER TESTU01 TSO OMVS
segments:
  description:
    - Dictionary containing the RACF profile information organized by segments.
    - Always includes base profile information (C(base_segment) and C(group)/C(users) sections).
    - Additional segments are only included if explicitly requested via the I(segments) parameter.
    - Each segment is a dictionary with key-value pairs extracted from RACF output.
    - The keys and values within each segment are dynamic and depend on what RACF returns.
    - Empty segments (where RACF returns "NO [SEGMENT] INFORMATION") will be empty dictionaries.
  returned: success
  type: dict
  contains:
    base_segment:
      description:
        - Base profile information that is always returned regardless of the I(segments) parameter.
        - When I(profile_type=user), contains user attributes such as C(USER-ID), C(NAME), C(DEFAULT-GROUP), C(OWNER), C(CREATED), C(PASSDATE), C(PASS-INTERVAL), C(ATTRIBUTES), etc.
        - When I(profile_type=group), contains group attributes such as C(OWNER), C(CREATED), C(SUPERIOR GROUP), C(INSTALLATION DATA), C(SUBGROUP(S)), C(TERMUACC), C(UNIVERSAL), etc.
        - The exact keys present are dynamic and depend on the profile's RACF configuration.
        - Some fields like C(ATTRIBUTES) and C(CLASS AUTHORIZATIONS) are returned as lists when they contain multiple values.
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
      description:
        - Group connection information for user profiles.
        - Dictionary where each key is a group name and the value contains connection attributes.
        - Contains attributes such as C(AUTH), C(CONNECT-OWNER), C(CONNECT-DATE), C(LAST-CONNECT), C(REVOKE DATE), C(RESUME DATE), C(CONNECT ATTRIBUTES), etc.
        - Only returned when I(profile_type=user).
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
      description:
        - Connected user information for group profiles.
        - Dictionary where each key is a username and the value contains connection attributes.
        - Contains attributes such as C(ACCESS), C(ACCESS COUNT), C(UNIVERSAL ACCESS), C(REVOKE DATE), C(RESUME DATE), C(CONNECT ATTRIBUTES), etc.
        - Only returned when I(profile_type=group).
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
      description:
        - TSO segment information for user profiles.
        - Contains dynamic key-value pairs such as C(ACCTNUM), C(PROC), C(SIZE), C(MAXSIZE), C(JOBCLASS), C(MSGCLASS), C(SYSOUTCLASS), C(USERDATA), C(COMMAND), etc.
        - The exact keys present depend on the user's TSO configuration in RACF.
        - Only returned when I(profile_type=user) and C(tso) is included in the I(segments) parameter.
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
      description:
        - OMVS segment information for user and group profiles.
        - Contains dynamic key-value pairs such as C(UID), C(HOME), C(PROGRAM), C(CPUTIMEMAX), C(ASSIZEMAX), C(FILEPROCMAX), C(PROCUSERMAX), etc.
        - The exact keys present depend on the OMVS configuration in RACF.
        - Only returned when C(omvs) is included in the I(segments) parameter.
      returned: when omvs segment is requested
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
      returned: when dfp segment is requested
      type: dict
      sample:
        MGMTCLAS: "STANDARD"
        STORCLAS: "SCPERM"
        DATACLAS: "DCEXTL"
    OPERPARM:
      description:
        - OPERPARM segment information for user profiles.
        - Contains operator parameters such as C(STORAGE), C(AUTH), C(ALTGRP), C(AUTO), C(HC), C(INTIDS), C(LEVEL), C(LOGCMDRESP), C(MIGID), etc.
        - Some fields like C(MONITOR), C(MSCOPE), and C(ROUTCODE) are returned as lists when they contain multiple values.
        - The exact keys present depend on the operator configuration in RACF.
        - Only returned when I(profile_type=user) and C(operparm) is included in the I(segments) parameter.
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
      description:
        - LANGUAGE segment information for user profiles.
        - Contains language-related settings such as C(PRIMARY) and C(SECONDARY) language codes.
        - The exact keys present depend on the language configuration in RACF.
        - Only returned when I(profile_type=user) and C(lang) is included in the I(segments) parameter.
      returned: when profile_type is user and lang segment is requested
      type: dict
      sample:
        PRIMARY: "ENU"
        SECONDARY: "JPN"
    CSDATA:
      description:
        - CSDATA (Custom Data) segment information for user and group profiles.
        - Contains custom application-specific data defined in RACF.
        - The exact keys present depend on what custom data has been configured for the profile.
        - Only returned when C(csdata) is included in the I(segments) parameter.
      returned: when csdata segment is requested
      type: dict
      sample: {}
changed:
  description: Indicates if any changes were made (always false for info modules).
  returned: always
  type: bool
  sample: false
rc:
  description:
    - Return code from the TSO command.
    - Returns 0 on success.
    - Returns non-zero on failure (e.g., 8 when profile not found).
  returned: always
  type: int
  sample: 0
msg:
  description:
    - Error message describing the failure reason.
    - Only present when the module fails.
  returned: failure
  type: str
  sample: "Profile 'TESTU01' not found in RACF database"
stdout:
  description:
    - Standard output from the TSO command.
  returned: always
  type: str
  sample: "NAME NOT FOUND IN RACF DATA SET"
stderr:
  description:
    - Standard error from the TSO command.
  returned: always
  type: str
  sample: ""
"""

EXAMPLES = r"""
- name: Get basic user profile info
  ibm.ibm_zos_core.zos_user_info:
    name: TESTU01
    profile_type: user

- name: Get user profile info with segments
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


# Fields that contain space-separated or comma-separated lists in RACF output
# These fields will be split into Python lists instead of keeping as strings
FIELDS_TO_SPLIT = {
    "MONITOR",      # Space-separated list of monitor attributes
    "MSCOPE",       # Space-separated list of message scopes
    "ROUTCODE",     # Comma-separated list of routing codes (e.g., "1:2,11")
    "ATTRIBUTES",   # Space-separated list of user/group attributes
    "CLASS AUTHORIZATIONS",  # Space-separated list of authorized classes
    "MFORM"      # Space-separated list of message forms
}

# Regex patterns for parsing RACF output
RACF_HEADER_PATTERN = r'^(NO )?([A-Z]+) INFORMATION'
RACF_KV_PATTERN = r'^\s*([A-Z0-9\s]+?)\s*[=:]\s*(.*)'

# Prefixes to skip when parsing RACF output
SKIP_PREFIXES = ('---', 'LISTUSER ', 'LISTGRP ')


def extract_generic_segment(output_text: str, target_segment_name: str) -> Dict[str, Any]:
    """
    Parse a specific segment from RACF LISTUSER/LISTGRP command output.

    This function extracts and parses a named segment (e.g., TSO, OMVS, DFP)
    from RACF command output. It handles both 'KEY=VALUE' and 'KEY: VALUE'
    formats and automatically splits certain fields into lists.

    Args:
        output_text (str): Raw output from RACF LISTUSER or LISTGRP command
        target_segment_name (str): Name of segment to extract (e.g., 'TSO', 'OMVS', 'DFP')

    Returns:
        Dict[str, Any]: Dictionary containing parsed segment data as key-value pairs.
                       Returns empty dict if segment not found or has no data.
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


def parse_base_user_info(output_text: str) -> Dict[str, Any]:
    """
    Parse base user information from RACF LISTUSER output.

    Extracts general user attributes and group connection details from the base
    section of LISTUSER output (before any segment headers like "TSO INFORMATION").

    Args:
        output_text: Raw RACF LISTUSER command output text

    Returns:
        Dictionary with structure:
        {
            "general": {key: value, ...},  # User-level attributes
            "group": {
                "GROUP_NAME": {key: value, ...},  # Per-group connection attributes
                ...
            }
        }
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
    Parse base group information from RACF LISTGROUP output.

    Extracts general group attributes and connected user details from the base
    section of LISTGROUP output (before any segment headers).

    Args:
        output_text: Raw RACF LISTGROUP command output text

    Returns:
        Dictionary with structure:
        {
            "general": {key: value, ...},  # Group-level attributes
            "users": {
                "USERNAME": {key: value, ...},  # Per-user connection attributes
                ...
            }
        }
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


def parse_tso(output_text: str) -> Dict[str, Any]:
    """Parse TSO segment from RACF output."""
    return extract_generic_segment(output_text, "TSO")


def parse_omvs(output_text: str) -> Dict[str, Any]:
    """Parse OMVS segment from RACF output."""
    return extract_generic_segment(output_text, "OMVS")


def parse_dfp(output_text: str) -> Dict[str, Any]:
    """Parse DFP segment from RACF output."""
    return extract_generic_segment(output_text, "DFP")


def parse_operparm(output_text: str) -> Dict[str, Any]:
    """Parse OPERPARM segment from RACF output."""
    return extract_generic_segment(output_text, "OPERPARM")


def parse_language(output_text: str) -> Dict[str, Any]:
    """Parse LANGUAGE segment from RACF output."""
    return extract_generic_segment(output_text, "LANGUAGE")


def parse_csdata(output_text: str) -> Dict[str, Any]:
    """Parse CSDATA segment from RACF output."""
    return extract_generic_segment(output_text, "CSDATA")


def run_module():
    """Main module execution function."""

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
            'choices': ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata']
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
        # Valid segments for user: dfp, tso, omvs, operparm, lang, csdata
        valid_user_segments = ['dfp', 'tso', 'omvs', 'operparm', 'lang', 'csdata']

        # Filter segments to only valid ones for user
        filtered_segments = [s for s in segments if s in valid_user_segments]

        # Build command - start with LISTUSER and user name
        cmd = f'LISTUSER {name}'

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

        # Build command - start with LISTGRP and group name
        cmd = f'LISTGRP {name}'

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
    if rc != 0 or 'NAME NOT FOUND IN RACF DATA SET' in stdout.upper() or f'INVALID {profile_type.upper()} NAME' in stdout.upper():
        result['rc'] = rc
        result['stdout'] = stdout
        # Only include stderr if it contains something other than the command echo
        result['stderr'] = '' if stderr.strip() == cmd else stderr
        result['msg'] = f"Profile '{name}' not found in RACF database"
        module.fail_json(**result)

    # Parse segments based on profile_type
    try:
        if profile_type == 'user':
            base_data = parse_base_user_info(stdout)
            final_user_profile = {**base_data}

            # Only include segments that were explicitly requested
            if filtered_segments:
                segment_parser_map = {
                    'tso': ('TSO', parse_tso),
                    'omvs': ('OMVS', parse_omvs),
                    'dfp': ('DFP', parse_dfp),
                    'operparm': ('OPERPARM', parse_operparm),
                    'lang': ('LANGUAGE', parse_language),
                    'csdata': ('CSDATA', parse_csdata)
                }

                for seg in filtered_segments:
                    if seg in segment_parser_map:
                        key, parser_func = segment_parser_map[seg]
                        final_user_profile[key] = parser_func(stdout)

        else:  # profile_type == 'group'
            base_data = parse_base_group_info(stdout)
            final_user_profile = {**base_data}

            # Only include segments that were explicitly requested
            if filtered_segments:
                segment_parser_map = {
                    'omvs': ('OMVS', parse_omvs),
                    'dfp': ('DFP', parse_dfp),
                    'csdata': ('CSDATA', parse_csdata)
                }

                for seg in filtered_segments:
                    if seg in segment_parser_map:
                        key, parser_func = segment_parser_map[seg]
                        final_user_profile[key] = parser_func(stdout)

        result['rc'] = rc
        result['segments'] = final_user_profile
        result['stdout'] = stdout
        result['stderr'] = stderr

        module.exit_json(**result)

    except (KeyError, IndexError, AttributeError) as parse_err:
        result['rc'] = rc
        result['stdout'] = stdout
        # Only include stderr if it contains something other than the command echo
        result['stderr'] = '' if stderr.strip() == cmd else stderr
        result['msg'] = f"Failed to parse RACF output: {str(parse_err)}"
        module.fail_json(**result)
    except Exception as err:
        result['rc'] = rc
        result['stdout'] = stdout
        # Only include stderr if it contains something other than the command echo
        result['stderr'] = '' if stderr.strip() == cmd else stderr
        result['msg'] = f"Unexpected error during parsing: {str(err)}"
        module.fail_json(**result)


if __name__ == '__main__':
    run_module()
