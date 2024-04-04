#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019 - 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_copy
version_added: '1.2.0'
short_description: Copy data to z/OS
description:
  - The L(zos_copy,./zos_copy.html) module copies a file or data set from a local or a
    remote machine to a location on the remote machine.
author:
  - "Asif Mahmud (@asifmahmud)"
  - "Demetrios Dimatos (@ddimatos)"
  - "Ivan Moreno (@rexemin)"
options:
  asa_text:
    description:
      - If set to C(true), indicates that either C(src) or C(dest) or both
        contain ASA control characters.
      - When C(src) is a USS file and C(dest) is a data set, the copy will
        preserve ASA control characters in the destination.
      - When C(src) is a data set containing ASA control characters and
        C(dest) is a USS file, the copy will put all control characters as
        plain text in the destination.
      - If C(dest) is a non-existent data set, it will be created with record
        format Fixed Block with ANSI format (FBA).
      - If neither C(src) or C(dest) have record format Fixed Block with ANSI
        format (FBA) or Variable Block with ANSI format (VBA), the module
        will fail.
      - This option is only valid for text files. If C(is_binary) is C(true)
        or C(executable) is C(true) as well, the module will fail.
    type: bool
    default: false
    required: false
  backup:
    description:
      - Specifies whether a backup of the destination should be created before
        copying data.
      - When set to C(true), the module creates a backup file or data set.
      - The backup file name will be returned on either success or failure of
        module execution such that data can be retrieved.
    type: bool
    default: false
    required: false
  backup_name:
    description:
      - Specify a unique USS file name or data set name for the destination backup.
      - If the destination C(dest) is a USS file or path, the C(backup_name) must
        be an absolute path name.
      - If the destination is an MVS data set name, the C(backup_name) provided
        must meet data set naming conventions of one or more qualifiers, each
        from one to eight characters long, that are delimited by periods.
      - If the C(backup_name) is not provided, the default C(backup_name) will
        be used. If the C(dest) is a USS file or USS path, the name of the backup
        file will be the destination file or path name appended with a
        timestamp, e.g. C(/path/file_name.2020-04-23-08-32-29-bak.tar). If the
        C(dest) is an MVS data set, it will be a data set with a randomly generated
        name.
      - If C(dest) is a data set member and C(backup_name) is not provided, the data set
        member will be backed up to the same partitioned data set with a randomly
        generated member name.
    required: false
    type: str
  content:
    description:
      - When used instead of C(src), sets the contents of a file or data set
        directly to the specified value.
      - Works only when C(dest) is a USS file, sequential data set, or a
        partitioned data set member.
      - If C(dest) is a directory, then content will be copied to
        C(/path/to/dest/inline_copy).
    type: str
    required: false
  dest:
    description:
      - The remote absolute path or data set where the content should be copied to.
      - C(dest) can be a USS file, directory or MVS data set name.
      - If C(dest) has missing parent directories, they will be created.
      - If C(dest) is a nonexistent USS file, it will be created.
      - If C(dest) is a new USS file or replacement, the file will be appropriately tagged with
        either the system's default locale or the encoding option defined. If the USS file is
        a replacement, the user must have write authority to the file either through ownership,
        group or other permissions, else the module will fail.
      - If C(dest) is a nonexistent data set, it will be created following the
        process outlined here and in the C(volume) option.
      - If C(dest) is a nonexistent data set, the attributes assigned will depend on the type of
        C(src). If C(src) is a USS file, C(dest) will have a Fixed Block (FB) record format and the
        remaining attributes will be computed. If I(is_binary=true), C(dest) will have a Fixed Block
        (FB) record format with a record length of 80, block size of 32760, and the remaining
        attributes will be computed. If I(executable=true),C(dest) will have an Undefined (U) record
        format with a record length of 0, block size of 32760, and the remaining attributes will be
        computed.
      - When C(dest) is a data set, precedence rules apply. If C(dest_data_set)
        is set, this will take precedence over an existing data set. If C(dest)
        is an empty data set, the empty data set will be written with the
        expectation its attributes satisfy the copy. Lastly, if no precendent
        rule has been exercised, C(dest) will be created with the same attributes
        of C(src).
      - When the C(dest) is an existing VSAM (KSDS) or VSAM (ESDS), then source
        can be an ESDS, a KSDS or an RRDS. The VSAM (KSDS) or VSAM (ESDS) C(dest) will
        be deleted and recreated following the process outlined in the C(volume) option.
      - When the C(dest) is an existing VSAM (RRDS), then the source must be an RRDS.
        The VSAM (RRDS) will be deleted and recreated following the process outlined
       in the C(volume) option.
      - When C(dest) is and existing VSAM (LDS), then source must be an LDS. The
        VSAM (LDS) will be deleted and recreated following the process outlined
        in the C(volume) option.
      - When C(dest) is a data set, you can override storage management rules
        by specifying C(volume) if the storage class being used has
        GUARANTEED_SPACE=YES specified, otherwise, the allocation will
        fail. See C(volume) for more volume related processes.
    type: str
    required: true
  encoding:
    description:
      - Specifies which encodings the destination file or data set should be
        converted from and to.
      - If C(encoding) is not provided, the module determines which local and remote
        charsets to convert the data from and to. Note that this is only done for text
        data and not binary data.
      - Only valid if C(is_binary) is false.
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
        required: false
        type: str
  tmp_hlq:
    description:
      - Override the default high level qualifier (HLQ) for temporary and backup
        datasets.
      - The default HLQ is the Ansible user used to execute the module and if
        that is not available, then the value C(TMPHLQ) is used.
    required: false
    type: str
  force:
    description:
      - If set to C(true) and the remote file or data set C(dest) is empty,
        the C(dest) will be reused.
      - If set to C(true) and the remote file or data set C(dest) is NOT empty,
        the C(dest) will be deleted and recreated with the C(src) data set
        attributes, otherwise it will be recreated with the C(dest) data set
        attributes.
      - To backup data before any deletion, see parameters C(backup) and
        C(backup_name).
      - If set to C(false), the file or data set will only be copied if the
        destination does not exist.
      - If set to C(false) and destination exists, the module exits with a note to
        the user.
    type: bool
    default: false
    required: false
  force_lock:
    description:
      - By default, when C(dest) is a MVS data set and is being used by another
        process with DISP=SHR or DISP=OLD the module will fail. Use C(force_lock)
        to bypass this check and continue with copy.
      - If set to C(true) and destination is a MVS data set opened by another
        process then zos_copy will try to copy using DISP=SHR.
      - Using C(force_lock) uses operations that are subject to race conditions
        and can lead to data loss, use with caution.
      - If a data set member has aliases, and is not a program
        object, copying that member to a dataset that is in use will result in
        the aliases not being preserved in the target dataset. When this scenario
        occurs the module will fail.
    type: bool
    default: false
    required: false
  ignore_sftp_stderr:
    description:
      - During data transfer through SFTP, the module fails if the SFTP command
        directs any content to stderr. The user is able to override this
        behavior by setting this parameter to C(true). By doing so, the module
        would essentially ignore the stderr stream produced by SFTP and continue
        execution.
      - When Ansible verbosity is set to greater than 3, either through the
        command line interface (CLI) using B(-vvvv) or through environment
        variables such as B(verbosity = 4), then this parameter will
        automatically be set to C(true).
    type: bool
    required: false
    default: false
    version_added: "1.4.0"
  is_binary:
    description:
      - If set to C(true), indicates that the file or data set to be copied is a
        binary file or data set.
      - When I(is_binary=true), no encoding conversion is applied to the content,
        all content transferred retains the original state.
      - Use I(is_binary=true) when copying a Database Request Module (DBRM) to
        retain the original state of the serialized SQL statements of a program.
    type: bool
    default: false
    required: false
  executable:
    description:
      - If set to C(true), indicates that the file or library to be copied is an executable.
      - If the C(src) executable has an alias, the alias information is also copied. If the
        C(dest) is Unix, the alias is not visible in Unix, even though the information is there and
        will be visible if copied to a library.
      - If I(executable=true), and C(dest) is a data set, it must be a PDS or PDSE (library).
      - If C(dest) is a nonexistent data set, the library attributes assigned will be
        Undefined (U) record format with a record length of 0, block size of 32760 and the
        remaining attributes will be computed.
      - If C(dest) is a file, execute permission for the user will be added to the file (``u+x``).
    type: bool
    default: false
    required: false
  aliases:
    description:
      - If set to C(true), indicates that any aliases found in the source
        (USS file, USS dir, PDS/E library or member) are to be preserved during the copy operation.
      - Aliases are implicitly preserved when libraries are copied over to USS destinations.
        That is, when C(executable=True) and C(dest) is a USS file or directory, this option will be ignored.
      - Copying of aliases for text-based data sets from USS sources or to USS destinations is not currently supported.
    type: bool
    default: false
    required: false
  local_follow:
    description:
      - This flag indicates that any existing filesystem links in the source tree
        should be followed.
    type: bool
    default: true
    required: false
  group:
    description:
      - Name of the group that will own the file system objects.
      - When left unspecified, it uses the current group of the current user
        unless you are root, in which case it can preserve the previous
        ownership.
      - This option is only applicable if C(dest) is USS, otherwise ignored.
    type: str
    required: false
  mode:
    description:
      - The permission of the destination file or directory.
      - If C(dest) is USS, this will act as Unix file mode, otherwise ignored.
      - It should be noted that modes are octal numbers.
        The user must either add a leading zero so that Ansible's YAML parser
        knows it is an octal number (like C(0644) or C(01777))or quote it
        (like C('644') or C('1777')) so Ansible receives a string and can do its
        own conversion from string into number. Giving Ansible a number without
        following one of these rules will end up with a decimal number which
        will have unexpected results.
      - The mode may also be specified as a symbolic mode
        (for example, ``u+rwx`` or ``u=rw,g=r,o=r``) or a special
        string `preserve`.
      - I(mode=preserve) means that the file will be given the same permissions as
        the source file.
    type: str
    required: false
  owner:
    description:
      - Name of the user that should own the filesystem object, as would be
        passed to the chown command.
      - When left unspecified, it uses the current user unless you are root,
        in which case it can preserve the previous ownership.
      - This option is only applicable if C(dest) is USS, otherwise ignored.
    type: str
    required: false
  remote_src:
    description:
      - If set to C(false), the module searches for C(src) at the local machine.
      - If set to C(true), the module goes to the remote/target machine for C(src).
    type: bool
    default: false
    required: false
  src:
    description:
      - Path to a file/directory or name of a data set to copy to remote
        z/OS system.
      - If C(remote_src) is true, then C(src) must be the path to a Unix
        System Services (USS) file, name of a data set, or data set member.
      - If C(src) is a local path or a USS path, it can be absolute or relative.
      - If C(src) is a directory, C(dest) must be a partitioned data set or
        a USS directory.
      - If C(src) is a file and C(dest) ends with "/" or is a
        directory, the file is copied to the directory with the same filename as
        C(src).
      - If C(src) is a directory and ends with "/", the contents of it will be copied
        into the root of C(dest). If it doesn't end with "/", the directory itself
        will be copied.
      - If C(src) is a directory or a file, file names will be truncated and/or modified
        to ensure a valid name for a data set or member.
      - If C(src) is a VSAM data set, C(dest) must also be a VSAM.
      - Wildcards can be used to copy multiple PDS/PDSE members to another
        PDS/PDSE.
      - Required unless using C(content).
    type: str
  validate:
    description:
      - Specifies whether to perform checksum validation for source and
        destination files.
      - Valid only for USS destination, otherwise ignored.
    type: bool
    required: false
    default: false
  volume:
    description:
      - If C(dest) does not exist, specify which volume C(dest) should be
        allocated to.
      - Only valid when the destination is an MVS data set.
      - The volume must already be present on the device.
      - If no volume is specified, storage management rules will be used to
        determine the volume where C(dest) will be allocated.
      - If the storage administrator has specified a system default unit name
        and you do not set a C(volume) name for non-system-managed data sets,
        then the system uses the volumes associated with the default unit name.
        Check with your storage administrator to determine whether a default
        unit name has been specified.
    type: str
    required: false
  dest_data_set:
    description:
      - Data set attributes to customize a C(dest) data set to be copied into.
    required: false
    type: dict
    suboptions:
      type:
        description:
          - Organization of the destination
        type: str
        required: true
        choices:
          - KSDS
          - ESDS
          - RRDS
          - LDS
          - SEQ
          - PDS
          - PDSE
          - MEMBER
          - BASIC
          - LIBRARY
      space_primary:
        description:
          - If the destination I(dest) data set does not exist , this sets the
            primary space allocated for the data set.
          - The unit of space used is set using I(space_type).
        type: int
        required: false
      space_secondary:
        description:
          - If the destination I(dest) data set does not exist , this sets the
            secondary space allocated for the data set.
          - The unit of space used is set using I(space_type).
        type: int
        required: false
      space_type:
        description:
          - If the destination data set does not exist, this sets the unit of
            measurement to use when defining primary and secondary space.
          - Valid units of size are C(K), C(M), C(G), C(CYL), and C(TRK).
        type: str
        choices:
          - K
          - M
          - G
          - CYL
          - TRK
        required: false
      record_format:
        description:
          - If the destination data set does not exist, this sets the format of the
            data set. (e.g C(FB))
          - Choices are case-insensitive.
        required: false
        choices:
          - FB
          - VB
          - FBA
          - VBA
          - U
        type: str
      record_length:
        description:
          - The length of each record in the data set, in bytes.
          - For variable data sets, the length must include the 4-byte prefix area.
          - "Defaults vary depending on format: If FB/FBA 80, if VB/VBA 137, if U 0."
        type: int
        required: false
      block_size:
        description:
          - The block size to use for the data set.
        type: int
        required: false
      directory_blocks:
        description:
          - The number of directory blocks to allocate to the data set.
        type: int
        required: false
      key_offset:
        description:
          - The key offset to use when creating a KSDS data set.
          - I(key_offset) is required when I(type=KSDS).
          - I(key_offset) should only be provided when I(type=KSDS)
        type: int
        required: false
      key_length:
        description:
          - The key length to use when creating a KSDS data set.
          - I(key_length) is required when I(type=KSDS).
          - I(key_length) should only be provided when I(type=KSDS)
        type: int
        required: false
      sms_storage_class:
        description:
          - The storage class for an SMS-managed dataset.
          - Required for SMS-managed datasets that do not match an SMS-rule.
          - Not valid for datasets that are not SMS-managed.
          - Note that all non-linear VSAM datasets are SMS-managed.
        type: str
        required: false
      sms_data_class:
        description:
          - The data class for an SMS-managed dataset.
          - Optional for SMS-managed datasets that do not match an SMS-rule.
          - Not valid for datasets that are not SMS-managed.
          - Note that all non-linear VSAM datasets are SMS-managed.
        type: str
        required: false
      sms_management_class:
        description:
          - The management class for an SMS-managed dataset.
          - Optional for SMS-managed datasets that do not match an SMS-rule.
          - Not valid for datasets that are not SMS-managed.
          - Note that all non-linear VSAM datasets are SMS-managed.
        type: str
        required: false

extends_documentation_fragment:
  - ibm.ibm_zos_core.template

notes:
    - Destination data sets are assumed to be in catalog. When trying to copy
      to an uncataloged data set, the module assumes that the data set does
      not exist and will create it.
    - Destination will be backed up if either C(backup) is C(true) or
      C(backup_name) is provided. If C(backup) is C(false) but C(backup_name)
      is provided, task will fail.
    - When copying local files or directories, temporary storage will be used
      on the remote z/OS system. The size of the temporary storage will
      correspond to the size of the file or directory being copied. Temporary
      files will always be deleted, regardless of success or failure of the
      copy task.
    - VSAM data sets can only be copied to other VSAM data sets.
    - For supported character sets used to encode data, refer to the
      L(documentation,https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html).
    - This module uses SFTP (Secure File Transfer Protocol) for the underlying
      transfer protocol; SCP (secure copy protocol) and Co:Z SFTP are not supported. In the
      case of Co:z SFTP, you can exempt the Ansible user id on z/OS from using Co:Z thus falling
      back to using standard SFTP. If the module detects SCP, it will temporarily use SFTP for
      transfers, if not available, the module will fail.
    - Beginning in version 1.8.x, zos_copy will no longer attempt to correct a copy of
      a data type member into a PDSE that contains program objects. You can control this
      behavior using module option C(executable) that will signify an executable is being
      copied into a PDSE with other executables. Mixing data type members with program
      objects will result in a (FSUM8976,./zos_copy.html) error.
seealso:
- module: zos_fetch
- module: zos_data_set
"""

EXAMPLES = r"""
- name: Copy a local file to a sequential data set
  zos_copy:
    src: /path/to/sample_seq_data_set
    dest: SAMPLE.SEQ.DATA.SET

- name: Copy a local file to a USS location and validate checksum
  zos_copy:
    src: /path/to/test.log
    dest: /tmp/test.log
    validate: true

- name: Copy a local ASCII encoded file and convert to IBM-1047
  zos_copy:
    src: /path/to/file.txt
    dest: /tmp/file.txt

- name: Copy a local directory to a PDSE
  zos_copy:
    src: /path/to/local/dir/
    dest: HLQ.DEST.PDSE

- name: Copy file with permission details
  zos_copy:
    src: /path/to/foo.conf
    dest: /etc/foo.conf
    mode: 0644
    group: foo
    owner: bar

- name: Module will follow the symbolic link specified in src
  zos_copy:
    src: /path/to/link
    dest: /path/to/uss/location
    local_follow: true

- name: Copy a local file to a PDS member and convert encoding
  zos_copy:
    src: /path/to/local/file
    dest: HLQ.SAMPLE.PDSE(MEMBER)
    encoding:
      from: UTF-8
      to: IBM-037

- name: Copy a VSAM  (KSDS) to a VSAM  (KSDS)
  zos_copy:
    src: SAMPLE.SRC.VSAM
    dest: SAMPLE.DEST.VSAM
    remote_src: true

- name: Copy inline content to a sequential dataset and replace existing data
  zos_copy:
    content: 'Inline content to be copied'
    dest: SAMPLE.SEQ.DATA.SET

- name: Copy a USS file to sequential data set and convert encoding beforehand
  zos_copy:
    src: /path/to/remote/uss/file
    dest: SAMPLE.SEQ.DATA.SET
    remote_src: true

- name: Copy a USS directory to another USS directory
  zos_copy:
    src: /path/to/uss/dir
    dest: /path/to/dest/dir
    remote_src: true

- name: Copy a local binary file to a PDSE member
  zos_copy:
    src: /path/to/binary/file
    dest: HLQ.SAMPLE.PDSE(MEMBER)
    is_binary: true

- name: Copy a sequential data set to a PDS member
  zos_copy:
    src: SAMPLE.SEQ.DATA.SET
    dest: HLQ.SAMPLE.PDSE(MEMBER)
    remote_src: true

- name: Copy a local file and take a backup of the existing file
  zos_copy:
    src: /path/to/local/file
    dest: /path/to/dest
    backup: true
    backup_name: /tmp/local_file_backup

- name: Copy a PDS on remote system to a new PDS
  zos_copy:
    src: HLQ.SRC.PDS
    dest: HLQ.NEW.PDS
    remote_src: true

- name: Copy a PDS on remote system to a PDS, replacing the original
  zos_copy:
    src: HLQ.SAMPLE.PDSE
    dest: HLQ.EXISTING.PDSE
    remote_src: true
    force: true

- name: Copy PDS member to a new PDS member. Replace if it already exists
  zos_copy:
    src: HLQ.SAMPLE.PDSE(SRCMEM)
    dest: HLQ.NEW.PDSE(DESTMEM)
    remote_src: true
    force: true

- name: Copy a USS file to a PDSE member. If PDSE does not exist, allocate it
  zos_copy:
    src: /path/to/uss/src
    dest: DEST.PDSE.DATA.SET(MEMBER)
    remote_src: true

- name: Copy a sequential data set to a USS file
  zos_copy:
    src: SRC.SEQ.DATA.SET
    dest: /tmp/
    remote_src: true

- name: Copy a PDSE member to USS file
  zos_copy:
    src: SRC.PDSE(MEMBER)
    dest: /tmp/member
    remote_src: true

- name: Copy a PDS to a USS directory (/tmp/SRC.PDS)
  zos_copy:
    src: SRC.PDS
    dest: /tmp
    remote_src: true

- name: Copy all members inside a PDS to another PDS
  zos_copy:
    src: SOME.SRC.PDS(*)
    dest: SOME.DEST.PDS
    remote_src: true

- name: Copy all members starting with 'ABC' inside a PDS to another PDS
  zos_copy:
    src: SOME.SRC.PDS(ABC*)
    dest: SOME.DEST.PDS
    remote_src: true

- name: Allocate destination in a specific volume
  zos_copy:
    src: SOME.SRC.PDS
    dest: SOME.DEST.PDS
    volume: 'VOL033'
    remote_src: true

- name: Copy a USS file to a fully customized sequential data set
  zos_copy:
    src: /path/to/uss/src
    dest: SOME.SEQ.DEST
    remote_src: true
    volume: '222222'
    dest_data_set:
      type: SEQ
      space_primary: 10
      space_secondary: 3
      space_type: K
      record_format: VB
      record_length: 150

- name: Copy a Program Object and its aliases on a remote system to a new PDSE member MYCOBOL
  zos_copy:
    src: HLQ.COBOLSRC.PDSE(TESTPGM)
    dest: HLQ.NEW.PDSE(MYCOBOL)
    remote_src: true
    executable: true
    aliases: true

- name: Copy a Load Library from a USS directory /home/loadlib to a new PDSE
  zos_copy:
    src: '/home/loadlib/'
    dest: HLQ.LOADLIB.NEW
    remote_src: true
    executable: true
    aliases: true

- name: Copy a file with ASA characters to a new sequential data set.
  zos_copy:
    src: ./files/print.txt
    dest: HLQ.PRINT.NEW
    asa_text: true
"""

RETURN = r"""
src:
    description: Source file or data set being copied.
    returned: changed
    type: str
    sample: /path/to/source.log
dest:
    description: Destination file/path or data set name.
    returned: success
    type: str
    sample: SAMPLE.SEQ.DATA.SET
dest_created:
    description: Indicates whether the module created the destination.
    returned: success and if dest was created by the module.
    type: bool
    sample: true
destination_attributes:
    description: Attributes of a dest created by the module.
    returned: success and destination was created by the module.
    type: dict
    contains:
      block_size:
        description:
          Block size of the dataset.
        type: int
        sample: 32760
      record_format:
        description:
          Record format of the dataset.
        type: str
        sample: FB
      record_length:
        description:
          Record length of the dataset.
        type: int
        sample: 45
      space_primary:
        description:
          Allocated primary space for the dataset.
        type: int
        sample: 2
      space_secondary:
        description:
          Allocated secondary space for the dataset.
        type: int
        sample: 1
      space_type:
        description:
          Unit of measurement for space.
        type: str
        sample: K
      type:
        description:
          Type of dataset allocated.
        type: str
        sample: PDSE
    sample:
        {
            "block_size": 32760,
            "record_format": "FB",
            "record_length": 45,
            "space_primary": 2,
            "space_secondary": 1,
            "space_type": "K",
            "type": "PDSE"
        }
checksum:
    description: SHA256 checksum of the file after running zos_copy.
    returned: When ``validate=true`` and if ``dest`` is USS
    type: str
    sample: 8d320d5f68b048fc97559d771ede68b37a71e8374d1d678d96dcfa2b2da7a64e
backup_name:
    description: Name of the backup file or data set that was created.
    returned: if backup=true or backup_name=true
    type: str
    sample: /path/to/file.txt.2015-02-03@04:15~
gid:
    description: Group id of the file, after execution.
    returned: success and if dest is USS
    type: int
    sample: 100
group:
    description: Group of the file, after execution.
    returned: success and if dest is USS
    type: str
    sample: httpd
owner:
    description: Owner of the file, after execution.
    returned: success and if dest is USS
    type: str
    sample: httpd
uid:
    description: Owner id of the file, after execution.
    returned: success and if dest is USS
    type: int
    sample: 100
mode:
    description: Permissions of the target, after execution.
    returned: success and if dest is USS
    type: str
    sample: 0644
size:
    description: Size(in bytes) of the target, after execution.
    returned: success and dest is USS
    type: int
    sample: 1220
state:
    description: State of the target, after execution.
    returned: success and if dest is USS
    type: str
    sample: file
note:
    description: A note to the user after module terminates.
    returned: When ``force=true`` and ``dest`` exists
    type: str
    sample: No data was copied
msg:
    description: Failure message returned by the module.
    returned: failure
    type: str
    sample: Error while gathering data set information
stdout:
    description: The stdout from a USS command or MVS command, if applicable.
    returned: failure
    type: str
    sample: Copying local file /tmp/foo/src to remote path /tmp/foo/dest
stderr:
    description: The stderr of a USS command or MVS command, if applicable.
    returned: failure
    type: str
    sample: No such file or directory "/tmp/foo"
stdout_lines:
    description: List of strings containing individual lines from stdout.
    returned: failure
    type: list
    sample: [u"Copying local file /tmp/foo/src to remote path /tmp/foo/dest.."]
stderr_lines:
    description: List of strings containing individual lines from stderr.
    returned: failure
    type: list
    sample: [u"FileNotFoundError: No such file or directory '/tmp/foo'"]
rc:
    description: The return code of a USS or MVS command, if applicable.
    returned: failure
    type: int
    sample: 8
cmd:
    description: The MVS command issued, if applicable.
    returned: failure
    type: str
    sample: REPRO INDATASET(SAMPLE.DATA.SET) OUTDATASET(SAMPLE.DEST.DATA.SET)
"""


import glob
import math
import os
import shutil
import stat
import tempfile
import traceback
from hashlib import sha256
from re import IGNORECASE

from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import PY3
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    backup, better_arg_parser, copy, data_set, encode, validation)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import \
    AnsibleModuleHelper
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    is_member,
    is_data_set
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import \
    ZOAUImportError
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.mvs_cmd import \
    idcams

if PY3:
    import pathlib
    from re import fullmatch
else:
    from re import match as fullmatch

try:
    from zoautil_py import datasets, opercmd
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())
    opercmd = ZOAUImportError(traceback.format_exc())

try:
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


class CopyHandler(object):
    def __init__(
        self,
        module,
        is_binary=False,
        executable=False,
        aliases=False,
        asa_text=False,
        backup_name=None,
        force_lock=False,
    ):
        """Utility class to handle copying data between two targets

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently
                                      running module

        Keyword Arguments:
            is_binary {bool} -- Whether the file or data set to be copied
                                contains binary data
            executable {bool} -- Whether the file or data set to be copied
                                is executable
            backup_name {str} -- The USS path or data set name of destination
                                 backup
            force_lock {str} -- Whether the dest data set should be copied into
                                using disp=shr when is opened by another
                                process.
        """
        self.module = module
        self.is_binary = is_binary
        self.executable = executable
        self.asa_text = asa_text
        self.aliases = aliases
        self.backup_name = backup_name
        self.force_lock = force_lock

    def run_command(self, cmd, **kwargs):
        """ Wrapper for AnsibleModule.run_command """
        return self.module.run_command(cmd, **kwargs)

    def copy_to_seq(
        self,
        src,
        conv_path,
        dest,
        src_type
    ):
        """Copy source to a sequential data set.

        Raises:
            CopyOperationError -- When copying into the data set fails.

        Arguments:
            src {str} -- Path to USS file or data set name
            conv_path {str} -- Path to the converted source file
            dest {str} -- Name of destination data set
            src_type {str} -- Type of the source
        """
        new_src = conv_path or src
        copy_args = dict()
        copy_args["options"] = ""

        if src_type == 'USS' and self.asa_text:
            response = copy.copy_asa_uss2mvs(new_src, dest)

            if response.rc != 0:
                raise CopyOperationError(
                    msg="Unable to copy source {0} to {1}".format(new_src, dest),
                    rc=response.rc,
                    stdout=response.stdout_response,
                    stderr=response.stderr_response
                )
        else:
            # While ASA files are just text files, we do a binary copy
            # so dcp doesn't introduce any additional blanks or newlines.
            if self.is_binary or self.asa_text:
                copy_args["options"] = "-B"

            if self.force_lock:
                copy_args["options"] += " -f"

            try:
                datasets.copy(new_src, dest, **copy_args)
            except zoau_exceptions.ZOAUException as copy_exception:
                raise CopyOperationError(
                    msg="Unable to copy source {0} to {1}".format(new_src, dest),
                    rc=copy_exception.response.rc,
                    stdout=copy_exception.response.stdout_response,
                    stderr=copy_exception.response.stderr_response
                )

    def copy_to_vsam(self, src, dest):
        """Copy source VSAM to destination VSAM.

        Raises:
            CopyOperationError -- When REPRO fails to copy the data set.

        Arguments:
            src {str} -- The name of the source VSAM
            dest {str} -- The name of the destination VSAM
        """
        out_dsp = "shr" if self.force_lock else "old"
        dds = {"OUT": "{0},{1}".format(dest.upper(), out_dsp)}
        repro_cmd = """  REPRO -
        INDATASET('{0}') -
        OUTFILE(OUT)""".format(src.upper())
        rc, out, err = idcams(repro_cmd, dds=dds, authorized=True)
        if rc != 0:
            raise CopyOperationError(
                msg=("IDCAMS REPRO encountered a problem while "
                     "copying {0} to {1}".format(src, dest)),
                rc=rc,
                stdout=out,
                stderr=err,
                stdout_lines=out.splitlines(),
                stderr_lines=err.splitlines(),
                cmd=repro_cmd,
            )

    def _copy_tree(self, entries, src, dest, dirs_exist_ok=False):
        """Recursively copy USS directory to another USS directory.
        This function was created to circumvent using shutil.copytree
        as it presented the issue of corrupting file contents after second copy
        because the use of shutil.copy2. This issue is only present in
        Python 3.11 and 3.12.

        Arguments:
            entries {list} -- List of files under src directory.
            src_dir {str} -- USS source directory.
            dest_dir {str} -- USS dest directory.
            dirs_exist_ok {bool} -- Whether to copy files to an already existing directory.

        Raises:
            Exception -- When copying into the directory fails.

        Returns:
            {str } -- Destination directory that was copied.
        """
        os.makedirs(dest, exist_ok=dirs_exist_ok)
        for src_entry in entries:
            src_name = os.path.join(validation.validate_safe_path(src), validation.validate_safe_path(src_entry.name))
            dest_name = os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(src_entry.name))
            try:
                if src_entry.is_symlink():
                    link_to = os.readlink(src_name)
                    os.symlink(link_to, dest_name)
                    shutil.copystat(src_name, dest_name, follow_symlinks=True)
                elif src_entry.is_dir():
                    self.copy_tree(src_name, dest_name, dirs_exist_ok=dirs_exist_ok)
                else:
                    opts = dict()
                    opts["options"] = ""

                    try:
                        datasets.copy(src_name, dest_name, **opts)
                    except zoau_exceptions.ZOAUException as copy_exception:
                        raise Exception(copy_exception.response.stderr_response)
                    shutil.copystat(src_name, dest_name, follow_symlinks=True)
            except Exception as err:
                raise err

        return dest

    def copy_tree(self, src_dir, dest_dir, dirs_exist_ok=False):
        """
        Copies a USS directory into another USS directory.

        Arguments:
            src_dir {str} -- USS source directory.
            dest_dir {str} -- USS dest directory.
            dirs_exist_ok {bool} -- Whether to copy files to an already existing directory.

        Returns:
            {str} -- Destination directory that was copied.
        """
        with os.scandir(src_dir) as itr:
            entries = list(itr)
        return self._copy_tree(entries, src_dir, dest_dir, dirs_exist_ok=dirs_exist_ok)

    def convert_encoding(self, src, encoding, remote_src):
        """Convert encoding for given src

        Arguments:
            src {str} -- Path to the USS source file or directory
            encoding {dict} -- Charsets that the source is to be converted
                               from and to
            remote_src {bool} -- Whether the file was already on the remote
                                node or not.

        Raises:
            CopyOperationError -- When the encoding of a USS file is not
                                       able to be converted

        Returns:
            {str} -- The USS path where the converted data is stored
        """
        from_code_set = encoding.get("from")
        to_code_set = encoding.get("to")
        enc_utils = encode.EncodeUtils()
        new_src = src
        if os.path.isdir(new_src):
            try:
                if remote_src:
                    temp_dir = tempfile.mkdtemp()
                    shutil.copytree(new_src, temp_dir, dirs_exist_ok=True)
                    new_src = temp_dir

                self._convert_encoding_dir(new_src, from_code_set, to_code_set)
                self._tag_file_encoding(new_src, to_code_set, is_dir=True)

            except CopyOperationError as err:
                if new_src != src:
                    shutil.rmtree(new_src)
                raise err
            except Exception as err:
                if new_src != src:
                    shutil.rmtree(new_src)
                raise CopyOperationError(msg=str(err))
        else:
            try:
                if remote_src:
                    fd, temp_src = tempfile.mkstemp()
                    os.close(fd)
                    shutil.copy(new_src, temp_src)
                    new_src = temp_src

                rc = enc_utils.uss_convert_encoding(
                    new_src,
                    new_src,
                    from_code_set,
                    to_code_set
                )
                if not rc:
                    raise EncodingConversionError(
                        new_src,
                        from_code_set,
                        to_code_set
                    )
                self._tag_file_encoding(new_src, to_code_set)

            except CopyOperationError as err:
                if new_src != src:
                    os.remove(new_src)
                raise err
            except Exception as err:
                if new_src != src:
                    os.remove(new_src)
                raise CopyOperationError(msg=str(err))
        return new_src

    def _convert_encoding_dir(self, dir_path, from_code_set, to_code_set):
        """Convert encoding for all files inside a given directory

        Arguments:
            dir_path {str} -- Absolute path to the input directory
            from_code_set {str} -- The character set to convert the files from
            to_code_set {str} -- The character set to convert the files to

        Raises
            EncodingConversionError -- When the encoding of a USS file is not
                                       able to be converted
        """
        enc_utils = encode.EncodeUtils()
        for path, dirs, files in os.walk(dir_path):
            for file_path in files:
                full_file_path = os.path.join(validation.validate_safe_path(path), validation.validate_safe_path(file_path))
                rc = enc_utils.uss_convert_encoding(
                    full_file_path, full_file_path, from_code_set, to_code_set
                )
                if not rc:
                    raise EncodingConversionError(
                        full_file_path, from_code_set, to_code_set
                    )

    def _tag_file_encoding(self, file_path, tag, is_dir=False):
        """Tag the file specified by 'file_path' with the given code set.
        If `file_path` is a directory, all of the files and subdirectories will
        be tagged recursively.

        Raises:
            CopyOperationError -- When chtag fails.

        Arguments:
            file_path {str} -- Absolute file path
            tag {str} -- Specifies which code set to tag the file

        Keyword Arguments:
            is_dir {bool} -- Whether 'file_path' specifies a directory.
                             (Default {False})

        """
        tag_cmd = "chtag -{0}c {1} {2}".format(
            "R" if is_dir else "t", tag, file_path)
        rc, out, err = self.run_command(tag_cmd)
        if rc != 0:
            raise CopyOperationError(
                msg="Unable to tag the file {0} to {1}".format(file_path, tag),
                rc=rc,
                stdout=out,
                stderr=err,
                stdout_lines=out.splitlines(),
                stderr_lines=err.splitlines(),
            )

    def _merge_hash(self, *args):
        """Combine multiple dictionaries"""
        result = dict()
        for arg in args:
            result.update(arg)
        return result

    def file_has_crlf_endings(self, src):
        """Reads src as a binary file and checks whether it uses CRLF or LF
        line endings.

        Arguments:
            src {str} -- Path to a USS file

        Returns:
            {bool} -- True if the file uses CRLF endings, False if it uses LF
                      ones.
        """
        # Python has to read the file in binary mode to not mask CRLF
        # endings or enable universal newlines. If we used encoding="cp037",
        # we would get '\n' as the line ending even when the file uses '\r\n'.
        with open(src, "rb") as src_file:
            # Reading the file in 1024-byte chunks.
            content = src_file.read(1024)

            while content:
                # In EBCDIC, \r\n are bytes 0d and 15, respectively.
                if b'\x0d\x15' in content:
                    return True
                content = src_file.read(1024)

        return False

    def create_temp_with_lf_endings(self, src):
        """Creates a temporary file with the same content as src but without
        carriage returns.

        Arguments:
            src {str} -- Path to a USS source file.

        Raises:
            CopyOperationError: If the conversion fails.

        Returns:
            {str} -- Path to the temporary file created.
        """
        try:
            fd, converted_src = tempfile.mkstemp()
            os.close(fd)

            with open(converted_src, "wb") as converted_file:
                with open(src, "rb") as src_file:
                    chunk = src_file.read(1024)
                    # In IBM-037, \r is the byte 0d.
                    converted_file.write(chunk.replace(b'\x0d', b''))

            self._tag_file_encoding(converted_src, "IBM-037")

            return converted_src
        except Exception as err:
            raise CopyOperationError(
                msg="Error while trying to convert EOL sequence for source.",
                stderr=to_native(err)
            )


class USSCopyHandler(CopyHandler):
    def __init__(
        self,
        module,
        is_binary=False,
        executable=False,
        asa_text=False,
        aliases=False,
        common_file_args=None,
        backup_name=None,
    ):
        """Utility class to handle copying files or data sets to USS target

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently
                                      running module

        Keyword Arguments:
            common_file_args {dict} -- mode, group and owner information to be
            applied to destination file.

            is_binary {bool} -- Whether the file to be copied contains binary data
            backup_name {str} -- The USS path or data set name of destination backup
        """
        super().__init__(
            module,
            is_binary=is_binary,
            executable=executable,
            asa_text=asa_text,
            aliases=aliases,
            backup_name=backup_name
        )
        self.common_file_args = common_file_args

    def copy_to_uss(
        self,
        src,
        dest,
        conv_path,
        src_ds_type,
        src_member,
        member_name,
        force,
        content_copy,
    ):
        """Copy a file or data set to a USS location

        Arguments:
            src {str} -- The USS source
            dest {str} -- Destination file or directory on USS
            conv_path {str} -- Path to the converted source file or directory
            src_ds_type {str} -- Type of source
            src_member {bool} -- Whether src is a data set member
            member_name {str} -- The name of the source data set member
            force {bool} -- Whether to copy files to an already existing directory
            content_copy {bool} -- Whether copy is using content option or not.

        Returns:
            {str} -- Destination where the file was copied to
        """
        changed_files = None

        if src_ds_type in data_set.DataSet.MVS_SEQ.union(data_set.DataSet.MVS_PARTITIONED):
            self._mvs_copy_to_uss(
                src, dest, src_ds_type, src_member, member_name=member_name
            )

            if self.executable:
                status = os.stat(dest)
                os.chmod(dest, status.st_mode | stat.S_IEXEC)
        else:
            norm_dest = os.path.normpath(dest)
            dest_parent_dir, tail = os.path.split(norm_dest)
            if PY3:
                path_helper = pathlib.Path(dest_parent_dir)
                if dest_parent_dir != "/" and not path_helper.exists():
                    path_helper.mkdir(parents=True, exist_ok=True)
            else:
                # When using Python 2, instead of using pathlib, we'll use os.makedirs.
                # pathlib is not available in Python 2.
                try:
                    if dest_parent_dir != "/" and not os.path.exists(dest_parent_dir):
                        os.makedirs(dest_parent_dir)
                except os.error as err:
                    # os.makedirs throws an error whether the directories were already
                    # present or their creation failed. There's no exist_ok to tell it
                    # to ignore the first case, so we ignore it manually.
                    if "File exists" not in err:
                        raise CopyOperationError(msg=to_native(err))

            if os.path.isfile(conv_path or src):
                dest = self._copy_to_file(src, dest, content_copy, conv_path)
                changed_files = None
            else:
                dest, changed_files = self._copy_to_dir(src, dest, conv_path, force)

        if self.common_file_args is not None:
            mode = self.common_file_args.get("mode")
            group = self.common_file_args.get("group")
            owner = self.common_file_args.get("owner")
            if mode is not None:
                if not os.path.isdir(dest):
                    self.module.set_mode_if_different(dest, mode, False)
                if changed_files:
                    self.module.set_mode_if_different(dest, mode, False)
                    for filepath in changed_files:
                        self.module.set_mode_if_different(
                            os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(filepath)), mode, False
                        )
            if group is not None:
                self.module.set_group_if_different(dest, group, False)
            if owner is not None:
                self.module.set_owner_if_different(dest, owner, False)
        return dest

    def _copy_to_file(self, src, dest, content_copy, conv_path):
        """Helper function to copy a USS src to USS dest.

        Arguments:
            src {str} -- USS source file path
            dest {str} -- USS dest file path
            content_copy {bool} -- Whether copy is using content option or not.
            conv_path {str} -- Path to the converted source file or directory

        Raises:
            CopyOperationError -- When copying into the file fails.

        Returns:
            {str} -- Destination where the file was copied to
        """
        src_path = os.path.basename(src) if not content_copy else "inline_copy"
        if os.path.isdir(dest):
            dest = os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(src_path))
        new_src = conv_path or src
        try:
            if self.is_binary:
                copy.copy_uss2uss_binary(new_src, dest)
            else:
                opts = dict()
                opts["options"] = ""
                datasets.copy(new_src, dest, **opts)
                shutil.copystat(new_src, dest, follow_symlinks=True)
                # shutil.copy(new_src, dest)
            if self.executable:
                status = os.stat(dest)
                os.chmod(dest, status.st_mode | stat.S_IEXEC)
        except zoau_exceptions.ZOAUException as err:
            raise CopyOperationError(
                msg="Unable to copy file {0} to {1}".format(new_src, dest),
                stderr=err.response.stderr_response,
            )
        except OSError as err:
            raise CopyOperationError(
                msg="Destination {0} is not writable".format(dest),
                stderr=str(err)
            )
        except Exception as err:
            raise CopyOperationError(
                msg="Unable to copy file {0} to {1}".format(new_src, dest),
                stderr=str(err),
            )
        return dest

    def _copy_to_dir(
        self,
        src_dir,
        dest_dir,
        conv_path,
        force
    ):
        """Helper function to copy a USS directory to another USS directory.
        If the path for dest_dir does not end with a trailing slash ("/"),
        the src_dir itself will be copied into the destination.

        Arguments:
            src_dir {str} -- USS source directory
            dest_dir {str} -- USS dest directory
            conv_path {str} -- Path to the converted source directory
            force {bool} -- Whether to copy files to an already existing directory

        Raises:
            CopyOperationError -- When copying into the directory fails.

        Returns:
            {tuple} -- Destination where the directory was copied to, and
                       a list of paths for all subdirectories and files
                       that got copied.
        """
        copy_directory = True if not src_dir.endswith("/") else False
        new_src_dir = conv_path or src_dir
        new_src_dir = os.path.normpath(new_src_dir)
        dest = dest_dir
        changed_files, original_permissions = self._get_changed_files(new_src_dir, dest_dir, copy_directory)

        try:
            if copy_directory:
                dest = os.path.join(validation.validate_safe_path(dest_dir), validation.validate_safe_path(os.path.basename(os.path.normpath(src_dir))))
            # dest = shutil.copytree(new_src_dir, dest, dirs_exist_ok=force)
            dest = self.copy_tree(new_src_dir, dest, dirs_exist_ok=force)

            # Restoring permissions for preexisting files and subdirectories.
            for filepath, permissions in original_permissions:
                mode = "0{0:o}".format(stat.S_IMODE(permissions))
                self.module.set_mode_if_different(os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(filepath)), mode, False)
        except Exception as err:
            raise CopyOperationError(
                msg="Error while copying data to destination directory {0}".format(dest_dir),
                stdout=str(err),
            )
        return dest, changed_files

    def _get_changed_files(self, src, dest, copy_directory):
        """Traverses a source directory and gets all the paths to files and
        subdirectories that got copied into a destination.

        Arguments:
            src (str) -- Path to the directory where files are copied from.
            dest (str) -- Path to the directory where files are copied into.
            copy_directory (bool) -- Whether the src directory itself will be copied
                                     into dest. The src basename will get appended
                                     to filepaths when comparing.


        Returns:
            tuple -- A list of paths for all new subdirectories and files that
                     got copied into dest, and a list of the permissions
                     for the files and directories already present on the
                     destination.
        """
        files_to_copy = self._walk_uss_tree(src)

        # It's not needed to normalize the path because it was already normalized
        # on _copy_to_dir.
        parent_dir = os.path.basename(src) if copy_directory else ''

        files_to_change = []
        existing_files = []
        for relative_path in files_to_copy:
            if os.path.exists(
                os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(parent_dir), validation.validate_safe_path(relative_path))
            ):
                existing_files.append(relative_path)
            else:
                files_to_change.append(relative_path)

        # This change adds to the files_to_change variable any file that accord with
        # a name found in the source copy
        files_to_change.extend(existing_files)
        # Creating tuples with (filename, permissions).
        original_permissions = [
            (filepath, os.stat(
                os.path.join(validation.validate_safe_path(dest), validation.validate_safe_path(parent_dir), validation.validate_safe_path(filepath))
            ).st_mode)
            for filepath in existing_files
        ]

        return files_to_change, original_permissions

    def _walk_uss_tree(self, dir):
        """Walks the tree directory for dir and returns all relative paths
        found.
        Arguments:
            dir (str) -- Path to the directory to traverse.
        Returns:
            list -- List of relative paths to all content inside dir.
        """
        original_working_dir = os.getcwd()
        # The function gets relative paths, so it changes the current working
        # directory to the root of src.
        os.chdir(dir)
        paths = []

        for dirpath, subdirs, files in os.walk(".", True):
            paths += [
                os.path.join(validation.validate_safe_path(dirpath), validation.validate_safe_path(subdir)).replace("./", "")
                for subdir in subdirs
            ]
            paths += [
                os.path.join(validation.validate_safe_path(dirpath), validation.validate_safe_path(filepath)).replace("./", "")
                for filepath in files
            ]

        # Returning the current working directory to what it was before to not
        # interfere with the rest of the module.
        os.chdir(original_working_dir)

        return paths

    def _mvs_copy_to_uss(
        self,
        src,
        dest,
        src_ds_type,
        src_member,
        member_name=None
    ):
        """Helper function to copy an MVS data set src to USS dest.

        Arguments:
            src {str} -- Name of source data set or data set member
            dest {str} -- USS dest file path
            src_ds_type -- Type of source
            src_member {bool} -- Whether src is a data set member

        Raises:
            CopyOperationError -- When copying the data set into USS fails.

        Keyword Arguments:
            member_name {str} -- The name of the source data set member
        """

        if os.path.isdir(dest):
            # If source is a data set member, destination file should have
            # the same name as the member.
            dest = "{0}/{1}".format(dest, member_name or src)

            if src_ds_type in data_set.DataSet.MVS_PARTITIONED and not src_member:
                try:
                    os.mkdir(dest)
                except FileExistsError:
                    pass

        try:
            if src_member or src_ds_type in data_set.DataSet.MVS_SEQ:
                if self.asa_text:
                    response = copy.copy_asa_mvs2uss(src, dest)
                    rc = response.rc
                elif self.executable:
                    try:
                        rc = datasets.copy(src, dest, alias=True, executable=True)
                    except zoau_exceptions.ZOAUException as copy_exception:
                        response = copy_exception.response
                        rc = response.rc
                else:
                    try:
                        rc = datasets.copy(src, dest)
                    except zoau_exceptions.ZOAUException as copy_exception:
                        response = copy_exception.response
                        rc = response.rc

                if rc != 0:
                    raise CopyOperationError(
                        msg="Error while copying source {0} to {1}".format(src, dest),
                        rc=response.rc,
                        stdout=response.stdout_response,
                        stderr=response.stderr_response
                    )
            else:
                if self.executable:
                    try:
                        datasets.copy(src, dest, alias=True, executable=True)
                    except zoau_exceptions.ZOAUException as copy_exception:
                        raise CopyOperationError(
                            msg="Error while copying source {0} to {1}".format(src, dest),
                            rc=copy_exception.response.rc,
                            stdout=copy_exception.response.stdout_response,
                            stderr=copy_exception.response.stderr_response
                        )
                elif self.asa_text:
                    response = copy.copy_asa_pds2uss(src, dest)

                    if response.rc != 0:
                        raise CopyOperationError(
                            msg="Error while copying source {0} to {1}".format(src, dest),
                            rc=response.rc,
                            stdout=response.stdout_response,
                            stderr=response.stderr_response
                        )
                else:
                    copy.copy_pds2uss(
                        src,
                        dest,
                        is_binary=self.is_binary,
                        asa_text=self.asa_text
                    )
        except CopyOperationError as err:
            raise err
        except Exception as err:
            raise CopyOperationError(msg=str(err))


class PDSECopyHandler(CopyHandler):
    def __init__(
        self,
        module,
        is_binary=False,
        executable=False,
        aliases=False,
        asa_text=False,
        backup_name=None,
        force_lock=False,
    ):
        """ Utility class to handle copying to partitioned data sets or
        partitioned data set members.

        Arguments:
            module {AnsibleModule} -- The AnsibleModule object from currently
                                      running module

        Keyword Arguments:
            is_binary {bool} -- Whether the data set to be copied contains
                                binary data
            backup_name {str} -- The USS path or data set name of destination backup
        """
        super().__init__(
            module,
            is_binary=is_binary,
            executable=executable,
            aliases=aliases,
            asa_text=asa_text,
            backup_name=backup_name,
            force_lock=force_lock
        )

    def copy_to_pdse(
        self,
        src,
        conv_path,
        dest,
        src_ds_type,
        src_member=None,
        dest_member=None,
        encoding=None,
    ):
        """Copy source to a PDS/PDSE or PDS/PDSE member.

        Raises:
            CopyOperationError -- When copying into a member fails.

        Arguments:
            src {str} -- Path to USS file/directory or data set name.
            conv_path {str} -- Path to the converted source file/directory.
            dest {str} -- Name of destination data set.
            src_ds_type {str} -- The type of source.
            src_member {bool, optional} -- Member of the source data set to copy.
            dest_member {str, optional} -- Name of destination member in data set.
            encoding {dict, optional} -- Dictionary with encoding options.
        """
        new_src = conv_path or src
        src_members = []
        dest_members = []

        if src_ds_type == "USS":

            if os.path.isfile(new_src):
                path = os.path.dirname(new_src)
                files = [os.path.basename(new_src)]
            else:
                path, dirs, files = next(os.walk(new_src))

            src_members = [
                os.path.normpath("{0}/{1}".format(path, file)) if (self.is_binary or self.executable)
                else normalize_line_endings("{0}/{1}".format(path, file), encoding)
                for file in files
            ]
            dest_members = [
                dest_member if dest_member
                else data_set.DataSet.get_member_name_from_file(file)
                for file in files
            ]

        elif src_ds_type in data_set.DataSet.MVS_SEQ:
            src_members = [new_src]
            dest_members = [dest_member]

        else:
            members = []
            src_data_set_name = data_set.extract_dsname(new_src)

            if src_member:
                members.append(data_set.extract_member_name(new_src))
            else:
                # The 'members' variable below is used to store a list of members in the src PDS/E.
                # Items in the list are passed to the copy_to_member function.
                # Aliases are included in the output by list_members unless the alias option is disabled.
                # The logic for preserving/copying aliases is contained in the copy_to_member function.
                opts = {}
                opts['options'] = '-H '  # mls option to hide aliases
                members = datasets.list_members(new_src, **opts)

            src_members = ["{0}({1})".format(src_data_set_name, member) for member in members]
            dest_members = [
                dest_member if dest_member
                else member
                for member in members
            ]

        existing_members = datasets.list_members(dest)  # fyi - this list includes aliases
        overwritten_members = []
        new_members = []
        bulk_src_members = ""
        result = dict()

        for src_member, destination_member in zip(src_members, dest_members):
            if destination_member in existing_members:
                overwritten_members.append(destination_member)
            else:
                new_members.append(destination_member)
            bulk_src_members += "{0} ".format(src_member)

        # Copy section
        if src_ds_type == "USS" or self.asa_text or len(src_members) == 1:
            """
            USS -> MVS : Was kept on member by member basis bc file names longer than 8
            characters will throw an error when copying to a PDS, because of the member name
            character limit.
            MVS -> MVS (asa only): This has to be copied on member by member basis bc OPUT
            does not allow for bulk member copy or entire PDS to PDS copy.
            """
            for src_member, destination_member in zip(src_members, dest_members):
                result = self.copy_to_member(
                    src_member,
                    "{0}({1})".format(dest, destination_member),
                    src_ds_type
                )
        else:
            """
            MVS -> MVS
            Copies a list of members into a PDS, using this list of members greatly
            enhances performance of datasets_copy.
            """
            result = self.copy_to_member(
                bulk_src_members,
                dest,
                src_ds_type
            )

        if result["rc"] != 0:
            msg = "Unable to copy source {0} to {1}.".format(
                new_src,
                dest
            )
            raise CopyOperationError(
                msg=msg,
                rc=result["rc"],
                stdout=result["out"],
                stderr=result["err"],
                overwritten_members=overwritten_members,
                new_members=new_members
            )

    def copy_to_member(
        self,
        src,
        dest,
        src_type
    ):
        """Copy source to a PDS/PDSE member. The only valid sources are:
            - USS files
            - Sequential data sets
            - PDS/PDSE members

        Arguments:
            src {str} -- Path to USS file or data set name.
            dest {str} -- Name of destination data set
            src_type {str} -- Type of the source.

        Returns:
            dict -- Dictionary containing the return code, stdout, and stderr from
                    the copy command.
        """
        src = src.replace("$", "\\$")
        dest = dest.replace("$", "\\$").upper()
        opts = dict()
        opts["options"] = ""

        if src_type == 'USS' and self.asa_text:
            response = copy.copy_asa_uss2mvs(src, dest)
            rc, out, err = response.rc, response.stdout_response, response.stderr_response
        else:
            # While ASA files are just text files, we do a binary copy
            # so dcp doesn't introduce any additional blanks or newlines.
            if self.is_binary or self.asa_text:
                opts["options"] = "-B"

            if self.force_lock:
                opts["options"] += " -f"

            try:
                rc = datasets.copy(src, dest, alias=self.aliases, executable=self.executable, **opts)
                out = ""
                err = ""
            except zoau_exceptions.ZOAUException as copy_exception:
                rc = copy_exception.response.rc
                out = copy_exception.response.stdout_response
                err = copy_exception.response.stderr_response

        return dict(
            rc=rc,
            out=out,
            err=err
        )


def get_file_record_length(file):
    """Gets the longest line length from a file.

    Arguments:
        file (str) -- Path of the file.

    Returns:
        int -- Length of the longest line in the file.
    """
    max_line_length = 0

    with open(file, "r", encoding="utf-8") as src_file:
        current_line = src_file.readline()

        while current_line:
            line_length = len(current_line.rstrip("\n\r"))

            if line_length > max_line_length:
                max_line_length = line_length

            current_line = src_file.readline()

    if max_line_length == 0:
        max_line_length = 80

    return max_line_length


def dump_data_set_member_to_file(data_set_member, is_binary):
    """Dumps a data set member into a file in USS.

    Arguments:
        data_set_member (str) -- Name of the data set member to dump.
        is_binary (bool) -- Whether the data set member contains binary data.

    Returns:
        str -- Path of the file in USS that contains the dump of the member.

    Raise:
        DataSetMemberAttributeError: When the call to dcp fails.
    """
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)

    copy_args = dict()
    if is_binary:
        copy_args["options"] = "-B"

    response = datasets.copy(data_set_member, temp_path, **copy_args)
    if response != 0:
        raise DataSetMemberAttributeError(data_set_member)

    return temp_path


def get_data_set_attributes(
    name,
    size,
    is_binary,
    asa_text=False,
    record_format=None,
    record_length=None,
    type="SEQ",
    volume=None
):
    """Returns the parameters needed to allocate a new data set by using a mixture
    of default values and user provided ones.

    Binary data sets will always have "VB" and 1028 as their record format and
    record length, respectively. Values provided when calling the function will
    be overwritten in this case.

    The default values for record format and record length are taken from the
    default values that the cp command uses. Primary space is computed based on
    the size provided, and secondary space is 10% of the primary one.

    Block sizes are computed following the recomendations on this documentation
    page: https://www.ibm.com/docs/en/zos/2.4.0?topic=options-block-size-blksize

    Arguments:
        name (str) -- Name of the new sequential data set.
        size (int) -- Number of bytes needed for the new data set.
        is_binary (bool) -- Whether or not the data set will have binary data.
        asa_text (bool) -- Whether the data set will have ASA control characters.
        record_format (str, optional) -- Type of record format.
        record_length (int, optional) -- Record length for the data set.
        type (str, optional) -- Type of the new data set.
        volume (str, optional) -- Volume where the data set should be allocated.

    Returns:
        dict -- Parameters that can be passed into data_set.DataSet.ensure_present
    """
    # Calculating the size needed to allocate.
    space_primary = int(math.ceil((size / 1024)))
    space_primary = space_primary + int(math.ceil(space_primary * 0.05))
    space_secondary = int(math.ceil(space_primary * 0.10))

    # set default value - record_format
    if record_format is None:
        if is_binary:
            record_format = "FB"
        else:
            record_format = "VB"

    # set default value - record_length
    if record_length is None:
        if is_binary:
            record_length = 80
        else:
            record_length = 1028

    # compute block size
    max_block_size = 32760
    if record_format == "FB":
        # Computing the biggest possible block size that doesn't exceed
        # the maximum size allowed.
        block_size = math.floor(max_block_size / record_length) * record_length
    else:
        block_size = max_block_size

    if asa_text:
        record_format = "FBA"
        block_size = 27920

    parms = dict(
        name=name,
        type=type,
        space_primary=space_primary,
        space_secondary=space_secondary,
        record_format=record_format,
        record_length=record_length,
        block_size=block_size,
        space_type="K"
    )

    if volume:
        parms['volumes'] = [volume]

    return parms


def create_seq_dataset_from_file(
    file,
    dest,
    force,
    is_binary,
    asa_text,
    record_length=None,
    volume=None
):
    """Creates a new sequential dataset with attributes suitable to copy the
    contents of a file into it.

    Arguments:
        file (str) -- Path of the source file.
        dest (str) -- Name of the data set.
        force (bool) -- Whether to replace an existing data set.
        is_binary (bool) -- Whether the file has binary data.
        asa_text (bool) -- Whether the file has ASA control characters.
        volume (str, optional) -- Volume where the data set should be.
    """
    src_size = os.stat(file).st_size
    # record_format = record_length = None
    record_format = None
    # When dealing with ASA files, if copying from USS,
    # the record length will need to be adjusted (we know it
    # comes from USS because those flows don't send a
    # value for record_length, while flows from source data
    # sets do).
    adjust_record_format = False

    # When src is a binary file, the module will use default attributes
    # for the data set, such as a record format of "VB".
    if not is_binary:
        record_format = "FB"
        if not record_length:
            record_length = get_file_record_length(file)
            adjust_record_format = True

    if asa_text and adjust_record_format:
        # Adding one byte more to the record length to account for the
        # control character at the start of each line.
        record_length += 1

    dest_params = get_data_set_attributes(
        name=dest,
        size=src_size,
        is_binary=is_binary,
        asa_text=asa_text,
        record_format=record_format,
        record_length=record_length,
        volume=volume
    )

    data_set.DataSet.ensure_present(replace=force, **dest_params)


def backup_data(ds_name, ds_type, backup_name, tmphlq=None):
    """Back up the given data set or file to the location specified by 'backup_name'.
    If 'backup_name' is not specified, then calculate a temporary location
    and copy the file or data set there.
    Arguments:
        ds_name {str} -- Name of the file or data set to be backed up
        ds_type {str} -- Type of the file or data set
        backup_name {str} -- Path to USS location or name of data set
        where data will be backed up
    Returns:
        {str} -- The USS path or data set name where data was backed up
    """
    module = AnsibleModuleHelper(argument_spec={})
    try:
        if ds_type == "USS":
            return backup.uss_file_backup(ds_name, backup_name=backup_name)
        return backup.mvs_file_backup(ds_name, backup_name, tmphlq)
    except Exception as err:
        module.fail_json(
            msg=str(err.msg),
            stdout=err.stdout,
            stderr=err.stderr,
            rc=err.rc
        )


def is_compatible(
    src_type,
    dest_type,
    copy_member,
    src_member,
    is_src_dir,
    is_src_inline,
    executable,
    asa_text,
    src_has_asa_chars,
    dest_has_asa_chars
):
    """Determine whether the src and dest are compatible and src can be
    copied to dest.

    Arguments:
        src_type {str} -- Type of the source (e.g. PDSE, USS).
        dest_type {str} -- Type of destination.
        copy_member {bool} -- Whether dest is a data set member.
        src_member {bool} -- Whether src is a data set member.
        is_src_dir {bool} -- Whether the src is a USS directory.
        is_src_inline {bool} -- Whether the src comes from inline content.
        executable {bool} -- Whether the src is a executable to be copied.
        asa_text {bool} -- Whether the copy operation will handle ASA control characters.
        src_has_asa_chars {bool} -- Whether the src contains ASA control characters.
        dest_has_asa_chars {bool} -- Whether the dest contains ASA control characters.

    Returns:
        {bool} -- Whether src can be copied to dest.
    """

    # ********************************************************************
    # If the destination does not exist, then obviously it will need
    # to be created. As a result, target is compatible.
    # ********************************************************************
    if dest_type is None:
        return True

    # ********************************************************************
    # If source or destination is a sequential data set and executable as true
    # is incompatible to execute the copy.
    # ********************************************************************
    if executable:
        if src_type in data_set.DataSet.MVS_SEQ or dest_type in data_set.DataSet.MVS_SEQ:
            return False

    # ********************************************************************
    # For copy operations involving ASA control characters, at least one
    # of the files/data sets has got to have ASA characters.
    # ********************************************************************
    if asa_text:
        return src_has_asa_chars or dest_has_asa_chars

    # ********************************************************************
    # If source is a sequential data set, then destination must be
    # partitioned data set member, other sequential data sets or USS files.
    # Anything else is incompatible.
    # ********************************************************************
    if src_type in data_set.DataSet.MVS_SEQ:
        return not (
            (dest_type in data_set.DataSet.MVS_PARTITIONED and not copy_member) or dest_type == "VSAM"
        )

    # ********************************************************************
    # If source is a partitioned data set, then we need to determine
    # target compatibility for two different scenarios:
    #   - If the source is a data set member
    #   - If the source is an entire data set
    #
    # In the first case, the possible targets are: USS files, PDS/PDSE
    # members and sequential data sets. Anything else is incompatible.
    #
    # In the second case, the possible targets are USS directories and
    # other PDS/PDSE. Anything else is incompatible.
    # ********************************************************************
    elif src_type in data_set.DataSet.MVS_PARTITIONED:
        if dest_type == "VSAM":
            return False
        if not src_member:
            return not (copy_member or dest_type in data_set.DataSet.MVS_SEQ)
        return True

    # ********************************************************************
    # If source is a USS file, then the destination can be another USS file,
    # a directory, a sequential data set or a partitioned data set member.
    # When using the content option, the destination should specify
    # a member name if copying into a partitioned data set.
    #
    # If source is instead a directory, the destination has to be another
    # directory or a partitioned data set.
    # ********************************************************************
    elif src_type == "USS":
        if dest_type in data_set.DataSet.MVS_SEQ or copy_member:
            return not is_src_dir
        elif dest_type in data_set.DataSet.MVS_PARTITIONED and not copy_member and is_src_inline:
            return False
        elif dest_type in data_set.DataSet.MVS_VSAM:
            return False
        else:
            return True

    # ********************************************************************
    # If source is a VSAM data set, we need to check compatibility between
    # all the different types of VSAMs, following the documentation for the
    # dest parameter.
    # ********************************************************************
    else:
        if (dest_type == "KSDS" or dest_type == "ESDS"):
            return src_type == "ESDS" or src_type == "KSDS" or src_type == "RRDS"
        elif dest_type == "RRDS":
            return src_type == "RRDS"
        elif dest_type == "LDS":
            return src_type == "LDS"
        else:
            return dest_type == "VSAM"


def does_destination_allow_copy(
    src,
    src_type,
    dest,
    dest_exists,
    member_exists,
    dest_type,
    is_uss,
    force,
    volume=None
):
    """Checks whether or not the module can copy into the destination
    specified.

    Arguments:
        src {str} -- Name of the source.
        src_type {bool} -- Type of the source (SEQ/PARTITIONED/VSAM/USS).
        dest {str} -- Name of the destination.
        dest_exists {bool} -- Whether or not the destination exists.
        member_exists {bool} -- Whether or not a member in a partitioned destination exists.
        dest_type {str} -- Type of the destination (SEQ/PARTITIONED/VSAM/USS).
        is_uss {bool} -- Whether or not the destination is inside USS.
        force {bool} -- Whether or not the module can replace existing destinations.
        volume {str, optional} -- Volume where the destination should be.

    Returns:
        bool -- If the module has the permissions needed to create, use or replace
                the destination.
    """
    # If the destination is inside USS and the module doesn't have permission to replace it,
    # it fails.
    if is_uss and dest_exists:
        if src_type == "USS" and os.path.isdir(dest) and os.path.isdir(src) and not force:
            return False
        elif os.path.isfile(dest) and not force:
            return False

    # If the destination is a sequential or VSAM data set and is empty, the module will try to use it,
    # otherwise, force needs to be True to continue and replace it.
    if (dest_type in data_set.DataSet.MVS_SEQ or dest_type in data_set.DataSet.MVS_VSAM) and dest_exists:
        is_dest_empty = data_set.DataSet.is_empty(dest, volume)
        if not (is_dest_empty or force):
            return False

    # When the destination is a partitioned data set, the module will have to be able to replace
    # existing members inside of it, if needed.
    if dest_type in data_set.DataSet.MVS_PARTITIONED and dest_exists and member_exists and not force:
        return False

    return True


def get_file_checksum(src):
    """Calculate SHA256 hash for a given file

    Arguments:
        src {str} -- The absolute path of the file

    Returns:
        str -- The SHA256 hash of the contents of input file
    """
    b_src = to_bytes(src)
    if not os.path.exists(b_src) or os.path.isdir(b_src):
        return None
    blksize = 64 * 1024
    hash_digest = sha256()
    try:
        with open(to_bytes(src, errors="surrogate_or_strict"), "rb") as infile:
            block = infile.read(blksize)
            while block:
                hash_digest.update(block)
                block = infile.read(blksize)
    except Exception:
        raise
    return hash_digest.hexdigest()


def cleanup(src_list):
    """Remove all files or directories listed in src_list. Also perform
    additional cleanup of the /tmp directory.

    Arguments:
        src_list {list} -- A list of file paths
    """
    module = AnsibleModuleHelper(argument_spec={})
    tmp_prefix = tempfile.gettempprefix()
    tmp_dir = os.path.realpath("/" + tmp_prefix)
    dir_list = glob.glob(tmp_dir + "/ansible-zos-copy-payload*")
    conv_list = glob.glob(tmp_dir + "/converted*")
    tmp_list = glob.glob(tmp_dir + "/{0}*".format(tmp_prefix))

    for file in (dir_list + conv_list + tmp_list + src_list):
        try:
            if file and os.path.exists(file):
                if os.path.isfile(file):
                    os.remove(file)
                else:
                    shutil.rmtree(file)
        except OSError as err:
            err = str(err)
            if "Permission denied" not in err:
                module.fail_json(
                    msg="Error during clean up of file {0}".format(file), stderr=err
                )


def is_member_wildcard(src):
    """Determine whether src specifies a data set member wildcard in the
    form 'SOME.DATA.SET(*)' or 'SOME.DATA.SET(ABC*)'

    Arguments:
        src {str} -- The data set name

    Returns:
        re.Match -- If the data set specifies a member wildcard
        None -- If the data set does not specify a member wildcard
    """
    return fullmatch(
        r"^(?:(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})(?:[.]{1})){1,21}[A-Z$#@]{1}[A-Z0-9$#@-]{0,7}\([A-Z$#@\*]{1}[A-Z0-9$#@\*]{0,7}\)$",
        src,
        IGNORECASE,
    )


def get_attributes_of_any_dataset_created(
    dest,
    src_ds_type,
    src,
    src_name,
    is_binary,
    asa_text,
    volume=None
):
    """
    Get the attributes of dataset created by the function allocate_destination_data_set
    except for VSAM.

    Arguments:
        dest (str) -- Name of the destination data set.
        src_ds_type (str) -- Source of the destination data set.
        src (str) -- Name of the source data set, used as a model when appropiate.
        src_name (str) -- Extraction of the source name without the member pattern.
        is_binary (bool) -- Whether the data set will contain binary data.
        asa_text (bool) -- Whether the data set will contain ASA control characters.
        volume (str, optional) -- Volume where the data set should be allocated into.

    Returns:
        params (dict) -- Parameters used for the dataset created as name, type,
        space_primary, space_secondary, record_format, record_length, block_size and space_type
    """
    params = {}
    if src_ds_type == "USS":
        if os.path.isfile(src):
            size = os.stat(src).st_size
            params = get_data_set_attributes(
                dest,
                size=size,
                is_binary=is_binary,
                asa_text=asa_text,
                volume=volume
            )
        else:
            size = os.path.getsize(src)
            params = get_data_set_attributes(
                dest,
                size=size,
                is_binary=is_binary,
                asa_text=asa_text,
                volume=volume
            )
    else:
        src_attributes = datasets.list_datasets(src_name)[0]
        size = int(src_attributes.total_space)
        params = get_data_set_attributes(
            dest,
            size=size,
            is_binary=is_binary,
            asa_text=asa_text,
            volume=volume
        )
    return params


def allocate_destination_data_set(
    src,
    dest,
    src_ds_type,
    dest_ds_type,
    dest_exists,
    force,
    is_binary,
    executable,
    asa_text,
    dest_data_set=None,
    volume=None
):
    """
    Allocates a new destination data set to copy into, erasing a preexistent one if
    needed.

    Arguments:
        src (str) -- Name of the source data set, used as a model when appropiate.
        dest (str) -- Name of the destination data set.
        src_ds_type (str) -- Source of the destination data set.
        dest_ds_type (str) -- Type of the destination data set.
        dest_exists (bool) -- Whether the destination data set already exists.
        force (bool) -- Whether to replace an existent data set.
        is_binary (bool) -- Whether the data set will contain binary data.
        executable (bool) -- Whether the data to copy is an executable dataset or file.
        asa_text (bool) -- Whether the data to copy has ASA control characters.
        dest_data_set (dict, optional) -- Parameters containing a full definition
            of the new data set; they will take precedence over any other allocation logic.
        volume (str, optional) -- Volume where the data set should be allocated into.

    Returns:
        bool -- True if the data set was created, False otherwise.
        dest_params (dict) -- Parameters used for the dataset created as name,
        block_size, record_format, record_length, space_primary, space_secondary,
        space_type, type.
    """
    src_name = data_set.extract_dsname(src)
    is_dest_empty = data_set.DataSet.is_empty(dest) if dest_exists else True

    # Replacing an existing dataset only when it's not empty. We don't know whether that
    # empty dataset was created for the user by an admin/operator, and they don't have permissions
    # to create new datasets.
    # These rules assume that source and destination types are compatible.
    # Create the dict that will contains the values created by the module if it's empty action module will
    # not display the content.
    dest_params = {}
    if dest_exists and is_dest_empty:
        return False, dest_params

    # Giving more priority to the parameters given by the user.
    # Cover case the user set executable to true to create dataset valid.
    if dest_data_set:
        dest_params = dest_data_set
        dest_params["name"] = dest
        data_set.DataSet.ensure_present(replace=force, **dest_params)
    elif dest_ds_type in data_set.DataSet.MVS_SEQ:
        volumes = [volume] if volume else None
        data_set.DataSet.ensure_absent(dest, volumes=volumes)

        if src_ds_type == "USS":
            # Taking the temp file when a local file was copied with sftp.
            create_seq_dataset_from_file(src, dest, force, is_binary, asa_text, volume=volume)
        elif src_ds_type in data_set.DataSet.MVS_SEQ:
            data_set.DataSet.allocate_model_data_set(ds_name=dest, model=src_name, asa_text=asa_text, vol=volume)
        else:
            temp_dump = None
            try:
                # Dumping the member into a file in USS to compute the record length and
                # size for the new data set.
                src_attributes = datasets.list_datasets(src_name)[0]
                record_length = int(src_attributes.record_length)
                temp_dump = dump_data_set_member_to_file(src, is_binary)
                create_seq_dataset_from_file(
                    temp_dump,
                    dest,
                    force,
                    is_binary,
                    asa_text,
                    record_length=record_length,
                    volume=volume
                )
            finally:
                if temp_dump:
                    os.remove(temp_dump)
    elif dest_ds_type in data_set.DataSet.MVS_PARTITIONED and not dest_exists:
        # Taking the src as model if it's also a PDSE.
        if src_ds_type in data_set.DataSet.MVS_PARTITIONED:
            data_set.DataSet.allocate_model_data_set(ds_name=dest, model=src_name, executable=executable, asa_text=asa_text, vol=volume)
        elif src_ds_type in data_set.DataSet.MVS_SEQ:
            src_attributes = datasets.list_datasets(src_name)[0]
            # The size returned by listing is in bytes.
            size = int(src_attributes.total_space)
            record_format = src_attributes.record_format
            record_length = int(src_attributes.record_length)
            dest_params = get_data_set_attributes(
                dest,
                size,
                is_binary,
                asa_text,
                record_format=record_format,
                record_length=record_length,
                type="PDSE",
                volume=volume
            )
            data_set.DataSet.ensure_present(replace=force, **dest_params)
        elif src_ds_type == "USS":
            if os.path.isfile(src):
                # This is almost the same as allocating a sequential dataset.
                size = os.stat(src).st_size
                record_format = record_length = None
                type_ds = "PDSE"

                if is_binary:
                    record_format = "FB"
                    record_length = 80
                else:
                    record_format = "FB"
                    record_length = get_file_record_length(src)

                    # Adding 1 byte to the record length to accommodate
                    # ASA control chars.
                    if asa_text:
                        record_length += 1

                if executable:
                    record_format = "U"
                    record_length = 0
                    type_ds = "LIBRARY"

                dest_params = get_data_set_attributes(
                    dest,
                    size,
                    is_binary,
                    asa_text,
                    record_format=record_format,
                    record_length=record_length,
                    type=type_ds,
                    volume=volume
                )
            else:
                # TODO: decide on whether to compute the longest file record length and use that for the whole PDSE.
                size = sum(os.stat("{0}/{1}".format(src, member)).st_size for member in os.listdir(src))
                # This PDSE will be created with record format VB and a record length of 1028.

                if executable:
                    dest_params = get_data_set_attributes(
                        dest, size, is_binary,
                        record_format='U',
                        record_length=0,
                        type="LIBRARY",
                        volume=volume
                    )
                else:
                    dest_params = get_data_set_attributes(
                        dest,
                        size,
                        is_binary,
                        asa_text,
                        type="PDSE",
                        volume=volume
                    )

            data_set.DataSet.ensure_present(replace=force, **dest_params)
    elif dest_ds_type in data_set.DataSet.MVS_VSAM:
        # If dest_data_set is not available, always create the destination using the src VSAM
        # as a model.
        volumes = [volume] if volume else None
        data_set.DataSet.ensure_absent(dest, volumes=volumes)
        data_set.DataSet.allocate_model_data_set(ds_name=dest, model=src_name, vol=volume)
    if dest_ds_type not in data_set.DataSet.MVS_VSAM:
        dest_params = get_attributes_of_any_dataset_created(
            dest,
            src_ds_type,
            src,
            src_name,
            is_binary,
            asa_text,
            volume
        )
        dest_attributes = datasets.list_datasets(dest)[0]
        record_format = dest_attributes.record_format
        dest_params["type"] = dest_ds_type
        dest_params["record_format"] = record_format
    return True, dest_params


def normalize_line_endings(src, encoding=None):
    """
    Normalizes src's encoding to IBM-037 (a dataset's default) and then normalizes
    its line endings to LF.

    Arguments:
        src (str) -- Path of a USS file.
        encoding (dict, optional) -- Encoding options for the module.

    Returns:
        str -- Path to the normalized file.
    """
    # Before copying into a destination dataset, we'll make sure that
    # the source file doesn't contain any carriage returns that would
    # result in empty records in the destination.
    # Due to the differences between encodings, we'll normalize to IBM-037
    # before checking the EOL sequence.
    enc_utils = encode.EncodeUtils()
    src_tag = enc_utils.uss_file_tag(src)
    copy_handler = CopyHandler(AnsibleModuleHelper(dict()))

    if src_tag == "untagged":
        # This should only be true when src is a remote file and no encoding
        # was specified by the user.
        if not encoding:
            encoding = {"from": encode.Defaults.get_default_system_charset()}
        src_tag = encoding["from"]

    if src_tag != "IBM-037":
        fd, converted_src = tempfile.mkstemp()
        os.close(fd)

        enc_utils.uss_convert_encoding(
            src,
            converted_src,
            src_tag,
            "IBM-037"
        )
        copy_handler._tag_file_encoding(converted_src, "IBM-037")
        src = converted_src

    if copy_handler.file_has_crlf_endings(src):
        src = copy_handler.create_temp_with_lf_endings(src)

    return src


def data_set_locked(dataset_name):
    """
    Checks if a data set is in use and therefore locked (DISP=SHR), which
    is often caused by a long running task. Returns a boolean value to indicate the data set status.

    Arguments:
        dataset_name (str) - the data set name used to check if there is a lock.

    Returns:
        bool -- True if the data set is locked, or False if the data set is not locked.
    """
    # Using operator command "D GRS,RES=(*,{dataset_name})" to detect if a data set
    # is in use, when a data set is in use it will have "EXC/SHR and SHARE"
    # in the result with a length greater than 4.
    result = dict()
    result["stdout"] = []
    command_dgrs = "D GRS,RES=(*,{0})".format(dataset_name)
    response = opercmd.execute(command=command_dgrs)
    stdout = response.stdout_response
    if stdout is not None:
        for out in stdout.split("\n"):
            if out:
                result["stdout"].append(out)
    if len(result["stdout"]) > 4 and "EXC/SHR" in stdout and "SHARE" in stdout:
        return True
    elif len(result["stdout"]) <= 4 and "NO REQUESTORS FOR RESOURCE" in stdout:
        return False
    else:
        return False


def run_module(module, arg_def):
    # ********************************************************************
    # Verify the validity of module args. BetterArgParser raises ValueError
    # when a parameter fails its validation check
    # ********************************************************************
    try:
        parser = better_arg_parser.BetterArgParser(arg_def)
        parser.parse_args(module.params)
    except ValueError as err:
        # Bypass BetterArgParser when src is of the form 'SOME.DATA.SET(*)'
        if not is_member_wildcard(module.params["src"]):
            module.fail_json(
                msg="Parameter verification failed", stderr=str(err))
    # ********************************************************************
    # Initialize module variables
    # ********************************************************************
    src = module.params.get('src')
    dest = module.params.get('dest')
    remote_src = module.params.get('remote_src')
    is_binary = module.params.get('is_binary')
    executable = module.params.get('executable')
    asa_text = module.params.get('asa_text')
    aliases = module.params.get('aliases')
    backup = module.params.get('backup')
    backup_name = module.params.get('backup_name')
    validate = module.params.get('validate')
    mode = module.params.get('mode')
    group = module.params.get('group')
    owner = module.params.get('owner')
    encoding = module.params.get('encoding')
    volume = module.params.get('volume')
    tmphlq = module.params.get('tmp_hlq')
    force = module.params.get('force')
    force_lock = module.params.get('force_lock')
    content = module.params.get('content')

    dest_data_set = module.params.get('dest_data_set')
    if dest_data_set:
        if volume:
            dest_data_set["volumes"] = [volume]

    copy_member = is_member(dest)
    # This section we initialize different variables
    # that we used to pass from the action plugin.
    is_src_dir = os.path.isdir(src)
    is_uss = "/" in dest
    is_mvs_dest = is_data_set(dest)
    is_pds = is_src_dir and is_mvs_dest
    src_member = is_member(src)

    # ********************************************************************
    # When copying to and from a data set member, 'dest' or 'src' will be
    # in the form DATA.SET.NAME(MEMBER). When this is the case, extract the
    # actual name of the data set.
    # ********************************************************************
    dest_name = data_set.extract_dsname(dest)
    dest_member = data_set.extract_member_name(dest) if copy_member else None
    src_name = data_set.extract_dsname(src) if src else None
    member_name = data_set.extract_member_name(src) if src_member else None

    conv_path = src_ds_type = dest_ds_type = dest_exists = None
    res_args = dict()

    # ********************************************************************
    # 1. When the source is a USS file or directory , verify that the file
    #    or directory exists and has proper read permissions.
    # 2. Capture the file or data sets mode bits when mode param is set
    #    to 'preserve'
    # ********************************************************************
    if remote_src and "/" in src:
        # Keeping the trailing slash because the CopyHandler will do
        # different things depending on its existence.
        if src.endswith("/"):
            src = "{0}/".format(os.path.realpath(src))
        else:
            src = os.path.realpath(src)

        if not os.path.exists(src):
            module.fail_json(msg="Source {0} does not exist".format(src))
        if not os.access(src, os.R_OK):
            module.fail_json(msg="Source {0} is not readable".format(src))
        if mode == "preserve":
            mode = "0{0:o}".format(stat.S_IMODE(os.stat(src).st_mode))

    # ********************************************************************
    # Use the DataSet class to gather the type and volume of the source
    # and destination datasets, if needed.
    # ********************************************************************
    dest_member_exists = False
    converted_src = None
    # By default, we'll assume that src and dest don't have ASA control
    # characters. We'll only update these variables when they are
    # data sets with record format 'FBA' or 'VBA'.
    src_has_asa_chars = dest_has_asa_chars = False
    try:
        if "/" in src:
            src_ds_type = "USS"

            if os.path.isdir(src):
                is_src_dir = True

            # When the destination is a dataset, we'll normalize the source
            # file to UTF-8 for the record length computation as Python
            # generally uses UTF-8 as the default encoding.
            if not is_binary and not is_uss and not executable:
                new_src = src
                new_src = os.path.normpath(new_src)
                # Normalizing encoding when src is a USS file (only).
                encode_utils = encode.EncodeUtils()
                src_tag = encode_utils.uss_file_tag(new_src)
                # Normalizing to UTF-8.
                if not is_src_dir and src_tag != "UTF-8":
                    # If untagged, assuming the encoding/tag is the system's default.
                    if src_tag == "untagged" or src_tag is None:
                        if encoding:
                            src_tag = encoding["from"]
                        else:
                            src_tag = encode.Defaults.get_default_system_charset()

                    # Converting the original src to a temporary one in UTF-8.
                    fd, converted_src = tempfile.mkstemp()
                    os.close(fd)
                    encode_utils.uss_convert_encoding(
                        new_src,
                        converted_src,
                        src_tag,
                        "UTF-8"
                    )

                    # Creating the handler just for tagging, we're not copying yet!
                    copy_handler = CopyHandler(module, is_binary=is_binary)
                    copy_handler._tag_file_encoding(converted_src, "UTF-8")
        else:
            if data_set.DataSet.data_set_exists(src_name):
                if src_member and not data_set.DataSet.data_set_member_exists(src):
                    raise NonExistentSourceError(src)
                src_ds_type = data_set.DataSet.data_set_type(src_name)

                if src_ds_type not in data_set.DataSet.MVS_VSAM:
                    src_attributes = datasets.list_datasets(src_name)[0]
                    if src_attributes.record_format == 'FBA' or src_attributes.record_format == 'VBA':
                        src_has_asa_chars = True
            else:
                raise NonExistentSourceError(src)

            # An empty VSAM will throw an error when IDCAMS tries to open it to copy
            # the contents.
            if src_ds_type in data_set.DataSet.MVS_VSAM and data_set.DataSet.is_empty(src_name):
                module.exit_json(
                    note="The source VSAM {0} is likely empty. No data was copied.".format(src_name),
                    changed=False,
                    dest=dest
                )

            if encoding:
                module.fail_json(
                    msg="Encoding conversion is only valid for USS source"
                )

        if is_uss:
            dest_ds_type = "USS"
            if src_ds_type == "USS" and not is_src_dir and (dest.endswith("/") or os.path.isdir(dest)):
                src_basename = os.path.basename(src) if not content else "inline_copy"
                dest = os.path.normpath("{0}/{1}".format(dest, src_basename))
                if dest.startswith("//"):
                    dest = dest.replace("//", "/")

            if is_src_dir and not src.endswith("/"):
                dest_exists = os.path.exists(os.path.normpath("{0}/{1}".format(dest, os.path.basename(src))))
            else:
                dest_exists = os.path.exists(dest)

            if dest_exists and not os.access(dest, os.W_OK):
                module.fail_json(msg="Destination {0} is not writable".format(dest))
        else:
            dest_exists = data_set.DataSet.data_set_exists(dest_name, volume)
            dest_ds_type = data_set.DataSet.data_set_type(dest_name, volume)

            # dest_data_set.type overrides `dest_ds_type` given precedence rules
            if dest_data_set and dest_data_set.get("type"):
                dest_ds_type = dest_data_set.get("type")
            elif executable:
                """ When executable is selected and dest_exists is false means an executable PDSE was copied to remote,
                so we need to provide the correct dest_ds_type that will later be transformed into LIBRARY.
                Not using LIBRARY at this step since there are many checks with dest_ds_type in data_set.DataSet.MVS_PARTITIONED
                and LIBRARY is not in MVS_PARTITIONED frozen set."""
                dest_ds_type = "PDSE"

            if dest_data_set and (dest_data_set.get('record_format', '') == 'FBA' or dest_data_set.get('record_format', '') == 'VBA'):
                dest_has_asa_chars = True
            elif not dest_exists and asa_text:
                dest_has_asa_chars = True
            elif dest_exists and dest_ds_type not in data_set.DataSet.MVS_VSAM:
                dest_attributes = datasets.list_datasets(dest_name)[0]
                if dest_attributes.record_format == 'FBA' or dest_attributes.record_format == 'VBA':
                    dest_has_asa_chars = True

            if dest_data_set and (dest_data_set.get('record_format', '') == 'FBA' or dest_data_set.get('record_format', '') == 'VBA'):
                dest_has_asa_chars = True
            elif not dest_exists and asa_text:
                dest_has_asa_chars = True
            elif dest_exists and dest_ds_type not in data_set.DataSet.MVS_VSAM:
                dest_attributes = datasets.list_datasets(dest_name)[0]
                if dest_attributes.record_format == 'FBA' or dest_attributes.record_format == 'VBA':
                    dest_has_asa_chars = True

            if dest_ds_type in data_set.DataSet.MVS_PARTITIONED:
                # Checking if the members that would be created from the directory files
                # are already present on the system.
                if copy_member:
                    dest_member_exists = dest_exists and data_set.DataSet.data_set_member_exists(dest)
                elif src_ds_type == "USS":
                    root_dir = src
                    dest_member_exists = dest_exists and data_set.DataSet.files_in_data_set_members(root_dir, dest)
                elif src_ds_type in data_set.DataSet.MVS_PARTITIONED:
                    dest_member_exists = dest_exists and data_set.DataSet.data_set_shared_members(src, dest)

    except Exception as err:
        module.fail_json(msg=str(err))

    # ********************************************************************
    # Some src and dest combinations are incompatible. For example, it is
    # not possible to copy a PDS member to a VSAM data set or a USS file
    # to a PDS. Perform these sanity checks.
    # Note: dest_ds_type can also be passed from dest_data_set.type
    # ********************************************************************
    if not is_compatible(
        src_ds_type,
        dest_ds_type,
        copy_member,
        src_member,
        is_src_dir,
        (src_ds_type == "USS" and src is None),
        executable,
        asa_text,
        src_has_asa_chars,
        dest_has_asa_chars
    ):
        error_msg = "Incompatible target type '{0}' for source '{1}'".format(
            dest_ds_type, src_ds_type
        )

        if asa_text:
            error_msg = "{0}. Neither the source or the destination are ASA text files.".format(error_msg)

        module.fail_json(
            msg=error_msg
        )

    # ********************************************************************
    # To validate the source and dest are not locked in a batch process by
    # the machine and not generate a false positive check the disposition
    # for try to write in dest and if both src and dest are in lock.
    # ********************************************************************
    if dest_ds_type != "USS":
        if not force_lock:
            is_dest_lock = data_set_locked(dest_name)
            if is_dest_lock:
                module.fail_json(
                    msg="Unable to write to dest '{0}' because a task is accessing the data set.".format(dest_name))

    # ********************************************************************
    # Alias support is not avaiable to and from USS for text-based data sets.
    # ********************************************************************
    if aliases:
        if (src_ds_type == 'USS' or dest_ds_type == 'USS') and not executable:
            module.fail_json(
                msg="Alias support for text-based data sets is not available "
                    + "for USS sources (src) or targets (dest). "
                    + "Try setting executable=True or aliases=False."
            )

    # ********************************************************************
    # Attempt to write PDS (not member) to USS file (i.e. a non-directory)
    # ********************************************************************
    if (
        src_ds_type in data_set.DataSet.MVS_PARTITIONED and not src_member
        and dest_ds_type == 'USS' and not os.path.isdir(dest)
    ):
        module.fail_json(
            msg="Cannot write a partitioned data set (PDS) to a USS file."
        )

    # ********************************************************************
    # Backup should only be performed if dest is an existing file or
    # data set. Otherwise ignored.
    # ********************************************************************
    if dest_exists:
        if backup or backup_name:
            if dest_ds_type in data_set.DataSet.MVS_PARTITIONED and data_set.DataSet.is_empty(dest_name):
                # The partitioned data set is empty
                res_args["note"] = "Destination is empty, backup request ignored"
            else:
                backup_name = backup_data(dest, dest_ds_type, backup_name, tmphlq)

    # ********************************************************************
    # If destination does not exist, it must be created. To determine
    # what type of data set destination must be, a couple of simple checks
    # can be done. For example:
    # 1. Destination must be a PDS/PDSE if:
    #   - The source is a local directory
    #   - The source is a USS directory
    #   - The source is a PDS/PDSE
    #   - The destination is in the form DATA.SET.NAME(MEMBER)
    #
    # USS files and sequential data sets are not required to be explicitly
    # created; they are automatically created by the Python/ZOAU API.
    #
    # is_pds is determined in the action plugin when src is a directory and destination
    # is a data set (is_src_dir and is_mvs_dest are true)
    # ********************************************************************
    else:
        if not dest_ds_type:
            if (
                is_pds
                or copy_member
                or (src_ds_type in data_set.DataSet.MVS_PARTITIONED and (not src_member) and is_mvs_dest)
                or (src and os.path.isdir(src) and is_mvs_dest)
            ):
                dest_ds_type = "PDSE"
            elif src_ds_type in data_set.DataSet.MVS_VSAM:
                dest_ds_type = src_ds_type
            elif not is_uss:
                dest_ds_type = "SEQ"

            # Filling in the type in dest_data_set in case the user didn't specify it in
            # the playbook.
            if dest_data_set:
                dest_data_set["type"] = dest_ds_type

        res_args["changed"] = True

    if not does_destination_allow_copy(
        src,
        is_src_dir,
        dest_name,
        dest_exists,
        dest_member_exists,
        dest_ds_type,
        is_uss,
        force,
        volume
    ):
        module.fail_json(
            msg="{0} already exists on the system, unable to overwrite unless force=True is specified.".format(dest),
            changed=False,
            dest=dest
        )

    # Here we'll use the normalized source file by shadowing the
    # original one. This change applies only to the
    # allocate_destination_data_set call.
    if converted_src:
        original_src = src
        src = converted_src

    try:
        if not is_uss:
            res_args["changed"], res_args["dest_data_set_attrs"] = allocate_destination_data_set(
                src,
                dest_name, src_ds_type,
                dest_ds_type,
                dest_exists,
                force,
                is_binary,
                executable,
                asa_text,
                dest_data_set=dest_data_set,
                volume=volume
            )
    except Exception as err:
        if converted_src:
            src = original_src
        module.fail_json(
            msg="Unable to allocate destination data set: {0}".format(str(err)),
            dest_exists=dest_exists
        )

    if converted_src:
        src = original_src

    # ********************************************************************
    # Encoding conversion is only valid if the source is a local file,
    # local directory or a USS file/directory.
    # ********************************************************************
    copy_handler = CopyHandler(
        module,
        is_binary=is_binary,
        executable=executable,
        asa_text=asa_text,
        backup_name=backup_name,
        force_lock=force_lock,
    )

    try:
        if encoding:
            # 'conv_path' points to the converted src file or directory
            # if is_mvs_dest:
            #     encoding["to"] = encode.Defaults.DEFAULT_EBCDIC_MVS_CHARSET

            conv_path = copy_handler.convert_encoding(src, encoding, remote_src)

        # ------------------------------- o -----------------------------------
        # Copy to USS file or directory
        # ---------------------------------------------------------------------
        if is_uss:
            uss_copy_handler = USSCopyHandler(
                module,
                is_binary=is_binary,
                executable=executable,
                asa_text=asa_text,
                aliases=aliases,
                common_file_args=dict(mode=mode, group=group, owner=owner),
                backup_name=backup_name,
            )

            original_checksum = None
            if dest_exists:
                original_checksum = get_file_checksum(dest)

            dest = uss_copy_handler.copy_to_uss(
                src,
                dest,
                conv_path,
                src_ds_type,
                src_member,
                member_name,
                force,
                bool(content)
            )
            res_args['size'] = os.stat(dest).st_size
            remote_checksum = dest_checksum = None

            try:
                remote_checksum = get_file_checksum(src)
                dest_checksum = get_file_checksum(dest)

                if validate:
                    res_args["checksum"] = dest_checksum

                    if remote_checksum != dest_checksum:
                        raise CopyOperationError(msg="Validation failed for copied files")

                res_args["changed"] = (
                    res_args.get("changed") or dest_checksum != original_checksum or os.path.isdir(dest)
                )
            except Exception as err:
                if validate:
                    raise CopyOperationError(msg="Unable to calculate checksum", stderr=str(err))

        # ------------------------------- o -----------------------------------
        # Copy to sequential data set (PS / SEQ)
        # ---------------------------------------------------------------------
        elif dest_ds_type in data_set.DataSet.MVS_SEQ:
            # TODO: check how ASA behaves with this
            if src_ds_type == "USS" and not is_binary:
                new_src = conv_path or src
                conv_path = normalize_line_endings(new_src, encoding)

            copy_handler.copy_to_seq(
                src,
                conv_path,
                dest,
                src_ds_type
            )
            res_args["changed"] = True
            dest = dest.upper()

        # ---------------------------------------------------------------------
        # Copy to PDS/PDSE
        # ---------------------------------------------------------------------
        elif dest_ds_type in data_set.DataSet.MVS_PARTITIONED or dest_ds_type == "LIBRARY":

            pdse_copy_handler = PDSECopyHandler(
                module,
                is_binary=is_binary,
                executable=executable,
                asa_text=asa_text,
                aliases=aliases,
                backup_name=backup_name,
                force_lock=force_lock,
            )

            pdse_copy_handler.copy_to_pdse(
                src,
                conv_path,
                dest_name,
                src_ds_type,
                src_member=src_member,
                dest_member=dest_member,
                encoding=encoding
            )
            res_args["changed"] = True
            dest = dest.upper()

        # ------------------------------- o -----------------------------------
        # Copy to VSAM data set
        # ---------------------------------------------------------------------
        else:
            copy_handler.copy_to_vsam(src, dest)
            res_args["changed"] = True

    except CopyOperationError as err:
        raise err

    res_args.update(
        dict(
            src=src,
            dest=dest,
            ds_type=dest_ds_type,
            dest_exists=dest_exists,
            backup_name=backup_name,
        )
    )

    return res_args, conv_path


def main():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='str'),
            dest=dict(required=True, type='str'),
            is_binary=dict(type='bool', default=False),
            executable=dict(type='bool', default=False),
            asa_text=dict(type='bool', default=False),
            aliases=dict(type='bool', default=False, required=False),
            encoding=dict(
                type='dict',
                required=False,
                options={
                    'from': dict(
                        type='str',
                        required=True,
                    ),
                    "to": dict(
                        type='str',
                        required=False,
                    )
                }
            ),
            content=dict(type='str', no_log=True),
            backup=dict(type='bool', default=False),
            backup_name=dict(type='str'),
            local_follow=dict(type='bool', default=True),
            remote_src=dict(type='bool', default=False),
            ignore_sftp_stderr=dict(type='bool', default=False),
            validate=dict(type='bool', default=False),
            volume=dict(type='str', required=False),
            dest_data_set=dict(
                type='dict',
                required=False,
                options=dict(
                    type=dict(
                        type='str',
                        choices=['BASIC', 'KSDS', 'ESDS', 'RRDS',
                                 'LDS', 'SEQ', 'PDS', 'PDSE', 'MEMBER', 'LIBRARY'],
                        required=True,
                    ),
                    space_primary=dict(
                        type='int', required=False),
                    space_secondary=dict(
                        type='int', required=False),
                    space_type=dict(
                        type='str',
                        choices=['K', 'M', 'G', 'CYL', 'TRK'],
                        required=False,
                    ),
                    record_format=dict(
                        type='str',
                        choices=["FB", "VB", "FBA", "VBA", "U"],
                        required=False
                    ),
                    record_length=dict(type='int', required=False),
                    block_size=dict(type='int', required=False),
                    directory_blocks=dict(type="int", required=False),
                    key_offset=dict(type="int", required=False, no_log=False),
                    key_length=dict(type="int", required=False, no_log=False),
                    sms_storage_class=dict(type="str", required=False),
                    sms_data_class=dict(type="str", required=False),
                    sms_management_class=dict(type="str", required=False),
                )
            ),
            use_template=dict(type='bool', default=False),
            template_parameters=dict(
                type='dict',
                required=False,
                options=dict(
                    variable_start_string=dict(type='str', default='{{'),
                    variable_end_string=dict(type='str', default='}}'),
                    block_start_string=dict(type='str', default='{%'),
                    block_end_string=dict(type='str', default='%}'),
                    comment_start_string=dict(type='str', default='{#'),
                    comment_end_string=dict(type='str', default='#}'),
                    line_statement_prefix=dict(type='str', required=False),
                    line_comment_prefix=dict(type='str', required=False),
                    lstrip_blocks=dict(type='bool', default=False),
                    trim_blocks=dict(type='bool', default=True),
                    keep_trailing_newline=dict(type='bool', default=False),
                    newline_sequence=dict(
                        type='str',
                        default='\n',
                        choices=['\n', '\r', '\r\n']
                    ),
                    auto_reload=dict(type='bool', default=False),
                )
            ),
            force=dict(type='bool', default=False),
            force_lock=dict(type='bool', default=False),
            mode=dict(type='str', required=False),
            owner=dict(type='str', required=False),
            group=dict(type='str', required=False),
            tmp_hlq=dict(type='str', required=False, default=None),
        ),
    )

    arg_def = dict(
        src=dict(arg_type='data_set_or_path', required=False),
        dest=dict(arg_type='data_set_or_path', required=True),
        is_binary=dict(arg_type='bool', required=False, default=False),
        executable=dict(arg_type='bool', required=False, default=False),
        asa_text=dict(arg_type='bool', required=False, default=False),
        aliases=dict(arg_type='bool', required=False, default=False),
        content=dict(arg_type='str', required=False),
        backup=dict(arg_type='bool', default=False, required=False),
        backup_name=dict(arg_type='data_set_or_path', required=False),
        local_follow=dict(arg_type='bool', default=True, required=False),
        remote_src=dict(arg_type='bool', default=False, required=False),
        checksum=dict(arg_type='str', required=False),
        validate=dict(arg_type='bool', required=False),
        volume=dict(arg_type='str', required=False),
        force_lock=dict(type='bool', default=False),

        dest_data_set=dict(
            arg_type='dict',
            required=False,
            options=dict(
                type=dict(arg_type='str', required=True),
                space_primary=dict(arg_type='int', required=False),
                space_secondary=dict(
                    arg_type='int', required=False),
                space_type=dict(arg_type='str', required=False),
                record_format=dict(
                    arg_type='str', required=False),
                block_size=dict(arg_type='int', required=False),
                directory_blocks=dict(arg_type="int", required=False),
                key_offset=dict(arg_type="int", required=False),
                key_length=dict(arg_type="int", required=False),
                sms_storage_class=dict(arg_type="str", required=False),
                sms_data_class=dict(arg_type="str", required=False),
                sms_management_class=dict(arg_type="str", required=False),
            )
        ),

        use_template=dict(arg_type='bool', required=False),
        template_parameters=dict(
            arg_type='dict',
            required=False,
            options=dict(
                variable_start_string=dict(arg_type='str', required=False),
                variable_end_string=dict(arg_type='str', required=False),
                block_start_string=dict(arg_type='str', required=False),
                block_end_string=dict(arg_type='str', required=False),
                comment_start_string=dict(arg_type='str', required=False),
                comment_end_string=dict(arg_type='str', required=False),
                line_statement_prefix=dict(arg_type='str', required=False),
                line_comment_prefix=dict(arg_type='str', required=False),
                lstrip_blocks=dict(arg_type='bool', required=False),
                trim_blocks=dict(arg_type='bool', required=False),
                keep_trailing_newline=dict(arg_type='bool', required=False),
                newline_sequence=dict(arg_type='str', required=False),
                auto_reload=dict(arg_type='bool', required=False),
            )
        ),
    )

    if (
        not module.params.get("encoding").get("to")
        and not module.params.get("remote_src")
        and not module.params.get("is_binary")
        and not module.params.get("executable")
    ):
        module.params["encoding"]["to"] = encode.Defaults.get_default_system_charset()
    elif (
        not module.params.get("encoding").get("to")
    ):
        module.params["encoding"] = None

    if module.params.get("encoding"):
        module.params.update(
            dict(
                from_encoding=module.params.get("encoding").get("from"),
                to_encoding=module.params.get("encoding").get("to"),
            )
        )
        arg_def.update(
            dict(
                from_encoding=dict(arg_type="encoding"),
                to_encoding=dict(arg_type="encoding"),
            )
        )

    res_args = conv_path = None
    try:
        res_args, conv_path = run_module(module, arg_def)
        module.exit_json(**res_args)
    except CopyOperationError as err:
        cleanup([])
        module.fail_json(**(err.json_args))
    finally:
        cleanup([conv_path])


class EncodingConversionError(Exception):
    def __init__(self, src, f_code, t_code):
        self.msg = "Unable to convert encoding for {0} from {1} to {2}".format(
            src, f_code, t_code
        )
        super().__init__(self.msg)


class NonExistentSourceError(Exception):
    def __init__(self, src):
        self.msg = "Source data set {0} does not exist".format(src)
        super().__init__(self.msg)


class DataSetMemberAttributeError(Exception):
    def __init__(self, src):
        self.msg = "Unable to get size and record length of member {0}".format(src)
        super().__init__(self.msg)


class CopyOperationError(Exception):
    def __init__(
        self,
        msg,
        rc=None,
        stdout=None,
        stderr=None,
        stdout_lines=None,
        stderr_lines=None,
        cmd=None,
        dest_exists=None,
        overwritten_members=None,
        new_members=None
    ):
        self.json_args = dict(
            msg=msg,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            stdout_lines=stdout_lines,
            stderr_lines=stderr_lines,
            cmd=cmd,
            dest_exists=dest_exists,
        )
        self.overwritten_members = overwritten_members
        self.new_members = new_members
        super().__init__(msg)


if __name__ == "__main__":
    main()
