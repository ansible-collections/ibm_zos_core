# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
module: zos_encode
author: Zhao Lu <zlbjlu@cn.ibm.com>
short_description: Convert text encoding from ASCII to EBCDIC and EBCDIC to ASCII
description:
    - Convert text encoding located on USS(Unix System Services) or PS(sequential data set), PDS/E member
    - Convert text encoding from ASCII to EBCDIC and EBCDIC to ASCII
options:
  from_encoding:
    required: true
    description:
    - It indicates the encoding of the input file or data set
    - Both ASCII(ISO8859-1) and EBCDIC(IBM-1047) are supported now
    type: String
    default: EBCDIC
  to_encoding:
    required: false
    description:
    - This indicates the encoding of the output file or data set
    - Both ASCII(ISO8859-1) and EBCDIC(IBM-1047) are supported now
    - If it's not specified, it will depends on the setting of the from_encoding
      If from_encoding is set to EBCDIC, it will be set to ASCII
      If from_encoding is set to ASCII, it will be set to EBCDIC
    type: String
  src:
    required: true
    description:
    - It is the location of the data
    - It can be a Unix file(USS) or a sequential data set(MVS), PDS Member(MVS)
    - VSAM is not supported now
    type: str
  dest:
    required: false
    description:
    - It is the location of the data after the encoding conversion
    - It can be a Unix file(USS) or a sequential data set(MVS)
    - VSAM is not supported now
    type: str
  backup:
    required: false
    description:
      - Create a backup file or data set so you can get the original file back
        if there is any error in the conversion
    type: bool
    default: false
'''

EXAMPLES = '''
- name: convert a Unix file(USS) from ASCII to EBCDIC
  zos_encode:
    src: ./test.data
    from_encoding: ASCII

- name: convert a Unix file(USS) from EBCDIC to ASCII
  zos_encode:
    src: ./test.data
    from_encoding: EBCDIC

- name: convert a sequential data set(MVS) from EBCDIC to ASCII
  zos_encode:
    src: USER.TEST.PS
    from_encoding: EBCDIC

- name: convert a sequential data set(MVS) from ASCII to EBCDIC
  zos_encode:
    src: USER.TEST.PS
    from_encoding: ASCII
    to_encoding: EBCDIC

- name: convert a PDS member (MVS) from ASCII to EBCDIC
  zos_encode:
    src: USER.TEST.PS(TEST)
    from_encoding: ASCII
    to_encoding: EBCDIC
'''

RETURN = '''
from_encoding:
    description: The encoding of the input file or data set
    returned: always
    type： str
    sample: EBCDIC
to_encoding:
    returned: always
    description: The encoding of the output file or data set
    type： str
    sample: ASCII
src:
    description: The name of the input file or data set
    returned: always
    type： str
dest:
    description: The name of the output file or data set
    returned: always
    type： str
backup_file:
    description: Name of the backup file that was created.
    returned: if backup==true
    type: str
    sample: test.bak
changed:
    description: True if the state was changed, otherwise False
    returned: always
    type: bool
'''

import time
import tarfile
import re
from os import chmod, path
from tempfile import NamedTemporaryFile
from ansible.module_utils.basic import AnsibleModule
from zoautil_py import Datasets


def uss_convert_encoding(src, dest, from_encoding, to_encoding, module):
    ''' Convert the encoding of the data in a USS file
        from EBCDIC to ASCII and ASCII to EBCDIC '''
    convert_rc = False
    err_msg    = ''
    encodings = dict(EBCDIC='IBM-1047', ASCII='ISO8859-1')
    if not (src == dest):
        temp_f = dest
    else:
        f_temp = NamedTemporaryFile(delete=False)
        temp_f = f_temp.name
    conv_cmd = 'iconv -f {} -t {} {} > {}'.format(encodings[from_encoding], encodings[to_encoding], src, temp_f)
    rc, stdout, stderr = module.run_command(conv_cmd, use_unsafe_shell=True)
    if rc:
        err_msg = 'Failed when converting: ' + stderr
    else:
        if not (temp_f == dest):
            mv_cmd = 'mv {} {}'.format(temp_f, dest)
            rc, stdout, stderr = module.run_command(mv_cmd)
            f_temp.close()
            if rc:
                err_msg = 'Failed when moving the converted text to the target file: ' + stderr
            else:
                convert_rc = True
        else:
            convert_rc = True
    return convert_rc, err_msg


def mvs_convert_encoding(src, dest, from_encoding, to_encoding, module):
    ''' Convert the encoding of the data in a PS(sequential) data set
        from EBCDIC to ASCII and ASCII to EBCDIC '''
    convert_rc = False
    err_msg    = ''
    f_temp = NamedTemporaryFile(delete=False)
    f1_temp = NamedTemporaryFile(delete=False)
    temp_f = f_temp.name
    temp_f1 = f1_temp.name
    copy_cmd1 = 'cp "//\'{}\'" {}'.format(src, temp_f)
    rc, stdout, stderr = module.run_command(copy_cmd1)
    if not rc:
        rc, msg = uss_convert_encoding(temp_f, temp_f1, from_encoding, to_encoding, module)
        if not rc:
            err_msg = msg
        else:
            copy_cmd2 = 'cp {} "//\'{}\'" '.format(temp_f1, dest)
            rc, stdout, stderr = module.run_command(copy_cmd2)
            if rc:
                if 'EDC5061I' in stderr:
                    err_msg = 'Failed when coping: Data set {} is in use ...'.format(dest)
                else:
                    err_msg = 'Failed when coping: ' + stderr
            else:
                convert_rc = True
    f1_temp.close()
    f_temp.close()
    return convert_rc, err_msg

def uss_file_backup(src):
    err_msg = ''
    bt = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    apath = path.abspath(src)
    tar_name = apath + '_backup' + bt + '.tar'
    try:
        with tarfile.open(tar_name, "w:gz") as tar:
            tar.add(src)
    except tarfile.TarError:
        err_msg = 'Failed when backup the file {}'.format(src)
        module.fail_json(msg=err_msg)
    return tar_name


def mvs_file_backup(ds_name, module):
    f_temp = NamedTemporaryFile(delete=False)
    temp_f = f_temp.name
    cp_cmd = 'cp "//\'{}\'" {}'.format(ds_name, temp_f)
    rc, stdout, stderr = module.run_command(cp_cmd)
    if not rc:
        return uss_file_backup(temp_f)
    else:
        err_msg = 'Failed when coping: ' + stderr
        module.fail_json(msg=err_msg)

def run_rexx(script, module):
    temp_f = NamedTemporaryFile(delete=True)
    with open(temp_f.name, 'w') as f:
        f.write(script)
    chmod(temp_f.name, 0o755)
    path_name = path.dirname(temp_f.name)
    script_name = path.basename(temp_f.name)
    exec_cmd = './{}'.format(script_name)
    rc, stdout, stderr = module.run_command(exec_cmd, cwd=path_name)
    return rc, stdout, stderr


def data_set_exists(src, module):
    check_rc = False
    ds_type = ''
    rexx_script = '''/*rexx*/
call outtrap x.
address tso "listcat ent('{}')"
if rc <= 4 then
  say word(x.1,1)
call outtrap off
'''.format(src)
    rc, stdout, stderr = run_rexx(rexx_script, module)
    if not(rc and 'BPXW9018I' not in stderr):
        if 'ENTRY' not in stdout:
            check_rc = True
            if 'NONVSAM' in stdout:
                ds_type = 'NONVSAM'
            else:
                ds_type = 'VSAM'
    else:
        err_msg = 'Failed when checking file: ' + stderr
        module.fail_json(msg=err_msg)
    return check_rc, ds_type


def check_mvs_dataset(file, module):
    err_msg = ''
    is_mvs = False
    ds = file.upper()
    is_mvs, ds_type = data_set_exists(ds, module)
    if not is_mvs:
        err_msg = "The file {} does not exist, please check the file name again.".format(file)
    elif ds_type == 'VSAM':
        err_msg = "Conversion for data in VSAM is not supported now."
    return is_mvs, err_msg

def check_pds_member(ds, mem):
    check_rc = False
    err_msg  = ''
    if mem in Datasets.list_members(ds):
        check_rc = True
    else:
        err_msg = 'Cannot find {} in {}'.format(mem, ds)
    return check_rc, err_msg

def check_file(file, mvspat, module):
    is_uss  = False
    is_mvs  = False
    err_msg = ''
    if path.sep in file:
        is_uss = path.exists(path.abspath(file))
        if not is_uss:
            err_msg = "The file {} does not exist.".format(file)
    else:
        if re.match(mvspat, file):
            ds = file
            if '(' in file:
                ds   = file[0:file.rfind('(',1)]
                mem  = ''.join(re.findall(r'[(](.*?)[)]', file)).upper()
                is_mvs, err_msg = check_mvs_dataset(ds, module)
                if is_mvs:
                    is_mvs, err_msg = check_pds_member(ds, mem)
            else:
                is_mvs, err_msg = check_mvs_dataset(ds, module)
        else:
            is_uss = path.exists(path.abspath(file))
            if not is_uss:
                err_msg = "The file {} is neither an existing Unix file nor an invalid MVS data set.".format(file)
    return is_uss, is_mvs, err_msg


def run_module():
    module_args = dict(
        src=dict(type='str', required=True),
        dest=dict(type='str'),
        from_encoding=dict(type='str', default='EBCDIC', choices=['EBCDIC', 'ASCII']),
        to_encoding=dict(type='str', choices=['EBCDIC', 'ASCII']),
        backup=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    src = module.params.get("src")
    dest = module.params.get("dest")
    from_encoding = module.params.get('from_encoding')
    to_encoding = module.params.get('to_encoding')
    if from_encoding == 'EBCDIC' and not to_encoding:
        to_encoding = 'ASCII'
    if from_encoding == 'ASCII' and not to_encoding:
        to_encoding = 'EBCDIC'
    backup = module.params.get('backup')
    backup_file = ''
    changed = False
    is_uss_src = False
    is_mvs_src = False
    msg = 'Failed'
    err_msg = ''
    mvspat  = re.compile(r'^[a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}([.][a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}){0,21}([(][@$#A-Za-z][@$#A-Za-z0-9]{0,7}[)]){0,1}$')
    convert_rc = False
    result = dict(
        changed=changed,
        from_encoding=from_encoding,
        to_encoding=to_encoding,
        src=src,
        dest=dest,
    )

    is_uss_src, is_mvs_src, err_msg = check_file(src, mvspat, module)
    if err_msg:
        result['msg'] = err_msg
        module.fail_json(**result)

    if not dest:
        dest = src
        result['dest'] = dest
    else:
        if re.match(mvspat, dest):
            is_mvs, err_msg = check_mvs_dataset(dest, module)
            if err_msg:
                result['msg'] = err_msg
                module.fail_json(**result)

    if backup:
        if is_uss_src:
            backup_file = uss_file_backup(src)
        else:
            backup_file = mvs_file_backup(src, module)
        result['backup_file'] = backup_file

    if is_uss_src:
        convert_rc, err_msg = uss_convert_encoding(src, dest, from_encoding, to_encoding, module)
    if is_mvs_src:
        convert_rc, err_msg = mvs_convert_encoding(src, dest, from_encoding, to_encoding, module)

    if convert_rc:
        changed = True
        result = dict(
            changed=changed,
            src=src,
            dest=dest,
            from_encoding=from_encoding,
            to_encoding=to_encoding,
            backup=backup,
            backup_file=backup_file
        )
    else:
        result = dict(
            changed=changed,
            src=src,
            msg=err_msg
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
