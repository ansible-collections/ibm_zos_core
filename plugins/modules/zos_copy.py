# -*- coding: utf-8 -*-

# Copyright: (c) 2015, Jon Hawkesworth (@jhawkesworth) <figs@unity.demon.co.uk>
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: zos_copy
version_added: '0.0.3'
short_description: Copy a data set from local or remote machine to remote machine.
description:
    - The C(zos_copy) module copies a USS file or a data set from the local or 
      remote machine to a location on the remote machine.
    - Use the M(zos_fetch) module to copy files or data sets from remote locations
      to local machine.
options:
  src:
    description:
    - Local path to a file to copy to the remote z/OS system; can be absolute or
      relative.
    - If I(remote_src=true), name of the file, data set or data set member 
      on remote z/OS system.
    - If path is a directory and the destination is a PDS(E), all the files in it 
      would to be copied to a PDS(E).
    - If path is a directory, it is copied (including the source folder name)
      recursively to C(dest).
    - If path is a directory and ends with "/", only the inside contents of
      that directory are copied to the destination. Otherwise, if it does not
      end with "/", the directory itself with all contents is copied.
    - If path is a file and dest ends with "/", the file is copied to the
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
    - If C(dest) is a PDS, PDS(E) or VSAM, the copy module will only copy into 
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
notes:
- Currently zos_copy does not support copying symbolic links from both local to
  remote and remote to remote.
author:
  - Asif Mahmud <asif.mahmud@ibm.com>
  - Luke Zhao
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

- name: Copy a PDS(E) on remote system to an existing PDS(E) replacing the original
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.six import PY3

from zoautil_py import MVSCmd, Datasets
from zoautil_py.types import DDStatement

# The AnsibleModule object
module = None

def ascii_to_ebcdic(src, dest):
    tempf = tempfile.NamedTemporaryFile().name
    b_tempf = to_bytes(tempf, errors='surrogate_or_strict')
    with open(b_tempf, 'w+b') as ftemp:
        request = subprocess.Popen(['iconv', '-f', 'ISO8859-1', '-t', 'IBM-1047', src], stdout=ftemp)
        stdout = request.communicate()
        request = subprocess.Popen(['mv', b_tempf, dest], stdout=subprocess.PIPE)
        stdout += request.communicate()
    return stdout


def create_temp_ds_name(LLQ):
    """ Allocate data sets: sysin and sysprint for IDCAMS """
    temp_ds_hlq  = Datasets.hlq()
    current_date  = time.strftime("D%y%m%d", time.localtime())
    current_time  = time.strftime("T%H%M%S", time.localtime())
    temp_data_set = temp_ds_hlq + '.' + current_date + '.' + current_time + '.' + LLQ
    
    return temp_data_set


def vsam_exists_or_not(DSname):
    """ Check vsam data set using ZOAU API """
    check_rc      = False
    check_vsam_rc = -1
    sysin_ds_name = create_temp_ds_name('sysin')
    sysprint_ds_name = create_temp_ds_name('sysprint')

    Datasets.create(sysin_ds_name, "SEQ")
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)

    listcat_sysin = ' LISTCAT ENT(' + DSname + ') ALL'
    Datasets.write(sysin_ds_name, listcat_sysin)
    dd_statements = []
    dd_statements.append(DDStatement(ddName="sysin", dataset=sysin_ds_name))
    dd_statements.append(DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
    try:
        check_vsam_rc = MVSCmd.execute_authorized(pgm="idcams", args="", dds=dd_statements)
    except:
        msg = "Failed to call IDCAMS to check the data set %s" % Dsname
        module.fail_json(msg=msg)
    
    if check_vsam_rc == 0:
        check_rc   = True
        output     = Datasets.read(sysprint_ds_name)
        findReclen = re.findall(r'MAXLRECL-*\d+', output)
        findHiurba = re.findall(r'HI-U-RBA-*\d+', output)
        reclen     = ''.join(re.findall(r'\d+', findReclen[0]))
        hiurba     = ''.join(re.findall(r'\d+', findHiurba[0]))
    else:
        msg = "Failed to call IDCAMS to check the data set %s" % Dsname
        module.fail_json(msg=msg)
    
    Datasets.delete(sysin_ds_name)
    Datasets.delete(sysprint_ds_name)

    return check_rc, reclen, hiurba


def data_set_exists_or_not(DSname):
    """ check non-vsam data set exist or not  """
    check_rc = False
    try:
        check_rc = Datasets.exists(DSname)
    except:
        print('')
    return check_rc


def uncatalog_data_set_exists_or_not(Dsname, volume):
    """ check uncataloged data set exist or not """
    check_rc = False
    sysprint_ds_name = create_temp_ds_name('sysprint')
    sysin_ds_name = create_temp_ds_name('sysin')
    
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)
    Datasets.create(sysin_ds_name, "SEQ")
    
    adrdssu_sysin = ''' DUMP DATASET(INCLUDE( %s ) - 
       BY((CATLG,EQ,NO)))   - 
       SHR OUTDD(LIST)      - 
       LOGINDYNAM((%s)) ''' % (Dsname, volume)
    
    Datasets.write(sysin_ds_name, adrdssu_sysin)
    dd_statements = []
    dd_statements.append(DDStatement(ddName="list", dataset="dummy"))
    dd_statements.append(DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
    dd_statements.append(DDStatement(ddName="sysin", dataset=sysin_ds_name))
    try:
        check_uc_rc = MVSCmd.execute_authorized(pgm="adrdssu", args="TYPRUN=NORUN", dds=dd_statements)
    except:
        msg = "Failed to call ADRDSSU to check the data set %s" % Dsname
        module.fail_json(msg=msg)

    if Datasets.read(sysprint_ds_name).find(Dsname) != -1:
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
    sysin_ds_name = create_temp_ds_name('sysin')
    sysprint_ds_name = create_temp_ds_name('sysprint')

    Datasets.create(sysin_ds_name, "SEQ")
    Datasets.create(sysprint_ds_name, "SEQ", "", "FB", "",133)

    repro_sysin = ' REPRO INFILE(INPUT) OUTFILE(OUTPUT) '
    Datasets.write(sysin_ds_name, repro_sysin)
    
    dd_statements = []
    dd_statements.append(DDStatement(ddName="sysin", dataset=sysin_ds_name))
    dd_statements.append(DDStatement(ddName="input", dataset=src))
    dd_statements.append(DDStatement(ddName="output", dataset=VSAMname))
    dd_statements.append(DDStatement(ddName="sysprint", dataset=sysprint_ds_name))
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

def size_of_ps(Dsname):
    ds = Dsname.rsplit('.',1)[0]
    output = Datasets.list("%s.*" % ds, verbose=True).split('\n')
    for item in output:
        if item.find(Dsname) != -1:
            size = re.sub(r"\s{2,}", " ", item)
            rba = size.split(' ')[-2]   
    return rba

def main():

    global module

    module = AnsibleModule(
        argument_spec          = dict(
            src                = dict(type='path'),
            dest               = dict(type='str'),
            basename           = dict(type='str'),
            isUSS              = dict(type='bool', default=False), 
            isVSAM             = dict(type='bool', default=False),
            useQualifier       = dict(type='bool', default=True), 
            isBinary           = dict(type='bool', default=False),
            isCatalog          = dict(type='bool', default=True), 
            volume             = dict(type='str', default=''),
            encoding           = dict(type='str', default='EBCDIC',choices=['EBCDIC','ASCII']),
        ),
        add_file_common_args   = True,
        supports_check_mode    = True,
    )

    src                = module.params['src']
    b_src              = to_bytes(src, errors='surrogate_or_strict')
    dest               = module.params['dest']
    b_dest             = to_bytes(dest, errors='surrogate_or_strict')
    isUSS              = module.params['isUSS']
    mode               = module.params['mode']
    owner              = module.params['owner']
    group              = module.params['group']
    remote_src         = module.params['remote_src']
    isVSAM             = module.params['isVSAM']
    useQualifier       = module.params['useQualifier']
    isBinary           = module.params['isBinary']
    isCatalog          = module.params['isCatalog']
    volume             = module.params['volume']
    encoding           = module.params['encoding']
    basename           = module.params['basename']
    dsname             = ''
    size               = ''

    check_rc           = False
    copy_rc            = False
    changed            = False

    if not os.path.exists(b_src):
        module.fail_json(msg="Source %s not found" % (src))
    if not os.access(b_src, os.R_OK):
        module.fail_json(msg="Source %s not readable" % (src))

    if os.path.isdir(b_src):
        dest = os.path.join(src, basename)
        b_src = to_bytes(dest, errors='surrogate_or_strict')

    if isUSS:
        ascii_to_ebcdic(b_src, b_src)
        response = dict(dest=dest, changed=changed, mode=mode)
        module.exit_json(meta=response)
    else:
        #ascii_to_ebcdic(b_src, b_src)
        if useQualifier:
            hlq = Datasets.hlq()
            dsname = hlq + '.' + dest.upper()
    
    # Based on the parameter isCatalog is on or not, to check the data set exists or not.
    # For uncataloged data set, the parameter volume is required.
    # For VSAM data set(KSDS), it must be cataloged.
    if isCatalog:
        check_rc = data_set_exists_or_not(dsname)
        if isVSAM:
            check_rc, reclen, hiurba = vsam_exists_or_not(dsname.upper())
    else:
        if volume == "":
            msg = "Please specify the volume for the UNCATALOGED dataset: %s." % dsname
            module.fail_json(msg=msg, dest=dsname)
        else:
            check_rc = uncatalog_data_set_exists_or_not(dsname, volume.upper())
    
    # Based on the check result, continue the copy 
    # For VSAM data set, two steps is required to finish the copy:
    #   1) create a temp ps, and copy to this temp ps first
    #   2) copy the temp ps to the target VSAM data set
    
    if check_rc:
        if isVSAM:
            tempPS = create_temp_ds_name('tempps')
            Datasets.create(tempPS, "SEQ", "", "FB", "", int(reclen))
            copy_to_ps(b_src, tempPS, encoding)
            copy_rc = copy_to_vsam(tempPS, dsname)
            Datasets.delete(tempPS)
            if copy_rc: 
                #check_rc = vsam_exists_or_not(dsname)
                check_rc, reclen, size = vsam_exists_or_not(dsname)
        else:
            copy_rc = copy_to_ps(b_src, dsname, encoding)
            if copy_rc:
                size = size_of_ps(dsname)
    else:
        msg = dsname + " does not exist."
        module.fail_json(msg=msg)
    
   
    if copy_rc:
        msg = "Data in %s has been successfully copied into %s" % (b_src, dsname)
        changed = True
        res_args['dest']    = dsname 
        res_args['changed'] = changed
        res_args['size']    = size

        module.exit_json(**res_args)
    else:
        msg = 'failed'
        res_args = dict(
        dest=dest, changed=changed, msg=msg
        )
        module.fail_json(msg=msg) 

class AnsibleModuleError(Exception):
    def __init__(self, msg):
        super.__init__(msg)

if __name__ == '__main__':
    main()
