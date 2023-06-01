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
module: zos_unarchive
version_added: "1.7.0"
author:
  - Oscar Fernando Flores Garcia (@fernandofloresg)
short_description: Unarchive a dataset on z/OS.
description:
  - The C(zos_unarchive) module unpacks an archive. It will not unpack a compressed file that does not contain an archive.
options:
'''

EXAMPLES = r'''
'''

RETURN = r'''
'''

import abc
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
    mvs_cmd)
from ansible.module_utils.common.text.converters import to_bytes, to_native
from sys import version_info
import re
import os
import zipfile
import tarfile
from traceback import format_exc
from zlib import crc32
from fnmatch import fnmatch
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

try:
    from zoautil_py import datasets, mvscmd, types, jobs
except Exception:
    Datasets = MissingZOAUImport()
    mvscmd = MissingZOAUImport()
    types = MissingZOAUImport()
    jobs = MissingZOAUImport()

data_set_regex = r"(?:(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})(?:[.]{1})){1,21}[A-Z$#@]{1}[A-Z0-9$#@-]{0,7}(?:\([A-Z$#@]{1}[A-Z0-9$#@]{0,7}\)){0,1}"

class Unarchive(abc.ABC):
    def __init__(self, module):
        self.module = module
        self.path = module.params.get("path")
        self.dest = module.params.get("dest")
        self.format = module.params.get("format").get("name")
        self.format_options = module.params.get("format").get("format_options")
        self.tmphlq = module.params.get("tmp_hlq")
        self.force = module.params.get("force")
        self.targets = list()
        self.debug = list()
        self.include = module.params.get("include")
        self.exclude = module.params.get("exclude")
        self.list = module.params.get("list")
        self.changed = False
        self.missing = list()
        if self.dest == '':
            self.dest = os.path.dirname(self.path)

    @abc.abstractmethod
    def extract_path(self):
        pass
    
    @abc.abstractmethod
    def list_content(self):
        pass
    
    def path_exists(self):
        return self.path and os.path.exists(self.path)

    @property
    def result(self):
        return {
            'path': self.path,
            'changed': self.changed,
            'targets': self.targets,
            'debug': self.debug,
            'missing': self.missing,
        }

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

    def list_content(self):
        self.targets = self.list_archive_content(self.path)
        return

    def extract_path(self):
        """Unpacks the contents of the archive stored in path into dest folder.
        
        """
        original_working_dir = os.getcwd()
        # The function gets relative paths, so it changes the current working
        # directory to the root of src.
        os.chdir(self.dest)
        self.file = self.open(self.path)
        
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
            self.file.extractall()
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
                msg="Bad zip file error when trying to open file {0} ".format(path)
            )
        return file

    def list_archive_content(self, path):
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

    def list_content(self):
        self.targets = self.list_archive_content(self.path)
        return 

    def extract_path(self):
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
        self.file = self.open(self.path)

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
            self.file.extractall()
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
    
    def create_dest_data_set(
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
                rc, hlq, err = self.module.run_command("hlq")
                hlq = hlq.replace('\n', '')
            cmd = "mvstmphelper {0}.RESTORE".format(hlq)
            rc, temp_ds, err = self.module.run_command(cmd)
            arguments.update(name = temp_ds.replace('\n', '')) 
        if record_format is None:
            arguments.update(record_format = "FB")
        if record_length is None:
            arguments.update(record_length = 1024)
        if type is None:
            arguments.update(type = "SEQ")
        arguments.pop("self")
        changed = data_set.DataSet.ensure_present(**arguments)
        return arguments["name"], changed

    def get_include_data_sets_cmd(self):
        include_cmd = "INCL( "
        for include_ds in self.include:
            include_cmd += " '{0}', - \n".format(include_ds)
        include_cmd += " ) - \n"
        return include_cmd

    def get_exclude_data_sets_cmd(self):
        exclude_cmd = "EXCL( - \n"
        for exclude_ds in self.exclude:
            exclude_cmd += " '{0}', - \n".format(exclude_ds)
        exclude_cmd += " ) - \n"
        return exclude_cmd

    def get_volumes(self):
        volumes_cmd = "OUTDYNAM( - \n"
        for volume in self.volumes:
            volumes_cmd += " ('{0}'), - \n".format(volume)
        volumes_cmd += " ) - \n"
        return volumes_cmd

    def restore(self, source):
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
            filter = self.get_include_data_sets_cmd()
        if self.exclude:
            filter = self.get_exclude_data_sets_cmd()
        if self.volumes:
            volumes = self.get_volumes()
        restore_cmd = """ RESTORE INDD(ARCHIVE) - 
                          DS( -
                            {0} ) -
                            {1} -
                        CATALOG -
                        {2} """.format(filter, volumes, force)
        dds = dict(archive="{0},old".format(source))
        rc, out, err = mvs_cmd.adrdssu(cmd=restore_cmd, dds=dds, authorized=True)
        self.debug = self.get_restored_datasets(out)
        if rc != 0:
            unrestore_data_sets = self.get_unrestored_datasets(out)
            unrestore_data_sets = ", ".join(unrestore_data_sets)
            self.clean_environment(data_sets=[source], uss_files=[], remove_targets=True)
            self.module.fail_json(
                msg="Failed executing ADRDSSU to archive {0}. List of data sets not restored : {1}".format(source, unrestore_data_sets),
                stdout=out,
                stderr=err,
                stdout_lines=restore_cmd,
                rc=rc,
            )
        return rc

    def path_exists(self):
        return data_set.DataSet.data_set_exists(self.path)
    
    def get_restored_datasets(self, output):
        ds_list = list()
        find_ds_list = re.findall(r"SUCCESSFULLY PROCESSED\n(?:.*\n)*", output)
        if find_ds_list:
            ds_list = re.findall(data_set_regex, find_ds_list[0])
        self.targets = ds_list
        return ds_list

    def get_unrestored_datasets(self, output):
        ds_list = list()
        output = output.split("SUCCESSFULLY PROCESSED")[0]
        find_ds_list = re.findall(r"NOT PROCESSED FROM THE LOGICALLY FORMATTED DUMP TAPE DUE TO \n(?:.*\n)*", output)
        if find_ds_list:
            ds_list = re.findall(data_set_regex, find_ds_list[0])
        return ds_list

    @abc.abstractmethod
    def unpack(self):
        pass
    
    def extract_path(self):
        """Extract the MVS path contents.
        
        """
        temp_ds = ""
        if not self.use_adrdssu:
            temp_ds, _ = self.create_dest_data_set(**self.dest_data_set)
            rc = self.unpack(self.path, temp_ds)
        else:
            temp_ds, _ = self.create_dest_data_set(type="SEQ", record_format="U", tmp_hlq=self.tmphlq, replace=True)
            self.unpack(self.path, temp_ds)
            rc = self.restore(temp_ds)
            datasets.delete(temp_ds)
        self.changed = not rc
        return

    def list_content(self, source):
        restore_cmd = " RESTORE INDD(ARCHIVE) DS(INCL(**)) "
        cmd = " mvscmdauth --pgm=ADRDSSU --archive={0},old --args='TYPRUN=NORUN' --sysin=stdin --sysprint=*".format(source)
        rc, out, err = self.module.run_command(cmd, data=restore_cmd)
        self.get_restored_datasets(out)
    
    def list_archive_content(self):
        try:
            temp_ds = self.create_dest_data_set(type="SEQ", record_format="U", tmp_hlq=self.tmphlq, replace=True)
            self.unpack(self.path, temp_ds)
            self.list_content(temp_ds)
        finally:
            datasets.delete(temp_ds)

    def clean_environment(self, data_sets=[], uss_files=[], remove_targets=False):
        """Removes any allocated data sets that won't be needed after module termination.
        Arguments:
            data_sets - {list(str)} : list of data sets to remove
            uss_files - {list(str)} : list of uss files to remove
            remove_targets - bool : Indicates if already unpacked data sets need to be removed too.
        """
        for ds in data_sets:
            data_set.DataSet.ensure_absent(ds)
        if remove_targets:
            for target in self.targets:
                data_set.DataSet.ensure_absent(target)


class AMATerseUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(AMATerseUnarchive, self).__init__(module)
    
    def unpack(self, path, dest):
        """
        Unpacks using AMATerse, assumes the data set has only been packed once.
        """
        dds = {'args': 'UNPACK', 'sysut1': path, 'sysut2': dest}
        rc, out, err = mvs_cmd.amaterse(cmd="", dds=dds)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing AMATERSE to restore {0} into {1}".format(path, dest),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        return rc


class XMITUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(XMITUnarchive, self).__init__(module)
    
    def unpack(self, path, dest):
        """
        Unpacks using XMIT.

        path is the archive
        dest is the destination dataset
        """
        unpack_cmd = """
        PROFILE NOPROMPT
        RECEIVE INDSN('{0}')
        DA('{1}')
        """.format(path, dest)
        rc, out, err = mvs_cmd.ikjeft01(cmd=unpack_cmd, authorized=True)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing RECEIVE to restore {0} into {1}".format(path, dest),
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

def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True, alias='src'),
            dest=dict(type='str', default=''),
            include=dict(type='list', elements='str'),
            exclude=dict(type='list', elements='str'),
            list=dict(type='bool', default=False),
            format=dict(
                type='dict',
                required=False,
                name = dict(
                    type='str',
                    default='gz',
                    choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                    ),
                    format_options=dict(
                        type='dict',
                        required=False,
                        options=dict(
                            xmit_log_dataset=dict(
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
                        ),
                        default=dict(xmit_log_dataset="",
                                     dest_volumes=[],
                                     use_adrdssu=False,)
                    ),
                default=dict(name="", supotions=dict(
                                                    xmit_log_dataset="",
                                                    dest_volumes=[],
                                                    use_adrdssu=False,)),
                ),
            dest_data_set=dict(
                type='dict',
                required=False,
                options=dict(
                    name=dict(
                        type='str', required=False,
                    ),
                    type=dict(
                        type='str',
                        choices=['BASIC', 'KSDS', 'ESDS', 'RRDS',
                                 'LDS', 'SEQ', 'PDS', 'PDSE', 'MEMBER'],
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
            tmp_hlq=dict(type='str', default=''),
            force=dict(type='bool', default=False),
            remote_src=dict(type='bool', default=False),
            ),
        mutually_exclusive = [
            ['include', 'exclude'],
        ],
        supports_check_mode=True,
    )

    arg_defs = dict(
        path=dict(type='str', required=True, alias='src'),
        dest=dict(type='str', required=False, default=''),
        include=dict(type='list', elements='str'),
        exclude=dict(type='list', elements='str'),
        list=dict(type='bool', default=False),
        format=dict(
            type='dict',
            required=False,
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
                            xmit_log_dataset=dict(
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
                        default=dict(xmit_log_dataset=""),
                    )
                ),
            default=dict(name="", supotions=dict(xmit_log_dataset="")),
            ),
        dest_data_set=dict(
            arg_type='dict',
            required=False,
            options=dict(
                name=dict(arg_type='str', required=False),
                type=dict(arg_type='str', required=True),
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
        tmp_hlq=dict(type='qualifier_or_empty', default=''),
        force=dict(type='bool', default=False),
        mutually_exclusive = [
            ['include', 'exclude'],
        ],
        remote_src=dict(type='bool', default=False),
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

    if not unarchive.path_exists():
        module.fail_json(msg="{0} does not exists, please provide a valid path.".format(module.params.get("path")))

    unarchive.extract_path()

    module.exit_json(**unarchive.result)

def main():
    run_module()


if __name__ == '__main__':
    main()