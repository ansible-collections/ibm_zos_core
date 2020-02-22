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
    - Convert text encoding located on USS(Unix System Services) or PS(sequential data set)
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
    - It can be a Unix file(USS) or a sequential data set(MVS)
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
from zoautil_py import MVSCmd, Datasets
from zoautil_py.types import DDStatement

def uss_convert_encoding(src, dest, from_encoding, to_encoding):
    ''' Convert the encoding of the data in a USS file 
        from EBCDIC to ASCII and ASCII to EBCDIC '''
     
    convert_rc = False
    f_temp     = NamedTemporaryFile(delete=False)
    temp_f     = f_temp.name
    encodings = dict(EBCDIC = 'IBM-1047', ASCII = 'ISO8859-1')

    (conv_rc, stdout, stderr) = module.run_command('iconv -f %s -t %s %s > %s' % 
                   (encodings[from_encoding], encodings[to_encoding], src, temp_f),
                   use_unsafe_shell=True)

    if conv_rc == 0:
        cmd_mv = ['mv', temp_f, dest]
        (mv_rc, stdout, stderr) = module.run_command(cmd_mv)
    if mv_rc == 0:
        convert_rc = True

    f_temp.close()
    return convert_rc

def mvs_convert_encoding(src, dest, from_encoding, to_encoding):
    ''' Convert the encoding of the data in a PS(sequential) data set 
        from EBCDIC to ASCII and ASCII to EBCDIC '''
    convert_rc = False
    ftemp = NamedTemporaryFile(delete=False)
    tempf = ftemp.name
    encodings = dict(EBCDIC = 'IBM-1047', ASCII = 'ISO8859-1')
    copy_cmd1 = '''cp "//'%s'" %s''' % (src, tempf)
    (copy_rc, stdout, stderr) = module.run_command(copy_cmd1, use_unsafe_shell=True)
    if not copy_rc:
        ftemp1 = NamedTemporaryFile(delete=False)
        tempf1 = ftemp1.name
        (conv_rc, stdout, stderr) = module.run_command('iconv -f %s -t %s %s > %s' % 
               (encodings[from_encoding], encodings[to_encoding], tempf, tempf1),
                                                   use_unsafe_shell=True)
    if not copy_rc:
        copy_cmd2 = '''cp %s "//'%s'" ''' % (tempf1, dest)
        rc, out, err = module.run_command(copy_cmd2)
        if rc:
            module.fail_json(msg=err)
        else:
            convert_rc = True
    ftemp1.close()
    ftemp.close()
    return convert_rc

def uss_file_backup(src):
    bt    = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    apath = path.abspath(src)
    tar_name = apath + '_backup' + bt + '.tar'
    try:
        with tarfile.open(tar_name, "w:gz") as tar:
            tar.add(src)
    except tarfile.TarError:
        msg = 'Failed when backup the file %s' % src
        module.fail_json(msg=msg)
    return tar_name

def mvs_file_backup(ds_name):
    copy_rc = False
    f_temp  = NamedTemporaryFile(delete=False)
    temp_f  = f_temp.name
    cp_cmd  = 'cp "//\'%s\'" %s' % (ds_name, temp_f)
    copy_rc, stdout, stderr = module.run_command(cp_cmd, use_unsafe_shell=True)
    if not copy_rc:
        return uss_file_backup(temp_f)

def run_rexx(script):
    temp_f = NamedTemporaryFile(delete=True)
    with open(temp_f.name, 'w') as f:
        f.write(script)
    chmod(temp_f.name, 0o755)
    path_name = path.dirname(temp_f.name)
    script_name = path.basename(temp_f.name)
    exec_cmd = './%s' % script_name   
    (rc, stdout, stderr) = module.run_command(exec_cmd, cwd=path_name)
    return rc, stdout, stderr

def data_set_exists(src):
    check_rc = False
    ds_type  = ''
    rexx_script = '''/*rexx*/
call outtrap x.
address tso "listcat ent('%s')"
if rc <= 4 then
  say word(x.1,1)
call outtrap off
''' % src
    rc, stdout, stderr = run_rexx(rexx_script)
    if 'ENTRY' not in stdout:
        check_rc = True
        if 'NONVSAM' in stdout:
            ds_type = 'NONVSAM'
        else:
            ds_type = 'VSAM'
    return check_rc, ds_type

def check_mvs_dataset(file):
    msg    = ''
    is_mvs = False
    ds = file.upper()
    is_mvs, ds_type = data_set_exists(ds)
    if not is_mvs:
        msg = "The file %s does not exist, please check the file name again." % file
    elif ds_type == 'VSAM':
        msg = "Conversion for data in VSAM is not supported now."
    return is_mvs, msg

def check_file(file):
    is_uss = False
    is_mvs = False
    msg    = ''
    if path.sep in file:
        is_uss = path.exists(path.abspath(file))
        if not is_uss:
            msg = "The file %s does not exist." % file
    else:
        if re.match(r'^[a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}([.][a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}){0,21}$', file) and len(file) <= 44:
            is_mvs, msg = check_mvs_dataset(file)
        else:
            is_uss = path.exists(path.abspath(file))
            if not is_uss:
                msg = "The file %s is neither an existing Unix file nor an invalid MVS data set." % file
    return is_uss, is_mvs, msg

def run_module():
    global module
    module_args = dict(
        src           = dict(type='str', required=True),
        dest          = dict(type='str'),
        from_encoding = dict(type='str', default='EBCDIC', choices=['EBCDIC', 'ASCII']),
        to_encoding   = dict(type='str', choices=['EBCDIC', 'ASCII']),
        backup        = dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec       = module_args,
        supports_check_mode = True
    )

    src           = module.params.get("src")
    dest          = module.params.get("dest")
    from_encoding = module.params.get('from_encoding')
    to_encoding   = module.params.get('to_encoding')
    if from_encoding == 'EBCDIC':
        to_encoding = 'ASCII'
    backup        = module.params.get('backup')
    backup_file   = ''
    changed       = False
    is_uss_src    = False
    is_mvs_src    = False
    is_uss_dest   = False
    is_mvs_dest   = False
    msg           = 'Failed'
    convert_rc    = False

    result = dict(
        changed       = changed,
        from_encoding = from_encoding,
        to_encoding   = to_encoding,
        src           = src,
        dest          = dest,
        msg           = msg
    )
    
    is_uss_src, is_mvs_src, msg = check_file(src)
    if msg:
        result['msg'] = msg
        module.fail_json(**result)

    if not dest:
        dest = src
        result['dest'] = dest
    else:
        if re.match(r'^[a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}([.][a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}){0,21}$', dest) and len(dest) <= 44:
            is_mvs, msg = check_mvs_dataset(dest)
            if msg:
                result['msg'] = msg
                module.fail_json(**result)

    if backup:
        if is_uss_src:
            backup_file = uss_file_backup(src)
        else:
            backup_file = mvs_file_backup(src)
        result['backup_file'] = backup_file

    if is_uss_src:
        convert_rc = uss_convert_encoding(src, dest, from_encoding, to_encoding)
    if is_mvs_src:
        convert_rc = mvs_convert_encoding(src, dest, from_encoding, to_encoding)

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
            msg=msg
        )

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()