#!/usr/bin/python
# -*- coding: utf-8 -*-

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

import pytest
__metaclass__ = type


rexx_script_args = """/* REXX */
parse arg A ',' B
say 'args are ' || A || ',' || B
return 0

"""

rexx_script_chdir = """/* REXX */
address syscall 'getcwd cwd'
say cwd
return 0

"""


def create_script_content(msg, script_type):
    if script_type == 'rexx':
        # Without the comment in the first line, the interpreter will not be
        # able to run the script.
        # Without the last blank line, the REXX interpreter would throw
        # an error.
        return """/* REXX */
say '{0}'
return 0

""".format(msg)
    elif script_type == 'python':
        return """msg = "{0}"
print(msg)
""".format(msg)
    else:
        raise Exception('Type {0} is not valid.'.format(script_type))


def create_local_file(content, suffix):
    import os
    import tempfile

    fd, file_path = tempfile.mkstemp(
        prefix='zos_script',
        suffix=suffix
    )
    os.close(fd)

    with open(file_path, "w") as f:
        f.write(content)

    return file_path


def test_rexx_script_without_args(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = "Success"
        rexx_script = create_script_content(msg, 'rexx')
        script_path = create_local_file(rexx_script, 'rexx')

        zos_script_result = hosts.all.zos_script(
            cmd=script_path
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == msg
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_rexx_remote_script(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = "Success"
        rexx_script = create_script_content(msg, 'rexx')
        local_script = create_local_file(rexx_script, 'rexx')

        # Using zos_copy instead of doing an echo with shell to avoid trouble
        # with how single quotes are handled.
        script_path = '/tmp/zos_script_test_script'
        copy_result = hosts.all.zos_copy(
            src=local_script,
            dest=script_path
        )
        for result in copy_result.contacted.values():
            assert result.get('changed') is True

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            remote_src=True
        )

        for result in zos_script_result.contacted.values():
            print(result)
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == msg
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(local_script):
            os.remove(local_script)
        hosts.all.file(path=script_path, state='absent')


def test_rexx_script_with_args(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        rexx_script = rexx_script_args
        script_path = create_local_file(rexx_script, 'rexx')

        args = '1,2'
        cmd = "{0} '{1}'".format(script_path, args)

        zos_script_result = hosts.all.zos_script(
            cmd=cmd
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == 'args are {0}'.format(args)
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_rexx_script_chdir(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        rexx_script = rexx_script_chdir
        script_path = create_local_file(rexx_script, 'rexx')

        tmp_remote_dir = '/zos_script_tests'
        file_result = hosts.all.file(
            path=tmp_remote_dir,
            state='directory'
        )

        for result in file_result.contacted.values():
            assert result.get('changed') is True

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            chdir=tmp_remote_dir
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == tmp_remote_dir
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
        hosts.all.file(path=tmp_remote_dir, state='absent')


def test_rexx_script_tmp_path(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        rexx_script = create_script_content('tmp_path test', 'rexx')
        script_path = create_local_file(rexx_script, 'rexx')

        tmp_remote_dir = '/tmp/zos_script_tests'
        file_result = hosts.all.file(
            path=tmp_remote_dir,
            state='directory'
        )

        for result in file_result.contacted.values():
            assert result.get('changed') is True

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            tmp_path=tmp_remote_dir
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stderr', '') == ''
            assert tmp_remote_dir in result.get('remote_cmd', '')
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
        hosts.all.file(path=tmp_remote_dir, state='absent')


def test_python_script(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = "Success"
        python_script = create_script_content(msg, 'python')
        script_path = create_local_file(python_script, 'python')

        python_executable = hosts['options']['ansible_python_path']
        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            executable=python_executable
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == msg
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_rexx_script_creates_option(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = 'Success'
        rexx_script = create_script_content(msg, 'rexx')
        script_path = create_local_file(rexx_script, 'rexx')

        remote_file = '/tmp/zos_script_test_creates.txt'
        file_result = hosts.all.file(
            path=remote_file,
            state='touch'
        )

        for result in file_result.contacted.values():
            assert result.get('changed') is True

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            creates=remote_file
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is False
            assert result.get('skipped') is True
            assert result.get('failed', False) is False
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
        hosts.all.file(path=remote_file, state='absent')


def test_rexx_script_removes_option(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = 'Success'
        rexx_script = create_script_content(msg, 'rexx')
        script_path = create_local_file(rexx_script, 'rexx')

        # Not actually creating this file on the remote hosts.
        remote_file = '/tmp/zos_script_test_removes.txt'

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            removes=remote_file
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is False
            assert result.get('skipped') is True
            assert result.get('failed', False) is False
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
