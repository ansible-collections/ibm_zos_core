# Copyright (c) 2019, 2020 Lu Zhao <zlbjlu@cn.ibm.com>
# Copyright (c) IBM Corporation 2020
# LICENSE: [GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import stat
import re
import pathlib
import time
import subprocess

#from ansible.constants import mk_boolean as boolean
from ansible.errors import AnsibleError, AnsibleFileNotFound
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.utils.hashing import checksum as file_checksum
from ansible.utils.vars import merge_hash


def _update_result(
        result,
        src,
        dest,
        ds_type="USS",
        binary_mode=False):
    """ Helper function to update output result with the provided values """

    data_set_types = {
        'PS': "Sequential",
        'PO': "Partitioned",
        'PDSE': "Partitioned Extended",
        'PE': "Partitioned Extended",
        'VSAM': "VSAM",
        'USS': "USS"
    }
    file_or_ds = "file" if ds_type == 'USS' else "data set"
    updated_result = dict((k, v) for k, v in result.items())
    updated_result.update({
        'file': src,
        'dest': dest,
        'data_set_type': data_set_types[ds_type],
        'is_binary': binary_mode
    })
    return updated_result


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


def _create_temp_path_name(src):
    current_date = time.strftime("D%y%m%d", time.localtime())
    current_time = time.strftime("T%H%M%S", time.localtime())
    return "/tmp/ansible-playbook-{0}-{1}/{2}".format(current_date, current_time, src)


def _validate_dsname(ds_name):
    """ Validate the name of a given data set """
    dsn_regex = "^(([A-Z]{1}[A-Z0-9]{0,7})([.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}$"
    return re.match(dsn_regex, ds_name if '(' not in ds_name else ds_name[:ds_name.find('(')])


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
        ''' handler for file transfer operations '''
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
        force = _process_boolean(self._task.args.get('force'), default=True)
        validate = _process_boolean(self._task.args.get('validate'), default=True)
        local_follow = _process_boolean(self._task.args.get('local_follow'), default=False)
        remote_src = _process_boolean(self._task.args.get('remote_src'), default=False)
        use_qualifier = _process_boolean(self._task.args.get('use_qualifier', True), default=False)
        is_binary = _process_boolean(self._task.args.get('is_binary'), default=False)
        is_vsam = _process_boolean(self._task.args.get('is_vsam'), default=False)
        checksum = self._task.args.get('checksum', None)
        encoding = self._task.args.get('encoding', None)
        mode = self._task.args.get('mode', None)
        owner = self._task.args.get('owner', None)
        group = self._task.args.get('group', None)

        if src is None or dest is None:
            result['msg'] = "Source and destination are required"
        elif not isinstance(src, string_types):
            result['msg'] = "Invalid type supplied for 'source' option, it must be a string"
        elif not isinstance(dest, string_types):
            result['msg'] = "Invalid type supplied for 'destination' option, it must be a string"
        elif content and isinstance (content, string_types):
            result['msg'] = "Invalid type supplied for 'content' option, it must be a string"
        elif content and src:
            result['msg'] = "Only 'content' or 'src' can be provided. Not both"
        elif local_follow and not os.path.islink(src):
            result['msg'] = "The provided source is not a symbolic link"

        is_uss = '/' in dest
        is_pds = os.path.isdir(b_src)
        copy_member = '(' in src and src.endswith(')')
        new_module_args = dict((k, v) for k, v in self._task.args.items())

        if not is_uss:
            if mode or owner or group:
                result['msg'] = "Cannot specify 'mode', 'owner' or 'group' for MVS destination"

        if not remote_src:
            if not os.path.exists(b_src):
                result['msg'] = "The local file {0} does not exist".format(src)
            elif not os.access(b_src, os.R_OK):
                result['msg'] = "The local file {0} does not have appropriate read permisssion".format(src)
            elif '(' in src or ')' in src:
                result['msg'] = "Invalid source name provided"
            elif is_pds and is_uss:
                result['msg'] = "Source is a directory, which can not be copied to a USS location"

        if remote_src and not _validate_dsname(src):
            result['msg'] = "Invalid source data set name provided"
        
        if result.get('msg'):
            result.update(src=src, dest=dest, changed=False, failed=True)
            return result

        if not remote_src:
            if is_pds:
                path, dirs, files = next(os.walk(src))
                dir_size = 0
                if len(dirs) > 0:
                    result['msg'] = "Subdirectory found inside source directory"
                    result.update(src=src, dest=dest, changed=False, failed=True)
                    return result
                
                for file in files:
                    dir_size += pathlib.Path(path + "/" + file).stat().st_size
                
                new_module_args.update(
                    size=dir_size,
                    num_files=len(files)
                )
            else:
                local_checksum = file_checksum(src)
                new_module_args = dict((k, v) for k, v in self._task.args.items())
                new_module_args.update( 
                    size=pathlib.Path(src).stat().st_size, 
                    local_checksum=local_checksum
                )
        transfer_res = self._transfer_local_data_to_remote_machine(src, is_pds)
        if transfer_res.get("msg"):
            return transfer_res

        new_module_args.update(
            is_uss=is_uss, is_pds=is_pds, copy_member=copy_member, temp_path=transfer_res.get("temp_path")
        )
        copy_res = (
            self._execute_module(
                module_name='zos_copy', 
                module_args=new_module_args, 
                task_vars=task_vars
            )
        )
        if copy_res.get('msg'):
            result['msg'] = copy_res.get('msg')
            result['stdout'] = copy_res.get('stdout') or copy_res.get("module_stdout")
            result['stderr'] = copy_res.get('stderr') or copy_res.get("module_stderr")
            result['stdout_lines'] = copy_res.get("stdout").splitlines()
            result['stderr_lines'] = copy_res.get("stderr").splitlines()
            result['rc'] = copy_res.get('rc')
            return result
        return _update_result(result, src, dest, copy_res['ds_type'], is_binary)

    def _transfer_local_data_to_remote_machine(self, src, is_pds):
        ansible_user = self._play_context.remote_user
        ansible_host = self._play_context.remote_host
        temp_path = _create_temp_path_name(src)
        stdin = None
        result = dict()

        cmd = ['sftp', ansible_user + '@' + ansible_host]
        stdin = "put -r {0} {1}".format(src, temp_path)
        if not is_pds:
            stdin = stdin.replace(" -r", "")
        transfer_data = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = transfer_data.communicate(to_bytes(stdin))
        err = _detect_sftp_errors(err)
        if transfer_data.returncode != 0 or err:
            result['msg'] = "Error transferring source '{0}' to remote z/OS system".format(src)
            result['rc'] = transfer_data.returncode
            result['stderr'] = err
            result['stderr_lines'] = err.splitlines()
            result['failed'] = True
        else:
            result['temp_path'] = temp_path
        return result
