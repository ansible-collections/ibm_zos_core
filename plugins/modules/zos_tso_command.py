#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019 - 2023
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
module: zos_tso_command
version_added: '1.1.0'
short_description: Execute TSO commands
description:
    - Execute TSO commands on the target z/OS system with the provided options and receive a structured response.
author:
    - "Xiao Yuan Ma (@bjmaxy)"
    - "Rich Parker (@richp405)"
options:
  commands:
    description:
        - One or more TSO commands to execute on the target z/OS system.
        - Accepts a single string or list of strings as input.
        - If a list of strings is provided, processing will stop at the first failure, based on rc.
    required: true
    type: raw
    aliases:
        - command
  max_rc:
    description:
        - Specifies the maximum return code allowed for a TSO command.
        - If more than one TSO command is submitted, the I(max_rc) applies to all TSO commands.
    default: 0
    required: false
    type: int
"""

RETURN = r"""
output:
    description:
        List of each TSO command output.
    returned: always
    type: list
    elements: dict
    contains:
        command:
            description:
                The executed TSO command.
            returned: always
            type: str
        rc:
            description:
                The return code from the executed TSO command.
            returned: always
            type: int
            sample: 0
        max_rc:
            description:
                - Specifies the maximum return code allowed for a TSO command.
                - If more than one TSO command is submitted, the I(max_rc) applies to all TSO commands.
            returned: always
            type: int
            sample: 0
        content:
            description:
                The response resulting from the execution of the TSO command.
            returned: always
            type: list
            sample:
                [
                "NO MODEL DATA SET                                                OMVSADM",
                "TERMUACC                                                                ",
                "SUBGROUP(S)= VSAMDSET SYSCTLG  BATCH    SASS     MASS     IMSGRP1       ",
                "             IMSGRP2  IMSGRP3  DSNCAT   DSN120   J42      M63           ",
                "             J91      J09      J97      J93      M82      D67           ",
                "             D52      M12      CCG      D17      M32      IMSVS         ",
                "             DSN210   DSN130   RAD      CATLG4   VCAT     CSP           ",
                ]
        lines:
            description:
                The line number of the content.
            returned: always
            type: int
"""

EXAMPLES = r"""
- name: Execute TSO commands to allocate a new dataset
  zos_tso_command:
      commands:
          - alloc da('TEST.HILL3.TEST') like('TEST.HILL3')
          - delete 'TEST.HILL3.TEST'

- name: Execute TSO command list user TESTUSER to obtain TSO information
  zos_tso_command:
      commands:
           - LU TESTUSER

- name: Execute TSO command to list dataset data (allow 4 for no dataset listed or cert found)
  zos_tso_command:
      commands:
           - LISTDSD DATASET('HLQ.DATA.SET') ALL GENERIC
      max_rc: 4

- name: Execute TSO command to run a REXX script explicitly from a data set.
  zos_tso_command:
      commands:
           - EXEC HLQ.DATASET.REXX exec
"""

from ansible.module_utils.basic import AnsibleModule
from os import chmod
from tempfile import NamedTemporaryFile
from stat import S_IEXEC, S_IREAD, S_IWRITE
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)


def run_tso_command(commands, module, max_rc):
    script = """/* REXX */
PARSE ARG cmd
address tso
x = outtrap('listcato.', '*')
cmd
rc = RC
do j = 1 to listcato.0
    say listcato.j
end
x = outtrap('OFF')
exit rc
"""
    command_detail_json = copy_rexx_and_run_commands(script, commands, module, max_rc)
    return command_detail_json


def copy_rexx_and_run_commands(script, commands, module, max_rc):
    command_detail_json = []
    delete_on_close = True
    tmp_file = NamedTemporaryFile(delete=delete_on_close)
    with open(tmp_file.name, "w") as f:
        f.write(script)
    chmod(tmp_file.name, S_IEXEC | S_IREAD | S_IWRITE)
    for command in commands:
        rc, stdout, stderr = module.run_command([tmp_file.name, command])
        command_results = {}
        command_results["command"] = command
        command_results["rc"] = rc
        command_results["content"] = stdout.split("\n")
        command_results["lines"] = len(command_results.get("content", []))
        command_results["stderr"] = stderr

        if rc <= max_rc:
            command_results["failed"] = False
        else:
            command_results["failed"] = True

        command_detail_json.append(command_results)
        if command_results["failed"]:
            break

    return command_detail_json


def list_or_str_type(contents, dependencies):
    failed = False
    if isinstance(contents, list):
        for item in contents:
            if not isinstance(item, str):
                failed = True
                break
    elif isinstance(contents, str):
        contents = [contents]
    else:
        failed = True
    if failed:
        raise ValueError(
            'Invalid argument type for "{0}". expected "string or list of strings"'.format(
                contents
            )
        )
    return contents


def run_module():
    module_args = dict(
        commands=dict(type="raw", required=True, aliases=["command"]),
        max_rc=dict(type="int", required=False, default=0),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    result = dict(
        changed=False,
        failed=True,
    )

    arg_defs = dict(
        commands=dict(type=list_or_str_type, required=True, aliases=["command"]),
        max_rc=dict(type="int", required=False, default=0),
    )
    try:
        parser = BetterArgParser(arg_defs)
        parsed_args = parser.parse_args(module.params)
    except ValueError as e:
        module.fail_json(msg=repr(e), **result)

    commands = parsed_args.get("commands")
    max_rc = parsed_args.get("max_rc")
    if max_rc is None:
        max_rc = 0

    try:
        result["output"] = run_tso_command(commands, module, max_rc)
        result["max_rc"] = max_rc
        errors_found = False
        result_list = []

        for cmd in result.get("output"):
            tmp_string = 'Command "' + cmd.get("command", "") + '" execution'
            if cmd.get("rc") > max_rc:
                errors_found = True
                if max_rc > 0:
                    result_list.append(tmp_string + "failed.  RC was {0}; max_rc was {1}".format(cmd.get("rc"), max_rc))
                else:
                    result_list.append(tmp_string + "failed.  RC was {0}.".format(cmd.get("rc")))
            else:
                result_list.append(tmp_string + "succeeded.  RC was {0}.".format(cmd.get("rc")))

        if errors_found:
            result_string = "\n".join(result_list)

            module.fail_json(
                msg="Some ({0}) command(s) failed:\n{1}".format(errors_found, result_string),
                **result
            )

        result["changed"] = True
        result["failed"] = False
        module.exit_json(**result)

    except Exception as e:
        module.fail_json(
            msg="An unexpected error occurred: {0}".format(repr(e)), **result
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
