# Copyright (c) IBM Corporation 2019, 2024
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
from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.utils.display import Display
# from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.parsing.convert_bool import boolean
import os
import copy

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import template
from ansible_collections.ibm.ibm_zos_core.plugins.action.zos_copy import ActionModule as ZosCopyActionModule


display = Display()

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import template


display = Display()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        """ handler for file transfer operations """
        if task_vars is None:
            task_vars = {}

        result = super(ActionModule, self).run(tmp, task_vars)

        if result.get("skipped"):
            return result

        module_args = self._task.args.copy()

        use_template = _process_boolean(module_args.get("use_template"))
        location = module_args.get("location")
        if use_template and location != "local":
            result.update(dict(
                failed=True,
                changed=False,
                msg="Use of Jinja2 templates is only valid for local files. Location is set to '{0}' but should be 'local'".format(location)
            ))
            return result

        if location == "local":

            source = self._task.args.get("src", None)

            # Get a temporary file on the managed node
            tempfile = self._execute_module(
                module_name="tempfile", module_args={}, task_vars=task_vars,
            )
            dest_path = tempfile.get("path")
            # Calling execute_module from this step with tempfile leaves behind a tmpdir.
            # This is called to ensure the proper removal.
            tmpdir = self._connection._shell.tmpdir
            if tmpdir:
                self._remove_tmp_path(tmpdir)

            result["failed"] = True
            if source is None:
                result["msg"] = "Source is required."
            elif dest_path is None:
                result["msg"] = "Failed copying to remote, destination file was not created. {0}".format(tempfile.get("msg"))
            elif source is not None and os.path.isdir(to_bytes(source, errors="surrogate_or_strict")):
                result["msg"] = "Source must be a file."
            else:
                del result["failed"]

            if result.get("failed"):
                return result

            try:
                source = self._find_needle("files", source)
            except AnsibleError as e:
                result["failed"] = True
                result["msg"] = to_text(e)
                return result

            if tmp is None or "-tmp-" not in tmp:
                tmp = self._make_tmp_path()

            source_full = None
            try:
                source_full = self._loader.get_real_file(source)
                # source_rel = os.path.basename(source)
            except AnsibleFileNotFound as e:
                result["failed"] = True
                result["msg"] = "Source {0} not found. {1}".format(source_full, e)
                self._remove_tmp_path(tmp)
                return result

            # if self._connection._shell.path_has_trailing_slash(dest):
            #     dest_file = self._connection._shell.join_path(dest, source_rel)
            # else:
            self._connection._shell.join_path(dest_path)

            tmp_src = self._connection._shell.join_path(tmp, "source")

            rendered_file = None
            if use_template:
                template_parameters = module_args.get("template_parameters", dict())
                encoding = module_args.get("encoding", dict())

                try:
                    renderer = template.create_template_environment(
                        template_parameters,
                        source_full,
                        encoding.get("from", None)
                    )
                    template_dir, rendered_file = renderer.render_file_template(
                        os.path.basename(source_full),
                        task_vars
                    )
                except Exception as err:
                    result["msg"] = to_text(err)
                    result["failed"] = True
                    result["changed"] = False
                    result["invocation"] = dict(module_args=module_args)
                    return result

                source_full = rendered_file

            remote_path = None
            remote_path = self._transfer_file(source_full, tmp_src)

            if remote_path:
                self._fixup_perms2((tmp, remote_path))

            result = {}
            copy_module_args = {}
            module_args = self._task.args.copy()

            copy_module_args.update(
                dict(
                    src=tmp_src,
                    dest=dest_path,
                    mode="0600",
                    force=True,
                    encoding=module_args.get('encoding'),
                    remote_src=True,
                )
            )
            copy_task = self._task.copy()
            copy_task.args = copy_module_args
            copy_action = self._shared_loader_obj.action_loader.get(
                'ibm.ibm_zos_core.zos_copy',
                task=copy_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj)
            result.update(copy_action.run(task_vars=task_vars))
            if result.get("msg") is None:
                module_args["src"] = dest_path
                result.update(
                    self._execute_module(
                        module_name="ibm.ibm_zos_core.zos_job_submit",
                        module_args=module_args,
                        task_vars=task_vars,
                    )
                )
            else:
                result.update(dict(failed=True))

        else:
            result.update(
                self._execute_module(
                    module_name="ibm.ibm_zos_core.zos_job_submit",
                    module_args=module_args,
                    task_vars=task_vars,
                )
            )

        def delete_dict_entries(entries, dictionary):
            """ Deletes entries from a dictionary when provided key and dictionary.

                Arguments:
                    entries    (tuple)  - entries to delete from dictionary
                    dictionary (dic)    - dictionary to remove entries
            """
            for key in entries:
                if key in dictionary:
                    del dictionary[key]

        # Currently the direction is undecided if we should continue to use the
        # community action plugins or transition to SFTP, so this code
        # can remain should we want to clean up unrelated response values.
        # entries = ('checksum', 'dest', 'gid', 'group', 'md5sum', 'mode', 'owner', 'size', 'src', 'state', 'uid')
        # delete_dict_entries(entries, result)
        return result


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default
