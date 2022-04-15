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
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zos_gather_facts

short_description: z/OS gather facts module

version_added: "1.0.0"

description: Retrieve facts from z/OS targets.

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

import sys
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import BetterArgParser

def zinfo_cmd_string_builder():
    ipl_opt = " -t ipl"
    # sys_opt = " -t sys"
    # cpu_opt = " -t cpu"
    # iodf_opt = " -t iodf"

    # base value
    zinfo_arg_string = "zinfo -j"

    # build full string
    # contrived for now, develop this as the module takes shape
    zinfo_arg_string += ipl_opt
    # zinfo_arg_string += sys_opt

    return zinfo_arg_string

def flatten_zinfo_json(zinfo_dict):
    d = dict()
    for subset in list(zinfo_dict):
        d.update(zinfo_dict[subset])
    return d

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        gather_subset=dict(default=["all"], required=False, type='list', elements='str'),
        # the filter parameter was updated to type list in Ansible 2.11
        filter=dict(default=[], required=False, type='list', elements='str'),
        # gather_timeout=dict(default=10, required=False, type='int'),
        # fact_path=dict(default='/etc/ansible/facts.d', required=False, type='path'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        ansible_facts=dict(),
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications

    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # TODO - check for zoau version >=1.2.1 else error out

    cmd = zinfo_cmd_string_builder()

    # ansible_facts['zzz_REMOVE_ME_cmd_str'] = cmd
    result['ansible_facts'] = {
        'zzz_REMOVE_ME_cmd_str' : cmd
    }

    rc, fcinfo_out, err = module.run_command(cmd, encoding=None) # there's a way to force a path var into this.

    decode_str = fcinfo_out.decode('utf-8')

    # TODO - check for zinfo error messages
    # add error handling - json decode error - check string for zinfo error message

    result['ansible_facts']['zinfo'] = json.loads(decode_str)

    d = flatten_zinfo_json(json.loads(decode_str))
    result['ansible_facts'].update(d)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)
    # module.exit_json(ansible_facts=ansible_facts)



def main():
    run_module()

if __name__ == '__main__':
    main()