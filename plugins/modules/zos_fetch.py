#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = r'''
---
module: zos_fetch
version_added: "2.9"
short_description: Fetch data from z/OS
description:
  - This module copies a file or data set from a remote z/OS system to the
    local machine. Use the M(zos_copy) module to copy files from local machine
    to the remote z/OS system.
  - When fetching a sequential data set, the destination file name will be the
    same as the data set name.
  - When fetching a PDS/PDS(E), the destination will be a directory with the
    same name as the PDS/PDS(E).
  - Files that already exist at dest will be overwritten if they are different
    than the src.
author: "Asif Mahmud (@asifmahmud)"
options:
  src:
    description:
      - Name of PDS, PDS(E) members, VSAM data set, USS file path.
    required: true
    type: str
  dest:
    description:
      - Local path where the file or data set will be stored.
    required: true
    type: path
  fail_on_missing:
    description:
      - When set to true, the task will fail if the source file is missing.
    required: false
    default: "true"
    type: bool
  validate_checksum:
    description:
      - Verify that the source and destination checksums match after the files
        are fetched.
    required: false
    default: "true"
    type: bool
  flat:
    description:
      - Override the default behavior of appending hostname/path/to/file to the
        destination. If set to "false", the file or data set will be fetched to
        the destination directory without appending remote hostname to the
        destination. Refer to the M(fetch) module for a more detailed
        description of this parameter.
    required: false
    default: "true"
    type: bool
  is_binary:
    description:
      - Specifies if the file being fetched is a binary.
    required: false
    default: "false"
    type: bool
  use_qualifier:
    description:
      - Indicates whether the data set high level qualifier should be used when
        fetching.
    required: false
    default: "false"
    type: bool
notes:
    - When fetching PDS(E) and VSAM data sets, temporary storage will be used
      on the remote z/OS system. After the PDS(E) or VSAM data set is
      successfully transferred, the temprorary data set will deleted. The size
      of the temporary storage will correspond to the size of PDS(E) or VSAM
      data set being fetched. If module executation fails, the temporary
      storage will be cleaned.
    - To prevent redundancy, additional checksum validation will not be done
      when fetching PDS(E) because data integrity checks are done through the
      transfer methods used. As a result, the module response will not include
      C(checksum) parameter.
    - All data sets are always assumed to be in catalog. If an uncataloged data
      set needs to be fetched, it should be cataloged first.
seealso:
- module: fetch
- module: zos_copy
- module: copy
- module: zos_data_set
'''

EXAMPLES = r'''
- name: Fetch file from USS and store into /tmp/fetched/hostname/tmp/somefile
  zos_fetch:
    src: /tmp/somefile
    dest: /tmp/fetched

- name: Fetch a sequential data set and store in /tmp/SOME.DATA.SET
  zos_fetch:
    src: SOME.DATA.SET
    dest: /tmp/
    flat: true

- name: Fetch a PDS as binary and store in /tmp/SOME.PDS.DATASET
  zos_fetch:
    src: SOME.PDS.DATASET
    dest: /tmp/
    flat: true
    is_binary: true

- name: Fetch a unix file and don't validate its checksum
  zos_fetch:
    src: /tmp/somefile
    dest: /tmp/
    flat: true
    validate_checksum: false

- name: Fetch a VSAM data set
  zos_fetch:
    src: USER.TEST.VSAM
    dest: /tmp/
    flat: true

- name: Fetch a PDS member named 'DATA'
  zos_fetch:
    src: USER.TEST.PDS(DATA)
    dest: /tmp/
    flat: true
'''

RETURN = r'''
message:
    description: The output message returned from this module.
    type: dict
    returned: always
    contains:
      msg:
        description: Message returned by the module
        type: str
        sample: The data set was fetched successfully
      stdout:
        description: The stdout from a USS command or MVS command
        type: str
        sample: DATA SET 'USER.PROCLIB' NOT IN CATALOG
      stderr:
        description: The stderr of a USS command or MVS command
        type: str
        sample: File /tmp/result.log not found
      ret_code:
        description: The return code of a USS command or MVS command
        type: int
        sample: 8
    sample:
      - "msg": "Failed to read data set member for data set USER.TEST.PROCLIB"
      - "stdout": "DATA SET 'USER.TEST.PROCLIB' NOT IN CATALOG"
      - "stderr": ""
      - "ret_code": 1
file:
    description: The source file path on remote machine
    returned: success
    type: str
    sample: SOME.DATA.SET
dest:
    description: The destination file path on controlling machine
    returned: success
    type: str
    sample: /tmp/SOME.DATA.SET
is_binary:
    description: Indicates which transfer mode was used to fetch the file
    returned: success
    type: bool
    sample: True
checksum:
    description: The SHA1 checksum of the fetched file
    returned: success and src is a non-partitioned data set
    type: str
    sample: 33ab5639bfd8e7b95eb1d8d0b87781d4ffea4d5d
md5sum:
    description: The MD5 hash of the fetched file
    returned: success and src is a USS file
    type: str
    sample: 9011901c4b1bba2fa8b73b0409af8a10
data_set_type:
    description: Indidcates the fetched file's data set type
    returned: success
    type: str
    sample: PDSE
note:
    description: Notice of module failure when C(fail_on_missing) is false
    returned: failure and fail_on_missing=false
    type: str
    sample: The data set USER.PROCLIB does not exist. No data was fetched.
changed:
    description: Indicates if any changes were made during the module operation
    returned: always
    type: bool
'''


import os
import base64
import hashlib
import random
import string
import re
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes
from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, data_set_utils
)
try:
    from zoautil_py import Datasets, MVSCmd, types
except Exception:
    Datasets = ""
    MVSCmd = ""
    types = ""


# Ansible module object
module = None

MVS_DS_TYPES = frozenset({'PS', 'PO', 'PDSE', 'PE'})


def _fail_json(msg="", stdout="", stderr="", ret_code=None):
    """ Wrapper for AnsibleModule.fail_json """
    module.fail_json(msg=msg, stdout=stdout, stderr=stderr, ret_code=ret_code)


def _run_command(cmd, **kwargs):
    """ Wrapper for AnsibleModule.run_command """
    return module.run_command(cmd, **kwargs)


def _fetch_zos_data_set(zos_data_set, is_binary, fetch_member=False):
    """ Read a sequential data set and return its contents """
    if fetch_member:
        rc, out, err = _run_command("cat \"//'{0}'\"".format(zos_data_set))
        if rc != 0:
            _fail_json(
                msg=(
                    "Failed to read data set member for "
                    "data set {0}".format(zos_data_set)
                ),
                stdout=out,
                stderr=err,
                ret_code=rc
            )
        content = out
    else:
        content = Datasets.read(zos_data_set)
    if is_binary:
        content = content.encode('utf-8', 'surrogateescape')
        return base64.b64encode(content.decode('utf-8', 'replace').encode())
    return content


def _copy_vsam_to_temp_data_set(ds_name):
    """ Copy VSAM data set to a temporary sequential data set """
    try:
        sysin = data_set_utils.DataSetUtils.create_temp_data_set('SYSIN')
        out_ds = data_set_utils.DataSetUtils.create_temp_data_set('OUTPUT')
        sysprint = data_set_utils.DataSetUtils.create_temp_data_set('SYSPRINT')
    except OSError as err:
        _fail_json(
            msg="Unable to create temporary data set while executing MVSCmd",
            stderr=str(err)
        )

    repro_sysin = ' REPRO INFILE(INPUT)  OUTFILE(OUTPUT) '
    Datasets.write(sysin, repro_sysin)

    dd_statements = []
    dd_statements.append(types.DDStatement(ddName='sysin', dataset=sysin))
    dd_statements.append(types.DDStatement(ddName='input', dataset=ds_name))
    dd_statements.append(types.DDStatement(ddName='output', dataset=out_ds))
    dd_statements.append(types.DDStatement(ddName='sysprint', dataset=sysprint))

    try:
        rc = MVSCmd.execute_authorized(pgm='idcams', args='', dds=dd_statements)
    except Exception as err:
        if Datasets.exists(out_ds):
            Datasets.delete(out_ds)

        if rc != 0:
            _fail_json(
                msg=(
                    "Non-zero return code received while executing MVSCmd "
                    "to copy VSAM data set {0}".format(ds_name)
                ),
                ret_code=rc
            )
        _fail_json(
            msg=(
                "Failed to call IDCAMS to copy VSAM data set {0} to "
                "sequential data set".format(ds_name)
            ),
            stderr=str(err),
            ret_code=rc
        )

    finally:
        Datasets.delete(sysprint)
        Datasets.delete(sysin)

    return out_ds


def _fetch_vsam(src, validate_checksum, is_binary):
    """ Fetch a VSAM data set """
    checksum = None
    temp_ds = _copy_vsam_to_temp_data_set(src)
    content = _fetch_zos_data_set(temp_ds, is_binary)
    if content is None:
        content = ''

    rc = Datasets.delete(temp_ds)
    if rc != 0:
        _fail_json(
            msg="Unable to delete data set {0}".format(temp_ds), ret_code=rc
        )

    if validate_checksum:
        checksum = _get_checksum(content)

    return content, checksum


def _fetch_pdse(src):
    """ Fetch a partitioned data set """
    result = dict()
    temp_dir = tempfile.mkdtemp()
    rc, out, err = _run_command("cp \"//'{0}'\" {1}".format(src, temp_dir))
    if rc != 0:
        _fail_json(
            msg=(
                "Error copying partitioned data set to USS. Make sure the PDS"
                "/PDS(E) is not empty"
            ),
            stdout=out,
            stderr=err,
            ret_code=rc
        )

    result['pds_path'] = temp_dir
    return result


def _fetch_ps(src, validate_checksum, is_binary):
    """ Fetch a sequential data set """
    checksum = None
    content = _fetch_zos_data_set(src, is_binary)
    if content is None:
        content = ""
    if validate_checksum:
        checksum = _get_checksum(content)
    return content, checksum


def _get_checksum(data):
    """ Calculate checksum for the given data """
    digest = hashlib.sha1()
    data = to_bytes(data, errors='surrogate_or_strict')
    digest.update(data)
    return digest.hexdigest()


def run_module():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            dest=dict(required=True, type='path'),
            fail_on_missing=dict(required=False, default=True, type='bool'),
            validate_checksum=dict(required=False, default=True, type='bool'),
            flat=dict(required=False, default=True, type='bool'),
            is_binary=dict(required=False, default=False, type='bool'),
            use_qualifier=dict(required=False, default=False, type='bool')
        )
    )

    arg_def = dict(
        src=dict(arg_type='data_set_or_path_type', required=True),
        dest=dict(arg_type='path', required=True),
        fail_on_missing=dict(arg_type='bool', required=False, default=True),
        validate_checksum=dict(arg_type='bool', required=False, default=True),
        is_binary=dict(arg_type='bool', required=False, default=False),
        use_qualifier=dict(arg_type='bool', required=False, default=False)
    )

    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        _fail_json(msg="Parameter verification failed", stderr=str(err))

    src = parsed_args.get('src', None)
    b_src = to_bytes(src)
    fail_on_missing = boolean(parsed_args.get('fail_on_missing'))
    validate_checksum = boolean(parsed_args.get('validate_checksum'))
    is_binary = boolean(parsed_args.get('is_binary'))
    use_qualifier = boolean(parsed_args.get('use_qualifier'))

    res_args = dict()
    _fetch_member = src.endswith(')')
    ds_name = src if not _fetch_member else src[:src.find('(')]
    try:
        ds_utils = data_set_utils.DataSetUtils(module, ds_name)
        if not ds_utils.data_set_exists():
            if fail_on_missing:
                _fail_json(
                    msg=(
                        "The data set {0} does not exist or is "
                        "uncataloged".format(src)
                    )
                )
            module.exit_json(
                note=(
                    "Source {0} was not found. No data was fetched".format(src)
                )
            )
        ds_type = ds_utils.get_data_set_type()
        if not ds_type:
            _fail_json(msg="Unable to determine data set type")

    except Exception as err:
        _fail_json(
            msg="Error while gathering data set information", stderr=str(err)
        )

    if use_qualifier:
        src = Datasets.hlq() + '.' + src

    # Fetch sequential dataset
    if ds_type == 'PS':
        content, checksum = _fetch_ps(src, validate_checksum, is_binary)
        res_args['checksum'] = checksum
        res_args['content'] = content

    # PDS/PDSE
    elif ds_type in ('PO', 'PDSE', 'PE'):
        if _fetch_member:
            content = _fetch_zos_data_set(src, is_binary, fetch_member=True)
            res_args['content'] = content
            res_args['checksum'] = _get_checksum(content)
        else:
            result = _fetch_pdse(src)
            res_args['pds_path'] = result['pds_path']

    # VSAM dataset
    elif ds_type == 'VSAM':
        content, checksum = _fetch_vsam(src, validate_checksum, is_binary)
        res_args['checksum'] = checksum
        res_args['content'] = content

    res_args['file'] = src
    res_args['ds_type'] = ds_type
    module.exit_json(**res_args)


class UncatalogedDatasetError(Exception):
    def __init__(self, ds_name):
        super().__init__(
            ("Data set {0} is not in catalog. If you would like to fetch the "
                "data set, please catalog it first".format(ds_name))
        )


def main():
    run_module()


if __name__ == '__main__':
    main()
