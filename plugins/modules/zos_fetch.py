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
  - This module copies a file or data set from a remote z/OS system to the local machine.
    Use the M(zos_copy) module to copy files from local machine to the remote z/OS system.
  - When fetching a sequential data set, the destination file name will be the same as
    the data set name.
  - When fetching a PDS/PDS(E), the destination will be a directory with the same name
    as the PDS/PDS(E).
author: "Asif Mahmud (@asifmahmud)"
options:
  src:
    description:
      - Name of PDS, PDS(E) members, VSAM data set, USS file path.
    required: true
  dest:
    description:
      - Local path where the file or data set will be stored.
    required: true
  fail_on_missing:
    description:
      - When set to true, the task will fail if the source file is missing.
    required: false
    default: "true"
    type: bool
  validate_checksum:
    description:
      - Verify that the source and destination checksums match after the files are fetched.
    required: false
    default: "true"
    type: bool
  flat:
    description:
      - Override the default behavior of appending hostname/path/to/file to the
        destination. If set to "false", the file or data set will be fetched to
        the destination directory without appending remote hostname to the
        destination. Refer to the M(fetch) module for a more detailed description
        of this parameter.
    required: false
    default: "true"
    type: bool
  is_binary:
    description:
      - Specifies if the file being fetched is a binary.
    required: false
    default: "false"
    type: bool
  encoding:
    description:
      - If set to "EBCDIC", the encoding of source file or data set will be converted
        to ASCII before being transferred to local machine. If set to "ASCII", the
        encoding will not be converted.
    required: false
    default: "EBCDIC"
    choices: ["ASCII", "EBCDIC" ]
  use_qualifier:
    description:
      - Indicates whether the data set high level qualifier should be used when fetching.
    required: false
    default: "false"
    type: bool
notes:
    - When fetching PDS(E) and VSAM data sets, temporary storage will be used on the remote
      z/OS system. After the PDS(E) or VSAM data set is successfully transferred, the
      temprorary data set will deleted. The size of the temporary storage will correspond
      to the size of PDS(E) or VSAM data set being fetched. If module executation fails,
      the temporary storage will be cleaned.
    - To prevent redundancy, additional checksum validation will not be done when fetching
      PDS(E) because data integrity checks are done through the transfer methods used.
      As a result, the module response will not include C(checksum) parameter.
    - All data sets are always assumed to be in catalog. If an uncataloged data set needs to
      be fetched, it should be cataloged first.
seealso:
- module: fetch
- module: zos_copy
- module: copy
- module: zos_data_set
'''

EXAMPLES = r'''
- name: Fetch file from USS and store into /tmp/fetched/host.example.com/tmp/somefile
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

- name: Fetch a unix file without converting from EBCDIC to ASCII. Don't fail if file is missing
  zos_fetch:
    src: /tmp/somefile
    dest: /tmp/
    encoding: ASCII
    fail_on_missing: false

- name: Fetch a unix file and don't validate its checksum.
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
        description: The stdout from a USS command or MVS command, if applicable
        type: str
        sample: DATA SET 'USER.PROCLIB' NOT IN CATALOG
      stderr:
        description: The stderr of a USS command or MVS command, if applicable
        type: str
        sample: File /tmp/result.log not found
      ret_code:
        description: The return code of a USS command or MVS command, if applicable
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
    description: Indicates which transfer mode was used to fetch the file (binary or text)
    returned: success
    type: bool
    sample: True
encoding:
    description: The encoding of the fetched file
    returned: success
    type: str
    sample: ascii
checksum:
    description: The SHA1 checksum of the fetched file
    returned: success
    type: str
    sample: 33ab5639bfd8e7b95eb1d8d0b87781d4ffea4d5d
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
    description: Indicates if any changes were made during the module operation.
    returned: always
    type: bool
'''


import os
import base64
import subprocess
import hashlib
import random
import string
import re
import tempfile
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes
from ansible.module_utils.parsing.convert_bool import boolean
from zoautil_py import Datasets, MVSCmd
from zoautil_py import types


# Ansible module object
module = None

MVS_DS_TYPES = frozenset({'PS', 'PO', 'PDSE', 'PE'})


def _fail_json(**kwargs):
    """ Wrapper around AnsibleModule.fail_json """
    module.fail_json(**kwargs)


def _run_command(cmd, **kwargs):
    """ Wrapper around AnsibleModule.run_command """
    return module.run_command(cmd, **kwargs)


def _fetch_uss_file(src, validate_checksum, is_binary):
    """ Read a USS file and return its contents """
    read_mode = 'rb' if is_binary else 'r'
    content = checksum = None
    try:
        with open(src, read_mode) as infile:
            content = infile.read()
            if is_binary:
                content = base64.b64encode(content)
            if validate_checksum:
                checksum = _get_checksum(content)
    except (FileNotFoundError, IOError, OSError) as err:
        _fail_json(
            msg=str(err),
            stdout="",
            stderr="",
            ret_code=None
        )
    return content, checksum


def _fetch_zos_data_set(zos_data_set, is_binary, fetch_member=False):
    """ Read a sequential data set and return its contents """
    if fetch_member:
        rc, out, err = _run_command("cat \"//'{0}'\"".format(zos_data_set))
        if rc != 0:
            _fail_json(
                msg="Failed to read data set member for data set {0}".format(zos_data_set),
                stdout=out,
                stderr=err,
                ret_code=rc
            )
        content = out
    else:
        content = Datasets.read(zos_data_set)
    if is_binary:
        content = content.encode('utf-8', 'surrogateescape').decode('utf-8', 'replace')
        return base64.b64encode(content.encode())
    return content


def _create_temp_data_set_name(LLQ):
    """ Create a temporary data set name """
    chars = string.ascii_uppercase
    HLQ2 = ''.join(random.choice(chars) for i in range(5))
    return Datasets.hlq() + '.' + HLQ2 + '.' + LLQ


def _copy_vsam_to_temp_data_set(ds_name):
    """ Copy VSAM data set to a temporary sequential data set """
    sysin = _create_temp_data_set_name('SYSIN')
    out_ds = _create_temp_data_set_name('OUTPUT')
    sysprint = _create_temp_data_set_name('SYSPRINT')

    Datasets.create(sysin, 'SEQ')
    Datasets.create(out_ds, 'SEQ')
    Datasets.create(sysprint, "SEQ", "", "FB", "", 133)

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
                msg="Non-zero return code received while executing MVSCmd to copy VSAM data set {0}".format(ds_name),
                stdout="",
                stderr="",
                ret_code=rc
            )
        _fail_json(
            msg="Failed to call IDCAMS to copy VSAM data set {0} to sequential data set".format(ds_name),
            stdout="",
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
            msg="Unable to delete data set {0}".format(temp_ds),
            stdout="",
            stderr="",
            ret_code=rc
        )

    if validate_checksum:
        checksum = _get_checksum(content)

    return content, checksum


def _ebcdic_to_ascii(data):
    """ Convert encoding from EBCDIC to ASCII """
    rc, out, err = _run_command("iconv -f IBM-1047 -t ISO8859-1", data=data)
    if rc != 0:
        _fail_json(
            msg="Unable to convert from EBCDIC to ASCII",
            stdout=out,
            stderr=err,
            ret_code=rc
        )
    return out


def _get_checksum(data):
    """ Calculate checksum for the given data """
    digest = hashlib.sha1()
    data = to_bytes(data, errors='surrogate_or_strict')
    digest.update(data)
    return digest.hexdigest()


def _determine_data_set_type(ds_name, fail_on_missing=True):
    """ Use the LISTDS utility to determine the type of a given data set """
    rc, out, err = _run_command("tsocmd \"LISTDS '{0}'\"".format(ds_name))
    if "NOT IN CATALOG" in out:
        raise UncatalogedDatasetError(ds_name)
    if "INVALID DATA SET NAME" in out:
        if os.path.exists(ds_name) and os.path.isfile(ds_name):
            return 'USS'
        elif fail_on_missing:
            _fail_json(
                msg="The USS file {0} does not exist".format(ds_name),
                stdout=out,
                stderr=err,
                ret_code=rc
            )
        else:
            module.exit_json(note="The USS file {0} does not exist. No data was fetched.".format(ds_name))
    if rc != 0:
        msg = None
        if "ALREADY IN USE" in out:
            msg = "Dataset {0} may already be open by another user. Close the dataset and try again.".format(ds_name)
        else:
            msg = "Unable to determine data set type for data set {0}.".format(ds_name)
        _fail_json(msg=msg, stdout=out, stderr=err, ret_code=rc)
    ds_search = re.search("(-|--)DSORG(|-)\n(.*)", out)
    if ds_search:
        return ds_search.group(3).split()[-1].strip()
    return None


def _fetch_pdse(src):
    """ Fetch a partitioned data set """
    result = dict()
    temp_dir = tempfile.mkdtemp()
    rc, out, err = _run_command("cp \"//'{0}'\" {1}".format(src, temp_dir))
    if rc != 0:
        _fail_json(
            msg="Error copying partitioned data set to USS",
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
    if not content:
        _fail_json(
            msg="Error fetching sequential data set {0}".format(src),
            stdout="",
            stderr="",
            ret_code=None
        )
    if validate_checksum:
        checksum = _get_checksum(content)
    return content, checksum


def _validate_dsname(ds_name):
    """ Validate the name of a given data set """
    dsn_regex = "^(([A-Z]{1}[A-Z0-9]{0,7})([.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}$"
    return re.match(dsn_regex, ds_name if '(' not in ds_name else ds_name[:ds_name.find('(')])


def _validate_params(src, is_binary, encoding, is_uss, _fetch_member):
    """ Ensure the module parameters are valid """
    msg = None
    if is_binary and encoding is not None:
        msg = "Encoding parameter is not valid for binary transfer"
    if encoding and (encoding != 'EBCDIC' and encoding != 'ASCII'):
        msg = "Invalid value supplied for 'encoding' option, it must be either EBCDIC or ASCII"
    if not is_uss and not _validate_dsname(src):
        msg = "Invalid data set name provided"

    if msg:
        _fail_json(msg=msg, stdout="", stderr="", ret_code=None)


def run_module():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='path'),
            dest=dict(required=True, type='path'),
            fail_on_missing=dict(required=False, default=True, type='bool'),
            validate_checksum=dict(required=False, default=True, type='bool'),
            flat=dict(required=False, default=True, type='bool'),
            is_binary=dict(required=False, default=False, type='bool'),
            encoding=dict(required=False, choices=['ASCII', 'EBCDIC'], type='str'),
            is_uss=dict(required=False, default=False, type='bool'),
            use_qualifier=dict(required=False, default=False, type='bool'),
            _fetch_member=dict(required=False, type='bool')
        )
    )

    src = module.params.get('src', None)
    b_src = to_bytes(src)
    encoding = module.params.get('encoding')
    fail_on_missing = boolean(module.params.get('fail_on_missing'), strict=False)
    validate_checksum = boolean(module.params.get('validate_checksum'), strict=False)
    is_uss = boolean(module.params.get('is_uss'), strict=False)
    is_binary = boolean(module.params.get('is_binary'), strict=False)
    use_qualifier = boolean(module.params.get('use_qualifier'), strict=False)
    _fetch_member = boolean(module.params.get('_fetch_member'), strict=False)

    _validate_params(src, is_binary, encoding, is_uss, _fetch_member)

    res_args = dict()
    if (not is_uss) and use_qualifier:
        src = Datasets.hlq() + '.' + src

    ds_name = src if not _fetch_member else src[:src.find('(')]

    try:
        ds_type = _determine_data_set_type(ds_name, fail_on_missing)
        if not ds_type:
            _fail_json(msg="Could not determine data set type", stdout="", stderr="", ret_code=None)

    except UncatalogedDatasetError as err:
        if fail_on_missing:
            _fail_json(msg=str(err), stdout="", stderr="", ret_code=None)
        module.exit_json(note="Datasets must be cataloged for data to be fetched. No data was fetched")

    if ds_type in MVS_DS_TYPES and not Datasets.exists(src):
        if fail_on_missing:
            _fail_json(
                msg="The MVS data set {0} does not exist".format(src),
                stdout="",
                stderr="",
                ret_code=None
            )
        module.exit_json(note="The data set {0} does not exist. No data was fetched.".format(src))

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

    # USS file
    elif is_uss:
        content, checksum = _fetch_uss_file(src, validate_checksum, is_binary)
        res_args['checksum'] = checksum
        res_args['content'] = content

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
        super().__init__("Data set {0} is not in catalog. If you would like to fetch the data set, please catalog it first".format(ds_name))


def main():
    run_module()


if __name__ == '__main__':
    main()
