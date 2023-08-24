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

from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible.module_utils.parsing.convert_bool import boolean
import os
import copy
from ansible_collections.ibm.ibm_zos_core.plugins.action.zos_copy import ActionModule as ZosCopyActionModule


USS_SUPPORTED_FORMATS = ['tar', 'zip', 'bz2', 'pax', 'gz']
MVS_SUPPORTED_FORMATS = ['terse', 'xmit']

display = Display()


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        if result.get("skipped"):
            return result

        module_args = self._task.args.copy()

        if module_args.get("remote_src", False):
            result.update(
                self._execute_module(
                    module_name="ibm.ibm_zos_core.zos_unarchive",
                    module_args=module_args,
                    task_vars=task_vars,
                )
            )
        else:
            source = module_args.get("src")
            force = _process_boolean(module_args.get("force"))
            format = self._task.args.get("format")
            format_name = format.get("name")
            copy_module_args = dict()
            dest_data_set = format.get("dest_data_set")
            if dest_data_set is None:
                dest_data_set = dict()
            dest = ""
            if source.startswith('~'):
                source = os.path.expanduser(source)
            source = os.path.realpath(source)

            if format_name in USS_SUPPORTED_FORMATS:
                dest = self._execute_module(
                    module_name="tempfile", module_args={}, task_vars=task_vars,
                ).get("path")
            elif format_name in MVS_SUPPORTED_FORMATS:
                tmp_hlq = module_args.get("tmp_hlq") if module_args.get("tmp_hlq") is not None else ""
                cmd_res = self._execute_module(
                    module_name="command",
                    module_args=dict(
                        _raw_params="mvstmp {0}".format(tmp_hlq)
                    ),
                    task_vars=task_vars,
                )
                dest = cmd_res.get("stdout")
                if dest_data_set.get("space_primary") is None:
                    dest_data_set.update(space_primary=5, space_type="M")
                if format_name == 'terse':
                    dest_data_set.update(type='SEQ', record_format='FB', record_length=1024)
                if format_name == 'xmit':
                    dest_data_set.update(type='SEQ', record_format='FB', record_length=80)

            copy_module_args.update(
                dict(
                    src=source,
                    dest=dest,
                    dest_data_set=dest_data_set,
                    force=force,
                    is_binary=True,
                )
            )
            copy_task = copy.deepcopy(self._task)
            copy_task.args = copy_module_args
            zos_copy_action_module = ZosCopyActionModule(task=copy_task,
                                                         connection=self._connection,
                                                         play_context=self._play_context,
                                                         loader=self._loader,
                                                         templar=self._templar,
                                                         shared_loader_obj=self._shared_loader_obj)
            result.update(zos_copy_action_module.run(task_vars=task_vars))
            display.vvv(u"Copy result {0}".format(result), host=self._play_context.remote_addr)
            if result.get("msg") is None:
                module_args["src"] = dest

                result.update(
                    self._execute_module(
                        module_name="ibm.ibm_zos_core.zos_unarchive",
                        module_args=module_args,
                        task_vars=task_vars,
                    )
                )
            else:
                result.update(dict(failed=True))
        return result
