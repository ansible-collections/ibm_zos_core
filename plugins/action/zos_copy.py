# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

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

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)


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
            )
        )
        checksum = copy_res.get("checksum")
        if checksum:
            updated_result['checksum'] = checksum
    
    backup_file = copy_res.get("backup_file")
    if backup_file:
        updated_result['backup_file'] = backup_file
    
    return updated_result


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default


def _is_member(data_set):
    """Determine whether the input string specifies a data set member"""
    try:
        arg_def = dict(data_set=dict(arg_type='data_set_member'))
        parser = better_arg_parser.BetterArgParser(arg_def)
        parser.parse_args({'data_set': data_set})
    except ValueError:
        return False
    return True


def _is_data_set(data_set):
    """Determine whether the input string specifies a data set name"""
    try:
        arg_def = dict(data_set=dict(arg_type='data_set_base'))
        parser = better_arg_parser.BetterArgParser(arg_def)
        parser.parse_args({'data_set': data_set})
    except ValueError:
        return False
    return True


def _create_temp_path_name():
    """Create a temporary path name"""
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

        new_module_args = self._task.args
        is_pds = is_src_dir = False
        temp_path = real_path = None
        is_uss = '/' in dest if dest else None
        is_mvs_dest = _is_data_set(dest) if dest else None
        src_member = _is_member(src)
        copy_member = _is_member(dest)
        
        if src:
            src = os.path.realpath(src)
            is_src_dir = os.path.isdir(src)
            is_pds = is_src_dir and is_mvs_dest
            if content:
                result['msg'] = "Either 'src' or 'content' can be provided; not both."

            elif not isinstance(src, string_types):
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
        elif content and not isinstance(content, string_types):
            result['msg'] = (
                "Invalid type supplied for 'content' option, it must be a string"
            )
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
            if local_follow and not src:
                result['msg'] = "No path given for local symlink"

            elif src and not os.path.exists(b_src):
                result['msg'] = "The local file {0} does not exist".format(src)

            elif src and not os.access(b_src, os.R_OK):
                result['msg'] = (
                    "The local file {0} does not have appropriate "
                    "read permisssion".format(src)
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
                if is_src_dir:
                    path, dirs, files = next(os.walk(src))
                    if dirs:
                        result['msg'] = "Subdirectory found inside source directory"
                        result.update(dict(src=src, dest=dest, changed=False, failed=True))
                        return result
                    new_module_args['size'] = sum(
                        Path(path + "/" + f).stat().st_size for f in files
                    )
                else:
                    if mode == 'preserve':
                        new_module_args['mode'] = '0{:o}'.format(stat.S_IMODE(os.stat(b_src).st_mode))
                    new_module_args['size'] = Path(src).stat().st_size
                transfer_res = self._copy_to_remote(src, is_dir=is_src_dir)

            temp_path = transfer_res.get("temp_path")
            if transfer_res.get("msg"):
                return transfer_res

        new_module_args.update(
            dict(
                is_uss=is_uss, 
                is_pds=is_pds, 
                copy_member=copy_member,
                src_member=src_member,
                temp_path=temp_path,
                is_mvs_dest=is_mvs_dest
            )
        )
        copy_res = self._execute_module(
            module_name='zos_copy', 
            module_args=new_module_args, 
            task_vars=task_vars
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

    def _copy_to_remote(self, src, is_dir=False):
        """Copy a file or directory to the remote z/OS system """
        ansible_user = self._play_context.remote_user
        ansible_host = self._play_context.remote_addr
        temp_path = _create_temp_path_name()
        cmd = ['sftp', ansible_user + '@' + ansible_host]
        stdin = "put -r {0} {1}".format(src, temp_path)

        if is_dir:
            base = os.path.basename(src)
            self._connection.exec_command("mkdir -p {0}/{1}".format(temp_path, base))
        else:
            stdin = stdin.replace(" -r", "", 1)
        transfer_data = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = transfer_data.communicate(to_bytes(stdin))
        err = _detect_sftp_errors(err)

        if transfer_data.returncode != 0 or err:
            return dict(
                msg="Error transfering source '{0}' to remote z/OS system".format(src),
                rc=transfer_data.returncode,
                stderr=err,
                stderr_lines=err.splitlines(),
                failed=True
            )

        return dict(temp_path=temp_path)

    def _remote_cleanup(self, dest, dest_exists, task_vars):
        """Remove all files or data sets pointed to by 'dest' on the remote 
        z/OS system. The idea behind this cleanup step is that if, for some
        reason, the module fails after copying the data, we want to return the
        remote system to its original state. Which means deleting any newly
        created files or data sets.
        """
        if dest_exists is False:
            if '/' in dest:
                self._connection.exec_command("rm -rf {0}".format(dest))
            else:
                module_args = dict(name=dest, state='absent')
                if _is_member(dest):
                    module_args['type'] = "MEMBER"
                self._execute_module(
                    module_name='zos_data_set',
                    module_args=module_args,
                    task_vars=task_vars
                )
