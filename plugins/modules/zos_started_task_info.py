#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2026
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
module: zos_started_task_info
version_added: 2.2.0
author:
  - "Sarah Miller (@hmillersarah)"
short_description: Retrieve information on started tasks.
description:
  - Retrieve detailed status information for long-running started tasks on a single LPAR.

options:
  job_name:
    description:
        - The started task name used to query the system.
        - The name must be a single continuous string with no spaces or blank characters.
        - An asterisk wildcard pattern can be used to query multiple started tasks.
        - A trailing asterisk (\*) wildcard pattern can be used to query multiple started tasks. The pattern
          will apply to all started tasks matching the leading character string in I(job_name).
        - An asterisk (\*) wildcard cannot be specified in any other character positions in the
          I(job_name) besides a trailing asterisk.
        - Specify I(all) to query all active started tasks.
        - The name is case-insensitive and is normalized to uppercase before execution.
        - If a I(job_name) is specified, I(task_id) should not be specified as the parameters
          are mutually exclusive for querying started tasks.
    required: false
    type: str
    aliases:
        - job
        - task
        - task_name
  task_id:
    description:
        - A unique system-generated identifier that represents a specific started task running in z/OS. This id starts with STC.
        - If a I(task_id) is specified, I(job_name) should not be specified as the parameters
          are mutually exclusive for querying started tasks.
        - If a I(task_id) is specified, I(identifier_name) should not be specified as the parameters
          are mutually exclusive for querying started tasks.
    required: false
    type: str
  identifier_name:
    description:
        - The name that identifies the task. It can be paired with I(job_name) to display information about a specific 
          active started task.
        - If I(identifier_name) is specified, I(task_id) should not be specified as the parameters
          are mutually exclusive for querying started tasks.
        - If I(identifier_name) is specified, I(job_name) must be specified as well.
    required: false
    type: str
    aliases:
        - identifier

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

notes:
  - Either C(job_name) or C(task_id) is mandatory to display started task status information.
"""

EXAMPLES = r"""
- name: Display a started task using a started task name.
  zos_started_task_info:
    job_name: "PROCAPP"

- name: Display a started task using a started task name and identifier.
  zos_started_task_info:
    job_name: "PROCAPP.SAMPLE"

- name: Display a started task using a started task id.
  zos_started_task_info:
    task_id: "STC00012"

- name: Display all started tasks that begin with an s using a wildcard.
  zos_started_task_info:
    job_name: "s*"

- name: Display all started tasks.
  zos_started_task_info:
    job_name: "all"
"""

RETURN = r"""
changed:
  description:
    - Indicates whether any changes were made to the system. Always C(false) for info modules.
  returned: always
  type: bool
  sample: false
cmd:
  description:
    - Operator DISPLAY command executed via opercmd to query for started task information.
  returned: changed
  type: str
  sample: "D A,ICSF"
msg:
  description:
    - Failure or skip message returned by the module.
  returned: failure or skipped
  type: str
  sample: "No started task is active with the given name."
rc:
  description:
    - The return code is 0 when command executed successfully.
    - The return code is 1 when opercmd throws any error.
    - The return code is 4 when task_id format is invalid.
    - The return code is 5 when no parameters are specified or any parameter validation failed.
    - The return code is 8 when started task is not found using task_id.
  returned: changed
  type: int
  sample: 0
stderr:
  description:
    - The standard error (STDERR) from command execution. An empty string will be returned when no
      error occurs.
  returned: always
  type: str
  sample: "An error has occurred."
stderr_lines:
  description:
    - List of strings containing individual lines from STDERR.
  returned: always
  type: list
  sample: ["An error has occurred"]
stdout:
  description:
    - The standard output (STDOUT) from command execution. This return field may be empty when an
      error occurs.
  returned: success
  type: str
  sample: "EC00000A   2026287  12:14:28.00             ISF031I CONSOLE OMVS0000 ACTIVATED..."
stdout_lines:
  description:
    - List of strings containing individual lines from STDOUT.
  returned: success
  type: list
  sample: ["EC00000A   2026287  12:14:28.00             ISF031I CONSOLE OMVS0000 ACTIVATED"]
tasks:
  description:
    - The status information for a list of started tasks matching the specified criteria.
  returned: success
  type: list
  elements: dict
  contains:
    address_space_aste:
      description:
         - The central address space of the address space second table entry (ASTE).
      type: str
      sample: "03E99440"
    address_space_status:
      description:
         - The status of the address space. The address space may have no status indicator.
         - "The status may be one of the following: C(LW) - address space is in long wait; C(NF) - address
           space is not dispatchable due to failure; C(PR) - address space has a PER trap active."
      type: str
      sample: "LW"
    asidx:
      description:
         - Address space identifier (ASID), in hexadecimal.
      type: str
      sample: "0054"
    cpu_time:
      description:
         - The processor time used by the address space, including the initiator. This time does not
           include system request block (SRB) time.
         - The I(cpu_time) format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).
         - The I(cpu_time) will be C(********) when time exceeds 100000 hours.
         - The I(cpu_time) will be C(NOTAVAIL) when the TOD clock is not working.
      type: str
      sample: "00000.00.00.003"
    data_spaces:
      description:
         - The data spaces associated with the address space.
         - The I(data_spaces) list will be empty if there are no data spaces for the address space
           or if the system could not return the data space information.
      type: list
      elements: dict
      contains:
        data_space_name:
            description:
                - The data space name associated with the address space.
            type: str
            sample: "00000IEF"
        data_space_aste:
            description:
                - The central address space of the data space address space second table entry (ASTE).
            type: str
            sample: "0594D600"
    dmn:
      description:
         - The domain number (DMN) of the started task address space.
         - The DMN is not applicable for modern z/OS systems operating in goal mode.
      type: str
      sample: "N/A"
    elapsed_time:
      description:
         - For address spaces other than system address spaces, this value represents the elapsed time since the task
           was selected for execution.
         - For system address spaces created before master scheduler initialization, this value represents the elapsed
           time since the master scheduler was initialized.
         - For system address spaces created after master scheduler initialization, this value represents the elapsed
           time since the system address space was created.
         - The I(elapsed_time) format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).
         - The I(elapsed_time) will be C(********) when time exceeds 100000 hours.
         - The I(elapsed_time) will be C(NOTAVAIL) when the TOD clock is not working.
      type: str
      sample: "00003.20.23.013"
    per_trap:
      description:
         - Whether a program event recording (PER) trap is active in the address space.
      type: bool
      sample: false
    pgn:
      description:
         - The performance group number (PGN) of the started task address space.
         - The PGN is not applicable for modern z/OS systems operating in goal mode.
      type: str
      sample: "N/A"
    processor_id:
      description:
         - The identifier of the processor, for up to any four processors, if the started task requires
           the services of specific processors.
         - If C(NONE) is specified, the job can run on any processor.
      type: str
      sample: "NONE"
    quiesced:
      description:
         - Whether the address space has be quiesced.
      type: bool
      sample: false
    resource_group:
      description:
         - The resource group associated with the address space.
         - May be C(N/A) if there is no resource group associated with the address space.
      type: str
      sample: "N/A"
    server:
      description:
         - Whether the address space is a server.
      type: bool
      sample: false
    service_class:
      description:
         - The service class currently associated with the address space.
      type: str
      sample: "SYSSTC"
    service_class_period:
      description:
         - The service class period currently associated with the address space.
      type: str
      sample: "1"
    smc_requests:
      description:
         - The number of outstanding step-must-complete requests.
      type: str
      sample: "000"
    started_time:
      description:
         - The time when the started task started, including the UTC offset of the local system time zone.
         - The I(started_time) format is YYYY-MM-DD hh:mm:ss.SSSSSS±hh:mm (year-month-day
           hours.minutes.seconds.milliseconds±hours:minutes).
         - The started time will return an empty string if the value is unable to be calculated.
      type: str
      sample: "2025-09-11 18:21:50.293644+00:00"
    step_name:
      description:
         - If a step is specified in I(task_identifier), I(step_name) is the name of a step within
           the cataloged procedure that was called by the I(task_identifier) step.
         - I(step_name) will return an empty string if there is no catalog procedure.
      type: str
      sample: "IEFPROC"
    task_id:
      description:
         - The started task id, also known as the work unit identifier (WUID).
      type: str
      sample: "STC00018"
    task_identifier:
      description:
         - The task identifier can be the identifier of a task created by the START command, the name
           of a step that called a cataloged procedure, or the name of a system or initiator address space.
         - The task identifier will be C(STARTING) if initiation of a started job or system task is incomplete.
         - The task identifier will be C(*MASTER*) for the master address space.
      type: str
      sample: "SPROC"
    task_name:
      description:
         - The task name can be the name of a started task or the name of a system or initiator address space.
         - The task identifier will be C(STARTING) if initiation of a started job or system task is incomplete.
         - The task identifier will be C(*MASTER*) for the master address space.
      type: str
      sample: "SAMPLE"
    task_status:
      description:
         - "The status of the started task, which will be one of the following: C(IN) - swapped in; C(OUT) - swapped out;
           ready to run; C(OWT) - swapped out, waiting, not ready to run; C(OU*) - in process of being swapped out;
           C(IN*) - in process of being swapped in; C(NSW) - non-swappable"
      type: str
      sample: "NSW"
    type:
      description:
         - "The type of information retrieved, which will be one of the following: C(A) - attached APPC transaction program;
           C(I) - initiator address space; C(J) - job; C(M) - mount; C(S) - started task, C(*) - system address space"
      type: str
      sample: "S"
    unix_address_space:
      description:
         - Whether the address space is a z/OS Unix System Services dubbed address space.
      type: bool
      sample: true
    user_id:
      description:
         - The user ID associated with the unit of work.
      type: str
      sample: "USRT001"
    workload_name:
      description:
         - The name of the workload currently associated with the address space.
      type: str
      sample: "SYSTEM"
"""

from ansible.module_utils.basic import AnsibleModule
import traceback
import re
import math
import time
from datetime import datetime, timedelta, timezone
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dependency_checker import (
    validate_dependencies,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger

try:
    from zoautil_py import opercmd, zsystem, jobs
except ImportError:
    opercmd = ZOAUImportError(traceback.format_exc())
    zsystem = ZOAUImportError(traceback.format_exc())
    jobs = ZOAUImportError(traceback.format_exc())


def execute_command(operator_cmd):
    """Execute operator command.

    Parameters
    ----------
    operator_cmd : str
        Operator command.

    Returns
    -------
    tuple
        Tuple containing the RC, standard out, standard err of the
        query script and started task parameters.
    """
    # as of ZOAU v1.3.0, timeout is measured in centiseconds
    timeout_c = 0
    response = opercmd.execute(operator_cmd, timeout_c)

    rc = response.rc
    stdout = response.stdout_response
    stderr = response.stderr_response
    return rc, stdout, stderr


def fetch_task_name_and_asidx(module, task_id):
    """Executes JLS command and fetches task name

    Parameters
    ----------
    module : dict
        The started task display command parameters.
    task_id : str
        The started task id starts with STC.

    Returns
    -------
    task_name
        The name of started task.
    """
    try:
        task_details = jobs.fetch(task_id)
        if not isinstance(task_details, jobs.Job):
            module.fail_json(
                rc=1,
                msg=f"Fetching started task details using task_id: {task_id} is failed",
                changed=False
            )
    except Exception as err:
        module.fail_json(
            rc=err.response.rc,
            msg=f"Fetching started task details using task_id: {task_id} is failed with ZOAU error: {err.response.stderr_response}",
            changed=False
        )
    task_name = task_details.name
    asidx = f"{task_details.asid:04X}"
    return task_name, asidx


def prepare_display_command(module):
    """Validates parameters and creates display command

    Parameters
    ----------
    module : dict
        The started task display command parameters.

    Returns
    -------
    started_task_name
        The name of started task.
    asidx
        The address space identifier value, in hexadecimal.
    cmd
        The display command in string format.
    """
    identifier = module.params.get('identifier_name')
    job_name = module.params.get('job_name')
    task_id = module.params.get('task_id')
    started_task_name = ""
    task_name = asidx = ""
    if task_id:
        task_name, asidx = fetch_task_name_and_asidx(module, task_id)
    if task_name:
        started_task_name = task_name
    elif job_name:
        if (job_name == "all"):
            started_task_name = "STC"
        else:
            started_task_name = job_name
        if identifier:
            started_task_name = f"{started_task_name}.{identifier}"
    else:
        module.fail_json(
            rc=5,
            msg="either job_name or task_id is mandatory to display started task details.",
            changed=False
        )
    cmd = f"D A,{started_task_name}"
    return started_task_name, asidx, cmd


def extract_keys(stdout, asidx=None, task_params_before=None):
    """Extracts keys and values from the given stdout

    Parameters
    ----------
    stdout : string
        The started task display command output
    asidx : string
        The address space identifier value, in hexadecimal.
    task_params_before: list
        List of started task details which have same started task name.

    Returns
    -------
    tasks
        The list of task parameters.
    """
    keys = {
        'A': 'asidx',
        'CT': 'cpu_time',
        'ET': 'elapsed_time',
        'WUID': 'task_id'
    }
    lines = stdout.strip().split('\n')
    tasks = []
    current_task = {}
    task_header_regex = re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
    kv_pattern = re.compile(r'(\S+)=(\S+)')
    for line in lines[5:]:
        line = line.strip()
        match_firstline = task_header_regex.search(line)
        if len(line.split()) >= 5 and match_firstline:
            if current_task:
                current_task['started_time'] = ""
                el_time = current_task.get('elapsed_time')
                if el_time:
                    current_task['elapsed_time'] = convert_cpu_time(el_time) or current_task['elapsed_time']
                    current_task['started_time'] = calculate_start_time(el_time)
                if asidx:
                    if asidx == current_task.get('asidx'):
                        tasks.append(current_task)
                        current_task = {}
                        break
                elif task_params_before:
                    current_asid = current_task.get('asidx')
                    task_exists_before = False
                    for task in task_params_before:
                        if task.get('asidx') == current_asid:
                            task_exists_before = True
                            break
                    if not task_exists_before:
                        tasks.append(current_task)
                else:
                    tasks.append(current_task)
                current_task = {}
            current_task['task_name'] = match_firstline.group(1)
            current_task['task_identifier'] = match_firstline.group(2)
            for match in kv_pattern.finditer(line):
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                    current_task[key.lower()] = value
        elif current_task:
            for match in kv_pattern.finditer(line):
                key, value = match.groups()
                if key in keys:
                    key = keys[key]
                    current_task[key.lower()] = value
    if current_task:
        current_task['started_time'] = ""
        el_time = current_task.get('elapsed_time')
        if el_time:
            current_task['elapsed_time'] = convert_cpu_time(el_time) or current_task['elapsed_time']
            current_task['started_time'] = calculate_start_time(el_time)
        cpu_time = current_task.get('cpu_time')
        if cpu_time:
            current_task['cpu_time'] = convert_cpu_time(cpu_time) or current_task['cpu_time']
        if asidx:
            if asidx == current_task.get('asidx'):
                tasks.append(current_task)
        elif task_params_before:
            current_asid = current_task.get('asidx')
            task_exists_before = False
            for task in task_params_before:
                if task.get('asidx') == current_asid:
                    task_exists_before = True
                    break
            if not task_exists_before:
                tasks.append(current_task)
        else:
            tasks.append(current_task)
    return tasks


def parse_time(ts_str):
    """Parse timestamp

    Parameters
    ----------
    ts_str : string
        The time stamp in string format

    Returns
    -------
    timestamp
        Transformed timestamp
    """
    try:
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
    except Exception:
        return ""
    return ""


def calculate_start_time(ts_str):
    now = datetime.now().astimezone()
    parsed = parse_time(ts_str)
    if parsed is None:
        return ""
    # If it's a timedelta (duration), subtract from now → absolute datetime
    if isinstance(parsed, timedelta):
        return f"{now - parsed}"
    return ""


def convert_cpu_time(ts_str):
    parsed = parse_time(ts_str)
    if parsed is None:
        return ""
    # If it's a timedelta (duration), subtract from now → absolute datetime
    if isinstance(parsed, timedelta):
        total_seconds = int(parsed.total_seconds())
        milliseconds = int(parsed.microseconds / 1000)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Format: HHHHH.MM.SS.SSS
        return f"{hours:05}.{minutes:02}.{seconds:02}.{milliseconds:03}"
    return ""


def run_module():
    """Initialize the module.

    Raises
    ------
    fail_json
        z/OS started task operation failed.
    """
    module = AnsibleModule(
        argument_spec={
            'identifier_name': {
                'type': 'str',
                'required': False,
                'aliases': ['identifier']
            },
            'job_name': {
                'type': 'str',
                'required': False,
                'aliases': ['job', 'task_name', 'task']
            },
            'task_id': {
                'type': 'str',
                'required': False
            }
        },
        mutually_exclusive=[
            ['job_name', 'task_id'],
            ['identifier_name', 'task_id']
        ],
        supports_check_mode=True
    )

    validate_dependencies(module)

    args_def = {
        'identifier_name': {
            'arg_type': 'identifier_name',
            'required': False,
            'aliases': ['identifier']
        },
        'job_name': {
            'arg_type': 'str',
            'required': False,
            'aliases': ['job', 'task_name', 'task']
        },
        'task_id': {
            'type': 'str',
            'required': False
        }
    }

    # Validate input parameters
    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    result = dict()
    if module.check_mode:
        module.exit_json(**result)

    # Initialize logging module
    module_verbosity_level = module._verbosity
    SingletonLogger().get_logger(module_verbosity_level)

    """
    Below error messages or error codes are used to determine if response has any error.
    """
    error_details = {
            'IEE535I': 'A parameter on a command is not valid.',
            'NOT FOUND': 'Started task is not active',
            'IEE341I': 'Started task is not active',
            'IEE708I': 'The value of a keyword specified on a command is incorrect.',
        }
    err_msg = ['IEE341I', 'IEE535I', 'NOT FOUND', 'IEE708I']

    kwargs = {}
    kwargs.update({"wait": True})

    cmd = ""
    started_task_name, asidx, cmd = prepare_display_command(module)

    changed = False
    stdout = ""
    stderr = ""
    rc, out, err = execute_command(cmd)

    is_failed = False
    msg = ""
    task_params = []

    # Validate the sysout of opercmd with the above listed error codes to find if any error occured
    found_msg = next((msg for msg in err_msg if msg in out), None)
    if err != "" or found_msg:
        is_failed = True
        msg = error_details.get(found_msg)

    if is_failed:
        if rc == 0:
            rc = 1
        changed = False
        stdout = out
        stderr = err
        if err == "" or err is None:
            stderr = out
            stdout = ""
    else:
        task_params = extract_keys(out, asidx)
        if not task_params:
            module.fail_json(
                rc=1,
                msg="No started task is active with the given name.",
                changed=False
            )
        changed = True
        stdout = out
        stderr = err

    result = dict(
        changed=changed,
        cmd=cmd,
        msg=msg,
        tasks=task_params,
        rc=rc,
        stdout=stdout,
        stderr=stderr,
        stdout_lines=stdout.split('\n'),
        stderr_lines=stderr.split('\n'),
    )

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
