# Copyright (c) IBM Corporation 2019-2023
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

import os
import stat
import time
import shutil

from tempfile import mkstemp, gettempprefix

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible import cli

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.data_set import (
    is_member
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import encode

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import template

display = Display()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        """ handler for file transfer operations """
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        task_args = self._task.args.copy()
        del tmp

        src = task_args.get('src', None)
        dest = task_args.get('dest', None)
        content = task_args.get('content', None)

        force = _process_boolean(task_args.get('force'), default=True)
        backup = _process_boolean(task_args.get('backup'), default=False)
        local_follow = _process_boolean(task_args.get('local_follow'), default=False)
        remote_src = _process_boolean(task_args.get('remote_src'), default=False)
        is_binary = _process_boolean(task_args.get('is_binary'), default=False)
        force_lock = _process_boolean(task_args.get('force_lock'), default=False)
        executable = _process_boolean(task_args.get('executable'), default=False)
        asa_text = _process_boolean(task_args.get('asa_text'), default=False)
        ignore_sftp_stderr = _process_boolean(task_args.get("ignore_sftp_stderr"), default=False)
        backup_name = task_args.get("backup_name", None)
        encoding = task_args.get("encoding", None)
        mode = task_args.get("mode", None)
        owner = task_args.get("owner", None)
        group = task_args.get("group", None)

        is_src_dir = False
        temp_path = is_uss = None

        if dest:
            if not isinstance(dest, string_types):
                msg = "Invalid type supplied for 'dest' option, it must be a string"
                return self._exit_action(result, msg, failed=True)
            else:
                is_uss = "/" in dest
        else:
            msg = "Destination is required"
            return self._exit_action(result, msg, failed=True)

        if src:
            if content:
                msg = "Either 'src' or 'content' can be provided; not both."
                return self._exit_action(result, msg, failed=True)

            elif not isinstance(src, string_types):
                msg = "Invalid type supplied for 'src' option, it must be a string"
                return self._exit_action(result, msg, failed=True)

            elif len(src) < 1 or len(dest) < 1:
                msg = "'src' or 'dest' must not be empty"
                return self._exit_action(result, msg, failed=True)
            else:
                if not remote_src:
                    if src.startswith('~'):
                        src = os.path.expanduser(src)
                    src = os.path.realpath(src)
                    is_src_dir = os.path.isdir(src)

        if not src and not content:
            msg = "'src' or 'content' is required"
            return self._exit_action(result, msg, failed=True)

        if encoding and is_binary:
            msg = "The 'encoding' parameter is not valid for binary transfer"
            return self._exit_action(result, msg, failed=True)

        if (not backup) and backup_name is not None:
            msg = "Backup file provided but 'backup' parameter is False"
            return self._exit_action(result, msg, failed=True)

        if is_binary and asa_text:
            msg = "Both 'is_binary' and 'asa_text' are True. Unable to copy binary data as an ASA text file."
            return self._exit_action(result, msg, failed=True)

        if executable and asa_text:
            msg = "Both 'executable' and 'asa_text' are True. Unable to copy an executable as an ASA text file."
            return self._exit_action(result, msg, failed=True)

        use_template = _process_boolean(task_args.get("use_template"), default=False)
        if remote_src and use_template:
            msg = "Use of Jinja2 templates is only valid for local files, remote_src cannot be set to true."
            return self._exit_action(result, msg, failed=True)

        if not is_uss:
            if mode or owner or group:
                msg = "Cannot specify 'mode', 'owner' or 'group' for MVS destination"
                return self._exit_action(result, msg, failed=True)

        if force_lock:
            display.warning(
                msg="Using force_lock uses operations that are subject to race conditions and can lead to data loss, use with caution.")
        template_dir = None

        if not remote_src:
            if local_follow and not src:
                msg = "No path given for local symlink"
                return self._exit_action(result, msg, failed=True)

            elif src and not os.path.exists(src):
                msg = "The local file {0} does not exist".format(src)
                return self._exit_action(result, msg, failed=True)

            elif src and not os.access(src, os.R_OK):
                msg = (
                    "The local file {0} does not have appropriate "
                    "read permission".format(src)
                )
                return self._exit_action(result, msg, failed=True)

            if content:
                try:
                    local_content = _write_content_to_temp_file(content)
                    transfer_res = self._copy_to_remote(
                        local_content, ignore_stderr=ignore_sftp_stderr
                    )
                finally:
                    os.remove(local_content)
            else:
                if is_src_dir:
                    path, dirs, files = next(os.walk(src))
                    if not is_uss and dirs:
                        result["msg"] = "Cannot copy a source directory with subdirectories to a data set, the destination must be another directory"
                        result.update(
                            dict(src=src, dest=dest, changed=False, failed=True)
                        )
                        return result

                    if use_template:
                        template_parameters = task_args.get("template_parameters", dict())
                        if encoding:
                            template_encoding = encoding.get("from", None)
                        else:
                            template_encoding = None

                        try:
                            renderer = template.create_template_environment(
                                template_parameters,
                                src,
                                template_encoding
                            )
                            template_dir, rendered_dir = renderer.render_dir_template(
                                task_vars.get("vars", dict())
                            )
                        except Exception as err:
                            if template_dir:
                                shutil.rmtree(template_dir, ignore_errors=True)
                            return self._exit_action(result, str(err), failed=True)

                        src = rendered_dir

                else:
                    if mode == "preserve":
                        task_args["mode"] = "0{0:o}".format(
                            stat.S_IMODE(os.stat(src).st_mode)
                        )

                    if use_template:
                        template_parameters = task_args.get("template_parameters", dict())
                        if encoding:
                            template_encoding = encoding.get("from", None)
                        else:
                            template_encoding = None

                        try:
                            renderer = template.create_template_environment(
                                template_parameters,
                                src,
                                template_encoding
                            )
                            template_dir, rendered_file = renderer.render_file_template(
                                os.path.basename(src),
                                task_vars.get("vars", dict())
                            )
                        except Exception as err:
                            if template_dir:
                                shutil.rmtree(template_dir, ignore_errors=True)
                            return self._exit_action(result, str(err), failed=True)

                        src = rendered_file

                display.vvv(u"ibm_zos_copy calculated size: {0}".format(os.stat(src).st_size), host=self._play_context.remote_addr)
                transfer_res = self._copy_to_remote(
                    src, is_dir=is_src_dir, ignore_stderr=ignore_sftp_stderr
                )

            temp_path = transfer_res.get("temp_path")
            if transfer_res.get("msg"):
                return transfer_res
            display.vvv(u"ibm_zos_copy temp path: {0}".format(transfer_res.get("temp_path")), host=self._play_context.remote_addr)

        if not encoding:
            encoding = {
                "from": encode.Defaults.get_default_system_charset(),
            }

        """
        We format temp_path correctly to pass it as src option to the module,
        we keep the original source to return to the user and avoid confusion
        by returning the temp_path created.
        """
        original_src = task_args.get("src")
        if original_src:
            if not remote_src:
                base_name = os.path.basename(original_src)
                if original_src.endswith("/"):
                    src = temp_path + "/"
                else:
                    src = temp_path
        else:
            src = temp_path

        task_args.update(
            dict(
                src=src,
                encoding=encoding,
            )
        )
        copy_res = self._execute_module(
            module_name="ibm.ibm_zos_core.zos_copy",
            module_args=task_args,
            task_vars=task_vars,
        )

        # Erasing all rendered Jinja2 templates from the controller.
        if template_dir:
            shutil.rmtree(template_dir, ignore_errors=True)

        if copy_res.get("note") and not force:
            result["note"] = copy_res.get("note")
            return result

        if copy_res.get("msg"):
            result.update(
                dict(
                    msg=copy_res.get("msg"),
                    stdout=copy_res.get("stdout") or copy_res.get("module_stdout"),
                    stderr=copy_res.get("stderr") or copy_res.get("module_stderr"),
                    stdout_lines=copy_res.get("stdout_lines"),
                    stderr_lines=copy_res.get("stderr_lines"),
                    rc=copy_res.get("rc"),
                    invocation=dict(module_args=self._task.args),
                )
            )
            if backup or backup_name:
                result["backup_name"] = copy_res.get("backup_name")
            self._remote_cleanup(dest, copy_res.get("dest_exists"), task_vars)
            return result

        return _update_result(is_binary, copy_res, self._task.args, original_src)

    def _copy_to_remote(self, src, is_dir=False, ignore_stderr=False):
        """Copy a file or directory to the remote z/OS system """

        temp_path = "/{0}/{1}/{2}".format(gettempprefix(), _create_temp_path_name(), os.path.basename(src))
        self._connection.exec_command("mkdir -p {0}".format(os.path.dirname(temp_path)))
        _src = src.replace("#", "\\#")
        _sftp_action = 'put'
        full_temp_path = temp_path

        if is_dir:
            src = src.rstrip("/") if src.endswith("/") else src
            temp_path = os.path.dirname(temp_path)
            base = os.path.basename(src)
            self._connection.exec_command("mkdir -p {0}/{1}".format(temp_path, base))
            _sftp_action += ' -r'    # add '-r` to clone the source trees

        # To support multiple Ansible versions we must do some version detection and act accordingly
        version_inf = cli.CLI.version_info(False)
        version_major = version_inf['major']
        version_minor = version_inf['minor']

        # Override the Ansible Connection behavior for this module and track users configuration
        sftp_transfer_method = "sftp"
        user_ssh_transfer_method = None
        is_ssh_transfer_method_updated = False

        try:
            if version_major == 2 and version_minor >= 11:
                user_ssh_transfer_method = self._connection.get_option('ssh_transfer_method')

                if user_ssh_transfer_method != sftp_transfer_method:
                    self._connection.set_option('ssh_transfer_method', sftp_transfer_method)
                    is_ssh_transfer_method_updated = True

            elif version_major == 2 and version_minor <= 10:
                user_ssh_transfer_method = self._play_context.ssh_transfer_method

                if user_ssh_transfer_method != sftp_transfer_method:
                    self._play_context.ssh_transfer_method = sftp_transfer_method
                    is_ssh_transfer_method_updated = True

            if is_ssh_transfer_method_updated:
                display.vvv(u"ibm_zos_copy SSH transfer method updated from {0} to {1}.".format(user_ssh_transfer_method,
                            sftp_transfer_method), host=self._play_context.remote_addr)

            display.vvv(u"ibm_zos_copy: {0} {1} TO {2}".format(_sftp_action, _src, temp_path), host=self._play_context.remote_addr)
            (returncode, stdout, stderr) = self._connection._file_transport_command(_src, temp_path, _sftp_action)

            display.vvv(u"ibm_zos_copy return code: {0}".format(returncode), host=self._play_context.remote_addr)
            display.vvv(u"ibm_zos_copy stdout: {0}".format(stdout), host=self._play_context.remote_addr)
            display.vvv(u"ibm_zos_copy stderr: {0}".format(stderr), host=self._play_context.remote_addr)

            ansible_verbosity = None
            ansible_verbosity = display.verbosity
            display.vvv(u"play context verbosity: {0}".format(ansible_verbosity), host=self._play_context.remote_addr)

            # ************************************************************************* #
            # When plugin shh connection member _build_command(..) detects verbosity    #
            # greater than 3, it constructs a command that includes verbosity like      #
            # 'EXEC sftp -b - -vvv ...' where this then is returned in the connections  #
            # stream as 'stderr' and if a user has not set ignore_stderr it will fail   #
            # the modules execution. So in cases where verbosity                        #
            # (ansible.cfg verbosity = n || CLI -vvv) are collectively summed and       #
            # amount to greater than 3, ignore_stderr will be set to 'True' so that     #
            # 'err' which will not be None won't fail the module. 'stderr' does not     #
            # in our z/OS case actually mean an error happened, it just so happens      #
            # the verbosity is returned as 'stderr'.                                    #
            # ************************************************************************* #

            err = _detect_sftp_errors(stderr)

            if ansible_verbosity > 3:
                ignore_stderr = True

            if returncode != 0 or (err and not ignore_stderr):
                return dict(
                    msg="Error transfering source '{0}' to remote z/OS system".format(src),
                    rc=returncode,
                    stderr=err,
                    stderr_lines=err.splitlines(),
                    failed=True,
                )

        finally:
            # Restore the users defined option `ssh_transfer_method` if it was overridden

            if is_ssh_transfer_method_updated:
                if version_major == 2 and version_minor >= 11:
                    self._connection.set_option('ssh_transfer_method', user_ssh_transfer_method)

                elif version_major == 2 and version_minor <= 10:
                    self._play_context.ssh_transfer_method = user_ssh_transfer_method

                display.vvv(u"ibm_zos_copy SSH transfer method restored to {0}".format(user_ssh_transfer_method), host=self._play_context.remote_addr)
                is_ssh_transfer_method_updated = False

        return dict(temp_path=full_temp_path)

    def _remote_cleanup(self, dest, dest_exists, task_vars):
        """Remove all files or data sets pointed to by 'dest' on the remote
        z/OS system. The idea behind this cleanup step is that if, for some
        reason, the module fails after copying the data, we want to return the
        remote system to its original state. Which means deleting any newly
        created files or data sets.
        """
        if dest_exists is False:
            if "/" in dest:
                self._connection.exec_command("rm -rf {0}".format(dest))
            else:
                module_args = dict(name=dest, state="absent")
                if is_member(dest):
                    module_args["type"] = "MEMBER"
                self._execute_module(
                    module_name="ibm.ibm_zos_core.zos_data_set",
                    module_args=module_args,
                    task_vars=task_vars,
                )

    def _exit_action(self, result, msg, failed=False):
        """Exit action plugin with a message"""
        result.update(
            dict(
                changed=False,
                failed=failed,
                invocation=dict(module_args=self._task.args),
            )
        )
        if failed:
            result["msg"] = msg
        else:
            result["note"] = msg
        return result


def _update_result(is_binary, copy_res, original_args, original_src):
    """ Helper function to update output result with the provided values """
    ds_type = copy_res.get("ds_type")
    src = copy_res.get("src")
    note = copy_res.get("note")
    backup_name = copy_res.get("backup_name")
    dest_data_set_attrs = copy_res.get("dest_data_set_attrs")
    updated_result = dict(
        dest=copy_res.get("dest"),
        is_binary=is_binary,
        changed=copy_res.get("changed"),
        invocation=dict(module_args=original_args),
    )
    if src:
        updated_result["src"] = original_src
    if note:
        updated_result["note"] = note
    if backup_name:
        updated_result["backup_name"] = backup_name
    if ds_type == "USS":
        updated_result.update(
            dict(
                gid=copy_res.get("gid"),
                uid=copy_res.get("uid"),
                group=copy_res.get("group"),
                owner=copy_res.get("owner"),
                mode=copy_res.get("mode"),
                state=copy_res.get("state"),
                size=copy_res.get("size"),
            )
        )
        checksum = copy_res.get("checksum")
        if checksum:
            updated_result["checksum"] = checksum
    if dest_data_set_attrs is not None:
        if len(dest_data_set_attrs) > 0:
            dest_data_set_attrs.pop("name")
            updated_result["dest_created"] = True
            updated_result["destination_attributes"] = dest_data_set_attrs

    return updated_result


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default


def _create_temp_path_name():
    """Create a temporary path name"""
    current_date = time.strftime("D%y%m%d", time.localtime())
    current_time = time.strftime("T%H%M%S", time.localtime())
    return "ansible-zos-copy-payload-{0}-{1}".format(current_date, current_time)


def _detect_sftp_errors(stderr):
    """Detects if the stderr of the SFTP command contains any errors.
       The SFTP command usually returns zero return code even if it
       encountered an error while transferring data. Hence the need to parse
       its stderr to determine what error it ran into.
    """
    # The first line of stderr is a connection acknowledgement,
    # which can be ignored
    lines = to_text(stderr).splitlines()
    if len(lines) > 1:
        return "".join(lines[1:])
    return ""


def _write_content_to_temp_file(content):
    """Write given content to a temp file and return its path """
    fd, path = mkstemp()
    try:
        with os.fdopen(fd, "w") as infile:
            infile.write(content)
    except (OSError, IOError) as err:
        os.remove(path)
        raise AnsibleError(
            "Unable to write content to temporary file: {0}".format(repr(err))
        )
    return path
