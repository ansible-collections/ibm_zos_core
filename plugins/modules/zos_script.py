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
short_description: Run local scripts in z/OS
description:
  - The L(zos_script,./zos_script.html) module runs a local or remote script
    in the remote machine.

options:
  cmd:
    description:
      - If the script path contains spaces, make sure to enclose the command
        string in two pairs of quotes.
    type: str
    required: true
  chdir:
    description:
      - TODO
    type: str
    required: false
  executable:
    description:
      - TODO
    type: str
    required: false
  tmp_path:
    description:
      - TODO
    type: str
    required: false
  remote_src:
    description:
      - TODO
    type: bool
    required: false
  encoding:
    description:
      - Specifies which encodings the script should be converted from and to.
      - If C(encoding) is not provided, the module determines which local and remote
        charsets to convert the data from and to.
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
  - When copying local scripts, temporary storage will be used
    on the remote z/OS system. The size of the temporary storage will
    correspond to the size of the file being copied.
  - If executing REXX scripts, make sure to include a newline character on
    each line of the file. Otherwise, the interpreter may fail and return
    error BPXW0003I.
  - For supported character sets used to encode data, refer to the
    L(documentation,https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/resources/character_set.html).
  - L(zos_copy,./zos_copy.html) uses SFTP (Secure File Transfer Protocol) for the underlying
    transfer protocol; Co:Z SFTP is not supported. In the case of Co:z SFTP,
    you can exempt the Ansible userid on z/OS from using Co:Z thus falling back
    to using standard SFTP.

seealso:
  - module: zos_copy
  - module: zos_tso_command
"""

EXAMPLES = r"""
- name: Run a local REXX script on the managed z/OS node.
  zos_script:
    cmd: ./scripts/rexx_hello

- name: Run a local REXX script with args on the managed z/OS node.
  zos_script:
    cmd: ./scripts/rexx_test "1,2"
"""

RETURN = r"""
cmd:
    description:
    returned:
    type:
    sample:
remote_cmd:
    description:
    returned:
    type:
    sample:
rc:
    description:
    returned:
    type:
    sample:
msg:
    description:
    returned:
    type:
    sample:
stdout:
    description:
    returned:
    type:
    sample:
stderr:
    description:
    returned:
    type:
    sample:
stdout_lines:
    description:
    returned:
    type:
    sample:
stderr_lines:
    description:
    returned:
    type:
    sample:
"""


import os
import stat

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    encode
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

# try:
#     from zoautil_py import datasets
# except Exception:
#     Datasets = MissingZOAUImport()


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            cmd=dict(type='str', required=True),
            chdir=dict(type='str', required=False),
            executable=dict(type='str', required=False),
            tmp_path=dict(type='str', required=False),
            remote_src=dict(type='bool', required=False),
            encoding=dict(
                type='dict',
                required=False,
                options={
                    'from': dict(type='str', required=True,),
                    'to': dict(type='str', required=True,)
                }
            ),
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
        executable=dict(arg_type='path', required=False),
        tmp_path=dict(arg_type='path', required=False),
        remote_src=dict(arg_type='bool', required=False),
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

    # TODO: check that it actually needs to be defined dynamically when
    # using a local source.
    if module.params.get('encoding'):
        args_def.update(dict(
            encoding=dict(
                arg_type='dict',
                required=False,
                options={
                    'from': dict(arg_type='encoding', required=True),
                    'to': dict(arg_type='encoding', required=True)
                }
            )
        ))

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(msg="Parameter verification failed", stderr=str(err))

    script_path = module.params.get('script_path')
    script_args = module.params.get('script_args')
    chdir = module.params.get('chdir')
    executable = module.params.get('executable')

    # Adding group execute permissions to the script.
    script_permissions = os.lstat(script_path).st_mode
    os.chmod(
        script_path,
        script_permissions | stat.S_IXGRP
    )

    cmd_str = "{0} {1}".format(script_path, script_args)
    if executable:
        cmd_str = "{0} {1}".format(executable, cmd_str)
    if chdir:
        cmd_str = "'cd {0} && {1}'".format(chdir, cmd_str)

    cmd_str = cmd_str.strip()
    script_rc, stdout, stderr = module.run_command(cmd_str)

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

    # TODO: check whether changed should be flipped in this case.
    if script_rc != 0 or stderr:
        result["failed"] = True

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
