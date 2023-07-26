#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023
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
module: zos_archive
version_added: "1.7.0"
author:
  - Oscar Fernando Flores Garcia (@fernandofloresg)
short_description: Archive files and data sets on z/OS.

description:
  - Create or extend an archive on a remote z/OS system.
  - Sources for archiving must be on the remote z/OS system.
  - Supported sources are USS (UNIX System Services) or z/OS data sets.
  - The archive remains on the remote z/OS system.
  - For supported archive formats, see option C(format).

options:
  src:
    description:
      - List of names or globs of UNIX System Services (USS) files,
        PS (sequential data sets), PDS, PDSE to compress or archive.
      - USS file paths should be absolute paths.
      - "MVS data sets supported types are: C(SEQ), C(PDS), C(PDSE)."
      - VSAMs are not supported.
    type: list
    required: true
    elements: str
  format:
    description:
      - The compression type and corresponding options to use when archiving
        data.
    type: dict
    required: false
    suboptions:
      name:
        description:
          - The compression format to use.
        type: str
        required: false
        default: gz
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
          terse_pack:
            description:
              - Compression option for use with the terse format,
                I(name=terse).
              - Pack will compress records in a data set so that the output
                results in lossless data compression.
              - Spack will compress records in a data set so the output results
                in complex data compression.
              - Spack will produce smaller output and take approximately 3
                times longer than pack compression.
            type: str
            required: false
            choices:
              - PACK
              - SPACK
          xmit_log_data_set:
            description:
              - Provide the name of a data set to store xmit log output.
              - If the data set provided does not exist, the program
                will create it.
              - "If the data set provided exists, the data set must have
                the following attributes: LRECL=255, BLKSIZE=3120, and
                RECFM=VB"
              - When providing the I(xmit_log_data_set) name, ensure there
                is adequate space.
            type: str
          use_adrdssu:
            description:
              - If set to true, the C(zos_archive) module will use Data
                Facility Storage Management Subsystem data set services
                (DFSMSdss) program ADRDSSU to compress data sets into a
                portable format before using C(xmit) or C(terse).
            type: bool
            default: false
  dest:
    description:
      - The remote absolute path or data set where the archive should be
        created.
      - I(dest) can be a USS file or MVS data set name.
      - If I(dest) has missing parent directories, they will be created.
      - If I(dest) is a nonexistent USS file, it will be created.
      - Destination data set attributes can be set using I(dest_data_set).
    type: str
    required: true
  exclude:
    description:
      - Remote absolute path, glob, or list of paths, globs or data set name
        patterns for the file, files or data sets to exclude from path list
        and glob expansion.
      - "Patterns (wildcards) can contain one of the following, `?`, `*`."
      - "* matches everything."
      - "? matches any single character."
    type: list
    required: false
    elements: str
  group:
    description:
      - Name of the group that will own the archive file.
      - When left unspecified, it uses the current group of the current use
        unless you are root, in which case it can preserve the previous
        ownership.
      - This option is only applicable if C(dest) is USS, otherwise ignored.
    type: str
    required: false
  mode:
    description:
      - The permission of the destination archive file.
      - If C(dest) is USS, this will act as Unix file mode, otherwise
        ignored.
      - It should be noted that modes are octal numbers.
        The user must either add a leading zero so that Ansible's YAML
        parser knows it is an octal number (like C(0644) or C(01777))or
        quote it (like C('644') or C('1777')) so Ansible receives a string
        and can do its own conversion from string into number. Giving Ansible
        a number without following one of these rules will end up with a
        decimal number which will have unexpected results.
      - The mode may also be specified as a symbolic mode
        (for example, 'u+rwx' or 'u=rw,g=r,o=r') or a special
        string 'preserve'.
      - I(mode=preserve) means that the file will be given the same permissions
        as the source file.
    type: str
    required: false
  owner:
    description:
      - Name of the user that should own the archive file, as would be
        passed to the chown command.
      - When left unspecified, it uses the current user unless you are root,
        in which case it can preserve the previous ownership.
      - This option is only applicable if C(dest) is USS, otherwise ignored.
    type: str
    required: false
  remove:
    description:
      - Remove any added source files , trees or data sets after module
        L(zos_archive,./zos_archive.html) adds them to the archive.
        Source files, trees and data sets are identified with option I(path).
    type: bool
    required: false
    default: false
  dest_data_set:
    description:
      - Data set attributes to customize a C(dest) data set to be archived into.
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
      - The default HLQ is the Ansible user used to execute the module and
        if that is not available, then the environment variable value
        C(TMPHLQ) is used.
    required: false
    type: str
  force:
    description:
      - If set to C(true) and the remote file or data set C(dest) will be
        deleted. Otherwise it will be created with the C(dest_data_set)
        attributes or default values if C(dest_data_set) is not specified.
      - If set to C(false), the file or data set will only be copied if the
        destination does not exist.
      - If set to C(false) and destination exists, the module exits with a
        note to the user.
    type: bool
    default: false
    required: false

notes:
  - This module does not perform a send or transmit operation to a remote
    node. If you want to transport the archive you can use zos_fetch to
    retrieve to the controller and then zos_copy or zos_unarchive for
    copying to a remote or send to the remote and then unpack the archive
    respectively.
  - When packing and using C(use_adrdssu) flag the module will take up to two
    times the space indicated in C(dest_data_set).


seealso:
  - module: zos_fetch
  - module: zos_unarchive
'''

EXAMPLES = r'''
# Simple archive
- name: Archive file into a tar
  zos_archive:
    path: /tmp/archive/foo.txt
    dest: /tmp/archive/foo_archive_test.tar
    format:
      name: tar

# Archive multiple files
- name: Compress list of files into a zip
  zos_archive:
    path:
      - /tmp/archive/foo.txt
      - /tmp/archive/bar.txt
    dest: /tmp/archive/foo_bar_archive_test.zip
    format:
    name: zip

# Archive one data set into terse
- name: Compress data set into a terse
  zos_archive:
    path: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse

# Use terse with different options
- name: Compress data set into a terse, specify pack algorithm and use adrdssu
  zos_archive:
    path: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse
      format_options:
        terse_pack: "SPACK"
        use_adrdssu: True

# Use a pattern to store
- name: Compress data set pattern using xmit
  zos_archive:
    path: "USER.ARCHIVE.*"
    exclude_sources: "USER.ARCHIVE.EXCLUDE.*"
    dest: "USER.ARCHIVE.RESULT.XMIT"
    format:
      name: xmit
'''

RETURN = r'''
state:
    description:
        - The state of the input C(src).
        - C(absent) when the source files or data sets were removed.
        - C(present) when the source files or data sets were not removed.
        - C(incomplete) when C(remove) was true and the source files or
          data sets were not removed.
    type: str
    returned: always
dest_state:
    description:
      - The state of the I(dest) file or data set.
      - C(absent) when the file does not exist.
      - C(archive) when the file is an archive.
      - C(compress) when the file is compressed, but not an archive.
      - C(incomplete) when the file is an archive, but some files under
        I(path) were not found.
    type: str
    returned: success
missing:
    description: Any files or data sets that were missing from the source.
    type: list
    returned: success
archived:
    description:
    - Any files or data sets that were compressed or added to the
      archive.
    type: list
    returned: success
arcroot:
    description:
      - If C(src) is a list of USS files, this returns the top most parent
        folder of the list of files, otherwise is empty.
    type: str
    returned: always
expanded_sources:
    description: The list of matching paths from the src option.
    type: list
    returned: always
expanded_exclude_sources:
    description: The list of matching exclude paths from the exclude option.
    type: list
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
    mvs_cmd)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)
import os
import tarfile
import zipfile
import abc
import glob
import re


try:
    from zoautil_py import datasets
except Exception:
    Datasets = MissingZOAUImport()

XMIT_RECORD_LENGTH = 80
AMATERSE_RECORD_LENGTH = 1024

STATE_ABSENT = 'absent'
STATE_ARCHIVE = 'archive'
STATE_COMPRESSED = 'compressed'
STATE_INCOMPLETE = 'incomplete'


def get_archive_handler(module):
    """
    Return the proper archive handler based on archive format.
    Arguments:
        format: {str}
    Returns:
        Archive: {Archive}

    """
    format = module.params.get("format").get("name")
    if format in ["tar", "gz", "bz2", "pax"]:
        return TarArchive(module)
    elif format == "terse":
        return AMATerseArchive(module)
    elif format == "xmit":
        return XMITArchive(module)
    return ZipArchive(module)


def strip_prefix(prefix, string):
    return string[len(prefix):] if string.startswith(prefix) else string


def expand_paths(paths):
    expanded_path = []
    for path in paths:
        if '*' in path or '?' in path:
            e_paths = glob.glob(path)
        else:
            e_paths = [path]
        expanded_path.extend(e_paths)
    return expanded_path


def is_archive(path):
    return re.search(r'\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip|gz|bz2|xz|pax)$', os.path.basename(path), re.IGNORECASE)


class Archive():
    def __init__(self, module):
        self.module = module
        self.dest = module.params['dest']
        self.format = module.params.get("format").get("name")
        self.remove = module.params['remove']
        self.changed = False
        self.errors = []
        self.found = []
        self.targets = []
        self.archived = []
        self.not_found = []
        self.force = module.params['force']
        self.sources = module.params['src']
        self.arcroot = ""
        self.expanded_sources = ""
        self.expanded_exclude_sources = ""
        self.dest_state = STATE_ABSENT

    def targets_exist(self):
        return bool(self.targets)

    @abc.abstractmethod
    def dest_exists(self):
        pass

    @abc.abstractmethod
    def dest_type(self):
        pass

    @abc.abstractmethod
    def update_permissions(self):
        return

    @abc.abstractmethod
    def find_targets(self):
        pass

    @abc.abstractmethod
    def _get_checksums(self, path):
        pass

    @abc.abstractmethod
    def dest_checksums(self):
        pass

    @abc.abstractmethod
    def is_different_from_original(self):
        pass

    @abc.abstractmethod
    def remove_targets(self):
        pass

    @property
    def result(self):
        return {
            'archived': self.archived,
            'dest': self.dest,
            'arcroot': self.arcroot,
            'dest_state': self.dest_state,
            'changed': self.changed,
            'missing': self.not_found,
            'expanded_sources': list(self.expanded_sources),
            'expanded_exclude_sources': list(self.expanded_exclude_sources),
        }


class USSArchive(Archive):
    def __init__(self, module):
        super(USSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        if len(self.sources) == 1:
            self.arcroot = os.path.dirname(os.path.commonpath(self.sources))
        else:
            self.arcroot = os.path.commonpath(self.sources)
        self.expanded_sources = expand_paths(self.sources)
        self.expanded_exclude_sources = expand_paths(module.params['exclude'])
        self.expanded_exclude_sources = "" if len(self.expanded_exclude_sources) == 0 else self.expanded_exclude_sources

        self.sources = sorted(set(self.expanded_sources) - set(self.expanded_exclude_sources))

    def dest_exists(self):
        return os.path.exists(self.dest)

    def dest_type(self):
        return "USS"

    def update_permissions(self):
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.dest)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    def find_targets(self):
        for path in self.sources:
            if os.path.exists(path):
                self.targets.append(path)
            else:
                self.not_found.append(path)

    def _get_checksums(self, path):
        md5_cmd = "md5 -r \"{0}\"".format(path)
        rc, out, err = self.module.run_command(md5_cmd)
        checksums = out.split(" ")[0]
        return checksums

    def dest_checksums(self):
        if self.dest_exists():
            return self._get_checksums(self.dest)
        return None

    def is_different_from_original(self):
        if self.original_checksums is not None:
            return self.original_checksums != self.dest_checksums()
        return True

    def remove_targets(self):
        for target in self.archived:
            if os.path.isdir(target):
                os.removedirs(target)
            else:
                os.remove(target)

    def archive_targets(self):
        self.file = self.open(self.dest)

        try:
            for target in self.targets:
                if os.path.isdir(target):
                    for directory_path, directory_names, file_names in os.walk(target, topdown=True):
                        for directory_name in directory_names:
                            full_path = os.path.join(directory_path, directory_name)
                            self.add(full_path, strip_prefix(self.arcroot, full_path))

                        for file_name in file_names:
                            full_path = os.path.join(directory_path, file_name)
                            self.add(full_path, strip_prefix(self.arcroot, full_path))
                else:
                    self.add(target, strip_prefix(self.arcroot, target))
        except Exception as e:
            self.dest_state = STATE_INCOMPLETE
            if self.format == 'tar':
                archive_format = self.format
            else:
                archive_format = 'tar.' + self.format
            self.module.fail_json(
                msg='Error when writing %s archive at %s: %s' % (
                    archive_format, self.destination, e
                ),
                exception=e
            )
        self.file.close()

    def add(self, source, arcname):
        self._add(source, arcname)
        self.archived.append(source)

    def get_state(self):
        if not self.dest_exists():
            self.dest_state = STATE_ABSENT
        else:
            if is_archive(self.dest):
                self.dest_state = STATE_ARCHIVE
            if bool(self.not_found):
                self.dest_state = STATE_INCOMPLETE


class TarArchive(USSArchive):
    def __init__(self, module):
        super(TarArchive, self).__init__(module)

    def open(self, path):
        if self.format == 'tar':
            file = tarfile.open(path, 'w')
        elif self.format == 'pax':
            file = tarfile.open(path, 'w', format=tarfile.GNU_FORMAT)
        elif self.format in ('gz', 'bz2'):
            file = tarfile.open(path, 'w|' + self.format)
        return file

    def _add(self, source, arcname):
        self.file.add(source, arcname)


class ZipArchive(USSArchive):
    def __init__(self, module):
        super(ZipArchive, self).__init__(module)

    def open(self, path):
        try:
            file = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, True)
        except zipfile.BadZipFile:
            self.module.fail_json(
                msg="Improperly compressed zip file, unable to to open file {0} ".format(path)
            )
        return file

    def _add(self, source, arcname):
        self.file.write(source, arcname)


class MVSArchive(Archive):
    def __init__(self, module):
        super(MVSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        self.use_adrdssu = module.params.get("format").get("format_options").get("use_adrdssu")
        self.expanded_sources = self.expand_mvs_paths(self.sources)
        self.expanded_exclude_sources = self.expand_mvs_paths(module.params['exclude'])
        self.sources = sorted(set(self.expanded_sources) - set(self.expanded_exclude_sources))
        self.tmp_data_sets = list()
        self.dest_data_set = module.params.get("dest_data_set")
        self.dest_data_set = dict() if self.dest_data_set is None else self.dest_data_set
        self.tmphlq = module.params.get("tmp_hlq")

    def open(self):
        pass

    def close(self):
        pass

    def find_targets(self):
        """
        Finds target datasets in host.
        """
        for path in self.sources:
            if data_set.DataSet.data_set_exists(path):
                self.targets.append(path)
            else:
                self.not_found.append(path)

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
        default_size = 5
        dest_space_type = 'M'
        dest_primary_space = int(default_size)
        return dest_primary_space, dest_space_type

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
                rc, hlq, err = self.module.run_command("hlq")
                hlq = hlq.replace('\n', '')
            cmd = "mvstmphelper {0}.DZIP".format(hlq)
            rc, temp_ds, err = self.module.run_command(cmd)
            arguments.update(name=temp_ds.replace('\n', ''))

        if record_format is None:
            arguments.update(record_format="FB")
        if record_length is None:
            arguments.update(record_length=80)
        if type is None:
            arguments.update(type="SEQ")
        if space_primary is None:
            arguments.update(space_primary=5)
        if space_secondary is None:
            arguments.update(space_secondary=3)
        if space_type is None:
            arguments.update(space_type="M")
        arguments.pop("self")
        changed = data_set.DataSet.ensure_present(**arguments)
        return arguments["name"], changed

    def create_dest_ds(self, name):
        """
        Create destination data set to use as an archive.
        Arguments:
            name: {str}
        Returns:
            name {str} - name of the newly created data set.
        """
        record_length = XMIT_RECORD_LENGTH if self.format == "xmit" else AMATERSE_RECORD_LENGTH
        changed = data_set.DataSet.ensure_present(name=name, replace=True, type='SEQ', record_format='FB', record_length=record_length)
        # cmd = "dtouch -rfb -tseq -l{0} {1}".format(record_length, name)
        # rc, out, err = self.module.run_command(cmd)

        # if not changed:
        #     self.module.fail_json(
        #         msg="Failed preparing {0} to be used as an archive".format(name),
        #         stdout=out,
        #         stderr=err,
        #         stdout_lines=cmd,
        #         rc=rc,
        #     )
        return name

    def dump_into_temp_ds(self, temp_ds):
        """
        Dump src datasets identified as self.targets into a temporary dataset using ADRDSSU.
        """
        dump_cmd = """ DUMP OUTDDNAME(TARGET) -
         OPTIMIZE(4) DS(INCL( - """

        for target in self.targets:
            dump_cmd += "\n {0}, - ".format(target)
        dump_cmd += '\n ) '

        if self.force:
            dump_cmd += '- \n ) TOL( ENQF IOER ) '

        dump_cmd += ' )'
        dds = dict(target="{0},old".format(temp_ds))
        rc, out, err = mvs_cmd.adrdssu(cmd=dump_cmd, dds=dds, authorized=True)

        if rc != 0:
            self.module.fail_json(
                msg="Failed executing ADRDSSU to archive {0}".format(temp_ds),
                stdout=out,
                stderr=err,
                stdout_lines=dump_cmd,
                rc=rc,
            )
        return rc

    def _get_checksums(self, path):
        md5_cmd = "md5 -r \"//'{0}'\"".format(path)
        rc, out, err = self.module.run_command(md5_cmd)
        checksums = out.split(" ")[0]
        return checksums

    def dest_checksums(self):
        if self.dest_exists():
            return self._get_checksums(self.dest)
        return None

    def is_different_from_original(self):
        if self.original_checksums is not None:
            return self.original_checksums != self.dest_checksums()
        return True

    def dest_type(self):
        return "MVS"

    def dest_exists(self):
        return data_set.DataSet.data_set_exists(self.dest)

    def remove_targets(self):
        for target in self.archived:
            data_set.DataSet.ensure_absent(target)
        return

    def expand_mvs_paths(self, paths):
        expanded_path = []
        for path in paths:
            if '*' in path:
                e_paths = datasets.listing(path)
                e_paths = [path.name for path in e_paths]
            else:
                e_paths = [path]
            expanded_path.extend(e_paths)
        return expanded_path

    def get_state(self):
        if not self.dest_exists():
            self.dest_state = STATE_ABSENT
        else:
            if bool(self.not_found):
                self.dest_state = STATE_INCOMPLETE
            elif bool(self.archived):
                self.dest_state = STATE_ARCHIVE

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


class AMATerseArchive(MVSArchive):
    def __init__(self, module):
        super(AMATerseArchive, self).__init__(module)
        self.pack_arg = module.params.get("format").get("format_options").get("terse_pack")
        if self.pack_arg is None:
            self.pack_arg = "SPACK"

    def add(self, src, archive):
        """
        Archive src into archive using AMATERSE program.
        Arguments:
            src: {str}
            archive: {str}
        """
        dds = {'args': self.pack_arg, 'sysut1': src, 'sysut2': archive}
        rc, out, err = mvs_cmd.amaterse(cmd="", dds=dds)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing AMATERSE to archive {0} into {1}".format(src, archive),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        self.archived = self.targets[:]
        return rc

    def archive_targets(self):
        """
        Add MVS Datasets to the AMATERSE Archive by creating a temporary dataset and dumping the source datasets into it.
        """
        if self.use_adrdssu:
            source, changed = self._create_dest_data_set(
                type="SEQ",
                record_format="U",
                record_length=0,
                tmp_hlq=self.tmphlq,
                replace=True,
                space_primary=self.dest_data_set.get("space_primary"),
                space_type=self.dest_data_set.get("space_type"))
            self.dump_into_temp_ds(source)
            self.tmp_data_sets.append(source)
        else:
            # If we don't use a adrdssu container we cannot pack multiple data sets
            if len(self.targets) > 1:
                self.module.fail_json(
                    msg="To archive multiple source data sets, you must use option 'use_adrdssu=True'.")
            source = self.targets[0]
        # dest = self.create_dest_ds(self.dest)
        dest, changed = self._create_dest_data_set(
            name=self.dest,
            replace=True,
            type='SEQ',
            record_format='FB',
            record_length=AMATERSE_RECORD_LENGTH,
            space_primary=self.dest_data_set.get("space_primary"),
            space_type=self.dest_data_set.get("space_type"))
        self.changed = self.changed or changed
        self.add(source, dest)
        self.clean_environment(data_sets=self.tmp_data_sets)


class XMITArchive(MVSArchive):
    def __init__(self, module):
        super(XMITArchive, self).__init__(module)
        self.xmit_log_data_set = module.params.get("format").get("format_options").get("xmit_log_data_set")

    def add(self, src, archive):
        """
        Archive src into archive using TSO XMIT.
        Arguments:
            src: {str}
            archive: {str}
        """
        log_option = "LOGDSNAME({0})".format(self.xmit_log_data_set) if self.xmit_log_data_set else "NOLOG"
        xmit_cmd = """ XMIT A.B -
        FILE(SYSUT1) OUTFILE(SYSUT2) -
        {0} -
        """.format(log_option)
        dds = {"SYSUT1": "{0},shr".format(src), "SYSUT2": archive}
        rc, out, err = mvs_cmd.ikjeft01(cmd=xmit_cmd, authorized=True, dds=dds)
        if rc != 0:
            self.module.fail_json(
                msg="An error occurred while executing 'TSO XMIT' to archive {0} into {1}".format(src, archive),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        self.archived = self.targets[:]
        return rc

    def archive_targets(self):
        """
        Adds MVS Datasets to the TSO XMIT Archive by creating a temporary dataset and dumping the source datasets into it.
        """
        if self.use_adrdssu:
            source, changed = self._create_dest_data_set(
                type="SEQ",
                record_format="U",
                record_length=0,
                tmp_hlq=self.tmphlq,
                replace=True,
                space_primary=self.dest_data_set.get("space_primary"),
                space_type=self.dest_data_set.get("space_type"))
            self.dump_into_temp_ds(source)
            self.tmp_data_sets.append(source)
        else:
            # If we don't use a adrdssu container we cannot pack multiple data sets
            if len(self.sources) > 1:
                self.module.fail_json(
                    msg="To archive multiple source data sets, you must use option 'use_adrdssu=True'.")
            source = self.sources[0]
        # dest = self.create_dest_ds(self.dest)
        dest, changed = self._create_dest_data_set(
            name=self.dest,
            replace=True,
            type='SEQ',
            record_format='FB',
            record_length=XMIT_RECORD_LENGTH,
            space_primary=self.dest_data_set.get("space_primary"),
            space_type=self.dest_data_set.get("space_type"))
        self.changed = self.changed or changed
        self.add(source, dest)
        self.clean_environment(data_sets=self.tmp_data_sets)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            src=dict(type='list', elements='str', required=True),
            dest=dict(type='str', required=True),
            exclude=dict(type='list', elements='str'),
            format=dict(
                type='dict',
                options=dict(
                    name=dict(
                        type='str',
                        default='gz',
                        choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                    ),
                    format_options=dict(
                        type='dict',
                        required=False,
                        options=dict(
                            terse_pack=dict(
                                type='str',
                                choices=['PACK', 'SPACK'],
                            ),
                            xmit_log_data_set=dict(
                                type='str',
                            ),
                            use_adrdssu=dict(
                                type='bool',
                                default=False,
                            )
                        ),
                    ),
                )
            ),
            group=dict(type='str'),
            mode=dict(type='str'),
            owner=dict(type='str'),
            remove=dict(type='bool', default=False),
            dest_data_set=dict(
                type='dict',
                required=False,
                options=dict(
                    name=dict(
                        type='str', required=False,
                    ),
                    type=dict(
                        type='str',
                        choices=['SEQ'],
                        required=False,
                        default="SEQ",
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
                    sms_storage_class=dict(type="str", required=False),
                    sms_data_class=dict(type="str", required=False),
                    sms_management_class=dict(type="str", required=False),
                )
            ),
            tmp_hlq=dict(type='str'),
            force=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )

    arg_defs = dict(
        src=dict(type='list', elements='str', required=True),
        dest=dict(type='str', required=True),
        exclude=dict(type='list', elements='str', default=[]),
        format=dict(
            type='dict',
            options=dict(
                name=dict(
                    type='str',
                    default='gz',
                    choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                ),
                format_options=dict(
                    type='dict',
                    required=False,
                    options=dict(
                        terse_pack=dict(
                            type='str',
                            required=False,
                            choices=['PACK', 'SPACK'],
                        ),
                        xmit_log_data_set=dict(
                            type='str',
                            required=False,
                        ),
                        use_adrdssu=dict(
                            type='bool',
                            default=False,
                        )
                    ),
                    default=dict(
                        terse_pack="SPACK",
                        xmit_log_data_set="",
                        use_adrdssu=False),
                ),
            ),
            default=dict(
                name="",
                format_options=dict(
                    terse_pack="SPACK",
                    xmit_log_data_set="",
                    use_adrdssu=False
                )
            ),
        ),
        group=dict(type='str'),
        mode=dict(type='str'),
        owner=dict(type='str'),
        remove=dict(type='bool', default=False),
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
                sms_storage_class=dict(arg_type="str", required=False),
                sms_data_class=dict(arg_type="str", required=False),
                sms_management_class=dict(arg_type="str", required=False),
            )
        ),
        tmp_hlq=dict(type='qualifier_or_empty', default=''),
        force=dict(type='bool', default=False)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )
    if module.check_mode:
        module.exit_json(**result)

    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    archive = get_archive_handler(module)

    if archive.dest_exists() and not archive.force:
        module.fail_json(msg="%s file exists. Use force flag to replace dest" % archive.dest)

    archive.find_targets()
    if archive.targets_exist():
        archive.archive_targets()
        if archive.remove:
            archive.remove_targets()
    if archive.dest_exists():
        if archive.dest_type() == "USS":
            archive.update_permissions()
        archive.changed = archive.is_different_from_original()
    archive.get_state()

    module.exit_json(**archive.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
