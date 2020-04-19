#!/usr/bin/python
# -*- coding: utf-8 -*-​
# Copyright (c) IBM Corporation 2019, 2020
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: zos_copy
version_added: '0.0.3'
short_description: Copy data to z/OS
description:
    - The M(zos_copy) module copies a file or data set from a local or a
      remote machine to a location on the remote machine.
    - Use the M(zos_fetch) module to copy files or data sets from remote 
      locations to local machine.
author: "Asif Mahmud (@asifmahmud)"
options:
  src:
    description:
    - Local path to a file to copy to the remote z/OS system; can be absolute 
      or relative.
    - If I(remote_src=true), then src must be the name of the file, data set
      or data set member on remote z/OS system.
    - If the path is a directory, and the destination is a PDS(E), all the 
      files in it would be copied to a PDS(E).
    - If the path is a directory, it is copied (including the source folder 
      name) recursively to C(dest).
    - If the path is a directory and ends with "/", only the inside contents of
      that directory are copied to the destination. Otherwise, if it does not
      end with "/", the directory itself with all contents is copied.
    - If the path is a file and dest ends with "/", the file is copied to the
      folder with the same filename.
    - Required unless using C(content).
    type: str
  dest:
    description:
    - Remote absolute path or data set where the file should be copied to.
    - Destination can be a USS location separated with ‘/’
      or MVS location separated with ‘.’.
    - If C(src) is a directory, this must be a directory or a PDS(E).
    - If C(dest) is a nonexistent path, it will be created.
    - If C(src) and C(dest) are files and if the parent directory of C(dest)
      doesn't exist, then the task will fail.
    - If C(dest) is a PDS, PDS(E), or VSAM, the copy module will only copy into
      already allocated resource.
    type: str
    required: yes
  content:
    description:
    - When used instead of C(src), sets the contents of a file or data set
      directly to the specified value.
    - Works only when C(dest) is a USS file or sequential data set.
    - This is for simple values, for anything complex or with formatting please
      switch to the M(template) module.
    type: str
    required: false
  backup:
    description:
    - Determine whether a backup should be created.
    - When set to C(true), create a backup file including the timestamp 
      information so you can get the original file back if you somehow 
      clobbered it incorrectly.
    - No backup is taken when I(remote_src=False) and multiple files are being
      copied.
    type: bool
    default: false
    required: false
  force:
    description:
    - If C(true), the remote file or data set will be replaced when contents 
      are different than the source.
    - If C(false), the file will only be transferred if the destination does 
      not exist.
    type: bool
    default: true
    required: false
  mode:
    description:
    - The permission of the destination file or directory.
    - If C(dest) is USS, this will act as Unix file mode, otherwise ignored.
    - Refer to the M(copy) module for a detailed description of this parameter.
    type: path
    required: false
  remote_src:
    description:
    - If C(false), it will search for src at local machine.
    - If C(true), it will go to the remote/target machine for the src.
    type: bool
    default: false
    required: false
  local_follow:
    description:
    - This flag indicates that filesystem links in the source tree, if they 
      exist, should be followed.
    type: bool
    default: true
    required: false
  is_binary:
    description:
    - If C(true), indicates that the file or data set to be copied is a 
      binary file/data set. 
    type: bool
    default: false
    required: false
  use_qualifier:
    description:
    - Add user qualifier to data sets.
    type: bool
    default: true
    required: false
  encoding:
    description:
    - Specifies which encodings the destination file or data set should be
      converted from and to. 
    - If this parameter is not provided, no encoding conversions will take 
      place.
    - Only valid if I(is_binary=false)
    type: dict
    required: false
    suboptions:
      from:
        description:
            - The encoding to be converted from
        required: true
        type: str
      to:
        description:
            - The encoding to be converted to
        required: true
        type: str
  checksum:
    description:
    - SHA256 checksum of the file being copied.
    - Used to validate that the copy of the file or data set was successful.
    - If this is not provided and I(validate=true), Ansible will use local 
      calculated checksum of the src file.
    type: str
    required: false
  validate:
    description:
    - Verrify that the copy operation was successful by comparing the source 
      and destination checksum.
    type: bool
    default: true
    required: false
notes:
    - Destination data sets are assumed to be in catalog. When trying to copy 
      to an uncataloged data set, the module assumes that the data set does 
      not exist and will create it.
'''

EXAMPLES = r'''
- name: Copy a local file to a sequential data set
  zos_copy:
    src: /path/to/sample_seq_data_set
    dest: SAMPLE.SEQ.DATA.SET
- name: Copy a local file to a USS location
  zos_copy:
    src: /path/to/test.log
    dest: /tmp/test.log
- name: Copy a local ASCII encoded file and convert to IBM-1047
  zos_copy:
    src: /path/to/file.txt
    dest: /tmp/file.txt
    encoding:
      from: ISO8859-1
      to: IBM-1047
- name: Copy file with owner and permission details
  zos_copy:
    src: /path/to/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: '0644'
- name: Module will follow the symbolic link specified in src
  zos_copy:
    src: /path/to/link
    dest: /path/to/uss/location
    local_follow: true
- name: Copy a local file to a PDS member and validate checksum
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.PDSE(member_name)
    validate: true
- name: Copy a single file to a VSAM(KSDS)
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.VSAM
- name: Copy inline content to a sequential dataset and replace existing data
  zos_copy:
    content: 'Inline content to be copied'
    dest: SAMPLE.SEQ.DATA.SET
    force: true
- name: Copy a USS file to a sequential data set
  zos_copy:
    src: /path/to/remote/uss/file
    dest: SAMPLE.SEQ.DATA.SET
    remote_src: true
- name: Copy a binary file to a PDSE member
  zos_copy:
    src: /path/to/binary/file
    dest: HLQ.SAMPLE.PDSE(member_name)
    is_binary: true
- name: Copy a local file and take a backup of the existing file
  zos_copy:
    src: /path/to/local/file
    dest: /path/to/dest
    backup: true
- name: Copy a PDS(E) on remote system to a new PDS(E)
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.NEW.PDSE
    remote_src: true
- name: Copy a PDS(E) on remote system to a PDS(E), replacing the original
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.EXISTING.PDSE
    remote_src: true
    force: true
- name: Copy PDS(E) member to a new PDS(E) member. Replace if it already exists
  zos_copy:
    src: HLQ.SAMPLE.PDSE(member_name)
    dest: HLQ.NEW.PDSE(member_name)
    force: true
    remote_src: true
'''

RETURN = r'''
dest:
    description: Destination file/path or MVS data set name.
    returned: success
    type: str
    sample: SAMPLE.SEQ.DATA.SET
src:
    description: Source file used for the copy on the target machine.
    returned: changed
    type: str
    sample: /path/to/source.log
checksum:
    description: SHA256 checksum of the file after running copy.
    returned: success
    type: str
    sample: 8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e
backup_file:
    description: Name of the backup file or data set that was created.
    returned: changed and if backup=true
    type: str
    sample: 11540.20150212-220915.bak
gid:
    description: Group id of the file, after execution
    returned: success and if dest is USS
    type: int
    sample: 100
group:
    description: Group of the file, after execution
    returned: success and if dest is USS
    type: str
    sample: httpd
owner:
    description: Owner of the file, after execution
    returned: success and if dest is USS
    type: str
    sample: httpd
uid:
    description: Owner id of the file, after execution
    returned: success and if dest is USS
    type: int
    sample: 100
mode:
    description: Permissions of the target, after execution
    returned: success and if dest is USS
    type: str
    sample: 0644
size:
    description: Size of the target, after execution.
    returned: changed and src is a file
    type: int
    sample: 1220
state:
    description: State of the target, after execution
    returned: success and if dest is USS
    type: str
    sample: file
msg:
    description: Failure message returned by the module
    returned: failure
    type: str
    sample: Error while gathering data set information
stdout:
    description: The stdout from a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: Copying local file /tmp/foo/src to remote path /tmp/foo/dest
stderr:
    description: The stderr of a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: FileNotFoundError: No such file or directory '/tmp/foo'
stdout_lines:
    description: List of strings containing individual lines from stdout
    returned: failure
    type: list
    sample: [u"Copying local file /tmp/foo/src to remote path /tmp/foo/dest.."]
stderr_lines:
    description: List of strings containing individual lines from stderr
    returned: failure
    type: list
    sample: [u"FileNotFoundError: No such file or directory '/tmp/foo'"]
rc:
    description: The return code of a USS command or MVS command, if applicable
    returned: failure
    type: int
    sample: 8

'''

import os
import re
import os.path
import hashlib
import string
import random
import math
import tempfile

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser, data_set_utils, vtoc
)


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.six import PY3

from zoautil_py import MVSCmd, Datasets
from zoautil_py import types

MVS_PARTITIONED = frozenset({'PE', 'PO', 'PDSE', 'PDS'})
MVS_SEQ = frozenset({'PS', 'SEQ'})

# The AnsibleModule object
module = None

def _ascii_to_ebcdic(src, content):
    conv_cmd = "iconv -f ISO8859-1 -t IBM-1047"
    rc, out, err = module.run_command(conv_cmd, data=content)
    if rc != 0:
        module.fail_json(
          msg="Unable to convert encoding of {} to EBCDIC".format(src)
        )
    return out


def _copy_to_ds(ds_name, size=None, content=None, remote_src=False, src_ds=None):
    if not remote_src:
        temp_ds_name = data_set_utils.DataSetUtils.create_temp_data_set(
            "TEMP", size=str(size)
        )
        Datasets.write(temp_ds_name, _ascii_to_ebcdic(content))
    repro_cmd = "  REPRO INFILE({0}) OUTFILE({1})".format(temp_ds_name, ds_name)
    try:
        sysprint = _run_mvs_command("IDCAMS", repro_cmd, authorized=True)
    finally:
        if Datasets.exists(temp_ds_name):
            Datasets.delete(temp_ds_name)


def _run_mvs_command(pgm, cmd, dd=None, authorized=False):
    sysprint = "sysprint"
    sysin = "sysin"
    pgm = pgm.upper()
    if pgm == "IKJEFT01":
        sysprint = "systsprt"
        sysin = "systsin"

    mvs_cmd = "mvscmd"
    if authorized:
        mvs_cmd += "auth"
    mvs_cmd += " --pgm={0} --{1}=* --{2}=stdin"
    if dd:
        for k, v in dd.items():
            mvs_cmd += " --{0}={1}".format(k, v)
    
    rc, out, err = module.run_command(
        mvs_cmd.format(pgm, sysprint, sysin), data=cmd
    )
    if rc != 0:
        module.fail_json(
            msg="Non-zero return code received while executing mvscmd",
            stdout=out,
            stderr=err,
            ret_code=rc
        )
    return out


def _allocate_vsam(ds_name, size):
    volume = "000000"
    max_size = 16777215
    allocation_size = math.ceil(size/1048576)
    
    if allocation_size > max_size:
        msg = ("Size of data exceeds maximum allowed allocation size for VSAM."
               "Maximum size allowed: {0} Megabytes, given data size: {1}"
               " Megabytes".format(max_size, allocation_size))
        module.fail_json(msg=msg)
  
    define_sysin = ''' DEFINE CLUSTER (NAME({0})  -
   	                    VOLUMES({1})) -                           
                        DATA (NAME({0}.DATA) -
	                    MEGABYTES({2}, 5)) -
                        INDEX (NAME({0}.INDEX)) '''.format(
                            ds_name, volume, allocation_size
                        )

    try:
        sysprint = _run_mvs_command("IDCAMS", define_sysin)
    except Exception as err:
        module.fail_json(msg="Failed to call IDCAMS to allocate VSAM data set")


def _get_checksum(data):
    """ Calculate checksum for the given data """
    digest = hashlib.sha256()
    data = to_bytes(data, errors='surrogate_or_strict')
    digest.update(data)
    return digest.hexdigest()


def _get_mvs_checksum(ds_name):
    return _get_checksum(Datasets.read(ds_name))


def _copy_to_seq(
    src, 
    dest, 
    data, 
    validate=True, 
    local_checksum=None, 
    src_ds_type=None
):
    remote_checksum = _get_mvs_checksum(dest)
    rc = Datasets.write(dest, _ascii_to_ebcdic(src, data))
    if rc != 0:
        module.fail_json(
            msg="Unable to write content to destination {}".format(dest)
        )
    if validate:
        new_checksum = _get_mvs_checksum(dest)
        if remote_checksum != new_checksum:
            changed = True
        if new_checksum != local_checksum:
            module.fail_json(
                msg="Checksum mismatch", 
                checksum=new_checksum, 
                local_checksum=local_checksum, 
                changed=changed
            )


def _copy_remote_pdse(src_ds, dest, copy_member=False):
    if copy_member:
        rc, out, err = module.run_command(
            "cp \"//{}\" \"//{}\"".format(src_ds, dest)
        )
        if rc != 0:
            module.fail_json(
                msg="Unable to copy partitioned data set member",
                stdout=out,
                stderr=err,
                rc=rc
            )
    else:
        dds = dict(OUTPUT=dest, INPUT=src_ds)
        copy_cmd = "   COPY OUTDD=OUTPUT,INDD=((INPUT,R))"
        sysprint = _run_mvs_command("IEBCOPY", copy_cmd, dds)


def _copy_to_pdse(
    src_dir, 
    dest, 
    copy_member=False,  
    src_file=None
):
    cmd = None
    if copy_member:
        cmd = "cp {0} \"//'{}'\"".format(src_file, dest)
    else:
        path, dirs, files = next(os.walk(src_dir))
        cmd = "cp"
        for file in files:
            file = file if '.' not in file else file[:file.rfind('.')]
            cmd += " {0}/{1}".format(path, file)
        cmd += " \"//'{0}'\"".format(dest)
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Unable to copy to data set {}".format(dest))


def _create_data_set(src, ds_name, ds_type, size, d_blocks=None):
    if (ds_type in MVS_PARTITIONED.union(MVS_SEQ)):
        rc = Datasets.create(ds_name, ds_type, size, "FB", directory_blocks=d_blocks)
        if rc != 0:
            module.fail_json(
                "Unable to allocate destination data set to copy {}".format(src)
            )
    else:
        _allocate_vsam(ds_name, size)


def _remote_copy_handler(src, dest, src_ds_type, dest_ds_type, module_args):
    if dest_ds_type in MVS_SEQ:
        cmd = None
        if src_ds_type == 'USS':
            cmd = "cp {0} \"//'{1}'\"".format(src, dest)
        elif src_ds_type in MVS_SEQ.union(MVS_PARTITIONED):
            cmd = "cp \"//'{0}'\" \"//'{1}'\"".format(src, dest)
        else:
            _copy_to_ds(dest, remote_src=True, src_ds=src)


def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            dest=dict(required=True, type='str'),
            use_qualifier=dict(type='bool', default=False), 
            is_binary=dict(type='bool', default=False),
            is_vsam=dict(type='bool', default=False),
            encoding=dict(type='str', default='EBCDIC',choices=['EBCDIC','ASCII']),
            content=dict(type='str', no_log=True),
            backup=dict(type='bool', default=False),
            force=dict(type='bool', default=True),
            validate=dict(type='bool', default=False),
            remote_src=dict(type='bool', default=False),
            checksum=dict(type='str'),
            is_uss=dict(type='bool'),
            is_pds=dict(type='bool'),
            _local_data=dict(type='str'),
            _size=dict(type='int'),
            _local_checksum=dict(type='str'),
            _pds_path=dict(type='str'),
            _num_files=dict(type='int'),
            _copy_member=dict(type='bool')
        )
    )

    src = module.params.get('src')
    b_src = to_bytes(src, errors='surrogate_or_strict')
    dest = module.params.get('dest')
    b_dest = to_bytes(dest, errors='surrogate_or_strict')
    remote_src = module.params.get('remote_src')
    use_qualifier = module.params.get('use_qualifier')
    is_binary = module.params.get('is_binary')
    is_vsam = module.params.get('is_vsam')
    encoding = module.params.get('encoding')
    content = module.params.get('content')
    validate = module.params.get('validate')
    is_uss = module.params.get('is_uss')
    is_pds = module.params.get('is_pds')
    _local_checksum = module.params.get('_local_checksum')
    _local_data = module.params.get('_local_data')
    _pds_path = module.params.get('_pds_path')
    _num_files = module.params.get('_num_files')
    _size = module.params.get('_size')
    _copy_member = module.params.get('_copy_member')

    changed = False

    try:
        dest_ds_utils = data_set_utils.DataSetUtils(module, dest)
        dest_ds_type = dest_ds_utils.get_data_set_type()
    except Exception as err:
        module.fail_json(msg=str(err))

    if remote_src:
        try:
            src_ds_utils = data_set_utils.DataSetUtils(module, src)
            src_ds_type = src_ds_utils.get_data_set_type()
        except Exception as err:
            module.fail_json(msg=str(err))

        _remote_copy_handler(src, dest, src_ds_type, dest_ds_type, module.params)
    
    if dest_ds_utils.data_set_exists() is False:
        d_blocks = None
        if is_pds or src_ds_type == "PO":
            dest_ds_type = "PDSE"
            d_blocks = math.ceil(_num_files/6)
        elif is_vsam:
            dest_ds_type = "VSAM"
        else:
            dest_ds_type = "SEQ"

        _create_data_set(src, dest, dest_ds_type, _size, d_blocks=d_blocks)
        changed = True
    
    # Copy to sequential data set
    if dest_ds_type in MVS_SEQ:
        _copy_to_seq(
            src, 
            dest, 
            _local_data, 
            validate=validate, 
            local_checksum=_local_checksum, 
            remote_src=remote_src,
            src_ds_type=src_ds_type
        )

    # Copy to partitioned data set
    elif dest_ds_type in MVS_PARTITIONED:
        temp_file = None
        if _copy_member:
            fd, temp_file = tempfile.mkstemp()
            write_mode = 'wb' if is_binary else 'w'
            with os.fdopen(fd, write_mode) as tmp:
                tmp.write(_local_data)
        try:
            _copy_to_pdse(
                src if remote_src else _pds_path, 
                dest, 
                copy_member=_copy_member, 
                remote_src=remote_src, 
                src_file=temp_file
            )
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    # Copy to VSAM data set
    else:
        _copy_to_ds(dest, size=_size, content=_local_data)

    remote_checksum = None
    new_checksum = None

    res_args = dict(
        src=src,
        dest=dest,
        changed=changed,
        checksum=_get_mvs_checksum(dest),
        size="{} Bytes".format(module.params.get('_size')),
        ds_type = dest_ds_type
    )
    module.exit_json(**res_args)


class UncatalogedDatasetError(Exception):
    def __init__(self, ds_name):
        super().__init__(
            ("Data set {} is not in catalog. If you would like to copy to "
             "the data set, please catalog it first".format(ds_name))
        )


if __name__ == '__main__':
    main()
