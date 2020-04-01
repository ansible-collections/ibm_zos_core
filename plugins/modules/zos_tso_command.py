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
    - Execute a TSO command on the target z/OS system with the provided options
      and receive a structured response.
options:
  command:
    description:
        - The TSO command to execute on the target z/OS system.
    required: true
    type: str
  auth:
    required: false
    type: bool
    default: false
    description:
        - Instruct whether this command should run authorized or not.
        - If set to true, the command will be run as APF authorized,
           otherwise the command runs as unauthorized.
'''

RETURN = r'''
rc:
    description:
        The return code returned from the execution of the TSO command.
    returned: always
    type: int
    sample: 0
content:
    description:
        The response resulting from the execution of the TSO command
    returned: on success
    type: list[str]
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
'''

EXAMPLES = r'''
- name: Execute TSO command allocate a new dataset
  zos_tso_command:
      command: alloc da('TEST.HILL3.TEST') like('TEST.HILL3')

- name: Execute TSO command delete an existing dataset
  zos_tso_command:
      command: delete 'TEST.HILL3.TEST'

- name: Execute TSO command list user TESTUSER tso information
  zos_tso_command:
      command: LU TESTUSER
      auth: true
'''

from ansible.module_utils.basic import AnsibleModule
try:
    from zoautil_py import Datasets
except Exception:
    Datasets = ""
from traceback import format_exc


def run_tso_command(command, auth, module):
    try:
        if auth:
            """When I issue tsocmd command to run authorized command,
            it always returns error BPXW9047I select error,BPXW9018I
            read error even when the return code is 0, so use ZOAU
            command mvscmdauth to run authorized command.
            """
            if len(command) < 80:
                rc, stdout, stderr = module.run_command("mvscmdauth --pgm=IKJEFT01 --sysprint=* --systsprt=* "
                                                        "--systsin=stdin", data=command, use_unsafe_shell=True)
            else:
                """if the command length longer than 80 chars,
                as ZOAU mvscmd does not support stdin longer than 80 chars,
                so we have to store the command in a temp dataset and run mvscmdauth
                command.
                """
                hlq = Datasets.hlq()
                TEMP_COMMAND_DS = Datasets.temp_name(hlq)
                Datasets.create(TEMP_COMMAND_DS, type="SEQ", format="FB")
                Datasets.write(TEMP_COMMAND_DS, command)
                rc, stdout, stderr = module.run_command("mvscmdauth --pgm=IKJEFT01 --sysprint=* --systsprt=* "
                                                        "--systsin=" + TEMP_COMMAND_DS, use_unsafe_shell=True)
                Datasets.delete(TEMP_COMMAND_DS)
        else:
            """Run the unauthorized tso command."""
            rc, stdout, stderr = module.run_command(['tso', command])

    except Exception as e:
        raise e
    return (stdout, stderr, rc)


def run_module():
    module_args = dict(
        command=dict(type='str', required=True),
        auth=dict(type='bool', required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    result = dict(
        changed=False,
    )

    command = module.params.get("command")
    auth = module.params.get("auth")
    if command is None or command.strip() == "":
        module.fail_json(
            msg='Please provided a valid value for option "command".', **result)

    try:
        stdout, stderr, rc = run_tso_command(command, auth, module)

        content = stdout.splitlines()
        result['content'] = content
        result['rc'] = rc
        if rc == 0:
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(msg='The TSO command "' + command + '" execution failed.', **result)

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
