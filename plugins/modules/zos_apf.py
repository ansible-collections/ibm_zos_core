#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'comminuty'}

DOCUMENTATION = r'''
---
module: zos_apf
author:
  - "Behnam (@balkajbaf)"
short_description: Add/remove libraries to Authorized Program Facility (APF)
description:
  - Add/remove libraries to Authorized Program Facility (APF)
  - Make APF statement persistent entries to data set or data set member
  - Change APF list format to "DYNAMIC" or "STATIC"
  - Get current APF list entries
options:
  dsname:
    description:
      - The name of z/OS data set (library) to be added/removed.
    required: False
    type: str
    aliases: [ name, lib, library ]
  state:
    description:
      - Ensure the library is added C(state=present) or removed C(state=absent)
      - APF list format has to be "DYNAMIC"
    required: False
    type: str
    choices:
      - absent
      - present
    default: present
  force_dynamic:
    description:
      - Ensure APF list format is "DYNAMIC" before add/remove libraries
    required: False
    type: bool
    default: False
  volume:
    description:
      - The volume identifier for the volume containing the library specified on
        the C(dsname) parameter, value should be one of the following,
        1. The volume serial number
        2. Six asterisks (******), indicating that the system is to use the
        volume serial number of the current system residence (SYSRES) volume.
        3. *MCAT*, indicating that the system is to use the volume serial number
        of the volume containing the master catalog.
      - If C(volume) is not specified, C(dsname) has to be cataloged.
    required: False
    type: str
  sms:
    description:
      - Indicates that the library specified on the C(dsname) parameter is
        managed by the storage management subsystem (SMS), and therefore no
        volume is associated with the library.
      - If C(sms=True), C(volume) value will be ignored.
    required: False
    type: bool
    default: False
  operation:
    description:
      - Change AFP list format to "DYNAMIC" or "STATIC"
      - Display AFP list current format
      - Display APF list entries
      - If C(operation!=None), add/remove operation will be ignored.
      - If C(operation=list), C(dsname), C(volume) and C(sms) will be used
        as filters
    required: False
    type: str
    choices:
      - set_dynamic
      - set_static
      - check_format
      - list
  persistent:
    description:
      - Add/remove persistent entries to/from a dataset
      - C(dsname) will not be persisted/removed if C(persistent=None)
    required: False
    type: dict
    suboptions:
      persistds:
        description:
          - The dataset be used to Persist or Remove the APF entry
        required: True
        type: str
      marker:
        description:
          - The marker line template.
          - C({mark}) will be replaced with "BEGIN" and "END".
          - Using a custom marker without the C({mark}) variable may result
            in the block being repeatedly inserted on subsequent playbook runs.
        required: False
        type: str
        default: "/* {mark} ANSIBLE MANAGED BLOCK <timestamp> */"
      backup:
        description:
          - Creates a backup file or backup data set for I(src), including the
            timestamp information to ensure that you retrieve the original file.
          - I(backup_name) can be used to specify a backup file name if I(backup=true).
          - The backup file name will be return on either success or failure
            of module execution such that data can be retrieved.
        required: false
        type: bool
        default: false
      backup_name:
        description:
          - Specify the USS file name or data set name for the destination backup.
          - If the source I(src) is a USS file or path, the backup_name name must be a
            file or path name, and the USS file or path must be an absolute path name.
          - If the source is an MVS data set, the backup_name name must be
            an MVS data set name.
          - If the backup_name is not provided, the default backup_name name
            will be used. If the source is a USS file or path, the name of
            the backup file will be the source file or path name appended
            with a timestamp,
            e.g. C(/path/file_name.2020-04-23-08-32-29-bak.tar).
          - If the source is an MVS data set, it will be a data set with a
            random name generated by calling the ZOAU API. The MVS backup
            data set recovery can be done by renaming it.
        required: false
        type: str
  batch:
    description:
      - A list of dictionaries for adding/removing libraries
      - This is mutually exclusive with C(dsname), C(volume), C(sms)
      - Can be used with C(persistent)
    type: list
    elements: dict
    required: false
    suboptions:
      dsname:
        description:
          - The name of z/OS data set (library) to be added/removed.
        type: str
        required: True
        aliases: [ name, lib, library ]
      volume:
        description:
          - The volume identifier for the volume containing the library
            specified on the C(dsname) parameter, value should be one of the
            following,
            1. The volume serial number
            2. Six asterisks (******), indicating that the system is to use the
            volume serial number of the current system residence (SYSRES)
            volume.
            3. *MCAT*, indicating that the system is to use the volume serial
            number of the volume containing the master catalog.
          - If C(volume) is not specified, C(dsname) has to be cataloged.
        required: False
        type: str
      sms:
        description:
          - Indicates that the library specified on the C(dsname) parameter is
            managed by the storage management subsystem (SMS), and therefore no
            volume is associated with the library.
          - If true C(volume) will be ignored.
        required: False
        type: bool
        default: False
'''


EXAMPLES = r'''
- name: Add a library to APF list
  zos_apf:
    dsname: SOME.SEQUENTIAL.DATASET
    volume: T12345
- name: Add a library (cataloged) to APF list and persistence
  zos_apf:
    dsname: SOME.SEQUENTIAL.DATASET
    force_dynamic: True
    persistent:
      persistds: SOME.PARTITIONED.DATASET(MEM)
- name: Remove a library from APF list and persistence
  zos_apf:
    state: absent
    dsname: SOME.SEQUENTIAL.DATASET
    volume: T12345
    persistent:
      persistds: SOME.PARTITIONED.DATASET(MEM)
- name: Use batch to add a set of libraries to APF list and persistence and custom marker
  zos_apf:
    persistent:
      persistds: SOME.PARTITIONED.DATASET(MEM)
      marker: "/* {mark} PROG001 USR0010 */"
    batch:
      - dsname: SOME.SEQ.DS1
      - dsname: SOME.SEQ.DS2
        sms: True
      - dsname: SOME.SEQ.DS3
        volume: T12345
- name: Print APF list matching dsname pattern or volume serial number
  zos_apf:
    operation: list
    dsname: SOME.SEQ.*
    volume: T12345
- name: Set APF list format to STATIC
  zos_apf:
    operation: set_static
'''


RETURN = r'''
stdout:
  description: The stdout from ZOAU apfadm. Output varies based on type of operation.
  state:
    description: stdout of executed the operator command (opercmd), "SETPROG" from ZOAU apfadm
  operation:
    description: stdout of operation options
    list:
      description: Returns a list of dictionaries of APF list entries
      type: list
      example:
        [{'vol': 'PP0L6P', 'ds': 'DFH.V5R3M0.CICS.SDFHAUTH'},
        {'vol': 'PP0L6P', 'ds': 'DFH.V5R3M0.CICS.SDFJAUTH'}, ...]
    set_dynamic:
      description: Set to DYNAMIC
      type: str
    set_static:
      description: Set to STATIC
      type: str
    check_format:
      description: DYNAMIC or STATIC
      type: str
stderr:
  description: The error messages from ZOAU apfadm
  type: str
  sample: BGYSC1310E ADD Error: Dataset COMMON.LINKLIB volume COMN01 is already present in APF list.
rc:
  description: The return code from ZOAU apfadm
  type: bool
msg:
  description: The module messages
  returned: failure
  type: str
  sample: Parameter verification failed
backup_name:
    description: Name of the backup file or data set that was created.
    returned: if backup=true
    type: str
'''

import re
import json
from ansible.module_utils.six import b
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes
from ansible.module_utils.six import PY3
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, data_set, backup as Backup)
from os import path
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)

try:
    from zoautil_py import zsystem
except Exception:
    Datasets = MissingZOAUImport()

if PY3:
    from shlex import quote
else:
    from pipes import quote

# supported data set types
DS_TYPE = ['PS', 'PO']


def backupOper(module, src, backup):
    # analysis the file type
    ds_utils = data_set.DataSetUtils(src)
    file_type = ds_utils.ds_type()
    if file_type != 'USS' and file_type not in DS_TYPE:
        message = "{0} data set type is NOT supported".format(str(file_type))
        module.fail_json(msg=message)

    # backup can be True(bool) or none-zero length string. string indicates that backup_name was provided.
    # setting backup to None if backup_name wasn't provided. if backup=None, Backup module will use
    # pre-defined naming scheme and return the created destination name.
    if isinstance(backup, bool):
        backup = None
    try:
        if file_type == 'USS':
            backup_name = Backup.uss_file_backup(src, backup_name=backup, compress=False)
        else:
            backup_name = Backup.mvs_file_backup(dsn=src, bk_dsn=backup)
    except Exception:
        module.fail_json(msg="creating backup has failed")

    return backup_name


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dsname=dict(
                type='str',
                required=False,
                aliases=['lib', 'library', 'name']
            ),
            state=dict(
                type='str',
                default='present',
                choices=['absent', 'present']
            ),
            force_dynamic=dict(
                type='bool',
                default=False
            ),
            volume=dict(
                type='str',
                required=False
            ),
            sms=dict(
                type='bool',
                required=False,
                default=False
            ),
            operation=dict(
                type='str',
                required=False,
                choices=['set_dynamic', 'set_static', 'check_format', 'list']
            ),
            persistent=dict(
                type='dict',
                required=False,
                options=dict(
                    persistds=dict(
                        type='str',
                        required=True,
                    ),
                    marker=dict(
                        type='str',
                        required=False,
                        default='/* {mark} ANSIBLE MANAGED BLOCK <timestamp> */'
                    ),
                    backup=dict(
                        type='bool',
                        default=False
                    ),
                    backup_name=dict(
                        type='str',
                        required=False,
                        default=None
                    ),
                )
            ),
            batch=dict(
                type='list',
                elements='dict',
                required=False,
                options=dict(
                    dsname=dict(
                        type='str',
                        required=True,
                        aliases=['lib', 'library', 'name']
                    ),
                    volume=dict(
                        type='str',
                        required=False
                    ),
                    sms=dict(
                        type='bool',
                        required=False,
                        default=False
                    ),
                )
            ),
        ),
        mutually_exclusive=[
            # batch
            ['batch', 'dsname'],
            ['batch', 'volume'],
            # operation
            ['operation', 'persistent'],
            ['batch', 'operation'],
        ],
    )

    params = module.params

    arg_defs = dict(
        dsname=dict(arg_type='str', required=False, aliases=['lib', 'library', 'name']),
        state=dict(arg_type='str', default='present', choices=['absent', 'present']),
        force_dynamic=dict(arg_type='bool', default=False),
        volume=dict(arg_type='str', required=False),
        sms=dict(arg_type='bool', required=False, default=False),
        operation=dict(arg_type='str', required=False, choices=['set_dynamic', 'set_static', 'check_format', 'list']),
        persistent=dict(
            arg_type='dict',
            required=False,
            options=dict(
                persistds=dict(arg_type='str', required=True),
                marker=dict(arg_type='str', required=False, default='/* {mark} ANSIBLE MANAGED BLOCK <timestamp> */'),
                backup=dict(arg_type='bool', default=False),
                backup_name=dict(arg_type='str', required=False, default=None),
            )
        ),
        batch=dict(arg_type='list', elements='dict', required=False, default=None,
            options=dict(
                dsname=dict(arg_type='str', required=True, aliases=['lib', 'library', 'name']),
                volume=dict(arg_type='str', required=False),
                sms=dict(arg_type='bool', required=False, default=False),
            )
        ),
        mutually_exclusive=[
            # batch
            ['batch', 'dsname'],
            ['batch', 'volume'],
            # operation
            ['operation', 'persistent'],
            ['batch', 'operation'],
        ],
    )
    result = dict(changed=False)
    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    dsname = parsed_args.get('dsname')
    state = parsed_args.get('state')
    force_dynamic = parsed_args.get('force_dynamic')
    volume = parsed_args.get('volume')
    sms = parsed_args.get('sms')
    operation = parsed_args.get('operation')
    persistent = parsed_args.get('persistent')
    batch = parsed_args.get('batch')

    if persistent:
        persistDS = persistent.get('persistds')
        backup = persistent.get('backup')
        if backup:
            if persistent.get('backup_name'):
                backup = persistent.get('backup_name')
                del persistent['backup_name']
            result['backup_name'] = backupOper(module, persistDS, backup)
            del persistent['backup']
        if state == "present":
            persistent['addDataset'] = persistDS
        else:
            persistent['delDataset'] = persistDS
        del persistent['persistds']

    if operation:
        ret = zsystem.apf(opt=operation)
    else:
        if state == "present":
            opt = "add"
        else:
            opt = "del"
        if batch:
            for item in batch:
                item['opt'] = opt
            ret = zsystem.apf(batch=batch, forceDynamic=force_dynamic, persistent=persistent)
        else:
            if not dsname:
                module.fail_json(msg='dsname is required')
            ret = zsystem.apf(opt=opt, dsname=dsname, volume=volume, sms=sms, forceDynamic=force_dynamic, persistent=persistent)

    operOut = ret.stdout_response
    operErr = ret.stderr_response
    operRc = ret.rc
    result['stderr'] = operErr
    result['rc'] = operRc
    if operation == 'list':
        try:
            dsRx = ""
            volRx = ""
            if dsname:
                dsRx = re.compile(dsname)
            if volume:
                volRx = re.compile(volume)
            if sms:
                sms = "*SMS*"
            if dsRx or volRx or sms:
                data = json.loads(operOut)
                operOut = ""
                for d in data[2:]:
                    ds = d.get('ds')
                    vol = d.get('vol')
                    if (dsRx and dsRx.match(ds)) or (volRx and volRx.match(vol)) or (sms and sms == vol):
                        operOut = operOut + "{0} {1}\n".format(vol, ds)
        except Exception:
            pass

    result['stdout'] = operOut

    module.exit_json(**result)


if __name__ == '__main__':
    main()
