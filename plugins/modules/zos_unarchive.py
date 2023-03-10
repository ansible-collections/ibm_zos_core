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
    data_set)
from ansible.module_utils.common.text.converters import to_bytes, to_native
import glob
import bz2
from sys import version_info
import re
import os
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
    from zoautil_py import datasets, mvscmd, types, jobs
except Exception:
    Datasets = MissingZOAUImport()
    mvscmd = MissingZOAUImport()
    types = MissingZOAUImport()
    jobs = MissingZOAUImport()

# TODO Define Unarchive class
class Unarchive(abc.ABC):
    def __init__(self, module):
        # TODO params init
        self.module = module
        self.path = module.params.get("path")
        self.dest = module.params.get("dest")
        self.format = module.params.get("format").get("name")
        self.format_options = module.params.get("format").get("suboptions")
        self.tmphlq = module.params.get("tmp_hlq")
        self.force = module.params.get("force")

    @abc.abstractmethod
    def extract_path(self):
        pass
    
    @property
    def result(self):
        return {
            'path': self.path,
            'changed': self.changed,
        }
class MVSUnarchive(Unarchive):
    def __init__(self, module):
        # TODO MVSUnarchive params init
        super(MVSUnarchive, self).__init__(module)
        # self.dest_volume = module.params.get("format").suboptions("dest_volume")
    
    def create_temp_ds(self, tmphlq):
        if tmphlq:
            hlq = tmphlq
        else:
            rc, hlq, err = self.module.run_command("hlq")
            hlq = hlq.replace('\n', '')
        cmd = "mvstmphelper {0}.RESTORE".format(hlq)
        rc, temp_ds, err = self.module.run_command(cmd)
        temp_ds = temp_ds.replace('\n', '')
        changed = data_set.DataSet.ensure_present(name=temp_ds, replace=True, type='SEQ', record_format='U')
        return temp_ds

    def restore(self, source):
        """
        Calls ADDRSU using RESTORE to unpack the dump datasets.
        """
        """
        Dump src datasets identified as self.targets into a temporary dataset using ADRDSSU.
        """
        restore_cmd = """ RESTORE INDD(ARCHIVE) - 
                          DS(INCL(**)) - 
                          CATALOG """
        cmd = " mvscmdauth --pgm=ADRDSSU --archive={0},old --sysin=stdin --sysprint=*".format(source)
        rc, out, err = self.module.run_command(cmd, data=restore_cmd)

        if rc != 0:
            self.module.fail_json(
                msg="Failed executing ADRDSSU to archive {0}".format(source),
                stdout=out,
                stderr=err,
                stdout_lines=restore_cmd,
                rc=rc,
            )
        return rc

    def path_exists(self):
        return data_set.DataSet.data_set_exists(self.path)

class AMATerseUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(AMATerseUnarchive, self).__init__(module)
    
    def unpack(self, path, dest):
        """
        Unpacks using AMATerse, assumes the data set has only been packed once.
        """
        cmd = "mvscmdhelper --pgm=AMATERSE --args='UNPACK' --sysut1={0} --sysut2={1} --sysprint=*".format(path, dest)
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing AMATERSE to restore {0} into {1}".format(path, dest),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        return rc

    def extract_path(self):
        # 0. Create a tmp data set to dump the contens of untersing
        # 1. Call Terse to unpack the dataset
        # 2. Call super to RESTORE using ADDRSU
        rc = 1
        try:
            temp_ds = self.create_temp_ds(self.tmphlq)
            self.unpack(self.path, temp_ds)
            rc = super(AMATerseUnarchive, self).restore(temp_ds)
        finally:
            datasets.delete(temp_ds)
        self.changed = not rc
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
        RECEIVE INDSN('{0}') - 
        DA('{1}')
        """.format(path, dest)
        cmd = "tsocmd RECEIVE INDSN\\( \\'{0}\\' \\) ".format(path)
        # rc, out, err = self.module.run_command(cmd, data=unpack_cmd)
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed executing RECEIVE to restore {0} into {1}".format(path, dest),
                stdout=out,
                stderr=err,
                rc=rc,
            )
        return rc

    def extract_path(self):
        # 0. Create a tmp data set to dump the contens of receive
        # 1. Call RECEIVE.
        # 2. Call super to RESTORE using ADDRSU
        temp_ds = self.create_temp_ds(self.tmphlq)
        self.unpack(self.path, temp_ds)
        rc = super(XMITUnarchive, self).restore(temp_ds)
        self.changed = not rc
        return rc


def get_unarchive_handler(module):
    format = module.params.get("format").get("name")
    if format in ["tar", "gz", "bz2"]:
        # return TarUnarchive(module)
        None
    elif format == "terse":
        return AMATerseUnarchive(module)
    elif format == "xmit":
        return XMITUnarchive(module)
    # return ZipUnarchive(module)

def run_module():
    # TODO Add module parameters
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True),
            dest=dict(type='str'),
            format=dict(
                type='dict',
                required=False,
                name = dict(
                    type='str',
                    default='gz',
                    choices=['bz2', 'gz', 'tar', 'zip', 'terse', 'xmit', 'pax']
                    ),
                    suboptions=dict(
                        type='dict',
                        required=False,
                        options=dict(
                            xmit_log_dataset=dict(
                                type='str',
                                required=False,
                            ),
                            dest_volume=dict(
                                type='str',
                                required=False
                            ),
                        ),
                        default=dict(xmit_log_dataset="")
                    ),
                default=dict(name="", supotions=dict(xmit_log_dataset="")),
                ),
            tmp_hlq=dict(type='str', default=''),
            force=dict(type='bool', default=False)
            ),
        supports_check_mode=True,
    )

    arg_defs = dict(
        path=dict(type='str', required=True, alias='src'),
        dest=dict(type='str', required=False),
        exclude_path=dict(type='list', elements='str', default=[]),
        format=dict(
            type='dict',
            required=False,
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
                            xmit_log_dataset=dict(
                                type='str',
                                required=False,
                            ),
                            dest_volume=dict(
                                type='str',
                                required=False
                            ),
                        ),
                        default=dict(xmit_log_dataset=""),
                    )
                ),
            default=dict(name="", supotions=dict(xmit_log_dataset="")),
            ),
        tmp_hlq=dict(type='qualifier_or_empty', default=''),
        force=dict(type='bool', default=False)
    )
    
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    try:
        parser = better_arg_parser.BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
        # TODO Is it ok to override module.params with parsed_args ?
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))
    # TODO Add module logic steps
    # 3. how about keep newest file when unarchiving?
    unarchive = get_unarchive_handler(module)

    if not unarchive.path_exists():
        module.fail_json(msg="{0} does not exists, please provide a valid path.".format(module.params.get("path")))

    unarchive.extract_path()

    module.exit_json(**unarchive.result)

def main():
    run_module()


if __name__ == '__main__':
    main()