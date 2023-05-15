#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2022, 2023
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
module: zos_operator
version_added: '1.1.0'
short_description: Execute operator command
description:
    - Execute an operator command and receive the output.
author:
  - "Ping Xiao (@xiaopingBJ)"
  - "Demetrios Dimatos (@ddimatos)"
  - "Rich Parker (@richp405)"
  - "Oscar Fernando Flores (@fernandofloresg)"
options:
  cmd:
    description:
      - The command to execute.
      - If the command contains single-quotations, another set of single quotes must be added.
      - For example, change the command "...,P='DSN3EPX,-DBC1,S'" to "...,P=''DSN3EPX,-DBC1,S'' ".
    type: str
    required: true
  verbose:
    description:
      - Return diagnostic messages that describes the commands execution,
        options, buffer and response size.
    type: bool
    required: false
    default: false
  wait_time_s:
    description:
      - Set maximum time in seconds to wait for the commands to execute.
      - When set to 0, the system default is used.
      - This option is helpful on a busy system requiring more time to execute
        commands.
      - Setting I(wait) can instruct if execution should wait the
        full I(wait_time_s).
    type: int
    required: false
    default: 1
  wait:
    description:
      - Configuring wait used by the L(zos_operator,./zos_operator.html) module
        has been deprecated and will be removed in a future ibm.ibm_zos_core
        collection.
      - Setting this option will yield no change, it is deprecated.
      - Review option I(wait_time_s) to instruct operator commands to wait.
    type: bool
    required: false
    default: true
"""

EXAMPLES = r"""
- name: Execute an operator command to show device status and allocation
  zos_operator:
    cmd: 'd u'

- name: Execute an operator command to show device status and allocation with verbose information
  zos_operator:
    cmd: 'd u'
    verbose: true

- name: Execute an operator command to purge all job logs (requires escaping)
  zos_operator:
    cmd: "\\$PJ(*)"

- name: Execute operator command to show jobs, waiting up to 5 seconds for response
  zos_operator:
    cmd: 'd a,all'
    wait_time_s: 5

- name: Execute operator command to show jobs, always waiting 7 seconds for response
  zos_operator:
    cmd: 'd a,all'
    wait_time_s: 7

- name: Display the system symbols and associated substitution texts.
  zos_operator:
    cmd: 'D SYMBOLS'
"""

RETURN = r"""
rc:
    description:
      Return code for the submitted operator command.
    returned: always
    type: int
    sample: 0
cmd:
    description:
      Operator command submitted.
    returned: always
    type: str
    sample: d u,all
elapsed:
    description:
      The number of seconds that elapsed waiting for the command to complete.
    returned: always
    type: float
    sample: 51.53
wait_time_s:
    description:
      The maximum time in seconds to wait for the commands to execute.
    returned: always
    type: int
    sample: 5
content:
    description:
       The resulting text from the command submitted.
    returned: on success
    type: list
    sample:
        [ "EC33017A   2022244  16:00:49.00             ISF031I CONSOLE OMVS0000 ACTIVATED",
          "EC33017A   2022244  16:00:49.00            -D U,ALL ",
          "EC33017A   2022244  16:00:49.00             IEE457I 16.00.49 UNIT STATUS 645",
          "                                           UNIT TYPE STATUS        VOLSER     VOLSTATE      SS",
          "                                           0000 3390 F-NRD                        /RSDNT     0",
          "                                           0001 3211 OFFLINE                                 0",
          "                                           0002 3211 OFFLINE                                 0",
          "                                           0003 3211 OFFLINE                                 0",
          "                                           0004 3211 OFFLINE                                 0",
          "                                           0005 3211 OFFLINE                                 0",
          "                                           0006 3211 OFFLINE                                 0",
          "                                           0007 3211 OFFLINE                                 0",
          "                                           0008 3211 OFFLINE                                 0",
          "                                           0009 3277 OFFLINE                                 0",
          "                                           000C 2540 A                                       0",
          "                                           000D 2540 A                                       0",
          "                                           000E 1403 A                                       0",
          "                                           000F 1403 A                                       0",
          "                                           0010 3211 A                                       0",
          "                                           0011 3211 A                                       0"
        ]
changed:
    description:
      Indicates if any changes were made during module operation.
      Given operator commands may introduce changes that are unknown to the
      module. True is always returned unless either a module or
      command failure has occurred.
    returned: always
    type: bool
    sample: true
"""

from timeit import default_timer as timer
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    MissingZOAUImport,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)

try:
    from zoautil_py import opercmd
except Exception:
    opercmd = MissingZOAUImport()


def execute_command(operator_cmd, timeout=1, *args, **kwargs):
    start = timer()
    response = opercmd.execute(operator_cmd, timeout, *args, **kwargs)
    end = timer()
    rc = response.rc
    stdout = response.stdout_response
    stderr = response.stderr_response
    elapsed = round(end - start, 2)
    return rc, stdout, stderr, elapsed


def run_module():
    module_args = dict(
        cmd=dict(type="str", required=True),
        verbose=dict(type="bool", required=False, default=False),
        wait_time_s=dict(type="int", required=False, default=1),
        wait=dict(type="bool", required=False, default=True),
    )

    result = dict(changed=False)
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    try:
        new_params = parse_params(module.params)
        rc_message = run_operator_command(new_params)
        result["rc"] = rc_message.get("rc")
        result["elapsed"] = rc_message.get("elapsed")
        # This section will build 2 lists of strings: content=>user return, and
        # short_str, which is the first 5 lines of stdout and stderr.
        # 5: depending on the shell, there can be 1-2 leading blank lines +
        # the first few lines of ouput from the operator call will look like this:
        # .....ISF031I CONSOLE OMVSADM ACTIVATED
        # .....-actual command run
        # .....first result of command
        # text or other output may then follow
        # short_str is local, and just to check for problem response values.
        # ssctr is a limit variable so we don't pull more than 5 lines of each.
        result["content"] = []
        stdout = rc_message.get("stdout")
        if stdout is not None:
            for out in stdout.split("\n"):
                if out:
                    result["content"].append(out)
        stderr = rc_message.get("stderr")
        error = []
        if stderr is not None:
            for err in stderr.split("\n"):
                if err:
                    error.append(err)
                    result["content"].append(err)
        # call is returned from run_operator_command, specifying what was run.
        # result["cmd"] = new_params.get("cmd")
        result["cmd"] = rc_message.get("call")
        result["wait_time_s"] = new_params.get("wait_time_s")
        result["changed"] = False

        # rc=0, something succeeded (the calling script ran),
        # but it could still be a bad/invalid command.
        # As long as there are more than 2 lines, it's worth looking through.
        if int(result["rc"]) == 0:
            if len(result["content"]) > 2:
                result["changed"] = True
            else:
                module.fail_json(msg="Expected response to be more than 2 lines.", **result)
        else:
            module.fail_json(msg=("A non-zero return code was received : {0}. Review the response for more details.").format(result["rc"]),
                             cmd=result["cmd"],
                             elapsed_time=result["elapsed"],
                             wait_time_s=result["wait_time_s"],
                             stderr=str(error) if error is not None else result["content"],
                             stderr_lines=str(error).splitlines() if error is not None else result["content"],
                             changed=result["changed"],)
    except Error as e:
        module.fail_json(msg=repr(e), **result)
    except Exception as e:
        module.fail_json(
            msg="An unexpected error occurred: {0}".format(repr(e)), **result
        )

    module.exit_json(**result)


def parse_params(params):
    arg_defs = dict(
        cmd=dict(arg_type="str", required=True),
        verbose=dict(arg_type="bool", required=False),
        wait_time_s=dict(arg_type="int", required=False),
        wait=dict(arg_type="bool", required=False, removed_at_date='2022-11-30',
                  removed_from_collection='ibm.ibm_zos_core'),
    )
    parser = BetterArgParser(arg_defs)
    new_params = parser.parse_args(params)
    return new_params


def run_operator_command(params):
    AnsibleModuleHelper(argument_spec={})

    kwargs = {}

    if params.get("verbose"):
        kwargs.update({"verbose": True})
        kwargs.update({"debug": True})

    wait_s = params.get("wait_time_s")
    cmdtxt = params.get("cmd")

    args = []
    rc, stdout, stderr, elapsed = execute_command(cmdtxt, timeout=wait_s, *args, **kwargs)

    if rc > 0:
        message = "\nOut: {0}\nErr: {1}\nRan: {2}".format(stdout, stderr, cmdtxt)
        raise OperatorCmdError(cmdtxt, rc, message.split("\n"))

    return {
        "rc": rc,
        "stdout": stdout,
        "stderr": stderr,
        "call": cmdtxt,
        "elapsed": elapsed,
    }


class Error(Exception):
    pass


class OperatorCmdError(Error):
    def __init__(self, cmd, rc, message):
        self.msg = 'An error occurred executing the operator command "{0}", with RC={1} and response "{2}"'.format(
            cmd, str(rc), message
        )


def main():
    run_module()


if __name__ == "__main__":
    main()
