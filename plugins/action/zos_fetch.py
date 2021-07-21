# Copyright (c) IBM Corporation 2019, 2020, 2021
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
import subprocess
import re

from hashlib import sha256
from ansible.module_utils._text import to_bytes, to_text
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import encode

SUPPORTED_DS_TYPES = frozenset({"PS", "PO", "VSAM", "USS"})

display = Display()


def _update_result(result, src, dest, ds_type="USS", is_binary=False):
    """ Helper function to update output result with the provided values """
    data_set_types = {
        "PS": "Sequential",
        "PO": "Partitioned",
        "PDSE": "Partitioned Extended",
        "PE": "Partitioned Extended",
        "VSAM": "VSAM",
        "USS": "USS",
    }
    file_or_ds = "file" if ds_type == "USS" else "data set"
    updated_result = dict((k, v) for k, v in result.items())
    updated_result.update(
        {
            "file": src,
            "dest": dest,
            "data_set_type": data_set_types[ds_type],
            "is_binary": is_binary,
        }
    )
    return updated_result


def _process_boolean(arg, default=False):
    """ Return boolean representation of arg.
        If arg is None, return the default value
    """
    try:
        return boolean(arg)
    except TypeError:
        return default


def _get_file_checksum(src):
    """ Calculate SHA256 hash for a given file """
    b_src = to_bytes(src)
    if not os.path.exists(b_src) or os.path.isdir(b_src):
        return None
    blksize = 64 * 1024
    hash_digest = sha256()
    try:
        with open(to_bytes(src, errors="surrogate_or_strict"), "rb") as infile:
            block = infile.read(blksize)
            while block:
                hash_digest.update(block)
                block = infile.read(blksize)
    except Exception as err:
        raise AnsibleError("Unable to calculate checksum: {0}".format(str(err)))
    return hash_digest.hexdigest()


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


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        # ********************************************************** #
        #                 Parameter initializations                  #
        # ********************************************************** #

        src = self._task.args.get('src')
        dest = self._task.args.get('dest')
        encoding = self._task.args.get('encoding')
        # Option sftp_port is deprecated in 1.4.0 to be removed in 1.5.0
        sftp_port = self._task.args.get('sftp_port', self._play_context.port or 22)
        flat = _process_boolean(self._task.args.get('flat'), default=False)
        is_binary = _process_boolean(self._task.args.get('is_binary'))
        ignore_sftp_stderr = _process_boolean(
            self._task.args.get("ignore_sftp_stderr"), default=False
        )
        validate_checksum = _process_boolean(
            self._task.args.get("validate_checksum"), default=True
        )

        # ********************************************************** #
        #                 Parameter sanity checks                    #
        # ********************************************************** #

        msg = None
        if src is None or dest is None:
            msg = "Source and destination are required"
        elif not isinstance(src, string_types):
            msg = "Invalid type supplied for 'source' option, it must be a string"
        elif not isinstance(dest, string_types):
            msg = (
                "Invalid type supplied for 'destination' option, it must be a string"
            )
        elif len(src) < 1 or len(dest) < 1:
            msg = "Source and destination parameters must not be empty"

        # elif not isinstance(sftp_port, int) or not 0 < sftp_port <= 65535:
        #     msg = "Invalid port provided for SFTP. Expected an integer between 0 to 65535."

        if msg:
            result["msg"] = msg
            result["failed"] = True
            return result

        ds_type = None
        fetch_member = "(" in src and src.endswith(")")
        if fetch_member:
            member_name = src[src.find("(") + 1: src.find(")")]
        src = self._connection._shell.join_path(src)
        src = self._remote_expand_user(src)

        # ********************************************************** #
        #  Determine destination path:                               #
        #  1. If the 'flat' parameter is 'false', then hostname      #
        #     will be appended to dest.                              #
        #  2. If 'flat' is 'true', then dest must not be a directory.#
        #     If it is a directory, a trailing forward slash must    #
        #     be added.                                              #
        # ********************************************************** #

        # ********************************************************** #
        #  If a data set member is being fetched, extract the member #
        #  name and update dest with the name of the member.         #
        #  For instance: If src is: USER.TEST.PROCLIB(DATA)          #
        #  and dest is: /tmp/, then updated dest would be /tmp/DATA  #
        # ********************************************************** #

        if os.path.sep not in self._connection._shell.join_path("a", ""):
            src = self._connection._shell._unquote(src)
            source_local = src.replace("\\", "/")
        else:
            source_local = src

        dest = os.path.expanduser(dest)
        if flat:
            if os.path.isdir(
                to_bytes(dest, errors="surrogate_or_strict")
            ) and not dest.endswith(os.sep):
                result["msg"] = (
                    "dest is an existing directory, append a forward "
                    "slash to the dest if you want to fetch src into "
                    "that directory"
                )
                result["failed"] = True
                return result
            if dest.endswith(os.sep):
                if fetch_member:
                    base = os.path.dirname(dest)
                    dest = os.path.join(base, member_name)
                else:
                    base = os.path.basename(source_local)
                    dest = os.path.join(dest, base)
            if not dest.startswith("/"):
                dest = self._loader.path_dwim(dest)
        else:
            if "inventory_hostname" in task_vars:
                target_name = task_vars["inventory_hostname"]
            else:
                target_name = self._play_context.remote_addr
            suffix = member_name if fetch_member else source_local
            dest = "{0}/{1}/{2}".format(
                self._loader.path_dwim(dest), target_name, suffix
            )
            try:
                dirname = os.path.dirname(dest).replace("//", "/")
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            except OSError as err:
                result["msg"] = "Unable to create destination directory {0}".format(
                    dirname
                )
                result["stderr"] = str(err)
                result["stderr_lines"] = str(err).splitlines()
                result["failed"] = True
                return result

        dest = dest.replace("//", "/")
        local_checksum = _get_file_checksum(dest)

        # ********************************************************** #
        #                Execute module on remote host               #
        # ********************************************************** #
        new_module_args = self._task.args.copy()
        new_module_args.update(
            dict(local_charset=encode.Defaults.get_default_system_charset())
        )
        remote_path = None
        try:
            fetch_res = self._execute_module(
                module_name="ibm.ibm_zos_core.zos_fetch",
                module_args=new_module_args,
                task_vars=task_vars
            )
            ds_type = fetch_res.get("ds_type")
            src = fetch_res.get("file")
            remote_path = fetch_res.get("remote_path")

            if fetch_res.get("msg"):
                result["msg"] = fetch_res.get("msg")
                result["stdout"] = fetch_res.get("stdout") or fetch_res.get(
                    "module_stdout"
                )
                result["stderr"] = fetch_res.get("stderr") or fetch_res.get(
                    "module_stderr"
                )
                result["stdout_lines"] = fetch_res.get("stdout_lines")
                result["stderr_lines"] = fetch_res.get("stderr_lines")
                result["rc"] = fetch_res.get("rc")
                result["failed"] = True
                return result

            elif fetch_res.get("note"):
                result["note"] = fetch_res.get("note")
                return result

            if ds_type in SUPPORTED_DS_TYPES:
                if ds_type == "PO" and os.path.isfile(dest) and not fetch_member:
                    result[
                        "msg"
                    ] = "Destination must be a directory to fetch a partitioned data set"
                    result["failed"] = True
                    return result

                fetch_content = self._transfer_remote_content(
                    dest,
                    remote_path,
                    ds_type,
                    ignore_stderr=ignore_sftp_stderr,
                )
                if fetch_content.get("msg"):
                    return fetch_content

                if validate_checksum and ds_type != "PO" and not is_binary:
                    new_checksum = _get_file_checksum(dest)
                    result["changed"] = local_checksum != new_checksum
                    result["checksum"] = new_checksum
                else:
                    result["changed"] = True

            else:
                result["msg"] = (
                    "The data set type '{0}' is not"
                    " currently supported".format(ds_type)
                )
                result["failed"] = True
                return result
        except Exception as err:
            result["msg"] = "Failure during module execution"
            result["stderr"] = str(err)
            result["stderr_lines"] = str(err).splitlines()
            result["failed"] = True
            return result

        # ********************************************************** #
        #              Cleanup temp files and directories            #
        # ********************************************************** #

        finally:
            self._remote_cleanup(remote_path, ds_type, encoding)
        return _update_result(result, src, dest, ds_type, is_binary=is_binary)

    def _transfer_remote_content(
        self, dest, remote_path, src_type, ignore_stderr=False
    ):
        """ Transfer a file or directory from USS to local machine.
            After the transfer is complete, the USS file or directory will
            be removed.
        """
        result = dict()
        _sftp_action = 'get'

        if src_type == "PO":
            _sftp_action += ' -r'    # add '-r` to clone the source trees

        display.vvv(u"{0} {1} TO {2}".format(_sftp_action, remote_path, dest), host=self._play_context.remote_addr)
        (returncode, stdout, stderr) = self._connection._file_transport_command(remote_path, dest, _sftp_action)

        display.vvv(u"ibm_zos_fetch return code: {0}".format(returncode), host=self._play_context.remote_addr)
        display.vvv(u"ibm_zos_fetch stdout: {0}".format(stdout), host=self._play_context.remote_addr)
        display.vvv(u"ibm_zos_fetch stderr: {0}".format(stderr), host=self._play_context.remote_addr)
        display.vvv(u"play context verbosity: {0}".format(self._play_context.verbosity), host=self._play_context.remote_addr)

        err = _detect_sftp_errors(stderr)

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

        if self._play_context.verbosity > 3:
            ignore_stderr = True

        if re.findall(r"Permission denied", err):
            result["msg"] = "Insufficient write permission for destination {0}".format(
                dest
            )
        elif returncode != 0 or (err and not ignore_stderr):
            result["msg"] = "Error transferring remote data from z/OS system"
            result["rc"] = returncode
        if result.get("msg"):
            result["stderr"] = err
            result["failed"] = True
        return result

    def _remote_cleanup(self, remote_path, src_type, encoding):
        """Remove all temporary files and directories from the remote system"""
        # When fetching USS files and no encoding parameter is provided
        # do not remove the original file.
        if not (src_type == "USS" and not encoding):
            rm_cmd = "rm -r {0}".format(remote_path)
            if src_type != "PO":
                rm_cmd = rm_cmd.replace(" -r", "")
            self._connection.exec_command(rm_cmd)
