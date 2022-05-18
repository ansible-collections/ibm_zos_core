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
  - Retrieve useful variables from the target z/OS systems.
  - Add variables to the ansible_facts dictionary, which is available from all
    playbooks.
  - Apply filters on the gather_subset list to cut down on variables that are
    added to the ansible_facts dictionary.
  - Note: Module will fail fast if any illegal options are provided. This is
    done to raise awareness of a failure early in an automation setting.

options:
  gather_subset:
    type: list
    elements: str
    default: ['all']
    required: False
    description:
      - If specified, it will only collect facts that come under the specified
        subset (eg. ipl will only return ipl facts). Specifying subsets is
        recommended to save time on gatherthing all facts when the facts needed
        are constrained down to one or more subsets.
  filter:
    type: list
    elements: str
    required: False
    default: []
    description:
      - Uses shell-style (fnmatch) pattern matching to filter out the collected
        facts.
      - An empty list means 'no filter', same as providing '*'.
      - Note - this is done after the facts are gathered, so this doesn't save
        time/compute. It only reduces the number of variables that are added to
        the ansible_facts dictionary. To restrict the actual facts that are
        collected, refer to the gather_subset parameter above.

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
        facts that do not match 'parmlib'
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset:
      - ipl
      - sys
    filter:
      - "*parmlib*"
'''

RETURN = r'''
ansible_facts:
  description: Store the facts that are gathered from z/OS systems.
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
    """Removes one layer of mapping in the dictionary. Top-level keys correspond
        to zinfo subsets and are removed.
    Arguments:
        zinfo_dict {dict} -- A dictionary that contains the parsed result from
                             the zinfo json string.
    Returns:
        [dict] -- A flattened dictionary.
    """
    d = dict()
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
            ("The zos_gather_facts module requires ZOAU >= 1.2.1. Please upgrade "
             "the ZOAU version on the target node.")
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
        # there are only 2 known error messages in zinfo, if neither gets
        # triggered then we send out this generic zinfo error message.
        err_msg = ('An exception has occurred in Z Open Automation Utilities '
                   '(ZOAU) utility \'zinfo\'. See \'zinfo_err_msg\' for '
                   'additional details.')
        if 'BGYSC5201E' in err.decode('utf-8'):
            err_msg = ('An invalid susbset was detected. See \'zinfo_err_msg\' for '
                       'additional details.')
        elif 'BGYSC5202E' in err.decode('utf-8'):
            err_msg = ('An invalid option was passed to zinfo. See \'zinfo_err_msg\' '
                       'for additional details.')

        module.fail_json(msg=err_msg, zinfo_err_msg=err)

    zinfo_dict = {}  # to track parsed zinfo facts.

    try:
        zinfo_dict = json.loads(decode_str)
    except json.JSONDecodeError:
        # TODO -figure out this error message...what do i tell user?
        # (Jenny - why did this error happen and how could users fix the error?)
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
