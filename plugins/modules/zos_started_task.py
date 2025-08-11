#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2022, 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (absolute_import, division, print_function)
import traceback

__metaclass__ = type

DOCUMENTATION = r"""
module: zos_started_task
version_added: 1.16.0
author:
  - "Ravella Surendra Babu (@surendra.ravella582)"
short_description: Perform operations on started tasks.
description:
  - Start, display, modify, cancel, force and stop a started task

options:
  asid:
    description:
      - I(asid) is a unique address space identifier which gets assigned to each running task.
    required: false
    type: str
  device_type:
    description:
      - I(device_type) is the type of the output device (if any) associated with the task.
    required: false
    type: str
  device_number:
    description:
      - I(device_number) is the number of the device to be started. A device number is 3 or 4 hexadecimal digits. 
        A slash (/) must precede a 4-digit number but is not before a 3-digit number.
    required: false
    type: str
  identifier:
    description:
      - I(device_number) is the name that identifies the task to be started. This name can be up to 8 characters long. 
        The first character must be alphabetical.
    required: false
    type: str
  job_account:
    description:
      - I(job_account) specifies accounting data in the JCL JOB statement for the started task. 
        If the source JCL was a job and has already accounting data, the value that is specified on this parameter 
        overrides the accounting data in the source JCL.
    required: false
    type: str
  job_name:
    description:
      - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
        then member_name is used as job_name.
    required: false
    type: str
  keyword_parameters:
    description:
      - Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure. 
        The maximum length of each keyword=option is 66 characters. No individual value within this field can be longer than 
        44 characters in length.
    required: false
    type: str
  member_name:
    description:
      - I(member_name) is a 1 - 8 character name of a member of a partitioned data set that contains the source JCL 
        for the task to be started. The member can be either a job or a cataloged procedure.
    required: false
    type: str
  operation:
    description:
      - The started task operation which needs to be performed.
      - >
        If I(operation=start) and the data set does not exist on the managed node,
        no action taken, module completes successfully with I(changed=False).
    required: false
    type: str
    choices:
      - start
      - stop
      - modify
      - display
      - force
      - cancel
  parameters:
    description:
      - Program parameters passed to the started program, which might be a list in parentheses or a string in single quotation marks
    required: false
    type: str
  reus_asid:
    description:
      - When REUSASID=YES is specified on the START command and REUSASID(YES) is specified in the DIAGxx parmlib member, 
        a reusable ASID is assigned to the address space created by the START command. If REUSASID=YES is not specified 
        on the START command or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.
  subsystem_name:
    description:
      - The name of the subsystem that selects the task for processing. The name must be 1 - 4 characters, 
        which are defined in the IEFSSNxx parmlib member, and the subsystem must be active.
    required: false
    type: str
  volume_serial:
    description:
      - If devicetype is a tape or direct-access device, the volume serial number of the volume is mounted on the device.
    required: false
    type: str
"""
EXAMPLES = r"""
- name: Start a started task using member name.
  zos_started_task:
    member: "PROCAPP"
    operation: "start"
"""
RETURN = r"""

"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    zoau_version_checker
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError
)

try:
    from zoautil_py import opercmd
except Exception:
    datasets = ZOAUImportError(traceback.format_exc())
    gdgs = ZOAUImportError(traceback.format_exc())

try:
    from zoautil_py import exceptions as zoau_exceptions
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())

def execute_command(operator_cmd, timeout_s=1, *args, **kwargs):
    """Execute operator command.

    Parameters
    ----------
    operator_cmd : str
        Operator command.
    timeout_s : int
        Timeout to wait for the command execution, measured in centiseconds.
    *args : dict
        Arguments for the command.
    **kwargs : dict
        More arguments for the command.

    Returns
    -------
    OperatorQueryResult
        The result of the command.
    """
    # as of ZOAU v1.3.0, timeout is measured in centiseconds, therefore:
    timeout_c = 100 * timeout_s
    response = opercmd.execute(operator_cmd, timeout_c, *args, **kwargs)

    rc = response.rc
    stdout = response.stdout_response
    stderr = response.stderr_response
    return rc, stdout, stderr

def prepare_start_command(member, identifier, job_name, job_account, device, volume_serial, subsystem_name, reus_asid, parameters, keyword_parameters):
    cmd = 'S '+member
    if identifier:
      cmd = cmd + "." + identifier + "," + device + "," + volume_serial + "," + parameters
    if jobname:
      cmd = cmd + ",jobname=" + job_name
    if jobaccount:
      cmd = cmd + ",jobacct=" + job_account
    if subsystem_name:
      cmd = cmd + ",SUB=" + subsystem_name
    if reus_asid:
      cmd = cmd + ",REUSASID=" + reus_asid
    if keyword_parameters:
      cmd = cmd + "," + keyword_parameters
    return cmd

def run_module():
    """Initialize the module.

    Raises
    ------
    fail_json
        z/OS started task operation failed.
    """
    module = AnsibleModule(
        argument_spec={
            'operation': {
                'type': 'str',
                'required': True,
                'choices': ['start', 'stop', 'modify', 'display', 'force', 'cancel']
            },
            'member_name': {
                'type': 'str',
                'required': False,
                'aliases': ['member']
            },
            'identifier': {
                'arg_type': 'str',
                'required': False
            },
            'job_name': {
                'type': 'str',
                'required': False,
                'aliases': ['task_name']
            },
            'job_account': { #55 chars
                'type': 'str',
                'required': False
            },
            'device_type': {
                'type': 'str',
                'required': False
            },
            'device_number': { #A device number is 3 or 4 hexadecimal digits. A slash (/) must precede a 4-digit number but is not before a 3-digit number.
                'type': 'str',
                'required': False
            },
            'volume_serial': {
                'type': 'str',
                'required': False
            },
            'subsystem_name': { #The name must be 1 - 4 characters
                'type': 'str',
                'required': False
            },
            'reus_asid': {
                'type': 'bool',
                'required': False,
                'choices': ['yes', 'no']
            },
            'parameters': {
                'type': 'str',
                'required': False
            },
            'keyword_parameters': { #The maximum length of each keyword=option is 66 characters. No individual value within this field can be longer than 44 characters in length.
                'type': 'str',
                'required': False
            },
            'asid': {
                'type': 'str',
                'required': False
            }
        },
        mutually_exclusive=[
            ['job_name', 'identifier'],
            ['device_name', 'device_type']
        ],
        supports_check_mode=True
    )

    args_def = {
        'operation': {
            'type': 'str',
            'required': True
        },
        'member_name': {
            'arg_type': 'member_name',
            'required': False,
            'aliases': ['member']
        },
        'identifier_name': {
            'arg_type': 'identifier_name',
            'required': False
        },
        'job_name': {
            'arg_type': 'str',
            'required': False,
            'aliases': ['job']
        },
        'job_account': {
            'arg_type': 'str',
            'required': False
        },
        'device_type': {
            'arg_type': 'str',
            'required': False
        },
        'device_number': {
            'arg_type': 'str',
            'required': False
        },
        'volume_serial': {
            'arg_type': 'str',
            'required': False
        },
        'subsystem_name': {
            'arg_type': 'str',
            'required': False
        },
        'reus_asid': {
            'arg_type': 'str',
            'required': False
        },
        'parameters': {
            'arg_type': 'str',
            'required': False
        },
        'keyword_parameters': {
            'arg_type': 'str',
            'required': False
        },
        'asid': {
            'arg_type': 'str',
            'required': False
        }
    }

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )
    operation = module.params.get('operation')
    member = module.params.get('member_name')
    identifier = module.params.get('identifier')
    job_name = module.params.get('job_name')
    job_account = module.params.get('job_account')
    asid = module.params.get('asid')
    parameters = module.params.get('parameters')
    device_type = module.params.get('device_type')
    device_number = module.params.get('device_number')
    volume_serial = module.params.get('volume_serial')
    subsystem_name = module.params.get('subsystem_name')
    reus_asid = module.params.get('reus_asid')
    keyword_parameters = module.params.get('keyword_parameters')
    device = device_type if device_type is not None else device_number
    kwargs = {}

    # Validations
    if job_account != "" and len(job_account) > 55:
        module.fail_json(
            msg="job_account value should not exceed 55 characters.",
            changed=False
            )
    if device_number != "":
        devnum_len = len(device_number)
        if devnum_len not in (3, 5) or ( devnum_len == 5 and not device_number.startswith("/")):
            module.fail_json(
                msg="Invalid device_number.",
                changed=False
                )
    if subsystem_name != "" and len(job_account) > 4:
        module.fail_json(
            msg="The subsystem_name must be 1 - 4 characters.",
            changed=False
            )
    # keywaord arguments validation.....

    wait_s = 5

    use_wait_arg = False
    if zoau_version_checker.is_zoau_version_higher_than("1.2.4"):
        use_wait_arg = True

    if use_wait_arg:
        kwargs.update({"wait": True})

    args = []
    cmd = ''
    started_task_name = ""
    if operation != 'start':
        if job_name is not None:
            started_task_name = job_name
        elif member is not None:
            started_task_name = member
            if identifier is not None:
                started_task_name = started_task_name + "." + identifier
        else:
            module.fail_json(
            msg="one of job_name, member_name or identifier is needed but all are missing.",
            changed=False
            )
    if operation == 'start':
        ##member name is mandatory
        if member is None or member.strip() == "":
            module.fail_json(
            msg="member_name is missing which is mandatory.",
            changed=False
            ) 
        cmd = prepare_start_command(member, identifier, job_name, job_account, device, volume_serial, subsystem_name, reus_asid, parameters, keyword_parameters)
    elif operation == 'display':
        cmd = 'd a,'+started_task_name
    elif operation == 'stop':
        cmd = 'p '+started_task_name
    elif operation == 'cancel':
        cmd = 'c '+started_task_name
        if asid:
            cmd = cmd+',a='+asid
    elif operation == 'force':
        cmd = 'force '+started_task_name
        if asid:
            cmd = cmd+',a='+asid
    elif operation == 'modify':
        cmd = 'f '+started_task_name+','+parameters
    changed = False
    stdout = ""
    stderr = ""
    rc, out, err = execute_command(cmd, timeout_s=wait_s, *args, **kwargs)
    if "ERROR" in out or err != "":
        changed = False
        stdout = out
        stderr = err
        if err == "" or err is None:
            stderr = out 
    else:
        changed = True
        stdout = out
        stderr = err


    result = dict()

    if module.check_mode:
        module.exit_json(**result)

    result = dict(
            changed=changed,
            cmd=cmd,
            remote_cmd=cmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            stdout_lines=stdout.split('\n'),
            stderr_lines=stderr.split('\n'),
        )

    module.exit_json(**result)


if __name__ == '__main__':
  run_module()
