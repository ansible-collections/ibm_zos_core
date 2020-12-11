#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["stableinterface"],
    "supported_by": "community",
}

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
      - Return verbose (sec trace) information.
      - This also shows if the command(s) were issued, and if SAF approved the run.
    type: bool
    required: false
    default: false
  debug:
    description:
      - Return debugging information, step by step through the command execution.
    type: bool
    required: false
    default: false
  security:
    description:
      - Call command with (verbose) operator which returns more details.
      - This also shows if the command(s) were issued, and if SAF approved the run.
    type: bool
    required: false
    default: false
  delay:
    description:
      - Set maximum time in seconds to wait for response.
    type: int
    required: false
    default: 0
"""

EXAMPLES = r"""
- name: Execute an operator command to show active jobs
  zos_operator:
    cmd: 'd u,all'

- name: Execute an operator command to show active jobs with verbose information
  zos_operator:
    cmd: 'd u,all'
    verbose: true

- name: Execute an operator command to show active jobs with verbose and debug information
  zos_operator:
    cmd: 'd u,all'
    verbose: true
    debug: true

- name: Execute an operator command to purge all job logs (requires escaping)
  zos_operator:
    cmd: "\\$PJ(*)"

- name: Execute operator command to show jobs, returning security information
  zos_operator:
    cmd: 'd u,all'
    security: true

- name: Execute operator command to show jobs, waiting for 5 seconds for response
  zos_operator:
    cmd: 'd u,all'
    delay: 5
"""

RETURN = r"""
rc:
    description:
       Return code of the operator command
    returned: on success
    type: int
    sample: 0
content:
    description:
       The response resulting from the execution of the operator command
    returned: on success
    type: list
    sample:
        [ "MV2C      2020039  04:29:57.58             ISF031I CONSOLE XIAOPIN ACTIVATED ",
          "MV2C      2020039  04:29:57.58            -D U,ALL                           ",
          "MV2C      2020039  04:29:57.59             IEE457I 04.29.57 UNIT STATUS 948  ",
          "         UNIT TYPE STATUS        VOLSER     VOLSTATE      SS                 ",
          "          0100 3277 OFFLINE                                 0                ",
          "          0101 3277 OFFLINE                                 0                ",
          "---- if verbose security is true, additional output will resemble:",
          "ISF050I USER=OMVSADM GROUP= PROC=REXX TERMINAL=09A3233B",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFSPROG.SDSF",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.FILTER.PREFIX",
          "ISF055I ACTION=D Access allowed USERLEVEL=7 REQLEVEL=1",
          "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.ODSP.ULOG.JES2",
          "--- if security is true, output on will resemble:",
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
        debug=dict(type="bool", required=False, default=False),
        security=dict(type="bool", required=False, default=False),
        delay=dict(type="int", required=False, default=0),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    try:
        new_params = parse_params(module.params)
        rc_message = run_operator_command(new_params)
        result["rc"] = rc_message.get("rc")
        result["content"] = rc_message.get("message").split("\n")
    except Error as e:
        module.fail_json(msg=repr(e), **result)
    except Exception as e:
        module.fail_json(
            msg="An unexpected error occurred: {0}".format(repr(e)), **result
        )

    result["changed"] = True
    module.exit_json(**result)


def parse_params(params):
    arg_defs = dict(
        cmd=dict(arg_type="str", required=True),
        verbose=dict(arg_type="bool", required=False),
        debug=dict(arg_type="bool", required=False),
        security=dict(arg_type="bool", required=False),
        delay=dict(arg_type="int", required=False),
    )
    parser = BetterArgParser(arg_defs)
    new_params = parser.parse_args(params)
    return new_params


def run_operator_command(params):
    ## remove reset sequence... the value resets when the script ends.

    # Usage: (rexfile) delay reset command [parameters] [-v] [-d] [-s]
    #       -v: print out verbose security information
    #       -d: print out debug messages
    #       -s: pass (verbose) to the sdsf command

    script = """/*rexx*/
arg delay command
Address 'TSO'
IsfRC = isfcalls( "ON" )
showoutput = 0
verbose=""
do ix = 4 to 7
  if ix <= __argv.0 then
    do
      c = strip(__argv.ix)
      showoutput=1
      select
        when c == "-v" then do
          say "Showing Security Messages"
          ISFSECTRACE='ON'
          end

        when c == "-s" then do
          say "Verbose sdsf exec option"
          verbose="( VERBOSE WAIT )"
          end

        when c == "-d" then do
          say "Regular tracing"
          trace R
          end

        otherwise
          exit -1
        end
    end
end
ISFDELAY=delay
sdsfcmd = False
if verbose == '' then do
  verbose='(WAIT)'
  end
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
if isfresp.0 > 0 then
  do
    say ""
    say "Responses"
    do ix=1 to isfresp.0
      say isfresp.ix
    end
  end
if isfulog.0 > 0 then
  do
    say ""
    say "Log Output"
    do ix=1 to isfulog.0
      say isfulog.ix
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

    fulline = " " + str(params.get("delay")) + " "

    fulline += '"' + params.get("cmd") + '"'

    if params.get("verbose"):
        fulline += " -v"
    if params.get("debug"):
        fulline += " -d"
    if params.get("security"):
        fulline += " -s"

    delete_on_close = True
    tmp_file = NamedTemporaryFile(delete=delete_on_close)
    with open(tmp_file.name, "w") as f:
        f.write(script)
    chmod(tmp_file.name, S_IEXEC | S_IREAD | S_IWRITE)

    rc, stdout, stderr = module.run_command(tmp_file.name + fulline)

    message = "running " + fulline + "\n" + stdout + stderr
    rc = 0

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
