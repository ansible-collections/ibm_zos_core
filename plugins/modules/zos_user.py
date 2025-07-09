#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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
module: zos_user
version_added: '2.0.0'
author:
  - "Alex Moreno (@rexemin)"
short_description:
description:
  - The L(zos_user,./zos_user.html)
options:

attributes:
  action:
    support: none
    description: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
  async:
    support: full
    description: Supports being used with the ``async`` keyword.
  check_mode:
    support: full
    description: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.

notes:

seealso:
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)

def run_module():
    """
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True,
                'aliases': ['src']
            },
            'operation': {
                'type': 'choice',
                'required': True,
                'choices': ['create', 'list', 'update', 'delete', 'purge', 'connect', 'remove']
            },
            'scope': {
                'type': 'choice',
                'required': True,
                'choices': ['user', 'group']
            }
        },
        supports_check_mode=True
    )

    args_def = {
        'name': {
            'arg_type': 'str',
            'required': True,
            'aliases': ['src']
        },
        'operation': {
            'type': 'str',
            'required': True
        },
        'scope': {
            'type': 'str',
            'required': True
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

if __name__ == '__main__':
    run_module()
