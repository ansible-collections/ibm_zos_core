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
version_added: 2.0.0
author:
  - "Ravella Surendra Babu (@surendrababuravella)"
short_description: Perform operations on started tasks.
description:
  - start, display, modify, cancel, force and stop a started task

options:
  arm:
    description:
        - I(arm) indicates to execute normal task termination routines without causing address space destruction.
    required: false
    type: bool
  armrestart:
    description:
        - Indicates that the batch job or started task should be automatically restarted after the cancel
          completes, if it is registered as an element of the automatic restart manager. If the job or
          task is not registered or if you do not specify this parameter, MVS will not automatically
          restart the job or task.
        - Only applicable when state is cancelled or forced, otherwise is ignored.
    required: false
    type: bool
  asid:
    description:
        - When state is cancelled or stopped or forced, asid is the hexadecimal address space
          identifier of the work unit you want to cancel, stop or force.
        - When state=displayed, asid is the hexadecimal address space identifier of the work unit of
          the task you get details from.
    required: false
    type: str
  device_type:
    description:
        - Option device_type is the type of the output device (if any) associated with the task.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
  device_number:
    description:
        - Option device_number is the number of the device to be started. A device number is 3 or 4
          hexadecimal digits. A slash (/) must precede a 4-digit number but is not before a 3-digit
          number.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
  dump:
    description:
        - A dump is to be taken. The type of dump (SYSABEND, SYSUDUMP, or SYSMDUMP)
          depends on the JCL for the job.
        - Only applicable when state=cancelled otherwise ignored.
    required: false
    type: bool
  identifier_name:
    description:
        - Option identifier_name is the name that identifies the task. This name can be up to 8
          characters long. The first character must be alphabetical.
    required: false
    type: str
    aliases:
        - identifier
  job_account:
    description:
        - Option job_account specifies accounting data in the JCL JOB statement for the started
          task. If the source JCL was a job and has already accounting data, the value that is
          specified on this parameter overrides the accounting data in the source JCL.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
  job_name:
    description:
        - When state=started job_name is a name which should be assigned to a started task
          while starting it. If job_name is not specified, then member_name is used as job_name.
          Otherwise, job_name is the started task job name used to find and apply the state
          selected.
    required: false
    type: str
    aliases:
        - job
        - task
        - task_name
  keyword_parameters:
    description:
        - Any appropriate keyword parameter that you specify to override the corresponding
          parameter in the cataloged procedure. The maximum length of each keyword=option is 66
          characters. No individual value within this field can be longer than 44 characters in length.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: dict
  member_name:
    description:
        - Option member_name is a 1 - 8 character name of a member of a partitioned data set that
          contains the source JCL for the task to be started. The member can be either a job or a
          cataloged procedure.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
    aliases:
        - member
  parameters:
    description:
        - Program parameters passed to the started program, which might be a list in parentheses or
          a string in single quotation marks
    required: false
    type: list
    elements: str
  retry:
    description:
        - I(retry) is applicable for only FORCE TCB.
        - Only applicable when state=forced otherwise ignored.
    required: false
    type: str
    choices:
        - 'YES'
        - 'NO'
  reus_asid:
    description:
        - When REUSASID=YES is specified on the START command and REUSASID(YES) is specified in the DIAGxx parmlib member,
          a reusable ASID is assigned to the address space created by the START command. If REUSASID=YES is not specified
          on the START command or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
    choices:
        - 'YES'
        - 'NO'
  state:
    description:
        - I(state) should be the desired state of the started task after the module is executed.
        - If state is started and the respective member is not present on the managed node, then error will be thrown with rc=1,
          changed=false and stderr which contains error details.
        - If state is cancelled , modified, displayed, stopped or forced and the started task is not running on the managed node,
          then error will be thrown with rc=1, changed=false and stderr contains error details.
        - If state is displayed and the started task is running, then the module will return the started task details along with
          changed=true.
    required: True
    type: str
    choices:
        - started
        - displayed
        - modified
        - cancelled
        - stopped
        - forced
  subsystem:
    description:
        - The name of the subsystem that selects the task for processing. The name must be 1 - 4
          characters, which are defined in the IEFSSNxx parmlib member, and the subsystem must
          be active.
    required: false
    type: str
  tcb_address:
    description:
        - I(tcb_address) is a 6-digit hexadecimal TCB address of the task to terminate.
        - Only applicable when state=forced otherwise ignored.
    required: false
    type: str
  volume_serial:
    description:
        - If devicetype is a tape or direct-access device, the volume serial number of the volume is
          mounted on the device.
        - Only applicable when state=started otherwise ignored.
    required: false
    type: str
  userid:
    description:
        - The user ID of the time-sharing user you want to cancel or force.
        - Only applicable when state=cancelled or state=forced , otherwise ignored.
    required: false
    type: str
  verbose:
    description:
        - When verbose=true return system logs that describe the task execution.
          Using this option will can return a big response depending on system load, also it could
          surface other programs activity.
    required: false
    type: bool
    default: false
  wait_time:
    description:
        - Option wait_time is the total time that module zos_started_task will wait for a submitted task in centiseconds.
          The time begins when the module is executed on the managed node. Default value of 0 means to wait the default
          amount of time supported by the opercmd utility.
    required: false
    default: 0
    type: int

attributes:
  action:
    support: none
    description: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
  async:
    support: full
    description: Supports being used with the ``async`` keyword.
  check_mode:
    support: full
    description: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.
"""
EXAMPLES = r"""
- name: Start a started task using member name.
  zos_started_task:
    state: "started"
    member: "PROCAPP"
- name: Start a started task using member name and identifier.
  zos_started_task:
    state: "started"
    member: "PROCAPP"
    identifier: "SAMPLE"
- name: Start a started task using member name and job.
  zos_started_task:
    state: "started"
    member: "PROCAPP"
    job_name: "SAMPLE"
- name: Start a started task using member name, job and enable verbose.
  zos_started_task:
    state: "started"
    member: "PROCAPP"
    job_name: "SAMPLE"
    verbose: True
- name: Start a started task using member name, subsystem and enable reuse asid.
  zos_started_task:
    state: "started"
    member: "PROCAPP"
    subsystem: "MSTR"
    reus_asid: "YES"
- name: Display a started task using started task name.
  zos_started_task:
    state: "displayed"
    task_name: "PROCAPP"
- name: Display started tasks using matching regex.
  zos_started_task:
    state: "displayed"
    task_name: "s*"
- name: Display all started tasks.
  zos_started_task:
    state: "displayed"
    task_name: "all"
- name: Cancel a started tasks using task name.
  zos_started_task:
    state: "cancelled"
    task_name: "SAMPLE"
- name: Cancel a started tasks using task name and asid.
  zos_started_task:
    state: "cancelled"
    task_name: "SAMPLE"
    asid: 0014
- name: Cancel a started tasks using task name and asid.
  zos_started_task:
    state: "modified"
    task_name: "SAMPLE"
    parameters: ["XX=12"]
- name: Stop a started task using task name.
  zos_started_task:
    state: "stopped"
    task_name: "SAMPLE"
- name: Stop a started task using task name, identifier and asid.
  zos_started_task:
    state: "stopped"
    task_name: "SAMPLE"
    identifier: "SAMPLE"
    asid: 00A5
- name: Force a started task using task name.
  zos_started_task:
    state: "forced"
    task_name: "SAMPLE"
"""

RETURN = r"""
changed:
  description:
    True if the state was changed, otherwise False.
  returned: always
  type: bool
cmd:
    description: Command executed via opercmd.
    returned: changed
    type: str
    sample: S SAMPLE
msg:
    description: Failure or skip message returned by the module.
    returned: failure or skipped
    type: str
    sample:
      File /u/user/file.txt is already missing on the system, skipping script
rc:
    description:
    - The return code is 0 when command executed successfully.
    - The return code is 1 when opercmd throws any error.
    - The return code is 5 when any parameter validation failed.
    returned: changed
    type: int
    sample: 0
state:
    description: The final state of the started task, after execution..
    returned: changed
    type: str
    sample: S SAMPLE
stderr:
    description: The STDERR from the command, may be empty.
    returned: changed
    type: str
    sample: An error has ocurred.
stderr_lines:
    description: List of strings containing individual lines from STDERR.
    returned: changed
    type: list
    sample: ["An error has ocurred"]
stdout:
    description: The STDOUT from the command, may be empty.
    returned: changed
    type: str
    sample: ISF031I CONSOLE OMVS0000 ACTIVATED.
stdout_lines:
    description: List of strings containing individual lines from STDOUT.
    returned: changed
    type: list
    sample: ["Allocation to SYSEXEC completed."]
tasks:
  description:
    The output information for a list of started tasks matching specified criteria.
    If no started task is found then this will return empty.
  returned: success
  type: list
  elements: dict
  contains:
    address_space_second_table_entry:
      description:
         The control block used to manage memory for a started task
      type: str
      sample: 03E78500
    affinity:
      description:
         The identifier of the processor, for up to any four processors, if the job requires the services of specific processors.
         affinity=NONE means the job can run on any processor.
      type: str
      sample: NONE
    asid:
      description:
         Address space identifier (ASID), in hexadecimal.
      type: str
      sample: 0054
    cpu_time:
      description:
         The processor time used by the address space, including the initiator. This time does not include SRB time.
         cpu_time has one of these below formats, where ttt is milliseconds, sss or ss is seconds, mm is minutes, and hh or hhhhh is hours.
         sss.tttS when time is less than 1000 seconds
         hh.mm.ss when time is at least 1000 seconds, but less than 100 hours
         hhhhh.mm when time is at least 100 hours
         ******** when time exceeds 100000 hours
         NOTAVAIL when the TOD clock is not working
      type: str
      sample: 000.008S
    dataspaces:
      description:
         The started task dataspaces details.
      returned: success
      type: list
      elements: dict
      contains:
        data_space_address_entry:
          description:
            Central address of the data space ASTE.
          type: str
          sample: 058F2180
        dataspace_name:
          description:
            Data space name associated with the address space.
          type: str
          sample: CIRRGMAP
    domain_number:
      description:
         domain_number=N/A if the system is operating in goal mode.
      type: str
      sample: N/A
    elapsed_time:
      description:
         - For address spaces other than system address spaces, the elapsed time since job select time.
         - For system address spaces created before master scheduler initialization, the elapsed time since master scheduler initialization.
         - For system address spaces created after master scheduler initialization, the elapsed time since system address space creation.
            elapsed_time has one of these below formats, where ttt is milliseconds, sss or ss is seconds, mm is minutes, and hh or hhhhh is hours.
            sss.tttS when time is less than 1000 seconds
            hh.mm.ss when time is at least 1000 seconds, but less than 100 hours
            hhhhh.mm when time is at least 100 hours
            ******** when time exceeds 100000 hours
            NOTAVAIL when the TOD clock is not working
      type: str
      sample: 812.983S
    priority:
      description:
         The priority of a started task is determined by the Workload Manager (WLM), based on the service class and importance assigned to it.
      type: str
      sample: 1
    proc_step_name:
      description:
         - For APPC-initiated transactions, the user ID requesting the transaction.
         - The name of a step within a cataloged procedure that was called by the step specified in field sss.
         - Blank, if there is no cataloged procedure.
         - The identifier of the requesting transaction program.
      type: str
      sample: VLF
    program_event_recording:
      description:
         YES if A PER trap is active in the address space.
         NO if No PER trap is active in the address space.
      type: str
      sample: NO
    program_name:
      description:
         program_name=N/A if the system is operating in goal mode.
      type: str
      sample: N/A
    queue_scan_count:
      description:
         YES if the address space has been quiesced.
         NO if the address space is not quiesced.
      type: str
      sample: NO
    resource_group:
      description:
         The name of the resource group currently associated the service class. It can also be N/A if there is no resource group association.
      type: str
      sample: N/A
    server:
      description:
         YES if the address space is a server.
         No if the address space is not a server.
      type: str
      sample: NO
    started_class_list:
      description:
         The name of the service class currently associated with the address space.
      type: str
      sample: SYSSTC
    started_time:
      description:
         The time when the started task started.
      type: str
      sample: "2025-09-11 18:21:50.293644+00:00"
    system_management_control:
      description:
         Number of outstanding step-must-complete requests.
      type: str
      sample: 000
    task_identifier:
      description:
         - The name of a system address space.
         - The name of a step, for a job or attached APPC transaction program attached by an initiator.
         - The identifier of a task created by the START command.
         - The name of a step that called a cataloged procedure.
         - STARTING if initiation of a started job, system task, or attached APPC transaction program is incomplete.
         - MASTER* for the master address space.
         - The name of an initiator address space.
      type: str
      sample: SPROC
    task_name:
      description:
         - The name of the started task.
      type: str
      sample: SAMPLE
    task_status:
      description:
         - IN for swapped in.
         - OUT for swapped out, ready to run.
         - OWT for swapped out, waiting, not ready to run.
         - OU* for in process of being swapped out.
         - IN* for in process of being swapped in.
         - NSW for non-swappable.
      type: str
      sample: NSW
    task_type:
      description:
         - S for started task.
      type: str
      sample: S
    workload_manager:
      description:
         - The name of the workload currently associated with the address space.
      type: str
      sample: SYSTEM
verbose_output:
    description: If C(verbose=true), the system log related to the started task executed state will be shown.
    returned: changed
    type: list
    sample: NC0000000 ZOSMACHINE 25240 12:40:30.15 OMVS0000 00000210....
"""

from ansible.module_utils.basic import AnsibleModule
import traceback
import re
from datetime import datetime, timedelta
import re
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError
)

try:
    from zoautil_py import opercmd, zsystem
except ImportError:
    zoau_exceptions = ZOAUImportError(traceback.format_exc())


def execute_command(operator_cmd, started_task_name, execute_display_before=False, execute_display_after=False, timeout_s=1, **kwargs):
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
    task_params = []
    # as of ZOAU v1.3.0, timeout is measured in centiseconds, therefore:
    timeout_c = 100 * timeout_s
    if execute_display_before:
        task_params = execute_display_command(started_task_name, timeout_c)
    response = opercmd.execute(operator_cmd, timeout_c, **kwargs)

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


def validate_and_prepare_start_command(module):
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
    member = module.params.get('member_name')
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    job_account = module.params.get('job_account')
    parameters = module.params.get('parameters') or []
    device_type = module.params.get('device_type') or ""
    device_number = module.params.get('device_number') or ""
    volume_serial = module.params.get('volume_serial') or ""
    subsystem_name = module.params.get('subsystem')
    reus_asid = module.params.get('reus_asid')
    keyword_parameters = module.params.get('keyword_parameters')
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


def prepare_display_command(module):
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
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
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


def prepare_stop_command(module):
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
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    asid = module.params.get('asid')
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


def prepare_modify_command(module):
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
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    parameters = module.params.get('parameters')
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


def prepare_cancel_command(module):
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
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    asid = module.params.get('asid')
    dump = module.params.get('dump')
    armrestart = module.params.get('armrestart')
    userid = module.params.get('userid')
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


def prepare_force_command(module):
    """Validates parameters and creates force command

    Parameters
    ----------
    module : dict
        The started task force command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    cmd
        The force command in string format.
    """
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    asid = module.params.get('asid')
    arm = module.params.get('arm')
    armrestart = module.params.get('armrestart')
    userid = module.params.get('userid')
    tcb_address = module.params.get('tcb_address')
    retry = module.params.get('retry')
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
    keys = {
        'A': 'asid',
        'CT': 'cpu_time',
        'ET': 'elapsed_time',
        'WUID': 'work_unit_identifier',
        'USERID': 'userid',
        'P': 'priority',
        'PER': 'program_event_recording',
        'SMC': 'system_management_control',
        'PGN': 'program_name',
        'SCL': 'started_class_list',
        'WKL': 'workload_manager',
        'ASTE': 'data_space_address_entry',
        'ADDR SPACE ASTE': 'address_space_second_table_entry',
        'RGP': 'resource_group',
        'DSPNAME': 'dataspace_name',
        'DMN': 'domain_number',
        'AFF': 'affinity',
        'SRVR': 'server',
        'QSC': 'queue_scan_count'
    }
    lines = stdout.strip().split('\n')
    tasks = []
    current_task = {}
    aste_key = "ADDR SPACE ASTE"
    task_header_regex = re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
    kv_pattern = re.compile(rf'({re.escape(aste_key)}|\S+)=(\S+)')
    for line in lines[5:]:
        line = line.strip()
        match_firstline = task_header_regex.search(line)
        if len(line.split()) >= 5 and match_firstline:
            if current_task:
                el_time = current_task.get('elapsed_time')
                if el_time:
                    current_task['started_time'] = calculate_start_time(el_time)
                tasks.append(current_task)
                current_task = {}
            current_task['task_name'] = match_firstline.group(1)
            current_task['task_identifier'] = match_firstline.group(2)
            if "=" not in match_firstline.group(5):
                current_task['proc_step_name'] = match_firstline.group(3)
                current_task['task_type'] = match_firstline.group(4)
                current_task['task_status'] = match_firstline.group(5)
            else:
                current_task['task_type'] = match_firstline.group(3)
                current_task['task_status'] = match_firstline.group(4)
            for match in kv_pattern.finditer(line):
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                current_task[key.lower()] = value
        elif current_task:
            data_space = {}
            for match in kv_pattern.finditer(line):
                dsp_keys = ['dataspace_name', 'data_space_address_entry']
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                if key in dsp_keys:
                    data_space[key] = value
                else:
                    current_task[key.lower()] = value
            if current_task.get("dataspaces"):
                current_task["dataspaces"] = current_task["dataspaces"] + [data_space]
            elif data_space:
                current_task["dataspaces"] = [data_space]
    if current_task:
        el_time = current_task.get('elapsed_time')
        if el_time:
            current_task['started_time'] = calculate_start_time(el_time)
        tasks.append(current_task)
    return tasks


def parse_time(ts_str):
    # Case 1: Duration like "000.005seconds"
    sec_match = re.match(r"^(\d+\.?\d*)\s*S?$", ts_str, re.IGNORECASE)
    if sec_match:
        return timedelta(seconds=float(sec_match.group(1)))
    # Case 2: hh.mm.ss
    hms_match = re.match(r"^(\d+).(\d{2}).(\d{2})$", ts_str)
    if hms_match:
        h, m, s = map(int, hms_match.groups())
        return timedelta(hours=h, minutes=m, seconds=s)
    # Case 3: hhhhh.mm
    hm_match = re.match(r"^(\d{1,5}).(\d{2})$", ts_str)
    if hm_match:
        h, m = map(int, hm_match.groups())
        return timedelta(hours=h, minutes=m)


def calculate_start_time(ts_str):
    now = datetime.now().astimezone()
    parsed = parse_time(ts_str)
    if parsed is None:
        return ""
    # If it's a timedelta (duration), subtract from now → absolute datetime
    if isinstance(parsed, timedelta):
        return f"{now - parsed}"


def fetch_logs(command, timeout):
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
    time_mins = timeout // 60 + 1
    option = '-t' + str(time_mins)
    stdout = zsystem.read_console(options=option)
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


def run_module():
    """Initialize the module.

    Raises
    ------
    fail_json
        z/OS started task operation failed.
    """
    module = AnsibleModule(
        argument_spec={
            'state': {
                'type': 'str',
                'required': True,
                'choices': ['started', 'stopped', 'modified', 'displayed', 'forced', 'cancelled']
            },
            'arm': {
                'type': 'bool',
                'required': False
            },
            'armrestart': {
                'type': 'bool',
                'required': False
            },
            'asid': {
                'type': 'str',
                'required': False
            },
            'device_number': {
                'type': 'str',
                'required': False
            },
            'device_type': {
                'type': 'str',
                'required': False
            },
            'dump': {
                'type': 'bool',
                'required': False
            },
            'identifier_name': {
                'type': 'str',
                'required': False,
                'aliases': ['identifier']
            },
            'job_account': {
                'type': 'str',
                'required': False
            },
            'job_name': {
                'type': 'str',
                'required': False,
                'aliases': ['job', 'task_name', 'task']
            },
            'keyword_parameters': {
                'type': 'dict',
                'required': False,
                'no_log': False
            },
            'member_name': {
                'type': 'str',
                'required': False,
                'aliases': ['member']
            },
            'parameters': {
                'type': 'list',
                'elements': 'str',
                'required': False
            },
            'retry': {
                'type': 'str',
                'required': False,
                'choices': ['YES', 'NO']
            },
            'reus_asid': {
                'type': 'str',
                'required': False,
                'choices': ['YES', 'NO']
            },
            'subsystem': {
                'type': 'str',
                'required': False
            },
            'tcb_address': {
                'type': 'str',
                'required': False
            },
            'userid': {
                'type': 'str',
                'required': False
            },
            'verbose': {
                'type': 'bool',
                'required': False,
                'default': False
            },
            'volume_serial': {
                'type': 'str',
                'required': False
            },
            'wait_time': {
                'type': 'int',
                'required': False,
                'default': 0
            }
        },
        mutually_exclusive=[
            ['device_number', 'device_type']
        ],
        supports_check_mode=True
    )

    args_def = {
        'state': {
            'arg_type': 'str',
            'required': True
        },
        'arm': {
            'arg_type': 'bool',
            'required': False
        },
        'armrestart': {
            'arg_type': 'bool',
            'required': False
        },
        'asid': {
            'arg_type': 'str',
            'required': False
        },
        'device_number': {
            'arg_type': 'str',
            'required': False
        },
        'device_type': {
            'arg_type': 'str',
            'required': False
        },
        'dump': {
            'arg_type': 'bool',
            'required': False
        },
        'identifier_name': {
            'arg_type': 'identifier_name',
            'required': False,
            'aliases': ['identifier']
        },
        'job_account': {
            'arg_type': 'str',
            'required': False
        },
        'job_name': {
            'arg_type': 'str',
            'required': False,
            'aliases': ['job', 'task_name', 'task']
        },
        'keyword_parameters': {
            'arg_type': 'basic_dict',
            'required': False
        },
        'member_name': {
            'arg_type': 'member_name',
            'required': False,
            'aliases': ['member']
        },
        'parameters': {
            'arg_type': 'list',
            'elements': 'str',
            'required': False
        },
        'retry': {
            'arg_type': 'str',
            'required': False
        },
        'reus_asid': {
            'arg_type': 'str',
            'required': False
        },
        'subsystem': {
            'arg_type': 'str',
            'required': False
        },
        'tcb_address': {
            'arg_type': 'str',
            'required': False
        },
        'userid': {
            'arg_type': 'str',
            'required': False
        },
        'verbose': {
            'arg_type': 'bool',
            'required': False
        },
        'volume_serial': {
            'arg_type': 'str',
            'required': False
        },
        'wait_time': {
            'arg_type': 'int',
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
    state = module.params.get('state')
    userid = module.params.get('userid')
    wait_time_s = module.params.get('wait_time')
    verbose = module.params.get('verbose')
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
    NON-CANCELABLE: When cancel command can't stop job and force command is needed.
    CANCELABLE: When force command used without using cancel command
    """
    start_errmsg = ['ERROR', 'INVALID PARAMETER']
    stop_errmsg = ['NOT ACTIVE', 'INVALID PARAMETER']
    display_errmsg = ['NOT ACTIVE', 'INVALID PARAMETER']
    modify_errmsg = ['REJECTED', 'NOT ACTIVE', 'INVALID PARAMETER']
    cancel_errmsg = ['NOT ACTIVE', 'NOT LOGGED ON', 'INVALID PARAMETER', 'DUPLICATE NAME FOUND', 'NON-CANCELABLE']
    force_errmsg = ['NOT ACTIVE', 'NOT LOGGED ON', 'INVALID PARAMETER', 'CANCELABLE', 'DUPLICATE NAME FOUND']
    err_msg = []
    kwargs = {}

    if wait_time_s:
        kwargs.update({"wait": True})

    cmd = ""

    execute_display_before = False
    execute_display_after = False
    if state == "started":
        err_msg = start_errmsg
        execute_display_after = True
        started_task_name, cmd = validate_and_prepare_start_command(module)
    elif state == "displayed":
        err_msg = display_errmsg
        started_task_name, cmd = prepare_display_command(module)
    elif state == "stopped":
        execute_display_before = True
        err_msg = stop_errmsg
        started_task_name, cmd = prepare_stop_command(module)
    elif state == "cancelled":
        if not userid:
            execute_display_before = True
        err_msg = cancel_errmsg
        started_task_name, cmd = prepare_cancel_command(module)
    elif state == "forced":
        if not userid:
            execute_display_before = True
        err_msg = force_errmsg
        started_task_name, cmd = prepare_force_command(module)
    elif state == "modified":
        execute_display_after = True
        err_msg = modify_errmsg
        started_task_name, cmd = prepare_modify_command(module)
    changed = False
    stdout = ""
    stderr = ""
    rc, out, err, task_params = execute_command(cmd, started_task_name, execute_display_before, execute_display_after, timeout_s=wait_time_s, **kwargs)
    isFailed = False
    system_logs = ""
    if err != "" or any(msg in out for msg in err_msg):
        isFailed = True
    # Fetch system logs to validate any error occured in execution
    if not isFailed or verbose:
        system_logs = fetch_logs(cmd.upper(), wait_time_s)
        if any(msg in system_logs for msg in err_msg):
            isFailed = True
    if not verbose:
        system_logs = ""
    current_state = ""
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
        current_state = state
        changed = True
        stdout = out
        stderr = err
        if state == "displayed":
            task_params = extract_keys(out)

    result = dict()

    if module.check_mode:
        module.exit_json(**result)

    result = dict(
        changed=changed,
        state=current_state,
        cmd=cmd,
        tasks=task_params,
        rc=rc,
        stdout=stdout,
        stderr=stderr,
        stdout_lines=stdout.split('\n'),
        stderr_lines=stderr.split('\n'),
        verbose_output=system_logs
    )

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
