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
  - The L(zos_stat,./zos_stat.html) module retrieves facts from resources
    stored in a z/OS system.
  - Resources that can be queried are files, data sets and aggregates.
options:
  name:
    description:
        - Name of a data set or aggregate, or a file path, to query.
        - Data sets can be sequential, partitioned (PDS), partitioned
          extended (PDSE), VSAMs or generation data sets (GDGs).
    type: str
    required: true
  volume:
    description:
        - Name of the volume where the data set will be searched on.
        - Required when getting facts from a data set. Ignored otherwise.
    type: str
    required: false
  type:
    description:
        - Type of resource to query.
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
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    DataSet,
    MVSDataSet,
    GenerationDataGroup
)

class FactsHandler():
    """Base class for every other handler that will query resources on
    a z/OS system.
    """

    def __init__(name: str, module: AnsibleModule):
        """For now, the only attribute the different classes will share it's
        the name of the resource they are trying to query. They will also all
        require access to an AnsibleModule object to run shell commands.
        """
        self.name = name
        self.module = module

    @abc.abstractmethod
    def exists():
        pass

    @abc.abstractmethod
    def query():
        pass

    @abc.abstractmethod
    def get_extra_data():
        """Extra data will be treated as any information that should be returned
        to the user as part of the 'notes' section of the final JSON object.
        """
        pass


class DataSetHandler(FactsHandler):
    """Class that can query facts from a sequential, partitioned (PDS), partitioned
    extended (PDSE), VSAM or generation data sets.
    """

    def __init__(name: str, volume: str, module: AnsibleModule):
        """Create a new handler that will contain the args given and look up
        the type of data set we'll query.
        """
        super(DataSetHandler, self).__init__(name, module)
        self.volume = volume
        self.data_set_type = DataSet.data_set_type(name, volume=volume)
        # Since data_set_type returns None for a non-existent data set,
        # we'll set this value now and avoid another call to the util.
        self.exists = True if self.data_set_type else False

    def exists():
        return self.exists

    def query():
        # Query facts.
        # Format return value.


class QueryException(Exception):
    """Exception class to encapsulate any error the handlers raise while
    trying to query a resource.
    """
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

def get_facts_handler(name: str, resource_type: str, module: AnsibleModule, volume: str = None):
    """Returns the correct handler needed depending on the type of resource
    we will query.
    """
    if resource_type == 'data_set':
        return DataSetHandler(name, volume, module)
    elif resource_type == 'file':
        pass
    elif resource_type == 'aggregate':
        pass


def run_module():
    """Parses the module's options and retrieves facts accordingly.
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True
            },
            'volume': {
                'type': 'str',
                'required': False,
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
            ('type', 'data_set', ('volume',))
        ],
        supports_check_mode=True,
    )

    args_def = {
        'name': {
            'arg_type': 'data_set_or_path',
            'required': True
        },
        'volume': {
            'arg_type': 'str',
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

    name = module.params.get('name')
    volume = module.params.get('volume')
    resource_type = module.params.get('type')

    facts_handler = get_facts_handler(name, resource_type, module, volume)
    result = {}

    if not facts_handler.exists():
        result['msg'] = f'{name} could not be found on the system.'
        module.fail_json(**result)

    try:
        data = facts_handler.query()
        notes = facts_handler.get_extra_data()
    except QueryException as exc:
        result['msg'] = exc.msg
        module.fail_json(**result)

    result['stat'] = data
    result['changed'] = True
    if notes:
        result['notes'] = notes

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
