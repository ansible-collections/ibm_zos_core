#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_find
version_added: "2.9"
short_description: Find matching data sets
description:
  - Return a list of data sets based on specific criteria.
  - Multiple criteria can be added (AND'd) together.
  - The C(zos_find) module can only find MVS data sets. Use the
    L(find,https://docs.ansible.com/ansible/latest/modules/find_module.html)
    module to find USS files.
author:
  - "Asif Mahmud (@asifmahmud)"
  - "Demetrios Dimatos (@ddimatos)"
options:
  age:
    description:
      - Select data sets whose age is equal to or greater than the specified time.
      - Use a negative age to find data sets equal to or less than the specified time.
      - You can choose days, weeks, months or years by specifying the first letter of
        any of those words (e.g., "1w"). The default is days.
      - Age is determined by using the 'referenced date' of the data set.
    type: str
    required: false
  age_stamp:
    description:
      - Choose the age property against which to compare age.
      - C(creation_date) is the date the data set was created and C(ref_date) is the date
        the data set was last referenced.
      - C(ref_date) is only applicable to sequential and partitioned data sets.
    choices:
      - creation_date
      - ref_date
    default: creation_date
    type: str
    required: false
  contains:
    description:
      - A string which should be matched against the data set content or data
        set member content.
    type: str
    required: false
  excludes:
    description:
      - Data sets whose names match an excludes pattern are culled from patterns matches.
        Multiple patterns can be specified using a list.
      - The pattern can be a regular expression.
      - If the pattern is a regular expression, it must match the full data set name.
    aliases:
      - exclude
    type: list
    required: false
  patterns:
    description:
      - One or more data set or member patterns.
      - The patterns restrict the list of data sets or members to be returned to those
        names that match at least one of the patterns specified. Multiple patterns
        can be specified using a list.
      - This parameter expects a list, which can be either comma separated or YAML.
      - If C(pds_patterns) is provided, C(patterns) must be member patterns.
      - When searching for members within a PDS/PDSE, pattern can be a regular expression.
    type: list
    required: true
  size:
    description:
      - Select data sets whose size is equal to or greater than the specified size.
      - Use a negative size to find files equal to or less than the specified size.
      - Unqualified values are in bytes but b, k, m, g, and t can be appended to
        specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
      - Filtering by size is currently only valid for sequential and partitioned data sets.
    required: false
    type: str
  pds_patterns:
    description:
      - List of PDS/PDSE to search. Wildcard is possible.
      - Required when searching for data set members.
      - Valid only for C(nonvsam) resource types. Otherwise ignored.
    aliases:
      - pds_paths
      - pds_pattern
    type: list
    required: false
  resource_type:
    description:
      - The type of resource to search.
      - C(nonvsam) refers to one of SEQ, LIBRARY (PDSE), PDS, LARGE, BASIC, EXTREQ, or EXTPREF.
      - C(cluster) refers to a VSAM cluster. The C(data) and C(index) are the data and index
        components of a VSAM cluster.
    choices:
      - nonvsam
      - cluster
      - data
      - index
    type: str
    required: false
    default: "nonvsam"
  volume:
    description:
      - If provided, only the data sets allocated in the specified list of
        volumes will be searched.
    type: list
    required: false
    aliases:
      - volumes
notes:
  - Only cataloged data sets will be searched. If an uncataloged data set needs to
    be searched, it should be cataloged first. The M(zos_data_set) module can be
    used to catalog uncataloged data sets.
  - The M(zos_find) module currently does not support wildcards for high level qualifiers.
    For example, C(SOME.*.DATA.SET) is a valid pattern, but C(*.DATA.SET) is not.
  - If a data set pattern is specified as C(USER.*), the matching data sets will have two
    name segments such as C(USER.ABC), C(USER.XYZ) etc. If a wildcard is specified
    as C(USER.*.ABC), the matching data sets will have three name segments such as
    C(USER.XYZ.ABC), C(USER.TEST.ABC) etc.
  - The time taken to execute the module is proportional to the number of data
    sets present on the system and how large the data sets are.
  - When searching for content within data sets, only non-binary content is considered.
seealso:
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

- name: Find all members starting with characters 'TE' in a given list of PDS patterns
  zos_find:
    patterns: '^te.*'
    pds_patterns:
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
    resource_type: cluster
"""


RETURN = r"""
data_sets:
    description: All matches found with the specified criteria.
    returned: success
    type: list
    sample: [
      {
        "name": "IMS.CICS13.USERLIB",
        "members": {
            "COBU",
            "MC2CNAM",
            "TINAD"
        },
        "type": "NONVSAM"
      },
      {
        "name": "SAMPLE.DATA.SET",
        "type": "CLUSTER"
      },
      {
        "name": "SAMPLE.VSAM.DATA",
        "type": "DATA"
      }
    ]
matched:
    description: The number of matched data sets found.
    returned: success
    type: int
    sample: 49
examined:
    description: The number of data sets searched.
    returned: success
    type: int
    sample: 158
msg:
    description: Failure message returned by the module.
    returned: failure
    type: str
    sample: Error while gathering data set information
stdout:
    description: The stdout from a USS command or MVS command, if applicable.
    returned: failure
    type: str
    sample: Searching dataset IMSTESTL.COMNUC
stderr:
    description: The stderr of a USS command or MVS command, if applicable.
    returned: failure
    type: str
    sample: No such file or directory "/tmp/foo"
rc:
    description: The return code of a USS or MVS command, if applicable.
    returned: failure
    type: int
    sample: 8
"""

import re
import time
import datetime
import math

from copy import deepcopy
from re import match as fullmatch


from ansible.module_utils.six import PY3
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    vtoc, mvs_cmd
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper
)

if PY3:
    from shlex import quote
else:
    from pipes import quote


def content_filter(module, patterns, content):
    """ Find data sets that match any pattern in a list of patterns and
    contains the given content

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used in the module
        patterns {list[str]} -- A list of data set patterns
        content {str} -- The content string to search for within matched data sets

    Returns:
        dict[ps=set, pds=dict[str, str], searched=int] -- A dictionary containing
        a set of matched "PS" data sets, a dictionary containing "PDS" data sets
        and members corresponding to each PDS, an int representing number of total
        data sets examined.
    """
    filtered_data_sets = dict(ps=set(), pds=dict(), searched=0)
    for pattern in patterns:
        rc, out, err = _dgrep_wrapper(
            pattern, content=content, verbose=True, ignore_case=True
        )
        if rc > 4 and rc != 28:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'dgrep'",
                rc=rc, stdout=out, stderr=err
            )
        for line in err.splitlines():
            if line and line.strip().startswith("BGYSC1005I"):
                filtered_data_sets['searched'] += 1

        for line in out.splitlines():
            if line:
                line = line.split()
                ds_name = line[0]
                if _ds_type(ds_name) == "PO":
                    try:
                        filtered_data_sets['pds'][ds_name].add(line[1])
                    except KeyError:
                        filtered_data_sets['pds'][ds_name] = set([line[1]])
                else:
                    filtered_data_sets['ps'].add(ds_name)
    return filtered_data_sets


def data_set_filter(module, pds_paths, patterns):
    """ Find data sets that match any pattern in a list of patterns.

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        patterns {list[str]} -- A list of data set patterns

    Returns:
        dict[ps=set, pds=dict[str, str], searched=int] -- A dictionary containing
        a set of matched "PS" data sets, a dictionary containing "PDS" data sets
        and members corresponding to each PDS, an int representing number of total
        data sets examined.
    """
    filtered_data_sets = dict(ps=set(), pds=dict(), searched=0)
    patterns = pds_paths or patterns
    for pattern in patterns:
        rc, out, err = _dls_wrapper(pattern, list_details=True)
        if rc != 0:
            if "BGYSC1103E" in err:
                return filtered_data_sets

            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'dls'",
                rc=rc, stdout=out, stderr=err
            )
        for ds in err.splitlines():
            if ds and ds.strip().startswith("BGYSC1005I"):
                filtered_data_sets['searched'] += 1

        for line in out.splitlines():
            result = line.split()
            if result:
                if result[1] == "PO":
                    if pds_paths:
                        mls_rc, mls_out, mls_err = module.run_command(
                            "mls '{0}(*)'".format(result[0])
                        )
                        if mls_rc == 2:
                            filtered_data_sets["pds"][result[0]] = {}
                        else:
                            filtered_data_sets["pds"][result[0]] = \
                                set(filter(None, mls_out.splitlines()))
                    else:
                        filtered_data_sets["pds"][result[0]] = {}
                else:
                    filtered_data_sets["ps"].add(result[0])
    return filtered_data_sets


def pds_filter(module, pds_dict, member_patterns, excludes=None):
    """ Return all PDS/PDSE data sets whose members match any of the patterns
    in the given list of member patterns.

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used in the module
        pds_dict {dict[str, str]} -- A dictionary where each key is the name of
                                    of the PDS/PDSE and the value is a list of
                                    members belonging to the PDS/PDSE
        member_patterns {list} -- A list of member patterns to search for

    Returns:
        dict[str, set[str]] -- Filtered PDS/PDSE with corresponding members
    """
    filtered_pds = dict()
    for pds, members in pds_dict.items():
        for m in members:
            for mem_pat in member_patterns:
                if _match_regex(module, mem_pat, m):
                    try:
                        filtered_pds[pds].add(m)
                    except KeyError:
                        filtered_pds[pds] = set({m})
    # ************************************************************************
    # Exclude any member that matches a given pattern in 'excludes'.
    # Changes will be made to 'filtered_pds' each iteration. Therefore,
    # iteration should be performed over a copy of 'filtered_pds'. Because
    # Python performs a shallow copy when copying a dictionary, a deep copy
    # should be performed.
    # ************************************************************************
    if excludes:
        for pds, members in deepcopy(filtered_pds).items():
            for m in members:
                for ex_pat in excludes:
                    if _match_regex(module, ex_pat, m):
                        filtered_pds[pds].remove(m)
                        break
    return filtered_pds


def vsam_filter(module, patterns, resource_type, age=None):
    """ Return all VSAM data sets that match any of the patterns
    in the given list of patterns.

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        patterns {list[str]} -- A list of data set patterns

    Returns:
        set[str]-- Matched VSAM data sets
    """
    filtered_data_sets = set()
    now = time.time()
    for pattern in patterns:
        rc, out, err = _vls_wrapper(pattern, details=True)
        if rc > 4:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'vls'",
                rc=rc, stdout=out, stderr=err
            )
        for entry in out.splitlines():
            if entry:
                vsam_props = entry.split()
                vsam_name = vsam_props[0]
                vsam_type = vsam_name.split('.')[-1]
                if _match_resource_type(resource_type, vsam_type):
                    if age:
                        if _age_filter(vsam_props[1], now, age):
                            filtered_data_sets.add(vsam_name)
                    else:
                        filtered_data_sets.add(vsam_name)
    return filtered_data_sets


def data_set_attribute_filter(
    module, data_sets, size=None, age=None, age_stamp="creation_date"
):
    """ Filter data sets based on attributes such as age or size.

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        data_sets {set[str]} -- A set of data set names
        size {int} -- The size, in bytes, that should be used to filter data sets
        age {int} -- The age, in days, that should be used to filter data sets

    Returns:
        set[str] -- Matched data sets filtered by age and size
    """
    filtered_data_sets = set()
    now = time.time()
    for ds in data_sets:
        rc, out, err = _dls_wrapper(
            ds, u_time=age is not None, size=size is not None
        )
        if rc != 0:
            module.fail_json(
                msg="Non-zero return code received while executing ZOAU shell command 'dls'",
                rc=rc, stdout=out, stderr=err
            )
        out = out.strip().split()
        ds_age = out[1] if age_stamp == "ref_date" else _get_creation_date(module, ds)
        if (
            (
                age
                and size
                and _age_filter(ds_age, now, age)
                and _size_filter(int(out[6]), size)
            ) or
            (
                age and not size and _age_filter(ds_age, now, age)
            ) or
            (
                size and not age and _size_filter(int(out[5]), size)
            )
        ):
            filtered_data_sets.add(ds)
    return filtered_data_sets


# TODO:
# Implement volume_filter() using "vtocls" shell command from ZOAU
# when it becomes available.
def volume_filter(module, data_sets, volumes):
    """Return only the data sets that are allocated in one of the volumes from
    the list of input volumes.

    Arguments:
        module {AnsibleModule} -- The Ansible module object
        data_sets {set[str]} -- A set of data sets to be filtered
        volumes {list[str]} -- A list of input volumes

    Returns:
        set[str] -- The filtered data sets
    """
    filtered_data_sets = set()
    for volume in volumes:
        vtoc_entry = vtoc.get_volume_entry(volume)
        if vtoc_entry:
            for ds in vtoc_entry:
                if ds.get('data_set_name') in data_sets:
                    filtered_data_sets.add(ds.get('data_set_name'))
        else:
            module.fail_json(
                msg="Unable to retrieve VTOC information for volume {0}".format(volume)
            )

    return filtered_data_sets


def exclude_data_sets(module, data_set_list, excludes):
    """Remove data sets that match any pattern in a list of patterns

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        data_set_list {set[str]} -- A set of data sets to be filtered
        excludes {list[str]} -- A list of data set patterns to be excluded

    Returns:
        set[str] -- The remaining data sets that have not been excluded
    """
    for ds in set(data_set_list):
        for ex_pat in excludes:
            if _match_regex(module, ex_pat, ds):
                data_set_list.remove(ds)
                break
    return data_set_list


def _age_filter(ds_date, now, age):
    """Determine whether a given date is older than 'age'

    Arguments:
        ds_date {str} -- The input date in the format YYYY/MM/DD
        now {float} -- The time elapsed since the last epoch
        age {int} -- The age, in days, to compare against

    Returns:
        bool -- Whether 'ds_date' is older than 'age'
    """
    year, month, day = list(map(int, ds_date.split("/")))
    if year == "0000":
        return age >= 0

    # Seconds per day = 86400
    ds_age = datetime.datetime(year, month, day).timestamp()
    if age >= 0 and (now - ds_age) / 86400 >= abs(age):
        return True
    elif age < 0 and (now - ds_age) / 86400 <= abs(age):
        return True
    return False


def _get_creation_date(module, ds):
    """Retrieve the creation date for a given data set

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        ds {str} -- The name of the data set

    Returns:
        str -- The data set creation date in the format "YYYY/MM/DD"
    """
    rc, out, err = mvs_cmd.idcams(
        "  LISTCAT ENT('{0}') HISTORY".format(ds), authorized=True
    )
    if rc != 0:
        module.fail_json(
            msg="Non-zero return code received while retrieving data set age",
            rc=rc, stderr=err, stdout=out
        )
    out = re.findall(r"CREATION-*[A-Z|0-9]*", out.strip())
    if out:
        out = out[0]
        date = "".join(re.findall(r"-[A-Z|0-9]*", out)).replace("-", "").split(".")
        days = 1 if len(date) < 2 else int(date[1])
        years = int(date[0])
        days_per_month = 30.4167
        return "{0}/{1}/{2}".format(
            years,
            math.ceil(days / days_per_month),
            math.ceil(days % days_per_month)
        )

    # If no creation data is found, return default "000/1/1"
    return "000/1/1"


def _size_filter(ds_size, size):
    """ Determine whether a given size is greater than the input size

    Arguments:
        ds_size {int} -- The input size, in bytes
        size {int} -- The size, in bytes, to compare against

    Returns:
        bool -- Whether 'ds_size' is greater than 'age'
    """
    if size >= 0 and ds_size >= abs(size):
        return True
    if size < 0 and ds_size <= abs(size):
        return True
    return False


def _match_regex(module, pattern, string):
    """ Determine whether the input regex pattern matches the string

    Arguments:
        module {AnsibleModule} -- The Ansible module object being used
        pattern {str} -- The regular expression to match
        string {str} -- The string to match

    Returns:
        re.Match -- A Match object that matches the pattern to string
    """
    try:
        return fullmatch(pattern, string, re.IGNORECASE)
    except re.error as err:
        module.fail_json(
            msg="Invalid regular expression '{0}'".format(pattern),
            stderr=repr(err)
        )


def _dgrep_wrapper(
    data_set_pattern,
    content,
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

    dgrep_cmd += " {0} {1}".format(quote(content), quote(data_set_pattern))
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


def _match_resource_type(type1, type2):
    if type1 == type2:
        return True
    if type1 == "CLUSTER" and type2 not in ("DATA", "INDEX"):
        return True
    return False


def _ds_type(ds_name):
    """Utility function to determine the DSORG of a data set

    Arguments:
        ds_name {str} -- The name of the data set

    Returns:
        str -- The DSORG of the data set
    """
    rc, out, err = mvs_cmd.ikjeft01(
        "  LISTDS '{0}'".format(ds_name),
        authorized=True
    )
    if rc == 0:
        search = re.search(r"(-|--)DSORG(-\s*|\s*)\n(.*)", out, re.MULTILINE)
        return search.group(3).split()[-1]
    return None


def run_module(module):
    # Parameter initialization
    age = module.params.get('age')
    age_stamp = module.params.get('age_stamp')
    contains = module.params.get('contains')
    excludes = module.params.get('excludes') or module.params.get('exclude')
    patterns = module.params.get('patterns')
    size = module.params.get('size')
    pds_paths = (
        module.params.get('pds_paths')
        or module.params.get('pds_patterns')
        or module.params.get('pds_pattern')
    )
    resource_type = module.params.get('resource_type').upper()
    volume = module.params.get('volume') or module.params.get('volumes')

    res_args = dict(data_sets=[])
    filtered_data_sets = set()
    init_filtered_data_sets = filtered_pds = dict()

    if age:
        # convert age to days:
        m = re.match(r"^(-?\d+)(d|w|m|y)?$", age.lower())
        days_per_unit = {"d": 1, "w": 7, "m": 30, "y": 365}
        if m:
            age = int(m.group(1)) * days_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(age=age, msg="failed to process age")

    if size:
        # convert size to bytes:
        m = re.match(r"^(-?\d+)(b|k|m|g|t)?$", size.lower())
        bytes_per_unit = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}
        if m:
            size = int(m.group(1)) * bytes_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(size=size, msg="failed to process size")

    if resource_type == "NONVSAM":
        if contains:
            init_filtered_data_sets = content_filter(
                module,
                pds_paths if pds_paths else patterns,
                contains
            )
        else:
            init_filtered_data_sets = data_set_filter(
                module,
                pds_paths,
                patterns
            )
        if pds_paths:
            filtered_pds = pds_filter(
                module, init_filtered_data_sets.get("pds"), patterns, excludes=excludes
            )
            filtered_data_sets = set(filtered_pds.keys())
        else:
            filtered_data_sets = \
                init_filtered_data_sets.get("ps").union(set(init_filtered_data_sets['pds'].keys()))

        # Filter data sets by age or size
        if size or age:
            filtered_data_sets = data_set_attribute_filter(
                module, filtered_data_sets, size=size, age=age, age_stamp=age_stamp
            )

        # Filter data sets by volume
        if volume:
            filtered_data_sets = volume_filter(module, filtered_data_sets, volume)

        res_args['examined'] = init_filtered_data_sets.get("searched")

    else:
        filtered_data_sets = vsam_filter(module, patterns, resource_type, age=age)
        res_args['examined'] = len(filtered_data_sets)

    # Filter out data sets that match one of the patterns in 'excludes'
    if excludes and not pds_paths:
        filtered_data_sets = exclude_data_sets(module, filtered_data_sets, excludes)

    for ds in filtered_data_sets:
        if resource_type == "NONVSAM":
            members = filtered_pds.get(ds) or init_filtered_data_sets['pds'].get(ds)
            if members:
                res_args['data_sets'].append(
                    dict(name=ds, members=members, type=resource_type)
                )
            else:
                res_args['data_sets'].append(dict(name=ds, type=resource_type))
        else:
            res_args['data_sets'].append(dict(name=ds, type=resource_type))

    res_args['matched'] = len(filtered_data_sets)
    return res_args


def main():
    module = AnsibleModule(
        argument_spec=dict(
            age=dict(type="str", required=False),
            age_stamp=dict(
                type="str",
                required=False,
                choices=["creation_date", "ref_date"],
                default="creation_date"
            ),
            contains=dict(type="str", required=False),
            excludes=dict(type="list", required=False, aliases=["exclude"]),
            patterns=dict(type="list", required=True),
            size=dict(type="str", required=False),
            pds_patterns=dict(
                type="list",
                required=False,
                aliases=["pds_pattern", "pds_paths"]
            ),
            resource_type=dict(
                type="str", required=False, default="nonvsam",
                choices=["cluster", "data", "index", "nonvsam"]
            ),
            volume=dict(type="list", required=False, aliases=["volumes"])
        )
    )

    arg_def = dict(
        age=dict(arg_type="str", required=False),
        age_stamp=dict(
            arg_type="str",
            required=False,
            choices=["creation_date", "ref_date"],
            default="creation_date"
        ),
        contains=dict(arg_type="str", required=False),
        excludes=dict(arg_type="list", required=False, aliases=["exclude"]),
        patterns=dict(arg_type="list", required=True),
        size=dict(arg_type="str", required=False),
        pds_patterns=dict(
            arg_type="list",
            required=False,
            aliases=["pds_pattern", "pds_paths"]
        ),
        resource_type=dict(
            arg_type="str",
            required=False,
            default="nonvsam",
            choices=["cluster", "data", "index", "nonvsam"]
        ),
        volume=dict(arg_type="list", required=False, aliases=["volumes"])
    )
    try:
        BetterArgParser(arg_def).parse_args(module.params)
    except ValueError as err:
        module.fail_json(
            msg="Parameter verification failed", stderr=str(err)
        )
    module.exit_json(**run_module(module))


if __name__ == '__main__':
    main()
