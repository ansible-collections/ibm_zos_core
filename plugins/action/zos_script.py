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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import copy
import shlex
from os import path

from ansible.plugins.action import ActionBase
from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import encode
from ansible_collections.ibm.ibm_zos_core.plugins.action.zos_copy import ActionModule as ZosCopyActionModule


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        if result.get("skipped"):
            return result

        # TODO: use chdir in the tempfile.
        module_args = self._task.args.copy()

        # First separating the command into the script path and its args
        # if they are present.
        cmd_parts = shlex.split(module_args.get('cmd'))
        if len(cmd_parts) == 0:
            result.update(dict(
                changed=False,
                failed=True,
                invocation=dict(module_args=self._task.args),
                msg="The command could not be validated, please check that it conforms to shell syntax."
            ))
            return result

        # Copying the script when it's a local file.
        remote_src = self._process_boolean(module_args.get('remote_src'))
        if not remote_src:
            script_path = cmd_parts[0]
            script_path = path.abspath(path.normpath(script_path))

            # Getting a temporary path for the script.
            # TODO: maybe add path/prefix as an option to zos_script.
            # TODO: remove tempfile during cleanup.
            tempfile_args=dict(
                state="file"
            )

            tempfile_result = self._execute_module(
                module_name="ansible.builtin.tempfile",
                module_args=tempfile_args,
                task_vars=task_vars
            )
            result.update(tempfile_result)

            if not result.get("changed") or result.get("failed"):
                result.update(dict(
                    changed=False,
                    failed=True,
                    invocation=dict(
                        module_args=self._task.args,
                        tempfile_args=tempfile_result.get('invocation', dict()).get('module_args')
                    ),
                    msg="An error ocurred while trying to create a tempfile for the script."
                ))
                return result

            # Letting zos_copy handle the transfer of the script.
            zos_copy_args = dict(
                src=script_path,
                dest=tempfile_result.get('path'),
                force=True,
                is_binary=False,
                encoding=module_args.get('encoding'),
                use_template=module_args.get('use_template'),
                template_parameters=module_args.get('template_parameters'),
            )
            copy_task = copy.deepcopy(self._task)
            copy_task.args = zos_copy_args
            zos_copy_action_plugin = ZosCopyActionModule(
                task=copy_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj
            )

            zos_copy_result = zos_copy_action_plugin.run(task_vars=task_vars)
            result.update(zos_copy_result)

        module_args['local_charset'] = encode.Defaults.get_default_system_charset()

        module_result = self._execute_module(
            module_name='ibm.ibm_zos_core.zos_script',
            module_args=module_args,
            task_vars=task_vars
        )

        result.update(module_result)
        return result

    def _process_boolean(arg, default=False):
        try:
            return boolean(arg)
        except TypeError:
            return default