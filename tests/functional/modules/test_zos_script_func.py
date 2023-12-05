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


# Using || to concatenate strings without extra spaces.
rexx_script_args = """/* REXX */
parse arg A ',' B
say 'args are ' || A || ',' || B
return 0

"""

# For validating that chdir gets honored by the module.
rexx_script_chdir = """/* REXX */
address syscall 'getcwd cwd'
say cwd
return 0

"""

# For testing a default template. Note that the Jinja variable is static
# and it's always called playbook_msg.
rexx_script_template_default = """/* REXX */
say '{{ playbook_msg }}'
return 0

"""

# For testing templates with custom markers. Here the markers are static
# too (always '((', '))', '&$' and '$&').
rexx_script_template_custom = """/* REXX */
&$ This is a comment that should create problems if not substituted $&
say '(( playbook_msg ))'
return 0

"""


def create_script_content(msg, script_type):
    """Returns a string containing either a valid REXX script or a valid
    Python script. The script will print the given message."""
    if script_type == 'rexx':
        # Without the comment in the first line, the interpreter will not be
        # able to run the script.
        # Without the last blank line, the REXX interpreter will throw
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


def create_python_script_stderr(msg, rc):
    """Returns a Python script that will write out to STDERR and return
    a given RC. The RC can be 0, but for testing it would be better if it
    was something else."""
    return """import sys
print('{0}', file=sys.stderr)
exit({1})
""".format(msg, rc)


def create_local_file(content, suffix):
    """Creates a tempfile that has the given content."""
    import os
    import tempfile

    fd, file_path = tempfile.mkstemp(
        prefix='zos_script',
        suffix=suffix
    )
    os.close(fd)

    with open(file_path, 'w') as f:
        f.write(content)

    return file_path


def test_rexx_script_without_args(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = 'Success'
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
        msg = 'Success'
        rexx_script = create_script_content(msg, 'rexx')
        local_script = create_local_file(rexx_script, 'rexx')

        # Using zos_copy instead of doing an echo with shell to avoid trouble
        # with how single quotes are handled.
        script_path = '/tmp/zos_script_test_script'
        copy_result = hosts.all.zos_copy(
            src=local_script,
            dest=script_path,
            mode='600'
        )
        for result in copy_result.contacted.values():
            assert result.get('changed') is True

        pre_stat_info = hosts.all.stat(path=script_path)

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            remote_src=True
        )

        post_stat_info = hosts.all.stat(path=script_path)

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == msg
            assert result.get('stderr', '') == ''
        # Checking that permissions remained unchanged after executing
        # zos_script.
        for pre_stat, post_stat in zip(
            pre_stat_info.contacted.values(),
            post_stat_info.contacted.values()
        ):
            assert pre_stat.get('mode') == post_stat.get('mode')
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


def test_script_template_with_default_markers(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        rexx_script = rexx_script_template_default
        script_path = create_local_file(rexx_script, 'rexx')

        # Updating the vars available to the tasks.
        template_vars = dict(
            playbook_msg='Success'
        )
        for host in hosts['options']['inventory_manager']._inventory.hosts.values():
            host.vars.update(template_vars)

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            use_template=True
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == template_vars['playbook_msg']
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_script_template_with_custom_markers(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        rexx_script = rexx_script_template_custom
        script_path = create_local_file(rexx_script, 'rexx')

        # Updating the vars available to the tasks.
        template_vars = dict(
            playbook_msg='Success'
        )
        for host in hosts['options']['inventory_manager']._inventory.hosts.values():
            host.vars.update(template_vars)

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            use_template=True,
            template_parameters=dict(
                variable_start_string='((',
                variable_end_string='))',
                comment_start_string='&$',
                comment_end_string='$&',
            )
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert result.get('stdout', '').strip() == template_vars['playbook_msg']
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_python_script_with_stderr(ansible_zos_module):
    import os

    hosts = ansible_zos_module

    try:
        msg = 'Error'
        rc = 1
        python_script = create_python_script_stderr(msg, rc)
        script_path = create_local_file(python_script, 'python')

        python_executable = hosts['options']['ansible_python_path']
        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            executable=python_executable
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed') is True
            assert result.get('rc') == rc
            assert result.get('stdout', '') == ''
            assert result.get('stderr', '').strip() == msg
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
