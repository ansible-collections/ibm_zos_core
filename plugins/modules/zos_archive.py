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
      suboptions:
          description:
            - Options specific to each format.
          type: dict
          required: false
          suboptions:
            terse_pack:
              description: Pack option to use for terse format.
              type: str
              choices: ['PACK', 'SPACK']
            xmit_log_dataset:
              description: Provide a name of data set to use for xmit log.
              type: str
            use_adrdssu:
              description: Use DFSMSdss ADRDSSU step.
              type: bool
              default: False

  dest:
    description: The file name of the dest archive.
    type: str
    required: false
  exclude_path:
    description:
        - Remote absolute path, glob, or list of paths or globs for the file or files to exclude
           from path list and glob expansion.
    type: list
    required: false
    elements: str
  force_archive:
    description:
      - Allows you to force the module to treat this as an archive even if only a single file is specified.
      - By default when a single file is specified it is compressed only (not archived).
    type: bool
    required: false
    default: false
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
  replace_dest:
    description:
      - Replace the existing archive C(dest).
    type: bool
    default: false
    required: false
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
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
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


try:
    from zoautil_py import datasets
except Exception:
    Datasets = MissingZOAUImport()

XMIT_RECORD_LENGTH = 80
AMATERSE_RECORD_LENGTH = 1024


def get_archive_handler(module):
    """
    Return the proper archive handler based on archive format.
    Arguments:
        format: {str}
    Returns:
        Archive: {Archive}

    """
    format = module.params.get("format").get("name")
    if format in ["tar", "gz", "bz2"]:
        return TarArchive(module)
    elif format == "terse":
        return AMATerseArchive(module)
    elif format == "xmit":
        return XMITArchive(module)
    return ZipArchive(module)


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
        self.not_found = []
        self.force = module.params['force']
        self.paths = module.params['path']
        self.tmp_debug = ""

        # remove files from exclusion list


    def targets_exist(self):
        return bool(self.targets)

    @abc.abstractmethod
    def dest_exists(self):
        pass

    @abc.abstractmethod
    def dest_type(self):
        return "USS"

    @abc.abstractmethod
    def update_permissions(self):
        return

    @abc.abstractmethod
    def find_targets(self):
        for path in self.paths:
            if os.path.exists(path):
                self.targets.append(path)
            else:
                self.not_found.append(path)

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
            'archived': self.targets,
            'dest': self.dest,
            # 'dest_state': self.dest_state,
            'changed': self.changed,
            # 'arcroot': self.root,
            'missing': self.not_found,
            # 'expanded_paths': list(self.expanded_paths),
            # 'expanded_exclude_paths': list(self.expanded_exclude_paths),
            # tmp debug variables
            'tmp_debug': self.tmp_debug,
            # 'targets': self.targets,
        }


class USSArchive(Archive):
    def __init__(self, module):
        super(USSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        self.arcroot = os.path.commonpath(self.paths)

    def dest_exists(self):
        return os.path.exists(self.dest)

    def dest_type(self):
        return "USS"

    def update_permissions(self):
        return

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
        for target in self.targets:
            if os.path.isdir(target):
                os.removedirs(target)
            else:
                os.remove(target)

class TarArchive(USSArchive):
    def __init__(self, module):
        super(TarArchive, self).__init__(module)
    
    def open(self, path):
        if self.format == 'tar':
            self.file = tarfile.open(path, 'w')
        elif self.format in ('gz', 'bz2'):
            self.file = tarfile.open(path, 'w|' + self.format)

    def add(self, source):
        self.file.add(source, os.path.relpath(source, self.arcroot))

    def archive_targets(self):
        self.open(self.dest)
        for file in self.targets:
            self.add(file)
        self.file.close()


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

    def add(self, source):
        self.file.write(source)

    def archive_targets(self):
        for file in self.targets:
            self.add(file)
        self.file.close()
            


class PaxArchive(USSArchive):
    def __init__(self, module):
        super(PaxArchive, self).__init__(module)
    
    def open(self):
        pass
    def close(self):
        pass
    def add(self):
        pass
    def archive_targets(self):
        pass


class MVSArchive(Archive):
    def __init__(self, module):
        super(MVSArchive, self).__init__(module)
        self.original_checksums = self.dest_checksums()
        self.use_adrdssu = module.params.get("format").get("suboptions").get("use_adrdssu")

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
        Create
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
        return


class AMATerseArchive(MVSArchive):
    def __init__(self, module):
        super(AMATerseArchive, self).__init__(module)
        self.pack_arg = module.params.get("format").get("suboptions").get("terse_pack")

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
        self.found = self.targets[:]
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
        self.xmit_log_dataset = module.params.get("format").get("suboptions").get("xmit_log_dataset")

    def add(self, path, archive):
        """
        Archive path into archive using TSO XMIT.
        Arguments:
            path: {str}
            archive: {str}
        """
        log_option = "LOGDSNAME\\({0}\\)".format(self.xmit_log_dataset) if self.xmit_log_dataset else "NOLOG"
        tso_cmd = " tsocmd XMIT A.B DSN\\( \\'{0}\\' \\) OUTDSN\\( \\'{1}\\' \\) {2}".format(path, archive, log_option)
        rc, out, err = self.module.run_command(tso_cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing TSO XMIT to archive {0} into {1}".format(path, archive),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        self.found = self.targets[:]
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
            exclude_path=dict(type='list', elements='str', default=[]),
            force_archive=dict(type='bool', default=False),
            format=dict(
                type='dict',
                options=dict(
                    name=dict(
                        type='str',
                        default='gz',
                        choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                    ),
                    suboptions=dict(
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
                        # default=dict(terse_pack="", xmit_log_dataset=""),
                    ),
                )
                # default=dict(name="", supotions=dict(terse_pack="", xmit_log_dataset="")),
            ),
            group=dict(type='str', default=''),
            mode=dict(type='str', default=''),
            owner=dict(type='str', default=''),
            remove=dict(type='bool', default=False),
            exclusion_patterns=dict(type='list', elements='str'),
            replace_dest=dict(type='bool', default=False),
            tmp_hlq=dict(type='str', default=''),
            force=dict(type='bool', default=False)
        ),
        supports_check_mode=True,
    )

    arg_defs = dict(
        path=dict(type='list', elements='str', required=True, alias='src'),
        dest=dict(type='str', required=False),
        exclude_path=dict(type='list', elements='str', default=[]),
        force_archive=dict(type='bool', default=False),
        format=dict(
            type='dict',
            options=dict(
                name=dict(
                    type='str',
                    default='gz',
                    choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                ),
                suboptions=dict(
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
                supotions=dict(
                    terse_pack="SPACK",
                    xmit_log_dataset="",
                    use_adrdssu=False
                )
            ),
        ),
        group=dict(type='str', default=''),
        mode=dict(type='str', default=''),
        owner=dict(type='str', default=''),
        remove=dict(type='bool', default=False),
        exclusion_patterns=dict(type='list', elements='str'),
        replace_dest=dict(type='bool', default=False, alias='force'),
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
            # archive.update_permissions()
            None
        archive.changed = archive.is_different_from_original()

    module.exit_json(**archive.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
