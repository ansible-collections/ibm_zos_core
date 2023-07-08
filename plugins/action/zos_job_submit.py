# Copyright (c) IBM Corporation 2019, 2020, 2023
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
# from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.module_utils.parsing.convert_bool import boolean
import os

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import template


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
        if use_template and location != "LOCAL":
            result.update(dict(
                failed=True,
                changed=False,
                msg="Use of Jinja2 templates is only valid for local files. Location is set to '{0}' but should be 'LOCAL'".format(location)
            ))
            return result

        if module_args["location"] == "LOCAL":

            source = self._task.args.get("src", None)

            # Get a temporary file on the managed node
            dest_path = self._execute_module(
                module_name="tempfile", module_args={}, task_vars=task_vars,
            ).get("path")

            result["failed"] = True
            if source is None or dest_path is None:
                result["msg"] = "src and dest are required"
            elif source is not None and source.endswith("/"):
                result["msg"] = "src must be a file"
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

            if os.path.isdir(to_bytes(source, errors="surrogate_or_strict")):
                result["failed"] = True
                result["msg"] = to_text("NOT SUPPORTING THE DIRECTORY.")
                return result

            if tmp is None or "-tmp-" not in tmp:
                tmp = self._make_tmp_path()

            source_full = None
            try:
                source_full = self._loader.get_real_file(source)
                source_rel = os.path.basename(source)
            except AnsibleFileNotFound as e:
                result["failed"] = True
                result["msg"] = "could not find src=%s, %s" % (source_full, e)
                self._remove_tmp_path(tmp)
                return result

            # if self._connection._shell.path_has_trailing_slash(dest):
            #     dest_file = self._connection._shell.join_path(dest, source_rel)
            # else:
            dest_file = self._connection._shell.join_path(dest_path)

            dest_status = self._execute_remote_stat(
                dest_file, all_vars=task_vars, follow=False
            )

            if dest_status["exists"] and dest_status["isdir"]:
                self._remove_tmp_path(tmp)
                result["failed"] = True
                result["msg"] = "can not use content with a dir as dest"
                return result

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
            module_args["temp_file"] = dest_path

            copy_module_args.update(
                dict(
                    src=tmp_src,
                    dest=dest_path,
                    mode="0600",
                    _original_basename=source_rel,
                )
            )
            result.update(
                self._execute_module(
                    module_name="copy",
                    module_args=copy_module_args,
                    task_vars=task_vars,
                )
            )
            result.update(
                self._execute_module(
                    module_name="ibm.ibm_zos_core.zos_job_submit",
                    module_args=module_args,
                    task_vars=task_vars,
                )
            )

            if rendered_file:
                os.remove(rendered_file)

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
