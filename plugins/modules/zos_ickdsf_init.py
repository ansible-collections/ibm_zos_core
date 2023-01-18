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

- name: Initialize 3 new DASD volumes (0901, 0902, 0903) for use on a z/OS system as 'DEMO01', 'DEMO02', 'DEMO03' using Ansible loops.
  zos_ickdsf_init:
    volume_address: "090{{ item }}"
    volid: "DEMO0{{ item }}"
  register: output
  loop: "{{ range(1, 4, 1) }}"
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

# from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import better_arg_parser
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import ickdsf  # pylint: disable=import-error


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
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # sms managed and index are defined by ickdsf init as mutually exclusive.
    if module.params['sms_managed'] and not module.params['index']:
      module.fail_json(msg="'Index' cannot be False for SMS managed volumes.", **result)

    if module.check_mode:
        module.exit_json(**result)

    # try:
    #     parser = better_arg_parser.BetterArgParser(module_args)
    #     parser.parse_args(module.params)
    # except ValueError as err:
    #     module.fail_json(msg="Parameter verification failed", stderr=str(err))

    result.update(ickdsf.init(module, result, module.params))

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
