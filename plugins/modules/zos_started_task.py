#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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

__metaclass__ = type

DOCUMENTATION = r"""
module: zos_started_task
version_added: 1.16.0
author:
  - "Ravella Surendra Babu (@surendra.ravella582)"
short_description: Perform operations on started tasks.
description:
  - start, display, modify, cancel, force and stop a started task

options:
  start_task:
    description:
      - The start operation of the started task.
    required: false
    type: dict
    suboptions:
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
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
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
            aliases:
            - job
            - task
            - task_name
        keyword_parameters:
            description:
            - Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure.
                The maximum length of each keyword=option is 66 characters. No individual value within this field can be longer than
                44 characters in length.
            required: false
            type: dict
        member_name:
            description:
            - I(member_name) is a 1 - 8 character name of a member of a partitioned data set that contains the source JCL
                for the task to be started. The member can be either a job or a cataloged procedure.
            required: false
            type: str
            aliases:
            - member
        parameters:
            description:
            - Program parameters passed to the started program, which might be a list in parentheses or a string in single quotation marks
            required: false
            type: list
            elements: str
        reus_asid:
            description:
            - When REUSASID=YES is specified on the START command and REUSASID(YES) is specified in the DIAGxx parmlib member,
                a reusable ASID is assigned to the address space created by the START command. If REUSASID=YES is not specified
                on the START command or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.
            required: false
            type: str
            choices:
            - 'YES'
            - 'NO'
        subsystem:
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
  display_task:
    description:
      - The display operation of the started task.
    required: false
    type: dict
    suboptions:
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
        job_name:
            description:
            - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
                then member_name is used as job_name.
            required: false
            type: str
            aliases:
            - job
            - task
            - task_name
  modify_task:
    description:
      - The modify operation of the started task.
    required: false
    type: dict
    suboptions:
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
        job_name:
            description:
            - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
                then member_name is used as job_name.
            required: false
            type: str
            aliases:
            - job
            - task
            - task_name
        parameters:
            description:
            - Program parameters passed to the started program, which might be a list in parentheses or a string in single quotation marks
            required: false
            type: list
            elements: str
  cancel_task:
    description:
      - The cancel operation of the started task.
    required: false
    type: dict
    suboptions:
        armrestart:
            description:
            - I(armrestart) indicates to restart a started task automatically after the cancel completes.
            required: false
            type: bool
        asid:
            description:
            - I(asid) is a unique address space identifier which gets assigned to each running started task.
            required: false
            type: str
        dump:
            description:
            - I(dump) indicates to take dump before ending a started task.
            required: false
            type: bool
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
        job_name:
            description:
            - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
                then member_name is used as job_name.
            required: false
            type: str
            aliases:
            - job
            - task
            - task_name
        userid:
            description:
            - I(userid) is the user ID of the time-sharing user you want to cancel.
            required: false
            type: str
  force_task:
    description:
      - The force operation of the started task.
    required: false
    type: dict
    suboptions:
        arm:
            description:
            - I(arm) indicates to execute normal task termination routines without causing address space destruction.
            required: false
            type: bool
        armrestart:
            description:
            - I(armrestart) indicates to restart a started task automatically after the cancel completes.
            required: false
            type: bool
        asid:
            description:
            - I(asid) is a unique address space identifier which gets assigned to each running started task.
            required: false
            type: str
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
        job_name:
            description:
            - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
                then member_name is used as job_name.
            required: false
            type: str
            aliases:
            - job
            - task
            - task_name
        retry:
            description:
            - I(retry) is applicable for only FORCE TCB.
            required: false
            type: str
            choices:
            - 'YES'
            - 'NO'
        tcb_address:
            description:
            - I(tcb_address) is a 6-digit hexadecimal TCB address of the task to terminate.
            required: false
            type: str
        userid:
            description:
            - I(userid) is the user ID of the time-sharing user you want to cancel.
            required: false
            type: str
  stop_task:
    description:
      - The stop operation of the started task.
    required: false
    type: dict
    suboptions:
        asid:
            description:
            - I(asid) is a unique address space identifier which gets assigned to each running started task.
            required: false
            type: str
        identifier_name:
            description:
            - I(identifier_name) is the name that identifies the task to be started. This name can be up to 8 characters long.
                The first character must be alphabetical.
            required: false
            type: str
            aliases:
            - identifier
        job_name:
            description:
            - I(job_name) is a name which should be assigned to a started task while starting it. If job_name is not specified,
                then member_name is used as job_name.
            required: false
            type: str
            aliases:
            - job
            - task
            - task_name
  verbose:
    description:
      - Return System logs that describe the task's execution.
    required: false
    type: bool
    default: false
  wait_time_s:
    required: false
    default: 0
    type: int
    description:
      - Option I(wait_time_s) is the the maximum amount of time, in centiseconds (0.01s), to wait for a response after submitting
        the console command. Default value of 0 means to wait the default amount of time supported by the opercmd utility.
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
import traceback
import re
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
    from zoautil_py import opercmd, zsystem
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())

# try:
#     from zoautil_py import exceptions as zoau_exceptions
# except ImportError:
#     zoau_exceptions = ZOAUImportError(traceback.format_exc())


def execute_command(operator_cmd, started_task_name, execute_display_before=False, execute_display_after=False, timeout_s=1, *args, **kwargs):
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
    tuple
        Tuple containing the RC, standard out, standard err of the
        query script and started task parameters.
    """
    task_params = {}
    # as of ZOAU v1.3.0, timeout is measured in centiseconds, therefore:
    timeout_c = 100 * timeout_s
    if execute_display_before:
        task_params = execute_display_command(started_task_name, timeout_c)
    response = opercmd.execute(operator_cmd, timeout_c, *args, **kwargs)

    if execute_display_after:
        task_params = execute_display_command(started_task_name, timeout_c)

    rc = response.rc
    stdout = response.stdout_response
    stderr = response.stderr_response
    return rc, stdout, stderr, task_params


def execute_display_command(started_task_name, timeout_s):
    """Execute operator display command.

    Parameters
    ----------
    started_task_name : str
        The name of started task.
    timeout_s : int
        Timeout to wait for the command execution, measured in centiseconds.

    Returns
    -------
    list
        List contains extracted parameters from display command output of started task
    """
    cmd = "d a," + started_task_name
    display_response = opercmd.execute(cmd, timeout_s)
    task_params = []
    if display_response.rc == 0 and display_response.stderr_response == "":
        task_params = extract_keys(display_response.stdout_response)
    return task_params


def validate_and_prepare_start_command(module, start_parms):
    """Validates parameters and creates start command

    Parameters
    ----------
    start_parms : dict
        The started task start command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The start command in string format.
    """
    member = start_parms.get('member_name')
    identifier = start_parms.get('identifier_name')
    job_name = start_parms.get('job_name')
    job_account = start_parms.get('job_account')
    parameters = start_parms.get('parameters') or []
    device_type = start_parms.get('device_type') or ""
    device_number = start_parms.get('device_number') or ""
    volume_serial = start_parms.get('volume_serial') or ""
    subsystem_name = start_parms.get('subsystem')
    reus_asid = start_parms.get('reus_asid')
    keyword_parameters = start_parms.get('keyword_parameters')
    keyword_parameters_string = ""
    device = device_type if device_type else device_number
    # Validations
    if device_number and device_type:
        module.fail_json(
            rc=5,
            msg="device_number and device_type are mutually exclusive.",
            changed=False
        )
    if job_account and len(job_account) > 55:
        module.fail_json(
            rc=5,
            msg="job_account value should not exceed 55 characters.",
            changed=False
        )
    if device_number:
        devnum_len = len(device_number)
        if devnum_len not in (3, 5) or (devnum_len == 5 and not device_number.startswith("/")):
            module.fail_json(
                rc=5,
                msg="Invalid device_number.",
                changed=False
            )
    if subsystem_name and len(subsystem_name) > 4:
        module.fail_json(
            rc=5,
            msg="The subsystem_name must be 1 - 4 characters.",
            changed=False
        )
    if keyword_parameters:
        for key, value in keyword_parameters.items():
            key_len = len(key)
            value_len = len(value)
            if key_len > 44 or value_len > 44 or key_len + value_len > 65:
                module.fail_json(
                    rc=5,
                    msg="The length of a keyword=option is exceeding 66 characters or length of an individual value is exceeding 44 characters."
                        + "key:{0}, value:{1}".format(key, value),
                    changed=False
                )
            else:
                if keyword_parameters_string:
                    keyword_parameters_string = keyword_parameters_string + "," + f"{key}={value}"
                else:
                    keyword_parameters_string = f"{key}={value}"
    if job_name:
        started_task_name = job_name
    elif member:
        started_task_name = member
        if identifier:
            started_task_name = started_task_name + "." + identifier
    else:
        module.fail_json(
            rc=5,
            msg="member_name is missing which is mandatory.",
            changed=False
        )
    if not member:
        module.fail_json(
            rc=5,
            msg="member_name is missing which is mandatory.",
            changed=False
        )
    if job_name and identifier:
        module.fail_json(
            rc=5,
            msg="job_name and identifier_name are mutually exclusive while starting a started task.",
            changed=False
        )
    parameters_updated = ""
    if parameters:
        if len(parameters) == 1:
            parameters_updated = "'" + parameters[0] + "'"
        else:
            parameters_updated = f"({','.join(parameters)})"

    cmd = 'S ' + member
    if identifier:
        cmd = cmd + "." + identifier
    if parameters:
        cmd = cmd + "," + device + "," + volume_serial + "," + parameters_updated
    elif volume_serial:
        cmd = cmd + "," + device + "," + volume_serial
    elif device:
        cmd = cmd + "," + device
    if job_name:
        cmd = cmd + ",JOBNAME=" + job_name
    if job_account:
        cmd = cmd + ",JOBACCT=" + job_account
    if subsystem_name:
        cmd = cmd + ",SUB=" + subsystem_name
    if reus_asid:
        cmd = cmd + ",REUSASID=" + reus_asid
    if keyword_parameters_string:
        cmd = cmd + "," + keyword_parameters_string
    return started_task_name, cmd


def prepare_display_command(module, display_parms):
    """Validates parameters and creates display command

    Parameters
    ----------
    display_parms : dict
        The started task display command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The display command in string format.
    """
    identifier = display_parms.get('identifier_name')
    job_name = display_parms.get('job_name')
    started_task_name = ""
    if job_name:
        started_task_name = job_name
        if identifier:
            started_task_name = started_task_name + "." + identifier
    else:
        module.fail_json(
            rc=5,
            msg="job_name is missing which is mandatory.",
            changed=False
        )
    cmd = 'D A,' + started_task_name
    return started_task_name, cmd


def prepare_stop_command(module, stop_parms):
    """Validates parameters and creates stop command

    Parameters
    ----------
    stop_parms : dict
        The started task stop command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The stop command in string format.
    """
    identifier = stop_parms.get('identifier_name')
    job_name = stop_parms.get('job_name')
    asid = stop_parms.get('asid')
    started_task_name = ""
    if job_name:
        started_task_name = job_name
        if identifier:
            started_task_name = started_task_name + "." + identifier
    else:
        module.fail_json(
            rc=5,
            msg="job_name is missing which is mandatory.",
            changed=False
        )
    cmd = 'P ' + started_task_name
    if asid:
        cmd = cmd + ',A=' + asid
    return started_task_name, cmd


def prepare_modify_command(module, modify_parms):
    """Validates parameters and creates modify command

    Parameters
    ----------
    modify_parms : dict
        The started task modify command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The modify command in string format.
    """
    identifier = modify_parms.get('identifier_name')
    job_name = modify_parms.get('job_name')
    parameters = modify_parms.get('parameters')
    started_task_name = ""
    if job_name:
        started_task_name = job_name
        if identifier:
            started_task_name = started_task_name + "." + identifier
    else:
        module.fail_json(
            rc=5,
            msg="job_name is missing which is mandatory.",
            changed=False
        )
    if parameters is None:
        module.fail_json(
            rc=5,
            msg="parameters are mandatory.",
            changed=False
        )
    cmd = 'F ' + started_task_name + "," + ",".join(parameters)
    return started_task_name, cmd


def prepare_cancel_command(module, cancel_parms):
    """Validates parameters and creates cancel command

    Parameters
    ----------
    cancel_parms : dict
        The started task modify command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The cancel command in string format.
    """
    identifier = cancel_parms.get('identifier_name')
    job_name = cancel_parms.get('job_name')
    asid = cancel_parms.get('asid')
    dump = cancel_parms.get('dump')
    armrestart = cancel_parms.get('armrestart')
    userid = cancel_parms.get('userid')
    started_task_name = ""
    if job_name:
        started_task_name = job_name
        if identifier:
            started_task_name = started_task_name + "." + identifier
    elif userid:
        started_task_name = "U=" + userid
    else:
        module.fail_json(
            rc=5,
            msg="Both job_name and userid are missing, one of them is needed to cancel a task.",
            changed=False
        )
    if userid and armrestart:
        module.fail_json(
            rc=5,
            msg="The ARMRESTART parameter is not valid with the U=userid parameter.",
            changed=False
        )
    cmd = 'C ' + started_task_name
    if asid:
        cmd = cmd + ',A=' + asid
    if dump:
        cmd = cmd + ',DUMP'
    if armrestart:
        cmd = cmd + ',ARMRESTART'
    return started_task_name, cmd


def prepare_force_command(module, force_parms):
    """Validates parameters and creates force command

    Parameters
    ----------
    force_parms : dict
        The started task force command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The force command in string format.
    """
    identifier = force_parms.get('identifier_name')
    job_name = force_parms.get('job_name')
    asid = force_parms.get('asid')
    arm = force_parms.get('arm')
    armrestart = force_parms.get('armrestart')
    userid = force_parms.get('userid')
    tcb_address = force_parms.get('tcb_address')
    retry = force_parms.get('retry')
    started_task_name = ""
    if tcb_address and len(tcb_address) != 6:
        module.fail_json(
            rc=5,
            msg="The TCB address of the task should be exactly 6-digit hexadecimal.",
            changed=False
        )
    if retry and not tcb_address:
        module.fail_json(
            rc=5,
            msg="The RETRY parameter is valid with the TCB parameter only.",
            changed=False
        )
    if userid and armrestart:
        module.fail_json(
            rc=5,
            msg="The ARMRESTART parameter is not valid with the U=userid parameter.",
            changed=False
        )
    if job_name:
        started_task_name = job_name
        if identifier:
            started_task_name = started_task_name + "." + identifier
    elif userid:
        started_task_name = "U=" + userid
    else:
        module.fail_json(
            rc=5,
            msg="Both job_name and userid are missing, one of them is needed to cancel a task.",
            changed=False
        )
    cmd = 'FORCE ' + started_task_name
    if asid:
        cmd = cmd + ',A=' + asid
    if arm:
        cmd = cmd + ',ARM'
    if armrestart:
        cmd = cmd + ',ARMRESTART'
    if tcb_address:
        cmd = cmd + ',TCB=' + tcb_address
    if retry:
        cmd = cmd + ',RETRY=' + retry
    return started_task_name, cmd


def extract_keys(stdout):
    """Extracts keys and values from the given stdout

    Parameters
    ----------
    stdout : string
        The started task display command output

    Returns
    -------
    tasks
        The list of task parameters.
    """
    keys = {'A': 'ASID', 'CT': 'CPU_Time', 'ET': 'Elapsed_Time', 'WUID': 'WUID', 'USERID': 'USERID', 'P': 'Priority'}
    lines = stdout.strip().split('\n')
    tasks = []
    current_task = None
    task_header_regex = re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
    kv_pattern = re.compile(r'(\S+)=(\S+)')
    for line in lines[5:]:
        line = line.strip()
        if len(line.split()) >= 5 and task_header_regex.search(line):
            if current_task:
                tasks.append(current_task)
            match = task_header_regex.search(line)
            current_task = {
                "TASK_NAME": match.group(1),
                "DETAILS": {}
            }
            for match in kv_pattern.finditer(line):
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                current_task["DETAILS"][key] = value
        elif current_task:
            for match in kv_pattern.finditer(line):
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                current_task["DETAILS"][key] = value
    if current_task:
        tasks.append(current_task)
    return tasks


def fetch_logs(command):
    """Extracts keys and values from the given stdout

    Parameters
    ----------
    command : string
        The comand which need to be checked in system logs

    Returns
    -------
    list
        The list of logs from SYSLOG
    """
    stdout = zsystem.read_console(options='-t1')
    stdout_lines = stdout.splitlines()
    first = None
    pattern = rf"\b{command}\b"
    for i, line in enumerate(stdout_lines):
        if re.search(pattern, line, re.IGNORECASE):
            first = i
    if not first:
        return ""
    logs = "\n".join(stdout_lines[first:])
    return logs


def parse_and_validate_args(params):
    """Parse and validate input parameters

    Parameters
    ----------
    params : dict
        The dictionary which has input parameters.

    Returns
    -------
    dict
        The validated list of input parameters.
    """
    start_args = dict(
        device_type=dict(type="str", required=False),
        device_number=dict(type="str", required=False),
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_account=dict(type="str", required=False),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        keyword_parameters=dict(type="basic_dict", required=False),
        member_name=dict(type="member_name", required=False, aliases=["member"]),
        parameters=dict(type="list", elements="str", required=False),
        reus_asid=dict(type="str", required=False),
        subsystem=dict(type="str", required=False),
        volume_serial=dict(type="str", required=False)
    )
    display_args = dict(
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"])
    )
    modify_args = dict(
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        parameters=dict(type="list", elements="str", required=False)
    )
    cancel_args = dict(
        armrestart=dict(type="bool", required=False),
        asid=dict(type="str", required=False),
        dump=dict(type="bool", required=False),
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        userid=dict(type="str", required=False)
    )
    force_args = dict(
        arm=dict(type="bool", required=False),
        armrestart=dict(type="bool", required=False),
        asid=dict(type="str", required=False),
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        retry=dict(type="str", required=False),
        tcb_address=dict(type="str", required=False),
        userid=dict(type="str", required=False)
    )
    stop_args = dict(
        asid=dict(type="str", required=False),
        identifier_name=dict(type="identifier_name", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"])
    )
    module_args = dict(
        start_task=dict(type="dict", required=False, options=start_args),
        stop_task=dict(type="dict", required=False, options=stop_args),
        display_task=dict(type="dict", required=False, options=display_args),
        modify_task=dict(type="dict", required=False, options=modify_args),
        cancel_task=dict(type="dict", required=False, options=cancel_args),
        force_task=dict(type="dict", required=False, options=force_args),
        verbose=dict(type="bool", required=False),
        wait_time_s=dict(type="int", default=5)
    )
    parser = better_arg_parser.BetterArgParser(module_args)
    parsed_args = parser.parse_args(params)
    return parsed_args


def run_module():
    """Initialize the module.

    Raises
    ------
    fail_json
        z/OS started task operation failed.
    """
    start_args = dict(
        device_type=dict(type="str", required=False),
        device_number=dict(type="str", required=False),
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_account=dict(type="str", required=False),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        keyword_parameters=dict(type="dict", required=False, no_log=False),
        member_name=dict(type="str", required=False, aliases=["member"]),
        parameters=dict(type="list", elements="str", required=False),
        reus_asid=dict(type="str", required=False, choices=["YES", "NO"]),
        subsystem=dict(type="str", required=False),
        volume_serial=dict(type="str", required=False)
    )
    display_args = dict(
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"])
    )
    modify_args = dict(
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        parameters=dict(type="list", elements="str", required=False)
    )
    cancel_args = dict(
        armrestart=dict(type="bool", required=False),
        asid=dict(type="str", required=False),
        dump=dict(type="bool", required=False),
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        userid=dict(type="str", required=False)
    )
    force_args = dict(
        arm=dict(type="bool", required=False),
        armrestart=dict(type="bool", required=False),
        asid=dict(type="str", required=False),
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"]),
        retry=dict(type="str", required=False, choices=["YES", "NO"]),
        tcb_address=dict(type="str", required=False),
        userid=dict(type="str", required=False)
    )
    stop_args = dict(
        asid=dict(type="str", required=False),
        identifier_name=dict(type="str", required=False, aliases=["identifier"]),
        job_name=dict(type="str", required=False, aliases=["job", "task", "task_name"])
    )

    module_args = dict(
        start_task=dict(type="dict", required=False, options=start_args),
        stop_task=dict(type="dict", required=False, options=stop_args),
        display_task=dict(type="dict", required=False, options=display_args),
        modify_task=dict(type="dict", required=False, options=modify_args),
        cancel_task=dict(type="dict", required=False, options=cancel_args),
        force_task=dict(type="dict", required=False, options=force_args),
        verbose=dict(type="bool", required=False, default=False),
        wait_time_s=dict(type="int", default=5)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[
            ["start_task", "stop_task", "display_task", "modify_task", "cancel_task", "force_task"]
        ],
        supports_check_mode=True
    )

    try:
        parms = parse_and_validate_args(module.params)
    except ValueError as err:
        module.fail_json(
            rc=5,
            msg='Parameter verification failed.',
            stderr=str(err)
        )
    wait_time_s = parms.get('wait_time_s')
    verbose = parms.get('verbose')
    kwargs = {}
    """
    Below error messages are used to detrmine if response has any error.When
    response could have any of below error message has explained below.

    ERROR: Response contains this keyword when JCL contains syntax error.
    INVALID PARAMETER: When invalid parameter passed in command line.
    NOT ACTIVE: When started task with the given job name is not active
    REJECTED: When modify command is not supported by respective started task.
    NOT LOGGED ON: When invalid userid passed in command.
    DUPLICATE NAME FOUND: When multiple started tasks exist with same name.
    CANCELABLE: When force command used without using cancel command
    """
    start_errmsg = ['ERROR', 'INVALID PARAMETER']
    stop_errmsg = ['NOT ACTIVE']
    display_errmsg = ['NOT ACTIVE']
    modify_errmsg = ['REJECTED', 'NOT ACTIVE']
    cancel_errmsg = ['NOT ACTIVE', 'NOT LOGGED ON', 'INVALID PARAMETER', 'DUPLICATE NAME FOUND']
    force_errmsg = ['NOT ACTIVE', 'NOT LOGGED ON', 'INVALID PARAMETER', 'CANCELABLE', 'DUPLICATE NAME FOUND']
    err_msg = []

    use_wait_arg = False
    if zoau_version_checker.is_zoau_version_higher_than("1.2.4"):
        use_wait_arg = True

    if use_wait_arg:
        kwargs.update({"wait": True})

    args = []
    cmd = ""

    execute_display_before = False
    execute_display_after = False
    if parms.get('start_task'):
        err_msg = start_errmsg
        execute_display_after = True
        started_task_name, cmd = validate_and_prepare_start_command(module, parms.get('start_task'))
    elif parms.get('display_task'):
        err_msg = display_errmsg
        started_task_name, cmd = prepare_display_command(module, parms.get('display_task'))
    elif parms.get('stop_task'):
        execute_display_before = True
        err_msg = stop_errmsg
        started_task_name, cmd = prepare_stop_command(module, parms.get('stop_task'))
    elif parms.get('cancel_task'):
        execute_display_before = True
        err_msg = cancel_errmsg
        started_task_name, cmd = prepare_cancel_command(module, parms.get('cancel_task'))
    elif parms.get('force_task'):
        execute_display_before = True
        err_msg = force_errmsg
        started_task_name, cmd = prepare_force_command(module, parms.get('force_task'))
    elif parms.get('modify_task'):
        execute_display_after = True
        err_msg = modify_errmsg
        started_task_name, cmd = prepare_modify_command(module, parms.get('modify_task'))
    changed = False
    stdout = ""
    stderr = ""
    rc, out, err, task_params = execute_command(cmd, started_task_name, execute_display_before, execute_display_after, timeout_s=wait_time_s, *args, **kwargs)
    isFailed = False
    system_logs = ""
    if err != "" or any(msg in out for msg in err_msg):
        isFailed = True
    if not isFailed or verbose:
        system_logs = fetch_logs(cmd.upper())
        if any(msg in system_logs for msg in err_msg):
            isFailed = True
    if isFailed:
        if rc == 0:
            rc = 1
        changed = False
        stdout = out
        stderr = err
        if err == "" or err is None:
            stderr = out
            stdout = ""
    else:
        changed = True
        stdout = out
        stderr = err
        if parms.get('display_task'):
            task_params = extract_keys(out)

    result = dict()

    if module.check_mode:
        module.exit_json(**result)
    state = ""
    
    result = dict(
            changed=changed,
            cmd=cmd,
            tasks=task_params,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            stdout_lines=stdout.split('\n'),
            stderr_lines=stderr.split('\n'),
        )
    if verbose:
        result["verbose_output"] = system_logs
    if parms.get('display_task') or parms.get('modify_task'):
        if len(task_params) > 0 and not isFailed:
            result["state"] = "Active"
        else:
            result["state"] = "NotActive"
    
    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
