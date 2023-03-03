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
version_added: "1.6.0"
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
    type: str
    choices: [ bz2, gz, tar, zip, terse, xmit, pax]
    default: gz
    required: false
  dest:
    description: The file name of the destination archive.
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
  list:
    description:
      - List the names of the archive contents
    type: bool
    default: false
    required: false
  tmp_hlq:
    description:
      - High Level Qualifier used for temporary datasets.
    type: str
    required: false
'''

EXAMPLES = r'''
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
    version_added: 3.4.0
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
    data_set)
from ansible.module_utils.common.text.converters import to_bytes, to_native
import glob
import bz2
from sys import version_info
import re
import os
import abc
import io
import zipfile
import tarfile
from traceback import format_exc
from zlib import crc32
from fnmatch import fnmatch
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

try:
    from zoautil_py import datasets, mvscmd, types
except Exception:
    Datasets = MissingZOAUImport()
    mvscmd = MissingZOAUImport()
    types = MissingZOAUImport()


LZMA_IMP_ERR = None
try:
    import lzma
    HAS_LZMA = True
except ImportError:
    LZMA_IMP_ERR = format_exc()
    HAS_LZMA = False

PY27 = version_info[0:2] >= (2, 7)
STATE_ABSENT = 'absent'
STATE_ARCHIVED = 'archive'
STATE_COMPRESSED = 'compress'
STATE_INCOMPLETE = 'incomplete'
XMIT_RECORD_LENGTH = 80
AMATERSE_RECORD_LENGTH = 1024


def _to_bytes(s):
    return to_bytes(s, errors='surrogate_or_strict')


def _to_native(s):
    return to_native(s, errors='surrogate_or_strict')


def _to_native_ascii(s):
    return to_native(s, errors='surrogate_or_strict', encoding='ascii')


def matches_exclusion_patterns(path, exclusion_patterns):
    return any(fnmatch(path, p) for p in exclusion_patterns)


def get_archive(module: AnsibleModule):
    """
    Return the proper archive handler based on archive format.
    Arguments:
        format: {str}
    Returns:
        Archive: {Archive}


    """
    """
    TODO Come up with rules to decide based on src, dest and format
    which archive handler to use.
    """
    format = module.params.get("format").get("name")
    if format in ["tar", "gz", "bz2"]:
        return TarArchive(module)
    elif format == "terse":
        return AMATerseArchive(module)
    elif format == "xmit":
        return XMITArchive(module)
    return ZipArchive(module)


def common_path(paths):
    empty = b'' if paths else ''

    return os.path.join(
        os.path.dirname(os.path.commonprefix([os.path.join(os.path.dirname(p), empty) for p in paths])), empty
    )


def expand_paths(paths):
    expanded_path = []
    is_globby = False
    for path in paths:
        b_path = _to_bytes(path)
        if b'*' in b_path or b'?' in b_path:
            e_paths = glob.glob(b_path)
            is_globby = True
        else:
            e_paths = [b_path]
        expanded_path.extend(e_paths)
    return expanded_path, is_globby


def strip_prefix(prefix, string):
    return string[len(prefix):] if string.startswith(prefix) else string


class Archive(abc.ABC):
    def __init__(self, module):
        self.module = module
        self.destination = module.params['dest']
        self.exclusion_patterns = module.params['exclusion_patterns'] or []
        self.format = module.params.get("format").get("name")
        self.must_archive = module.params['force_archive']
        self.remove = module.params['remove']
        self.tmp_hlq = module.params['tmp_hlq']
        self.changed = False
        self.destination_state = STATE_ABSENT
        self.errors = []
        self.file = None
        self.successes = []
        self.targets = []
        self.not_found = []
        self.list = module.params['list']
        self.force = module.params['force']

        paths = module.params['path']

        if self.format in ("terse", "xmit"):
            self.paths = paths
            self.expanded_paths, self.has_globs = "", ""
            self.expanded_exclude_paths = ""
            self.root = ""
        else:
            self.expanded_paths, self.has_globs = expand_paths(paths)
            self.expanded_exclude_paths = expand_paths(module.params['exclude_path'])[0]

            self.paths = sorted(set(self.expanded_paths) - set(self.expanded_exclude_paths))

            if not self.paths:
                module.fail_json(
                    path=', '.join(paths),
                    # expanded_paths=_to_native(b', '.join(self.expanded_paths)),
                    # expanded_exclude_paths=_to_native(b', '.join(self.expanded_exclude_paths)),
                    msg='Error, no source paths were found'
                )
            self.original_checksums = self.destination_checksums()
            self.original_size = self.destination_size()
            self.root = common_path(self.paths)
        self.tmp_debug = ""


    def add(self, path, archive):
        """
        Abstract add path into archive function.
        Arguments:
            path: {str}
            archive: {str}
        """
        try:
            self._add(_to_native_ascii(path), _to_native(archive))
            if self.contains(_to_native(archive)):
                self.successes.append(path)
        except Exception as e:
            self.errors.append('%s: %s' % (_to_native_ascii(path), _to_native(e)))

    def add_targets(self):
        """
        Add targets invokes the add abstract methods, each Archive handler
        will implement it differently.
        """
        self.open()

        try:
            for target in self.targets:
                if os.path.isdir(target):
                    for directory_path, directory_names, file_names in os.walk(target, topdown=True):
                        for directory_name in directory_names:
                            full_path = os.path.join(directory_path, directory_name)
                            self.add(full_path, strip_prefix(self.root, full_path))

                        for file_name in file_names:
                            full_path = os.path.join(directory_path, file_name)
                            self.add(full_path, strip_prefix(self.root, full_path))
                else:
                    self.add(target, strip_prefix(self.root, target))
        except Exception as e:
            if self.format in ('zip', 'tar'):
                archive_format = self.format
            else:
                archive_format = 'tar.' + self.format
            self.module.fail_json(
                msg='Error when writing %s archive at %s: %s' % (
                    archive_format, self.destination, e
                ),
                exception=e
            )
        self.close()

        if self.errors:
            self.module.fail_json(
                msg='Errors when writing archive at %s: %s' % (self.destination, '; '.join(self.errors))
            )

    def find_targets(self):
        """
        Find USS targets, this is the default behaviour, MVS handlers will override it.
        """
        for path in self.paths:
            if not os.path.lexists(path):
                self.not_found.append(path)
            else:
                self.targets.append(path)

    def is_different_from_original(self):
        if self.original_checksums is None:
            return self.original_size != self.destination_size()
        else:
            return self.original_checksums != self.destination_checksums()

    def destination_checksums(self):
        if self.destination_exists() and self.destination_readable():
            return self._get_checksums(self.destination)
        return None

    def destination_exists(self):
        return self.destination and os.path.exists(self.destination)

    def destination_readable(self):
        return self.destination and os.access(self.destination, os.R_OK)

    def destination_size(self):
        return os.path.getsize(self.destination) if self.destination_exists() else 0

    def remove_targets(self):
        for path in self.successes:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        # remove tree
                        None
                    else:
                        os.remove(path)
                except OSError:
                    self.errors.append(path)
        for path in self.paths:
            try:
                if os.path.isdir(path):
                    # remove tree
                    None
            except OSError:
                self.errors.append(path)

        if self.errors:
            self.module.fail_json(
                dest=self.destination, msg='Error deleting some source files: ', files=self.errors
            )

    def is_archive(self, path):
        return re.search(br'\.(tar|tar\.(gz|bz2|xz)|tgz|tbz2|zip)$', os.path.basename(path), re.IGNORECASE)

    def has_targets(self):
        return bool(self.targets)

    def has_unfound_targets(self):
        return bool(self.not_found)

    def destination_type(self):
        return "USS"

    def update_permissions(self):
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.destination)
        self.changed = self.module.set_fs_attributes_if_different(file_args, self.changed)

    def listing(self):
        return self.list

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def contains(self, name):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def _add(self, path, archive):
        pass

    @abc.abstractmethod
    def _get_checksums(self, path):
        pass

    @abc.abstractmethod
    def list_contents(self):
        pass

    @property
    def result(self):
        return {
            'archived': self.successes,
            'dest': self.destination,
            'dest_state': self.destination_state,
            'changed': self.changed,
            'arcroot': self.root,
            'missing': self.not_found,
            'expanded_paths': list(self.expanded_paths),
            'expanded_exclude_paths': list(self.expanded_exclude_paths),
            # tmp debug variables
            # 'tmp_debug': self.tmp_debug,
            # 'targets': self.targets,
        }

class TarArchive(Archive):
    def __init__(self, module):
        super(TarArchive, self).__init__(module)
        self.fileIO = None

    def close(self):
        self.file.close()
        if self.format == 'xz':
            with lzma.open(_to_native(self.destination), 'wb') as f:
                f.write(self.fileIO.getvalue())
            self.fileIO.close()

    def contains(self, name):
        try:
            self.file.getmember(name)
        except KeyError:
            return False
        return True

    def open(self):
        open_mode = 'w' if self.force else 'x'

        try:
            if self.format in ('gz', 'bz2'):
                self.file = tarfile.open(_to_native_ascii(self.destination), open_mode + ':' + self.format)
            # python3 tarfile module allows xz format but for python2 we have to create the tarfile
            # in memory and then compress it with lzma.
            elif self.format == 'xz':
                self.fileIO = io.BytesIO()
                self.file = tarfile.open(fileobj=self.fileIO, mode=open_mode)
            elif self.format == 'tar':
                self.file = tarfile.open(_to_native_ascii(self.destination), open_mode)
            else:
                self.module.fail_json(msg="%s is not a valid archive format" % self.format)
        except FileExistsError as e:
            self.module.fail_json(msg="%s file exists. Use force flag to replace dest" % self.destination)

    def _add(self, path, archive):
        def py27_filter(tarinfo):
            return None if matches_exclusion_patterns(tarinfo.name, self.exclusion_patterns) else tarinfo

        def py26_filter(path):
            return matches_exclusion_patterns(path, self.exclusion_patterns)

        if PY27:
            self.file.add(path, archive, recursive=False, filter=py27_filter)
        else:
            self.file.add(path, archive, recursive=False, exclude=py26_filter)

    def _get_checksums(self, path):
        if HAS_LZMA:
            LZMAError = lzma.LZMAError
        else:
            # Just picking another exception that's also listed below
            LZMAError = tarfile.ReadError
        try:
            if self.format == 'xz':
                with lzma.open(_to_native_ascii(path), 'r') as f:
                    archive = tarfile.open(fileobj=f)
                    checksums = set((info.name, info.chksum) for info in archive.getmembers())
                    archive.close()
            else:
                archive = tarfile.open(_to_native_ascii(path), 'r|' + self.format)
                checksums = set((info.name, info.chksum) for info in archive.getmembers())
                archive.close()
        except (LZMAError, tarfile.ReadError, tarfile.CompressionError):
            try:
                # The python implementations of gzip, bz2, and lzma do not support restoring compressed files
                # to their original names so only file checksum is returned
                f = self._open_compressed_file(_to_native_ascii(path), 'r')
                checksums = set([(b'', crc32(f.read()))])
                f.close()
            except Exception:
                checksums = set()
        return checksums

    def list_contents(self):
        if self.format == 'tar':
            self.file = tarfile.open(_to_native_ascii(self.destination), 'r')
        elif self.format in ('gz', 'bz2'):
            self.file = tarfile.open(_to_native_ascii(self.destination), 'r|' + self.format)
        elif self.format == 'xz':
            self.fileIO = io.BytesIO()
            self.file = tarfile.open(fileobj=self.fileIO, mode='r')
        else:
            self.module.fail_json(msg="%s is not a valid archive format for listing contents" % self.format)
        self.successes = self.file.getnames()
        self.file.close()

class ZipArchive(Archive):
    def __init__(self, module):
        super(ZipArchive, self).__init__(module)

    def open(self):
        self.file = zipfile.ZipFile(self.destination, 'w', zipfile.ZIP_DEFLATED, True)

    def close(self):
        self.file.close()

    def _add(self, path, archive):
        if not matches_exclusion_patterns(path, self.exclusion_patterns):
            self.file.write(_to_bytes(path), archive)

    def contains(self, name):
        try:
            self.file.getinfo(name)
        except KeyError:
            return False
        return True

    def _get_checksums(self, path):
        try:
            archive = zipfile.ZipFile(path, 'r')
            checksums = set((info.filename, info.CRC) for info in archive.infolist())
            archive.close()
        except zipfile.BadZipFile:
            checksums = set()
        return checksums

    def list_contents(self):
        self.file = zipfile.ZipFile(self.destination, 'r', zipfile.ZIP_DEFLATED, True)
        self.successes = self.file.namelist()
        self.file.close()


class MVSArchive(Archive):
    def __init__(self, module):
        super(MVSArchive, self).__init__(module)
        self.paths = [_to_native_ascii(p) for p in self.paths]

    def open(self):
        pass

    def close(self):
        pass

    def find_targets(self):
        """
        Based on path, find existing targets.
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
        # TODO shall we catch ensure_present error ? It raises a DataSetCreate Error. I think yes.
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

        cmd = " mvscmdauth --pgm=ADRDSSU --TARGET={0},old --sysin=stdin --sysprint=*".format(temp_ds)
        rc, out, err = self.module.run_command(cmd, data=dump_cmd)

        if rc != 0:
            self.module.fail_json(
                msg="Failed executing ADRDSSU to archive {0}".format(temp_ds),
                stdout=out,
                stderr=err,
                stdout_lines=dump_cmd,
                rc=rc,
            )
        return rc

    def add_targets(self):
        for target in self.targets:
            self._add(target, self.destination)

    def _add(self, path, archive):
        if not matches_exclusion_patterns(path, self.exclusion_patterns):
            rc = datasets.zip(archive, path)
            if rc != 0:
                self.module.fail_json(msg="Error creating MVS archive")
            self.successes.append(path)

    def list_contents(self):
        pass

    def _get_checksums(self, path):
        pass

    def contains(self):
        pass

    def is_different_from_original(self):
        return True

    def destination_type(self):
        return "MVS"

    def destination_exists(self):
        return data_set.DataSet.data_set_exists(self.destination)


class AMATerseArchive(MVSArchive):
    def __init__(self, module):
        super(AMATerseArchive, self).__init__(module)
        self.pack_arg = module.params.get("format").get("suboptions").get("terse_pack")

    def _add(self, path, archive):
        """
        Archive path into archive using AMATERSE program.
        Arguments:
            path: {str}
            archive: {str}
        """
        cmd = "mvscmdhelper --pgm=AMATERSE --args='{0}' --sysut1={1} --sysut2={2} --sysprint=*".format(self.pack_arg, path, archive)
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing AMATERSE to archive {0} into {1}".format(path, archive),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        self.successes = self.targets[:]
        return rc

    def add_targets(self):
        """
        Add MVS Datasets to the AMATERSE Archive by creating a temporary dataset and dumping the source datasets into it.
        """
        temp_ds = self.prepare_temp_ds(self.module.params.get("tmp_hlq"))
        try:
            destination = self.create_dest_ds(self.destination)
            rc = self.dump_into_temp_ds(temp_ds)
            rc = self._add(temp_ds, destination)
        finally:
            datasets.delete(temp_ds)

class XMITArchive(MVSArchive):
    def __init__(self, module):
        super(XMITArchive, self).__init__(module)
        self.xmit_log_dataset = module.params.get("format").get("suboptions").get("xmit_log_dataset")

    def _add(self, path, archive):
        """
        Archive path into archive using TSO XMIT.
        Arguments:
            path: {str}
            archive: {str}
        """
        log_option = "LOGDSNAME\\({0}\\)".format(self.xmit_log_dataset) if self.xmit_log_dataset else "NOLOG"
        tso_cmd = " tsocmd XMIT A.B DSN\\( \\'{0}\\' \\) OUTDSN\\( \\'{1}\\' \\) {2}".format( path, archive, log_option)
        rc, out, err = self.module.run_command(tso_cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing TSO XMIT to archive {0} into {1}".format(path, archive),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        self.successes = self.targets[:]
        return rc

    def add_targets(self):
        """
        Adds MVS Datasets to the TSO XMIT Archive by creating a temporary dataset and dumping the source datasets into it.
        """
        temp_ds = self.prepare_temp_ds(self.module.params.get("tmp_hlq"))
        try:
            destination = self.create_dest_ds(self.destination)
            rc = self.dump_into_temp_ds(temp_ds)
            rc = self._add(temp_ds, destination)
        finally:
            datasets.delete(temp_ds)


def run_module():
    None
    
def main():
    run_module()


if __name__ == '__main__':
    main()
