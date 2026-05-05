#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025, 2026
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
  - "Yogesh Rana (@yrana17)"
short_description: Manage user and group profiles in RACF
description:
  - The L(zos_user,./zos_user.html) module executes RACF TSO commands that can manage
    user and group RACF profiles.
  - The module can create, update and delete RACF profiles about them.
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
      - Specifies the operation to perform on the RACF profile.
      - The available choices depend on the value of I(scope).
      - C(create) - Creates a new profile. Supported for both I(scope=user) and I(scope=group).
      - C(update) - Modifies an existing profile. Supported for both I(scope=user) and I(scope=group).
      - C(delete) - Removes the profile from RACF but may leave residual references in the database. Supported for both I(scope=user) and I(scope=group).
      - C(purge) - Completely removes the profile and all associated references from the RACF database.
        Unloads the database using C(IRRDBU00), identifies all references via C(IRRRID00), and executes
        the necessary commands to remove them.
      - C(connect) - Links a user to a group. Only supported when I(scope=user).
      - C(remove) - Removes a user from a group. Only supported when I(scope=user).
    type: str
    required: true
    choices:
      - create
      - update
      - delete
      - purge
      - connect
      - remove
  scope:
    description:
      - Whether the RACF profile specified in I(name) is a user or group profile.
    type: str
    required: true
    choices:
      - user
      - group
  database:
    description:
      - Name of the RACF database to use for the purge operation.
      - This option is only applicable when I(operation=purge).
    type: str
    required: false
  keep_dump:
    description:
      - Whether to keep the database dump datasets after the purge operation completes.
      - This option is only applicable when I(operation=purge).
      - When set to C(true), the IRRDBU00 dump dataset and IRRRID00 CLIST will be retained
        for debugging or auditing purposes.
      - When set to C(false), these temporary datasets will be deleted after the purge operation.
    type: bool
    required: false
    default: false
  optimize_dump:
    description:
      - Whether to optimize the database dump operation without locking the input RACF database.
      - This option is only applicable when I(operation=purge).
      - When set to C(true), the IRRDBU00 utility runs with the C(NOLOCKINPUT) option.
        This improves system availability by allowing concurrent updates to the database.
        However, it may result in inconsistent data if changes occur during the process.
      - The user ID requires C(READ) authority to the RACF database when using C(NOLOCKINPUT).
      - When set to C(false), the IRRDBU00 utility runs with the C(LOCKINPUT) option.
        This ensures data consistency by locking the database, but it prevents other
        processes from updating RACF profiles until the dump completes.
      - The user ID requires C(UPDATE) authority to the RACF database to permit the utility to C(LOCKINPUT).
    type: bool
    required: false
    default: true
  no_exec:
    description:
      - Whether to skip execution of generated clist.
      - This option is only applicable when I(operation=purge).
      - When set to C(true), the module will generate the CLIST with DELUSER/DELGROUP
        commands but will not execute it.
      - When set to C(false), the CLIST will be generated and executed to purge the profiles.
      - This option is useful for reviewing the purge commands before execution.
    type: bool
    required: false
    default: false
  tmp_hlq:
    description:
      - Override the default high level qualifier (HLQ) for temporary data sets.
      - This option is only applicable when I(operation=purge).
      - Temporary data sets are created during the purge operation for database dumps,
        CLIST generation, and intermediate processing.
      - If not specified, the system default HLQ will be used.
    type: str
    required: false
  general:
    description:
      - Options that change common attributes in a RACF profile.
    required: false
    type: dict
    suboptions:
      user_name:
        description:
          - Display name for the user profile(not the userid).
          - This corresponds to the RACF NAME parameter.
          - Maximum length of 20 characters.
          - This option is only valid for user profiles (I(scope=user)).
          - This option is only applicable when I(operation=create) or I(operation=update).
          - If omitted, RACF will display UNKNOWN when listing the user.
          - To remove/reset the user name to default (UNKNOWN), set this to an empty string C("").
        type: str
        required: false
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
              - "Each custom field should be a C(key: value) pair."
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
            required: false
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
      - Options that set DFP attributes from the Storage Management Subsystem.
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
          - Must be a number between 0 and 16,777,215 suffixed by a unit.
          - Valid units are m (megabytes), g (gigabytes), t (terabytes) or
            p (petabytes).
          - An empty string will delete the current limit set.
        type: str
        required: false
      shared_size:
        description:
          - Maximum number of bytes of shared memory that can be allocated
            by the user.
          - Must be a number between 1 and 16,777,215 suffixed by a unit.
          - Valid units are m (megabytes), g (gigabytes), t (terabytes) or
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
          - Maximum length of 40 characters.
          - An empty value deletes this field.
        type: str
        required: false
      logon_cmd:
        description:
          - Command that needs to be run during TSO/E logon.
          - Maximum length of 80 characters.
          - This option keeps case.
          - An empty value deletes this field.
        type: str
        required: false
      logon_proc:
        description:
          - User's default logon procedure.
          - The value for this field is 1 to 8 alphanumeric characters.
          - An empty value deletes this field.
        type: str
        required: false
      dest_id:
        description:
          - Default destination to which the user can route dynamically allocated SYSOUT
            data sets.
          - The value for this field is 1 to 7 alphanumeric characters.
          - An empty value deletes this field.
        type: str
        required: false
      hold_class:
        description:
          - User's default hold class.
          - This option consists of 1 alphanumeric character.
          - An empty value deletes this field.
        type: str
        required: false
      job_class:
        description:
          - User's default job class.
          - This option consists of 1 alphanumeric character.
          - An empty value deletes this field.
        type: str
        required: false
      msg_class:
        description:
          - User's default message class.
          - This option consists of 1 alphanumeric character.
          - An empty value deletes this field.
        type: str
        required: false
      sysout_class:
        description:
          - User's default SYSOUT class.
          - This option consists of 1 alphanumeric character.
          - An empty value deletes this field.
        type: str
        required: false
      region_size:
        description:
          - Minimum region size if the user does not request a region size at logon.
          - A value between 0 and 2,096,128.
          - A value of -1 deletes this field.
        type: int
        required: false
      max_region_size:
        description:
          - Maximum region size that the user can request at logon.
          - A value between 0 and 2,096,128.
          - A value of -1 deletes this field.
        type: int
        required: false
      security_label:
        description:
          - User's security label if the user specifies one on the TSO logon panel.
          - An empty value deletes this field.
        type: str
        required: false
      unit_name:
        description:
          - Default name of a device or group of devices that a procedure uses for
            allocations.
          - The value for this field is 1 to 8 alphanumeric characters.
          - An empty value deletes this field.
        type: str
        required: false
      user_data:
        description:
          - Optional installation data defined for the user profile.
          - Must be 4 EBCDIC characters.
          - An empty value deletes this field.
        type: str
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
      - Options that configure what a user can do inside a group that is connected to.
      - These options are only used when C(operation=connect) and they are ignored
        otherwise.
    required: false
    type: dict
    suboptions:
      authority:
        description:
          - Level of group authority given to a user profile.
        type: str
        required: false
        choices:
          - use
          - create
          - connect
          - join
      universal_access:
        description:
          - Level of universal access authority given to a user profile.
        type: str
        required: false
        choices:
          - alter
          - control
          - update
          - read
          - none
      group_name:
        description:
          - Group to which the user will be connected to.
          - The rest of the options in this block will affect this group.
          - If not supplied, RACF will use a default group. It is recommended to specify
            this option when trying to connect a user to a group.
        type: str
        required: false
      group_account:
        description:
          - Whether the user's protected data sets are accessible to other users in the group.
        type: bool
        required: false
        default: false
      group_operations:
        description:
          - Whether a user should have the group-OPERATIONS attribute when connected to a group.
        type: bool
        required: false
        default: false
      auditor:
        description:
          - Whether a user should have auditor privileges for the group it is connected to.
        type: bool
        required: false
        default: false
      adsp_attribute:
        description:
          - Whether to give a user the ADSP attribute, which tells RACF to automatically protect
            data sets it creates with discrete profiles.
        type: bool
        required: false
        default: false
      special:
        description:
          - Whether to give a user profile the SPECIAL attribute.
          - This attribute lets a user change attributes of other profiles. Use with caution.
        type: bool
        required: false
        default: false
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
        default: false
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
        default: false
      maintenance_access:
        description:
          - Whether the user has authorization to do maintenance operations on all
            RACF-protected DASD data sets, tape volumes, and DASD volumes.
        type: bool
        required: false
        default: false
      restricted:
        description:
          - Whether to give the profile the RESTRICTED attribute.
        type: bool
        required: false
        default: false
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
        default: false
      display:
        description:
          - Which information should be displayed when monitoring
            jobs, TSO sessions, or data set status.
          - Possible values are C(jobnames), C(jobnamest), C(sess),
            C(sesst), C(status) and C(delete).
          - Multiple choices are allowed.
          - C(delete) will remove this field from the profile.
        type: list
        elements: str
        choices: [jobnames, jobnamest, sess, sesst, status, delete]
        required: false
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
              - Deletes the systems from this field.
            type: list
            elements: str
            required: false
      automated_msgs:
        description:
          - Whether the extended console can receive messages
            that have been automated by the MFP.
        type: bool
        required: false
        default: false
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
        default: false
      internal_msgs:
        description:
          - Whether the console should receive messages that
            are directed to console ID zero.
        type: bool
        required: false
        default: false
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
        default: false
      unknown_msgs:
        description:
          - Whether the console should receive messages that
            are directed to unknown console IDs.
        type: bool
        required: false
        default: false
      responses:
        description:
          - Whether command responses should be logged.
        type: bool
        required: false
        default: true
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
        choices:
          - anyday
          - weekdays
          - monday
          - tuesday
          - wednesday
          - thursday
          - friday
          - saturday
          - sunday
        default:
            - anyday
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
        default: anytime
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
  password_mgmt:
    description:
      - Options that manage password and passphrase settings for a user profile.
      - These options are only valid for user profiles (I(scope=user)).
      - These options are only applicable when I(operation=create) or I(operation=update).
    required: false
    type: dict
    suboptions:
      password:
        description:
          - Password for the user.
          - Maximum length of 8 characters.
          - When creating a user, if neither I(password) nor I(passphrase) is specified,
            RACF will not assign a password and the user will need to be assigned one
            before they can log in.
          - When a password is set for the first time during user creation, RACF marks it
            as EXPIRED by default. To change this, update the user with I(expired=false)
            after creation.
          - An empty string will remove the password and set it to NOPASSWORD.
          - It is recommended to use Ansible Vault to encrypt this value.
          - This option is mutually exclusive with I(passphrase).
        type: str
        required: false
      passphrase:
        description:
          - Passphrase for the user.
          - Minimum length of 9 characters, maximum length of 100 characters.
          - When creating a user, if neither I(password) nor I(passphrase) is specified,
            RACF will not assign a password and the user will need to be assigned one
            before they can log in.
          - When a passphrase is set for the first time during user creation, RACF marks it
            as EXPIRED by default. To change this, update the user with I(expired=false)
            after creation.
          - An empty string will remove the passphrase and set it to NOPHRASE.
          - It is recommended to use Ansible Vault to encrypt this value.
          - This option is mutually exclusive with I(password).
        type: str
        required: false
      expired:
        description:
          - Whether the password or passphrase should be marked as expired.
          - When C(true), the user will be required to change their password/passphrase
            on next login.
          - When C(false), the password/passphrase will be marked as NOEXPIRED.
          - This option is only applicable when I(operation=update).
          - This option B(must) be used together with I(password) or I(passphrase) in the
            same task. RACF requires a password/passphrase to be specified when using
            EXPIRED/NOEXPIRED.
          - When a password/passphrase is set for the first time during user creation,
            RACF automatically marks it as EXPIRED. To change it to NOEXPIRED, you must
            update the user and specify the same password/passphrase again with C(expired=false).
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
  - This module requires appropriate RACF authority to execute commands.
  - For standard operations (create, update, delete, connect, remove), the user executing the module must have sufficient RACF authority
    to perform the requested operation (typically SPECIAL or group-SPECIAL attribute).
  - For purge operations using IRRDBU00 utility - When I(optimize_dump=true) (default), IRRDBU00 runs with PARM=NOLOCKINPUT requiring
    READ authority to the input RACF database data sets. When I(optimize_dump=false), IRRDBU00 runs with PARM=LOCKINPUT requiring UPDATE
    authority to lock the database during the unload.
  - The IRRRID00 utility is used during purge operations to identify residual references and generate a CLIST of removal commands.
    The user must have READ authority to the input dataset (the unloaded RACF database produced by IRRDBU00).
  - To execute the generated CLIST from IRRRID00, the user must have sufficient RACF authority - DELUSER/DELGROUP requires the SPECIAL
    attribute, group-SPECIAL (within scope), or ownership of the target profile/superior group.

seealso:
  - module: ibm.ibm_zos_core.zos_tso_command
"""

EXAMPLES = r"""
- name: Create a new group profile using RACF defaults.
  zos_user:
    name: newgrp
    operation: create
    scope: group

- name: Create a user with full name and owner.
  zos_user:
    name: newuser
    operation: create
    scope: user
    general:
      user_name: John Doe
      owner: admin

- name: Update a user's full name.
  zos_user:
    name: existusr
    operation: update
    scope: user
    general:
      user_name: Jane Smith

- name: Remove a user's full name (sets to UNKNOWN).
  zos_user:
    name: existusr
    operation: update
    scope: user
    general:
      user_name: ""

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
    operation: update
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

- name: Purge user from RACF database
  zos_user:
    name: user
    operation: purge
    scope: user
    database: racf_db

- name: Purge group from RACF database
  zos_user:
    name: newgrp
    operation: purge
    scope: group
    database: racf_db

- name: Create a user with password (will be marked as EXPIRED by default)
  zos_user:
    name: newuser
    operation: create
    scope: user
    password_mgmt:
      password: "{{ user_password }}"

- name: Create a user with passphrase (will be marked as EXPIRED by default)
  zos_user:
    name: newuser
    operation: create
    scope: user
    password_mgmt:
      passphrase: "{{ user_passphrase }}"

- name: Update user password to NOEXPIRED
  zos_user:
    name: newuser
    operation: update
    scope: user
    password_mgmt:
      password: "{{ user_password }}"
      expired: false
    omvs:
      uid: auto

"""

RETURN = r"""
changed:
    description: Indicates whether any changes were made to the system.
    returned: always
    type: bool
    sample: true
cmd:
    description: The RACF command that was executed with tsocmd.
    returned: always
    type: str
    sample: "ADDUSER (DUSR1001)"
msg:
    description: |
        Message returned by the module. Contains error messages on failure,
        informational messages when no changes are needed (e.g., entity already exists),
        or validation error messages.
    returned: always
    type: str
    sample: "An error occurred while executing the RACF command."
rc:
    description: Return code from the RACF command execution.
    returned: always
    type: int
    sample: 0
stdout:
    description: |
        Standard output from the RACF command execution.
        In check mode, may contain informational messages about the entity state.
        For I(operation=purge), this includes technical details such as dump dataset names and CLIST processing messages.
    returned: always
    type: str
    sample: "User DUSR1001 is defined as PROTECTED.\n"
stdout_lines:
    description: List of strings containing individual lines from stdout.
    returned: always
    type: list
    elements: str
    sample: ["User DUSR1001 is defined as PROTECTED.", ""]
stderr:
    description: |
        Standard error from the RACF command execution.
        TSO command output is automatically filtered out.
    returned: always
    type: str
    sample: ""
stderr_lines:
    description: List of strings containing individual lines from stderr.
    returned: always
    type: list
    elements: str
    sample: [""]
num_entities_modified:
    description: |
        Number of profiles and references modified by the operation.
        Set to 0 when entity already exists or is already in desired state.
        Set to 1 for successful single entity operations.
        For purge operations, reflects the count of entities deleted.
    returned: always
    type: int
    sample: 1
entities_modified:
    description: |
        List of all profiles and references modified by the operation.
        For user scope operations (create, update, delete, connect, remove), contains the user profile name when successful.
        For group scope operations (create, update, delete), contains the group profile name when successful.
        For purge operations, contains all users/groups deleted by the CLIST.
        Empty list when no changes are made (entity already exists or in desired state).
    returned: always
    type: list
    elements: str
    sample: ['DUSR1001']
database_dumped:
    description: |
        Whether the module used IRRDBU00 utility to dump the RACF database.
        Set to C(true) only when the purge operation successfully executes the C(IRRDBU00) utility.
        Only relevant when I(operation=purge).
    returned: always
    type: bool
    sample: false
dump_kept:
    description: |
        Indicates whether the RACF database dump was retained on the managed node.
        This behavior is controlled by the I(keep_dump) input parameter.
        Only relevant when I(database_dumped=true).
    returned: always
    type: bool
    sample: false
dump_name:
    description: |
        The name of the dataset containing the output from the C(IRRDBU00) utility.
        This field is only populated when both I(database_dumped) and I(keep_dump) are C(true).
        Otherwise, this value returns C(null).
    returned: always
    type: str
    sample: USER.BACKUP.RACF.DATABASE
"""

from typing import Any

import copy
import math
import re
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dependency_checker import (
    validate_dependencies,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import \
    ZOAUImportError
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger

try:
    from zoautil_py import datasets, mvscmd, ztypes
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())
    mvscmd = ZOAUImportError(traceback.format_exc())
    ztypes = ZOAUImportError(traceback.format_exc())


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
        raise ValueError('Cannot specify "delete" with other values for option operator.display.')
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
        raise ValueError('Cannot specify "anyday" with other values for option restrictions.days.')
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
        self.database = module_params['database']
        self.keep_dump = module_params['keep_dump']
        self.optimize_dump = module_params['optimize_dump']
        self.no_exec = module_params['no_exec']
        self.tmp_hlq = module_params.get('tmp_hlq')
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
        self.verbosity = module._verbosity

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

            # Only process dictionary blocks
            if isinstance(self.params[block], dict):
                # Collect keys to delete to avoid modifying dict during iteration
                keys_to_delete = [k for k, v in self.params[block].items() if v == ""]
                for k in keys_to_delete:
                    del self.params[block][k]

                # Handle nested dictionaries - iterate over remaining keys after deletion
                for option in list(self.params[block].keys()):
                    if isinstance(self.params[block][option], dict):
                        subkeys_to_delete = [sk for sk, sv in self.params[block][option].items() if sv == ""]
                        for sk in subkeys_to_delete:
                            del self.params[block][option][sk]

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
        # Get filter configuration for this operation, default to empty dict if not found
        operation_filters = self.filters.get(self.operation, {})
        for block in operation_filters.get('nested', []):
            if not isinstance(block, (list, tuple)) or len(block) < 3:
                continue
            first_level = self.params.get(block[0], {})
            # Added check to ensure it's a dictionary and is not None
            if isinstance(first_level, dict) and first_level.get(block[1]) is not None:
                filtered_params = self.filter_block(self.params[block[0]][block[1]], block[2])
                self.params[block[0]][block[1]] = filtered_params if filtered_params else None

        for block in operation_filters.get('flat', []):
            if not isinstance(block, (list, tuple)) or len(block) < 2:
                continue
            if self.params.get(block[0]) is not None and isinstance(self.params[block[0]], dict):
                filtered_params = self.filter_block(self.params[block[0]], block[1])
                self.params[block[0]] = filtered_params if filtered_params else None

        # Removing empty dictionaries from the parameters.
        clean_params = copy.deepcopy(self.params)
        for block in self.params:
            if self.params[block] is None:
                del clean_params[block]
                continue

            # Added isinstance condition check to prevent iteration over non-dict values
            if isinstance(self.params[block], dict):
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

        # Get valid blocks for this operation, default to empty list if not found
        operation_blocks = self.valid_blocks.get(self.operation, [])
        # if len(self.valid_blocks[self.operation]) == 0:
        if len(operation_blocks) == 0:
            return True

        # for block in self.valid_blocks[self.operation]:
        for block in operation_blocks:
            if self.params.get(block) is not None:
                return True

        return False

    def get_missing_blocks_message(self):
        """Generate appropriate error message when no blocks are defined.

        Returns
        -------
            str: Error message describing which parameter blocks are missing.
        """
        operation_blocks = self.valid_blocks.get(self.operation, [])

        if len(operation_blocks) == 1:
            # Operations like connect, remove require specific block
            return f'Required parameter block {operation_blocks[0]} was not provided for {self.operation} operation, no changes made.'
        else:
            # Operations like update accept multiple blocks
            return f'No parameter blocks were provided for {self.operation} operation. Expected one of: {", ".join(operation_blocks)}. No changes made.'

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

    def _execute_racf_command(self, cmd):
        """Helper method to execute a RACF command and update entity tracking.
        In check_mode, returns the command without executing it.

        Parameters
        ----------
            cmd: str
                The RACF command to execute.

        Returns
        -------
            tuple: RC, stdout, stderr, and the command string.
        """
        # In check_mode, return the command without executing it
        if self.module.check_mode:
            return 0, "No Actual Execution in check mode", "", cmd

        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)

        if rc == 0:
            self.num_entities_modified = 1
            self.entities_modified = [self.name]

        return rc, stdout, stderr, cmd

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
        parts = []
        general = self.params.get('general')

        if general is not None:
            if general.get('custom_fields') is not None:
                if general['custom_fields'].get('add') is not None:
                    custom_fields = general['custom_fields']['add']
                    parts.append('CSDATA( ')
                    for field in custom_fields:
                        parts.append(f'{field}({custom_fields[field]}) ')
                    parts.append(') ')
                elif general['custom_fields'].get('delete') is not None:
                    custom_fields = general['custom_fields']['delete']
                    parts.append('CSDATA( ')
                    for field in custom_fields:
                        parts.append(f'NO{field.upper()} ')
                    parts.append(') ')
                elif general['custom_fields'].get('delete_block') is not None:
                    parts.append('NOCSDATA ')
            if general.get('installation_data') is not None:
                if general.get('installation_data') != "":
                    parts.append(f"DATA('{general['installation_data']}') ")
                else:
                    parts.append("NODATA ")
            if general.get('model') is not None:
                if general.get('model') != "":
                    parts.append(f"MODEL({general['model']}) ")
                else:
                    parts.append("NOMODEL ")
            if general.get('owner') is not None and general.get('owner') != "":
                parts.append(f"OWNER({general['owner']}) ")

        return ''.join(parts)

    def _make_dfp_substring(self):
        """Creates a string that defines the DFP segment of a profile.

        Returns
        -------
            str: DFP segment of a RACF command.
        """
        parts = []
        dfp = self.params.get('dfp')

        if dfp is not None:
            if dfp.get('delete', False):
                return "NODFP"

            parts.append("DFP(")

            if dfp.get('data_app_id') is not None:
                if dfp.get('data_app_id') != "":
                    parts.append(f" DATAAPPL({dfp['data_app_id']})")
                else:
                    parts.append(" NODATAAPPL")
            if dfp.get('data_class') is not None:
                if dfp.get('data_class') != "":
                    parts.append(f" DATACLAS({dfp['data_class']})")
                else:
                    parts.append(" NODATACLAS")
            if dfp.get('management_class') is not None:
                if dfp.get('management_class') != "":
                    parts.append(f" MGMTCLAS({dfp['management_class']})")
                else:
                    parts.append(" NOMGMTCLAS")
            if dfp.get('storage_class') is not None:
                if dfp.get('storage_class') != "":
                    parts.append(f" STORCLAS({dfp['storage_class']})")
                else:
                    parts.append(" NOSTORCLAS")

            parts.append(" )")

        return ''.join(parts)

    def _get_database_info(self):
        """
        Get database space information by checking if the database exists
        and retrieving its total space allocation.

        Returns:
            int: database_total_space in KB
        Raises:
            Exception: If database does not exist
        """
        if not datasets.exists(self.database):
            raise Exception(f"The RACF database {self.database} does not exist. No purge was performed.")

        database_listing = datasets.list_datasets(self.database)[0]
        database_total_space = math.ceil(database_listing.total_space / 1000)

        return database_total_space

    def _run_irrdbu00_utility(self, database_total_space):
        """
        Run the IRRDBU00 utility to dump the RACF database.

        Args:
            database_total_space: Total space allocated for the database

        Returns:
            str: Name of the dump dataset created
        Raises:
            Exception: If utility execution fails
        """
        hlq = self.tmp_hlq if self.tmp_hlq else datasets.get_hlq()
        dump_data_set = datasets.tmp_name(high_level_qualifier=hlq)

        irrdbu00_dds = [
            ztypes.DDStatement('SYSPRINT', '*'),
            ztypes.DDStatement('INDD1', ztypes.DatasetDefinition(
                self.database,
                disposition='SHR'
            )),
            ztypes.DDStatement('OUTDD', ztypes.DatasetDefinition(
                dump_data_set,
                type='SEQ',
                disposition='NEW',
                normal_disposition='CATALOG',
                abnormal_disposition='DELETE',
                device_unit='SYSDA',
                primary=database_total_space,
                primary_unit='KB',
                secondary=math.ceil(database_total_space / 2),
                secondary_unit='KB',
                record_format='VB',
                record_length=4096,
                block_size=20480
            ))
        ]
        lock_input = 'NOLOCKINPUT' if self.optimize_dump else 'LOCKINPUT'
        irrdbu00_response = mvscmd.execute_authorized('IRRDBU00', lock_input, dds=irrdbu00_dds)

        # Check return code from IRRDBU00 execution
        if irrdbu00_response.rc != 0:
            raise Exception(f"IRRDBU00 failed with RC={irrdbu00_response.rc}: {irrdbu00_response.stderr_response}")

        return dump_data_set

    def _run_irrrid00_utility(self, dump_data_set, database_total_space):
        """
        Run the IRRRID00 utility to generate and execute CLIST for profile purge.

        Args:
            dump_data_set: Name of the dump dataset from IRRDBU00
            database_total_space: Total space allocated for the database

        Returns:
            tuple: (rc, stdout, stderr, cmd, clist, out)
        Raises:
            Exception: If utility execution fails
        """
        hlq = self.tmp_hlq if self.tmp_hlq else datasets.get_hlq()
        sysin_name = datasets.tmp_name(high_level_qualifier=hlq)
        clist = datasets.tmp_name(high_level_qualifier=hlq)

        try:
            # Create SYSIN dataset with profile name
            sysin_data_set = datasets.create(
                name=sysin_name,
                dataset_type='SEQ',
                record_format='FB',
                record_length=80,
                device_unit='SYSDA',
                primary=1,
                primary_unit='KB',
                secondary=0,
                secondary_unit='KB',
            )
            datasets.write(sysin_name, self.name, append=False)

            irrrid00_dds = [
                ztypes.DDStatement('SYSPRINT', '*'),
                ztypes.DDStatement('SYSOUT', '*'),
                ztypes.DDStatement('SORTOUT', ztypes.DatasetDefinition(
                    datasets.tmp_name(high_level_qualifier=hlq),
                    type='SEQ',
                    disposition='NEW',
                    normal_disposition='DELETE',
                    abnormal_disposition='DELETE',
                    device_unit='SYSDA',
                    primary=database_total_space,
                    primary_unit='KB',
                    secondary=math.ceil(database_total_space / 2),
                    secondary_unit='KB',
                    record_format='VB',
                    record_length=4096,
                    block_size=20480
                )),
                ztypes.DDStatement('SYSUT1', ztypes.DatasetDefinition(
                    datasets.tmp_name(high_level_qualifier=hlq),
                    type='SEQ',
                    disposition='NEW',
                    normal_disposition='DELETE',
                    abnormal_disposition='DELETE',
                    device_unit='SYSDA',
                    primary=database_total_space,
                    primary_unit='KB',
                    secondary=math.ceil(database_total_space / 2),
                    secondary_unit='KB',
                )),
                ztypes.DDStatement('INDD', ztypes.DatasetDefinition(
                    dump_data_set,
                    disposition='OLD'
                )),
                ztypes.DDStatement('OUTDD', ztypes.DatasetDefinition(
                    clist,
                    type='SEQ',
                    disposition='NEW',
                    normal_disposition='CATALOG',
                    abnormal_disposition='DELETE',
                    device_unit='SYSDA',
                    primary=database_total_space,
                    primary_unit='KB',
                    secondary=math.ceil(database_total_space / 2),
                    secondary_unit='KB',
                    record_format='VB',
                    record_length=259,
                    block_size=1036
                )),
                ztypes.DDStatement('SYSIN', ztypes.DatasetDefinition(
                    sysin_name,
                    disposition='SHR'
                ))
            ]
            irrrid00_response = mvscmd.execute('IRRRID00', dds=irrrid00_dds)

            # Check return code from IRRRID00 execution
            if irrrid00_response.rc != 0:
                raise Exception(f"IRRRID00 failed with RC={irrrid00_response.rc}: {irrrid00_response.stderr_response}")

            # Read the generated CLIST and remove the EXIT statement
            # IRRRID00 includes EXIT as a safety feature to prevent accidental deletion
            # We need to remove it to allow the DELUSER/DELGROUP commands to execute
            clist_content = datasets.read(clist)

            # Handle EXIT statement based on no_exec parameter
            entities_to_modify = []
            if not self.no_exec:
                # Remove the EXIT statement (with surrounding whitespace)
                clist_content_modified = re.sub(r'^\s*EXIT\s*$', '', clist_content, flags=re.MULTILINE)

                # Parse the CLIST to extract entities that will be modified
                # Look for DELUSER and DELGROUP commands in the CLIST
                deluser_pattern = re.compile(r'^\s*DELUSER\s+(\S+)', re.MULTILINE)
                delgroup_pattern = re.compile(r'^\s*DELGROUP\s+(\S+)', re.MULTILINE)

                # Find all DELUSER commands
                for match in deluser_pattern.finditer(clist_content_modified):
                    entity_name = match.group(1).strip()
                    if entity_name and entity_name not in entities_to_modify:
                        entities_to_modify.append(entity_name)

                # Find all DELGROUP commands
                for match in delgroup_pattern.finditer(clist_content_modified):
                    entity_name = match.group(1).strip()
                    if entity_name and entity_name not in entities_to_modify:
                        entities_to_modify.append(entity_name)

                # Write the modified CLIST back to the dataset
                datasets.write(clist, clist_content_modified, append=False)

            cmd = f"EXEC '{clist}'"
            rc, stdout, stderr = self.module.run_command(f"""tsocmd "{cmd}" """)

            # Update entities_modified based on successful execution
            if rc == 0 and entities_to_modify and not self.no_exec:
                self.num_entities_modified = len(entities_to_modify)
                self.entities_modified = entities_to_modify
            else:
                self.num_entities_modified = 0
                self.entities_modified = []

            # Read CLIST content BEFORE cleanup (must be inside try block)
            dcat_cmd = f"dcat {clist}"

            if self.verbosity >= 3:
                dcat_cmd = f"dcat -d {clist}"

            rc_dcat, out, err = self.module.run_command(dcat_cmd)

            if rc_dcat != 0:
                # Log warning if dcat fails but don't fail the operation
                self.module.warn(f"Failed to read CLIST content: RC={rc_dcat}, Error: {err}")
                out = ""  # Provide empty output if dcat fails

            return rc, stdout, stderr, cmd, clist, out
        finally:
            # Cleaning up.
            if datasets.exists(sysin_name):
                datasets.delete(sysin_name)

    def _extract_rc_from_error(self, error_msg):
        """
        Extract return code from error message.

        Args:
            error_msg: Error message string that may contain "RC=<number>"

        Returns:
            int: Extracted RC if found, otherwise 1
        """
        import re
        rc_match = re.search(r'RC=(\d+)', error_msg)
        if rc_match:
            return int(rc_match.group(1))
        return 1

    def _purge_profile(self):
        """
        Purge a RACF profile by running two utilities in sequence:
        1. IRRDBU00 - Dump the RACF database
        2. IRRRID00 - Generate and execute CLIST for profile deletion

        Returns:
            tuple: (rc, stdout, stderr, cmd)
                rc: 0 for success, non-zero for failure
                stdout: Standard output from commands
                stderr: Standard error from commands
                cmd: Command that was executed
        """
        dump_data_set = None
        clist = None

        try:
            # Step 1: Get database space information
            database_total_space = self._get_database_info()
        except Exception as e:
            # Extract RC from exception message if available, otherwise use 1
            error_msg = str(e)
            rc = self._extract_rc_from_error(error_msg)
            return rc, "", f"Failed to get database information: {error_msg}", None

        try:
            # Step 2: Run IRRDBU00 utility to dump the RACF database
            dump_data_set = self._run_irrdbu00_utility(database_total_space)
        except Exception as e:
            # Extract RC from exception message if available, otherwise use 1
            error_msg = str(e)
            rc = self._extract_rc_from_error(error_msg)
            return rc, "", f"Failed to run IRRDBU00 utility: {error_msg}", None

        try:
            # Step 3: Run IRRRID00 utility to generate and execute CLIST
            rc, stdout, stderr, cmd, clist, out = self._run_irrrid00_utility(dump_data_set, database_total_space)

            # Check return code from tsocmd execution
            if rc != 0:
                return rc, stdout, stderr or f"CLIST execution failed with RC={rc}", cmd

            self.database_dumped = True
            self.dump_kept = self.keep_dump
            self.dump_name = dump_data_set if self.keep_dump else None

            return 0, f"dump_data_set: {dump_data_set}, clist: {clist}, output: {out}", "", cmd
        except Exception as e:
            # Extract RC from exception message if available, otherwise use 1
            error_msg = str(e)
            rc = self._extract_rc_from_error(error_msg)
            return rc, "", f"Failed to run IRRRID00 utility: {error_msg}", None
        finally:
            # Clean up dump datasets if keep_dump is False
            if not self.keep_dump:
                if clist and datasets.exists(clist):
                    datasets.delete(clist)
                if dump_data_set and datasets.exists(dump_data_set):
                    datasets.delete(dump_data_set)


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
                ('omvs', ('uid', 'custom_uid', 'delete')),
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
        'list': [],
        # Note: 'connect' and 'remove' operations are not supported for groups
        # and are intentionally included here. If attempted, execute_operation()
        # will provide a clear error message.
        'connect': [],
        'remove': []
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
        elif self.operation == 'update':
            rc, stdout, stderr, cmd = self._update_group()
        elif self.operation == 'delete':
            rc, stdout, stderr, cmd = self._delete_group()
        elif self.operation == 'purge':
            rc, stdout, stderr, cmd = self._purge_profile()
        else:
            self.module.fail_json(
                msg=f"Operation '{self.operation}' is not supported for group profiles. "
                    f"Supported operations for groups: create, update, delete, purge"
            )

        self.cmd = cmd
        # Getting the base dictionary.
        result = super().execute_operation()
        result['rc'] = rc
        result['stdout'] = stdout
        result['stderr'] = stderr
        return result

    def _group_exists(self) -> Any:
        """Check if a group profile exists in RACF using LISTGRP command.

        Returns
        -------
            bool: True if group exists (RC=0), False otherwise
        """
        cmd = f'LISTGRP ({self.name})'
        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)
        return rc == 0

    def _create_group(self):
        """Builds and execute an ADDGROUP command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ADDGROUP command.
        """
        # Check if group already exists
        if self._group_exists():
            cmd = f'ADDGROUP ({self.name})'
            return 0, f"Group {self.name} already exists", "", cmd

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

        return self._execute_racf_command(cmd)

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
            elif omvs.get('uid') == 'auto':
                cmd = f'{cmd} OMVS(AUTOGID)'
            elif omvs.get('uid') != 'none' and omvs.get('uid') in ('custom', 'shared'):
                cmd = f"{cmd} OMVS(GID({omvs['custom_uid']})"
                if omvs['uid'] == 'shared':
                    cmd = f'{cmd}SHARED'
                cmd = f'{cmd})'
            elif omvs.get('uid') == 'none':
                cmd = f'{cmd} OMVS(NOGID)'

        return self._execute_racf_command(cmd)

    def _delete_group(self):
        """Builds and execute a DELGROUP command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the DELGROUP command.
        """
        # Check if group exists
        if not self._group_exists():
            cmd = f'DELGROUP ({self.name})'
            return 0, f"Group {self.name} does not exist", "", cmd

        cmd = f'DELGROUP ({self.name})'

        return self._execute_racf_command(cmd)

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
                ('omvs', ('uid', 'custom_uid', 'home', 'program', 'nonshared_size', 'shared_size',
                          'addr_space_size', 'map_size', 'max_procs', 'max_threads', 'max_cpu_time', 'max_files')),
                ('tso', ('account_num', 'logon_cmd', 'logon_proc', 'dest_id', 'hold_class', 'job_class',
                         'msg_class', 'sysout_class', 'region_size', 'max_region_size', 'security_label',
                         'unit_name', 'user_data')),
                ('access', ('default_group', 'clauth', 'roaudit', 'category', 'operator_card',
                            'maintenance_access', 'restricted', 'security_label', 'security_level')),
                ('operator', ('alt_group', 'authority', 'cmd_system', 'search_key', 'migration_id', 'display',
                              'msg_level', 'msg_format', 'msg_storage', 'msg_scope', 'automated_msgs', 'del_msgs',
                              'hardcopy_msgs', 'internal_msgs', 'routing_msgs', 'undelivered_msgs', 'unknown_msgs',
                              'responses')),
                ('restrictions', ('days', 'time', 'resume', 'revoke')),
                ('password_mgmt', ('password', 'passphrase', 'expired'))
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
        'update': ['general', 'dfp', 'language', 'omvs', 'tso', 'access', 'operator', 'restrictions', 'password_mgmt'],
        'delete': [],
        'purge': [],
        'list': [],
        'connect': ['connect'],
        'remove': ['connect']
    }

    validations = [
        (('general', 'user_name'), 'length', ((0, 20),)),
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
        (('tso', 'user_data'), 'format', (r'[^\s*$]|[0-9a-zA-Z]{4}',)),
        (('operator', 'alt_group'), 'length', ((0, 8),)),
        (('operator', 'cmd_system'), 'length', ((0, 8),)),
        (('operator', 'search_key'), 'length', ((0, 8),)),
        (('operator', 'msg_storage'), 'range', (1, 2000, 0)),
        (('restrictions', 'time'), 'format', ('^([01]?[0-9]|2[0-3])[0-5][0-9]:([01]?[0-9]|2[0-3])[0-5][0-9]$', 'anytime')),
        (('restrictions', 'resume'), 'format', ('^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/([0-9]{2})$',)),
        (('restrictions', 'revoke'), 'format', ('^(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/([0-9]{2})$',)),
        (('password_mgmt', 'password'), 'length', ((0, 8),)),
        # passphrase validation is handled in validate_params() method
        # to allow empty string (0) OR 9-100 chars, but not 1-8 chars
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
                nonshared_size = int(nonshared_size[:len(nonshared_size) - 1])
                if nonshared_size < 0 or nonshared_size > 16_777_215:
                    raise ValueError('Value of omvs.nonshared_size is outside of its range.')

            if self.params['omvs'].get('shared_size') is not None:
                shared_size = self.params['omvs']['shared_size']
                shared_size = int(shared_size[:len(shared_size) - 1])
                if shared_size < 1 or shared_size > 16_777_215:
                    raise ValueError('Value of omvs.shared_size is outside of its range.')

        # Validate password_mgmt parameters
        if self.params.get('password_mgmt') is not None:
            password_mgmt = self.params['password_mgmt']
            expired = password_mgmt.get('expired')
            password = password_mgmt.get('password')
            passphrase = password_mgmt.get('passphrase')

            # Validate expired can only be used with password or passphrase
            if expired is not None and password is None and passphrase is None:
                raise ValueError(
                    "The 'expired' parameter can only be used when 'password' or 'passphrase' is also specified. "
                    "RACF does not allow EXPIRED/NOEXPIRED to be set independently."
                )

            # Validate passphrase: must be empty string (for NOPHRASE) OR 9-100 chars
            if passphrase is not None and len(passphrase) > 0:
                if len(passphrase) < 9 or len(passphrase) > 100:
                    raise ValueError(
                        "Passphrase must be either empty string (to remove passphrase) or 9-100 characters long."
                    )

    def execute_operation(self):
        """Given the operation and scope, it executes a RACF command.

        Returns
        -------
            tuple: Return code, standard output and standard error from the command.
        """
        if self.operation == 'create':
            rc, stdout, stderr, cmd = self._create_user()
        elif self.operation == 'update':
            rc, stdout, stderr, cmd = self._update_user()
        elif self.operation == 'delete':
            rc, stdout, stderr, cmd = self._delete_user()
        elif self.operation == 'purge':
            rc, stdout, stderr, cmd = self._purge_profile()
        elif self.operation == 'connect':
            rc, stdout, stderr, cmd = self._connect_user()
        elif self.operation == 'remove':
            rc, stdout, stderr, cmd = self._remove_user()

        self.cmd = cmd

        # Getting the base dictionary.
        result = super().execute_operation()
        result['rc'] = rc
        result['stdout'] = stdout
        result['stderr'] = stderr
        return result

    def _user_exists(self):
        """Check if a user profile exists in RACF using LISTUSER command.

        Returns
        -------
            bool: True if user exists (RC=0), False otherwise
        """
        cmd = f'LISTUSER ({self.name})'
        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{cmd}" """)
        return rc == 0

    def _create_user(self):
        """Builds and execute an ADDUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ADDUSER command.
        """
        # Check if user already exists
        if self._user_exists():
            cmd = f'ADDUSER ({self.name})'
            return 0, f"User {self.name} already exists", "", cmd

        cmd = f'ADDUSER ({self.name})'

        # Add NAME parameter if user_name is provided in general block
        general = self.params.get('general', {})
        if general and general.get('user_name') is not None and general.get('user_name') != "":
            cmd = f"{cmd} NAME('{general['user_name']}')"

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_language_substring()}'.strip()
        cmd = f'{cmd} {self._make_tso_substring()}'.strip()
        cmd = f'{cmd} {self._make_omvs_substring()}'.strip()
        cmd = f'{cmd} {self._make_access_substring_creation()}'.strip()
        cmd = f'{cmd} {self._make_restrictions_substring()}'.strip()
        cmd = f'{cmd} {self._make_operator_substring()}'.strip()
        cmd = f'{cmd} {self._make_password_mgmt_substring()}'.strip()

        return self._execute_racf_command(cmd)

    def _update_user(self):
        """Builds and execute an ALTUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the ALTUSER command.
        """
        cmd = f'ALTUSER ({self.name})'

        # Add NAME parameter if user_name is provided in general block
        general = self.params.get('general', {})
        if general and general.get('user_name') is not None:
            if general['user_name'] == "":
                # Empty string resets NAME to default (displays as UNKNOWN)
                cmd = f"{cmd} NAME()"
            else:
                # Non-empty string sets the actual name
                cmd = f"{cmd} NAME('{general['user_name']}')"

        cmd = f'{cmd} {self._make_general_string()}'.strip()
        cmd = f'{cmd} {self._make_dfp_substring()}'.strip()
        cmd = f'{cmd} {self._make_language_substring()}'.strip()
        cmd = f'{cmd} {self._make_tso_substring()}'.strip()
        cmd = f'{cmd} {self._make_omvs_substring()}'.strip()
        cmd = f'{cmd} {self._make_access_substring_creation()}'.strip()
        cmd = f'{cmd} {self._make_restrictions_substring()}'.strip()
        cmd = f'{cmd} {self._make_operator_substring()}'.strip()
        cmd = f'{cmd} {self._make_password_mgmt_substring()}'.strip()

        return self._execute_racf_command(cmd)

    def _delete_user(self):
        """Builds and execute a DELUSER command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the DELUSER command.
        """
        # Check if user exists
        if not self._user_exists():
            cmd = f'DELUSER ({self.name})'
            return 0, f"User {self.name} does not exist", "", cmd

        cmd = f'DELUSER ({self.name})'

        return self._execute_racf_command(cmd)

    def _user_connected_to_group(self, group_name):
        """Check if a user is already connected to a group.

        Parameters
        ----------
            group_name: str
                The group name to check connection for.

        Returns
        -------
            bool: True if user is connected to the group, False otherwise.
        """
        import re
        check_cmd = f'LISTUSER {self.name}'
        rc, stdout, stderr = self.module.run_command(f""" tsocmd "{check_cmd}" """)
        if rc == 0:
            # Check if the group appears in the user's group list
            # LISTUSER output includes "GROUP=" or "CONNECTS=" sections showing group memberships
            # Use word boundary regex to match exact group name, not substrings
            pattern = r'\b' + re.escape(group_name.upper()) + r'\b'
            return re.search(pattern, stdout.upper()) is not None
        return False

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

        return self._execute_racf_command(cmd)

    def _remove_user(self):
        """Builds and execute a REMOVE command.

        Returns
        -------
            tuple: RC, stdout and stderr from the RACF command, and the REMOVE command.
        """
        cmd = f'REMOVE ({self.name}) '

        connect = self.params.get('connect')

        if connect.get('group_name') is not None:
            group_name = connect['group_name']
            cmd = f"{cmd}GROUP({group_name})"

            # Check if user is connected to this group before attempting remove for idempotency
            if not self._user_connected_to_group(group_name):
                # User not connected - idempotent behavior, return success with no changes
                self.num_entities_modified = 0
                self.entities_modified = []
                return 0, f"User {self.name} is not connected to group {group_name}", "", cmd
        else:
            return 1, "", "No group was provided for a remove operation.", cmd

        if self.params.get('general') is not None:
            if self.params['general'].get('owner') is not None:
                cmd = f"{cmd} OWNER({self.params['general']['owner']})"

        return self._execute_racf_command(cmd)

    def _make_language_substring(self):
        """Creates a string that defines the LANGUAGE block of a user profile.

        Returns
        -------
            str: LANGUAGE parameters of a RACF command.
        """
        parts = []
        language = self.params.get('language')

        if language is not None:
            if language.get('delete', False):
                return "NOLANGUAGE"

            parts.append("LANGUAGE(")

            if language.get('primary') is not None:
                if language.get('primary') != "":
                    parts.append(f" PRIMARY({language['primary']})")
                else:
                    parts.append(" NOPRIMARY")
            if language.get('secondary') is not None:
                if language.get('secondary') != "":
                    parts.append(f" SECONDARY({language['secondary']})")
                else:
                    parts.append(" NOSECONDARY")

            parts.append(" )")

        return ''.join(parts)

    def _make_omvs_substring(self):
        """Creates a string that defines the OMVS (Unix System Services) block of
        a user profile.

        Returns
        -------
            str: OMVS parameters of a RACF command.
        """
        parts = []
        omvs = self.params.get('omvs')

        if omvs is not None:
            if omvs.get('delete', False):
                return "NOOMVS"

            parts.append("OMVS(")

            if omvs.get('uid') == 'auto':
                parts.append(' AUTOUID')
            elif omvs.get('uid') != 'none' and omvs.get('uid') in ('custom', 'shared'):
                parts.append(f" UID({omvs['custom_uid']})")
                if omvs['uid'] == 'shared':
                    parts.append('SHARED')
            elif omvs.get('uid') == 'none':
                parts.append(' NOUID')

            if omvs.get('home') is not None:
                if omvs.get('home') != "":
                    parts.append(f" HOME({omvs['home']})")
                else:
                    parts.append(" NOHOME")
            if omvs.get('program') is not None:
                if omvs.get('program') != "":
                    parts.append(f" PROGRAM({omvs['program']})")
                else:
                    parts.append(" NOPROGRAM")
            if omvs.get('nonshared_size') is not None:
                if omvs.get('nonshared_size') != "":
                    parts.append(f" MEMLIMIT({omvs['nonshared_size']})")
                else:
                    parts.append(" NOMEMLIMIT")
            if omvs.get('shared_size') is not None:
                if omvs.get('shared_size') != "":
                    parts.append(f" SHMEMMAX({omvs['shared_size']})")
                else:
                    parts.append(" NOSHMEMMAX")
            if omvs.get('addr_space_size') is not None:
                if omvs.get('addr_space_size') != 0:
                    parts.append(f" ASSIZEMAX({omvs['addr_space_size']})")
                else:
                    parts.append(" NOASSIZEMAX")
            if omvs.get('map_size') is not None:
                if omvs.get('map_size') != 0:
                    parts.append(f" MMAPAREAMAX({omvs['map_size']})")
                else:
                    parts.append(" NOMMAPAREAMAX")
            if omvs.get('max_procs') is not None:
                if omvs.get('max_procs') != 0:
                    parts.append(f" PROCUSERMAX({omvs['max_procs']})")
                else:
                    parts.append(" NOPROCUSERMAX")
            if omvs.get('max_threads') is not None:
                if omvs.get('max_threads') != -1:
                    parts.append(f" THREADSMAX({omvs['max_threads']})")
                else:
                    parts.append(" NOTHREADSMAX")
            if omvs.get('max_cpu_time') is not None:
                if omvs.get('max_cpu_time') != 0:
                    parts.append(f" CPUTIMEMAX({omvs['max_cpu_time']})")
                else:
                    parts.append(" NOCPUTIMEMAX")
            if omvs.get('max_files') is not None:
                if omvs.get('max_files') != 0:
                    parts.append(f" FILEPROCMAX({omvs['max_files']})")
                else:
                    parts.append(" NOFILEPROCMAX")

            parts.append(" )")

        return ''.join(parts)

    def _make_tso_substring(self):
        """Creates a string that defines the TSO block of a user profile.

        Returns
        -------
            str: TSO parameters of a RACF command.
        """
        parts = []
        tso = self.params.get('tso')

        if tso is not None:
            if tso.get('delete', False):
                return "NOTSO"

            parts.append("TSO(")

            if tso.get('account_num') is not None:
                if tso.get('account_num') != "":
                    parts.append(f" ACCTNUM({tso['account_num']})")
                else:
                    parts.append(" NOACCTNUM")
            if tso.get('logon_cmd') is not None:
                if tso.get('logon_cmd') != "":
                    parts.append(f" COMMAND({tso['logon_cmd']})")
                else:
                    parts.append(" NOCOMMAND")
            if tso.get('dest_id') is not None:
                if tso.get('dest_id') != "":
                    parts.append(f" DEST({tso['dest_id']})")
                else:
                    parts.append(" NODEST")
            if tso.get('hold_class') is not None:
                if tso.get('hold_class') != "":
                    parts.append(f" HOLDCLASS({tso['hold_class']})")
                else:
                    parts.append(" NOHOLDCLASS")
            if tso.get('job_class') is not None:
                if tso.get('job_class') != "":
                    parts.append(f" JOBCLASS({tso['job_class']})")
                else:
                    parts.append(" NOJOBCLASS")
            if tso.get('msg_class') is not None:
                if tso.get('msg_class') != "":
                    parts.append(f" MSGCLASS({tso['msg_class']})")
                else:
                    parts.append(" NOMSGCLASS")
            if tso.get('sysout_class') is not None:
                if tso.get('sysout_class') != "":
                    parts.append(f" SYS({tso['sysout_class']})")
                else:
                    parts.append(" NOSYS")
            if tso.get('region_size') is not None:
                if tso.get('region_size') != -1:
                    parts.append(f" SIZE({tso['region_size']})")
                else:
                    parts.append(" NOSIZE")
            if tso.get('max_region_size') is not None:
                if tso.get('max_region_size') != -1:
                    parts.append(f" MAXSIZE({tso['max_region_size']})")
                else:
                    parts.append(" NOMAXSIZE")
            if tso.get('logon_proc') is not None:
                if tso.get('logon_proc') != "":
                    parts.append(f" PROC({tso['logon_proc']})")
                else:
                    parts.append(" NOPROC")
            if tso.get('security_label') is not None:
                if tso.get('security_label') != "":
                    parts.append(f" SECLABEL({tso['security_label']})")
                else:
                    parts.append(" NOSECLABEL")
            if tso.get('unit_name') is not None:
                if tso.get('unit_name') != "":
                    parts.append(f" UNIT({tso['unit_name']})")
                else:
                    parts.append(" NOUNIT")
            if tso.get('user_data') is not None:
                if tso.get('user_data') != "":
                    parts.append(f" USERDATA({tso['user_data']})")
                else:
                    parts.append(" NOUSERDATA")

            parts.append(" )")

        return ''.join(parts)

    def _make_operator_substring(self):
        """Creates a string that defines the OPERATOR block of a user profile.

        Returns
        -------
            str: OPERATOR parameters of a RACF command.
        """
        parts = []
        operator = self.params.get('operator')

        if operator is not None:
            if operator.get('delete', False):
                return "NOOPERPARM"

            parts.append("OPERPARM(")

            if operator.get('alt_group') is not None:
                if operator.get('alt_group') != "":
                    parts.append(f" ALTGRP({operator['alt_group']})")
                else:
                    parts.append(" NOALTGRP")
            if operator.get('authority') is not None:
                if operator.get('authority') != "delete":
                    parts.append(f" AUTH({operator['authority']})")
                else:
                    parts.append(" NOAUTH")
            if operator.get('cmd_system') is not None:
                if operator.get('cmd_system') != "":
                    parts.append(f" CMDSYS({operator['cmd_system']})")
                else:
                    parts.append(" NOCMDSYS")
            if operator.get('search_key') is not None:
                if operator.get('search_key') != "":
                    parts.append(f" KEY({operator['search_key']})")
                else:
                    parts.append(" NOKEY")
            if operator.get('migration_id', False):
                parts.append(" MIGID(YES)")
            else:
                parts.append(" MIGID(NO)")
            if operator.get('display') is not None:
                if "delete" not in operator['display']:
                    options = operator['display']
                    parts.append(' MONITOR( ')
                    for option in options:
                        parts.append(f'{option} ')
                    parts.append(') ')
                else:
                    parts.append(" NOMONITOR")
            if operator.get('msg_level') is not None:
                if operator.get('msg_level') != "delete":
                    parts.append(f" LEVEL({operator['msg_level']})")
                else:
                    parts.append(" NOLEVEL")
            if operator.get('msg_format') is not None:
                if operator.get('msg_format') != 'delete':
                    parts.append(f" MFORM({operator['msg_format']})")
                else:
                    parts.append(" NOMFORM")
            if operator.get('msg_storage') is not None:
                if operator.get('msg_storage') != 0:
                    parts.append(f" STORAGE({operator['msg_storage']})")
                else:
                    parts.append(" NOSTORAGE")
            if operator.get('msg_scope') is not None:
                if operator['msg_scope'].get('add') is not None:
                    scopes = operator['msg_scope']['add']
                    # added MSCOPE command option for create option
                    if self.operation == 'create':
                        parts.append('MSCOPE( ')
                    elif self.operation == 'update':
                        parts.append('ADDMSCOPE( ')
                    for scope in scopes:
                        parts.append(f'{scope} ')
                    parts.append(') ')
                elif operator['msg_scope'].get('delete') is not None:
                    scopes = operator['msg_scope']['delete']
                    parts.append('DELMSCOPE( ')
                    for scope in scopes:
                        parts.append(f'{scope} ')
                    parts.append(') ')
                else:
                    parts.append('NOMSCOPE')
            if operator.get('automated_msgs', False):
                parts.append(" AUTO(YES)")
            else:
                parts.append(" AUTO(NO)")
            if operator.get('del_msgs') is not None:
                if operator.get('del_msgs') != 'delete':
                    parts.append(f" DOM({operator['del_msgs']})")
                else:
                    parts.append(" NODOM")
            if operator.get('hardcopy_msgs', False):
                parts.append(" HC(YES)")
            else:
                parts.append(" HC(NO)")
            if operator.get('internal_msgs', False):
                parts.append(" INTIDS(YES)")
            else:
                parts.append(" INTIDS(NO)")
            if operator.get('routing_msgs') is not None:
                routes = operator['routing_msgs']
                parts.append(' ROUTCODE( ')
                for route in routes:
                    parts.append(f'{route} ')
                parts.append(') ')
            if operator.get('undelivered_msgs', False):
                parts.append(" UD(YES)")
            else:
                parts.append(" UD(NO)")
            if operator.get('unknown_msgs', False):
                parts.append(" UNKNIDS(YES)")
            else:
                parts.append(" UNKNIDS(NO)")
            if operator.get('responses', False):
                parts.append(" LOGCMDRESP(SYSTEM)")
            else:
                parts.append(" LOGCMDRESP(NO)")

            parts.append(" )")

        return ''.join(parts)

    def _make_access_substring_creation(self):
        """Creates a string that defines various parameters for a user profile.

        Returns
        -------
            str: User create/alter parameters of a RACF command.
        """
        parts = []
        access = self.params.get('access')

        if access is not None:
            if access.get('default_group') is not None:
                parts.append(f"DFLTGRP({access['default_group']}) ")
            if access.get('clauth') is not None:
                if access['clauth'].get('add') is not None:
                    clauth = access['clauth']['add']
                    parts.append('CLAUTH( ')
                    for auth_class in clauth:
                        parts.append(f'{auth_class} ')
                    parts.append(') ')
                elif access['clauth'].get('delete') is not None:
                    clauth = access['clauth']['delete']
                    parts.append('NOCLAUTH( ')
                    for auth_class in clauth:
                        parts.append(f'{auth_class} ')
                    parts.append(') ')
            if access.get('roaudit') is not None:
                roaudit = "ROAUDIT" if access['roaudit'] else "NOROAUDIT"
                parts.append(f'{roaudit} ')
            if access.get('category') is not None:
                if access['category'].get('add') is not None:
                    categories = access['category']['add']
                    parts.append('ADDCATEGORY( ')
                    for category in categories:
                        parts.append(f'{category} ')
                    parts.append(') ')
                elif access['category'].get('delete') is not None:
                    categories = access['category']['delete']
                    parts.append('DELCATEGORY( ')
                    for category in categories:
                        parts.append(f'{category} ')
                    parts.append(') ')
            if access.get('operator_card') is not None:
                op_card = "OIDCARD" if access['operator_card'] else "NOOIDCARD"
                parts.append(f'{op_card} ')
            if access.get('maintenance_access') is not None:
                operations = "OPERATIONS" if access['maintenance_access'] else "NOOPERATIONS"
                parts.append(f'{operations} ')
            if access.get('restricted') is not None:
                restricted = "RESTRICTED" if access['restricted'] else "NORESTRICTED"
                parts.append(f'{restricted} ')
            if access.get('security_label') is not None:
                if access.get('security_label') != "":
                    parts.append(f"SECLABEL({access['security_label']}) ")
                else:
                    parts.append("NOSECLABEL ")
            if access.get('security_level') is not None:
                if access.get('security_level') != "":
                    parts.append(f"SECLEVEL({access['security_level']}) ")
                else:
                    parts.append("NOSECLEVEL ")

        return ''.join(parts)

    def _make_restrictions_substring(self):
        """Creates a string that defines various parameters for how a user can
        access a system.

        Returns
        -------
            str: User parameters of a RACF command.
        """
        parts = []
        restrictions = self.params.get('restrictions')

        if restrictions is not None:
            if restrictions.get('days') is not None or restrictions.get('time') is not None:
                parts.append("WHEN( ")
                if restrictions.get('days') is not None:
                    parts.append("DAYS( ")
                    for day in restrictions['days']:
                        parts.append(f"{day} ")
                    parts.append(") ")
                if restrictions.get('time') is not None:
                    parts.append(f"TIME({restrictions['time']}) ")
                parts.append(") ")

            if restrictions.get('resume') is not None:
                parts.append(f"RESUME({restrictions['resume']})")
            elif restrictions.get('delete_resume', False):
                parts.append("NORESUME ")

            if restrictions.get('revoke') is not None:
                parts.append(f"REVOKE({restrictions['revoke']})")
            elif restrictions.get('delete_revoke', False):
                parts.append("NOREVOKE ")

        return ''.join(parts)

    def _make_password_mgmt_substring(self):
        """Creates a string that defines password management parameters for a user.

        Returns
        -------
            str: Password management parameters of a RACF command.
        """
        cmd = ""
        password_mgmt = self.params.get('password_mgmt')

        if password_mgmt is not None:
            # Handle password or passphrase (mutually exclusive at module level)
            # Note: RACF does not automatically clear the opposite authentication method
            # Users must explicitly clear passphrase when setting password (and vice versa)
            if password_mgmt.get('password') is not None:
                if password_mgmt['password'] == "":
                    # Empty string removes password
                    cmd = f"{cmd}NOPASSWORD "
                else:
                    cmd = f"{cmd}PASSWORD({password_mgmt['password']}) "
            elif password_mgmt.get('passphrase') is not None:
                if password_mgmt['passphrase'] == "":
                    # Empty string removes passphrase
                    cmd = f"{cmd}NOPHRASE "
                else:
                    cmd = f"{cmd}PHRASE('{password_mgmt['passphrase']}') "

            # Handle expired flag (only for update operations)
            if password_mgmt.get('expired') is not None:
                if password_mgmt['expired']:
                    cmd = f"{cmd}EXPIRED "
                else:
                    cmd = f"{cmd}NOEXPIRED "

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
                'choices': ['create', 'update', 'delete', 'purge', 'connect', 'remove']
            },
            'scope': {
                'type': 'str',
                'required': True,
                'choices': ['user', 'group']
            },
            'database': {
                'type': 'str',
                'required': False
            },
            'keep_dump': {
                'type': 'bool',
                'default': False
            },
            'optimize_dump': {
                'type': 'bool',
                'default': True
            },
            'no_exec': {
                'type': 'bool',
                'required': False,
                'default': False
            },
            'tmp_hlq': {
                'type': 'str',
                'required': False
            },
            'general': {
                'type': 'dict',
                'required': False,
                'options': {
                    'user_name': {
                        'type': 'str',
                        'required': False
                    },
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
                        'required': False,
                        'no_log': False
                    },
                    'migration_id': {
                        'type': 'bool',
                        'required': False,
                        'default': False
                    },
                    'display': {
                        'type': 'list',
                        'elements': 'str',
                        'required': False,
                        'choices': ['jobnames', 'jobnamest', 'sess', 'sesst', 'status', 'delete']
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
                                'type': 'list',
                                'elements': 'str',
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
                        'type': 'list',
                        'elements': 'str',
                        'required': False,
                        'choices': ['anyday', 'weekdays', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                        'default': ['anyday']
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
            },
            'password_mgmt': {
                'type': 'dict',
                'required': False,
                'no_log': False,
                'mutually_exclusive': [
                    ('password', 'passphrase')
                ],
                'options': {
                    'password': {
                        'type': 'str',
                        'required': False,
                        'no_log': True
                    },
                    'passphrase': {
                        'type': 'str',
                        'required': False,
                        'no_log': True
                    },
                    'expired': {
                        'type': 'bool',
                        'required': False
                    },
                }
            }
        },
        # Require database when operation=purge.
        required_if=[('operation', 'purge', ('database',))],
        supports_check_mode=True
    )

    validate_dependencies(module)

    args_def = {
        'name': {'arg_type': 'str', 'required': True, 'aliases': ['src']},
        'operation': {'arg_type': 'str', 'required': True},
        'scope': {'arg_type': 'str', 'required': True},
        'database': {'arg_type': 'str', 'required': False},
        'keep_dump': {'arg_type': 'bool', 'required': True},
        'optimize_dump': {'arg_type': 'bool', 'required': True},
        'no_exec': {'arg_type': 'bool', 'required': False},
        'tmp_hlq': {'arg_type': 'str', 'required': False},
        'general': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'user_name': {'arg_type': 'str', 'required': False},
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
                        'delete': {'arg_type': 'list', 'elements': 'str', 'required': False}
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
        },
        'password_mgmt': {
            'arg_type': 'dict',
            'required': False,
            'options': {
                'password': {'arg_type': 'str', 'required': False},
                'passphrase': {'arg_type': 'str', 'required': False},
                'expired': {'arg_type': 'bool', 'required': False},
            }
        }
    }

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        result = RACFHandler._get_validation_error_result(
            error_msg=str(err),
            rc=1
        )
        result['msg'] = 'Parameter verification failed.'
        module.fail_json(**result)

    # Initialize logging module
    module_verbosity_level = module._verbosity
    logger = SingletonLogger().get_logger(module_verbosity_level)
    logger.info("Logger initialized successfully")

    operation_handler = get_racf_handler(module, module.params)
    operation_handler.clean_input()
    if not operation_handler.are_blocks_defined():
        result = operation_handler.get_state()
        result['msg'] = operation_handler.get_missing_blocks_message()
        module.exit_json(**result)

    try:
        operation_handler.validate_params()
    except ValueError as err:
        result = operation_handler.get_state()
        result['msg'] = str(err)
        module.fail_json(**result)

    # In check_mode for purge operation, set no_exec to True to prevent execution
    if module.check_mode:
        module.params['no_exec'] = True

    result = operation_handler.execute_operation()

    if module.check_mode:
        # In check_mode, determine if changes would be made
        # changed=true if operation would execute, changed=false if already in desired state
        stdout = result.get('stdout', '')
        cmd = result.get('cmd', '')

        # Check if entity already in desired state (no changes needed)
        pattern = r'already exists|does not exist|not connected to group'
        if re.search(pattern, stdout, re.IGNORECASE):
            result['changed'] = False
            result['stdout'] = ""
            result['num_entities_modified'] = 0
            result['msg'] = stdout
        else:
            result['changed'] = True
            result['msg'] = ""
            result['stdout'] = stdout if module.params.get('operation', '').lower() == 'purge' else ""
            result['num_entities_modified'] = 1
            result['entities_modified'] = module.params['name']

        module.exit_json(**result)

    # Clear stderr if it only contains the command echo (TSO behavior)
    if result.get('cmd') and result.get('stderr'):
        if result['stderr'].strip() == result['cmd'].strip():
            result['stderr'] = ""

    result['stdout_lines'] = result['stdout'].split('\n')
    result['stderr_lines'] = result['stderr'].split('\n')

    if result['rc'] == 0:
        result['changed'] = result['num_entities_modified'] > 0

        # Successful message
        if 'msg' not in result:
            result['msg'] = 'Command executed successfully.'

        # Successful exit
        module.exit_json(**result)
    else:
        result['changed'] = False
        result['msg'] = 'An error occurred while executing the RACF command.'
        module.fail_json(**result)


if __name__ == '__main__':
    run_module()
