#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023
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
short_description: Initialize volumes or minidisks.
description:
  - Initialize a volume or minidisk on z/OS.
  - I(zos_volume_init) will create the volume label and entry into the volume table of contents (VTOC).
  - Volumes are used for storing data and executable programs.
  - A minidisk is a portion of a disk that is linked to your virtual machine.
  - A VTOC lists the data sets that reside on a volume, their location, size, and other attirbutes.
  - I(zos_volume_init) uses the ICKDSF utility.
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
  address:
    description:
      - I(address) is a 3 or 4 digit hexadecimal number that specifies the address of the volume or minidisk.
      - I(address) can be the number assigned to the device (device number) when it is installed or the virtual address.
    required: true
    type: str
  verify_volid:
    description:
      - Verify that the volume serial matches what is on the existing volume or minidisk.
      - I(verify_volid) must be 1 to 6 alphanumeric characters or "*NONE*".
      - To verify that a volume serial number does not exist, use I(verify_volid="*NONE*").
      - If I(verify_volid) is specified and the volume serial number does not match that found on the volume or minidisk, initialization does not complete.
      - If I(verify_volid="*NONE*") is specified and a volume serial is found on the volume or minidisk, initialization does not complete.
      - Note - This option is NOT a boolean, please leave it blank in order to skip the verification. # TODO
    required: false
    type: str
  verify_offline:
    description:
      - Verify that the device is not online to any other systems, initialization does not complete.
      - Beware, defaults set on target z/OS systems may override ICKDSF parameters. # TODO
    type: bool
    required: false
    default: true
  volid:
    description:
      - The volume serial number used to initialize a volume or minidisk.
      - Expects 1-6 alphanumeric, national ($, \\#, \\@) or special characters.
      - A I(volid) with less than 6 characters will be padded with spaces.
      - Characters are not validated so check with operating system guide for valid alphanumeric characters.
      - A I(volid) can also be referred to as volser or volume serial number.
      - When I(volid) is not specified for a previously initialized volume or minidisk, the volume serial number will remain unchanged.
    required: false
    type: str
  vtoc_size:
    description:
      - The number of tracks to initialize the volume table of contents (VTOC) with.
      - The VTOC will be placed in cylinder 0 head 1.
      - If no tracks are specified it will default to the number of tracks in a cylinder minus 1. Tracks in a cylinder vary based on direct-access storage device (DASD) models, for 3390 a cylinder is 15 tracks.
    required: false
    type: int
  index:
    description:
      - Create a volume table of contents (VTOC) index.
      - The VTOC index enhances the performance of VTOC access.
      - When set to I(false), no index will be created.
    required: false
    type: bool
    default: true
  sms_managed:
    description:
      - Specifies that hte volume be managed by Storage Management System (SMS).
      - If I(sms_managed) is I(true) then I(index) mist also be I(true).
    type: bool
    required: false
    default: true
  verify_volume_empty:
    description:
      - Verify that no data sets other than the volume table of contents (VTOC) index or the VSAM Volume Data Set(VVDS) exist on the target volume.
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
    address: "1234"
    volid: "DEMO01"

- name: Initialize target volume with all default options and additionally check the existing volid
        matches the given value 'DEMO02' before re-initializing the volume and renaming it to 'DEMO01'.
  zos_volume_init:
    address: "1234"
    volid: "DEMO01"
    verify_volid: "DEMO02"

- name: Initialize non-SMS managed target volume with all the default options.
  zos_volume_init:
    address: "1234"
    volid: "DEMO01"
    sms_managed: no

- name: Initialize a new SMS managed DASD volume with new volume serial 'e8d8' with 30 track VTOC, an index, as long as
        the existing volume serial is 'ine8d8' and there are no pre-existing data sets on the target. The check to see
        if volume is online before intialization is skipped.
  zos_volume_init:
    address: e8d8
    vtoc_size: 30
    index: yes
    sms_managed: yes
    volid: ine8d8
    verify_volid: ine8d8
    verify_volume_empty: yes
    verify_offline: no

- name: Initialize 3 new DASD volumes (0901, 0902, 0903) for use on a z/OS system as 'DEMO01', 'DEMO02', 'DEMO03'
        using Ansible loops.
  zos_volume_init:
    address: "090{{ item }}"
    volid: "DEMO0{{ item }}"
  loop: "{{ range(1, 4, 1) }}"
"""
RETURN = r"""
cmd:
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
    - Return code from ICKDSF init mvs command.
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
        address=dict(type="str", required=True),
        verify_volid=dict(type="str", required=False),
        verify_offline=dict(type="bool", required=False, default=True),
        volid=dict(type="str", required=False),
        vtoc_size=dict(type="int", required=False),
        index=dict(type="bool", required=False, default=True),
        sms_managed=dict(type="bool", required=False, default=True),
        verify_volume_empty=dict(type="bool", required=False, default=True),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
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
