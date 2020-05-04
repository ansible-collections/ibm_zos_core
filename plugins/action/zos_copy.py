# Copyright (c) 2019, 2020 Lu Zhao <zlbjlu@cn.ibm.com>
# Copyright (c) IBM Corporation 2020
# LICENSE: [GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import stat
import re
import time
import subprocess

from tempfile import mkstemp
from pathlib import Path

from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.hashing import checksum as file_checksum
from ansible.utils.vars import merge_hash


def _update_result(is_binary, **copy_res):
    """ Helper function to update output result with the provided values """
    ds_type = copy_res.get("ds_type")
    updated_result = dict(
        file=copy_res.get("src"),
        dest=copy_res.get("dest"),
        is_binary=is_binary,
        changed=copy_res.get("changed")
    )
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
                checksum=copy_res.get("checksum"),
            )
        )
    if copy_res.get("backup_file"):
        updated_result['backup_file'] = copy_res.get("backup_file")
    return updated_result


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default


def _create_temp_path_name():
    current_date = time.strftime("D%y%m%d", time.localtime())
    current_time = time.strftime("T%H%M%S", time.localtime())
    return "/tmp/ansible-zos-copy-payload-{0}-{1}".format(current_date, current_time)


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
        with os.fdopen(fd, 'w') as infile:
            infile.write(content)
    except (OSError, IOError) as err:
        os.remove(path)
        raise AnsibleError("Unable to write content to temporary file")
    return path


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        """ handler for file transfer operations """
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        
        src = self._task.args.get('src', None)
        b_src = to_bytes(src, errors='surrogate_or_strict')
        dest = self._task.args.get('dest', None)
        b_dest = to_bytes(dest, errors='surrogate_or_strict')
        content = self._task.args.get('content', None)
        backup = _process_boolean(self._task.args.get('backup'), default=False)
        local_follow = _process_boolean(self._task.args.get('local_follow'), default=False)
        remote_src = _process_boolean(self._task.args.get('remote_src'), default=False)
        is_binary = _process_boolean(self._task.args.get('is_binary'), default=False)
        validate = _process_boolean(self._task.args.get('validate'), default=False)
        backup_path = self._task.args.get("backup_path", None)
        encoding = self._task.args.get('encoding', None)
        mode = self._task.args.get('mode', None)
        owner = self._task.args.get('owner', None)
        group = self._task.args.get('group', None)

        new_module_args = dict((k, v) for k, v in self._task.args.items())
        is_uss = '/' in dest
        is_pds = False
        copy_member = '(' in dest and dest.endswith(')')
        temp_path = None
        if src:
            is_pds = os.path.isdir(b_src)
            if not isinstance(src, string_types):
                result['msg'] = (
                    "Invalid type supplied for 'src' option, it must be a string"
                )
            elif len(src) < 1 or len(dest) < 1:
                result['msg'] = "'src' or 'dest' must not be empty"

        if not src and not content:
            result['msg'] = "'src' or 'content' is required"
        elif not dest:
            result['msg'] = "Destination is required"
        elif not isinstance(dest, string_types):
            result['msg'] = (
                "Invalid type supplied for 'dest' option, it must be a string"
            )
        elif content and not isinstance (content, string_types):
            result['msg'] = (
                "Invalid type supplied for 'content' option, it must be a string"
            )
        elif content and src:
            result['msg'] = "Only 'content' or 'src' can be provided, not both"

        elif encoding and is_binary:
            result['msg'] = "The 'encoding' parameter is not valid for binary transfer"

        elif (not backup) and backup_path is not None:
            result['msg'] = "Backup path provided but 'backup' parameter is False"
        
        if not is_uss:
            if mode or owner or group:
                result['msg'] = (
                    "Cannot specify 'mode', 'owner' or 'group' for MVS destination"
                )
        if not remote_src:
            if src and not os.path.exists(b_src):
                result['msg'] = "The local file {0} does not exist".format(src)
            elif src and not os.access(b_src, os.R_OK):
                result['msg'] = (
                    "The local file {0} does not have appropriate "
                    "read permisssion".format(src)
                )
            elif src and local_follow and not os.path.islink(src):
                result['msg'] = "The provided source is not a symbolic link"
            elif src and os.path.islink(b_src) and (not local_follow):
                result['msg'] = (
                    "Source is a symbolic link. If you would like to follow"
                    " symbolic links, set 'local_follow' parameter to true"
                )
            elif is_pds and is_uss:
                result['msg'] = (
                    "Source is a directory, which can not be copied "
                    "to a USS location"
                )
        
        if result.get('msg'):
            result.update(dict(src=src, dest=dest, changed=False, failed=True))
            return result

        if not remote_src:
            if content:
                try:
                    local_content = _write_content_to_temp_file(content)
                    transfer_res = self._copy_to_remote(local_content)
                finally:
                    os.remove(local_content)
            else:
                if local_follow:
                    src = os.path.realpath(src)
                if is_pds:
                    path, dirs, files = next(os.walk(src))
                    if dirs:
                        result['msg'] = "Subdirectory found inside source directory"
                        result.update(dict(src=src, dest=dest, changed=False, failed=True))
                        return result
                    dir_size = sum(Path(path + "/" + f).stat().st_size for f in files)
                    new_module_args.update(dict(size=dir_size))
                else:
                    if mode == 'preserve':
                        new_module_args['mode'] = '0{:o}'.format(stat.S_IMODE(os.stat(b_src).st_mode))
                    new_module_args['size'] = Path(src).stat().st_size
                transfer_res = self._copy_to_remote(src, is_pds=is_pds)

            temp_path = transfer_res.get("temp_path")
            if transfer_res.get("msg"):
                self._remote_cleanup(dest, True, task_vars)
                return transfer_res

        new_module_args.update(
            dict(
                is_uss=is_uss, 
                is_pds=is_pds, 
                copy_member=copy_member,
                temp_path=temp_path
            )
        )
        copy_res = (
            self._execute_module(
                module_name='zos_copy', 
                module_args=new_module_args, 
                task_vars=task_vars
            )
        )
        if copy_res.get('note'):
            result['note'] = copy_res.get('note')
            return result

        if copy_res.get('msg'):
            result.update(
                dict(
                    msg=copy_res.get('msg'),
                    stdout=copy_res.get('stdout') or copy_res.get("module_stdout"),
                    stderr=copy_res.get('stderr') or copy_res.get("module_stderr"),
                    stdout_lines=copy_res.get("stdout_lines"),
                    stderr_lines=copy_res.get("stderr_lines"),
                    rc=copy_res.get('rc')
                )   
            )
            self._remote_cleanup(dest, copy_res.get("dest_exists"), task_vars)
            return result
        try:
            result = _update_result(is_binary, **copy_res)
        except Exception as err:
            self._remote_cleanup(dest, copy_res.get("dest_exists"), task_vars)
            result['msg'] = str(err)
            result['failed'] = True

        return result

    def _copy_to_remote(self, src, is_pds=False):
        result = dict()
        ansible_user = self._play_context.remote_user
        ansible_host = self._play_context.remote_addr
        temp_path = _create_temp_path_name()
        cmd = ['sftp', ansible_user + '@' + ansible_host]
        stdin = "put -r {0} {1}".format(src, temp_path)

        if is_pds:
            base = os.path.basename(src)
            self._connection.exec_command("mkdir -p {0}/{1}".format(temp_path, base))
        else:
            stdin = stdin.replace(" -r", "")
        transfer_data = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = transfer_data.communicate(to_bytes(stdin))
        err = _detect_sftp_errors(err)
        if transfer_data.returncode != 0 or err:
            result['msg'] = "Error transfering source '{0}' to remote z/OS system".format(src)
            result['rc'] = transfer_data.returncode
            result['stderr'] = err
            result['stderr_lines'] = err.splitlines()
            result['failed'] = True
            return result

        result['temp_path'] = temp_path
        return result

    def _remote_cleanup(self, dest, dest_exists, task_vars):
        if dest_exists is False:
            if '/' in dest:
                self._connection.exec_command("rm -rf {0}".format(dest))
            else:
                module_args = dict(name=dest, state='absent')
                if dest.endswith(')'):
                    module_args['type'] = "MEMBER"
                self._execute_module(
                    module_name='zos_data_set',
                    module_args=module_args,
                    task_vars=task_vars
                )
