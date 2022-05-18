#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2022
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

DOCUMENTATION = r'''
---
module: zos_gather_facts

short_description: Gather facts about target z/OS systems.

version_added: "1.4.2"

description:
  - Retrieve useful variables from z/OS target systems.
  - Variables are added to ansible_facts dict which is available from all
    playbooks.
  - Use gather_subset and filter to cut down on variables added to
    ansible_facts.
  - Module will fail fast if any illegal options are provided. This is done to
    raise awareness of a failure early in an automation setting.

options:
  gather_subset:
    type: list
    elements: str
    default: ['all']
    required: False
    description:
      - If specified, it will only collect facts which come under the specified
        subset (eg ipl will return only ipl facts). Specifying subsets is an
        excellent way to save on time taken to gather all facts in cases where
        facts needed can be constrained down to one or more subsets.
  filter:
    type: list
    elements: str
    required: False
    default: []
    description:
      - uses shell-style (fnmatch) pattern matching to filter out collected
        facts.
      - Note - this is done after the facts are gathered, so this will not save
        time/compute, it will only reduce the number of variables added to
        ansible_facts. To restrict the actual facts collected, refer to the
        gather_subset parameter.
      - An empty list means 'no filter', same as providing '*'.

author:
    - Ketan Kelkar (@ketankelkar)
'''

EXAMPLES = r'''
- name: Return all available z/OS facts
  ibm.ibm_zos_core.zos_gather_facts:

- name: Return z/OS facts in the systems subset ('sys')
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset: sys

- name: Return z/OS facts in the subsets ('ipl' and 'sys') and filter out all
        facts which do not match 'parmlib'
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset:
      - ipl
      - sys
    filter:
      - "*parmlib*"
'''

RETURN = r'''
ansible_facts:
  description: Facts from z/OS are added to ansible_facts.
  returned: sometimes
  type: dict
'''

from fnmatch import fnmatch
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    zoau_version_checker
)


def zinfo_cmd_string_builder(gather_subset):
    """Builds command string for 'zinfo' based off gather_subset list.
    Arguments:
        gather_subset {list} -- list of subsets to pass in.
    Returns:
        [str] -- A string containing a command line argument calling zinfo with
                the appropriate options.
        [None] -- Received bad value for subset.
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
    """Removes one layer of mapping in the dict. Top-level keys correspond to
        zinfo subsets and are removed.
    Arguments:
        zinfo_dict {dict} -- dict containing parsed result from zinfo json str.
    Returns:
        [dict] -- A flattened dict.
    """
    d = dict()
    for subset in list(zinfo_dict):
        d.update(zinfo_dict[subset])
    return d


def apply_filter(zinfo_dict, filter_list):
    """Returns dict containing only keys which fit the specified filter(s).
    Arguments:
        zinfo_dict {dict} -- flattened dict containing results from zinfo.
        filter_list {list} -- str list of shell wildcard patterns ie 'filters'
                              to apply to zinfo_dict keys.
    Returns:
        [dict] -- A dict with keys filtered out.
    """

    if filter_list is None or filter_list == [] or '*' in filter_list:
        return zinfo_dict

    filtered_d = {}
    for filter in filter_list:
        for k, v in zinfo_dict.items():
            if(fnmatch(k, filter)):
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


        #                     saved for future development                    #
        # gather_timeout=dict(default=10, required=False, type='int'),        #
        # fact_path=dict(
        #       default='/etc/ansible/facts.d', required=False, type='path'),
        #######################################################################
    )

    # setup Ansible module basics
    result = dict(
        changed=False,  # fact gathering will never change state of system
        ansible_facts=dict(),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json(**result)

    if not zoau_version_checker.is_zoau_version_higher_than("1.2.1"):
        module.fail_json(
            ("zos_gather_facts module requires ZOAU >= 1.2.1. Please update "
             "ZOAU version on the target node.")
        )

    gather_subset = module.params['gather_subset']

    # build out zinfo command with correct options
    # call this whether or not gather_subsets list is empty/valid/etc
    # rely on the function to report back errors. Note the function only
    # returns None if there's malicious or improperly formatted subsets.
    # Invalid subsets are caught when the actual zinfo command is run.
    cmd = zinfo_cmd_string_builder(gather_subset)
    if not cmd:
        module.fail_json(msg="Invalid subset given to Ansible.")

    rc, fcinfo_out, err = module.run_command(cmd, encoding=None)

    decode_str = fcinfo_out.decode('utf-8')

    # We DO NOT return a partial list. Instead we FAIL FAST since we are
    # targeting automation -- quiet but well-intended error messages may easily
    # be skipped
    if rc != 0:
        # there are only 2 known error messages in zinfo, if neither gets
        # triggered then we send out this generic zinfo error message.
        err_msg = ('An exception has occurred in Z Open Automation Utilities '
                   '(ZOAU) utility \'zinfo\'. See \'zinfo_err_msg\' for '
                   'additional details.')
        if 'BGYSC5201E' in err.decode('utf-8'):
            err_msg = ('Invalid susbset detected. See \'zinfo_err_msg\' for '
                       'additional details.')
        elif 'BGYSC5202E' in err.decode('utf-8'):
            err_msg = ('Invalid option passed to zinfo. See \'zinfo_err_msg\' '
                       'for additional details.')

        module.fail_json(msg=err_msg, zinfo_err_msg=err)

    zinfo_dict = {}  # to track parsed zinfo facts.

    try:
        zinfo_dict = json.loads(decode_str)
    except json.JSONDecodeError:
        # TODO -figure out this error message...what do i tell user?
        module.fail_json(msg="There was JSON error.")

    # remove zinfo subsets from parsed zinfo result, flatten by one level
    flattened_d = flatten_zinfo_json(zinfo_dict)

    # apply filter
    filter = module.params['filter']
    filtered_d = apply_filter(flattened_d, filter)

    # add updated facts dict to ansible_facts dict
    result['ansible_facts'].update(filtered_d)

    # successful module execution
    module.exit_json(**result)


# NOTE

# How does the user know what subsets are available. maybe investigate what
# Ansible does and copy them. Alternative idea is to document 'current'
# available subsets but not enforce additional or maybe link out to zoau zinfo
# doc (linking out is frowned upon.)

# Thinking about creating a mapping (maybe CSV) in module_utils which can allow
# for more legal subset options (eg 'iplinfo', 'ipl', 'ipl_info' -> ipl, etc).
# The mapping can be updated with zinfo but there will also be a provision
# for subsets not in the mapping. We cannot tie ansible error reporting to
# zinfo error reporting because that could change in the future and result in
# mismatched compatibility, instead we can simply pass on zinfo output as is
# and leave it to the user to figure out which subsets are illegal


def main():
    run_module()


if __name__ == '__main__':
    main()
