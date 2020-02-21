# Copyright (c) 2019, 2020 Lu Zhao <zlbjlu@cn.ibm.com>
# Copyright (c) IBM Corporation 2020
# LICENSE: [GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import stat
import tempfile
import re

#from ansible.constants import mk_boolean as boolean
from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.hashing import checksum
from ansible.utils.vars import merge_hash


def _read_file(src, is_binary=False):
    read_mode = 'rb' if is_binary else 'r'
    try:
        content = open(src, read_mode).read()
    except (FileNotFoundError, IOError, OSError) as err:
        raise AnsibleError("Could not read file {}".format(src))
    return content


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default

class ActionModule(ActionBase):
    def get_copy_action_plugin(self):
        return (self._shared_loader_obj.action_loader.get(
            'copy',
            task=self._task.copy(),
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj))

    def run(self, tmp=None, task_vars=None):
        ''' handler for file transfer operations '''
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        
        src          = self._task.args.get('src', None)
        b_src        = to_bytes(src, errors='surrogate_or_strict')
        dest         = self._task.args.get('dest', None)
        b_dest       = to_bytes(dest, errors='surrogate_or_strict')
        content      = self._task.args.get('content', None)
        backup       = _process_boolean(self._task.args.get('backup'), default=False)
        force        = _process_boolean(self._task.args.get('force'), default=True)
        validate     = _process_boolean(self._task.args.get('validate'), default=True)
        local_follow = _process_boolean(self._task.args.get('local_follow'), default=True)
        remote_src   = _process_boolean(self._task.args.get('remote_src'), default=False)
        is_uss        = _process_boolean(self._task.args.get('is_uss', False), default=False)
        is_vsam       = _process_boolean(self._task.args.get('is_vsam', False), default=False)
        use_qualifier = _process_boolean(self._task.args.get('use_qualifier', True), default=False)
        is_binary     = _process_boolean(self._task.args.get('is_binary', True), default=False)
        is_catalog    = _process_boolean(self._task.args.get('is_catalog', True), default=True)
        checksum     = self._task.args.get('checksum', None)
        volume       = self._task.args.get('volume', None)
        encoding     = self._task.args.get('encoding', None)
        mode         = self._task.args.get('mode', None)
        owner        = self._task.args.get('owner', None)
        group        = self._task.args.get('group', None)

        if is_uss:
            zos_params = frozenset({'is_uss', 'is_binary', 'is_catalog', 'is_vsam', 'use_qualifier', 'volume', 'encoding'})
            new_module_args = dict((k,v) for k,v in self._task.args.items() if k not in zos_params)
            result.update(self._execute_module(module_name='copy', module_args=new_module_args, task_vars=task_vars))
            return result
        
        if not remote_src:
            if not os.path.exists(b_src):
                result['msg'] = "The local file {} does not exist".format(src)
            if not os.access(b_src, os.R_OK):
                result['msg'] = "The local file {} does not appropriate read permisssion".format(src)
        
        if result.get('msg'):
            result.update(src=src, dest=dest, changed=False)
            return result
        
        content = _read_file(src)
        new_module_args = dict((k,v) for k,v in self._task.args.items())
        new_module_args.update(_local_data=content, _size=len(content.encode('utf-8')))
        result.update(self._execute_module(module_name='zos_copy', module_args=new_module_args, task_vars=task_vars))
        ch = checksum(src)

        return result
