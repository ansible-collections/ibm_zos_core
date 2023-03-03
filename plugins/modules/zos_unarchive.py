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
    better_arg_parser,)
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
    from zoautil_py import datasets, mvscmd, types
except Exception:
    Datasets = MissingZOAUImport()
    mvscmd = MissingZOAUImport()
    types = MissingZOAUImport()

# TODO Define Unarchive class
class Unarchive(abc.ABC):
    def __init__(self, module):
        # TODO params init
        None

# TODO Define MVSUnarchive class
class MVSUnarchive(Unarchive):
    def __init__(self, module):
        # TODO MVSUnarchive params init
        super(MVSUnarchive, self).__init__(module)
        None


# TODO Define TerseUnarchive class
class TerseUnarchive(MVSUnarchive):
    def __init__(self, module):
        super(TerseUnarchive, self).__init__(module)

# TODO Define XMITUnarchive class

def run_module():
    # TODO Add module parameters
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='list', elements='str', required=True),
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
        path=dict(type='list', elements='str', required=True, alias='src'),
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
    None


def main():
    run_module()


if __name__ == '__main__':
    main()