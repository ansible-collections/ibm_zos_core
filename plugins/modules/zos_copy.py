# -*- coding: utf-8 -*-​
# Copyright (c) IBM Corporation 2019, 2020
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: zos_copy
version_added: '0.0.3'
short_description: Copy data sets or files to remote z/OS systems
description:
    - The M(zos_copy) module copies a file or data set from a local or a
      remote machine to a location on the remote machine.
    - Use the M(zos_fetch) module to copy files or data sets from remote locations
      to local machine.
authors:
  - Asif Mahmud <asif.mahmud@ibm.com>
  - Luke Zhao <zlbjlu@cn.ibm.com>
options:
  src:
    description:
    - Local path to a file to copy to the remote z/OS system; can be absolute or
      relative.
    - If I(remote_src=true), then src must be the name of the file, data set
      or data set member on remote z/OS system.
    - If the path is a directory, and the destination is a PDS(E), all the files
      in it would be copied to a PDS(E).
    - If the path is a directory, it is copied (including the source folder name)
      recursively to C(dest).
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
  backup:
    description:
    - Determine whether a backup should be created.
    - When set to C(true), create a backup file including the timestamp information
      so you can get the original file back if you somehow clobbered it incorrectly.
    - No backup is taken when I(remote_src=False) and multiple files are being
      copied.
    type: bool
    default: false
  force:
    description:
    - If C(true), the remote file or data set will be replaced when contents are
      different than the source.
    - If C(false), the file will only be transferred if the destination does not exist.
    type: bool
    default: true
  mode:
    description:
    - The permission of the destination file or directory.
    - If C(dest) is USS, this will act as Unix file mode, otherwise ignored.
    - Refer to the M(copy) module for a detailed description of this parameter.
    type: path
  remote_src:
    description:
    - If C(false), it will search for src at local machine.
    - If C(true), it will go to the remote/target machine for the src.
    type: bool
    default: false
  local_follow:
    description:
    - This flag indicates that filesystem links in the source tree, if they exist,
      should be followed.
    type: bool
    default: true
  is_uss:
    description:
    - Specifies whether C(dest) is a USS location.
    - If C(false), it indicates that the destination is an MVS data set.
    type: bool
    default: false
  is_vsam:
    description:
    - If C(true), indicates that the destination is a VSAM data set.
    type: bool
    default: false
  is_binary:
    description:
    - If C(true), indicates that the file or data set to be copied is a binary file/data set.
    type: bool
    default: false
  is_catalog:
    description:
    - Indicates whether the destination data set is cataloged. If it is not cataloged,
      the data set will be recataloged before copying. After the data set has been
      successfully copied, the destination data set will be uncataloged.
    type: bool
    default: true
  volume:
    description:
    - Name of the volume if I(is_catalog=false).
    type: str
  use_qualifier:
    description:
    - Add user qualifier to data sets.
    type: bool
    default: true
  encoding:
    description:
    - Indicates the encoding of the file or data set on the remote machine.
    - If set to C(ASCII), the module will not convert the encoding to EBCDIC.
    - If set to C(EBCDIC), the module will convert the encoding of the file or data
      set to EBCDIC before copying to destination.
    - Only valid if I(is_binary=false)
    type: str
    default: EBCDIC
  checksum:
    description:
    - SHA1 checksum of the file being copied.
    - Used to validate that the copy of the file or data set was successful.
    - If this is not provided and I(validate=true), Ansible will use local calculated
      checksum of the src file.
    type: str
  validate:
    description:
    - Verrify that the copy operation was successful by comparing the source and
      destination checksum.
    type: bool
    default: true
  wait_s:
    description:
      - The time (in seconds) to wait for an uncataloged data set to be recataloged
    required: false
    default: 10
    type: int
notes:
    - All VSAM data sets are assumed to be cataloged. When trying to copy to an
      uncataloged VSAM data set, it must be recataloged first.
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
    is_uss: true
- name: Copy a local ASCII encoded file and convert to EBCDIC
  zos_copy:
    src: /path/to/file.txt
    dest: /tmp/file.txt
    encoding: EBCDIC
    is_uss: true
- name: Copy file with owner and permission
  zos_copy:
    src: /path/to/foo.conf
    dest: /etc/foo.conf
    owner: foo
    group: foo
    mode: '0644'
- name: If local_follow=true, the module will follow the symbolic link specified in src
  zos_copy:
    src: /path/to/link
    dest: /path/to/uss/location
    is_uss: true
- name: Copy a local file to a PDS member and validate checksum
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.PDSE(member_name)
    validate: true
- name: Copy a single file to a VSAM(KSDS)
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.VSAM
    is_vsam: true
- name: Copy inline content to a sequential dataset and replace existing data
  zos_copy:
    content: 'Hello World'
    dest: SAMPLE.SEQ.DATA.SET
    force: true
- name: Copy a USS file to a sequential data set
  zos_copy:
    src: /path/to/remote/uss/file
    dest: SAMPLE.SEQ.DATA.SET
    remote_src: true
- name: Copy a binary file to an uncataloged PDSE member
  zos_copy:
    src: /path/to/binary/file
    dest: HLQ.SAMPLE.PDSE(member_name)
    is_binary: true
    is_catalog: false
    volume: SCR03
    wait_s: 15
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
- name: Copy a PDS(E) on remote system to an existing PDS(E), replacing the original
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.EXISTING.PDSE
    remote_src: true
    force: true
- name: Copy a PDS(E) member to a new PDS(E) member. Replace if it already exists
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
    description: SHA1 checksum of the file after running copy.
    returned: success
    type: str
    sample: 6e642bb8dd5c2e027bf21dd923337cbb4214f827
md5sum:
    description: MD5 checksum of the file or data set after running copy
    returned: when supported
    type: str
    sample: 2a5aeecc61dc98c4d780b14b330e3282
backup_file:
    description: Name of the backup file or data set that was created.
    returned: changed and if backup=true
    type: str
    sample: 11540.20150212-220915.bak
gid:
    description: Group id of the file, after execution
    returned: success and if is_uss=true
    type: int
    sample: 100
group:
    description: Group of the file, after execution
    returned: success and if is_uss=true
    type: str
    sample: httpd
owner:
    description: Owner of the file, after execution
    returned: success and if is_uss=true
    type: str
    sample: httpd
uid:
    description: Owner id of the file, after execution
    returned: success and if is_uss=true
    type: int
    sample: 100
mode:
    description: Permissions of the target, after execution
    returned: success and if is_uss=true
    type: str
    sample: 0644
size:
    description: Size of the target, after execution.
    returned: changed, src is a file
    type: int
    sample: 1220
state:
    description: State of the target, after execution
    returned: success and if is_uss=true
    type: str
    sample: file
'''

import errno
import filecmp
import grp
import os
import re
import os.path
import platform
import pwd
import shutil
import stat
import tempfile
import traceback
import subprocess
import time    
import codecs
import hashlib
import string
import random

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.six import PY3

from zoautil_py import MVSCmd, Datasets
from zoautil_py import types

# The AnsibleModule object
module = None

def ascii_to_ebcdic(src, content):
    conv_cmd = "iconv -f ISO8859-1 -t IBM-1047"
    rc, out, err = module.run_command(conv_cmd, data=content)
    if rc != 0:
        module.fail_json(msg="Unable to convert encoding of {} to EBCDIC".format(src))
    return out


def _create_temp_data_set_name(LLQ):
    """ Create a temporary data set name """
    chars = string.ascii_uppercase
    HLQ2 = ''.join(random.choice(chars) for i in range(5))
    return Datasets.hlq() + '.' + HLQ2 + '.' + LLQ


def vsam_exists_or_not(ds_name):
    """ Check vsam data set using ZOAU API """
    check_rc      = False
    check_vsam_rc = -1
    sysin_ds_name = _create_temp_data_set_name('sysin')
    sysprint_ds_name = _create_temp_data_set_name('sysprint')

    Datasets.create(sysin_ds_name, "SEQ")
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)

    listcat_sysin = ' LISTCAT ENT(' + ds_name + ') ALL'
    Datasets.write(sysin_ds_name, listcat_sysin)
    dd_statements = []
    dd_statements.append(types.DDStatement(ddName="sysin", dataset=sysin_ds_name))
    dd_statements.append(types.DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
    try:
        check_vsam_rc = MVSCmd.execute_authorized(pgm="idcams", args="", dds=dd_statements)
    except:
        msg = "Failed to call IDCAMS to check the data set {}".format(ds_name)
        module.fail_json(msg=msg)
    
    if check_vsam_rc == 0:
        check_rc   = True
        output     = Datasets.read(sysprint_ds_name)
        findReclen = re.findall(r'MAXLRECL-*\d+', output)
        findHiurba = re.findall(r'HI-U-RBA-*\d+', output)
        reclen     = ''.join(re.findall(r'\d+', findReclen[0]))
        hiurba     = ''.join(re.findall(r'\d+', findHiurba[0]))
    else:
        msg = "Failed to call IDCAMS to check the data set {}".format(ds_name)
        module.fail_json(msg=msg)
    
    Datasets.delete(sysin_ds_name)
    Datasets.delete(sysprint_ds_name)

    return check_rc, reclen, hiurba


def data_set_exists_or_not(ds_name):
    """ check non-vsam data set exist or not  """
    check_rc = False
    try:
        check_rc = Datasets.exists(ds_name)
    except:
        print('')
    return check_rc


def uncatalog_data_set_exists_or_not(ds_name, volume):
    """ check uncataloged data set exist or not """
    check_rc = False
    sysprint_ds_name = _create_temp_data_set_name('sysprint')
    sysin_ds_name = _create_temp_data_set_name('sysin')
    
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)
    Datasets.create(sysin_ds_name, "SEQ")
    
    adrdssu_sysin = ''' DUMP DATASET(INCLUDE( %s ) - 
       BY((CATLG,EQ,NO)))   - 
       SHR OUTDD(LIST)      - 
       LOGINDYNAM((%s)) ''' % (ds_name, volume)
    
    Datasets.write(sysin_ds_name, adrdssu_sysin)
    dd_statements = []
    dd_statements.append(types.DDStatement(ddName="list", dataset="dummy"))
    dd_statements.append(types.DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
    dd_statements.append(types.DDStatement(ddName="sysin", dataset=sysin_ds_name))
    try:
        check_uc_rc = MVSCmd.execute_authorized(pgm="adrdssu", args="TYPRUN=NORUN", dds=dd_statements)
    except:
        msg = "Failed to call ADRDSSU to check the data set {}".format(ds_name)
        module.fail_json(msg=msg)

    if Datasets.read(sysprint_ds_name).find(ds_name) != -1:
       check_rc = True
    
    Datasets.delete(sysin_ds_name)
    Datasets.delete(sysprint_ds_name)

    return check_rc

def copy_to_ps(src, PSname, encoding):
    copy_rc = False
    tempf = codecs.open(src, 'r', encoding='ascii')
    for line in tempf:
        line_bytes = (re.split(b'\n', line.encode('ascii')))
        for record in line_bytes:
            if record != b'':
                rec = record.decode('ascii')
                try:  
                    copy_ps_rc = Datasets.write(PSname, rec, append=True)
                except:
                    msg = "Failed to copy to the data set %s" % PSname
                    module.fail_json(msg=msg)
    if copy_ps_rc == 0:
        copy_rc = True
    return copy_rc

def copy_to_vsam(src, VSAMname):
    copy_rc      = False
    copy_vsam_rc = -1
    sysin_ds_name = _create_temp_data_set_name('sysin')
    sysprint_ds_name = _create_temp_data_set_name('sysprint')

    Datasets.create(sysin_ds_name, "SEQ")
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)

    repro_sysin = ' REPRO INFILE(INPUT) OUTFILE(OUTPUT) '
    Datasets.write(sysin_ds_name, repro_sysin)
    
    dd_statements = []
    dd_statements.append(types.DDStatement(ddName="sysin", dataset=sysin_ds_name))
    dd_statements.append(types.DDStatement(ddName="input", dataset=src))
    dd_statements.append(types.DDStatement(ddName="output", dataset=VSAMname))
    dd_statements.append(types.DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
    try:
        copy_vsam_rc = MVSCmd.execute_authorized(pgm="idcams", args="", dds=dd_statements)
    except:
        msg = "Failed to call IDCAMS to copy the data set %s" % VSAMname
        module.fail_json(msg=msg)
    
    if copy_vsam_rc == 0:
        copy_rc = True
    
    Datasets.delete(sysin_ds_name)
    Datasets.delete(sysprint_ds_name)
    return copy_rc 

def size_of_ps(ds_name):
    ds = ds_name.rsplit('.',1)[0]
    output = Datasets.list("%s.*" % ds, verbose=True).split('\n')
    for item in output:
        if item.find(ds_name) != -1:
            size = re.sub(r"\s{2,}", " ", item)
            rba = size.split(' ')[-2]   
    return rba

def _determine_data_set_type(ds_name):
    rc, out, err = module.run_command("tsocmd \"LISTDS '{}'\"".format(ds_name))
    if "NOT IN CATALOG" in out:
        raise UncatalogedDatasetError(ds_name)
    if "INVALID DATA SET NAME" in out:
        return 'USS'
    
    if rc != 0:
        msg = None
        if "ALREADY IN USE" in out:
            msg = "Dataset {} may already be open by another user. Close the dataset and try again.".format(ds_name)
        else:
            msg = "Unable to determine data set type for data set {}.".format(ds_name)
        module.fail_json(msg=msg, rc=rc, stdout=out, stderr=err)
    
    ds_search = re.search("(-|--)DSORG(|-)\n(.*)", out)
    if ds_search:
        return ds_search.group(3).split()[-1].strip()
    return None

def _recatalog_data_set(ds_name, volume):
    """ Recatalog an uncataloged data set """
    sysin_ds_name = _create_temp_data_set_name('SYSIN')
    Datasets.create(sysin_ds_name, 'SEQ')
    idcams_sysin = ''' DEFINE NVSAM -
        (NAME({}) -
        VOLUMES({}) - 
        DEVT(SYSDA)) '''.format(ds_name, volume)

    Datasets.write(sysin_ds_name, idcams_sysin)
    dd_statements = []
    dd_statements.append(types.DDStatement(ddName="sysin", dataset=sysin_ds_name))
    dd_statements.append(types.DDStatement(ddName="sysprint", dataset='*'))

    try:
        rc = MVSCmd.execute_authorized(pgm="idcams", args='', dds=dd_statements)
        if rc != 0:
            module.fail_json(msg="Non-zero return code received while executing MVSCmd to recatalog {}".format(ds_name), rc=rc)
    
    except Exception as err:
        module.fail_json(msg="Failed to call IDCAMS to recatalog data set {}: {}".format(ds_name, str(err)))
    
    finally:
        Datasets.delete(sysin_ds_name) 

    return ds_name

def _get_checksum(data):
    """ Calculate checksum for the given data """
    digest = hashlib.sha1()
    data = to_bytes(data, errors='surrogate_or_strict')
    digest.update(data)
    return digest.hexdigest()

def _get_mvs_checksum(ds_name):
    return _get_checksum(Datasets.read(ds_name))

def _copy_to_ps(src, dest, data, validate=True, local_checksum=None):
    rc = Datasets.write(dest, ascii_to_ebcdic(src, data))
    if rc != 0:
        module.fail_json(msg="Unable to write content to destination {}".format(dest))
    if validate:
        remote_checksum = _get_mvs_checksum(dest)
        new_checksum = _get_mvs_checksum(dest)
        if remote_checksum != new_checksum:
            changed = True
        elif new_checksum != local_checksum:
            module.fail_json(msg="Checksum mismatch", checksum=new_checksum, local_checksum=local_checksum, changed=changed)

def main():
    global module

    module = AnsibleModule(
        argument_spec          = dict(
            src                = dict(required=True, type='path'),
            dest               = dict(required=True, type='path'),
            is_uss             = dict(type='bool', default=False), 
            is_vsam            = dict(type='bool', default=False),
            use_qualifier      = dict(type='bool', default=False), 
            is_binary          = dict(type='bool', default=False),
            is_catalog         = dict(type='bool', default=True), 
            volume             = dict(type='str'),
            encoding           = dict(type='str', default='EBCDIC',choices=['EBCDIC','ASCII']),
            content            = dict(type='str', no_log=True),
            backup             = dict(type='bool', default=False),
            force              = dict(type='bool', default=True),
            validate           = dict(type='bool', default=False),
            remote_src         = dict(type='bool', default=False),
            checksum           = dict(type='str'),
            wait_s             = dict(type='int', default=10),
            _local_data        = dict(type='str'),
            _size              = dict(type='int'),
            _local_checksum    = dict(type='str')
        )
    )

    src                = module.params['src']
    b_src              = to_bytes(src, errors='surrogate_or_strict')
    dest               = module.params['dest']
    b_dest             = to_bytes(dest, errors='surrogate_or_strict')
    is_uss             = module.params['is_uss']
    remote_src         = module.params['remote_src']
    is_vsam            = module.params['is_vsam']
    use_qualifier      = module.params['use_qualifier']
    is_binary          = module.params['is_binary']
    is_catalog         = module.params['is_catalog']
    volume             = module.params['volume']
    encoding           = module.params['encoding']
    content            = module.params['content']
    validate           = module.params['validate']
    wait_s             = module.params['wait_s']
    _local_checksum    = module.params['_local_checksum']
    ds_name            = ''
    size               = ''

    check_rc           = False
    copy_rc            = False
    changed            = False


    if remote_src:
        if not os.path.exists(b_src):
            module.fail_json(msg="Source {} does not exist".format(src))
        if not os.access(b_src, os.R_OK):
            module.fail_json(msg="Source {} not readable".format(src))

    try:
        ds_type = _determine_data_set_type(dest)
    except UncatalogedDatasetError as err:
        if not is_catalog:
            _recatalog_data_set(dest)
            time.sleep(wait_s)
            ds_type = _determine_data_set_type(dest)
        else:
            rc = Datasets.create(dest, "SEQ", size, "FB")
            if rc != 0:
                module.fail_json("Unable to allocate data set to copy {}".format(src))
    
    # Copy to sequential data set
    if ds_type == 'PS':
        _copy_to_ps(src, dest, module.params['_local_data'], module.params['_local_checksum'])

    # Copy to partitioned data set
    elif ds_type in ('PO', 'PDSE', 'PE'):
        pass
        #_copy_to_pdse()

    remote_checksum = None
    new_checksum = None

    res_args = dict(
        src=src, 
        dest=dest, 
        changed=changed, 
        checksum=_get_mvs_checksum(dest), 
        size="{} Bytes".format(module.params['_size'])
    )
    module.exit_json(**res_args)

class AnsibleModuleError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class UncatalogedDatasetError(Exception):
    def __init__(self, ds_name):
        super().__init__("Data set {} is not in catalog. If you would like to copy to the data set, please specify its volume".format(ds_name))

if __name__ == '__main__':
    main()
