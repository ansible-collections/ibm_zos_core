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
module: zos_volume_init
short_description: Initialize volumes or minidisks on z/OS through ICKDSF init command.
description:
  - Wraps the ICKDSF INIT command to initialize volume or minidisk.
  - Writes volume label and VTOC on volume or minidisk.
version_added: 1.6.0
author:
  - "Austen Stewart (@stewartad)"
  - "Almigdad Suliman (@Almigdad-Suliman)"
  - "Nicholas Teves (@TODO)"
  - "Nuoya Xie (@nxie13)"
  - "Trevor Glassey (@tkglassey)"
  - "Tyler Edwards (@TLEdwards-Git)"
  - "Ketan Kelkar (@ketankelkar)"

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
- name: Initialize target volume with all default options. Target volume address is '1234', set volume name to 'DEMO01'.
        Target volume is checked to ensure it is offline and contains no data sets. Volume is SMS managed, has an index
        and VTOC size defined by the system.
  zos_volume_init:
    volume_address: "1234"
    volid: "DEMO01"

- name: Initialize target volume with all default options same as above and additionally check the existing volid
        matches the given value 'DEMO02' before re-initializing the volume and renaming it to 'DEMO01'
  zos_volume_init:
    volume_address: "1234"
    volid: "DEMO01"
    verify_volid: "DEMO02"

- name: Initialize non-SMS managed target volume with all the default options.
  zos_volume_init:
    volume_address: "1234"
    volid: "DEMO01"
    sms_managed: no

- name: Initialize a new SMS managed DASD volume with new volume serial 'e8d8' with 30 track VTOC, an index, as long as
        the existing volume serial is 'ine8d8' and there are no pre-existing data sets on the target. The check to see
        if volume is online before intialization is skipped.
  zos_volume_init:
    volume_address: e8d8
    vtoc_tracks: 30
    index: yes
    sms_managed: yes
    volid: ine8d8
    verify_existing_volid: ine8d8
    verify_no_data_sets_exist: yes
    verify_offline: no

- name: Initialize 3 new DASD volumes (0901, 0902, 0903) for use on a z/OS system as 'DEMO01', 'DEMO02', 'DEMO03'
        using Ansible loops.
  zos_volume_init:
    volume_address: "090{{ item }}"
    volid: "DEMO0{{ item }}"
  loop: "{{ range(1, 4, 1) }}"
"""
RETURN = r"""
command:
  description: INIT command issued to ICKDSF tool.
  returned: success
  type: list
  elements: str
  sample:
      [
        " init unit(0903) noverify noverifyoffline volid(DEMO08) - ",
        "   nods noindex",
      ]
msg:
  description: Failure message returned by module.
  returned: failure
  type: str
  sample: \'Index\' cannot be False for SMS managed volumes.
rc:
  description:
    - return code from ICKDSF init mvs command
  type: dict
  returned: when ICKDSF init command is issued.
content:
  description:
    - Raw output from ICKDSF.
  returned: when ICKDSF init command is issued.
  type: list
  elements: str
  sample:
      [
        "1ICKDSF - MVS/ESA    DEVICE SUPPORT FACILITIES 17.0                TIME: 18:32:22        01/17/23     PAGE   1",
        "0        ",
        "0 INIT UNIT(0903) NOVERIFY NOVERIFYOFFLINE VOLID(KET678) -",
        "0   NODS NOINDEX",
        "-ICK00700I DEVICE INFORMATION FOR 0903 IS CURRENTLY AS FOLLOWS:",
        "-          PHYSICAL DEVICE = 3390",
        "-          STORAGE CONTROLLER = 2107",
        "-          STORAGE CONTROL DESCRIPTOR = E8",
        "-          DEVICE DESCRIPTOR = 0C",
        "-          ADDITIONAL DEVICE INFORMATION = 4A00003C",
        "-          TRKS/CYL = 15, # PRIMARY CYLS = 100",
        "0ICK04000I DEVICE IS IN SIMPLEX STATE",
        "0ICK00703I DEVICE IS OPERATED AS A MINIDISK",
        " ICK00091I 0903 NED=002107.900.IBM.75.0000000BBA01",
        "-ICK03091I EXISTING VOLUME SERIAL READ = KET987",
        "-ICK03096I EXISTING VTOC IS LOCATED AT CCHH=X'0000 0001' AND IS    14 TRACKS.",
        "0ICK01314I VTOC IS LOCATED AT CCHH=X'0000 0001' AND IS    14 TRACKS.",
        "-ICK00001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0",
        "0          18:32:22    01/17/23",
        "0        ",
        "-ICK00002I ICKDSF PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 0",
      ]
"""

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
