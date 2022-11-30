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

#######################################################
# TODO - Not sure where the following information goes,
# perhaps add it to the list of authors.
# Team: JumpStart Team 8
#   - "Austen Stewart"
#   - "Almigdad Suliman"
#   - "Nicholas Teves"
#   - "Nuoya Xie"
#   - "Trevor Glassey"
#   - "Tyler Edwards"
# Date: 07/2021
#######################################################

DOCUMENTATION = r"""
module: zos_ickdsf_init
short_description: Initialize volumes or minidisks on z/OS through ICKDSF init command.
description:
  - ICKDSF INIT command to initialize volume or minidisk.
  - Writes volume label and VTOC on volume or minidisk.
version_added: 1.6.0
author:
  - "Austen Stewart (@TODO)"
  - "Nuoya Xie (@TODO)"
  - "Trevor Glassey (@TODO)"

options:
  volume_address:
    description:
      - 3 or 4 hexadecimal digit address of the volume to initialize.
      - This could be a unit address or device number.
    required: true
    type: str
  verify_existing_volid:
    description:
      - Verify that the provided volume serial matches the one found on existing volume/minidisk.
      - Module fails if volser does not match.
      - Note - This option is NOT a boolean, please leave it blank in order to skip the verification.
    required: false
    type: str
  verify_offline:
    description:
      - Verify that the device is offline to all other systems.
      - Beware, defaults set on target z/OS systems may override ICKDSF parameters.
    type: bool
    required: false
    default: true
  volid:
    description:
      - Specify the volume serial number to initialize the volume with.
      - Expects 1-6 alphanumeric, national ($, \\#, \\@) or special characters.
      - volid's specified with less than 6 characters are left justified and padded with blank chars (X'40').
      - Characters are not validated so check with operating system guide for valid alphanumeric characters.
      - Also referred to as volser or volume serial number.
      - Default behavior in the case this parameter is not specified in the case of an existing device initialization is the reuse the existing volume serial.
    required: false
    type: str
  vtoc_tracks:
    description:
      - The number of tracks to initialize the VTOC with.
      - The VTOC will be placed at cylinder 0 head 1 for the number of tracks specified.
      - Typically, ICKDSF will default the size to the number of tracks in a cylinder minus 1.
      - For a 3390, the default is cylinder 0, track 1 for 14 tracks
    required: false
    type: int
  index:
    description:
      - Create a VTOC index during volume initialization.
      - The index size will be based on the size of the volume and the size of the VTOC that was created.
      - The index will be placed on the volume after the VTOC.
      - Set to false to not generate an index.
    required: false
    type: bool
    default: true
  sms_managed:
    description:
      - Assigned to be managed by Storage Management System (SMS).
    type: bool
    required: false
    default: true
  verify_no_data_sets_exist:
    description:
      - Verify if data sets other than the VTOC index data set and/or VVDS exist on the volume to be initialized.
      - Beware that z/OS system defaults can override ICKDSF parameters.
    required: false
    type: bool
    default: true
  addr_range:
    description:
      - If initializing a range of volumes, how many additional addresses to initialize.
    required: false
    type: int
  volid_prefix:
    description:
      - If initializing a range of volumes, the prefix of volume IDs to initialize. This with have the address appended to it.
    required: false
    type: str
  output_html:
    description:
      - Options for creating HTML output of ICKDSF command.
    required: false
    type: dict
    suboptions:
      full_file_path:
        description:
          - File path to place output HTML file.
        required: true
        type: str
      append:
        description:
          - Optionally append to file, instead of overwriting.
        type: bool
        default: true
"""
EXAMPLES = r"""
- name: Initialize a new dasd volume for use on a z/OS system and save the output to a html file. This task sets
        the new volume serial to 'e8d8', confirms that the existing volume serial is 'ine8d8', skips the check to see
        if the volume is offline, creates a VTOC of size 30 and an index. This volume will be managed by SMS.
  zos_ickdsf_init:
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

- name: Initialize 3 new dasd volume for use on a z/OS system and save the output to a html file. These additional will be set as ine8d9 and ine8da
  zos_ickdsf_init:
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
"""
RETURN = r'''
command:
  description: INIT command issued to ICKDSF tool.
  returned: success
  type: list
  elements: str
  sample:
    - "[ \" init unit(0903) noverify noverifyoffline volid(KTN003) - \",\"   ds \" ]"
msg:
  description: Failure message returned by module.
  returned: failure
  type: str
  sample: 'Volume address must be a valid 64-bit hex value'
mvs_raw_output:
  description:
    - Output of mvs_raw module call.
    - This is a temporary return field.
  returned: when mvs_raw is invoked
  type: str
  sample: not sure...
ret_code:
  description:
    - return code from mvs_raw
  type: dict
  returned: success
'''

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
    def convert():
        '''Converts zos_ickdsf_init arguments to a JCL command for use with zos_mvs_raw'''
        return ''


class CommandInit(IckdsfCommand):
    '''Class implementing ICKDSF Init command'''

    @staticmethod
    def convert(args):

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
            'volume_address': 'unit({0})'.format(volume_address)
        }

        if vtoc_tracks:
            cmd_args['vtoc_tracks'] = 'vtoc(0, 1, {0})'.format(vtoc_tracks)
        else:
            cmd_args['vtoc_tracks'] = ''
        if volid:
            cmd_args['volid'] = 'volid({0})'.format(volid)
        else:
            cmd_args['volid'] = ''
        if not verify_existing_volid:
            cmd_args['verify_existing_volid'] = 'noverify'
        else:
            cmd_args['verify_existing_volid'] = 'verify({0})'.format(verify_existing_volid)
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
            ' init {0} {1} {2} {3} - '.format(
                cmd_args['volume_address'],
                cmd_args['verify_existing_volid'],
                cmd_args['verify_offline'],
                cmd_args['volid']),
            ' {0} {1} {2} {3}'.format(
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
                formatted_next_addr = 'unit({0})'.format(next_addr)
                formatted_next_vol_id = 'volid({0})'.format(next_vol_id)
                cmd.append(' init {0} {1} {2} {3} - '.format(
                    formatted_next_addr,
                    cmd_args['verify_existing_volid'],
                    cmd_args['verify_offline'],
                    formatted_next_vol_id))
                cmd.append(' {0} {1} {2} {3}'.format(
                    cmd_args['vtoc_tracks'],
                    cmd_args['sms_managed'],
                    cmd_args['verify_no_data_sets_exist'],
                    cmd_args['index']))

        return cmd


def run_module():

    module_args = dict(
        volume_address=dict(type="str", required=True),
        verify_existing_volid=dict(type="str", required=False),
        verify_offline=dict(type="bool", required=False, default=True),
        volid=dict(type="str", required=False),
        vtoc_tracks=dict(type="int", required=False),
        index=dict(type="bool", required=False, default=True),
        sms_managed=dict(type="bool", required=False, default=True),
        verify_no_data_sets_exist=dict(type="bool", required=False, default=True),
        addr_range=dict(type="int"),
        volid_prefix=dict(type="str"),
        output_html=dict(type="dict", required=False, options=dict(
            full_file_path=dict(type="str", required=True),
            append=dict(type="bool", default=True, required=False))
        )
    )

    result = dict(
        changed=False,
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

    result['command'] = CommandInit.convert(module.params)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
