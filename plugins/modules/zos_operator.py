#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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
short_description: Execute operator command
description:
    - Execute an operator command and receive the output.
author: "Ping Xiao (@xiaopingBJ)"
options:
  cmd:
    description:
      - The command to execute.
    type: str
    required: true
  verbose:
    description:
      - Return diagnostic messages that lists and describes the execution of the
        operator commands.
      - Return security trace messages that help you understand and diagnose the
        execution of the operator commands
      - Return trace instructions displaying how the the command's operation is
        read, evaluated and executed.
    type: bool
    required: false
    default: false
  wait_time_s:
    description:
      - Set maximum time in seconds to wait for the commands to execute.
      - When set to 0, the system default is used.
      - This option is helpful on a busy system needing more time to execute
        commands.
      - Setting I(wait) can instruct if execution should wait the
        full I(wait_time_s).
    type: int
    required: false
    default: 0
  wait:
    description:
      - Specify to wait the full I(wait_time_s) interval before retrieving
        responses.
      - This option is recommended to ensure the responses are accessible and
        captured by logging facilities and the I(verbose) option.
      - I(delay=True) waits the full I(wait_time_s) interval.
      - I(delay=False) returns as soon as the first command executes.
    type: bool
    required: false
    default: true
"""

EXAMPLES = r"""
- name: Execute an operator command to show active jobs
  zos_operator:
    cmd: 'd u,all'

- name: Execute an operator command to show active jobs with verbose information
  zos_operator:
    cmd: 'd u,all'
    verbose: true

- name: Execute an operator command to purge all job logs (requires escaping)
  zos_operator:
    cmd: "\\$PJ(*)"

- name: Execute operator command to show jobs, waiting UP TO 5 seconds for response
  zos_operator:
    cmd: 'd u,all'
    wait_time_s: 5
    wait: false

- name: Execute operator command to show jobs, always waiting 7 seconds for response
  zos_operator:
    cmd: 'd u,all'
    wait_time_s: 7
    wait: true
"""

RETURN = r"""
rc:
    description:
      Return code of the operator command
    returned: always
    type: int
    sample: 0
content:
    description:
       The text from the command issued, plus verbose messages if I(verbose=True)
    returned: on success
    type: list
    sample:
        [ "MV2C      2020039  04:29:57.58             ISF031I CONSOLE XIAOPIN ACTIVATED ",
          "MV2C      2020039  04:29:57.58            -D U,ALL                           ",
          "MV2C      2020039  04:29:57.59             IEE457I 04.29.57 UNIT STATUS 948  ",
          "         UNIT TYPE STATUS        VOLSER     VOLSTATE      SS                 ",
          "          0100 3277 OFFLINE                                 0                ",
          "          0101 3277 OFFLINE                                 0                ",
          "ISF050I USER=OMVSADM GROUP= PROC=REXX TERMINAL=09A3233B",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFSPROG.SDSF",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.FILTER.PREFIX",
          "ISF055I ACTION=D Access allowed USERLEVEL=7 REQLEVEL=1",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.ODSP.ULOG.JES2",
          "ISF147I REXX variable ISFTIMEOUT fetched, return code 00000001 value is ''.",
          "ISF754I Command 'SET DELAY 5' generated from associated variable ISFDELAY.",
          "ISF769I System command issued, command text: D U,ALL -S.",
          "ISF146I REXX variable ISFDIAG set, return code 00000001 value is '00000000 00000000 00000000 00000000 00000000'.",
          "ISF766I Request completed, status: COMMAND ISSUED."
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


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.ansible_module import (
    AnsibleModuleHelper,
)
from ansible.module_utils.six import PY3
from tempfile import NamedTemporaryFile
from stat import S_IEXEC, S_IREAD, S_IWRITE
from os import chmod

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.better_arg_parser import (
    BetterArgParser,
)

if PY3:
    from shlex import quote
else:
    from pipes import quote


def run_module():
    module_args = dict(
        cmd=dict(type="str", required=True),
        verbose=dict(type="bool", required=False, default=False),
        wait_time_s=dict(type="int", required=False, default=0),
        wait=dict(type="bool", required=False, default=True),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    try:
        new_params = parse_params(module.params)
        rc_message = run_operator_command(new_params)
        result["rc"] = rc_message.get("rc")
        result["content"] = rc_message.get("message").split("\n")
        if result["rc"] == 0:
          if( len(result["content"] > 2 ):
              if "INVALID" not in result["content"][2]:
                  if "ERROR" note in result["content"][2]:
                    result["changed"] = True
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
        wait=dict(arg_type="bool", required=False),
    )
    parser = BetterArgParser(arg_defs)
    new_params = parser.parse_args(params)
    return new_params


def run_operator_command(params):
    # Usage: (rexfile) wait_time_s command [-v] [-n]
    #       -v: print out verbose security information
    #       -n: nowait

    script = """/*rexx*/
wait_time = __argv.2
command = __argv.3
verbosemode = __argv.4
nowait = __argv.5

Address 'TSO'
IsfRC = isfcalls( "ON" )
showoutput = 0
waitmsg = " WAIT"
if nowait == "NOWAIT" then do
  waitmsg = ""
  end

verbose = ""
if verbosemode == "VERB" then do
  showoutput = 1
  ISFSECTRACE="ON"
  verbose = "( VERBOSE" waitmsg ")"
  end
else do
  if waitmsg == " WAIT" then do
    verbose = "( WAIT )"
    end
  end

if wait_time > 0 then do
  ISFDELAY=wait_time
  end

sdsfcmd = False

fwd = WORD(command, 1)
ffwd = translate(fwd)
if( ffwd == 'QUERY' | ffwd == 'SET' | ffwd == 'WHO') then
  do
    sdsfcmd = True
  end
if sdsfcmd == True then
  do
    address SDSF "ISFEXEC " command verbose
  end
else
  do
    address SDSF "ISFEXEC '/"command"'" verbose
  end
saverc = rc

IsfRC = isfcalls( "OFF" )
trace Off
if isfulog.0 > 0 then
  do
    do ix=1 to isfulog.0
      say isfulog.ix
    end
  end
if isfresp.0 > 0 then
  do
    do ix=1 to isfresp.0
      say isfresp.ix
    end
  end
if showoutput > 0 then
  do
    SAY "===================="
    SAY "result code: " saverc
    SAY "===================="

    say ""
    say "Action messages"
    say isfmsg
    say ""
    do ix=1 to isfmsg2.0
      say isfmsg2.ix
    end
    say ""
  end
EXIT saverc
"""
    module = AnsibleModuleHelper(argument_spec={})

    fulline = " " + str(params.get("wait_time_s")) + " "

    fulline += '"' + params.get("cmd") + '"'

    if params.get("verbose"):
        fulline += " VERB"
    else:
        fulline += " QUIET"

    if params.get("wait"):
        fulline += " WAIT"
    else:
        fulline += " NOWAIT"

    delete_on_close = True
    tmp_file = NamedTemporaryFile(delete=delete_on_close)
    with open(tmp_file.name, "w") as f:
        f.write(script)
    chmod(tmp_file.name, S_IEXEC | S_IREAD | S_IWRITE)

    rc, stdout, stderr = module.run_command(tmp_file.name + fulline)

    message = "running " + fulline + "\n" + stdout + stderr

    if rc > 0:
        raise OperatorCmdError(fulline, rc, message.split("\n") if message else message)

    return {"rc": rc, "message": message}


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
