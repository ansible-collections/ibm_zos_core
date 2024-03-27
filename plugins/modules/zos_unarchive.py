#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023 - 2024
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zos_unarchive
version_added: "1.7.0"
author:
  - Oscar Fernando Flores Garcia (@fernandofloresg)
short_description: Unarchive files and data sets in z/OS.
description:
  - The C(zos_unarchive) module unpacks an archive after optionally
    transferring it to the remote system.
  - For supported archive formats, see option C(format).
  - Supported sources are USS (UNIX System Services) or z/OS data sets.
  - Mixing MVS data sets with USS files for unarchiving is not supported.
  - The archive is sent to the remote as binary, so no encoding is performed.
options:
  src:
    description:
      - The remote absolute path or data set of the archive to be uncompressed.
      - I(src) can be a USS file or MVS data set name.
      - USS file paths should be absolute paths.
      - MVS data sets supported types are C(SEQ), C(PDS), C(PDSE).
    type: str
    required: true
  format:
    description:
      - The compression type and corresponding options to use when archiving
        data.
    type: dict
    required: true
    suboptions:
      name:
        description:
          - The compression format to use.
        type: str
        required: true
        choices:
          - bz2
          - gz
          - tar
          - zip
          - terse
          - xmit
          - pax
      format_options:
        description:
          - Options specific to a compression format.
        type: dict
        required: false
        suboptions:
          xmit_log_data_set:
            description:
              - Provide the name of a data set to store xmit log output.
              - If the data set provided does not exist, the program
                will create it.
              - 'If the data set provided exists, the data set must have
                the following attributes: LRECL=255, BLKSIZE=3120, and
                RECFM=VB'
              - When providing the I(xmit_log_data_set) name, ensure there
                is adequate space.
            type: str
          use_adrdssu:
            description:
              - If set to true, the C(zos_archive) module will use Data
                Facility Storage Management Subsystem data set services
                (DFSMSdss) program ADRDSSU to uncompress data sets from
                a portable format after using C(xmit) or C(terse).
            type: bool
            default: False
          dest_volumes:
            description:
              - When I(use_adrdssu=True), specify the volume the data sets
                will be written to.
              - If no volume is specified, storage management rules will be
                used to determine the volume where the file will be
                unarchived.
              - If the storage administrator has specified a system default
                unit name and you do not set a volume name for
                non-system-managed data sets, then the system uses the
                volumes associated with the default unit name. Check with
                your storage administrator to determine whether a default
                unit name has been specified.
            type: list
            elements: str
  dest:
    description:
      - The remote absolute path or data set where the content should be unarchived to.
      - I(dest) can be a USS file, directory or MVS data set name.
      - If dest has missing parent directories, they will not be created.
    type: str
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
      - The permission of the uncompressed files.
      - If C(dest) is USS, this will act as Unix file mode, otherwise ignored.
      - It should be noted that modes are octal numbers.
        The user must either add a leading zero so that Ansible's YAML parser
        knows it is an octal number (like C(0644) or C(01777))or quote it
        (like C('644') or C('1777')) so Ansible receives a string and can do
        its own conversion from string into number. Giving Ansible a number
        without following one of these rules will end up with a decimal number
        which will have unexpected results.
      - The mode may also be specified as a symbolic mode
        (for example, ``u+rwx`` or ``u=rw,g=r,o=r``) or a special
        string `preserve`.
      - I(mode=preserve) means that the file will be given the same permissions
        as
        the source file.
    type: str
    required: false
  owner:
    description:
      - Name of the user that should own the filesystem object, as would be
        passed to the chown command.
      - When left unspecified, it uses the current user unless you are root,
        in which case it can preserve the previous ownership.
    type: str
    required: false
  include:
    description:
      - A list of directories, files or data set names to extract from the
        archive.
      - When C(include) is set, only those files will we be extracted leaving
        the remaining files in the archive.
      - Mutually exclusive with exclude.
    type: list
    elements: str
    required: false
  exclude:
    description:
      - List the directory and file or data set names that you would like to
        exclude from the unarchive action.
      - Mutually exclusive with include.
    type: list
    elements: str
    required: false
  list:
    description:
      - Will list the contents of the archive without unpacking.
    type: bool
    required: false
    default: false
  dest_data_set:
    description:
      - Data set attributes to customize a C(dest) data set that the archive will be copied into.
    required: false
    type: dict
    suboptions:
      name:
        description:
          - Desired name for destination dataset.
        type: str
        required: false
      type:
        description:
          - Organization of the destination
        type: str
        required: false
        default: SEQ
        choices:
          - SEQ
          - PDS
          - PDSE
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
          - If the destination data set does not exist, this sets the format of
            the
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
          - For variable data sets, the length must include the 4-byte prefix
            area.
          - "Defaults vary depending on format: If FB/FBA 80, if VB/VBA 137,
            if U 0."
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
  tmp_hlq:
    description:
      - Override the default high level qualifier (HLQ) for temporary data
        sets.
      - The default HLQ is the Ansible user used to execute the module and if
        that is not available, then the environment variable value C(TMPHLQ) is
        used.
    type: str
    required: false
  force:
    description:
      - If set to true and the remote file or data set dest exists, the dest
        will be deleted.
    type: bool
    required: false
    default: false
  remote_src:
    description:
      - If set to true, C(zos_unarchive) retrieves the archive from the remote
        system.
      - If set to false, C(zos_unarchive) searches the local machine (Ansible
        controller) for the archive.
    type: bool
    required: false
    default: false
notes:
  - VSAMs are not supported.
  - This module uses L(zos_copy,./zos_copy.html) to copy local scripts to
    the remote machine which uses SFTP (Secure File Transfer Protocol) for the
    underlying transfer protocol; SCP (secure copy protocol) and Co:Z SFTP are not
    supported. In the case of Co:z SFTP, you can exempt the Ansible user id on z/OS
    from using Co:Z thus falling back to using standard SFTP. If the module detects
    SCP, it will temporarily use SFTP for transfers, if not available, the module
    will fail.
seealso:
  - module: zos_archive
'''

EXAMPLES = r'''
# Simple extract
- name: Copy local tar file and unpack it on the managed z/OS node.
  zos_unarchive:
    src: "./files/archive_folder_test.tar"
    format:
      name: tar

# use include
- name: Unarchive a bzip file selecting only a file to unpack.
  zos_unarchive:
    src: "/tmp/test.bz2"
    format:
      name: bz2
    include:
      - 'foo.txt'

# Use exclude
- name: Unarchive a terse data set and excluding data sets from unpacking.
  zos_unarchive:
    src: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse
    exclude:
      - USER.ARCHIVE.TEST1
      - USER.ARCHIVE.TEST2

# List option
- name: List content from XMIT
  zos_unarchive:
    src: "USER.ARCHIVE.RESULT.XMIT"
    format:
      name: xmit
      format_options:
        use_adrdssu: True
    list: True
'''

RETURN = r'''
src:
  description:
    File path or data set name unpacked.
  type: str
  returned: always
dest_path:
  description:
    - Destination path where archive was unpacked.
  type: str
  returned: always
targets:
  description:
    List of files or data sets in the archive.
  type: list
  elements: str
  returned: success
missing:
  description:
    Any files or data sets not found during extraction.
  type: str
  returned: success
'''

import abc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
    validation,
    mvs_cmd)
import re
import os
import zipfile
import tarfile
import traceback
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError,
)

try:
    from zoautil_py import datasets
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())

data_set_regex = r"(?:(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})(?:[.]{1})){1,21}[A-Z$#@]{1}[A-Z0-9$#@-]{0,7}(?:\([A-Z$#@]{1}[A-Z0-9$#@]{0,7}\)){0,1}"

XMIT_RECORD_LENGTH = 80
AMATERSE_RECORD_LENGTH = 1024


class Unarchive():
    def __init__(self, module):
        self.module = module
        self.src = module.params.get("src")
        self.dest = module.params.get("dest")
        self.format = module.params.get("format").get("name")
        self.format_options = module.params.get("format").get("format_options")
        self.tmphlq = module.params.get("tmp_hlq")
        self.force = module.params.get("force")
        self.targets = list()
        self.include = module.params.get("include")
        self.exclude = module.params.get("exclude")
        self.list = module.params.get("list")
        self.changed = False
        self.missing = list()
        self.remote_src = module.params.get("remote_src")
        if self.dest == '':
            self.dest = os.path.dirname(self.src)

    @abc.abstractmethod
    def extract_src(self):
        pass

    @abc.abstractmethod
    def _list_content(self):
        pass

    def src_exists(self):
        return self.src and os.path.exists(self.src)

    def dest_type(self):
        return "USS"

    def dest_unarchived(self):
        return bool(self.targets)

    def update_permissions(self):
        """
        Update permissions in unarchived files.
        """
        for target in self.targets:
            file_name = os.path.join(validation.validate_safe_path(self.dest), validation.validate_safe_path(target))
            file_args = self.module.load_file_common_arguments(self.module.params, path=file_name)
            self.module.set_fs_attributes_if_different(file_args, self.changed)

    @property
    def result(self):
        return {
            'src': self.src,
            'dest_path': self.dest,
            'changed': self.changed,
            'targets': self.targets,
            'missing': self.missing,
        }

    def extract_all(self, members):
        for member in members:
            self.file.extract(member)


class TarUnarchive(Unarchive):
    def __init__(self, module):
        super(TarUnarchive, self).__init__(module)

    def open(self, path):
        """Open an archive using tarfile lib for read.

        Arguments:
            path(str): Path to a tar, pax, gz or bz2 file to be opened.

        Returns:
            Return a TarFile object for the path name.
        """
        if self.format == 'tar':
            file = tarfile.open(path, 'r')
        elif self.format in ('pax'):
            file = tarfile.open(path, 'r', format=tarfile.GNU_FORMAT)
        elif self.format in ('gz', 'bz2'):
            file = tarfile.open(path, 'r:' + self.format)
        else:
            self.module.fail_json(msg="%s is not a valid archive format for listing contents" % self.format)
        return file

    def list_archive_content(self, path):
        self.targets = self._list_content(self.src)

    def _list_content(self, path):
        """Returns a list of members in an archive.

        Arguments:
            path(str): Path to a tar, pax, gz or bz2 file to list its contents.

        Returns:
            list(str): List of members inside the archive.
        """
        self.file = self.open(path)
        members = self.file.getnames()
        self.file.close()
        return members

    def extract_src(self):
        """Unpacks the contents of the archive stored in path into dest folder.

        """
        original_working_dir = os.getcwd()
        # The function gets relative paths, so it changes the current working
        # directory to the root of src.
        os.chdir(self.dest)
        self.file = self.open(self.src)

        files_in_archive = self.file.getnames()
        if self.include:
            for path in self.include:
                if path not in files_in_archive:
                    self.missing.append(path)
                else:
                    self.file.extract(path)
                    self.targets.append(path)
        elif self.exclude:
            for path in files_in_archive:
                if path not in self.exclude:
                    self.file.extract(path)
                    self.targets.append(path)
        else:
            self.extract_all(members=sanitize_members(self.file.getmembers(), self.dest, self.format))
            self.targets = files_in_archive
        self.file.close()
        # Returning the current working directory to what it was before to not
        # interfere with the rest of the module.
        os.chdir(original_working_dir)
        self.changed = bool(self.targets)


class ZipUnarchive(Unarchive):
    def __init__(self, module):
        super(ZipUnarchive, self).__init__(module)

    def open(self, path):
        """Unpacks the contents of the archive stored in path into dest folder.

        """
        try:
            file = zipfile.ZipFile(path, 'r', zipfile.ZIP_DEFLATED, True)
        except zipfile.BadZipFile:
            self.module.fail_json(
                msg="Improperly compressed zip file, unable to to open file {0} ".format(path)
            )
        return file

    def list_archive_content(self):
        self.targets = self._list_content(self.src)

    def _list_content(self, path):
        """Returns a list of members in an archive.

        Arguments:
            path(str): Path to a tar, pax, gz or bz2 file to list its contents.

        Returns:
            list(str): List of members inside the archive.
        """
        self.file = self.open(path)
        members = self.file.namelist()
        self.file.close()
        return members

    def extract_src(self):
        """Returns a list of members in an archive.

        Arguments:
            path(str): Path to a tar, pax, gz or bz2 file to list its contents.

        Returns:
            list(str): List of members inside the archive.
        """
        original_working_dir = os.getcwd()
        # The function gets relative paths, so it changes the current working
        # directory to the root of src.
        os.chdir(self.dest)
        self.file = self.open(self.src)

        files_in_archive = self.file.namelist()
        if self.include:
            for path in self.include:
                if path not in files_in_archive:
                    self.missing.append(path)
                else:
                    self.file.extract(path)
                    self.targets.append(path)
        elif self.exclude:
            for path in files_in_archive:
                if path not in self.exclude:
                    self.file.extract(path)
                    self.targets.append(path)
        else:
            self.extract_all(members=sanitize_members(self.file.infolist(), self.dest, self.format))
            self.targets = files_in_archive
        self.file.close()
        # Returning the current working directory to what it was before to not
        # interfere with the rest of the module.
        os.chdir(original_working_dir)
        self.changed = bool(self.targets)


class MVSUnarchive(Unarchive):
    def __init__(self, module):
        super(MVSUnarchive, self).__init__(module)
        self.volumes = self.format_options.get("dest_volumes")
        self.use_adrdssu = self.format_options.get("use_adrdssu")
        self.dest_data_set = module.params.get("dest_data_set")
        self.dest_data_set = dict() if self.dest_data_set is None else self.dest_data_set
        self.source_size = 0

    def dest_type(self):
        return "MVS"

    def _compute_dest_data_set_size(self):
        """
        Computes the attributes that the destination data set or temporary destination
        data set should have in terms of size, record_length, etc.
        """

        """
        - Size of temporary DS for archive handling.

        If remote_src then we can get the source_size from archive on the system.

        If not remote_src then we can get the source_size from temporary_ds.
        Both are named src so no problemo.

        If format is xmit, dest_data_set size is the same as source_size.

        If format is terse, dest_data_set size is different than the source_size, has to be greater,
        but how much? In this case we can add dest_data_set option.

        Apparently the only problem is when format name is terse.
        """

        # Get the size from the system
        src_attributes = datasets.list_datasets(self.src)[0]
        # The size returned by list_datasets is in bytes.
        source_size = int(src_attributes.total_space)
        if self.format == 'terse':
            source_size = int(source_size * 1.5)
        return source_size

    def _create_dest_data_set(
            self,
            name=None,
            replace=None,
            type=None,
            space_primary=None,
            space_secondary=None,
            space_type=None,
            record_format=None,
            record_length=None,
            block_size=None,
            directory_blocks=None,
            key_length=None,
            key_offset=None,
            sms_storage_class=None,
            sms_data_class=None,
            sms_management_class=None,
            volumes=None,
            tmp_hlq=None,
            force=None,
    ):
        """Create a temporary data set.

        Arguments:
            tmp_hlq(str): A HLQ specified by the user for temporary data sets.

        Returns:
            str: Name of the temporary data set created.
        """
        arguments = locals()
        if name is None:
            if tmp_hlq:
                hlq = tmp_hlq
            else:
                hlq = datasets.get_hlq()
            temp_ds = datasets.tmp_name(high_level_qualifier=hlq)
            arguments.update(name=temp_ds)
        if record_format is None:
            arguments.update(record_format="FB")
        if record_length is None:
            arguments.update(record_length=80)
        if type is None:
            arguments.update(type="SEQ")
        if space_primary is None:
            arguments.update(space_primary=self._compute_dest_data_set_size())
        arguments.pop("self")
        changed = data_set.DataSet.ensure_present(**arguments)
        return arguments["name"], changed

    def _get_include_data_sets_cmd(self):
        include_cmd = "INCL( "
        for include_ds in self.include:
            include_cmd += " '{0}', - \n".format(include_ds)
        include_cmd += " ) - \n"
        return include_cmd

    def _get_exclude_data_sets_cmd(self):
        exclude_cmd = "EXCL( - \n"
        for exclude_ds in self.exclude:
            exclude_cmd += " '{0}', - \n".format(exclude_ds)
        exclude_cmd += " ) - \n"
        return exclude_cmd

    def _get_volumes(self):
        volumes_cmd = "OUTDYNAM( - \n"
        for volume in self.volumes:
            volumes_cmd += " ('{0}'), - \n".format(volume)
        volumes_cmd += " ) - \n"
        return volumes_cmd

    def _restore(self, source):
        """
        Calls ADDRSU using RESTORE to unpack the dump datasets.

        Arguments:
            source(str): Name of the data set to use as archive in ADRDSSU restore operation.

        Returns:
            int: Return code result of restore operation.
        """
        filter = "INCL(**) "
        volumes = ""
        force = "REPLACE -\n TOLERATE(ENQFAILURE) " if self.force else ""
        if self.include:
            filter = self._get_include_data_sets_cmd()
        if self.exclude:
            filter = self._get_exclude_data_sets_cmd()
        if self.volumes:
            volumes = self._get_volumes()
        restore_cmd = """ RESTORE INDD(ARCHIVE) -
                          DS( -
                            {0} ) -
                            {1} -
                        CATALOG -
                        {2} """.format(filter, volumes, force)
        dds = dict(archive="{0},old".format(source))
        rc, out, err = mvs_cmd.adrdssu(cmd=restore_cmd, dds=dds, authorized=True)
        self._get_restored_datasets(out)

        if rc != 0:
            # AdrddssuRestoreError
            unrestored_data_sets = self._get_unrestored_datasets(out)
            unrestored_data_sets = ", ".join(unrestored_data_sets)
            self.clean_environment(data_sets=[source], uss_files=[], remove_targets=True)
            self.module.fail_json(
                msg="Failed executing ADRDSSU to unarchive {0}. List of data sets not restored : {1}".format(source, unrestored_data_sets),
                stdout=out,
                stderr=err,
                stdout_lines=restore_cmd,
                rc=rc,
            )
        return rc

    def src_exists(self):
        return data_set.DataSet.data_set_exists(self.src)

    def _get_restored_datasets(self, output):
        ds_list = list()
        find_ds_list = re.findall(r"SUCCESSFULLY PROCESSED\n(?:.*\n)*", output)
        if find_ds_list:
            ds_list = re.findall(data_set_regex, find_ds_list[0])
        self.targets = ds_list
        return ds_list

    def _get_unrestored_datasets(self, output):
        ds_list = list()
        output = output.split("SUCCESSFULLY PROCESSED")[0]
        find_ds_list = re.findall(r"NOT PROCESSED FROM THE LOGICALLY FORMATTED DUMP TAPE DUE TO \n(?:.*\n)*", output)
        if find_ds_list:
            ds_list = re.findall(data_set_regex, find_ds_list[0])
        return ds_list

    @abc.abstractmethod
    def unpack(self):
        pass

    def extract_src(self):
        """Extract the MVS path contents.

        """
        temp_ds = ""
        if not self.use_adrdssu:
            temp_ds, rc = self._create_dest_data_set(**self.dest_data_set)
            rc = self.unpack(self.src, temp_ds)
        else:
            temp_ds, rc = self._create_dest_data_set(type="SEQ",
                                                     record_format="U",
                                                     record_length=0,
                                                     tmp_hlq=self.tmphlq,
                                                     replace=True)
            self.unpack(self.src, temp_ds)
            rc = self._restore(temp_ds)
            datasets.delete(temp_ds)
        self.changed = not rc

        if not self.remote_src:
            datasets.delete(self.src)
        return

    def _list_content(self, source):
        restore_cmd = " RESTORE INDD(ARCHIVE) DS(INCL(**)) "
        cmd = " mvscmdauth --pgm=ADRDSSU --archive={0},old --args='TYPRUN=NORUN' --sysin=stdin --sysprint=*".format(source)
        rc, out, err = self.module.run_command(cmd, data=restore_cmd)
        self._get_restored_datasets(out)

    def list_archive_content(self):
        temp_ds, rc = self._create_dest_data_set(type="SEQ", record_format="U", record_length=0, tmp_hlq=self.tmphlq, replace=True)
        self.unpack(self.src, temp_ds)
        self._list_content(temp_ds)
        datasets.delete(temp_ds)
        if not self.remote_src:
            datasets.delete(self.src)

    def clean_environment(self, data_sets=None, uss_files=None, remove_targets=False):
        """Removes any allocated data sets that won't be needed after module termination.
        Arguments:
            data_sets - {list(str)} : list of data sets to remove
            uss_files - {list(str)} : list of uss files to remove
            remove_targets - bool : Indicates if already unpacked data sets need to be removed too.
        """
        if data_set is not None:
            for ds in data_sets:
                data_set.DataSet.ensure_absent(ds)
        if uss_files is not None:
            for file in uss_files:
                os.remove(file)
        if remove_targets:
            for target in self.targets:
                data_set.DataSet.ensure_absent(target)


class AMATerseUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(AMATerseUnarchive, self).__init__(module)

    def unpack(self, src, dest):
        """
        Unpacks using AMATerse, assumes the data set has only been packed once.
        """
        dds = {'args': 'UNPACK', 'sysut1': src, 'sysut2': dest}
        rc, out, err = mvs_cmd.amaterse(cmd="", dds=dds)
        if rc != 0:
            ds_remove_list = [dest, src] if not self.remote_src else [dest]
            self.clean_environment(data_sets=ds_remove_list, uss_files=[], remove_targets=True)
            self.module.fail_json(
                msg="Failed executing AMATERSE to restore {0} into {1}".format(src, dest),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        return rc


class XMITUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(XMITUnarchive, self).__init__(module)

    def unpack(self, src, dest):
        """
        Unpacks using XMIT.

        src is the archive
        dest is the destination dataset
        """
        unpack_cmd = """
        PROFILE NOPROMPT
        RECEIVE INDSN('{0}')
        DA('{1}')
        """.format(src, dest)
        rc, out, err = mvs_cmd.ikjeft01(cmd=unpack_cmd, authorized=True)
        if rc != 0:
            ds_remove_list = [dest, src] if not self.remote_src else [dest]
            self.clean_environment(data_sets=ds_remove_list, uss_files=[], remove_targets=True)
            self.module.fail_json(
                msg="Failed executing RECEIVE to restore {0} into {1}".format(src, dest),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        return rc


def get_unarchive_handler(module):
    format = module.params.get("format").get("name")
    if format in ["tar", "gz", "bz2", "pax"]:
        return TarUnarchive(module)
    elif format == "terse":
        return AMATerseUnarchive(module)
    elif format == "xmit":
        return XMITUnarchive(module)
    return ZipUnarchive(module)


def tar_filter(member, dest_path):
    name = member.name
    if name.startswith(('/', os.sep)):
        name = member.path.lstrip('/' + os.sep)
    if os.path.isabs(name):
        raise AbsolutePathError
    target_path = os.path.realpath(os.path.join(validation.validate_safe_path(dest_path), validation.validate_safe_path(name)))
    if os.path.commonpath([target_path, dest_path]) != dest_path:
        raise OutsideDestinationError(member, target_path)
    if member.islnk() or member.issym():
        if os.path.isabs(member.linkname):
            raise AbsoluteLinkError(member)
        target_path = os.path.realpath(os.path.join(validation.validate_safe_path(dest_path), validation.validate_safe_path(member.linkname)))
        if os.path.commonpath([target_path, dest_path]) != dest_path:
            raise LinkOutsideDestinationError(member, target_path)


def zip_filter(member, dest_path):
    name = member.filename
    if name.startswith(('/', os.sep)):
        name = name.lstrip('/' + os.sep)
    if os.path.isabs(name):
        raise AbsolutePathError
    target_path = os.path.realpath(os.path.join(validation.validate_safe_path(dest_path), validation.validate_safe_path(name)))
    if os.path.commonpath([target_path, dest_path]) != dest_path:
        raise OutsideDestinationError(member, target_path)


def sanitize_members(members, dest, format):
    """
    Filter inspired by (PEP 706)
        - Refuse to extract any absolute path
        - Refuse to extract any member with leading '/'
    """
    dest_path = os.path.realpath(dest)
    for member in members:
        if format == 'zip':
            zip_filter(member, dest_path)
        else:
            tar_filter(member, dest_path)
    return members


class AbsolutePathError(Exception):
    def __init__(self, tarinfo):
        self.msg = "Unable to extract {0} as the files extracted can not contain an absolute path".format(tarinfo.name)
        super().__init__(self.msg)


class OutsideDestinationError(Exception):
    def __init__(self, tarinfo, path):
        self.msg = 'Unable to extract {0} to {1}, which is outside the designated destination'.format(tarinfo.name, path)
        super().__init__(self.msg)


class AbsoluteLinkError(Exception):
    def __init__(self, tarinfo):
        self.msg = '{0} is a symlink to an absolute path'.format(tarinfo.name)
        super().__init__(self.msg)


class LinkOutsideDestinationError(Exception):
    def __init__(self, tarinfo, path):
        self.msg = 'Unable to extract {0} it would link to {1}, which is outside the designated destination'.format(tarinfo.name, path)
        super().__init__()


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='str', required=True),
            dest=dict(type='str'),
            include=dict(type='list', elements='str'),
            exclude=dict(type='list', elements='str'),
            list=dict(type='bool', default=False),
            format=dict(
                type='dict',
                required=True,
                options=dict(
                    name=dict(
                        type='str',
                        required=True,
                        choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                    ),
                    format_options=dict(
                        type='dict',
                        required=False,
                        options=dict(
                            xmit_log_data_set=dict(
                                type='str',
                                required=False,
                            ),
                            dest_volumes=dict(
                                type='list',
                                elements='str',
                            ),
                            use_adrdssu=dict(
                                type='bool',
                                default=False,
                            )
                        )
                    ),
                ),
            ),
            group=dict(type='str'),
            mode=dict(type='str'),
            owner=dict(type='str'),
            dest_data_set=dict(
                type='dict',
                required=False,
                options=dict(
                    name=dict(
                        type='str', required=False,
                    ),
                    type=dict(
                        type='str',
                        choices=['SEQ', 'PDS', 'PDSE'],
                        required=False,
                        default='SEQ',
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
            tmp_hlq=dict(type='str'),
            force=dict(type='bool', default=False),
            remote_src=dict(type='bool', default=False),
        ),
        mutually_exclusive=[
            ['include', 'exclude'],
        ],
        supports_check_mode=True,
    )

    arg_defs = dict(
        src=dict(type='str', required=True),
        dest=dict(type='str', required=False, default=''),
        include=dict(type='list', elements='str'),
        exclude=dict(type='list', elements='str'),
        list=dict(type='bool', default=False),
        format=dict(
            type='dict',
            required=True,
            options=dict(
                name=dict(
                    type='str',
                    required=True,
                    default='gz',
                    choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                ),
                format_options=dict(
                    type='dict',
                    required=False,
                    options=dict(
                        xmit_log_data_set=dict(
                            type='str',
                            required=False,
                        ),
                        dest_volumes=dict(
                            type='list',
                            elements='str'
                        ),
                        use_adrdssu=dict(
                            type='bool',
                            default=False,
                        ),
                    ),
                    default=dict(xmit_log_data_set=""),
                )
            ),
            default=dict(name="", format_options=dict(xmit_log_data_set="")),
        ),
        dest_data_set=dict(
            arg_type='dict',
            required=False,
            options=dict(
                name=dict(arg_type='str', required=False),
                type=dict(arg_type='str', required=False, default="SEQ"),
                space_primary=dict(arg_type='int', required=False),
                space_secondary=dict(
                    arg_type='int', required=False),
                space_type=dict(arg_type='str', required=False),
                record_format=dict(
                    arg_type='str', required=False),
                record_length=dict(type='int', required=False),
                block_size=dict(arg_type='int', required=False),
                directory_blocks=dict(arg_type="int", required=False),
                key_offset=dict(arg_type="int", required=False),
                key_length=dict(arg_type="int", required=False),
                sms_storage_class=dict(arg_type="str", required=False),
                sms_data_class=dict(arg_type="str", required=False),
                sms_management_class=dict(arg_type="str", required=False),
            )
        ),
        group=dict(type='str'),
        mode=dict(type='str'),
        owner=dict(type='str'),
        tmp_hlq=dict(type='qualifier_or_empty', default=''),
        force=dict(type='bool', default=False),
        remote_src=dict(type='bool', default=False),
        mutually_exclusive=[
            ['include', 'exclude'],
        ],
    )

    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))
    unarchive = get_unarchive_handler(module)

    if unarchive.list:
        unarchive.list_archive_content()
        module.exit_json(**unarchive.result)

    if not unarchive.src_exists():
        module.fail_json(msg="{0} does not exists, please provide a valid src.".format(module.params.get("src")))

    unarchive.extract_src()

    if unarchive.dest_unarchived() and unarchive.dest_type() == "USS":
        unarchive.update_permissions()

    module.exit_json(**unarchive.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
