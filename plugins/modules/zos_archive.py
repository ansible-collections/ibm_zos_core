#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2022
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
short_description: Archive a dataset on z/OS.

description:
  - Creates or extends an archive.
  - The source and archive are on the remote host,
    and the archive is not copied to the local host.

options:
  path:
    description:
      - Remote absolute path, glob, or list of paths or globs for the file or files to compress or archive.
    type: list
    required: true
    elements: str
  format:
    description:
      - The type of compression to use.
    type: dict
    required: false
    suboptions:
      name:
        description:
          - The name of the format to use.
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
          - Options specific to each format.
        type: dict
        required: false
        suboptions:
          terse_pack:
            description: Pack option to use for terse format.
            type: str
            choices:
              - PACK
              - SPACK
          xmit_log_dataset:
            description: Provide a name of data set to use for xmit log.
            type: str
          use_adrdssu:
            description:
              - If set to true, after unpacking a data set in C(xmit) or C(terse) format
                it will perform a single DFSMSdss ADRDSSU DUMP step.
            type: bool
            default: False
  dest:
    description: The file name of the dest archive.
    type: str
    required: false
  exclude_path:
    description:
        - Remote absolute path, glob, or list of paths, globs or data set name patterns for the file, files or data sets to exclude
           from path list and glob expansion.
    type: list
    required: false
    elements: str
  group:
    description:
      - Name of the group that should own the filesystem object, as would be fed to chown.
      - When left unspecified, it uses the current group of the current user unless you are root,
        in which case it can preserve the previous ownership.
    type: str
    required: false
  mode:
    description:
      - The permissions the resulting filesystem object should have.
    type: str
    required: false
  owner:
    description:
      - Name of the user that should own the filesystem object, as would be fed to chown.
      - When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.
    type: str
    required: false
  exclusion_patterns:
    description:
      - Glob style patterns to exclude files or directories from the resulting archive.
      - This differs from I(exclude_path) which applies only to the source paths from I(path).
    type: list
    elements: str
    required: false
  remove:
    description:
      - Remove any added source files and trees after adding to archive.
    type: bool
    required: false
    default: false
  tmp_hlq:
    description:
      - High Level Qualifier used for temporary datasets.
    type: str
    required: false
  force:
    description:
      - Create the dest archive file even if it already exists.
    type: bool
    required: false
    default: false
'''

EXAMPLES = r'''
# Simple archive
- name: Archive file into tar
  zos_archive:
    path: /tmp/archive/foo.txt
    dest: /tmp/archive/foo_archive_test.tar
    format:
      name: tar

# Archive multiple files
- name: Compress list of files into zip
  zos_archive:
    path:
      - /tmp/archive/foo.txt
      - /tmp/archive/bar.txt
    dest: /tmp/archive/foo_bar_archive_test.zip
    format:
    name: zip

# Archive one data set into terse
- name: Compress data set into terse
  zos_archive:
    path: "USER.ARCHIVE.TEST"
    dest: "USER.ARCHIVE.RESULT.TRS"
    format:
      name: terse

# Usae terse with different options
- name: Compress data set into terse, specify pack algorithm and use adrdssu
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
    exclude_paths: "USER.ARCHIVE.EXCLUDE.*"
    dest: "USER.ARCHIVE.RESULT.XMIT"
    format:
      name: xmit
'''

RETURN = r'''
state:
    description:
        The state of the input C(path).
    type: str
    returned: always
dest_state:
    description:
      - The state of the I(dest) file.
      - C(absent) when the file does not exist.
      - C(archive) when the file is an archive.
      - C(compress) when the file is compressed, but not an archive.
      - C(incomplete) when the file is an archive, but some files under I(path) were not found.
    type: str
    returned: success
missing:
    description: Any files that were missing from the source.
    type: list
    returned: success
archived:
    description: Any files that were compressed or added to the archive.
    type: list
    returned: success
arcroot:
    description: The archive root.
    type: str
    returned: always
expanded_paths:
    description: The list of matching paths from paths argument.
    type: list
    returned: always
expanded_exclude_paths:
    description: The list of matching exclude paths from the exclude_path argument.
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
        self.exclusion_patterns = module.params['exclusion_patterns'] or []
        self.format = module.params.get("format").get("name")
        self.remove = module.params['remove']
        self.tmp_hlq = module.params['tmp_hlq']
        self.changed = False
        self.errors = []
        self.found = []
        self.targets = []
        self.archived = []
        self.not_found = []
        self.force = module.params['force']
        self.paths = module.params['path']
        self.arcroot = ""
        self.expanded_paths = ""
        self.expanded_exclude_paths = ""
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

    def get_state(self):
        if not self.dest_exists():
            self.dest_state = STATE_ABSENT
        else:
            if is_archive(self.dest):
                self.dest_state = STATE_ARCHIVE
            if bool(self.not_found):
                self.dest_state = STATE_INCOMPLETE

    @property
    def result(self):
        return {
            'archived': self.archived,
            'dest': self.dest,
            'arcroot': self.arcroot,
            'dest_state': self.dest_state,
            'changed': self.changed,
            'missing': self.not_found,
            'expanded_paths': list(self.expanded_paths),
            'expanded_exclude_paths': list(self.expanded_exclude_paths),
        }


class USSArchive(Archive):
    def __init__(self, module):
        super(USSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        if len(self.paths) == 1:
            self.arcroot = os.path.dirname(os.path.commonpath(self.paths))
        else:
            self.arcroot = os.path.commonpath(self.paths)
        self.expanded_paths = expand_paths(self.paths)
        self.expanded_exclude_paths = expand_paths(module.params['exclude_path'])
        self.expanded_exclude_paths = "" if len(self.expanded_exclude_paths) == 0 else self.expanded_exclude_paths

        self.paths = sorted(set(self.expanded_paths) - set(self.expanded_exclude_paths))

    def dest_exists(self):
        return os.path.exists(self.dest)

    def dest_type(self):
        return "USS"

    def update_permissions(self):
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.dest)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    def find_targets(self):
        for path in self.paths:
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
            self.state = STATE_INCOMPLETE
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
                msg="Bad zip file error when trying to open file {0} ".format(path)
            )
        return file

    def _add(self, source, arcname):
        self.file.write(source, arcname)


class MVSArchive(Archive):
    def __init__(self, module):
        super(MVSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        self.use_adrdssu = module.params.get("format").get("format_options").get("use_adrdssu")
        self.expanded_paths = self.expand_mvs_paths(self.paths)
        self.expanded_exclude_paths = self.expand_mvs_paths(module.params['exclude_path'])
        self.paths = sorted(set(self.expanded_paths) - set(self.expanded_exclude_paths))

    def open(self):
        pass

    def close(self):
        pass

    def find_targets(self):
        """
        Finds target datasets in host.
        """
        for path in self.paths:
            if data_set.DataSet.data_set_exists(path):
                self.targets.append(path)
            else:
                self.not_found.append(path)

    def prepare_temp_ds(self, tmphlq):
        """
        Creates a temporary sequential dataset.
        Arguments:
            tmphlq: {str}
        """
        if tmphlq:
            hlq = tmphlq
        else:
            rc, hlq, err = self.module.run_command("hlq")
            hlq = hlq.replace('\n', '')
        cmd = "mvstmphelper {0}.DZIP".format(hlq)
        rc, temp_ds, err = self.module.run_command(cmd)
        temp_ds = temp_ds.replace('\n', '')
        changed = data_set.DataSet.ensure_present(name=temp_ds, replace=True, type='SEQ', record_format='U')
        return temp_ds

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


class AMATerseArchive(MVSArchive):
    def __init__(self, module):
        super(AMATerseArchive, self).__init__(module)
        self.pack_arg = module.params.get("format").get("format_options").get("terse_pack")
        if self.pack_arg is None:
            self.pack_arg = "SPACK"

    def add(self, path, archive):
        """
        Archive path into archive using AMATERSE program.
        Arguments:
            path: {str}
            archive: {str}
        """
        dds = {'args': self.pack_arg, 'sysut1': path, 'sysut2': archive}
        rc, out, err = mvs_cmd.amaterse(cmd="", dds=dds)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing AMATERSE to archive {0} into {1}".format(path, archive),
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
            source = self.prepare_temp_ds(self.module.params.get("tmp_hlq"))
            self.dump_into_temp_ds(source)
        else:
            # If we don't use a adrdssu container we cannot pack multiple data sets
            if len(self.targets) > 1:
                self.module.fail_json(
                    msg="You cannot archive multiple source data sets without accepting to use adrdssu")
            source = self.targets[0]
        dest = self.create_dest_ds(self.dest)
        self.add(source, dest)
        datasets.delete(source)


class XMITArchive(MVSArchive):
    def __init__(self, module):
        super(XMITArchive, self).__init__(module)
        self.xmit_log_dataset = module.params.get("format").get("format_options").get("xmit_log_dataset")

    def add(self, path, archive):
        """
        Archive path into archive using TSO XMIT.
        Arguments:
            path: {str}
            archive: {str}
        """
        log_option = "LOGDSNAME({0})".format(self.xmit_log_dataset) if self.xmit_log_dataset else "NOLOG"
        xmit_cmd = """ XMIT A.B -
        FILE(SYSUT1) OUTFILE(SYSUT2) -
        {0} -
        """.format(log_option)
        dds = {"SYSUT1": "{0},shr".format(path), "SYSUT2": archive}
        rc, out, err = mvs_cmd.ikjeft01(cmd=xmit_cmd, authorized=True, dds=dds)
        # rc, out, err = self.module.run_command(tso_cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing TSO XMIT to archive {0} into {1}".format(path, archive),
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
            source = self.prepare_temp_ds(self.module.params.get("tmp_hlq"))
            self.dump_into_temp_ds(source)
        else:
            # If we don't use a adrdssu container we cannot pack multiple data sets
            if len(self.paths) > 1:
                self.module.fail_json(
                    msg="You cannot archive multiple source data sets without accepting to use adrdssu")
            source = self.paths[0]
        dest = self.create_dest_ds(self.dest)
        self.add(source, dest)
        datasets.delete(source)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='list', elements='str', required=True),
            dest=dict(type='str'),
            exclude_path=dict(type='list', elements='str'),
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
                            xmit_log_dataset=dict(
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
            exclusion_patterns=dict(type='list', elements='str'),
            tmp_hlq=dict(type='str'),
            force=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )

    arg_defs = dict(
        path=dict(type='list', elements='str', required=True, alias='src'),
        dest=dict(type='str', required=False),
        exclude_path=dict(type='list', elements='str', default=[]),
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
                        xmit_log_dataset=dict(
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
                        xmit_log_dataset="",
                        use_adrdssu=False),
                ),
            ),
            default=dict(
                name="",
                format_options=dict(
                    terse_pack="SPACK",
                    xmit_log_dataset="",
                    use_adrdssu=False
                )
            ),
        ),
        group=dict(type='str'),
        mode=dict(type='str'),
        owner=dict(type='str'),
        remove=dict(type='bool', default=False),
        exclusion_patterns=dict(type='list', elements='str'),
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
