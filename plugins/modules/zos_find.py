#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)
from typing import Pattern

from ansible.module_utils.basic import AnsibleModule
from plugins.modules.zos_copy import run_module
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r"""
---
module: zos_find
version_added: '2.9'
short_description: Find matching data sets
description:
  - Return a list of data sets based on specific criteria. 
  - Multiple criteria are AND’d together.
  - Use the M(find) module to find USS files.
author: "Asif Mahmud (@asifmahmud)"
options:
  age:
    description:
      - Select data sets whose age is equal to or greater than the specified time.
      - Use a negative age to find data sets equal to or less than the specified time.
      - You can choose days, weeks, months or years by specifying the first letter of 
        any of those words (e.g., "1w"). If no letter is specified, it is assumed to be days.
      - Age is determined by using the 'referenced date' of the data set.
    type: str
    required: false
  contains:
    description:
      - A word which should be matched against the data set content or data 
        set member content.
    type: str
    required: false
  excludes:
    description:
      - Data sets whose names match an excludes pattern are culled from patterns matches. 
        Multiple patterns can be specified using a list.
      - The pattern can be a regular expression.
      - If the pattern is a regular expression, it must match the full data set name.
    type: list
    required: false
    aliases: ['exclude']
  patterns:
    description:
      - One or more data set patterns.
      - The patterns restrict the list of data sets to be returned to those whose 
        names match at least one of the patterns specified. Multiple patterns 
        can be specified using a list.
      - This parameter expects a list, which can be either comma separated or YAML.
      - When searching for members within a PDS/PDSE, pattern can be a regular expression.
    type: list
    required: true
  size:
    description:
      - Select data sets whose size is equal to or greater than the specified size.
      - Use a negative size to find files equal to or less than the specified size.
      - Unqualified values are in bytes but b, k, m, g, and t can be appended to 
        specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
    type: str
    required: false
  pds_paths:
    description:
      - List of PDS/PDSE to search. Wild-card possible.
      - Required only when searching for data set members, otherwise ignored.
      - if C(pds_paths) is provided, C(patterns) must be member patterns.
      - Only valid for NONVSAM data set types. Otherwise ignored.
    type: list
    required: false
  ds_type;
    description:
      - The type of resource to search. The two choices are 'NONVSAM' and 'VSAM'.
      - 'NONVSAM' refers to one of SEQ, LIBRARY (PDSE), PDS, LARGE, BASIC, EXTREQ, EXTPREF.
    choices:
      - NONVSAM
      - VSAM
    type: str
    required: false
    default: NONVSAM
  volume:
    description:
      - If provided, only the data sets allocated in the specified list of 
        volumes will be searched.
    type: list
    required: false
    aliases: ['volumes']
notes:
  - Only cataloged data sets will be searched. If an uncataloged data set needs to
    be searched, it should be cataloged first.
  - The M(zos_find) module currently does not support wildcards for high level qualifiers.
    For example, C(SOME.*.DATA.SET) is a valid pattern, but C(*.DATA.SET) is not.
  - If a data set pattern is specified as C(USER.*), the matching data sets will have two
    name segments such as C(USER.ABC), C(USER.XYZ) etc. If a wildcard is specified 
    as C(USER.*.ABC), the matching data sets will have three name segments such as
    C(USER.XYZ.ABC), C(USER.TEST.ABC) etc.
seealso:
- module: find
- module: zos_data_set
"""


EXAMPLES = r"""
- name: Find all data sets with HLQ 'IMS.LIB' or 'IMSTEST.LIB' that contain the word 'hello'
  zos_find:
    patterns:
      - IMS.LIB.*
      - IMSTEST.LIB.*
    contains: 'hello'
    age: 2d

- name: Search for 'rexx' in all datasets matching IBM.TSO.*.C??
  zos_find:
    patterns:
      - IBM.TSO.*.C??
    contains: 'rexx'

- name: Exclude data sets that have a low level qualifier 'TEST'
  zos_find:
    patterns: 'IMS.LIB.*'
    contains: 'hello'
    excludes: '*.TEST'

- name: Find all members starting with characters 'TE' in a list of PDS
  zos_find:
    patterns: 'TE*'
    pds_paths:
      - IMSTEST.TEST.*
      - IMSTEST.USER.*
      - USER.*.LIB

- name: Find all data sets greater than 2MB and allocated in one of the specified volumes
  zos_find:
    patterns: 'USER.*'
    size: 2m
    volumes:
      - SCR03
      - IMSSUN

- name: Find all VSAM clusters starting with the word 'USER'
  zos_find:
    patterns:
      - USER.*
    ds_type: VSAM
"""


RETURN = r"""
data_sets:
    description: All matches found with the specified criteria.
    returned: success
    type: list
    sample: [
      { name: "SOME.DATA.SET",
        members: [
            "MEMBER1",
            "MEMBER2"
        ]
      },
      { name: "SAMPLE.DATA.SET,
        "...": "...",
      },
    ]
matched:
    description: The number of matched data sets found
    returned: success
    type: int
    sample: 49
examined:
    description: Number of data sets looked at
    returned: success
    type: int
    sample: 158
"""

import re
import time
import datetime

from ansible.module_utils.six import PY3

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, vtoc
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport
)

if PY3:
    from shlex import quote
else:
    from pipes import quote

try:
    from zoautil_py import Datasets
except Exception:
    Datasets = MissingZOAUImport()
    MVSCmd = MissingZOAUImport()
    types = MissingZOAUImport()


def data_set_filter(module, patterns, content, excludes):
    filtered_data_sets = dict(ps=set(), pds=dict(), searched=0)
    for pattern in patterns:
        rc, out, err = _dgrep_wrapper(pattern, content=content, verbose=True, ignore_case=True)
        if rc > 4:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'dgrep'",
                rc=rc, stdout=out, stderr=err
            )
        for line in out.split("\n"):
            if line.startswith("BGYSC1005I"):
                filtered_data_sets['searched'] += 1
            else:
                result = line.split()
                if len(result) > 2:
                    try:
                        filtered_data_sets['pds'][result[0]].append(result[1])
                    except KeyError:
                        filtered_data_sets['pds'][result[0]] = [result[1]]
                else:
                    filtered_data_sets['ps'].add(result[0])

    for ds in filtered_data_sets['ps'].union(set(filtered_data_sets['pds'].keys())):
        for ex_pat in excludes:
            if re.fullmatch(ex_pat, ds, re.IGNORECASE):
                if ds in filtered_data_sets['ps']:
                    filtered_data_sets['ps'].remove(ds)
                else:
                    filtered_data_sets['pds'].pop(ds)
    return filtered_data_sets


#TODO: pds_filter() currently has O(n^3) time complexity. 
# Seems to be unavoidable due to the fact that each PDS could have multiple
# matched members and each member needs to be compared against multiple member patterns.
# Try to reduce the complexity to O(n^2) or less if possible.
def pds_filter(pds_list, member_patterns):
    filtered_pds = dict()
    for pds, member in pds_list.items():
        for m in member:
            for mem_pat in member_patterns:
                if re.fullmatch(mem_pat, m, re.IGNORECASE):
                    try:
                        filtered_pds[pds].append(m)
                    except KeyError:
                        filtered_pds[pds] = [m]
    return filtered_pds


def vsam_filter(module, patterns, excludes):
    filtered_data_sets = set()
    for pattern in patterns:
        rc, out, err = _vls_wrapper(pattern, details=True)
        if rc != 0:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'vls'",
                rc=rc, stdout=out, stderr=err
            )
        for line in out.split("\n"):
            filtered_data_sets.add(line.split()[0].strip())

    for ds in set(filtered_data_sets):
        for ex_pat in excludes:
            if re.fullmatch(ex_pat, ds, re.IGNORECASE):
                filtered_data_sets.remove(ds)
    return filtered_data_sets


def data_set_attribute_filter(module, data_sets, size=None, age=None):
    filtered_data_sets = set()
    now = time.time()
    for ds in data_sets:
        rc, out, err = _dls_wrapper(ds, u_time=age is not None, size=size is not None)
        if rc != 0:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'dls'",
                rc=rc, stdout=out, stderr=err
            )
        for line in out.split("\n"):
            result = line.split()
            if age and size and _age_filter(result[1], now, age) and int(result[6]) >= size:
                filtered_data_sets.add(ds)
            elif age and not size and _age_filter(result[1], now, age):
                filtered_data_sets.add(ds)
            elif size and not age and int(result[5]) >= size:
                filtered_data_sets.add(ds)
    return filtered_data_sets


#TODO: 
# Implement volume_filter() using "vtocls" shell command from ZOAU 
# when it becomes available.
def volume_filter(data_sets, volumes):
    """Return only the data sets that are allocated in one of the volumes from
    the list of input volumes.

    Arguments:
        data_sets {set[str]} -- A set of data sets to be filtered
        volumes {list[str]} -- A list of input volumes

    Returns:
        {set} -- The filtered data sets
    """
    filtered_data_sets = set()
    for volume in volumes:
        for ds in vtoc.get_volume_entry(volume):
            if ds.get('data_set_name') in data_sets:
                filtered_data_sets.add(ds)
    return filtered_data_sets


def _age_filter(ds_date, now, age):
    year, month, day = ds_date.split("/")
    if year == "0000":
        return age >= 0

    # Seconds per day = 86400
    ds_age = (datetime.datetime(year, month, day).timestamp())/86400
    if age >= 0 and now - ds_age >= abs(age):
        return True
    elif age < 0 and now - ds_age <= abs(age):
        return True
    return False


def _dgrep_wrapper(
    data_set_pattern, 
    content=None, 
    ignore_case=False, 
    line_num=False, 
    verbose=False, 
    context=None
):
    """A wrapper for ZOAU 'dgrep' shell command"""
    dgrep_cmd = "dgrep"
    if ignore_case:
        dgrep_cmd += " -i"
    if line_num:
        dgrep_cmd += " -n"
    if verbose:
        dgrep_cmd += " -v"
    if context:
        dgrep_cmd += " -C{0}".format(context)
    if content:
        dgrep_cmd += " {0}".format(quote(content))

    dgrep_cmd += " {0}".format(quote(data_set_pattern))
    return AnsibleModuleHelper(argument_spec={}).run_command(dgrep_cmd)


def _dls_wrapper(
    data_set_pattern, 
    list_details=False, 
    u_time=False, 
    size=False, 
    verbose=False, 
    migrated=False
):
    """A wrapper for ZOAU 'dls' shell command"""
    dls_cmd = "dls"
    if migrated:
        dls_cmd += " -m"
    else:
        if list_details:
            dls_cmd += " -l"
        if u_time:
            dls_cmd += " -u"
        if size:
            dls_cmd += " -s"
    if verbose:
        dls_cmd += " -v"

    dls_cmd += " {0}".format(quote(data_set_pattern))
    return AnsibleModuleHelper(argument_spec={}).run_command(dls_cmd)


def _vls_wrapper(pattern, details=False, verbose=False):
    """A wrapper for ZOAU 'vls' shell command"""
    vls_cmd = "vls"
    if details:
        vls_cmd += " -l"
    if verbose:
        vls_cmd += " -v"

    vls_cmd += " {0}".format(quote(pattern))
    return AnsibleModuleHelper(argument_spec={}).run_command(vls_cmd)


def run_module(module, arg_def):
    parsed_args = None
    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(
            msg="Parameter verification failed", stderr=str(err)
        )

    res_args = dict(data_sets=[])
    filtered_data_sets = filtered_pds = None
    age = parsed_args.get('age')
    contains = parsed_args.get('contains')
    excludes = parsed_args.get('excludes') or parsed_args.get('exclude')
    patterns = parsed_args.get('patterns')
    size = parsed_args.get('size')
    pds_paths = parsed_args.get('pds_paths')
    ds_type = parsed_args.get('ds_type')
    volume = parsed_args.get('volume') or parsed_args.get('volumes')

    # convert age to days:
    m = re.match(r"^(-?\d+)(d|w|m|y)?$", age.lower())
    days_per_unit = {"d": 1, "w": 7, "m": 30, "y": 365}
    if m:
        age = int(m.group(1)) * days_per_unit.get(m.group(2), 1)
    else:
        module.fail_json(age=age, msg="failed to process age")

    # convert size to bytes:
    m = re.match(r"^(-?\d+)(b|k|m|g|t)?$", size.lower())
    bytes_per_unit = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}
    if m:
        size = int(m.group(1)) * bytes_per_unit.get(m.group(2), 1)
    else:
        module.fail_json(size=size, msg="failed to process size")

    if ds_type == "NONVSAM":
        init_filtered_data_sets = data_set_filter(module, patterns, contains, excludes)
        if pds_paths:
            filtered_pds = pds_filter(init_filtered_data_sets.get("pds"), patterns)
            filtered_data_sets = set(filtered_pds.keys())
        else:
            filtered_data_sets = init_filtered_data_sets.get("ps")
        if size or age:
            filtered_data_sets = data_set_attribute_filter(module, filtered_data_sets, size=size, age=age)
        if volume:
            filtered_data_sets = volume_filter(filtered_data_sets, volume)
        res_args['examined'] = init_filtered_data_sets.get("searched")
    else:
        filtered_data_sets = vsam_filter(module, patterns, excludes)
    
    for ds in filtered_data_sets:
        if pds_paths:
            res_args['data_sets'].append(dict(name=ds, members=[m for m in filtered_pds[ds]]))
        else:
            res_args['data_sets'].append(dict(name=ds))

    res_args['matched'] = len(filtered_data_sets)
    return res_args


def main():
    module = AnsibleModule(
        argument_spec=dict(
            age=dict(type='str', required=False),
            contains=dict(type='str', required=False),
            excludes=dict(type='list', required=False, aliases=['exclude']),
            patterns=dict(type='list', required=True),
            size=dict(type='str', required=False),
            pds_paths=dict(type='list', required=False),
            ds_type=dict(type='str', required=False, default='NONVSAM', choices=['VSAM', 'NONVSAM']),
            volume=dict(type='list', required=False, aliases=['volumes'])
        )
    )

    arg_def = dict(
        age=dict(arg_type='str', required=False),
        contains=dict(arg_type='str', required=False),
        excludes=dict(arg_type='list', required=False, aliases=['exclude']),
        patterns=dict(arg_type='list', required=True),
        size=dict(arg_type='str', required=False),
        pds_paths=dict(arg_type='list', required=False),
        ds_type=dict(arg_type='str', required=False, default='NONVSAM', choices=['VSAM', 'NONVSAM']),
        volume=dict(arg_type='list', required=False, aliases=['volumes'])
    )

    module.exit_json(**run_module(module, arg_def))


if __name__ == '__main__':
    main()
