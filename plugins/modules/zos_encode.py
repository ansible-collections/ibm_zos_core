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
    - Convert text encoding located on a Unix file or path, MVS PS(sequential data set), PDS/E and KSDS(VSAM data set)
    - Convert text encoding from ASCII to EBCDIC and EBCDIC to ASCII
    - For uncatalogged data set, catalog it before conversion is required, see zos_dataset module to do the catalog.
options:
  from_encoding:
    required: true
    description:
    - It indicates the encoding of the input file or data set
    - Both ASCII(ISO8859-1) and EBCDIC(IBM-1047) are supported now
    type: String
    default: IBM-1047
  to_encoding:
    required: true
    description:
    - This indicates the encoding of the output file or data set
    - Both ASCII(ISO8859-1) and EBCDIC(IBM-1047) are supported now
    type: String
    default: ISO8859-1
  src:
    required: true
    description:
    - It is the location of the data
    - It can be a Unix file or path
    - It can be an MVS data set(PS, PDS/E, VSAM)
    type: str
  dest:
    required: false
    description:
    - It is the location of the data after the encoding conversion
    - It can be a Unix file or path 
    - It can be an MVS data set(PS, PDS/E, VSAM)
    - If length of the file name in src is more the 8 characters, name will be truncated when converting to a PDS
    type: str
  backup:
    required: false
    description:
      - Create a backup file or data set so you can get the original file back
        if there is any error in the conversion
      - if src is a Unix file or path, backup file name patter like this: path/src_name.test.1.d20200305-t104849.pax.Z
      - if src is an MVS data set， backup file name patter like this: src_name.BAK.D200305 
    type: bool
    default: false
'''

EXAMPLES = '''
- name: Convert data encoding (EBCDIC to ASCII) from a Unix file to the same file 
  zos_encode:
    src: ./zos_encode/test.data
    dest: 
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (EBCDIC to ASCII) from a Unix file to another file and backing up the original
  copy:
    src: ./zos_encode/test.data 
    dest: /user/zos_encode_out/test.data
    backup: yes

- name: Convert data encoding (EBCDIC to ASCII) from a Unix file to a different file 
  zos_encode:
    src: ./zos_encode/test.data
    dest: ./zos_encode/test.out
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (EBCDIC to ASCII) from a Unix file to a Unix path
  zos_encode:
    src: /u/user1/zos_encode/test.data
    dest: /u/user1/zos_encode_out/
    from_encoding: IBM-1047
    to_encoding: ISO8859-1
    
- name: Convert data encoding (ASCII to EBCDIC) from a Unix path to a different Unix path
  zos_encode:
    src: ./zos_encode
    dest: ./zos_encode_out
    from_encoding: ISO8859-1
    to_encoding: IBM-1047
    
- name: Convert data encoding (EBCDIC to ASCII) from a Unix file to a sequential data set
  zos_encode:
    src: ./zos_encode/test
    dest: USER.TEST.PS 
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (ASCII to EBCDIC) from a Unix path to a partitioned data set (extend)
  zos_encode:
    src: /u/zos_encode
    dest: USER.TEST.PDS
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (ASCII to EBCDIC) from a Unix file to a member in partitioned data set
  zos_encode:
    src: /u/zos_encode/test
    dest: USER.TEST.PDS(TESTO)
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (EBCDIC to ASCII) from a sequential data set to a Unix file
  zos_encode:
    src: USER.TEST.PS 
    dest: ./zos_encode/test
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (ASCII to EBCDIC) from a partitioned data set (extend) to a Unix path
  zos_encode:
    src: USER.TEST.PDS
    dest: /u/zos_encode
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (ASCII to EBCDIC) from a sequential data set to a different sequential data set
  zos_encode:
    src: USER.TEST.PS
    dest: USER.TEST1.PS
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (EBCDIC to ASCII) from a sequential data set to a partitioned data set (extended)
  zos_encode:
    src: USER.TEST.PS
    dest: USER.TEST1.PDS
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (ASCII to EBCDIC) from a Unix file to a VSAM data set
  zos_encode:
    src: /u/zos_encode/test
    dest: USER.TEST.VS
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (EBCDIC to ASCII) from a VSAM data set to a Unix file
  zos_encode:
    src: USER.TEST.VS
    dest: /u/zos_encode/test
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (EBCDIC to ASCII) from a VSAM data set to a sequential data set
  zos_encode:
    src: USER.TEST.VS
    dest: USER.TEST.PS
    from_encoding: IBM-1047
    to_encoding: ISO8859-1

- name: Convert data encoding (ASCII to EBCDIC) from a sequential data set to a VSAM data set
  zos_encode:
    src: USER.TEST.PS
    dest: USER.TEST.VS
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

- name: Convert data encoding (ASCII to EBCDIC) from a sequential data set to a VSAM data set
  zos_encode:
    src: USER.TEST.PS
    dest: USER.TEST.VS
    from_encoding: ISO8859-1
    to_encoding: IBM-1047

'''

RETURN = '''
from_encoding:
    description: The encoding of the input file or data set
    returned: always
    type： str
    sample: IBM-1047
to_encoding:
    returned: always
    description: The encoding of the output file or data set
    type： str
    sample: ISO8859-1
src:
    description: The name of the input file or data set
    returned: always
    type： str
dest:
    description: The name of the output file or data set
    returned: always
    type： str
backup_file:
    description: Name of backup file created
    returned: changed and if backup=yes
    type: str
    sample: /path/test.1.d20200305-t104849.pax.Z (if src is a Unix file or path)
    sample: USER.TEST.PS.BAK.D200305 (if src is an MVS data set)
changed:
    description: True if the state was changed, otherwise False
    returned: always
    type: bool
'''

import time
import tarfile
import re
from math import floor, ceil
from os import chmod, path, walk
from tempfile import NamedTemporaryFile, TemporaryDirectory
from ansible.module_utils.basic import AnsibleModule
from zoautil_py import Datasets

def listdsi_data_set(ds, module):
    ''' To call zOAU mvscmdauth to invoke IDCAMS LISTCAT command to get the record length and space used 
        Then estimate the space used by the VSAM data set 
    '''
    err_msg  = None
    reclen   = 0
    space_u  = 0
    listcat_cmd = " LISTCAT ENT('{}') ALL".format(ds)
    cmd = 'echo "{}" | mvscmdauth --pgm=ikjeft01 --systsprt=stdout --systsin=stdin'.format(listcat_cmd)
    rc, stdout, stderr = run_command(cmd, module)
    if not rc:
        find_reclen = re.findall(r'MAXLRECL-*\d+', stdout)
        find_cisize = re.findall(r'CISIZE-*\d+', stdout)
        find_recnum = re.findall(r'REC-TOTAL-*\d+', stdout)
        find_freeci = re.findall(r'FREESPACE-%CI-*\d+', stdout)
        find_freeca = re.findall(r'FREESPACE-%CA-*\d+', stdout)
        find_cioca  = re.findall(r'CI/CA-*\d+', stdout)
        find_trkoca = re.findall(r'TRACKS/CA-*\d+', stdout)
        if find_reclen:
            reclen = int(''.join(re.findall(r'\d+', find_reclen[0])))
        if find_cisize:
            cisize = int(''.join(re.findall(r'\d+', find_cisize[0])))
        if find_recnum:
            recnum = int(''.join(re.findall(r'\d+', find_recnum[0])))
        if find_freeci:
            freeci = int(''.join(re.findall(r'\d+', find_freeci[0])))
        if find_freeca:
            freeca = int(''.join(re.findall(r'\d+', find_freeca[0])))
        if find_cioca:
            cioca  = int(''.join(re.findall(r'\d+', find_cioca[0])))
        if find_trkoca:
            trkoca = int(''.join(re.findall(r'\d+', find_trkoca[0])))
        rec_in_ci = floor((cisize - cisize * freeci - 10) / reclen)
        ci_num    = ceil(recnum / rec_in_ci)
        ca_num    = ceil(ci_num / (cioca * (1 - freeca)))
        # For 3390, 56664 bytes / track
        space_u   = ceil(ca_num * trkoca * 566664 / 1024)
    else:
        err_msg = "Failed when getting the data set info for {}: {}".format(ds, stderr)
    return err_msg, reclen, space_u

def exit_when_exception(err_msg, result, module):
    ''' To call Ansible module.fail_json to exit with a warning messge '''
    result['msg'] = err_msg
    module.fail_json(**result)

def run_command(cmd, module):
    ''' To call Ansible module.run_command to execute command in USS '''
    try:
        rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    except:
        err_msg = 'Failed to run command {}: {}.'.format(cmd, stderr)
        module.fail_json(msg=err_msg)
    return rc, stdout, stderr

def uss_convert_encoding(src, dest, from_encoding, to_encoding, module):
    ''' Convert the encoding of the data in a USS file '''
    convert_rc = False
    err_msg    = None
    if not src == dest:
        temp_f = dest
    else:
        f_temp = NamedTemporaryFile(delete=False)
        temp_f = f_temp.name
    conv_cmd = 'iconv -f {} -t {} {} > {}'.format(from_encoding, to_encoding, src, temp_f)
    rc, stdout, stderr = run_command(conv_cmd, module)
    if not rc:
        if not (temp_f == dest):
            mv_cmd = ['mv', temp_f, dest]
            rc, stdout, stderr = run_command(mv_cmd, module)
            f_temp.close()
            convert_rc = True
        else:
            convert_rc = True
    else:
        err_msg = 'Failed when calling iconv commad: {}'.format(stderr)
    return convert_rc, err_msg 

def get_codeset(module):
    ''' To use USS command 'iconv -l' to get the current code set list '''
    code_set = None
    iconvl_cmd = ['iconv', '-l']
    rc, stdout, stderr = run_command(iconvl_cmd, module)
    if stdout:
        code_set_list = list(filter(None, re.split(r'[\n|\t]', stdout)))
        code_set = [c for i, c in enumerate(code_set_list) if i > 0 and i % 2 == 0]
    return code_set
    
def create_temp_ds_name(llq):
    temp_ds_hlq = Datasets.hlq()
    current_date = time.strftime("D%y%m%d", time.localtime())
    current_time = time.strftime("T%H%M%S", time.localtime())
    temp_dataset = temp_ds_hlq + '.' + current_date + '.' + current_time + '.' + llq
    return temp_dataset
    
def delete_temp_ds(temp_ds):
    Datasets.delete(temp_ds)

def temp_data_set(reclen, space_u):
    err_msg = None
    temp_ps = create_temp_ds_name('TEMP')
    size    = str(space_u * 2) + 'K'
    rc = Datasets.create(temp_ps, "SEQ", size, "FB", "", reclen)
    if rc:
        err_msg = 'Failed when creating a temporary sequential data set: {}'.format(stderr)
    return err_msg, temp_ps
    
def copy_vsam_ps(vsam, ps, module):
    err_msg = None
    repro_cmd = '''  REPRO INDATASET({}) -
    OUTDATASET({}) REPLACE '''.format(vsam, ps)
    cmd = 'echo "{}" | mvscmdauth --pgm=idcams --sysprint=stdout --sysin=stdin'.format(repro_cmd)
    rc, stdout, stderr = run_command(cmd, module)
    if rc:
        err_msg = 'Failed when copying VSAM data set {} to a temporary data set: {}'.format(vsam, stderr)
    return err_msg

def copy_uss2mvs(src, dest, ds_type, module):
    if ds_type == 'PO':
        tempdir = path.join(src, '*') 
        cp_uss2mvs = 'cp -CM -F rec {} "//\'{}\'" '.format(tempdir, dest)
    else:
        cp_uss2mvs = 'cp -F rec {} "//\'{}\'" '.format(src, dest)
    rc, stdout, stderr = run_command(cp_uss2mvs, module)
    return rc, stdout, stderr

def copy_ps2uss(src, temp_src, module):
    cp_ps2uss = 'cp -F rec "//\'{}\'" {}'.format(src, temp_src)
    rc, stdout, stderr = run_command(cp_ps2uss, module)
    return rc, stdout, stderr

def copy_pds2uss(src, temp_src, module):
    cp_pds2uss = 'cp -U -F rec "//\'{}\'" {}'.format(src, temp_src)
    rc, stdout, stderr = run_command(cp_pds2uss, module)
    return rc, stdout, stderr

def uss_convert_encoding_prev(src, dest, from_encoding, to_encoding, module):
    convert_rc = False
    err_msg    = None
    if not path.isfile(src):
        for (dirname, subshere, fileshere) in walk(src):
            if len(fileshere) == 0:
                err_msg = 'Directory {} is empty. Please check!'.format(src)
            elif len(fileshere) == 1:
                src = path.join(dirname, fileshere[0])
                if not path.isfile(dest):
                    dest = path.join(dest, fileshere[0])
                convert_rc, err_msg = uss_convert_encoding(src, dest, from_encoding, to_encoding, module)
            else:
                if path.isfile(dest):
                    err_msg = 'Conversion between the directory {} with more than 1 files to the normal file {} is invalid.'.format(src, dest)
                else:
                    for files in fileshere:
                        src_f   = path.join(dirname, files)
                        dest_f  = path.join(dest, files)
                        convert_rc, err_msg = uss_convert_encoding(src_f, dest_f, from_encoding, to_encoding, module)
    else:
        if not path.isfile(dest):
            head, tail = path.split(path.abspath(src))
            dest       = path.join(dest, tail)
        convert_rc, err_msg = uss_convert_encoding(src, dest, from_encoding, to_encoding, module)
    return convert_rc, err_msg

def mvs_convert_encoding_prev(src, dest, ds_type_src, ds_type_dest, from_encoding, to_encoding, module):
    convert_rc = False
    err_msg    = None
    temp_src   = src
    temp_dest  = dest
    if ds_type_src == 'PS':
        f0_temp = NamedTemporaryFile(delete=False)
        temp_src = f0_temp.name
        rc, stdout, stderr = copy_ps2uss(src, temp_src, module)
        if rc:
            err_msg = 'Faild when coping to USS file: {}'.format(stderr)
    if ds_type_src == 'PO':
        d0_temp = TemporaryDirectory()
        temp_src = d0_temp.name
        rc, stdout, stderr = copy_pds2uss(src, temp_src, module)
        if rc:
            err_msg = 'Faild when coping to USS file: {}'.format(stderr)
    if ds_type_src == 'VSAM':
        err_msg, reclen, space_u = listdsi_data_set(src, module)
        if not err_msg:
            err_msg, temp_ps = temp_data_set(reclen, space_u)
            if not err_msg:
                err_msg = copy_vsam_ps(src.upper(), temp_ps, module)
                if not err_msg:
                    f1_temp = NamedTemporaryFile(delete=False)
                    temp_src = f1_temp.name
                    rc, stdout, stderr = copy_ps2uss(temp_ps, temp_src, module)
                    delete_temp_ds(temp_ps)
                    if rc:
                        err_msg = 'Faild when coping to USS file: {}'.format(stderr)
    if ds_type_dest == 'PS' or ds_type_dest == 'VSAM':
        f_temp = NamedTemporaryFile(delete=False)
        temp_dest = f_temp.name
    if ds_type_dest == 'PO':
        d_temp = TemporaryDirectory()
        temp_dest = d_temp.name
    if not err_msg:
        rc, err_msg = uss_convert_encoding_prev(temp_src, temp_dest, from_encoding, to_encoding, module)
        if rc:
            if not ds_type_dest:
                convert_rc = rc
            else:
                if ds_type_dest == 'VSAM':
                    err_msg, reclen, space_u = listdsi_data_set(dest, module)
                    if not err_msg:
                        err_msg, temp_ps = temp_data_set(reclen, space_u)
                        rc, stdout, stderr = copy_uss2mvs(temp_dest, temp_ps, 'PS', module)
                        if not rc:
                            err_msg = copy_vsam_ps(temp_ps, dest.upper(), module)
                            delete_temp_ds(temp_ps)
                            if not err_msg:
                                convert_rc = True
                else:
                    rc, stdout, stderr = copy_uss2mvs(temp_dest, dest, ds_type_dest, module) 
                    if not rc:
                        convert_rc = True
                    else:
                        err_msg = 'Failed when copying back to the MVS data set {}: {}'.format(dest, stderr)
    return convert_rc, err_msg
    
def uss_file_backup(src, module):
    err_msg  = None
    src_name = path.abspath(src)
    ext      = time.strftime("D%Y%m%d-T%H%M%S", time.localtime()).lower()
    backup_f = '{}.{}.pax.Z'.format(src,ext)
    bk_cmd   = 'pax -wzf {} {}'.format(backup_f, src_name)
    rc, stdout, stderr = run_command(bk_cmd, module)
    if rc:
        err_msg = 'Could not make backup of {} to {}: {}'.format(src, backup_f, stderr)
    return backup_f, err_msg

def mvs_file_backup(src, module):
    err_msg      = None
    ds           = src.upper()
    dsn          = ds
    if '(' in dsn:
        dsn      = ds[0:ds.rfind('(',1)]
    current_date = time.strftime("D%y%m%d", time.localtime())
    if len(dsn) <= 30:
        bk_dsn   = '{}.BAK.{}'.format(dsn, current_date)
    else:
        temp     = dsn.split('.')
        for i in range(len(temp) - 2, 1, -1):
            if not temp[i] == '@':
                temp[i] = '@'
                break
        bk_dsn   = '.'.join(temp)
    bk_sysin     = ''' COPY DATASET(INCLUDE( {} )) -
    RENUNC({}, -
    {}) -
    CATALOG -
    OPTIMIZE(4)  '''.format(dsn, dsn, bk_dsn)
    bkup_cmd     = "echo '{}' | mvscmdauth --pgm=adrdssu --sysprint=stdout --sysin=stdin".format(bk_sysin)
    rc, stdout, stderr = run_command(bkup_cmd, module)
    if rc > 4:
        if 'DUPLICATE' in stdout:
            err_msg = 'Backup data set {} exists, please check'.format(bk_dsn)
        else:
            err_msg = "Failed when creating the backup of the data set {} : {}". format(dsn, stdout)
            if Datasets.exists(bk_dsn):
                delete_temp_ds(bk_dsn)
    return bk_dsn, err_msg

def check_pds_member(ds, mem):
    check_rc = False
    err_msg  = None
    if mem in Datasets.list_members(ds):
        check_rc = True
    else:
        err_msg = 'Cannot find member {} in {}'.format(mem, ds)
    return check_rc, err_msg

def check_mvs_dataset(ds, module):
    ''' To call zOAU mvscmdauth to check a cataloged data set exists or not '''
    check_rc = False
    err_msg  = None
    ds_type  = None
    list_cmd = " LISTDS '{}' ".format(ds)
    cmd = 'echo "{}" | mvscmdauth --pgm=ikjeft01 --systsprt=stdout --systsin=stdin'.format(list_cmd)
    rc, stdout, stderr = run_command(cmd, module)
    if rc <= 4:
        check_rc = True
        if ' PS ' in stdout:
            ds_type = 'PS'
        if ' PO ' in stdout:
            ds_type = 'PO'
        if ' VSAM ' in stdout:
            ds_type = 'VSAM'
    else:
        if ' NOT IN CATALOG ' in stdout:
            err_msg = "Data set {} is not catalogged, please check the name again.".format(ds)
    return check_rc, ds_type, err_msg
    
def check_file(file, mvspat, module):
    ''' check file is a Unix file or an MVS data set '''
    is_uss  = False
    is_mvs  = False
    ds_type = None
    err_msg = None
    if path.sep in file:
        is_uss = path.exists(path.abspath(file))
        if not is_uss:
            err_msg = "File {} does not exist.".format(file)
    else:
        if re.match(mvspat, file):
            ds = file.upper()
            if '(' in ds:
                dsn  = ds[0:ds.rfind('(',1)]
                mem  = ''.join(re.findall(r'[(](.*?)[)]', ds))
                rc, ds_type, err_msg = check_mvs_dataset(dsn, module)
                if rc:  
                    if ds_type == 'PO':
                        is_mvs, err_msg = check_pds_member(dsn, mem)
                        ds_type = 'PS'
                    else:
                        err_msg = 'Data set {} is not a partitioned data set'.format(dsn)
            else:
                is_mvs, ds_type, err_msg = check_mvs_dataset(ds, module)
            if not is_mvs:
                is_uss = path.exists(path.abspath(file))
        else:
            is_uss = path.exists(path.abspath(file))
            if not is_uss:
                err_msg = "The file {} is neither an existing Unix file nor an invalid MVS data set.".format(file)
    return is_uss, is_mvs, ds_type, err_msg

def run_module():
    module_args = dict(
        src           = dict(type='str', required=True),
        dest          = dict(type='str'),
        from_encoding = dict(type='str', default='IBM-1047'),
        to_encoding   = dict(type='str', default='ISO8859-1'),
        backup        = dict(type='bool', default=False),
        is_catalog    = dict(type='bool', default=True),
        volume        = dict(type='str')
    )
    module = AnsibleModule(
        argument_spec       = module_args,
        supports_check_mode = True
    )
    src           = module.params.get("src")
    dest          = module.params.get("dest")
    backup        = module.params.get('backup')
    from_encoding = module.params.get('from_encoding').upper()
    to_encoding   = module.params.get('to_encoding').upper()
    is_catalog    = module.params.get('is_catalog')
    volume        = module.params.get('volume')
    backup_file   = None
    changed       = False
    is_uss_src    = False
    is_mvs_src    = False
    is_uss_dest   = False
    is_mvs_dest   = False
    ds_type_src   = None
    ds_type_dest  = None
    err_msg       = None
    convert_rc    = False
    mvspat        = re.compile(r'^[a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}([.][a-zA-Z#$@][a-zA-Z0-9#$@-]{0,7}){0,21}([(][@$#A-Za-z][@$#A-Za-z0-9]{0,7}[)]){0,1}$')
    result = dict(
        changed       = changed,
        from_encoding = from_encoding,
        to_encoding   = to_encoding,
        src           = src,
        dest          = dest
    )

    ''' Check input code set is valid or not '''
    code_set = get_codeset(module)
    if not(from_encoding in code_set and to_encoding in code_set):
        err_msg = "Invalid codeset: Please check the value of the from_encoding or to_encoding!"
        exit_when_exception(err_msg, result, module)
    if from_encoding == to_encoding:
        err_msg = "The value of the from_encoding and to_encoding are the same, no need to do the conversion!"
        exit_when_exception(err_msg, result, module)

    ''' Check src/dest is a USS file or an MVS data set '''
    is_uss_src, is_mvs_src, ds_type_src, err_msg = check_file(src, mvspat, module)
    if err_msg:
            exit_when_exception(err_msg, result, module)
    if not dest:
            dest = src
            is_uss_dest  = is_uss_src
            is_mvs_dest  = is_mvs_src
            ds_type_dest = ds_type_src
    else:
        is_uss_dest, is_mvs_dest, ds_type_dest, err_msg = check_file(dest, mvspat, module)
        if err_msg:
            exit_when_exception(err_msg, result, module)
    result['dest'] = dest
    
    if backup:
        if is_uss_src:
            backup_file, err_msg = uss_file_backup(src, module)
        else:
            backup_file, err_msg = mvs_file_backup(src, module)
        if err_msg:
            exit_when_exception(err_msg, result, module)
    result['backup_file'] = backup_file

    if is_uss_src and is_uss_dest:
        convert_rc, err_msg = uss_convert_encoding_prev(src, dest, from_encoding, to_encoding, module)
    else:
        convert_rc, err_msg = mvs_convert_encoding_prev(src, dest, ds_type_src, ds_type_dest, from_encoding, to_encoding, module)
    if err_msg:
        exit_when_exception(err_msg, result, module)

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
