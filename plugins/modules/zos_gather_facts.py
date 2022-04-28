#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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
from asyncio import gather
from email.utils import decode_params
from xml.dom.minidom import Element
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zos_gather_facts

short_description: z/OS gather facts module

version_added: "1.4.2"

description: Retrieve facts from z/OS targets. Note - module will fail fast if any illegal options are provided. This is done to raise awareness of a failure early in an automation setting.

author:
    - Ketan Kelkar (@ketankelkar)
'''

EXAMPLES = r'''
- name: Return all available z/OS facts
  ibm.ibm_zos_core.zos_gather_facts:

- name: Return z/OS facts in the systems subset ('sys')
  ibm.ibm_zos_core.zos_gather_facts:
    gather_subset: sys

- name: Return z/OS facts in the systems subset ('ipl') and filter out all facts not related to 'parmlib'
    ibm.ibm_zos_core.zos_gather_facts:
    gather_subset:
      - ipl
    filter:
      - "parmlib*"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
ansible_facts:
  description: Facts to add to ansible_facts.
  returned: always
  type: dict
  contains:
    foo:
      description: Foo facts about operating system.
      type: str
      returned: when operating system foo fact is present
      sample: 'bar'
    answer:
      description:
      - Answer facts about operating system.
      - This description can be a list as well.
      type: str
      returned: when operating system answer fact is present
      sample: '42'
'''

# will be built out as gather scripts are integrated into the module.
# following the example of nxos_facts module: https://github.com/ansible/ansible/blob/98f804ecb44278628070829bd1841ca51476f7b9/lib/ansible/modules/network/nxos/nxos_facts.py

from fnmatch import fnmatch
import json
import sys

from ansible.module_utils.basic import AnsibleModule

def zinfo_cmd_string_builder(gather_subset):
    """Builds command string for 'zinfo' based off gather_subset list.
    Arguments:
        gather_subset {list} -- list of subsets to pass in.
    Raises:
        SomeError: maybe?? -- TODO
    Returns:
        [str] -- A string containing a command line argument calling zinfo with the appropriate options.
        None -- Bad value for subset.
    """
    if gather_subset == None or 'all' in gather_subset:
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
    """Removes one layer of mapping in the dict. Top-level keys correspond to zinfo subsets and are removed
    Arguments:
        zinfo_dict {dict} -- dict containing parsed result from zinfo json str.
    Raises:
        SomeError: maybe?? -- TODO
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
        filters
        filter_list {list} -- str list of shell wildcard patterns ie 'filters' to apply to zinfo_dict keys.
    Raises:
        SomeError: maybe?? -- TODO
    Returns:
        [dict] -- A dict with keys filtered out.
    """

    if filter_list is None or filter_list == []:
        return zinfo_dict

    filtered_d = {}
    for filter in filter_list:
        for k, v in zinfo_dict.items():
            if(fnmatch(k, filter)):
                filtered_d.update({k : v})
    return filtered_d

# How does the user know what subsets are available. maybe investigate what Ansible does and copy them. Alternative idea is to document 'current' available subsets but not enforce additional or maybe link out to zoau zinfo doc (linking out is frowned upon.)

# Thinking about creating a mapping (maybe CSV) in module_utils which can allow for more legal subset options (eg 'iplinfo', 'ipl', 'ipl_info' -> ipl, etc). The mapping can be updated as zinfo changes but there will also be a provision for subsets not in the mapping. We cannot tie ansible error reporting to zinfo error reporting because that could change in the future and result in mismatched compatibility, instead we can simply pass on zinfo output as is and leave it to the user to figure out which subsets are illegal,


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        gather_subset=dict(default=["all"], required=False, type='list', elements='str'),
        # the filter parameter was updated to type list in Ansible 2.11
        filter=dict(default=[], required=False, type='list', elements='str'),
        # gather_timeout=dict(default=10, required=False, type='int'),
        # fact_path=dict(default='/etc/ansible/facts.d', required=False, type='path'),
    )

    # setup Ansible module basics
    result = dict(
        changed=False, # fact gathering will never change state of system
        ansible_facts=dict(),
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    if module.check_mode:
        module.exit_json(**result)

    # TODO - check for zoau version >=1.2.1 else error out

    gather_subset = module.params['gather_subset']

    # build out zinfo command with correct options
    # call this whether or not gather_subsets list is empty/valid/etc
    # rely on the function to report back errors.
    cmd = zinfo_cmd_string_builder(gather_subset)
    if not cmd:
        module.fail_json(msg="Received an invalid subset.")


    # TODO - REMOVE THIS BLOCK
    result['ansible_facts']['zzz'] = {}
    result['ansible_facts']['zzz'].update({
        'params' : module.params,
        'cmd_str' : cmd,
    })

    rc, fcinfo_out, err = module.run_command(cmd, encoding=None)

    decode_str = fcinfo_out.decode('utf-8')

    # TODO - REMOVE THIS BLOCK
    result['ansible_facts']['zzz'].update({
        'rc' : rc,
        'err' : err,
    })

    # We DO NOT return a partial list. Instead we FAIL FAST since we are targeting automation -- so quiet but well-intended error messages may easily be skipped
    if rc != 0:
    # if err is not None:
        # TODO determine if more information should be divulged here...maybe print zinfo help msg
        err_msg = 'There was an issue with zinfo output...'
        if 'BGYSC5201E' in err.decode('utf-8'):
            err_msg = 'Invalid susbset detected.'
        elif 'BGYSC5202E' in err.decode('utf-8'):
            err_msg = 'Invalid option passed to zinfo.'

        module.fail_json(msg=err_msg, debug_cmd_str=cmd, debug_cmd_err=err, debug_rc=rc)

    zinfo_dict = {}
    try:
        zinfo_dict = json.loads(decode_str)
        result['ansible_facts']['zzz']['zinfo_output_str'] = json.loads(decode_str)
    except json.JSONDecodeError:
        # TODO -figure out this error message...what do i tell user?
        module.fail_json(msg="There was a JSON error.")

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