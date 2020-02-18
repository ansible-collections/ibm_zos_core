# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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
  - Luke Zhao <zlbjlu@cn.ibm.com>
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
