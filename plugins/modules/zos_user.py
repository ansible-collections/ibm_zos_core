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
short_description: Manage user and group profiles in RACF
description:
  - The L(zos_user,./zos_user.html) module executes RACF TSO commands that can manage
    user and group RACF profiles.
  - The module can create, update and delete RACF profiles, as well as list information
    about them.
options:
  name:
    description:
      - Name of the RACF profile the module will operate on.
    type: str
    required: true
    aliases:
      - src
  operation:
    description:
      - RACF command that will be executed.
      - Group profiles can be created, updated, listed, deleted and purged.
      - User profiles can use any of the choices.
      - C(delete) will run a RACF C(DELGROUP) or a C(DELUSER) TSO command. This will
        remove the profile but not every reference in the RACF database.
      - C(purge) will execute the RACF utility IRRDBU00, thereby removing all references
        of a profile from the RACF database.
      - C(connect) will add a given user profile to a group. C(remove) will remove the
        user from a group.
    type: str
    required: true
    choices:
      - create
      - update
      - list
      - delete
      - purge
      - connect
      - remove
  scope:
    description:
      - Whether commands should affect a user or a group profile.
    type: str
    required: true
    choices:
      - user
      - group
  general:
    description:
      - Options that change common attributes in a RACF profile.
    required: false
    type: dict
    suboptions:
      model:
        description:
          - RACF profile that will be used as a model for the profile being changed.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      owner:
        description:
          - Owner of the profile that is being changed.
          - It can be a user or a group profile.
        type: str
        required: false
      installation_data:
        description:
          - Installation-defined data that will be stored in the profile.
          - Maximum length of 255 characters.
          - The module will automatically enclose the contents in single quotation
            marks.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      custom_fields:
        description:
          - Custom fields that will be stored with the profile.
        type: dict
        required: false
        suboptions:
          add:
            description:
              - Adds custom fields to this profile.
              - Each custom field should be a C(key: value) pair.
            type: dict
            required: false
          delete:
            description:
              - Deletes each custom field listed.
            type: list
            elements: str
            required: false
          delete_block:
            description:
              - Delete the whole custom fields block from the profile.
              - This option is only valid when updating profiles, it will be ignored
                when creating one.
              - This option is mutually exclusive with C(add) and C(delete).
            type: bool
            required: required
  group:
    description:
      - Options that change group-specific attributes in a RACF profile.
      - Only valid when changing a group profile, ignored for user profiles.
    required: false
    type: dict
    suboptions:
      superior_group:
        description:
          - Superior group that will be assigned to the profile.
        type: str
        required: false
      terminal_access:
        description:
          - Whether to allow the use of the universal access authority for a
            terminal during authorization checking.
        type: bool
        required: false
      universal_group:
        description:
          - Whether the group should be allowed to have an unlimited number of
            users.
        type: bool
        required: false
  dfp:
    description:
      - Options that set DFP attributes from the Storage Management Subsytem.
    required: false
    type: dict
    suboptions:
      data_app_id:
        description: Name of a DFP data application.
        type: str
        required: false
      data_class:
        description: Default data class for data set allocation.
        type: str
        required: false
      management_class:
        description: Default management class for data set migration and backup.
        type: str
        required: false
      storage_class:
        description: Default storage class for data set space, device and volume.
        type: str
        required: false
      delete:
        description:
          - Delete the whole DFP block from the profile.
          - This option is only valid when updating profiles, it will be ignored
            when creating one.
          - This option is mutually exclusive with every other option in this section.
        type: bool
        required: false
  omvs:
    description:
      - Attributes for how Unix System Services should work under a profile.
    required: false
    type: dict
    suboptions:
      uid:
        description:
          - How RACF should assign a user its UID.
          - C(none) will be ignored when creating a profile.
          - C(custom) and C(shared) require C(custom_uid) too.
        type: str
        required: false
        choices:
          - auto
          - custom
          - shared
          - none
      custom_uid:
        description:
          - Specifies the profile's UID.
          - A number between 0 and 2,147,483,647.
        type: int
        required: false
      delete:
        description:
          - Delete the whole OMVS block from the profile.
          - This option is only valid when updating profiles, it will be ignored
            when creating one.
          - This option is mutually exclusive with every other option in this section.
        type: bool
        required: false

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
  - module: zos_tso_command
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

import copy
import re
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


class RACFHandler():
    """Parent class for group and user RACF operations.
    """
    # These next 4 fields should be overwritten by every subclass. Values here
    # are just an example of the format expected.
    # self.filters has information about what suboptions and options are valid
    # for a certain operation, generally to ignore the rest of the options since
    # they are not needed.
    filters = {
        'operation': {
            'nested': [],
            'flat': []
        }
    }

    # self.valid_blocks has information about what blocks are needed so an operation
    # makes sense.
    valid_blocks = {
        'operation': []
    }

    # self.should_remove_empty_strings tells whether or not deleting entire blocks
    # (what an empty string means in this module) makes sense in an operation, and
    # whether options with this value should be removed.
    should_remove_empty_strings = {}

    # self.validations has information on valid ranges or values for all options
    # that should be validated before running a RACF command.
    # First tuple defines the option/suboption that should be validated.
    # Second element defines the type of validation needed, there is 'format',
    # 'length' and 'range'.
    # Third element (and second tuple) is an argument tuple for the validation.
    validations = [
        # Format validation verifies that a string comes in a specific format.
        # If multiple formats are valid, specify them inside the arg tuple.
        # (('block', 'option'), 'format', ('format1', 'format2')),
        # Length validation verifies that a string contains a certain number
        # of characters. If multiple length ranges are valid, specify each one
        # as a 2-item tuple inside the arg tuple.
        # (('block', 'option', 'suboption'), 'length', ((min, max), (max, max))),
        # Range validation verifies that an integer has a value inside a specific
        # range. A third value in the arg tuple defines a special value that
        # represents deleting the field/block from a profile during update
        # operations.
        # (('block', 'option'), 'range', (min, max, deletion))
    ]

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
        # Standalone params.
        self.name = module_params['name']
        self.operation = module_params['operation']
        self.scope = module_params['scope']
        # Nested params.
        params_copy = copy.deepcopy(module_params)
        del params_copy['name']
        del params_copy['operation']
        del params_copy['scope']
        self.params = params_copy
        # Execution data.
        self.cmd = None
        self.num_entities_modified = 0
        self.entities_modified = []
        self.database_dumped = False
        self.dump_kept = False
        self.dump_name = None
        self.module = module

    def get_state(self):
        """Returns the current values of most fields.

        Returns
        -------
            dict: Dictionary with all fields.
        """
        return {
            'cmd': self.cmd,
            'num_entities_modified': self.num_entities_modified,
            'entities_modified': self.entities_modified,
            'database_dumped': self.database_dumped,
            'dump_kept': self.dump_kept,
            'dump_name': self.dump_name
        }

    def clean_input(self):
        """Removes empty strings and unnecessary options when needed. Modifies self.params.
        """
        if self.should_remove_empty_strings.get(self.operation, False):
            self.remove_empty_strings()
        self.clean_blocks()

    def remove_empty_strings(self):
        """Removes every field that has an empty space from self.params. Empty strings
        in the context of the module cause an entire block from a profile to get deleted.
        This behavior only applies to certain operations, see the values of
        self.should_remove_empty_strings in each subclass.
        """
        for block in self.params:
            if self.params[block] is None:
                continue

            for option in self.params[block]:
                if self.params[block][option] == "":
                    del self.params[block][option]
                elif isinstance(self.params[block][option], dict):
                    for suboption in self.params[block][option]:
                        if self.params[block][option][suboption] == "":
                            del self.params[block][option][suboption]

    def filter_block(self, block, allowed_options):
        """Returns a new dictionary with values from only the allowed
        options for a specific block (group of related suboptions for a profile).

        Parameters
        ----------
            block: dict
                Dictionary containing the suboptions for a specific set of
                attributes a RACF profile should have.
            allowed_options: list
                Suboptions from block that are allowed by an operation.

        Returns
        -------
            dict: Filtered dictionary containing only allowed options.
        """
        if block is not None:
            params = {}
            for option in allowed_options:
                if block.get(option) is not None:
                    params[option] = block[option]
            return params

        return None

    def clean_blocks(self):
        """Deletes unnecessary fields and blocks when an operation doesn't
        need them by using the information in self.filters.
        """
        for block in self.filters[self.operation].get('nested', {}):
            if self.params.get(block[0], {}).get(block[1]) is not None:
                filtered_params = self.filter_block(self.params[block[0]][block[1]], block[2])
                self.params[block[0]][block[1]] = filtered_params if filtered_params else None

        for block in self.filters[self.operation].get('flat', {}):
            if self.params.get(block[0]) is not None:
                filtered_params = self.filter_block(self.params[block[0]], block[1])
                self.params[block[0]] = filtered_params if filtered_params else None

        # Removing empty dictionaries from the parameters.
        clean_params = copy.deepcopy(self.params)
        for block in self.params:
            if self.params[block] is None:
                del clean_params[block]
                continue

            for option in self.params[block]:
                if self.params[block][option] is None:
                    del clean_params[block][option]

        self.params = clean_params

    def are_blocks_defined(self):
        """Checks that there's at least one block of information accompanying an operation.
        It's possible to call the module without actually giving it information about what it needs
        to change, since most options are not required and trying to tell the argument parser to ask
        for at least one block will become too unwieldy with how many operations this module needs
        to handle.

        Returns
        -------
            bool: Whether the module actually has something to do or if it should exit with no changes.
        """
        if len(self.valid_blocks[self.operation]) == 0:
            return True

        for block in self.valid_blocks[self.operation]:
            if self.params[block] is not None:
                return True

        return False

    def validate_params(self):
        """Uses self.validations to validate that all parameters are withing valid ranges
        or have valid values.

        Raises
        ------
            ValueError: When a parameter has an invalid value.
        """
        def validate_format(value, formats):
            for str_format in formats:
                if re.fullmatch(str_format, value) is not None:
                    return True

            return False

        def validate_length(value, lengths):
            for (min_length, max_length) in lengths:
                if len(value) >= min_length and len(value) <= max_length:
                    return True

            return False

        def validate_range(value, valid_range):
            min_value = valid_range[0]
            max_value = valid_range[1]
            deletion_value = valid_range[2]

            if (min_value <= value <= max_value) or value == deletion_value:
                return True

            return False

        for validation in self.validations:
            option = validation[0]
            if len(option) == 2:
                value = self.params.get(option[0], {}).get(option[1])
                option_name = f'{option[0]}.{option[1]}'
            else:
                value = self.params.get(option[0], {}).get(option[1], {}).get(option[2])
                option_name = f'{option[0]}.{option[1]}.{option[2]}'

            if value is None:
                continue

            if validation[1] == 'format':
                if validate_format(value, validation[2]):
                    continue
            elif validation[1] == 'length':
                if validate_length(value, validation[2]):
                    continue
            elif validation[1] == 'range':
                if validate_range(value, validation[2]):
                    continue

            # When having valid option values, we should never reach this line.
            raise ValueError(f'Option {option_name} has an invalid value, please check your task.')

    def execute_operation(self):
        """This method should handle all calls to RACF operations inside a subclass.

        Returns
        -------
            dict: Dictionary containing RC, stdout, stderr from the RACF command executed,
            as well as the command string, self.num_entities_modified, self.entities_modified,
            self.database_dumped, self.dump_kept and self.dump_name.
        """
        return self.get_state()

    def _make_general_string(self):
        """Creates a string that defines various common parameters of a profile.

        Returns
        -------
            str: A portion of the parameters of a RACF command.
        """
        cmd = ""
        general = self.params.get('general')

        if general is not None:
            if general.get('custom_fields') is not None:
                if general['custom_fields'].get('add') is not None:
                    custom_fields = general['custom_fields']['add']
                    cmd = f'{cmd}CSDATA( '
                    for field in custom_fields:
                        cmd = f'{cmd}{field}({custom_fields[field]}) '
                    cmd = f'{cmd}) '
                elif general['custom_fields'].get('delete') is not None:
                    custom_fields = general['custom_fields']['delete']
                    cmd = f'{cmd}CSDATA( '
                    for field in custom_fields:
                        cmd = f'{cmd}NO{field.upper()} '
                    cmd = f'{cmd}) '
                elif general['custom_fields'].get('delete_block') is not None:
                    cmd = f'{cmd}NOCSDATA '
            if general.get('installation_data') is not None:
                if general.get('installation_data') != "":
                    cmd = f"{cmd}DATA('{general['installation_data']}') "
                else:
                    cmd = f"{cmd}NODATA "
            if general.get('model') is not None:
                if general.get('model') != "":
                    cmd = f"{cmd}MODEL({general['model']}) "
                else:
                    cmd = f"{cmd}NOMODEL "
            if general.get('owner') is not None and general.get('owner') != "":
                cmd = f"{cmd}OWNER({general['owner']}) "

        return cmd

    def _make_dfp_substring(self):
        """Creates a string that defines the DFP segment of a profile.

        Returns
        -------
            str: DFP segment of a RACF command.
        """
        cmd = ""
        dfp = self.params.get('dfp')

        if dfp is not None:
            cmd = f"{cmd}DFP("

            if dfp.get('data_app_id') is not None:
                if dfp.get('data_app_id') != "":
                    cmd = f"{cmd} DATAAPPL({dfp['data_app_id']})"
                else:
                    cmd = f"{cmd} NODATAAPPL"
            if dfp.get('data_class') is not None:
                if dfp.get('data_class') != "":
                    cmd = f"{cmd} DATACLAS({dfp['data_class']})"
                else:
                    cmd = f"{cmd} NODATACLAS"
            if dfp.get('management_class') is not None:
                if dfp.get('management_class') != "":
                    cmd = f"{cmd} MGMTCLAS({dfp['management_class']})"
                else:
                    cmd = f"{cmd} NOMGMTCLAS"
            if dfp.get('storage_class') is not None:
                if dfp.get('storage_class') != "":
                    cmd = f"{cmd} STORCLAS({dfp['storage_class']})"
                else:
                    cmd = f"{cmd} NOSTORCLAS"

            cmd = f"{cmd} )"

        return cmd


class GroupHandler(RACFHandler):
    """Subclass containing all information needed to clean, validate and execute
    RACF commands affecting group profiles.
    """
    filters = {
        'create': {
            'nested': [
                ('general', 'custom_fields', ('add',))
            ],
            'flat': [
                ('omvs', ('uid', 'custom_uid')),
                ('dfp', ('data_app_id', 'data_class', 'storage_class', 'management_class'))
            ]
        },
        'update': {
            'flat': [
                ('omvs', ('uid', 'custom_uid')),
            ]
        },
        'delete': {},
        'purge': {},
        'list': {}
    }

    should_remove_empty_strings = {
        'create': True,
        'update': False,
        'delete': False,
        'purge': False,
        'list': False
    }

    # All empty lists indicate an operation that doesn't require any other
    # block to make sense.
    valid_blocks = {
        'create': [],
        'update': ['general', 'group', 'dfp', 'omvs'],
        'delete': [],
        'purge': [],
        'list': []
    }

    validations = [
        (('general', 'installation_data'), 'length', ((0, 255),)),
        (('dfp', 'data_app_id'), 'length', ((0, 8),)),
        (('dfp', 'data_class'), 'length', ((0, 8),)),
        (('dfp', 'management_class'), 'length', ((0, 8),)),
        (('dfp', 'storage_class'), 'length', ((0, 8),)),
        (('omvs', 'custom_uid'), 'range', (0, 2_147_483_647, 0)),
    ]

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
        super().__init__(module, module_params)

        # Removing all block params since these operations only need the
        # name.
        if self.operation in ['delete', 'purge', 'list']:
            self.params = {}

    def execute_operation(self):
        """Given the operation and scope, it executes a RACF command.

        Returns
        -------
            tuple: Return code, standard output and standard error from the command.
        """
        if self.operation == 'create':
            rc, stdout, stderr, cmd = self._create_group()
        if self.operation == 'update':
            rc, stdout, stderr, cmd = self._update_group()
        if self.operation == 'delete':
            rc, stdout, stderr, cmd = self._delete_group()

        self.cmd = cmd
        # Getting the base dictionary.
        result = super().execute_operation()
        result['rc'] = rc
        result['stdout'] = stdout
        result['stderr'] = stderr
        return result

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

        # The OMVS block won't use the string methods since a group only uses one option
        # from it.
        omvs = self.params.get('omvs')
        if omvs is not None:
            if omvs.get('uid') == 'auto':
                cmd = f'{cmd} OMVS(AUTOGID)'
            elif omvs.get('uid') != 'none':
                cmd = f"{cmd} OMVS(GID({omvs['custom_uid']})"
                if omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
                cmd = f'{cmd})'

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _update_group(self):
        """Builds and execute an ALTGROUP command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ALTGROUP command.
        """
        cmd = f'ALTGROUP ({self.name})'

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_group_string()}'.strip()

        # The OMVS block won't use the string options since a group only uses one option
        # from it.
        omvs = self.params.get('omvs')
        if omvs is not None:
            if omvs.get('delete'):
                cmd = f'{cmd} NOOMVS'

            if omvs.get('uid') == 'auto':
                cmd = f'{cmd} OMVS(AUTOGID)'
            elif omvs.get('uid') != 'none':
                cmd = f"{cmd} OMVS(GID({omvs['custom_uid']})"
                if omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
                cmd = f'{cmd})'
            else:
                cmd = f'{cmd} OMVS(NOGID)'

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _delete_group(self):
        """Builds and execute a DELGROUP command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the DELGROUP command.
        """
        cmd = f'DELGROUP ({self.name})'
        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _make_group_string(self):
        """Creates a string that defines the GROUP parameters of a profile.

        Returns
        -------
            str: GROUP parameters of a RACF command.
        """
        cmd = ""
        group = self.params.get('group')

        if group is not None:
            if group.get('superior_group') is not None:
                cmd = f"{cmd}SUPGROUP({group['superior_group']}) "
            if group.get('terminal_access') is not None:
                terminal_access = 'TERMUACC' if group['terminal_access'] else 'NOTERMUACC'
                cmd = f"{cmd}{terminal_access} "
            if group.get('universal_group', False):
                cmd = f"{cmd}UNIVERSAL "

        return cmd


class UserHandler(RACFHandler):
    """Subclass containing all information needed to clean, validate and execute
    RACF commands affecting user profiles.
    """
    filters = {
        'create': {
            'nested': [
                ('general', 'custom_fields', ('add',))
            ],
            'flat': [
                ('dfp', ('data_app_id', 'data_class', 'storage_class', 'management_class')),
                ('language', ('primary', 'secondary')),
                ('omvs', ('uid', 'custom_uid', 'home', 'program', 'nonshared_size', 'shared_size', 'addr_space_size', 'map_size', 'max_procs', 'max_threads', 'max_cpu_time', 'max_files')),
                ('tso', ('account_num', 'logon_cmd', 'logon_proc', 'dest_id', 'hold_class', 'job_class', 'msg_class', 'sysout_class', 'region_size', 'max_region_size', 'security_label', 'unit_name', 'user_data'))
            ]
        },
        'update': {},
        'delete': {},
        'purge': {},
        'list': {}
    }

    should_remove_empty_strings = {
        'create': True,
        'update': False,
        'delete': False,
        'purge': False,
        'list': False
    }

    # All empty lists indicate an operation that doesn't require any other
    # block to make sense.
    valid_blocks = {
        'create': [],
        'update': ['general', 'group', 'dfp', 'language', 'omvs'],
        'delete': [],
        'purge': [],
        'list': []
    }

    validations = [
        (('general', 'installation_data'), 'length', ((0, 255),)),
        (('dfp', 'data_app_id'), 'length', ((0, 8),)),
        (('dfp', 'data_class'), 'length', ((0, 8),)),
        (('dfp', 'management_class'), 'length', ((0, 8),)),
        (('dfp', 'storage_class'), 'length', ((0, 8),)),
        (('language', 'primary'), 'format', ('[a-zA-Z]{3}', '[a-zA-Z]{0, 24}')),
        (('language', 'secondary'), 'format', ('[a-zA-Z]{3}', '[a-zA-Z]{0, 24}')),
        (('omvs', 'custom_uid'), 'range', (0, 2_147_483_647, 0)),
        (('omvs', 'home'), 'length', ((0, 1023),)),
        (('omvs', 'program'), 'length', ((0, 1023),)),
        (('omvs', 'addr_space_size'), 'range', (10_485_760, 2_147_483_647, 0)),
        (('omvs', 'map_size'), 'range', (1, 16_777_216, 0)),
        (('omvs', 'max_procs'), 'range', (3, 32_767, 0)),
        (('omvs', 'max_threads'), 'range', (0, 100_000, -1)),
        (('omvs', 'max_cpu_time'), 'range', (7, 2_147_483_647, 0)),
        (('omvs', 'max_files'), 'range', (3, 524_287, 0)),
        (('tso', 'account_num'), 'length', ((0, 39),)),
        (('tso', 'logon_cmd'), 'length', ((0, 80),)),
        (('tso', 'logon_proc'), 'length', ((0, 8),)),
        (('tso', 'dest_id'), 'length', ((0, 7),)),
        (('tso', 'hold_class'), 'length', ((0, 1),)),
        (('tso', 'job_class'), 'length', ((0, 1),)),
        (('tso', 'msg_class'), 'length', ((0, 1),)),
        (('tso', 'sysout_class'), 'length', ((0, 1),)),
        (('tso', 'region_size'), 'range', (0, 2_096_128, -1)),
        (('tso', 'max_region_size'), 'range', (0, 2_096_128, -1)),
        (('tso', 'unit_name'), 'length', ((0, 8),)),
        (('tso', 'user_data'), 'format', ('[^\s*$]|[0-9a-zA-Z]{4}',)),
    ]

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
        super().__init__(module, module_params)

        # Removing all block params since these operations only need the
        # name.
        if self.operation in ['delete', 'purge', 'list']:
            self.params = {}

    def execute_operation(self):
        """Given the operation and scope, it executes a RACF command.

        Returns
        -------
            tuple: Return code, standard output and standard error from the command.
        """
        if self.operation == 'create':
            rc, stdout, stderr, cmd = self._create_user()
        if self.operation == 'update':
            rc, stdout, stderr, cmd = self._update_user()
        if self.operation == 'delete':
            rc, stdout, stderr, cmd = self._delete_user()

        self.cmd = cmd
        # Getting the base dictionary.
        result = super().execute_operation()
        result['rc'] = rc
        result['stdout'] = stdout
        result['stderr'] = stderr
        return result

    def _create_user(self):
        """Builds and execute an ADDUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ADDUSER command.
        """
        cmd = f'ADDUSER ({self.name})'

        # TODO: add language
        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()

        # The OMVS block won't use the string methods since a group only uses one option
        # from it.
        omvs = self.params.get('omvs')
        if omvs is not None:
            if omvs.get('uid') == 'auto':
                cmd = f'{cmd} OMVS(AUTOGID)'
            elif omvs.get('uid') != 'none':
                cmd = f"{cmd} OMVS(GID({omvs['custom_uid']})"
                if omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
                cmd = f'{cmd})'

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _update_user(self):
        """Builds and execute an ALTUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ALTUSER command.
        """
        pass

    def _delete_user(self):
        """Builds and execute a DELUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the DELUSER command.
        """
        cmd = f'DELUSER ({self.name})'
        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd


def get_racf_handler(module, module_params):
    """Returns the correct handler needed for the scope and operation given in a task.

    Parameters
    ----------
        module: AnsibleModule
            Object with all the task's context.
        module_params: dict
            Module options specified in the task.

    Returns
    -------
        RACFHandler: Object with the necessary context to execute a RACF command.
    """
    if module_params['scope'] == 'group':
        return GroupHandler(module, module_params)
    elif module_params['scope'] == 'user':
        return UserHandler(module, module_params)


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
                        'mutually_exclusive': [
                            ('add', 'delete'),
                            ('add', 'delete_block'),
                            ('delete', 'delete_block')
                        ],
                        'options': {
                            'add': {
                                'type': 'dict',
                                'required': False
                            },
                            'delete': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                            'delete_block': {
                                'type': 'bool',
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
            'language': {
                'type': 'dict',
                'required': False,
                'mutually_exclusive': [
                    ('primary', 'delete'),
                    ('secondary', 'delete')
                ],
                'options': {
                    'primary': {
                        'type': 'str',
                        'required': False
                    },
                    'secondary': {
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
                'mutually_exclusive': [
                    ('uid', 'delete'),
                    ('custom_uid', 'delete'),
                    ('home', 'delete'),
                    ('program', 'delete'),
                    ('nonshared_size', 'delete'),
                    ('shared_size', 'delete'),
                    ('addr_space_size', 'delete'),
                    ('map_size', 'delete'),
                    ('max_procs', 'delete'),
                    ('max_threads', 'delete'),
                    ('max_cpu_time', 'delete'),
                    ('max_files', 'delete')
                ],
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
                    },
                    'home': {
                        'type': 'str',
                        'required': False
                    },
                    'program': {
                        'type': 'int',
                        'required': False
                    },
                    # TODO: add validation for this one
                    'nonshared_size': {
                        'type': 'str',
                        'required': False
                    },
                    # TODO: add validation for this one
                    'shared_size': {
                        'type': 'str',
                        'required': False
                    },
                    'addr_space_size': {
                        'type': 'int',
                        'required': False
                    },
                    'map_size': {
                        'type': 'int',
                        'required': False
                    },
                    'max_procs': {
                        'type': 'int',
                        'required': False
                    },
                    'max_threads': {
                        'type': 'int',
                        'required': False
                    },
                    'max_cpu_time': {
                        'type': 'int',
                        'required': False
                    },
                    'max_files': {
                        'type': 'int',
                        'required': False
                    },
                    'delete': {
                        'type': 'bool',
                        'required': False
                    }
                }
            },
            'tso': {
                'type': 'dict',
                'required': False,
                'mutually_exclusive': [
                    ('account_num', 'delete'),
                    ('logon_cmd', 'delete'),
                    ('logon_proc', 'delete'),
                    ('dest_id', 'delete'),
                    ('hold_class', 'delete'),
                    ('job_class', 'delete'),
                    ('msg_class', 'delete'),
                    ('sysout_class', 'delete'),
                    ('region_size', 'delete'),
                    ('max_region_size', 'delete'),
                    ('security_label', 'delete'),
                    ('unit_name', 'delete'),
                    ('user_data', 'delete'),
                ],
                'options': {
                    'account_num': {
                        'type': 'str',
                        'required': False
                    },
                    'logon_cmd': {
                        'type': 'str',
                        'required': False
                    },
                    'logon_proc': {
                        'type': 'str',
                        'required': False
                    },
                    'dest_id': {
                        'type': 'str',
                        'required': False
                    },
                    'hold_class': {
                        'type': 'str',
                        'required': False
                    },
                    'job_class': {
                        'type': 'str',
                        'required': False
                    },
                    'msg_class': {
                        'type': 'str',
                        'required': False
                    },
                    'sysout_class': {
                        'type': 'str',
                        'required': False
                    },
                    'region_size': {
                        'type': 'int',
                        'required': False
                    },
                    'max_region_size': {
                        'type': 'int',
                        'required': False
                    },
                    'security_label': {
                        'type': 'str',
                        'required': False
                    },
                    'unit_name': {
                        'type': 'str',
                        'required': False
                    },
                    'user_data': {
                        'type': 'str',
                        'required': False
                    },
                    'delete': {
                        'type': 'bool',
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
                        'delete': {'arg_type': 'list', 'elements': 'str', 'required': False},
                        'delete_block': {'arg_type': 'bool', 'required': False}
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
        'language': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'primary': {'arg_type': 'str', 'required': False},
                'secondary': {'arg_type': 'str', 'required': False},
                'delete': {'arg_type': 'bool', 'required': False}
            }
        },
        'omvs': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'uid': {'arg_type': 'str', 'required': False},
                'custom_uid': {'arg_type': 'int', 'required': False},
                'home': {'arg_type': 'path', 'required': False},
                'program': {'arg_type': 'path', 'required': False},
                'nonshared_size': {'arg_type': 'str', 'required': False},
                'shared_size': {'arg_type': 'str', 'required': False},
                'addr_space_size': {'arg_type': 'int', 'required': False},
                'map_size': {'arg_type': 'int', 'required': False},
                'max_procs': {'arg_type': 'int', 'required': False},
                'max_threads': {'arg_type': 'int', 'required': False},
                'max_cpu_time': {'arg_type': 'int', 'required': False},
                'max_files': {'arg_type': 'int', 'required': False},
                'delete': {'arg_type': 'bool', 'required': False}
            }
        },
        'tso': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'account_num': {'arg_type': 'str', 'required': False},
                'logon_cmd': {'arg_type': 'str', 'required': False},
                'logon_proc': {'arg_type': 'str', 'required': False},
                'dest_id': {'arg_type': 'str', 'required': False},
                'hold_class': {'arg_type': 'str', 'required': False},
                'job_class': {'arg_type': 'str', 'required': False},
                'msg_class': {'arg_type': 'str', 'required': False},
                'sysout_class': {'arg_type': 'str', 'required': False},
                'region_size': {'arg_type': 'int', 'required': False},
                'max_region_size': {'arg_type': 'int', 'required': False},
                'security_label': {'arg_type': 'str', 'required': False},
                'unit_name': {'arg_type': 'str', 'required': False},
                'user_data': {'arg_type': 'str', 'required': False},
                'delete': {'arg_type': 'bool', 'required': False}
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

    # TODO: add support for check_mode.
    operation_handler = get_racf_handler(module, module.params)
    operation_handler.clean_input()
    if not operation_handler.are_blocks_defined():
        result = operation_handler.get_state()
        result['msg'] = 'No profile blocks were provided with this operation, no changes made.'
        module.exit_json(**result)

    try:
        operation_handler.validate_params()
    except ValueError as err:
        result['msg'] = str(err)
        module.fail_json(**result)

    result = operation_handler.execute_operation()
    result['stdout_lines'] = result['stdout'].split('\n')
    result['stderr_lines'] = result['stderr'].split('\n')

    if result['rc'] == 0:
        result['changed'] = True
    else:
        result['msg'] = 'An error ocurred while executing the RACF command.'
        module.fail_json(**result)

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
