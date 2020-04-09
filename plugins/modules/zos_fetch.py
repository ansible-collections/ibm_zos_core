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
    local machine. Use the
    L(fetch,https://docs.ansible.com/ansible/latest/modules/fetch_module.html)
    module to copy files from local machine to the remote z/OS system.
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
      - USS file paths should be absolute paths.
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
        destination. If set to "true", the file or data set will be fetched to
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
  encoding:
    description:
      - Specifies which encodings the fetched data set should be converted from
        and to. If this parameter is not provided, this module assumes that
        source file or data set is encoded in IBM-1047 and will be converted
        to ISO8859-1.
    required: false
    type: dict
    suboptions:
      from:
        description:
            - The encoding to be converted from
        required: true
        type: str
        default: IBM-1047
      to:
        description:
            - The encoding to be converted to
        required: true
        type: str
        default: ISO8859-1
notes:
    - When fetching PDS(E) and VSAM data sets, temporary storage will be used
      on the remote z/OS system. After the PDS(E) or VSAM data set is
      successfully transferred, the temporary data set will deleted. The size
      of the temporary storage will correspond to the size of PDS(E) or VSAM
      data set being fetched. If module execution fails, the temporary
      storage will be cleaned.
    - To prevent redundancy, additional checksum validation will not be done
      when fetching PDS(E) because data integrity checks are done through the
      transfer methods used. As a result, the module response will not include
      C(checksum) parameter.
    - All data sets are always assumed to be in catalog. If an uncataloged data
      set needs to be fetched, it should be cataloged first.
    - Fetching HFS or ZFS is currently not supported.
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

- name: Fetch a USS file and convert from IBM-037 to ISO8859-1
  zos_fetch:
    src: /etc/profile
    dest: /tmp/
    encoding:
      from: IBM-037
      to: ISO8859-1
    flat: true
'''

RETURN = r'''
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
    description: The SHA256 checksum of the fetched file
    returned: success and src is a non-partitioned data set
    type: str
    sample: 8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e
data_set_type:
    description: Indicates the fetched file's data set type
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
msg:
    description: Message returned by the module
    returned: failure
    type: str
    sample: The data set was fetched successfully
stdout:
    description: The stdout from a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: DATA SET 'USER.PROCLIB' NOT IN CATALOG
stderr:
    description: The stderr of a USS command or MVS command, if applicable
    returned: failure
    type: str
    sample: File /tmp/result.log not found
stdout_lines:
    description: List of strings containing individual lines from stdout
    returned: failure
    type: list
    sample: [u'USER.TEST.PDS NOT IN CATALOG..']
stderr_lines:
    description: List of strings containing individual lines from stderr
    returned: failure
    type: list
    sample: [u'Unable to traverse PDS USER.TEST.PDS not found']
rc:
    description: The return code of a USS command or MVS command, if applicable
    returned: failure
    type: int
    sample: 8
'''


import base64
import hashlib
import tempfile
import re
import os

from math import floor, ceil
from shutil import rmtree, copy, move
from shlex import quote
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


class FetchHandler:
    def __init__(self, module):
        self.module = module

    def _fail_json(self, **kwargs):
        """ Wrapper for AnsibleModule.fail_json """
        self.module.fail_json(**kwargs)

    def _run_command(self, cmd, **kwargs):
        """ Wrapper for AnsibleModule.run_command """
        return self.module.run_command(cmd, **kwargs)

    def _get_vsam_size(self, vsam):
        """ Invoke IDCAMS LISTCAT command to get the record length and space used.
            Then estimate the space used by the VSAM data set.
        """
        space_pri = 0
        total_size = 0
        # Bytes per cylinder for a 3390 DASD
        bytes_per_cyl = 849960

        listcat_cmd = " LISTCAT ENT('{0}') ALL".format(vsam)
        cmd = 'mvscmdauth --pgm=idcams --sysprint=stdout --sysin=stdin'
        rc, out, err = self._run_command(cmd, data=listcat_cmd)
        if not rc:
            find_space_pri = re.findall(r'SPACE-PRI-*\d+', out)
            if find_space_pri:
                space_pri = int(''.join(re.findall(r'\d+', find_space_pri[0])))
            total_size = ceil((bytes_per_cyl * space_pri) / 1024)
        else:
            self._fail_json(
                msg="Unable to obtain data set information for {0}: {1}".format(vsam, err),
                stdout=out,
                stderr=err,
                stdout_lines=out.splitlines(),
                stderr_lines=err.splitlines(),
                rc=rc
            )
        return total_size

    def _copy_vsam_to_temp_data_set(self, ds_name):
        """ Copy VSAM data set to a temporary sequential data set """
        check_rc = 0
        mvs_rc = 0
        vsam_size = self._get_vsam_size(ds_name)
        try:
            sysin = data_set_utils.DataSetUtils.create_temp_data_set('SYSIN')
            sysprint = data_set_utils.DataSetUtils.create_temp_data_set('SYSPRINT')
            out_ds_name = data_set_utils.DataSetUtils.create_temp_data_set(
                'VSM', size="{0}K".format(vsam_size)
            )
            repro_sysin = ' REPRO INFILE(INPUT)  OUTFILE(OUTPUT) '
            Datasets.write(sysin, repro_sysin)

            dd_statements = []
            dd_statements.append(types.DDStatement(ddName='sysin', dataset=sysin))
            dd_statements.append(types.DDStatement(ddName='input', dataset=ds_name))
            dd_statements.append(types.DDStatement(ddName='output', dataset=out_ds_name))
            dd_statements.append(types.DDStatement(ddName='sysprint', dataset=sysprint))

            mvs_rc = MVSCmd.execute_authorized(pgm='idcams', args='', dds=dd_statements)

        except OSError as err:
            self._fail_json(msg=str(err))

        except Exception as err:
            if Datasets.exists(out_ds_name):
                Datasets.delete(out_ds_name)

            if mvs_rc != 0:
                self._fail_json(
                    msg=(
                        "Non-zero return code received while executing MVSCmd "
                        "to copy VSAM data set {0}".format(ds_name)
                    ),
                    rc=mvs_rc
                )
            self._fail_json(
                msg=(
                    "Failed to call IDCAMS to copy VSAM data set {0} to a temporary"
                    " sequential data set".format(ds_name)
                ),
                stderr=str(err), rc=mvs_rc
            )

        finally:
            Datasets.delete(sysprint)
            Datasets.delete(sysin)

        return out_ds_name

    def _uss_convert_encoding(self, src, dest, from_code_set, to_code_set):
        """ Convert the encoding of the data in a USS file """
        temp_fo = None
        if src != dest:
            temp_fi = dest
        else:
            fd, temp_fi = tempfile.mkstemp()
        iconv_cmd = 'iconv -f {0} -t {1} {2} > {3}'.format(
                    quote(from_code_set), quote(to_code_set), quote(src), quote(temp_fi)
        )
        self._run_command(iconv_cmd, use_unsafe_shell=True)
        if dest != temp_fi:
            try:
                move(temp_fi, dest)
            except (OSError, IOError):
                raise
            finally:
                os.close(fd)
                if os.path.exists(temp_fi):
                    os.remove(temp_fi)

    def _fetch_uss_file(self, src, is_binary, encoding):
        """ Convert encoding of a USS file. Return a tuple of temporary file
            name containing converted data.
        """
        file_path = None
        if not is_binary:
            fd, file_path = tempfile.mkstemp()
            from_code_set = encoding.get('from')
            to_code_set = encoding.get('to')
            # enc_utils = encode_utils.EncodeUtils(self.module)
            try:
                # enc_utils.uss_convert_encoding(src, file_path, from_code_set, to_code_set)
                self._uss_convert_encoding(src, file_path, from_code_set, to_code_set)
            except Exception as err:
                os.remove(file_path)
                self._fail_json(
                    msg=(
                        "An error occured while converting encoding of the file "
                        "{0} from {1} to {2}"
                    ).format(src, from_code_set, to_code_set),
                    stderr=str(err), stderr_lines=str(err).splitlines()
                )
            finally:
                os.close(fd)

        return file_path if file_path else src

    def _fetch_vsam(self, src, is_binary, encoding):
        """ Copy the contents of a VSAM to a sequential data set.
            Afterwards, copy that data set to a USS file.
        """
        temp_ds = self._copy_vsam_to_temp_data_set(src)
        file_path = self._fetch_mvs_data(temp_ds, is_binary, encoding)
        rc = Datasets.delete(temp_ds)
        if rc != 0:
            os.remove(file_path)
            self._fail_json(
                msg="Unable to delete temporary data set {0}".format(temp_ds), rc=rc
            )

        return file_path

    def _fetch_pdse(self, src, is_binary, encoding):
        """ Copy a partitioned data set to a USS directory. If the data set
            is not being fetched in binary mode, encoding for all members inside
            the data set will be converted.
        """
        dir_path = tempfile.mkdtemp()
        cmd = "cp -B \"//'{0}'\" {1}"
        if not is_binary:
            cmd = cmd.replace(" -B", "")
        rc, out, err = self._run_command(cmd.format(src, dir_path))
        if rc != 0:
            rmtree(dir_path)
            self._fail_json(
                msg=(
                    "Error copying partitioned data set {0} to USS. Make sure it is"
                    " not empty".format(src)
                ),
                stdout=out, stderr=err, stdout_lines=out.splitlines(),
                stderr_lines=err.splitlines(), rc=rc
            )
        if not is_binary:
            # enc_utils = encode_utils.EncodeUtils(self.module)
            from_code_set = encoding.get('from')
            to_code_set = encoding.get('to')
            root, dirs, files = next(os.walk(dir_path))
            try:
                for file in files:
                    file_path = os.path.join(root, file)
                    self._uss_convert_encoding(
                        file_path, file_path, from_code_set, to_code_set
                    )
                    # enc_utils.uss_convert_encoding(
                    #     file_path, file_path, from_code_set, to_code_set
                    # )
            except Exception as err:
                rmtree(dir_path)
                self._fail_json(
                    msg=(
                        "An error occured while converting encoding of the member "
                        "{0} from {1} to {2}"
                    ).format(file, from_code_set, to_code_set),
                    stderr=str(err), stderr_lines=str(err).splitlines()
                )
        return dir_path

    def _fetch_mvs_data(self, src, is_binary, encoding):
        """ Copy a sequential data set or a partitioned data set member
            to a USS file
        """
        fd, file_path = tempfile.mkstemp()
        os.close(fd)
        cmd = "cp -B \"//'{0}'\" {1}"
        if not is_binary:
            cmd = cmd.replace(" -B", "")
        rc, out, err = self._run_command(cmd.format(src, file_path))
        if rc != 0:
            os.remove(file_path)
            self._fail_json(
                msg="Unable to copy {0} to USS".format(src),
                stdout=str(out), stderr=str(err), rc=rc,
                stdout_lines=str(out).splitlines(),
                stderr_lines=str(err).splitlines()
            )
        if not is_binary:
            # enc_utils = encode_utils.EncodeUtils(self.module)
            from_code_set = encoding.get('from')
            to_code_set = encoding.get('to')
            try:
                self._uss_convert_encoding(file_path, file_path, from_code_set, to_code_set)
                # enc_utils.uss_convert_encoding(
                #     file_path, file_path, from_code_set, to_code_set
                # )
            except Exception as err:
                os.remove(file_path)
                self._fail_json(
                    msg=(
                        "An error occured while converting encoding of the data set"
                        " {0} from {1} to {2}"
                    ).format(src, from_code_set, to_code_set),
                    stderr=str(err), stderr_lines=str(err).splitlines()
                )
        return file_path


def run_module():
    # ********************************************************** #
    #                Module initialization                       #
    # ********************************************************** #

    module = AnsibleModule(
        argument_spec=dict(
            src=dict(required=True, type='str'),
            dest=dict(required=True, type='path'),
            fail_on_missing=dict(required=False, default=True, type='bool'),
            flat=dict(required=False, default=True, type='bool'),
            is_binary=dict(required=False, default=False, type='bool'),
            use_qualifier=dict(required=False, default=False, type='bool'),
            validate_checksum=dict(required=False, default=True, type='bool'),
            encoding=dict(required=False, type='dict')
        )
    )

    src = module.params.get("src")
    if module.params.get("use_qualifier"):
        module.params['src'] = Datasets.hlq() + "." + src

    # The user did not provide any encoding information. The default values
    # will be used.
    if not module.params.get("encoding"):
        module.params['encoding'] = {"from": "IBM-1047", "to": "ISO8859-1"}

    module.params.update(dict(
        from_encoding=module.params.get('encoding').get('from'),
        to_encoding=module.params.get('encoding').get('to'))
    )

    # ********************************************************** #
    #                   Verify paramater validity                #
    # ********************************************************** #

    arg_def = dict(
        src=dict(arg_type='data_set_or_path', required=True),
        dest=dict(arg_type='path', required=True),
        fail_on_missing=dict(arg_type='bool', required=False, default=True),
        is_binary=dict(arg_type='bool', required=False, default=False),
        use_qualifier=dict(arg_type='bool', required=False, default=False),
        from_encoding=dict(arg_type='encoding', default="IBM-1047"),
        to_encoding=dict(arg_type='encoding', default="ISO-8859-1")
    )

    fetch_handler = FetchHandler(module)

    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parsed_args = parser.parse_args(module.params)
    except ValueError as err:
        fetch_handler._fail_json(
            msg="Parameter verification failed", stderr=str(err)
        )
    src = parsed_args.get('src')
    b_src = to_bytes(src)
    fail_on_missing = boolean(parsed_args.get('fail_on_missing'))
    use_qualifier = boolean(parsed_args.get('use_qualifier'))
    is_binary = boolean(parsed_args.get('is_binary'))
    encoding = module.params.get('encoding')

    # ********************************************************** #
    #  Check for data set existence and determine its type       #
    # ********************************************************** #

    res_args = dict()
    _fetch_member = '(' in src and src.endswith(')')
    ds_name = src if not _fetch_member else src[:src.find('(')]
    try:
        ds_utils = data_set_utils.DataSetUtils(module, ds_name)
        if ds_utils.data_set_exists() is False:
            if fail_on_missing:
                fetch_handler._fail_json(
                    msg=(
                        "The data set '{0}' does not exist or is "
                        "uncataloged".format(ds_name)
                    )
                )
            module.exit_json(
                note=(
                    "Source '{0}' was not found. No data was fetched".format(ds_name)
                )
            )
        ds_type = ds_utils.get_data_set_type()
        if not ds_type:
            fetch_handler._fail_json(msg="Unable to determine data set type")

    except Exception as err:
        fetch_handler._fail_json(msg="Error while gathering data set information", stderr=str(err))

    # ********************************************************** #
    #                  Fetch a sequential data set               #
    # ********************************************************** #

    if ds_type == 'PS':
        file_path = fetch_handler._fetch_mvs_data(src, is_binary, encoding)
        res_args['remote_path'] = file_path

    # ********************************************************** #
    #    Fetch a partitioned data set or one of its members       #
    # ********************************************************** #

    elif ds_type == "PO":
        if _fetch_member:
            member_name = src[src.find('(') + 1:src.find(')')]
            if not ds_utils.data_set_member_exists(member_name):
                fetch_handler._fail_json(
                    msg=("The data set member '{0}' was not found inside data"
                         " set '{1}'").format(member_name, ds_name)
                )
            file_path = fetch_handler._fetch_mvs_data(src, is_binary, encoding)
            res_args['remote_path'] = file_path
        else:
            res_args['remote_path'] = fetch_handler._fetch_pdse(src, is_binary, encoding)

    # ********************************************************** #
    #                  Fetch a USS file                          #
    # ********************************************************** #

    elif ds_type == 'USS':
        if not os.access(b_src, os.R_OK):
            fetch_handler._fail_json(
                msg="File '{0}' does not have appropriate read permission".format(src)
            )
        file_path = fetch_handler._fetch_uss_file(src, is_binary, encoding)
        res_args['remote_path'] = file_path

    # ********************************************************** #
    #                  Fetch a VSAM data set                     #
    # ********************************************************** #

    elif ds_type == 'VSAM':
        file_path = fetch_handler._fetch_vsam(src, is_binary, encoding)
        res_args['remote_path'] = file_path

    res_args['file'] = ds_name
    res_args['ds_type'] = ds_type
    module.exit_json(**res_args)


def main():
    run_module()


if __name__ == '__main__':
    main()
