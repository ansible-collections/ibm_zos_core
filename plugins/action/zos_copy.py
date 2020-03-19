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


def _get_dir_size(src):
    size = 0
    path, dirs, files = next(os.walk(src))
    for file in files:
        size += pathlib.Path(path + "/" + file).stat().st_size
    return size


def _create_temp_dir_name(src):
    current_date = time.strftime("D%y%m%d", time.localtime())
    current_time = time.strftime("T%H%M%S", time.localtime())
    return "/tmp/ansible-playbook-{0}-{1}/{2}".format(current_date, current_time, src)


def _validate_dsname(ds_name):
    """ Validate the name of a given data set """
    dsn_regex = "^(([A-Z]{1}[A-Z0-9]{0,7})([.]{1})){1,21}[A-Z]{1}[A-Z0-9]{0,7}$"
    return re.match(dsn_regex, ds_name if '(' not in ds_name else ds_name[:ds_name.find('(')])


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
        local_follow = _process_boolean(self._task.args.get('local_follow'), default=True)
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
        elif not isinstance (content, string_types):
            result['msg'] = "Invalid type supplied for 'content' option, it must be a string"
        elif encoding and not isinstance(encoding, string_types):
            result['msg'] = "Invalid type supplied for 'encoding' option, it must be a string"
        elif content and src:
            result['msg'] = "Only 'content' or 'src' can be provided. Not both"
        elif local_follow and not os.path.islink(src):
            result['msg'] = "The provided source is not a symbolic link"

        is_uss = '/' in dest
        is_pds = os.path.isdir(b_src)
        copy_member = '(' in src

        if not is_uss:
            if mode or owner or group:
                result['msg'] = "Cannot specify 'mode', 'owner' or 'group' for MVS destination"
            elif not _validate_dsname(dest):
                result['msg'] = "Invalid destination data set name provided"

        if not remote_src:
            if not os.path.exists(b_src):
                result['msg'] = "The local file {0} does not exist".format(src)
            elif not os.access(b_src, os.R_OK):
                result['msg'] = "The local file {0} does not have appropriate read permisssion".format(src)
            elif '(' in src or ')' in src:
                result['msg'] = "Invalid source name provided"

        if remote_src and not _validate_dsname(src):
            result['msg'] = "Invalid source data set name provided"
        
        if result.get('msg'):
            result.update(src=src, dest=dest, changed=False, failed=True)
            return result

        try:
            if is_uss:
                copy_action = self._get_copy_action_plugin()
                mvs_args = frozenset({'is_vsam', 'use_qualifier', 'encoding'})
                copy_action._task.args = dict((k, v) for k, v in self._task.args.items() if k not in mvs_args)
                return copy_action.run(task_vars=task_vars)

            if is_pds:
                _, dirs, files = next(os.walk(src))
                if len(dirs) > 0:
                    result['msg'] = "Subdirectory found inside source directory"
                    result.update(src=src, dest=dest, changed=False, failed=True)
                    return result

                temp_dir = self._transfer_local_dir_to_remote_machine(src, binary_mode=is_binary)
                new_module_args = dict((k, v) for k, v in self._task.args.items())
                new_module_args.update(_size=_get_dir_size(src), _pds_path=temp_dir)

            else:
                content = _read_file(src)
                local_checksum = file_checksum(src)
                new_module_args = dict((k,v) for k,v in self._task.args.items())
                new_module_args.update(
                    _local_data=content, 
                    _size=pathlib.Path(src).stat().st_size, 
                    _local_checksum=local_checksum
                )
            new_module_args.update(is_uss=is_uss, is_pds=is_pds, _copy_member=copy_member)
            result.update(self._execute_module(module_name='zos_copy', module_args=new_module_args, task_vars=task_vars))        

        finally:
            if is_pds:
                self._connection.exec_command("rm -r {0}".format(temp_dir))

        return result

    def _transfer_local_dir_to_remote_machine(self, src, binary_mode=False):
        ansible_user = self._play_context.remote_user
        ansible_host = self._play_context.remote_host
        temp_dir_name = _create_temp_dir_name(src)
        stdin = None

        rc, out, err = self._connection.exec_command("mkdir -p {0}".format(temp_dir_name))
        if rc != 0:
            raise AnsibleError("Unable to create temporary directory on remote host; stdout: {0}; stderr: {1}".format(out, err))

        if binary_mode:
            cmd = ['sftp', ansible_user + '@' + ansible_host]
            stdin = to_bytes("put -r {0} {1}".format(src, temp_dir_name))
        else:
            cmd = ["scp", '-r', src, ansible_user + '@' + ansible_host + ':' + temp_dir_name]
        
        transfer_dir = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = transfer_dir.communicate(stdin)
        if transfer_dir.returncode != 0:
            raise AnsibleError("Error transferring PDS from remote z/OS system; stdout: {0}; stderr: {1}".format(out, err))
        return temp_dir_name

    def _get_copy_action_plugin(self):
        return (self._shared_loader_obj.action_loader.get(
            'copy',
            task=self._task.copy(),
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj))
