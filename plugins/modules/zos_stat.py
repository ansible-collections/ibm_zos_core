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
module: zos_stat
version_added: '1.14.0'
author:
  - "Ivan Moreno (@rexemin)"
short_description: Retrieve facts from z/OS
description:
  - The L(zos_stat,./zos_stat.html) module retrieves facts from objects
    stored in a z/OS system.
  - Objects that can be queried are files, data sets and aggregates.
options:
  name:
    description:
        - Name of a data set or aggregate, or a file path, to query.
        - Data sets can be sequential, partitioned (PDS), partitioned
          extended (PDSE), VSAMs or generation data sets (GDGs).
    type: str
    required: true
  volumes:
    description:
        - List of volumes where a data set will be searched on.
        - Required when getting facts from a data set. Ignored otherwise.
    type: list
    elements: str
    required: false
  type:
    description:
        - Type of object to query.
    type: str
    required: false
    default: data_set
    choices:
      - data_set
      - file
      - aggregate

seealso:
  - module: ansible.builtin.stat
  - module: zos_find
"""

EXAMPLES = r"""
- name:
  zos_stat:
"""

RETURN = r"""
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)


def run_module():
    """Parses the module's options and retrieves facts accordingly.
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True
            },
            'volumes': {
                'type': 'list',
                'required': False,
                'elements': 'str',
            },
            'type': {
                'type': 'str',
                'required': False,
                'default': 'data_set',
                'choices': ['data_set', 'file', 'aggregate']
            }
        },
        required_if=[
            # Forcing a volume list when querying data sets.
            ('type', 'data_set', ('volumes',))
        ],
        supports_check_mode=True,
    )

    args_def = {
        'name': {
            'arg_type': 'data_set_or_path',
            'required': True
        },
        'volumes': {
            'arg_type': 'list',
            'required': False
        },
        'type': {
            'arg_type': 'str',
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

    result = {'changed': True}
    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
