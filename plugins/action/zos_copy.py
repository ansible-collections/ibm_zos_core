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
from ansible.plugins.action import ActionBase
from ansible.utils.hashing import checksum
from ansible.utils.vars import merge_hash

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
        
        mvs_copy_args = self._task.args.copy()
        src          = mvs_copy_args.get('src', None)
        b_src        = to_bytes(src, errors='surrogate_or_strict')
        dest         = mvs_copy_args.get('dest', None)
        b_dest       = to_bytes(dest, errors='surrogate_or_strict')
        backup       = mvs_copy_args.get('backup')
        _original_basename = mvs_copy_args.get('_original_basename', None)
        mode         = mvs_copy_args.get('mode', None)
        force        = mvs_copy_args.get('force', )
        validate     = mvs_copy_args.get('validate', None)
        follow       = mvs_copy_args.get('follow')
        local_follow = mvs_copy_args.get('local_follow')
        mode         = mvs_copy_args.get('mode')
        owner        = mvs_copy_args.get('owner')
        group        = mvs_copy_args.get('group')
        remote_src   = mvs_copy_args.get('remote_src')
        checksum     = mvs_copy_args.get('checksum')
        isUSS        = mvs_copy_args.get('isUSS', False)
        isVSAM       = mvs_copy_args.get('isVSAM', False)
        useQualifier = mvs_copy_args.get('useQualifier', True)
        isBinary     = mvs_copy_args.get('isBinary', False)
        isCatalog    = mvs_copy_args.get('isCatalog', True)
        volume       = mvs_copy_args.get('volume')
        encoding     = mvs_copy_args.get('encoding')
        content      = mvs_copy_args.get('content')
        
        #if self._connection._shell.tmpdir is None:
        tmpdir =  self._make_tmp_path()
        tmp_src = self._connection._shell.join_path(tmpdir, 'source')
        
        #print(b_src)

        if os.path.isfile(b_src):
            end = '/'
            basename = b_src[b_src.rfind(end)+1:]
        
        if isUSS:
            tmp_src = dest
        
        copy_module_args = {
            'src'    : src,
            'dest'   : tmp_src,
            'force'  : force,
            'mode'   : mode,
            'content': content
        }

        self._update_module_args('copy', copy_module_args, task_vars)
        copy_action = self.get_copy_action_plugin()
        copy_action._task.args = copy_module_args
        result = merge_hash(
            result,
            copy_action.run(task_vars=task_vars)
        )
        
        #print(tmp_src)
        #print(dest)
        mvs_copy_args.update(
            dict(
                basename  = basename,
                src       = tmp_src,
                dest      = dest,
                isCatalog = isCatalog,
                isUSS     = isUSS,
                isVSAM    = isVSAM
                )
            )
        
        module_return = self._execute_module(module_name='zos_copy', module_args=mvs_copy_args, task_vars=task_vars)
        
        result = merge_hash(
            module_return,
            copy_action.run(task_vars=task_vars)
        )

        # module.exit_json(**result)
        return result
