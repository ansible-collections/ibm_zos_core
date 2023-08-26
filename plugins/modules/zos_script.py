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
  cmd:
    description:
      - Path to the local or remote script followed by optional arguments.
      - If the script path contains spaces, make sure to enclose it in two
        pairs of quotes.
      - Arguments may need to be escaped so the shell in the remote machine
        handles them correctly.
    type: str
    required: true
  chdir:
    description:
      - Change the script's working directory to this path.
      - When not specified, the script will run in the user's
        home directory on the remote machine.
    type: str
    required: false
  creates:
    description:
      - Path to a file in the remote machine. If it exists, the
        script will not be executed.
    type: str
    required: false
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
  tmp_path:
    description:
      - Path in the remote machine where local scripts will be
        temporarily copied to.
      - When not specified, the module will copy local scripts to
        the default temporary path for the user.
      - If C(tmp_path) does not exist in the remote machine, the
        module will not create it.
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

extends_documentation_fragment:
  - ibm.ibm_zos_core.template

notes:
  - When executing local scripts, temporary storage will be used
    on the remote z/OS system. The size of the temporary storage will
    correspond to the size of the file being copied.
  - Execution permissions for the group assigned to the script will be
    added to remote scripts. The original permissions for the script will
    be restored by the module before the task ends.
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
    running REXX scripts contained in data sets, consider issuing a TSO
    command with L(zos_tso_command,./zos_tso_command.html).

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

- name: Run a local Python script that uses a custom tmp_path.
  zos_script:
    cmd: ./scripts/program.py
    executable: /usr/bin/python3
    tmp_path: /usr/tmp/ibm_zos_core

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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    encode
)


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            cmd=dict(type='str', required=True),
            chdir=dict(type='str', required=False),
            creates=dict(type='str', required=False),
            executable=dict(type='str', required=False),
            tmp_path=dict(type='str', required=False),
            remote_src=dict(type='bool', required=False),
            removes=dict(type='str', required=False),
            encoding=dict(
                type='dict',
                required=False,
                options={
                    'from': dict(type='str', required=True,),
                    'to': dict(type='str', required=True,)
                }
            ),
            use_template=dict(arg_type='bool', default=False),
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
            # Private parameters (from the action plugin).
            script_path=dict(type='str'),
            script_args=dict(type='str'),
            local_charset=dict(type='str')
        ),
        supports_check_mode=False
    )

    args_def = dict(
        cmd=dict(arg_type='str', required=True),
        chdir=dict(arg_type='path', required=False),
        creates=dict(arg_type='path', required=False),
        executable=dict(arg_type='path', required=False),
        tmp_path=dict(arg_type='path', required=False),
        remote_src=dict(arg_type='bool', required=False),
        removes=dict(arg_type='path', required=False),
        # use_template=dict(arg_type='bool', required=False),
        # template_parameters=dict(
        #     arg_type='dict',
        #     required=False,
        #     options=dict(
        #         variable_start_string=dict(arg_type='str', required=False),
        #         variable_end_string=dict(arg_type='str', required=False),
        #         block_start_string=dict(arg_type='str', required=False),
        #         block_end_string=dict(arg_type='str', required=False),
        #         comment_start_string=dict(arg_type='str', required=False),
        #         comment_end_string=dict(arg_type='str', required=False),
        #         line_statement_prefix=dict(arg_type='str', required=False),
        #         line_comment_prefix=dict(arg_type='str', required=False),
        #         lstrip_blocks=dict(arg_type='bool', required=False),
        #         trim_blocks=dict(arg_type='bool', required=False),
        #         keep_trailing_newline=dict(arg_type='bool', required=False),
        #         newline_sequence=dict(arg_type='str', required=False),
        #         auto_reload=dict(arg_type='bool', required=False),
        #     )
        # ),
        script_path=dict(arg_type='path', required=True),
        script_args=dict(arg_type='str', required=True)
    )

    if (
        not module.params.get('encoding')
        and not module.params.get('remote_src')
    ):
        module.params['encoding'] = {
            'from': module.params.get('local_charset'),
            'to': encode.Defaults.get_default_system_charset(),
        }

    if module.params.get('encoding'):
        module.params.update(dict(
            from_encoding=module.params.get('encoding').get('from'),
            to_encoding=module.params.get('encoding').get('to'),
        ))

        args_def.update(dict(
            from_encoding=dict(arg_type='encoding'),
            to_encoding=dict(arg_type='encoding'),
        ))

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    script_path = module.params.get('script_path')
    script_args = module.params.get('script_args')
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

    # Adding group execute permissions to the script.
    script_permissions = os.lstat(script_path).st_mode
    os.chmod(
        script_path,
        script_permissions | stat.S_IXGRP
    )

    cmd_str = "{0} {1}".format(script_path, script_args)
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
        module.fail_json(
            msg='The script terminated with an error.',
            **result
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
