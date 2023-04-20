#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2022, 2023
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
module: zos_gather_facts
short_description: Gather z/OS system facts.
version_added: '1.5.0'
requirements:
    - ZOAU 1.2.1 or later.
author:
    - "Ketan Kelkar (@ketankelkar)"
description:
  - Retrieve variables from target z/OS systems.
  - Variables are added to the I(ansible_facts) dictionary, available to
    playbooks.
  - Apply filters on the I(gather_subset) list to reduce the variables that are
    added to the I(ansible_facts) dictionary.
  - Note, the module will fail fast if any unsupported options are provided.
    This is done to raise awareness of a failure in an automation setting.
options:
  gather_subset:
    type: list
    elements: str
    default: ["all"]
    required: false
    description:
      - If specified, it will collect facts that come under the specified
        subset (eg. ipl will return ipl facts). Specifying subsets is
        recommended to reduce time in gathering facts when the facts needed
        are in a specific subset.
      - The following subsets are available C(ipl), C(cpu), C(sys), and
        C(iodf). Depending on the version of ZOAU, additional subsets may be
        available.
  filter:
    type: list
    elements: str
    required: false
    default: []
    description:
      - Filter out facts from the I(ansible_facts) dictionary.
      - Uses shell-style L(fnmatch, https://docs.python.org/3/library/fnmatch.html)
        pattern matching to filter out the collected facts.
      - An empty list means 'no filter', same as providing '*'.
      - Filtering is performed after the facts are gathered such that no compute
        is saved when filtering. Filtering only reduces the number of variables
        that are added to the I(ansible_facts) dictionary. To restrict the facts
        that are collected, refer to the I(gather_subset) parameter.
"""

EXAMPLES = r"""
- name: Return all available z/OS facts.
  ibm.ibm_zos_core.zos_gather_facts:

- name: Return z/OS facts in the systems subset ('sys').
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset: sys

- name: Return z/OS facts in the subsets ('ipl' and 'sys') and filter out all
        facts that do not match 'parmlib'.
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset:
      - ipl
      - sys
    filter:
      - "*parmlib*"
"""

RETURN = r"""
ansible_facts:
  description: Collection of facts that are gathered from the z/OS systems.
  returned: when collected
  type: dict
  sample:
    [
        "ansible_facts": {
            "arch_level": "2",
            "hw_name": "SYSZD6",
            "ipl_volume": "RES820",
            "lpar_name": "SVLLAB01",
            "primary_jes": "JES2",
            "product_mod_level": "00",
            "product_name": "z/OS",
            "product_owner": "IBM CORP",
            "product_release": "05",
            "product_version": "02",
            "smf_name": "3090",
            "sys_name": "EC33018A",
            "sysplex_name": "SVPLEX1",
            "vm_name": "EC33018A"
        }
    ]
"""

from fnmatch import fnmatch
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    zoau_version_checker
)


def zinfo_cmd_string_builder(gather_subset):
    """Builds a command string for 'zinfo' based off the gather_subset list.
    Arguments:
        gather_subset {list} -- A list of subsets to pass in.
    Returns:
        [str] -- A string that contains a command line argument for calling
                 zinfo with the appropriate options.
        [None] -- An invalid value was received for the subsets.
    """
    if gather_subset is None or 'all' in gather_subset:
        return "zinfo -j -a"

    # base value
    zinfo_arg_string = "zinfo -j"

    # build full string
    for subset in gather_subset:
        # remove leading/trailing spaces
        subset = subset.strip()
        # empty string as subset is bad
        if not subset:
            return None
        # sanitize subset against malicious (probably alphanumeric only?)
        if not subset.isalnum():
            return None
        zinfo_arg_string += " -t " + subset

    return zinfo_arg_string


def flatten_zinfo_json(zinfo_dict):
    """Removes one layer of mapping in the dictionary. Top-level keys
        correspond to zinfo subsets and are removed.
    Arguments:
        zinfo_dict {dict} -- A dictionary that contains the parsed result from
                             the zinfo json string.
    Returns:
        [dict] -- A flattened dictionary.
    """
    d = {}
    for subset in list(zinfo_dict):
        d.update(zinfo_dict[subset])
    return d


def apply_filter(zinfo_dict, filter_list):
    """Returns a dictionary that contains only the keys which fit the specified
       filters.
    Arguments:
        zinfo_dict {dict} -- A flattened dictionary that contains results from
                             zinfo.
        filter_list {list} -- A string list of shell wildcard patterns (i.e.
                              'filters') to apply to the zinfo_dict keys.
    Returns:
        [dict] -- A dictionary with keys that are filtered out.
    """

    if filter_list is None or filter_list == [] or '*' in filter_list:
        return zinfo_dict

    filtered_d = {}
    for filter in filter_list:
        for k, v in zinfo_dict.items():
            if fnmatch(k, filter):
                filtered_d.update({k: v})
    return filtered_d


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        gather_subset=dict(
            default=["all"], required=False, type='list', elements='str'
        ),
        # the filter parameter was updated to type list in Ansible 2.11
        filter=dict(default=[], required=False, type='list', elements='str'),


        #######################################################################
        #                     saved for future development                    #
        # gather_timeout=dict(default=10, required=False, type='int'),        #
        # fact_path=dict(
        #       default='/etc/ansible/facts.d', required=False, type='path'),
        #######################################################################
    )

    # setup Ansible module basics
    result = dict(
        changed=False,  # fact gathering will never change state of system
        ansible_facts={},
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json(**result)

    if not zoau_version_checker.is_zoau_version_higher_than("1.2.1"):
        module.fail_json(
            ("The zos_gather_facts module requires ZOAU >= 1.2.1. Please "
             "upgrade the ZOAU version on the target node.")
        )

    gather_subset = module.params['gather_subset']

    # build out zinfo command with correct options
    # call this whether or not gather_subsets list is empty/valid/etc
    # rely on the function to report back errors. Note the function only
    # returns None if there's malicious or improperly formatted subsets.
    # Invalid subsets are caught when the actual zinfo command is run.
    cmd = zinfo_cmd_string_builder(gather_subset)
    if not cmd:
        module.fail_json(msg="An invalid subset was passed to Ansible.")

    rc, fcinfo_out, err = module.run_command(cmd, encoding=None)

    decode_str = fcinfo_out.decode('utf-8')

    # We DO NOT return a partial list. Instead we FAIL FAST since we are
    # targeting automation -- quiet but well-intended error messages may easily
    # be skipped
    if rc != 0:
        # there are 3 known error messages in zinfo, if neither gets
        # triggered then we send out this generic zinfo error message.
        err_msg = ('An exception has occurred in Z Open Automation Utilities '
                   '(ZOAU) utility \'zinfo\'. See \'zinfo_err_msg\' for '
                   'additional details.')
        # triggered by invalid optarg eg "zinfo -q"
        if 'BGYSC5201E' in err.decode('utf-8'):
            err_msg = ('Invalid call to zinfo. See \'zinfo_err_msg\' for '
                       'additional details.')
        # triggered when optarg does not get expected arg eg "zinfo -t"
        elif 'BGYSC5202E' in err.decode('utf-8'):
            err_msg = ('Invalid call to zinfo. Possibly missing a valid subset'
                       ' See \'zinfo_err_msg\' for additional details.')
        # triggered by illegal subset eg "zinfo -t abc"
        elif 'BGYSC5203E' in err.decode('utf-8'):
            err_msg = ('An invalid subset was detected. See \'zinfo_err_msg\' '
                       'for additional details.')

        module.fail_json(msg=err_msg, zinfo_err_msg=err)

    zinfo_dict = {}  # to track parsed zinfo facts.

    try:
        zinfo_dict = json.loads(decode_str)
    except json.JSONDecodeError:
        # tell user something else for this error? This error is thrown when
        # Python doesn't like the json string it parsed from zinfo.
        module.fail_json(msg="Unsupported JSON format for the output.")

    # remove zinfo subsets from parsed zinfo result, flatten by one level
    flattened_d = flatten_zinfo_json(zinfo_dict)

    # apply filter
    filter = module.params['filter']
    filtered_d = apply_filter(flattened_d, filter)

    # add updated facts dict to ansible_facts dict
    result['ansible_facts'].update(filtered_d)

    # successful module execution
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
