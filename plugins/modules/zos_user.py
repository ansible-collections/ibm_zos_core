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
  language:
    description:
      - Options that set the preferred national languages for a user profile.
      - These options will override the system-wide defaults.
    required: false
    type: dict
    suboptions:
      primary:
        description:
          - User's primary language.
          - Value should be either a 3 character-long language code or an
            installation-defined name of up to 24 characters.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      secondary:
        description:
          - User's secondary language.
          - Value should be either a 3 character-long language code or an
            installation-defined name of up to 24 characters.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      delete:
        description:
          - Delete the whole LANGUAGE block from the profile.
          - This option is only valid when updating user profiles, it will be ignored
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
      home:
        description:
          - Path name for the z/OS Unix System Services home directory.
          - Maximum length of 1023 characters.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      program:
        description:
          - Path of the shell program to use when the user logs in.
          - Maximum length of 1023 characters.
          - An empty string will delete this field from the profile.
        type: str
        required: false
      nonshared_size:
        description:
          - Maximum number of bytes of nonshared memory that can be allocated
            by the user.
          - Must be a number between 0 and 16,777,215 subfixed by one of the
            following units: m (megabytes), g (gigabytes), t (terabytes) or
            p (petabytes).
          - An empty string will delete the current limit set.
        type: str
        required: false
      shared_size:
        description:
          - Maximum number of bytes of shared memory that can be allocated
            by the user.
          - Must be a number between 1 and 16,777,215 subfixed by one of the
            following units: m (megabytes), g (gigabytes), t (terabytes) or
            p (petabytes).
          - An empty string will delete the current limit set.
        type: str
        required: false
      addr_space_size:
        description:
          - Address space region size in bytes.
          - Value between 10,485,760 and 2,147,483,647.
          - A value of 0 will delete this field from the profile.
        type: int
        required: false
      map_size:
        description:
          - Maximum amount of data space storage that can be allocated by
            the user.
          - This option represents the number of memory pages, not bytes,
            available.
          - Value between 1 and 16,777,216.
          - A value of 0 will delete this field from the profile.
        type: int
        required: false
      max_procs:
        description:
          - Maximum number of processes the user is allowed to have active
            at the same time.
          - Value between 3 and 32,767.
          - A value of 0 will delete this field from the profile.
        type: int
        required: false
      max_threads:
        description:
          - Maximum number of threads the user can have concurrently active.
          - Value between 0 and 100,000.
          - A value of -1 will delete this field from the profile.
        type: int
        required: false
      max_cpu_time:
        description:
          - Specifies the RLIMIT_CPU hard limit. Indicates the cpu-time that a
            user process is allowed to use.
          - Value between 7 and 2,147,483,647 seconds.
          - A value of 0 will delete this field from the profile.
        type: int
        required: false
      max_files:
        description:
          - Maximum number of files the user is allowed to have concurrently
            active or open.
          - Value between 3 and 524,287.
          - A value of 0 will delete this field from the profile.
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
  tso:
    description:
      - Attributes for how TSO should handle a user profile.
    required: false
    type: dict
    suboptions:
      account_num:
        description:
          - User's default TSO account number when logging in.
          - Value between 3 and 524,287.
          - A value of 0 will delete this field from the profile.
        type: int
        required: false
      delete:
        description:
          - Delete the whole TSO block from the profile.
          - This option is only valid when updating profiles, it will be ignored
            when creating one.
          - This option is mutually exclusive with every other option in this section.
        type: bool
        required: false
  connect:
    description:
      -
    required: false
    type: dict
    suboptions:
  access:
    description:
      - Options that set different security attributes in a user profile.
    required: false
    type: dict
    suboptions:
      default_group:
        description:
          - RACF's default group for the user profile.
        type: str
        required: false
      clauth:
        description:
          - Classes in which a user is allowed to define profiles to RACF for protection.
        type: dict
        required: false
        suboptions:
          add:
            description:
              - Adds classes to the profile.
            type: list
            elements: str
            required: false
          delete:
            description:
              - Removes classes from the profile.
            type: list
            elements: str
            required: false
      roaudit:
        description:
          - Whether a user should have full responsibility for auditing the use of system
            resources.
        type: bool
        required: false
      category:
        description:
          - Security categories that the profile should have.
        type: dict
        required: false
        suboptions:
          add:
            description:
              - Adds security categories to the profile.
            type: list
            elements: str
            required: false
          delete:
            description:
              - Removes security categories from the profile.
            type: list
            elements: str
            required: false
      operator_card:
        description:
          - Whether a user must supply an operator identification card when logging in.
        type: bool
        required: false
      maintenance_access:
        description:
          - Whether the user has authorization to do maintenance operations on all
            RACF-protected DASD data sets, tape volumes, and DASD volumes.
        type: bool
        required: false
      restricted:
        description:
          - Whether to give the profile the RESTRICTED attribute.
        type: bool
        required: false
      security_label:
        description:
          - Security label applied to the profile.
          - Empty value deletes this field.
        type: str
        required: false
      security_level:
        description:
          - Security level applied to the profile.
          - Empty value deletes this field.
        type: str
        required: false
  operator:
    description:
      - Attributes used when a user establishes an extended MCS
        console session.
    required: false
    type: dict
    suboptions:
      alt_group:
        description:
          - Console group used in recovery.
          - Must be between 1 and 8 characters in length.
          - Empty value deletes this field.
        type: str
        required: false
      authority:
        description:
          - Console's authority to issue operator commands.
          - C(delete) will remove the field from the profile.
        type: str
        required: false
        choices:
          - master
          - all
          - info
          - cons
          - io
          - sys
          - delete
      cmd_system:
        description:
          - System to which commands from this console are to
            be sent.
          - Must be between 1 and 8 characters in length.
          - Empty value deletes this field.
        type: str
        required: false
      search_key:
        description:
          - Name used to display information for all consoles
            with the specified key by using the MVS command
            C(DISPLAY CONSOLES,KEY).
          - Must be between 1 and 8 characters in length.
          - Empty value deletes this field.
        type: str
        required: false
      migration_id:
        description:
          - Whether a 1-byte migration ID should be assigned to
            this console.
        type: bool
        required: false
      display:
        description:
          - Which information should be displayed when monitoring
            jobs, TSO sessions, or data set status.
          - Possible values are C(jobnames), C(jobnamest), C(sess),
            C(sesst), C(status) and C(delete).
          - Multiple choices are allowed.
          - C(delete) will remove this field from the profile.
        type: str
        required: false
        default: ['jobnames', 'sess']
      msg_level:
        description:
          - Specifies the messages that this console is to receive.
          - C(delete) will remove this field from the profile.
        type: str
        required: false
        choices:
          - nb
          - all
          - r
          - i
          - ce
          - e
          - in
          - delete
      msg_format:
        description:
          - Format in which messages are displayed at the console.
          - C(delete) will remove this field from the profile.
        type: str
        required: false
        choices:
          - j
          - m
          - s
          - t
          - x
          - delete
      msg_storage:
        description:
          - Specifies the amount of storage in the TSO/E user's address
            space that can be used for message queuing to the console.
          - Its value can be a number between 1 and 2,000.
          - A value of 0 deletes this field.
        type: int
        required: false
      msg_scope:
        description:
          - Systems from which this console can receive messages that
            are not directed to a specific console.
        type: dict
        required: false
        suboptions:
          add:
            description:
              - Add new systems to this field.
            type: list
            elements: str
            required: false
          remove:
            description:
              - Removes systems from this field.
            type: list
            elements: str
            required: false
          delete:
            description:
              - Deletes this field from the profile.
              - Mutually exclusive with the rest of the options
                in this section.
            type: bool
            required: false
      automated_msgs:
        description:
          - Whether the extended console can receive messages
            that have been automated by the MFP.
        type: bool
        required: false
      del_msgs:
        description:
          - Which delete operator message (DOM) requests the
            console can receive.
          - C(delete) will remove the field from the profile.
        type: str
        required: false
        choices:
          - normal
          - all
          - none
          - delete
      hardcopy_msgs:
        description:
          - Whether the console should receive all messages
            that are directed to hardcopy.
        type: bool
        required: false
      internal_msgs:
        description:
          - Whether the console should receive messages that
            are directed to console ID zero.
        type: bool
        required: false
      routing_msgs:
        description:
          - Specifies the routing codes of messages this
            operator is to receive.
          - C(ALL) can be specified to receive all codes. Conversely,
            C(NONE) can be used to receive none.
        type: list
        elements: str
        required: false
      undelivered_msgs:
        description:
          - Whether the console should receive undelivered
            messages.
        type: bool
        required: false
      unknown_msgs:
        description:
          - Whether the console should receive messages that
            are directed to unknown console IDs.
        type: bool
        required: false
      responses:
        description:
          - Whether command responses should be logged.
        type: bool
        required: false
      delete:
        description:
          - Delete the whole OPERPARM block from the profile.
          - This option is only valid when updating profiles, it will be ignored
            when creating one.
          - This option is mutually exclusive with every other option in this section.
        type: bool
        required: false
  restrictions:
    description:
      - Attributes that determine the days and times a user is
        allowed to login.
    required: false
    type: dict
    suboptions:
      days:
        description:
          - Days of the week that a user is allowed to login.
          - Multiple choices are allowed.
          - Valid values are C(anyday), C(weekdays), C(monday), C(tuesday),
            C(wednesday), C(thursday), C(friday), C(saturday) and C(sunday).
        type: list
        elements: str
        required: false
      time:
        description:
          - Daily time period when the user is allowed to login.
          - The value for this option must be in the format HHMM:HHMM.
          - This field uses a 24-hour format.
          - This field also accepts the value C(anytime) to indicate a
            user is free to login at any time of the day.
        type: str
        required: false
      resume:
        description:
          - Date when the user is allowed access to a system again.
          - The value for this option must be in the format MM/DD/YY,
            where C(YY) are the last two digits of the year.
        type: str
        required: false
      delete_resume:
        description:
          - Delete the resume field from the profile.
          - This option is only valid when connecting a user to a group.
          - This option is mutually exclusive with I(resume).
        type: bool
        required: false
      revoke:
        description:
          - Date when the user is forbidden access to a system.
          - The value for this option must be in the format MM/DD/YY,
            where C(YY) are the last two digits of the year.
        type: str
        required: false
      delete_revoke:
        description:
          - Delete the revoke field from the profile.
          - This option is only valid when connecting a user to a group.
          - This option is mutually exclusive with I(revoke).
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
- name: Create a new group profile using RACF defaults.
  zos_user:
    name: newgrp
    operation: create
    scope: group

- name: Create a new group profile using another group as a model and setting its owner.
  zos_user:
    name: newgrp
    operation: create
    scope: group
    general:
      model: oldgrp
      owner: admin

- name: Create a new group profile and set group attributes.
  zos_user:
    name: newgrp
    operation: create
    scope: group
    group:
      superior_group: sys1
      terminal_access: true
      universal_group: false

- name: Update a group profile to change its installation data and remove custom fields.
  zos_user:
    name: usergrp
    operation: update
    scope: group
    general:
      installation_data: New installation data
      custom_fields:
        delete_block: true

- name: Create a user using RACF defaults.
  zos_user:
    name: newuser
    operation: create
    scope: user

- name: Create a user using another profile as a model.
  zos_user:
    name: newuser
    operation: create
    scope: user
    general:
      model: olduser

- name: Create a user and set how Unix System Services should behave when it logs in.
  zos_user:
    name: newuser
    operation: create
    scope: user
    omvs:
      uid: auto
      home: /u/newuser
      program: /bin/sh
      nonshared_size: '10g'
      shared_size: '10g'
      addr_space_size: 10485760
      map_size: 2056
      max_procs: 16
      max_threads: 150
      max_cpu_time: 4096
      max_files: 4096

- name: Create a user and set access permissions to it.
  zos_user:
    name: newuser
    operation: create
    scope: user
    access:
      default_group: usergrp
      roaudit: true
      operator_card: false
      maintenance_access: true
      restricted: false
    restrictions:
      days:
        - monday
        - tuesday
        - wednesday
      time: anytime

- name: Update a user profile to change its TSO attributes and owner.
  zos_user:
    name: user
    operation: create
    scope: user
    general:
      owner: admin
    tso:
      hold_class: K
      job_class: K
      msg_class: K
      sysout_class: K
      region_size: 2048
      max_region_size: 4096

- name: Connect a user to a group using RACF defaults.
  zos_user:
    name: user
    operation: connect
    scope: user
    connect:
      group_name: usergrp

- name: Connect a user to a group and give it special permissions.
  zos_user:
    name: user
    operation: connect
    scope: user
    connect:
      group_name: usergrp
      authority: connect
      universal_access: alter
      group_account: true
      group_operations: true
      auditor: true
      adsp_attribute: true
      special: true

- name: Remove a user from a group.
  zos_user:
    name: user
    operation: remove
    scope: user
    connect:
      group_name: usergrp

- name: Delete a user from the RACF database.
  zos_user:
    name: user
    operation: delete
    scope: user

- name: Delete group from the RACF database.
  zos_user:
    name: usergrp
    operation: delete
    scope: group
"""

RETURN = r"""
operation:
    description: Operation that was performed by the module.
    returned: always
    type: str
    sample: create
racf_command:
    description: Full command string that was executed with tsocmd.
    returned: success
    type: str
    sample: "DELUSER (user)"
num_entities_modified:
    description: Number of profiles and references modified by the operation.
    returned: always
    type: int
    sample: 1
entities_modified:
    description: List of all profiles and references modified by the operation.
    returned: success
    type: list
    elements: str
    sample: ['user']
database_dumped:
    description: Whether the module used IRRRID00 to dump the RACF database.
    returned: always
    type: bool
    sample: false
dump_kept:
    description: Whether the RACF database dump was kept on the managed node.
    returned: always
    type: bool
    sample: false
dump_name:
    description: Name of the database containing the output from the IRRRID00 utility.
    returned: success
    type: str
    sample: USER.BACKUP.RACF.DATABASE
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


def multiple_choice_display(contents, dependencies):
    """Validates multiple choices for the operator.display option.

    Parameters
    ----------
        contents: Union[str, list[str]]
                 The contents of the choice argument.
        dependencies: dict
                     Any arguments this argument is dependent on.

    Raises
    -------
        ValueError: str
                   When an invalid argument provided.

    Returns
    -------
        list: List containing each choice selected.
    """
    allowed_values = {
        'jobnames',
        'jobnamest',
        'sess',
        'sesst',
        'status',
        'delete'
    }

    if not contents:
        return None
    if not isinstance(contents, list):
        contents = [contents]
    for value in contents:
        if value not in allowed_values:
            raise ValueError(f'Invalid argument "{value}" for option operator.display.')
    if 'delete' in contents and len(contents) > 1:
            raise ValueError(f'Cannot specify "delete" with other values for option operator.display.')
    return contents


def multiple_choice_days(contents, dependencies):
    """Validates multiple choices for the restrictions.days option.

    Parameters
    ----------
        contents: Union[str, list[str]]
                 The contents of the choice argument.
        dependencies: dict
                     Any arguments this argument is dependent on.

    Raises
    -------
        ValueError: str
                   When an invalid argument provided.

    Returns
    -------
        list: List containing each choice selected.
    """
    allowed_values = {
        'anyday',
        'weekdays',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday'
    }

    if not contents:
        return None
    if not isinstance(contents, list):
        contents = [contents]
    for value in contents:
        if value not in allowed_values:
            raise ValueError(f'Invalid argument "{value}" for option restrictions.days.')
    if 'anyday' in contents and len(contents) > 1:
            raise ValueError(f'Cannot specify "anyday" with other values for option restrictions.days.')
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
            if dfp.get('delete', False):
                return "NODFP"

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
                ('general', 'custom_fields', ('add',)),
                ('access', 'clauth', ('add',)),
                ('access', 'category', ('add',)),
                ('operator', 'msg_scope', ('add',))
            ],
            'flat': [
                ('dfp', ('data_app_id', 'data_class', 'storage_class', 'management_class')),
                ('language', ('primary', 'secondary')),
                ('omvs', ('uid', 'custom_uid', 'home', 'program', 'nonshared_size', 'shared_size', 'addr_space_size', 'map_size', 'max_procs', 'max_threads', 'max_cpu_time', 'max_files')),
                ('tso', ('account_num', 'logon_cmd', 'logon_proc', 'dest_id', 'hold_class', 'job_class', 'msg_class', 'sysout_class', 'region_size', 'max_region_size', 'security_label', 'unit_name', 'user_data')),
                ('access', ('default_group', 'clauth', 'roaudit', 'category', 'operator_card', 'maintenance_access', 'restricted', 'security_label', 'security_level')),
                ('operator', ('alt_group', 'authority', 'cmd_system', 'search_key', 'migration_id', 'display', 'msg_level', 'msg_format', 'msg_storage', 'msg_scope', 'automated_msgs', 'del_msgs', 'hardcopy_msgs', 'internal_msgs', 'routing_msgs', 'undelivered_msgs', 'unknown_msgs', 'responses')),
                ('restrictions', ('days', 'time', 'resume', 'revoke'))
            ]
        },
        'update': {},
        'delete': {},
        'purge': {},
        'list': {},
        'connect': {},
        'remove': {}
    }

    should_remove_empty_strings = {
        'create': True,
        'update': False,
        'delete': False,
        'purge': False,
        'list': False,
        'connect': False,
        'remove': False
    }

    # All empty lists indicate an operation that doesn't require any other
    # block to make sense.
    valid_blocks = {
        'create': [],
        'update': ['general', 'dfp', 'language', 'omvs', 'tso', 'access', 'operator', 'restrictions'],
        'delete': [],
        'purge': [],
        'list': [],
        'connect': ['connect'],
        'remove': ['connect']
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
        (('omvs', 'nonshared_size'), 'format', ('[0-9]{1,8}[mgtp]',)),
        (('omvs', 'shared_size'), 'format', ('[0-9]{1,8}[mgtp]',)),
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
        (('operator', 'alt_group'), 'length', ((0, 8),)),
        (('operator', 'cmd_system'), 'length', ((0, 8),)),
        (('operator', 'search_key'), 'length', ((0, 8),)),
        (('operator', 'msg_storage'), 'range', (1, 2000, 0)),
        (('restrictions', 'time'), 'format', ('^([01]?[0-9]|2[0-3])[0-5][0-9]:([01]?[0-9]|2[0-3])[0-5][0-9]$', 'anytime')),
        (('restrictions', 'resume'), 'format', ('^([0]?[1-9]|1[0-2])/([0-2]?[1-9]|3[0-1])/([0-9]{2})$',)),
        (('restrictions', 'revoke'), 'format', ('^([0]?[1-9]|1[0-2])/([0-2]?[1-9]|3[0-1])/([0-9]{2})$',)),
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

    def validate_params(self):
        """Adds a couple of validations for omvs.nonshared_size and omvs.shared_size.

        Raises
        ------
            ValueError: When a parameter has an invalid value.
        """
        super().validate_params()

        if self.params.get('omvs') is not None:
            if self.params['omvs'].get('nonshared_size') is not None:
                nonshared_size = self.params['omvs']['nonshared_size']
                nonshared_size = int(nonshared_size[:len(nonshared_size)-1])
                if nonshared_size < 0 or nonshared_size > 16_777_215:
                    raise ValueError('Value of omvs.nonshared_size is outside of its range.')

            if self.params['omvs'].get('shared_size') is not None:
                shared_size = self.params['omvs']['shared_size']
                shared_size = int(shared_size[:len(shared_size)-1])
                if shared_size < 1 or shared_size > 16_777_215:
                    raise ValueError('Value of omvs.shared_size is outside of its range.')

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
        if self.operation == 'connect':
            rc, stdout, stderr, cmd = self._connect_user()
        if self.operation == 'remove':
            rc, stdout, stderr, cmd = self._remove_user()

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

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_language_substring()}'.strip()
        cmd = f'{cmd} {self._make_tso_substring()}'.strip()
        cmd = f'{cmd} {self._make_omvs_substring()}'.strip()
        cmd = f'{cmd} {self._make_access_substring_creation()}'.strip()
        cmd = f'{cmd} {self._make_restrictions_substring()}'.strip()
        cmd = f'{cmd} {self._make_operator_substring()}'.strip()

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
        cmd = f'ALTUSER ({self.name})'

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_language_substring()}'.strip()
        cmd = f'{cmd} {self._make_tso_substring()}'.strip()
        cmd = f'{cmd} {self._make_omvs_substring()}'.strip()
        cmd = f'{cmd} {self._make_access_substring_creation()}'.strip()
        cmd = f'{cmd} {self._make_restrictions_substring()}'.strip()
        cmd = f'{cmd} {self._make_operator_substring()}'.strip()

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

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

    def _connect_user(self):
        """Builds and execute a CONNECT command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the CONNECT command.
        """
        cmd = f'CONNECT ({self.name}) '

        connect = self.params.get('connect')

        if connect.get('group_name') is not None:
            cmd = f"{cmd} GROUP({connect['group_name']}) "
        else:
            return 1, "", "No group was provided for a connect operation.", cmd

        if connect.get('authority') is not None:
            cmd = f"{cmd}AUTHORITY({connect['authority']}) "
        if connect.get('universal_access') is not None:
            cmd = f"{cmd}UACC({connect['universal_access']}) "
        if connect.get('group_account', False):
            cmd = f"{cmd}GRPACC "
        else:
            cmd = f"{cmd}NOGRPACC "
        if connect.get('group_operations', False):
            cmd = f"{cmd}OPERATIONS "
        else:
            cmd = f"{cmd}NOOPERATIONS "
        if connect.get('auditor', False):
            cmd = f"{cmd}AUDITOR "
        else:
            cmd = f"{cmd}NOAUDITOR "
        if connect.get('adsp_attribute', False):
            cmd = f"{cmd}ADSP "
        else:
            cmd = f"{cmd}NOADSP "
        if connect.get('special', False):
            cmd = f"{cmd}SPECIAL "
        else:
            cmd = f"{cmd}NOSPECIAL "

        if self.params.get('general') is not None:
            if self.params['general'].get('owner') is not None:
                cmd = f"{cmd} OWNER({self.params['general']['owner']})"

        if self.params.get('restrictions') is not None:
            restrictions = self.params['restrictions']
            if restrictions.get('resume') is not None:
                cmd = f"{cmd}RESUME({restrictions['resume']})"
            elif restrictions.get('delete_resume', False):
                cmd = f"{cmd}NORESUME "

            if restrictions.get('revoke') is not None:
                cmd = f"{cmd}REVOKE({restrictions['revoke']})"
            elif restrictions.get('delete_revoke', False):
                cmd = f"{cmd}NOREVOKE"

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _remove_user(self):
        """Builds and execute a REMOVE command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the REMOVE command.
        """
        cmd = f'REMOVE ({self.name}) '

        connect = self.params.get('connect')

        if connect.get('group_name') is not None:
            cmd = f"{cmd}GROUP({connect['group_name']})"
        else:
            return 1, "", "No group was provided for a remove operation.", cmd

        if self.params.get('general') is not None:
            if self.params['general'].get('owner') is not None:
                cmd = f"{cmd} OWNER({self.params['general']['owner']})"

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

    def _make_language_substring(self):
        """Creates a string that defines the LANGUAGE block of a user profile.

        Returns
        -------
            str: LANGUAGE parameters of a RACF command.
        """
        cmd = ""
        language = self.params.get('language')

        if language is not None:
            if language.get('delete', False):
                return "NOLANGUAGE"

            cmd = f"{cmd}LANGUAGE("

            if language.get('primary') is not None:
                if language.get('primary') != "":
                    cmd = f"{cmd} PRIMARY({language['primary']})"
                else:
                    cmd = f"{cmd} NOPRIMARY"
            if language.get('secondary') is not None:
                if language.get('secondary') != "":
                    cmd = f"{cmd} SECONDARY({language['secondary']})"
                else:
                    cmd = f"{cmd} NOSECONDARY"

            cmd = f"{cmd} )"

        return cmd

    def _make_omvs_substring(self):
        """Creates a string that defines the OMVS (Unix System Services) block of
        a user profile.

        Returns
        -------
            str: OMVS parameters of a RACF command.
        """
        cmd = ""
        omvs = self.params.get('omvs')

        if omvs is not None:
            if omvs.get('delete', False):
                return "NOOMVS"

            cmd = f"{cmd}OMVS("

            if omvs.get('uid') == 'auto':
                cmd = f'{cmd} AUTOUID'
            elif omvs.get('uid') != 'none':
                cmd = f"{cmd} UID({omvs['custom_uid']})"
                if omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
            else:
                cmd = f'{cmd} NOUID'

            if omvs.get('home') is not None:
                if omvs.get('home') != "":
                    cmd = f"{cmd} HOME({omvs['home']})"
                else:
                    cmd = f"{cmd} NOHOME"
            if omvs.get('program') is not None:
                if omvs.get('program') != "":
                    cmd = f"{cmd} PROGRAM({omvs['program']})"
                else:
                    cmd = f"{cmd} NOPROGRAM"
            if omvs.get('nonshared_size') is not None:
                if omvs.get('nonshared_size') != "":
                    cmd = f"{cmd} MEMLIMIT({omvs['nonshared_size']})"
                else:
                    cmd = f"{cmd} NOMEMLIMIT"
            if omvs.get('shared_size') is not None:
                if omvs.get('shared_size') != "":
                    cmd = f"{cmd} SHMEMMAX({omvs['shared_size']})"
                else:
                    cmd = f"{cmd} NOSHMEMMAX"
            if omvs.get('addr_space_size') is not None:
                if omvs.get('addr_space_size') != 0:
                    cmd = f"{cmd} ASSIZEMAX({omvs['addr_space_size']})"
                else:
                    cmd = f"{cmd} NOASSIZEMAX"
            if omvs.get('map_size') is not None:
                if omvs.get('map_size') != 0:
                    cmd = f"{cmd} MMAPAREAMAX({omvs['map_size']})"
                else:
                    cmd = f"{cmd} NOMMAPAREAMAX"
            if omvs.get('max_procs') is not None:
                if omvs.get('max_procs') != 0:
                    cmd = f"{cmd} PROCUSERMAX({omvs['max_procs']})"
                else:
                    cmd = f"{cmd} NOPROCUSERMAX"
            if omvs.get('max_threads') is not None:
                if omvs.get('max_threads') != -1:
                    cmd = f"{cmd} THREADSMAX({omvs['max_threads']})"
                else:
                    cmd = f"{cmd} NOTHREADSMAX"
            if omvs.get('max_cpu_time') is not None:
                if omvs.get('max_cpu_time') != 0:
                    cmd = f"{cmd} CPUTIMEMAX({omvs['max_cpu_time']})"
                else:
                    cmd = f"{cmd} NOCPUTIMEMAX"
            if omvs.get('max_files') is not None:
                if omvs.get('max_files') != 0:
                    cmd = f"{cmd} FILEPROCMAX({omvs['max_files']})"
                else:
                    cmd = f"{cmd} NOFILEPROCMAX"

            cmd = f"{cmd} )"

        return cmd

    def _make_tso_substring(self):
        """Creates a string that defines the TSO block of a user profile.

        Returns
        -------
            str: TSO parameters of a RACF command.
        """
        cmd = ""
        tso = self.params.get('tso')

        if tso is not None:
            if tso.get('delete', False):
                return "NOTSO"

            cmd = f"{cmd}TSO("

            if tso.get('account_num') is not None:
                if tso.get('account_num') != "":
                    cmd = f"{cmd} ACCTNUM({tso['account_num']})"
                else:
                    cmd = f"{cmd} NOACCTNUM"
            if tso.get('logon_cmd') is not None:
                if tso.get('logon_cmd') != "":
                    cmd = f"{cmd} COMMAND({tso['logon_cmd']})"
                else:
                    cmd = f"{cmd} NOCOMMAND"
            if tso.get('dest_id') is not None:
                if tso.get('dest_id') != "":
                    cmd = f"{cmd} DEST({tso['dest_id']})"
                else:
                    cmd = f"{cmd} NODEST"
            if tso.get('hold_class') is not None:
                if tso.get('hold_class') != "":
                    cmd = f"{cmd} HOLDCLASS({tso['hold_class']})"
                else:
                    cmd = f"{cmd} NOHOLDCLASS"
            if tso.get('job_class') is not None:
                if tso.get('job_class') != "":
                    cmd = f"{cmd} JOBCLASS({tso['job_class']})"
                else:
                    cmd = f"{cmd} NOJOBCLASS"
            if tso.get('msg_class') is not None:
                if tso.get('msg_class') != "":
                    cmd = f"{cmd} MSGCLASS({tso['msg_class']})"
                else:
                    cmd = f"{cmd} NOMSGCLASS"
            if tso.get('sysout_class') is not None:
                if tso.get('sysout_class') != "":
                    cmd = f"{cmd} SYS({tso['sysout_class']})"
                else:
                    cmd = f"{cmd} NOSYS"
            if tso.get('region_size') is not None:
                if tso.get('region_size') != -1:
                    cmd = f"{cmd} SIZE({tso['region_size']})"
                else:
                    cmd = f"{cmd} NOSIZE"
            if tso.get('max_region_size') is not None:
                if tso.get('max_region_size') != -1:
                    cmd = f"{cmd} MAXSIZE({tso['max_region_size']})"
                else:
                    cmd = f"{cmd} NOMAXSIZE"
            if tso.get('logon_proc') is not None:
                if tso.get('logon_proc') != "":
                    cmd = f"{cmd} PROC({tso['logon_proc']})"
                else:
                    cmd = f"{cmd} NOPROC"
            if tso.get('security_label') is not None:
                if tso.get('security_label') != "":
                    cmd = f"{cmd} SECLABEL({tso['security_label']})"
                else:
                    cmd = f"{cmd} NOSECLABEL"
            if tso.get('unit_name') is not None:
                if tso.get('unit_name') != "":
                    cmd = f"{cmd} UNIT({tso['unit_name']})"
                else:
                    cmd = f"{cmd} NOUNIT"
            if tso.get('user_data') is not None:
                if tso.get('user_data') != "":
                    cmd = f"{cmd} USERDATA({tso['user_data']})"
                else:
                    cmd = f"{cmd} NOUSERDATA"

            cmd = f"{cmd} )"

        return cmd

    def _make_operator_substring(self):
        """Creates a string that defines the OPERATOR block of a user profile.

        Returns
        -------
            str: OPERATOR parameters of a RACF command.
        """
        cmd = ""
        operator = self.params.get('operator')

        if operator is not None:
            if operator.get('delete', False):
                return "NOOPERPARM"

            cmd = f"{cmd}OPERPARM("

            if operator.get('alt_group') is not None:
                if operator.get('alt_group') != "":
                    cmd = f"{cmd} ALTGRP({operator['alt_group']})"
                else:
                    cmd = f"{cmd} NOALTGRP"
            if operator.get('authority') is not None:
                if operator.get('authority') != "delete":
                    cmd = f"{cmd} AUTH({operator['authority']})"
                else:
                    cmd = f"{cmd} NOAUTH"
            if operator.get('cmd_system') is not None:
                if operator.get('cmd_system') != "":
                    cmd = f"{cmd} CMDSYS({operator['cmd_system']})"
                else:
                    cmd = f"{cmd} NOCMDSYS"
            if operator.get('search_key') is not None:
                if operator.get('search_key') != "":
                    cmd = f"{cmd} KEY({operator['search_key']})"
                else:
                    cmd = f"{cmd} NOKEY"
            if operator.get('migration_id', False):
                cmd = f"{cmd} MIGID(YES)"
            else:
                cmd = f"{cmd} MIGID(NO)"
            if operator.get('display') is not None:
                if "delete" not in operator['display']:
                    options = operator['display']
                    cmd = f'{cmd} MONITOR( '
                    for option in options:
                        cmd = f'{cmd}{option} '
                    cmd = f'{cmd}) '
                else:
                    cmd = f"{cmd} NOMONITOR"
            if operator.get('msg_level') is not None:
                if operator.get('msg_level') != "delete":
                    cmd = f"{cmd} LEVEL({operator['msg_level']})"
                else:
                    cmd = f"{cmd} NOLEVEL"
            if operator.get('msg_format') is not None:
                if operator.get('msg_format') != 'delete':
                    cmd = f"{cmd} MFORM({operator['msg_format']})"
                else:
                    cmd = f"{cmd} NOMFORM"
            if operator.get('msg_storage') is not None:
                if operator.get('msg_storage') != 0:
                    cmd = f"{cmd} STORAGE({operator['msg_storage']})"
                else:
                    cmd = f"{cmd} NOSTORAGE"
            if operator.get('msg_scope') is not None:
                if operator['msg_scope'].get('add') is not None:
                    scopes = operator['msg_scope']['add']
                    cmd = f'{cmd}ADDMSCOPE( '
                    for scope in scopes:
                        cmd = f'{cmd}{scope} '
                    cmd = f'{cmd}) '
                elif operator['msg_scope'].get('add') is not None:
                    categories = access['category']['delete']
                    cmd = f'{cmd}DELMSCOPE( '
                    for scope in scopes:
                        cmd = f'{cmd}{scope} '
                    cmd = f'{cmd}) '
                else:
                    cmd = f'{cmd}NOMSCOPE'
            if operator.get('automated_msgs', False):
                cmd = f"{cmd} AUTO(YES)"
            else:
                cmd = f"{cmd} AUTO(NO)"
            if operator.get('del_msgs') is not None:
                if operator.get('del_msgs') != 'delete':
                    cmd = f"{cmd} DOM({operator['del_msgs']})"
                else:
                    cmd = f"{cmd} NODOM"
            if operator.get('hardcopy_msgs', False):
                cmd = f"{cmd} HC(YES)"
            else:
                cmd = f"{cmd} HC(NO)"
            if operator.get('internal_msgs', False):
                cmd = f"{cmd} INTIDS(YES)"
            else:
                cmd = f"{cmd} INTIDS(NO)"
            if operator.get('routing_msgs') is not None:
                routes = operator['routing_msgs']
                cmd = f'{cmd} ROUTCODE( '
                for route in routes:
                    cmd = f'{cmd}{route} '
                cmd = f'{cmd}) '
            if operator.get('undelivered_msgs', False):
                cmd = f"{cmd} UD(YES)"
            else:
                cmd = f"{cmd} UD(NO)"
            if operator.get('unknown_msgs', False):
                cmd = f"{cmd} UNKNIDS(YES)"
            else:
                cmd = f"{cmd} UNKNIDS(NO)"
            if operator.get('responses', False):
                cmd = f"{cmd} LOGCMDRESP(SYSTEM)"
            else:
                cmd = f"{cmd} LOGCMDRESP(NO)"

            cmd = f"{cmd} )"

        return cmd

    def _make_access_substring_creation(self):
        """Creates a string that defines various parameters for a user profile.

        Returns
        -------
            str: User create/alter parameters of a RACF command.
        """
        cmd = ""
        access = self.params.get('access')

        if access is not None:
            if access.get('default_group') is not None:
                cmd = f"{cmd}DFLTGRP({access['default_group']}) "
            if access.get('clauth') is not None:
                if access['clauth'].get('add') is not None:
                    clauth = access['clauth']['add']
                    cmd = f'{cmd}CLAUTH( '
                    for auth_class in clauth:
                        cmd = f'{cmd}{auth_class} '
                    cmd = f'{cmd}) '
                elif access['clauth'].get('delete') is not None:
                    clauth = access['clauth']['delete']
                    cmd = f'{cmd}NOCLAUTH( '
                    for auth_class in clauth:
                        cmd = f'{cmd}{auth_class} '
                    cmd = f'{cmd}) '
            if access.get('roaudit') is not None:
                roaudit = "ROAUDIT" if access['roaudit'] else "NOROAUDIT"
                cmd = f'{cmd}{roaudit} '
            if access.get('category') is not None:
                if access['category'].get('add') is not None:
                    categories = access['category']['add']
                    cmd = f'{cmd}ADDCATEGORY( '
                    for category in categories:
                        cmd = f'{cmd}{category} '
                    cmd = f'{cmd}) '
                elif access['category'].get('delete') is not None:
                    categories = access['category']['delete']
                    cmd = f'{cmd}DELCATEGORY( '
                    for category in categories:
                        cmd = f'{cmd}{category} '
                    cmd = f'{cmd}) '
            if access.get('operator_card') is not None:
                op_card = "OIDCARD" if access['operator_card'] else "NOOIDCARD"
                cmd = f'{cmd}{op_card} '
            if access.get('maintenance_access') is not None:
                operations = "OPERATIONS" if access['maintenance_access'] else "NOOPERATIONS"
                cmd = f'{cmd}{operations} '
            if access.get('restricted') is not None:
                restricted = "RESTRICTED" if access['restricted'] else "NORESTRICTED"
                cmd = f'{cmd}{restricted} '
            if access.get('security_label') is not None:
                if access.get('security_label') != "":
                    cmd = f"{cmd}SECLABEL('{access['security_label']}') "
                else:
                    cmd = f"{cmd}NOSECLABEL "
            if access.get('security_level') is not None:
                if access.get('security_level') != "":
                    cmd = f"{cmd}SECLEVEL('{access['security_level']}') "
                else:
                    cmd = f"{cmd}NOSECLEVEL "

        return cmd

    def _make_restrictions_substring(self):
        """Creates a string that defines various parameters for how a user can
        access a system.

        Returns
        -------
            str: User parameters of a RACF command.
        """
        cmd = ""
        restrictions = self.params.get('restrictions')

        if restrictions is not None:
            if restrictions.get('days') is not None or restrictions.get('time') is not None:
                cmd = f"{cmd}WHEN( "
                if restrictions.get('days') is not None:
                    cmd = f"{cmd}DAYS( "
                    for day in restrictions['days']:
                        cmd = f"{cmd}{day} "
                    cmd = f"{cmd}) "
                if restrictions.get('time') is not None:
                    cmd = f"{cmd}TIME({restrictions['time']}) "
                cmd = f"{cmd}) "

            if restrictions.get('resume') is not None:
                cmd = f"{cmd}RESUME({restrictions['resume']})"
            elif restrictions.get('delete_resume', False):
                cmd = f"{cmd}NORESUME "

            if restrictions.get('revoke') is not None:
                cmd = f"{cmd}REVOKE({restrictions['revoke']})"
            elif restrictions.get('delete_revoke', False):
                cmd = f"{cmd}NOREVOKE "

        return cmd


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
                        'type': 'str',
                        'required': False
                    },
                    'nonshared_size': {
                        'type': 'str',
                        'required': False
                    },
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
                    ('user_data', 'delete')
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
            },
            'connect': {
                'type': 'dict',
                'required': False,
                'options': {
                    'authority': {
                        'type': 'str',
                        'required': False,
                        'choices': ['use', 'create', 'connect', 'join']
                    },
                    'universal_access': {
                        'type': 'str',
                        'required': False,
                        'choices': ['alter', 'control', 'update', 'read', 'none']
                    },
                    'group_name': {
                        'type': 'str',
                        'required': False
                    },
                    'group_account': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'group_operations': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'auditor': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'adsp_attribute': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'special': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    }
                }

            },
            'access': {
                'type': 'dict',
                'required': False,
                'options': {
                    'default_group': {
                        'type': 'str',
                        'required': False
                    },
                    'clauth': {
                        'type': 'dict',
                        'required': False,
                        'mutually_exclusive': [
                            ('add', 'delete')
                        ],
                        'options': {
                            'add': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                            'delete': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                        }
                    },
                    'roaudit': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'category': {
                        'type': 'dict',
                        'required': False,
                        'mutually_exclusive': [
                            ('add', 'delete')
                        ],
                        'options': {
                            'add': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                            'delete': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                        }
                    },
                    'operator_card': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'maintenance_access': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'restricted': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'security_label': {
                        'type': 'str',
                        'required': False
                    },
                    'security_level': {
                        'type': 'str',
                        'required': False
                    },
                }
            },
            'operator': {
                'type': 'dict',
                'required': False,
                'mutually_exclusive': [
                    ('alt_group', 'delete'),
                    ('authority', 'delete'),
                    ('cmd_system', 'delete'),
                    ('search_key', 'delete'),
                    ('migration_id', 'delete'),
                    ('display', 'delete'),
                    ('msg_level', 'delete'),
                    ('msg_format', 'delete'),
                    ('msg_storage', 'delete'),
                    ('msg_scope', 'delete'),
                    ('automated_msgs', 'delete'),
                    ('del_msgs', 'delete'),
                    ('hardcopy_msgs', 'delete'),
                    ('internal_msgs', 'delete'),
                    ('routing_msgs', 'delete'),
                    ('undelivered_msgs', 'delete'),
                    ('unknown_msgs', 'delete'),
                    ('responses', 'delete')
                ],
                'options': {
                    'alt_group': {
                        'type': 'str',
                        'required': False
                    },
                    'authority': {
                        'type': 'str',
                        'required': False,
                        'choices': ['master', 'all', 'info', 'cons', 'io', 'sys', 'delete']
                    },
                    'cmd_system': {
                        'type': 'str',
                        'required': False
                    },
                    'search_key': {
                        'type': 'str',
                        'required': False
                    },
                    'migration_id': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'display': {
                        'type': 'raw',
                        'required': False,
                        'default': ['jobnames', 'sess']
                        # 'choices': ['jobnames', 'jobnamest', 'sess', 'sesst', 'status', 'delete']
                    },
                    'msg_level': {
                        'type': 'str',
                        'required': False,
                        'choices': ['nb', 'all', 'r', 'i', 'ce', 'e', 'in', 'delete']
                    },
                    'msg_format': {
                        'type': 'str',
                        'required': False,
                        'choices': ['j', 'm', 's', 't', 'x', 'delete']
                    },
                    'msg_storage': {
                        'type': 'int',
                        'required': False
                    },
                    'msg_scope': {
                        'type': 'dict',
                        'required': False,
                        'mutually_exclusive': [
                            ('add', 'remove'),
                            ('add', 'delete'),
                            ('remove', 'delete'),
                        ],
                        'options': {
                            'add': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                            'remove': {
                                'type': 'list',
                                'elements': 'str',
                                'required': False
                            },
                            'delete': {
                                'type': 'bool',
                                'required': False
                            }
                        }
                    },
                    'automated_msgs': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'del_msgs': {
                        'type': 'str',
                        'required': False,
                        'choices': ['normal', 'all', 'none', 'delete']
                    },
                    'hardcopy_msgs': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'internal_msgs': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'routing_msgs': {
                        'type': 'list',
                        'required': False,
                        'elements': 'str'
                    },
                    'undelivered_msgs': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'unknown_msgs': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'responses': {
                        'type': 'bool',
                        'required': False,
                        'default': True
                    },
                    'delete': {
                        'type': 'bool',
                        'required': False
                    }
                }
            },
            'restrictions': {
                'type': 'dict',
                'required': False,
                'mutually_exclusive': [
                    ('resume', 'delete_resume'),
                    ('revoke', 'delete_revoke')
                ],
                'options': {
                    'days': {
                        'type': 'raw',
                        'required': False,
                        'default': 'anyday'
                    },
                    'time': {
                        'type': 'str',
                        'required': False,
                        'default': 'anytime'
                    },
                    'resume': {
                        'type': 'str',
                        'required': False
                    },
                    'delete_resume': {
                        'type': 'bool',
                        'required': False
                    },
                    'revoke': {
                        'type': 'str',
                        'required': False
                    },
                    'delete_revoke': {
                        'type': 'bool',
                        'required': False
                    },
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
        },
        'connect': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'authority': {'arg_type': 'str', 'required': False},
                'universal_access': {'arg_type': 'str', 'required': False},
                'group_name': {'arg_type': 'str', 'required': False},
                'group_account': {'arg_type': 'bool', 'required': False},
                'group_operations': {'arg_type': 'bool', 'required': False},
                'auditor': {'arg_type': 'bool', 'required': False},
                'adsp_attribute': {'arg_type': 'bool', 'required': False},
                'special': {'arg_type': 'bool', 'required': False},
            }
        },
        'access': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'default_group': {'arg_type': 'str', 'required': False},
                'clauth': {
                    'arg_type': 'dict',
                    'required': False,
                    'options': {
                        'add': {'arg_type': 'list', 'elements': 'str', 'required': False},
                        'delete': {'arg_type': 'list', 'elements': 'str', 'required': False}
                    }
                },
                'roaudit': {'arg_type': 'bool', 'required': False},
                'category': {
                    'arg_type': 'dict',
                    'required': False,
                    'options': {
                        'add': {'arg_type': 'list', 'elements': 'str', 'required': False},
                        'delete': {'arg_type': 'list', 'elements': 'str', 'required': False}
                    }
                },
                'operator_card': {'arg_type': 'bool', 'required': False},
                'maintenance_access': {'arg_type': 'bool', 'required': False},
                'restricted': {'arg_type': 'bool', 'required': False},
                'security_label': {'arg_type': 'str', 'required': False},
                'security_level': {'arg_type': 'str', 'required': False},
            }
        },
        'operator': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'alt_group': {'arg_type': 'str', 'required': False},
                'authority': {'arg_type': 'str', 'required': False},
                'cmd_system': {'arg_type': 'str', 'required': False},
                'search_key': {'arg_type': 'str', 'required': False},
                'migration_id': {'arg_type': 'bool', 'required': False},
                'display': {'arg_type': multiple_choice_display, 'required': False},
                'msg_level': {'arg_type': 'str', 'required': False},
                'msg_format': {'arg_type': 'str', 'required': False},
                'msg_storage': {'arg_type': 'int', 'required': False},
                'msg_scope': {
                    'arg_type': 'dict',
                    'required': False,
                    'options': {
                        'add': {'arg_type': 'list', 'elements': 'str', 'required': False},
                        'remove': {'arg_type': 'list', 'elements': 'str', 'required': False},
                        'delete': {'arg_type': 'bool', 'required': False}
                    }
                },
                'automated_msgs': {'arg_type': 'bool', 'required': False},
                'del_msgs': {'arg_type': 'str', 'required': False},
                'hardcopy_msgs': {'arg_type': 'bool', 'required': False},
                'internal_msgs': {'arg_type': 'bool', 'required': False},
                'routing_msgs': {'arg_type': 'list', 'elements': 'str', 'required': False},
                'undelivered_msgs': {'arg_type': 'bool', 'required': False},
                'unknown_msgs': {'arg_type': 'bool', 'required': False},
                'responses': {'arg_type': 'bool', 'required': False},
                'delete': {'arg_type': 'bool', 'required': False}
            }
        },
        'restrictions': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'days': {'arg_type': multiple_choice_days, 'required': False},
                'time': {'arg_type': 'str', 'required': False},
                'resume': {'arg_type': 'str', 'required': False},
                'delete_resume': {'arg_type': 'bool', 'required': False},
                'revoke': {'arg_type': 'str', 'required': False},
                'delete_revoke': {'arg_type': 'bool', 'required': False}
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
        result = operation_handler.get_state()
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
