#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023, 2025
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

import os
import tempfile
import pytest
import yaml
from shellescape import quote
import subprocess
__metaclass__ = type

from ibm_zos_core.tests.helpers.users import ManagedUserType, ManagedUser
# Using || to concatenate strings without extra spaces.
REXX_SCRIPT_ARGS = """/* REXX */
parse arg 'FIRST=' A ' SECOND=' B
say 'args are ' || A || ',' || B
return 0

"""

# For validating that chdir gets honored by the module.
REXX_SCRIPT_CHDIR = """/* REXX */
address syscall 'getcwd cwd'
say cwd
return 0

"""

# For testing a default template. Note that the Jinja variable is static
# and it's always called playbook_msg.
REXX_SCRIPT_TEMPLATE_DEFAULT = """/* REXX */
say '{{ playbook_msg }}'
return 0

"""

# For testing templates with custom markers. Here the markers are static
# too (always '((', '))', '&$' and '$&').
REXX_SCRIPT_TEMPLATE_CUSTOM = """/* REXX */
&$ This is a comment that should create problems if not substituted $&
say '(( playbook_msg ))'
return 0

"""


PLAYBOOK_ASYNC_TEST = """- hosts: zvm
  collections:
    - ibm.ibm_zos_core
  gather_facts: False
  environment:
    _BPXK_AUTOCVT: "ON"
    ZOAU_HOME: "{0}"
    PYTHONPATH: "{0}/lib/{2}"
    LIBPATH: "{0}/lib:{1}/lib:/lib:/usr/lib:."
    PATH: "{0}/bin:/bin:/usr/lpp/rsusr/ported/bin:/var/bin:/usr/lpp/rsusr/ported/bin:/usr/lpp/java/java180/J8.0_64/bin:{1}/bin:"
    _CEE_RUNOPTS: "FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)"
    _TAG_REDIR_ERR: "txt"
    _TAG_REDIR_IN: "txt"
    _TAG_REDIR_OUT: "txt"
    LANG: "C"
    PYTHONSTDINENCODING: "cp1047"

  tasks:
    - name: Execute script in async mode.
      ibm.ibm_zos_core.zos_script:
        cmd: "{3} FIRST=a SECOND=b"
      async: 45
      poll: 0
      register: job_task

    - name: Query async task.
      async_status:
        jid: "{{{{ job_task.ansible_job_id }}}}"
      register: job_result
      until: job_result.finished | bool
      retries: 20
      delay: 5
"""

INVENTORY_ASYNC_TEST = """all:
  hosts:
    zvm:
      ansible_host: {0}
      ansible_ssh_private_key_file: {1}
      ansible_user: {2}
      ansible_python_interpreter: {3}"""



def create_script_content(msg, script_type):
    """Returns a string containing either a valid REXX script or a valid
    Python script. The script will print the given message."""

    if not script_type in ['rexx','python']:
        raise ValueError(f'Type {script_type} is not valid.')
    if script_type == 'rexx':
        # Without the comment in the first line, the interpreter will not be
        # able to run the script.
        # Without the last blank line, the REXX interpreter will throw
        # an error.
        content = f"""/* REXX */
say '{msg}'
return 0

"""
    else:
        content = f"""msg = "{msg}"
print(msg)
"""
    return content


# def create_python_script_stderr(msg, rc):
#     """Returns a Python script that will write out to STDERR and return
#     a given RC. The RC can be 0, but for testing it would be better if it
#     was something else."""
#     return f"""import sys
# print('{msg}', file=sys.stderr)
# exit({rc})
# """


def create_python_script_stderr(msg, rc):
    """Returns a Python script that will write out to STDERR and return
    a given RC. It will also return a valid JSON object to stdout.
    """
    return f"""import sys
import json
print('{msg}', file=sys.stderr)
result = {{
    "failed": True,
    "msg": "{msg}",
    "rc": {rc},
    "changed": True
}}
print(json.dumps(result))
sys.exit({rc})
"""


def create_local_file(content, suffix):
    """Creates a tempfile that has the given content."""

    fd, file_path = tempfile.mkstemp(
        prefix='zos_script',
        suffix=suffix
    )
    os.close(fd)

    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(content)

    return file_path

def create_local_file_with_carriagereturn(content, suffix):
    """Creates a tempfile that has the given content."""

    fd, file_path = tempfile.mkstemp(
        prefix='zos_script',
        suffix=suffix
    )
    os.close(fd)

    with open(file_path, 'w', encoding="utf-8", newline='\r\n') as f:
        f.write(content)

    return file_path


def test_rexx_script_without_args(ansible_zos_module):
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
    hosts = ansible_zos_module

    try:
        rexx_script = REXX_SCRIPT_ARGS
        script_path = create_local_file(rexx_script, 'rexx')

        first_arg = 'one'
        second_arg = 'two'
        args = f'FIRST={first_arg} SECOND={second_arg}'
        cmd = f"{script_path} '{args}'"

        zos_script_result = hosts.all.zos_script(
            cmd=cmd
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert first_arg in result.get('stdout', '')
            assert second_arg in result.get('stdout', '')
            # Making sure the action plugin passed every argument to the module.
            assert args in result.get('invocation').get('module_args').get('cmd')
            assert args in result.get('remote_cmd')
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_rexx_script_chdir(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        rexx_script = REXX_SCRIPT_CHDIR
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


@pytest.mark.template
def test_script_template_with_default_markers(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        rexx_script = REXX_SCRIPT_TEMPLATE_DEFAULT
        script_path = create_local_file(rexx_script, 'rexx')

        # Updating the vars available to the tasks.
        template_vars = {
            "playbook_msg":'<Success>'
        }
        # pylint: disable-next=protected-access
        for host in hosts['options']['inventory_manager']._inventory.hosts.values():
            host.vars.update(template_vars)

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            use_template=True,
            template_parameters={
                "autoescape": False
            }
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


@pytest.mark.template
def test_script_template_with_custom_markers(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        rexx_script = REXX_SCRIPT_TEMPLATE_CUSTOM
        script_path = create_local_file(rexx_script, 'rexx')

        # Updating the vars available to the tasks.
        template_vars = {
            "playbook_msg":'Success'
        }
        # pylint: disable-next=protected-access
        for host in hosts['options']['inventory_manager']._inventory.hosts.values():
            host.vars.update(template_vars)

        zos_script_result = hosts.all.zos_script(
            cmd=script_path,
            use_template=True,
            template_parameters={
                "variable_start_string":'((',
                "variable_end_string":'))',
                "comment_start_string":'&$',
                "comment_end_string":'$&',
            }
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


def managed_user_run_script(ansible_zos_module):
    """Runs a script originally created by omvsadm that has execute permissions
    for other users."""
    hosts = ansible_zos_module
    script_path = '/tmp/zos_script_test_script'
    msg = "Success"
    zos_script_result = hosts.all.zos_script(
        cmd=script_path,
        remote_src=True
    )

    for result in zos_script_result.contacted.values():
        assert result.get('changed') is True
        assert result.get('failed', False) is False
        assert result.get('rc') == 0
        assert result.get('stdout', '').strip() == msg
        assert result.get('stderr', '') == ''

# Related to issue #1542 in our repository.
def test_user_run_script_from_another_user(ansible_zos_module, z_python_interpreter):
    hosts = ansible_zos_module
    managed_user = None
    script_path = '/tmp/zos_script_test_script'

    try:
        msg = "Success"
        rexx_script = create_script_content(msg, 'rexx')
        local_script = create_local_file(rexx_script, 'rexx')

        # Using zos_copy instead of doing an echo with shell to avoid trouble
        # with how single quotes are handled.
        script_path = '/tmp/zos_script_test_script'
        copy_result = hosts.all.zos_copy(
            src=local_script,
            dest=script_path,
            # Permissions allow for any user to execute, trying to mimick
            # the use case that originated the issue.
            mode='605'
        )
        for result in copy_result.contacted.values():
            assert result.get('changed') is True

        managed_user = ManagedUser.from_fixture(
            hosts,
            z_python_interpreter
        )
        managed_user.execute_managed_user_test(
            managed_user_test_case="managed_user_run_script",
            debug=True,
            verbose=True,
            # Creating a user with a limited HLQ since it also puts
            # it in a new group, distinct from omvsadm's.
            managed_user_type=ManagedUserType.ZOS_LIMITED_HLQ
        )
    finally:
        hosts.all.file(path=script_path, state="absent")
        managed_user.delete_managed_user()


def test_remote_script_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module

    script_path = '/tmp/zos_script_test'

    msg = 'File {0} does not exist on the system, skipping script'.format(script_path)

    zos_script_result = hosts.all.zos_script(
        cmd=script_path,
        remote_src=True
    )

    for result in zos_script_result.contacted.values():
        assert result.get('changed') is False
        assert result.get('failed') is True
        assert msg in result.get('msg')


def test_remote_script_with_args_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module

    script_path = '/tmp/zos_script_test'
    first_arg = 'one'
    second_arg = 'two'
    args = f'FIRST={first_arg} SECOND={second_arg}'
    cmd = f"{script_path} '{args}'"

    msg = 'File {0} does not exist on the system, skipping script'.format(script_path)

    zos_script_result = hosts.all.zos_script(
        cmd=cmd,
        remote_src=True
    )

    for result in zos_script_result.contacted.values():
        assert result.get('changed') is False
        assert result.get('failed') is True
        assert msg in result.get('msg')


def test_rexx_script_with_args_remote_src(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        rexx_script = REXX_SCRIPT_ARGS
        local_script = create_local_file(rexx_script, 'rexx')

        script_path = '/tmp/zos_script_test_script'
        copy_result = hosts.all.zos_copy(
            src=local_script,
            dest=script_path,
            force=True
        )
        for result in copy_result.contacted.values():
            assert result.get('changed') is True

        first_arg = 'one'
        second_arg = 'two'
        args = f'FIRST={first_arg} SECOND={second_arg}'
        cmd = f"{script_path} '{args}'"

        zos_script_result = hosts.all.zos_script(
            cmd=cmd,
            remote_src=True
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert first_arg in result.get('stdout', '')
            assert second_arg in result.get('stdout', '')
            assert args in result.get('invocation').get('module_args').get('cmd')
            assert args in result.get('remote_cmd')
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(local_script):
            os.remove(local_script)
        hosts.all.file(path=script_path, state="absent")


def test_rexx_script_with_args_and_carriagereturn(ansible_zos_module):
    hosts = ansible_zos_module
    script_path = ''
    try:
        rexx_script = REXX_SCRIPT_ARGS
        script_path = create_local_file_with_carriagereturn(rexx_script, 'rexx')

        first_arg = 'one'
        second_arg = 'two'
        args = f'FIRST={first_arg} SECOND={second_arg}'
        cmd = f"{script_path} '{args}'"

        zos_script_result = hosts.all.zos_script(
            cmd=cmd
        )

        for result in zos_script_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('rc') == 0
            assert first_arg in result.get('stdout', '')
            assert second_arg in result.get('stdout', '')
            # Making sure the action plugin passed every argument to the module.
            assert args in result.get('invocation').get('module_args').get('cmd')
            assert args in result.get('remote_cmd')
            assert result.get('stderr', '') == ''
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)


def test_job_script_async(get_config):
    # Creating temp REXX file used by the playbook.
    try:
        rexx_script = REXX_SCRIPT_ARGS
        script_path = create_local_file(rexx_script, 'rexx')

        # Getting all the info required to run the playbook.
        path = get_config
        with open(path, 'r') as file:
            enviroment = yaml.safe_load(file)

        ssh_key = enviroment["ssh_key"]
        hosts = enviroment["host"].upper()
        user = enviroment["user"].upper()
        python_path = enviroment["python_path"]
        cut_python_path = python_path[:python_path.find('/bin')].strip()
        zoau = enviroment["environment"]["ZOAU_ROOT"]
        python_version = cut_python_path.split('/')[2]

        playbook = tempfile.NamedTemporaryFile(delete=True)
        inventory = tempfile.NamedTemporaryFile(delete=True)

        os.system("echo {0} > {1}".format(
            quote(PLAYBOOK_ASYNC_TEST.format(
                zoau,
                cut_python_path,
                python_version,
                script_path
            )),
            playbook.name
        ))

        os.system("echo {0} > {1}".format(
            quote(INVENTORY_ASYNC_TEST.format(
                hosts,
                ssh_key,
                user,
                python_path
            )),
            inventory.name
        ))

        command = "ansible-playbook -i {0} {1}".format(
            inventory.name,
            playbook.name
        )

        result = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            timeout=120,
            encoding='utf-8'
        )
        assert result.returncode == 0
        assert "ok=2" in result.stdout
        assert "changed=2" in result.stdout
        assert result.stderr == ""
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

