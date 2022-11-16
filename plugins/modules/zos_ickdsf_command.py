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

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


DOCUMENTATION = r"""
module: zos_icsdsf_command
author:
  - "Austen Stewart"
  - "Nuoya Xie"
  - "Trevor Glassey"
Team: JumpStart Team 8
  - "Austen Stewart"
  - "Almigdad Suliman"
  - "Nicholas Teves"
  - "Nuoya Xie"
  - "Trevor Glassey"
  - "Tyler Edwards"
Date: 07/2021
short_description: ICKDSF Playbook data manipulation to utilize zos_mvs_raw.
description:
  - Issue init command using MVS.
  - Transforms playbook to work with existing zos_mvs_raw module.
  - Action plugin executes on host before zos_mvs_raw is executed.

options:
  init:
    description:
      - Contains the supported ICKDSF INIT command parameters.
    required: false
    type: dict
      suboptions:
        volume_address:
          description:
            - 3 or 4 hexadecimal digits that contain the address of the volume to initialize.
          required: true
          type: str
        verify_existing_volid:
          description:
            - Used to indicate one of the following
            - Verification that an existing volume serial number does not exist for the volume by not including it.
            - Verification that the volume contains an existing specific volume serial number. This would be indicated
              by 1 to 6 alphanumeric characters that would contain the serial number that you wish to verify currently exists on the volume.
          required: false
          type: str
        verify_offline:
          description:
            - Used to indicate if verification should be done to verify that the volume is offline to all host systems.
              If this parameter is not specified, the default set up on the system that you are running the command to will be used.
          type: bool
          default: true
        volid:
          description:
            - This is used to indicate the 1 to 6 alphanumeric character volume serial number that you want to initialize the volume with.
          required: false
          type: str
        vtoc_tracks:
          description:
            - This is used to indicate the number of tracks to initialize the VTOC with. The VTOC will be placed at cylinder 0 head 1
              for the number of tracks specified.
          required: false
          type: int
        index:
          description:
            - This is used to indicate if a VTOC index should be created when initializing the volume.
              The index size will be created based on the size of the volume and the size of the VTOC that was created.
              The Index will be placed on the volume after the VTOC. If this parameter is not specified an index will be created on the volume.
          type: bool
          default: true
        sms_managed:
          description:
            - Assigned to be managed by Storage Management System (SMS).
          type: bool
          default: true
        verify_no_data_sets_exist:
          description:
            - This is used to verify if data sets other than the VTOC index data set and/or VVDS exist on the volume to be initialized.
              If this parameter is not specified, the default set up on the system you are running the command to will be used.
          type: bool
          default: true
        addr_range:
          description:
            - If initializing a range of volumes, how many additional addresses to initialize
          required: false
          type: int
        volid_prefix:
          description:
            - If initializing a range of volumes, the prefix of volume IDs to initialize. This with have the address appended to it.
          required: false
          type: str
  output_html:
    description:
      - Options for creating HTML output of ICKDSF command
    required: false
    type: dict
    suboptions:
      full_file path:
        description:
          - File path to place output HTML file
        required: true
        type: str
      append:
        description:
          - Optionally append to file, instead of overwriting
        type: bool
        default: true
  """
EXAMPLES = r"""

---
  - hosts: all
    collections:
    - ibm.ibm_zos_core
    gather_facts: no
    environment: "{{ environment_vars }}"
    connection: ibm.ibm_zos_core.zos_ssh
    become: false
    tasks:
      - name: Initialize a new dasd volume for use on a z/OS system and save the output to a html file.
        zos_ickdsf_command:
          init:
            volume_address: e8d8
            verify_existing_volid: ine8d8
            verify_offline: no
            volid: ine8d8
            vtoc_tracks: 30
            index: yes
            sms_managed: yes
            verify_no_data_sets_exist: yes
          output_html:
            full_file_path: ./test.html
            append: yes
        register: response

      - name: Print return information from the previous task
        ansible.builtin.debug:
          var: response


---
  - hosts: all
    collections:
    - ibm.ibm_zos_core
    gather_facts: no
    environment: "{{ environment_vars }}"
    connection: ibm.ibm_zos_core.zos_ssh
    become: false
    tasks:
      - name: Initialize 3 new dasd volume for use on a z/OS system and save the output to a html file. These additional will be set as ine8d9 and ine8da
        zos_ickdsf_command:
          init:
            volume_address: e8d8
            verify_offline: no
            volid: ine8d8
            vtoc_tracks: 30
            index: yes
            sms_managed: yes
            verify_no_data_sets_exist: yes
            addr_range: 2
            volid_prefix: in
          output_html:
            full_file_path: ./test.html
            append: yes
        register: response

      - name: Print return information from the previous task
        ansible.builtin.debug:
          var: response
"""

from ansible.module_utils.basic import AnsibleModule
from locale import Error
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import better_arg_parser


class IckdsfError(Error):
    '''
    Error class for errors specific to ICKDSF commands
    '''
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class IckdsfCommand(object):
    '''Superclass for ICKDSF commands'''
    def __init__(self, module) -> None:
        self.module = module

    @staticmethod
    def convert(self):
        '''Converts zos_ickdsf_command arguments to a JCL command for use with zos_mvs_raw'''
        return ''


class CommandInit(IckdsfCommand):
    '''Class implementing ICKDSF Init command'''

    @staticmethod
    def convert(args):
        if args.get('init'):
            args = args.get('init')

        # Get parameters from playbooks
        volume_address = args.get('volume_address')
        verify_existing_volid = args.get('verify_existing_volid')
        verify_offline = args.get('verify_offline')
        volid = args.get('volid')
        vtoc_tracks = args.get('vtoc_tracks')
        index = args.get('index')
        verify_no_data_sets_exist = args.get('verify_no_data_sets_exist')
        sms_managed = args.get('sms_managed')
        addr_range = args.get('addr_range')
        volid_prefix = args.get('volid_prefix')

        # validate parameters
        if volume_address is None:
            msg = 'Volume address must be defined'
            raise IckdsfError(msg)

        try:
            int(volume_address, 16)
        except ValueError:
            msg = 'Volume address must be a valid 64-bit hex value'
            raise IckdsfError(msg)

        # convert playbook args to JCL parameters
        cmd_args = {
            'volume_address': 'unit({})'.format(volume_address)
        }

        if vtoc_tracks:
            cmd_args['vtoc_tracks'] = 'vtoc(0, 1, {})'.format(vtoc_tracks)
        else:
            cmd_args['vtoc_tracks'] = ''
        if volid:
            cmd_args['volid'] = 'volid({})'.format(volid)
        else:
            cmd_args['volid'] = ''
        if not verify_existing_volid:
            cmd_args['verify_existing_volid'] = 'noverify'
        else:
            cmd_args['verify_existing_volid'] = 'verify({})'.format(verify_existing_volid)
        if verify_offline:
            cmd_args['verify_offline'] = 'verifyoffline'
        else:
            cmd_args['verify_offline'] = 'noverifyoffline'
        if verify_no_data_sets_exist:
            cmd_args['verify_no_data_sets_exist'] = 'nods'
        else:
            cmd_args['verify_no_data_sets_exist'] = 'ds'
        if index:
            cmd_args['index'] = ''
        else:
            cmd_args['index'] = 'noindex'
        if sms_managed:
            cmd_args['sms_managed'] = 'storagegroup'
        else:
            cmd_args['sms_managed'] = ''

        # Format into JCL strings for zos_mvs_raw
        cmd = [
            ' init {} {} {} {} - '.format(
                cmd_args['volume_address'],
                cmd_args['verify_existing_volid'],
                cmd_args['verify_offline'],
                cmd_args['volid']),
            ' {} {} {} {}'.format(
                cmd_args['vtoc_tracks'],
                cmd_args['sms_managed'],
                cmd_args['verify_no_data_sets_exist'],
                cmd_args['index'])]

        # Check if Playbook wants to INIT a range of volumes
        if addr_range and volid_prefix:
            if not verify_no_data_sets_exist:
                msg = 'You are not allowed to initialize a range of volumes without checking for data sets.'
                raise IckdsfError(msg)
            start = int(str(volume_address), 16)
            end = start + addr_range
            for i in range(start + 1, end + 1):
                next_addr = '{0:x}'.format(i)
                next_vol_id = str(volid_prefix) + next_addr
                formatted_next_addr = 'unit({})'.format(next_addr)
                formatted_next_vol_id = 'volid({})'.format(next_vol_id)
                cmd.append(' init {} {} {} {} - '.format(
                    formatted_next_addr,
                    cmd_args['verify_existing_volid'],
                    cmd_args['verify_offline'],
                    formatted_next_vol_id))
                cmd.append(' {} {} {} {}'.format(
                    cmd_args['vtoc_tracks'],
                    cmd_args['sms_managed'],
                    cmd_args['verify_no_data_sets_exist'],
                    cmd_args['index']))

        return cmd


def run_module():

    module_args = dict(
        buildix=dict(type="dict", options=dict(
            volume_address=dict(type="str", required=True),
            verify_existing_volid=dict(type="str", required=False),
            verify_offline=dict(type="bool", default=True),
            volid=dict(type="str", required=False),
            vtoc_tracks=dict(type="int", required=False),
            index=dict(type="bool", default=True),
            sms_managed=dict(type="bool", default=True),
            verify_no_data_sets_exist=dict(type="bool", default=True),
            addr_range=dict(type="int"),
            volid_prefix=dict(type="str")),
        ),
        init=dict(type="dict", options=dict(
            volume_address=dict(type="str", required=True),
            verify_existing_volid=dict(type="str", required=False),
            verify_offline=dict(type="bool", default=True),
            volid=dict(type="str", required=False),
            vtoc_tracks=dict(type="int", required=False),
            index=dict(type="bool", default=True),
            sms_managed=dict(type="bool", default=True),
            verify_no_data_sets_exist=dict(type="bool", default=True),
            addr_range=dict(type="int"),
            volid_prefix=dict(type="str")),
        ),
        output_html=dict(type="dict", options=dict(
            full_file_path=dict(type="str", required=True),
            append=dict(type="bool", default=True, required=False))
        )
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        command='',
        output=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        parser = better_arg_parser.BetterArgParser(module_args)
        parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    # table of ICKDSF command classes
    command_table = {
        'init': CommandInit
    }

    # loop over commands in playbook and execute appropriate conversion
    for cmd in module.params.keys():
        try:
            cmd_class = command_table.get(cmd)
            if cmd_class is not None:
                result['command'] = cmd_class.convert(module.params)
        except IckdsfError as e:
            module.fail_json(msg="Encountered error with Ickdsf", stderr=str(e))

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
