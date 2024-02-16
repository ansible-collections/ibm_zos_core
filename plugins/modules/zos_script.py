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
__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_script
version_added: '1.8.0'
author:
  - "Ivan Moreno (@rexemin)"
short_description: Run scripts in z/OS
description:
  - The L(zos_script,./zos_script.html) module runs a local or remote script
    in the remote machine.

options:
  chdir:
    description:
      - Change the script's working directory to this path.
      - When not specified, the script will run in the user's
        home directory on the remote machine.
    type: str
    required: false
  cmd:
    description:
      - Path to the local or remote script followed by optional arguments.
      - If the script path contains spaces, make sure to enclose it in two
        pairs of quotes.
      - Arguments may need to be escaped so the shell in the remote machine
        handles them correctly.
    type: str
    required: true
  creates:
    description:
      - Path to a file in the remote machine. If it exists, the
        script will not be executed.
    type: str
    required: false
  encoding:
    description:
      - Specifies which encodings the script should be converted from and to.
      - If C(encoding) is not provided, the module determines which local
        and remote charsets to convert the data from and to.
    type: dict
    required: false
    suboptions:
      from:
        description:
          - The encoding to be converted from.
        required: true
        type: str
      to:
        description:
          - The encoding to be converted to.
        required: true
        type: str
  executable:
    description:
      - Path of an executable in the remote machine to invoke the
        script with.
      - When not specified, the system will assume the script is
        interpreted REXX and try to run it as such. Make sure to
        include a comment identifying the script as REXX at the
        start of the file in this case.
    type: str
    required: false
  remote_src:
    description:
      - If set to C(false), the module will search the script in the
        controller.
      - If set to C(true), the module will search the script in the
        remote machine.
    type: bool
    required: false
  removes:
    description:
      - Path to a file in the remote machine. If it does not exist, the
        script will not be executed.
    type: str
    required: false

extends_documentation_fragment:
  - ibm.ibm_zos_core.template

notes:
  - When executing local scripts, temporary storage will be used
    on the remote z/OS system. The size of the temporary storage will
    correspond to the size of the file being copied.
  - The location in the z/OS system where local scripts will be copied to can be
    configured through Ansible's C(remote_tmp) option. Refer to
    L(Ansible's documentation,https://docs.ansible.com/ansible/latest/collections/ansible/builtin/sh_shell.html#parameter-remote_tmp)
    for more information.
  - All local scripts copied to a remote z/OS system  will be removed from the
    managed node before the module finishes executing.
  - Execution permissions for the group assigned to the script will be
    added to remote scripts. The original permissions for remote scripts will
    be restored by the module before the task ends.
  - The module will only add execution permissions for the file owner.
  - If executing REXX scripts, make sure to include a newline character on
    each line of the file. Otherwise, the interpreter may fail and return
    error C(BPXW0003I).
  - For supported character sets used to encode data, refer to the
    L(documentation,https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html).
  - This module uses L(zos_copy,./zos_copy.html) to copy local scripts to
    the remote machine.
  - L(zos_copy,./zos_copy.html) uses SFTP (Secure File Transfer Protocol)
    for the underlying transfer protocol; Co:Z SFTP is not supported. In
    the case of Co:z SFTP, you can exempt the Ansible userid on z/OS from
    using Co:Z thus falling back to using standard SFTP.
  - This module executes scripts inside z/OS UNIX System Services. For
    running REXX scripts contained in data sets or CLISTs, consider issuing a TSO
    command with L(zos_tso_command,./zos_tso_command.html).
  - The community script module does not rely on Python to execute scripts on a
    managed node, while this module does. Python must be present on the
    remote machine.

seealso:
  - module: zos_copy
  - module: zos_tso_command
"""

EXAMPLES = r"""
- name: Run a local REXX script on the managed z/OS node.
  zos_script:
    cmd: ./scripts/HELLO

- name: Run a local REXX script with args on the managed z/OS node.
  zos_script:
    cmd: ./scripts/ARGS "1,2"

- name: Run a remote REXX script while changing its working directory.
  zos_script:
    cmd: /u/user/scripts/ARGS "1,2"
    remote_src: true
    chdir: /u/user/output_dir

- name: Run a local Python script in the temporary directory specified in the Ansible environment variable 'remote_tmp'.
  zos_script:
    cmd: ./scripts/program.py
    executable: /usr/bin/python3

- name: Run a local script made from a template.
  zos_script:
    cmd: ./templates/PROGRAM
    use_template: true

- name: Run a script only when a file is not present.
  zos_script:
    cmd: ./scripts/PROGRAM
    creates: /u/user/pgm_result.txt

- name: Run a script only when a file is already present on the remote machine.
  zos_script:
    cmd: ./scripts/PROGRAM
    removes: /u/user/pgm_input.txt
"""

RETURN = r"""
cmd:
    description: Original command issued by the user.
    returned: changed
    type: str
    sample: ./scripts/PROGRAM
remote_cmd:
    description:
      Command executed on the remote machine. Will show the executable
      path used, and when running local scripts, will also show the
      temporary file used.
    returned: changed
    type: str
    sample: /tmp/zos_script.jycqqfny.ARGS 1,2
msg:
    description: Failure or skip message returned by the module.
    returned: failure or skipped
    type: str
    sample:
      File /u/user/file.txt is already missing on the system, skipping script
rc:
    description: Return code of the script.
    returned: changed
    type: int
    sample: 16
stdout:
    description: The STDOUT from the script, may be empty.
    returned: changed
    type: str
    sample: Allocation to SYSEXEC completed.
stderr:
    description: The STDERR from the script, may be empty.
    returned: changed
    type: str
    sample: An error has ocurred.
stdout_lines:
    description: List of strings containing individual lines from STDOUT.
    returned: changed
    type: list
    sample: ["Allocation to SYSEXEC completed."]
stderr_lines:
    description: List of strings containing individual lines from STDERR.
    returned: changed
    type: list
    sample: ["An error has ocurred"]
"""


import os
import stat
import shlex

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            chdir=dict(type='str', required=False),
            cmd=dict(type='str', required=True),
            creates=dict(type='str', required=False),
            encoding=dict(
                type='dict',
                required=False,
                options={
                    'from': dict(type='str', required=True,),
                    'to': dict(type='str', required=True,)
                }
            ),
            executable=dict(type='str', required=False),
            remote_src=dict(type='bool', required=False),
            removes=dict(type='str', required=False),
            use_template=dict(type='bool', default=False),
            template_parameters=dict(
                type='dict',
                required=False,
                options=dict(
                    variable_start_string=dict(type='str', default='{{'),
                    variable_end_string=dict(type='str', default='}}'),
                    block_start_string=dict(type='str', default='{%'),
                    block_end_string=dict(type='str', default='%}'),
                    comment_start_string=dict(type='str', default='{#'),
                    comment_end_string=dict(type='str', default='#}'),
                    line_statement_prefix=dict(type='str', required=False),
                    line_comment_prefix=dict(type='str', required=False),
                    lstrip_blocks=dict(type='bool', default=False),
                    trim_blocks=dict(type='bool', default=True),
                    keep_trailing_newline=dict(type='bool', default=False),
                    newline_sequence=dict(
                        type='str',
                        default='\n',
                        choices=['\n', '\r', '\r\n']
                    ),
                    auto_reload=dict(type='bool', default=False),
                )
            ),
        ),
        supports_check_mode=False
    )

    args_def = dict(
        chdir=dict(arg_type='path', required=False),
        cmd=dict(arg_type='str', required=True),
        creates=dict(arg_type='path', required=False),
        executable=dict(arg_type='path', required=False),
        remote_src=dict(arg_type='bool', required=False),
        removes=dict(arg_type='path', required=False),
        use_template=dict(arg_type='bool', required=False),
        template_parameters=dict(
            arg_type='dict',
            required=False,
            options=dict(
                variable_start_string=dict(arg_type='str', required=False),
                variable_end_string=dict(arg_type='str', required=False),
                block_start_string=dict(arg_type='str', required=False),
                block_end_string=dict(arg_type='str', required=False),
                comment_start_string=dict(arg_type='str', required=False),
                comment_end_string=dict(arg_type='str', required=False),
                line_statement_prefix=dict(arg_type='str', required=False),
                line_comment_prefix=dict(arg_type='str', required=False),
                lstrip_blocks=dict(arg_type='bool', required=False),
                trim_blocks=dict(arg_type='bool', required=False),
                keep_trailing_newline=dict(arg_type='bool', required=False),
                newline_sequence=dict(arg_type='str', required=False),
                auto_reload=dict(arg_type='bool', required=False),
            )
        ),
    )

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    cmd_str = module.params.get('cmd')
    cmd_parts = shlex.split(cmd_str)
    script_path = cmd_parts[0]
    chdir = module.params.get('chdir')
    executable = module.params.get('executable')
    creates = module.params.get('creates')
    removes = module.params.get('removes')

    if creates and os.path.exists(creates):
        result = dict(
            changed=False,
            skipped=True,
            msg='File {0} already exists on the system, skipping script'.format(creates)
        )
        module.exit_json(**result)

    if removes and not os.path.exists(removes):
        result = dict(
            changed=False,
            skipped=True,
            msg='File {0} is already missing on the system, skipping script'.format(removes)
        )
        module.exit_json(**result)

    if chdir and not os.path.exists(chdir):
        module.fail_json(
            msg='The given chdir {0} does not exist on the system.'.format(chdir)
        )

    # Adding owner execute permissions to the script.
    # The module will fail if the Ansible user is not the owner!
    script_permissions = os.lstat(script_path).st_mode
    os.chmod(
        script_path,
        script_permissions | stat.S_IXUSR
    )

    if executable:
        cmd_str = "{0} {1}".format(executable, cmd_str)

    cmd_str = cmd_str.strip()
    script_rc, stdout, stderr = module.run_command(
        cmd_str,
        cwd=chdir
    )

    result = dict(
        changed=True,
        cmd=module.params.get('cmd'),
        remote_cmd=cmd_str,
        rc=script_rc,
        stdout=stdout,
        stderr=stderr,
        stdout_lines=stdout.split('\n'),
        stderr_lines=stderr.split('\n'),
    )

    # Reverting script's permissions.
    os.chmod(script_path, script_permissions)

    if script_rc != 0 or stderr:
        result['msg'] = 'The script terminated with an error'
        module.fail_json(
            **result
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
