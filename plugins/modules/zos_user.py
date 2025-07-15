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


def dynamic_dict(contents, dependencies):
    """Validates options that are YAML dictionaries created by a user in a task.

    Parameters
    ----------
        contents: dict
            Content of the option provided by the user.
        dependencies: dict
            Any dependencies the option has.

    Raises
    ------
        ValueError: When something other than a dictionary gets provided.

    Returns
    -------
        dict: Dictionary containing information provided by the user.
    """
    if contents is None:
        return None
    if not isinstance(contents, dict):
        raise ValueError(f'Invalid value {contents}. The option needs a dictionary.')
    for key in contents:
        if isinstance(contents[key], dict):
            raise ValueError(f'Invalid value {contents[key]}. The option does not accept subdictionaries.')
    return contents


def are_blocks_defined(module_params):
    """Checks that there's at least one block of information accompanying an operation.
    It's possible to call the module without actually giving it information about what it needs
    to change, since most options are not required and trying to tell the argument parser to ask
    for at least one block will become too unwieldy with how many operations this module needs
    to handle.

    Parameters
    ----------
        module_params: dict
            All the module parameters specified in the task.

    Returns
    -------
        bool: Whether the module actually has something to do or if it should exit with no changes.
    """
    # All the lists with only 'name' on them indicate an operation that doesn't require any other
    # block to make sense.
    valid_blocks = {
        'group': {
            'create': ['name']
        }
    }

    scope = module_params['scope']
    operation = module_params['operation']

    for block in valid_blocks[scope][operation]:
        if module_params[block] is not None:
            return True

    return False


class RACFHandler():
    """Small class that handles executing RACF TSO commands and RACF utilities.
    """

    def __init__(self, module, module_params):
        """Initializes a new handler with all the context needed to execute RACF
        commands.

        Parameters
        ----------
            module: AnsibleModule
                Object with all the task's context.
            module_params: dict
                Module options specified in the task.
        """
        self.module = module
        self.name = module_params['name']
        self.general = module_params['general']
        self.group = module_params['group']
        self.dfp = module_params['dfp']
        self.omvs = module_params['omvs']
        self.ovm = module_params['ovm']

        self.cmd = None
        self.num_entities_modified = 0
        self.entities_modified = []
        self.database_dumped = False
        self.dump_kept = False
        self.dump_name = None

    def execute_operation(self, operation, scope):
        """Given the operation and scope, it executes a RACF command.

        Parameters
        ----------
            operation: str
                One of 'create', 'list', 'update', 'delete', 'purge', 'connect'
                or 'remove'.
            scope: str
                One of 'user' or 'group'.

        Returns
        -------
            tuple: Return code, standard output and standard error from the command.
        """
        if scope == 'group':
            if operation == 'create':
                rc, stdout, stderr, cmd = self._create_group()

        self.cmd = cmd
        return rc, stdout, stderr

    def _create_group(self):
        """Builds and execute an ADDGROUP command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ADDGROUP command.
        """
        cmd = f'ADDGROUP ({self.name})'

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_group_string()}'.strip()

        # OMVS and OVM blocks won't use the string options since a group only uses one option
        # from both blocks.
        if self.omvs is not None:
            if self.omvs['uid'] == 'auto':
                cmd = f'{cmd} OMVS(AUTOGID)'
            elif self.omvs['uid'] != 'none':
                cmd = f"{cmd} OMVS(GID({self.omvs['custom_uid']})"
                if self.omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
                cmd = f'{cmd})'

        if self.ovm is not None:
            cmd = f"{cmd} OVM(GID({self.ovm['uid']}))"

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _make_general_string(self):
        """Creates a string that defines various common parameters of a profile.

        Returns
        -------
            str: A portion of the parameters of a RACF command.
        """
        cmd = ""

        if self.general is not None:
            if self.general.get('custom_fields') is not None:
                if self.general['custom_fields'].get('add') is not None:
                    custom_fields = self.general['custom_fields']['add']
                    cmd = f'{cmd}CSDATA( '
                    for field in custom_fields:
                        cmd = f'{cmd}{field}({custom_fields[field]}) '
                    cmd = f'{cmd}) '
                elif self.general['custom_fields'].get('delete') is not None:
                    custom_fields = self.general['custom_fields']['delete']
                    cmd = f'{cmd}CSDATA( '
                    for field in custom_fields:
                        cmd = f'{cmd}NO{field.upper()} '
                    cmd = f'{cmd}) '
            if self.general.get('installation_data') is not None:
                cmd = f"{cmd}DATA('{self.general['installation_data']}') "
            if self.general.get('model') is not None:
                cmd = f"{cmd}MODEL({self.general['model']}) "
            if self.general.get('owner') is not None:
                cmd = f"{cmd}OWNER({self.general['owner']}) "

        return cmd

    def _make_group_string(self):
        """Creates a string that defines the GROUP parameters of a profile.

        Returns
        -------
            str: GROUP parameters of a RACF command.
        """
        cmd = ""

        if self.group is not None:
            if self.group.get('superior_group') is not None:
                cmd = f"{cmd}SUPGROUP({self.group['superior_group']}) "
            if self.group.get('terminal_access') is not None:
                terminal_access = 'TERMUACC' if self.group['terminal_access'] else 'NOTERMUACC'
                cmd = f"{cmd}{terminal_access} "
            if self.group.get('universal_group', False):
                cmd = f"{cmd}UNIVERSAL "

        return cmd

    def _make_dfp_substring(self):
        """Creates a string that defines the DFP segment of a profile.

        Returns
        -------
            str: DFP segment of a RACF command.
        """
        cmd = ""

        if self.dfp is not None:
            cmd = f"{cmd}DFP("

            if self.dfp.get('data_app_id') is not None:
                cmd = f"{cmd} DATAAPPL({self.dfp['data_app_id']})"
            if self.dfp.get('data_class') is not None:
                cmd = f"{cmd} DATACLAS({self.dfp['data_class']})"
            if self.dfp.get('management_class') is not None:
                cmd = f"{cmd} MGMTCLAS({self.dfp['management_class']})"
            if self.dfp.get('storage_class') is not None:
                cmd = f"{cmd} STORCLAS({self.dfp['storage_class']})"

            cmd = f"{cmd} )"

        return cmd

    def get_extra_data(self):
        """Returns all ancilliary information computed while executing a command.

        Returns
        -------
            dict: Dictionary containing cmd, num_entities_modified, entities_modified,
                database_dumped, dump_kept and dump_name.
        """
        return {
            'racf_command': self.cmd,
            'num_entities_modified': self.num_entities_modified,
            'entities_modified': self.entities_modified,
            'database_dumped': self.database_dumped,
            'dump_kept': self.dump_kept,
            'dump_name': self.dump_name,
        }


def run_module():
    """Parses the module's options and runs a RACF command.
    """
    module = AnsibleModule(
        argument_spec={
            'name': {
                'type': 'str',
                'required': True,
                'aliases': ['src']
            },
            'operation': {
                'type': 'str',
                'required': True,
                'choices': ['create', 'list', 'update', 'delete', 'purge', 'connect', 'remove']
            },
            'scope': {
                'type': 'str',
                'required': True,
                'choices': ['user', 'group']
            },
            'general': {
                'type': 'dict',
                'required': False,
                'options': {
                    'model': {
                        'type': 'str',
                        'required': False
                    },
                    'owner': {
                        'type': 'str',
                        'required': False
                    },
                    'installation_data': {
                        'type': 'str',
                        'required': False
                    },
                    'custom_fields': {
                        'type': 'dict',
                        'required': False,
                        'mutually_exclusive': [('add', 'delete')],
                        'options': {
                            'add': {
                                'type': 'dict',
                                'required': False
                            },
                            'delete': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            }
                        }
                    }
                }
            },
            'group': {
                'type': 'dict',
                'required': False,
                'options': {
                    'superior_group': {
                        'type': 'str',
                        'required': False
                    },
                    'terminal_access': {
                        'type': 'bool',
                        'required': False
                    },
                    'universal_group': {
                        'type': 'bool',
                        'required': False
                    }
                } 
            },
            'dfp': {
                'type': 'dict',
                'required': False,
                'mutually_exclusive': [
                    ('data_app_id', 'delete'),
                    ('data_class', 'delete'),
                    ('management_class', 'delete'),
                    ('storage_class', 'delete')
                ],
                'options': {
                    'data_app_id': {
                        'type': 'str',
                        'required': False
                    },
                    'data_class': {
                        'type': 'str',
                        'required': False
                    },
                    'management_class': {
                        'type': 'str',
                        'required': False
                    },
                    'storage_class': {
                        'type': 'str',
                        'required': False
                    },
                    'delete': {
                        'type': 'bool',
                        'required': False
                    }
                }
            },
            'omvs': {
                'type': 'dict',
                'required': False,
                'required_if': [
                    ('uid', 'custom', ('custom_uid',)),
                    ('uid', 'shared', ('custom_uid',))
                ],
                'options': {
                    'uid': {
                        'type': 'str',
                        'required': False,
                        'choices': ['auto', 'custom', 'shared', 'none']
                    },
                    'custom_uid': {
                        'type': 'int',
                        'required': False
                    }
                }
            },
            'ovm': {
                'type': 'dict',
                'required': False,
                'options': {
                    'uid': {
                        'type': 'int',
                        'required': False
                    }
                }
            }
        },
        supports_check_mode=True
    )

    args_def = {
        'name': {'arg_type': 'str', 'required': True, 'aliases': ['src']},
        'operation': {'arg_type': 'str', 'required': True},
        'scope': {'arg_type': 'str', 'required': True},
        'general': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'model': {'arg_type': 'str', 'required': False},
                'owner': {'arg_type': 'str', 'required': False},
                'installation_data': {'arg_type': 'str', 'required': False},
                'custom_fields': {
                    'arg_type': 'dict',
                    'required': False,
                    'options': {
                        'add': {'arg_type': dynamic_dict, 'required': False},
                        'delete': {'arg_type': 'list', 'elements': 'str', 'required': False}
                    }
                }
            }
        },
        'group': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'superior_group': {'arg_type': 'str', 'required': False},
                'terminal_access': {'arg_type': 'bool', 'required': False},
                'universal_group': {'arg_type': 'bool', 'required': False}
            }
        },
        'dfp': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'data_app_id': {'arg_type': 'str', 'required': False},
                'data_class': {'arg_type': 'str', 'required': False},
                'management_class': {'arg_type': 'str', 'required': False},
                'storage_class': {'arg_type': 'str', 'required': False},
                'delete': {'arg_type': 'bool', 'required': False}
            }
        },
        'omvs': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'uid': {'arg_type': 'str', 'required': False},
                'custom_uid': {'arg_type': 'int', 'required': False}
            }
        },
        'ovm': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'uid': {'arg_type': 'int', 'required': False}
            }
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

    result = {
        'changed': False,
        'operation': module.params['operation'],
        'racf_command': None,
        'num_entities_modified': 0,
        'entities_modified': [],
        'database_dumped': False,
        'dump_kept': False,
        'dump_name': None
    }

    if not are_blocks_defined(module.params):
        result['msg'] = 'No profile blocks were provided with this operation, no changes made.'
        module.exit_json(**result)

    operation = module.params['operation']
    scope = module.params['scope']
    racf_handler = RACFHandler(module, module.params)

    rc, stdout, stderr = racf_handler.execute_operation(operation, scope)
    result['rc'] = rc
    result['stdout'] = stdout
    result['stdout_lines'] = stdout.split('\n')
    result['stderr'] = stderr
    result['stderr_lines'] = stderr.split('\n')
    result.update(racf_handler.get_extra_data())

    if rc == 0:
        result['changed'] = True
    else:
        module.fail_json(**result)

    module.exit_json(**result)

    # TODO: check that fields are ignored (deleted from the class object) when needed.
    # TODO: add 'delete_block' to custom_fields
    # TODO: add support for check_mode.

if __name__ == '__main__':
    run_module()
