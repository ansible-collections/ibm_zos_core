#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
module: zos_tso_command
author: "Xiao Yuan Ma (@bjmaxy)"
short_description: Execute a TSO command
description:
    - Execute TSO commands on the target z/OS system with the provided options
      and receive a structured response.
options:
  commands:
    description:
        - The TSO commands to execute on the target z/OS system.
    required: true
    type: list
'''

RETURN = r'''
output:
    description:
        List of each tso command output.
    returned: always
    type: list
    elements: dict
    suboptions:
        command:
            description:
                The executed tso command.
            returned: always
            type: str
        rc:
            description:
                The return code returned from the execution of the TSO command.
            returned: always
            type: int
            sample: 0
        content:
            description:
                The response resulting from the execution of the TSO command
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
                The line number of the content .
            returned: always
            type: int
'''

EXAMPLES = r'''
- name: Execute TSO command allocate a new dataset
  zos_tso_command:
      commands:
          - alloc da('TEST.HILL3.TEST') like('TEST.HILL3')
          - delete 'TEST.HILL3.TEST'

- name: Execute TSO command list user TESTUSER tso information
  zos_tso_command:
      commands:
           - LU TESTUSER

'''

from ansible.module_utils.basic import AnsibleModule
from traceback import format_exc
from os import chmod, path
from tempfile import NamedTemporaryFile
import json


def run_tso_command(commands, module):
    script = """/* REXX */
ARG cmds
address tso
say '{"output":['
do while cmds <> ''
   x = outtrap('listcato.')
   i=1
   say '{'
   parse var  cmds cmd ';' cmds
   say ' "command" : "'cmd'",'
   no=POS(';',cmds)
   cmd
   say ' "rc" : 'RC','
   rc.i = RC
   i=i+1
   say ' "lines" : 'listcato.0','
   say ' "content" : [ '
   do j = 1 to listcato.0
       if j == listcato.0
          then say ' "'listcato.j '"'
       else
          say ' "'listcato.j '",'
   end
   say ']'
   x = outtrap('OFF')
   if no==0
      then say '}'
   else
      say '},'
end
say ']'
say '}'
drop listcato.
"""
    command_str = ''
    for item in commands:
        command_str = command_str + item + ";"

    rc, stdout, stderr = copy_rexx_and_run(script, command_str, module)

    command_detail_json = json.loads(stdout, strict=False)
    return command_detail_json


def copy_rexx_and_run(script, command, module):
    delete_on_close = True
    tmp_file = NamedTemporaryFile(delete=delete_on_close)
    with open(tmp_file.name, 'w') as f:
        f.write(script)
    chmod(tmp_file.name, 0o755)
    pathName = path.dirname(tmp_file.name)
    scriptName = path.basename(tmp_file.name)
    rc, stdout, stderr = module.run_command(['./' + scriptName, command], cwd=pathName)
    return rc, stdout, stderr


def run_module():
    module_args = dict(
        commands=dict(type='list', elements='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
    )

    commands = module.params.get("commands")
    if commands is None:
        module.fail_json(
            msg='Please provided a valid value for option "command".', **result)

    try:
        result = run_tso_command(commands, module)
        for cmd in result.get('output'):
            if cmd.get('rc') != 0:
                module.fail_json(msg='The TSO command "' + cmd.get('command') + '" execution failed.', **result)

        result['changed'] = True
        module.exit_json(**result)

    except Error as e:
        module.fail_json(msg=e.msg, **result)
    except Exception as e:
        trace = format_exc()
        module.fail_json(
            msg="An unexpected error occurred: {0}".format(trace), **result)


class Error(Exception):
    pass


def main():
    run_module()


if __name__ == '__main__':
    main()
