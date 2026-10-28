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
        - A trailing asterisk (`*`) wildcard pattern can be used to query multiple started tasks. The pattern
          will apply to all started tasks matching the leading character string in I(job_name).
        - An asterisk (`*`) wildcard cannot be specified in any other character positions in the
          I(job_name) besides a trailing asterisk.
        - Specify (`*`) to query all active started tasks. Note that if (`*`) is specified, all system activity
          status information will be displayed. This may include batch jobs, started tasks, mounted tasks,
          attached APPC transaction programs, system address spaces, active TSO/E users, and initiator address
          spaces.
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
        - Asterisk (`*`) wildcards cannot be specified for the I(task_id) parameter.
    required: false
    type: str
  identifier_name:
    description:
        - The name that identifies the task. It can be paired with I(job_name) to display information about a specific 
          active started task.
        - A trailing asterisk (`*`) wildcard pattern can be used to query multiple identifiers. The pattern
          will apply to all identifiers matching the leading character string in I(identifier_name).
        - An asterisk (`*`) wildcard cannot be specified in any other character positions in the
          I(identifier_name) besides a trailing asterisk.
        - If I(identifier_name) is specified, I(task_id) should not be specified as the parameters
          are mutually exclusive for querying started tasks.
        - If I(identifier_name) is specified, I(job_name) must be specified as well.
    required: false
    type: str
    aliases:
        - identifier
  verbose:
    description:
        - When C(verbose=true), the module will return the started task execution logs. Only started tasks with an associated task ID
          are able to return execution logs.
    required: false
    type: bool
    default: false

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
    job_name: "*"
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
    - Operator DISPLAY command executed via ZOAU C(opercmd) to query for started task information.
  returned: success
  type: str
  sample: "D A,ICSF"
msg:
  description:
    - Failure or skip message returned by the module. An empty string will be returned when no
      error occurs.
  returned: always
  type: str
  sample: "No started task is active with the given name."
rc:
  description:
    - The return code is 0 when command executed successfully.
    - The return code is 1 when ZOAU C(opercmd) throws any error.
    - The return code is 4 when parameter format is invalid.
    - The return code is 5 when no parameters are specified or any parameter validation failed.
    - The return code is 8 when started task is not found using I(task_id).
  returned: always
  type: int
  sample: 0
verbose_output:
  description:
     - If C(verbose=true), the the started task system logs will be shown.
  returned: success
  type: str
  sample:  04.33.04 STC00077 ---- SUNDAY,    12 OCT 2025 ----....
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
    - A list containing the status information for each started tasks matching the specified criteria. An empty
      list will be returned if no started tasks can be found that match the specified criteria.
  returned: success
  type: list
  elements: dict
  contains:
    address_space_aste:
      description:
         - The central address space of the address space second table entry (ASTE).
      returned: always
      type: str
      sample: "03E99440"
    address_space_flag:
      description:
         - The status of the address space. The address space may have no status indicator.
         - "The status may be one of the following: C(LW) - address space is in long wait; C(NF) - address
           space is not dispatchable due to failure; C(PR) - address space has a PER trap active."
      returned: always
      type: str
      sample: "LW"
    address_space_type:
      description:
         - "The type of work that owns the address space, which will be one of the following: C(A) - attached
           APPC transaction program; C(I) - initiator address space; C(J) - job; C(M) - mount; C(S) - started
           task, C(*) - system address space"
      returned: always
      type: str
      sample: "S"
    asidx:
      description:
         - Address space identifier (ASID), in hexadecimal.
      returned: always
      type: str
      sample: "0054"
    cpu_time:
      description:
         - The processor time used by the address space, including the initiator. This time does not
           include system request block (SRB) time.
         - The I(cpu_time) format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).
         - The I(cpu_time) will be C(********) when time exceeds 100000 hours.
         - The I(cpu_time) will be C(NOTAVAIL) when the TOD clock is not working.
      returned: always
      type: str
      sample: "00000.00.00.003"
    data_spaces:
      description:
         - The data spaces associated with the address space.
         - The I(data_spaces) list will be empty if there are no data spaces for the address space
           or if the system could not return the data space information.
      returned: always
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
      returned: always
      type: str
      sample: "00003.20.23.013"
    per_trap:
      description:
         - Whether a program event recording (PER) trap is active in the address space.
      returned: always
      type: bool
      sample: false
    processor_id:
      description:
         - The identifier of the processor, for up to any four processors, if the started task requires
           the services of specific processors.
         - If C(NONE) is specified, the job can run on any processor.
      returned: always
      type: str
      sample: "NONE"
    quiesced:
      description:
         - Whether the address space has be quiesced.
      returned: always
      type: bool
      sample: false
    resource_group:
      description:
         - The resource group associated with the address space.
         - May be C(N/A) if there is no resource group associated with the address space.
      returned: always
      type: str
      sample: "N/A"
    server:
      description:
         - Whether the address space is a server.
      returned: always
      type: bool
      sample: false
    service_class:
      description:
         - The service class currently associated with the address space.
      returned: always
      type: str
      sample: "SYSSTC"
    service_class_period:
      description:
         - The service class period currently associated with the address space.
      returned: always
      type: str
      sample: "1"
    smc_requests:
      description:
         - The number of outstanding step-must-complete requests.
      returned: always
      type: str
      sample: "000"
    started_time:
      description:
         - The time when the started task started, including the UTC offset of the local system time zone.
         - The I(started_time) format is YYYY-MM-DD hh:mm:ss.SSSSSS±hh:mm (year-month-day
           hours.minutes.seconds.milliseconds±hours:minutes).
         - The started time will return an empty string if the value is unable to be calculated.
      returned: always
      type: str
      sample: "2025-09-11 18:21:50.293644+00:00"
    step_name:
      description:
         - If a step is specified in I(task_identifier), I(step_name) is the name of a step within
           the cataloged procedure that was called by the I(task_identifier) step.
         - I(step_name) will return an empty string if there is no catalog procedure.
      returned: always
      type: str
      sample: "IEFPROC"
    task_id:
      description:
         - The started task id, also known as the work unit identifier (WUID).
      returned: always
      type: str
      sample: "STC00018"
    task_identifier:
      description:
         - The task identifier can be the identifier of a task created by the START command, the name
           of a step that called a cataloged procedure, or the name of a system or initiator address space.
         - The task identifier will be C(STARTING) if initiation of a started job or system task is incomplete.
         - The task identifier will be C(*MASTER*) for the master address space.
      returned: always
      type: str
      sample: "SPROC"
    task_name:
      description:
         - The task name can be the name of a started task or the name of a system or initiator address space.
         - The task identifier will be C(STARTING) if initiation of a started job or system task is incomplete.
         - The task identifier will be C(*MASTER*) for the master address space.
      returned: always
      type: str
      sample: "SAMPLE"
    task_status:
      description:
         - "The status of the started task, which will be one of the following: C(IN) - swapped in; C(OUT) - swapped out;
           ready to run; C(OWT) - swapped out, waiting, not ready to run; C(OU*) - in process of being swapped out;
           C(IN*) - in process of being swapped in; C(NSW) - non-swappable"
      returned: always
      type: str
      sample: "NSW"
    unix_address_space:
      description:
         - Whether the address space is a z/OS Unix System Services dubbed address space.
      returned: always
      type: bool
      sample: true
    user_id:
      description:
         - The user ID associated with the unit of work.
      returned: always
      type: str
      sample: "USRT001"
    workload_name:
      description:
         - The name of the workload currently associated with the address space.
      returned: always
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


ERROR_MESSAGES = {
    'IEE341I': 'Started task is not active',
    'IEE535I': 'A parameter on a command is not valid.',
    'IEE708I': 'The value of a keyword specified on a command is incorrect.',
    'NOT FOUND': 'Started task is not active',
}

# Mapping of display command keys to returned field names
TASK_KEYS = {
    'A': 'asidx',
    'PER': 'per_trap',
    'SMC': 'smc_requests',
    'AFF': 'processor_id',
    'CT': 'cpu_time',
    'ET': 'elapsed_time',
    'WUID': 'task_id',
    'USERID': 'user_id',
    'WKL': 'workload_name',
    'SCL': 'service_class',
    'P': 'service_class_period',
    'RGP': 'resource_group',
    'SRVR': 'server',
    'QSC': 'quiesced',
    'ADDR_SPACE_ASTE': 'address_space_aste',
}

# Mapping of display command keys to fields of each entry in the data_spaces list
DATA_SPACE_KEYS = {
    'DSPNAME': 'data_space_name',
    'ASTE': 'data_space_aste'
}

# Fields reported as YES/NO that are returned as booleans
BOOL_KEYS = {'per_trap', 'quiesced', 'server'}

# Default values for fields that may be absent from the display command output
TASK_FIELD_DEFAULTS = {
    **{field: "" for field in TASK_KEYS.values() if field not in BOOL_KEYS},
    **{field: False for field in BOOL_KEYS},
    'address_space_flag': "",
    'step_name': "",
    'data_spaces': [],
}

# Matches KEY=VALUE parameters
KV_PATTERN = re.compile(r'(\S+)=(\S+)')

# Matches task header
STATUS_CODES = r'(?:NSW|OWT|IN|OUT|SWPOUT|INSWAP|OUTSWAP)'
ADDRESS_SPACE_FLAGS = r'(?:LW|NF|PR)'
TASK_HEADER_REGEX = re.compile(
    r'^\s*(?P<task_name>\S+)\s+(?P<task_identifier>\S+)\s+'
    r'(?:(?P<step_name>\S+)\s+)?'
    r'(?P<task_status>' + STATUS_CODES + r')\s+'
    r'(?:(?P<address_space_flag>' + ADDRESS_SPACE_FLAGS + r')\s+)?'
    r'(?P<address_space_type>\S+)\s+\w+=')


def execute_command(operator_cmd):
    """Execute operator command.

    Parameters
    ----------
    operator_cmd : str
        Operator command.

    Returns
    -------
    rc : str
        The return code.
    stdout : str
        The stardard output of the query.
    stderr : str
        The standard error of the query.
    """
    # as of ZOAU v1.3.0, timeout is measured in centiseconds
    timeout_c = 0
    response = opercmd.execute(operator_cmd, timeout_c)

    rc = response.rc
    stdout = response.stdout_response
    stderr = response.stderr_response
    return rc, stdout, stderr


def fetch_task_name_and_asidx(module, task_id):
    """Executes ZOAU python API jobs.fetch command to fetch task name and ASID.

    Parameters
    ----------
    module : AnsibleModule
        The Ansible module object, used to report failures.
    task_id : str
        The started task id.

    Returns
    -------
    task_name : str
        The name of started task.
    asidx : str
        The address space identifier, as a 4-digit uppercase hex string.
    """
    msg = f"Fetching started task details using task_id: {task_id} is failed"
    try:
        task_details = jobs.fetch(task_id)
    except Exception as err:
        response = getattr(err, "response", None)
        stderr = getattr(response, "stderr_response", None) or str(err)
        module.fail_json(
            changed=False,
            rc=getattr(response, "rc", 1),
            msg=msg,
            stderr=stderr,
            stderr_lines=stderr.splitlines()
        )

    if not isinstance(task_details, jobs.Job):
        module.fail_json(changed=False, rc=1, msg=msg, stderr="", stderr_lines=[])

    task_name = task_details.name
    asidx = f"{task_details.asid:04X}"
    return task_name, asidx


def prepare_display_command(module):
    """Validates parameters and creates display command.

    Parameters
    ----------
    module : AnsibleModule
        The Ansible module instance.

    Returns
    -------
    started_task_name : str
        The name of the started task.
    asidx : str
        The address space identifier value in hexadecimal.
    cmd : str
        The display command in string format.
    """
    job_name = module.params.get('job_name')
    task_id = module.params.get('task_id')
    identifier = module.params.get('identifier_name')

    if task_id:
        started_task_name, asidx = fetch_task_name_and_asidx(module, task_id)
    elif job_name:
        asidx = ""
        # Convert asterisk wildcard to "all"
        if job_name == "*":
          job_name = "all"
        started_task_name = f"{job_name}.{identifier}" if identifier else job_name
    else:
        module.fail_json(
            rc=5,
            msg="Either 'job_name' or 'task_id' is mandatory to display started task details.",
            changed=False,
            stderr="", 
            stderr_lines=[]
        )

    cmd = f"D A,{started_task_name}"
    return started_task_name, asidx, cmd


def convert_to_bool(value):
    """Converts a YES/NO string to a boolean.

    Parameters
    ----------
    value : str
        The value returned by the display command.

    Returns
    -------
    bool or str
        True for YES, False for NO, otherwise the original value unchanged.
    """
    upper = value.upper()
    if upper == "YES":
        return True
    if upper == "NO":
        return False
    return value


def extract_kv_pairs(line, current_task):
    """Extract any KEY=VALUE pairs present in the line

    Parameters
    ----------
    line : string
        The STDOUT line
    current_task : dict
        Dictionary of current task key value pairs

    Returns
    -------
    current_task
        The updated current_task dictionary
    """
    line_normalized = line.replace('ADDR SPACE ASTE=', 'ADDR_SPACE_ASTE=')
    data_spaces = current_task.setdefault('data_spaces', [])
    for match in KV_PATTERN.finditer(line_normalized):
        key, value = match.groups()
        if key in DATA_SPACE_KEYS:
            # Each DSPNAME starts a new data space entry; its ASTE follows it.
            if key == 'DSPNAME':
                data_spaces.append({'data_space_name': value, 'data_space_aste': ""})
            elif data_spaces:
                data_spaces[-1][DATA_SPACE_KEYS[key]] = value
        elif key in TASK_KEYS:
            key = TASK_KEYS[key]
            current_task[key] = convert_to_bool(value) if key in BOOL_KEYS else value
    return current_task


def finalize_task(current_task):
    """Finalize the task by formatting the time-related variables

    Parameters
    ----------
    current_task : dict
        Dictionary of current task key value pairs

    Returns
    -------
    current_task
        The updated current_task dictionary with formatted elapsed_time,
        cpu_time and a calculated started_time.
    """
    # Ensure every documented field is always returned, even when the display
    # command output did not include it.
    for key in TASK_FIELD_DEFAULTS:
        current_task.setdefault(key, TASK_FIELD_DEFAULTS[key])
    current_task['started_time'] = ""
    el_time = current_task.get('elapsed_time')
    if el_time:
        current_task['elapsed_time'] = convert_time(el_time) or el_time
        current_task['started_time'] = calculate_start_time(el_time)
    cpu_time = current_task.get('cpu_time')
    if cpu_time:
        current_task['cpu_time'] = convert_time(cpu_time) or cpu_time
    return current_task


def extract_keys(stdout, asidx=None):
    """Extracts keys and values from the given stdout

    Parameters
    ----------
    stdout : string
        The started task display command output
    asidx : string
        The address space identifier value, in hexadecimal.

    Returns
    -------
    tasks
        The list of task parameters.
    """
    lines = stdout.strip().split('\n')
    tasks = []
    current_task = {}

    # Skip first five lines of stdout (command echo and system header banners)
    for line in lines[5:]:
        line = line.strip()
        match_firstline = TASK_HEADER_REGEX.search(line)

        # Detect the start of a new task header block
        if match_firstline:
            # Finalize and append the previous task before starting a new one
            if current_task:
                current_task = finalize_task(current_task)

                # Filter by ASID if specified, or append the task
                if asidx:
                    if asidx == current_task.get('asidx'):
                        tasks.append(current_task)
                        current_task = {}
                        break
                else:
                    tasks.append(current_task)
                current_task = {}

            # Initialize the new task record using named groups
            current_task['task_name'] = match_firstline.group('task_name')
            current_task['task_identifier'] = match_firstline.group('task_identifier')
            current_task['task_status'] = match_firstline.group('task_status')
            current_task['address_space_type'] = match_firstline.group('address_space_type')
            current_task['unix_address_space'] = 'O' in current_task['address_space_type']
            current_task['address_space_type'] = current_task['address_space_type'].replace('O', '')
            step_name = match_firstline.group('step_name')
            if step_name:
                current_task['step_name'] = step_name
            address_space_flag = match_firstline.group('address_space_flag')
            if address_space_flag:
                current_task['address_space_flag'] = address_space_flag

            # Extract any KEY=VALUE pairs present on the header line
            current_task = extract_kv_pairs(line, current_task)

        # Parse continuation lines belonging to the current task
        elif current_task:
            current_task = extract_kv_pairs(line, current_task)

    # Process and append the final task in the output
    if current_task:
        current_task = finalize_task(current_task)

        # Filter by ASID if specified, or append the final task
        if asidx:
            if asidx == current_task.get('asidx'):
                tasks.append(current_task)
        else:
            tasks.append(current_task)

    return tasks


def parse_time(ts_str):
    """Parse timestamp.

    Parameters
    ----------
    ts_str : string
        The time stamp in string format.

    Returns
    -------
    timedelta or None
        Parsed duration as a timedelta, or None if the input cannot be parsed.
    """
    try:
        # Case 1: sss.tttS
        sec_match = re.match(r"^(\d+\.?\d*)\s*S$", ts_str, re.IGNORECASE)
        if sec_match:
            return timedelta(seconds=float(sec_match.group(1)))
        # Case 2: hh.mm.ss
        hms_match = re.match(r"^(\d+)\.(\d{2})\.(\d{2})$", ts_str)
        if hms_match:
            h, m, s = map(int, hms_match.groups())
            return timedelta(hours=h, minutes=m, seconds=s)
        # Case 3: hhhhh.mm
        hm_match = re.match(r"^(\d{1,5})\.(\d{2})$", ts_str)
        if hm_match:
            h, m = map(int, hm_match.groups())
            return timedelta(hours=h, minutes=m)
    except Exception:
        return None
    return None


def calculate_start_time(ts_str):
    """Calculate start time.

    Parameters
    ----------
    ts_str : string
        The time stamp in string format.

    Returns
    -------
    str
        The calculated start time.
    """
    now = datetime.now().astimezone()
    parsed = parse_time(ts_str)
    # If it's a timedelta (duration), subtract from now → absolute datetime
    if isinstance(parsed, timedelta):
        return (now - parsed).isoformat(sep=" ", timespec="microseconds")
    return ""


def convert_time(ts_str):
    """Convert timedelta to hhhhh.mm.ss.SSS format.

    Parameters
    ----------
    ts_str : string
        The time stamp in string format.

    Returns
    -------
    str
        The converted time.
    """
    parsed = parse_time(ts_str)
    if isinstance(parsed, timedelta):
        total_seconds = int(parsed.total_seconds())
        milliseconds = int(parsed.microseconds / 1000)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Format: HHHHH.MM.SS.SSS
        return f"{hours:05}.{minutes:02}.{seconds:02}.{milliseconds:03}"
    return ""


def classify_err_response(rc, out, err):
    """Identify whether STDOUT contains error message or code.

    Parameters
    ----------
    rc : string
        The return code.
    out : string
        The standard output.
    err : string
        The standard error.

    Returns
    -------
    rc : str
        The return code.
    str
        The return message.
    out : str
        The standard output.
    err : str
        The standard error.
    bool
        Whether the STDOUT contains an error message or code.
    """

    """Return (rc, msg, stdout, stderr, is_error)."""
    code = next((c for c in ERROR_MESSAGES if c in out), None)
    if err or code:
        return (rc or 1), ERROR_MESSAGES.get(code), "", (err or out), True
    return rc, "", out, err, False


def get_task_logs(task_id):
    """Get job output logs.

    Parameters
    ----------
    task_id : string
        The started task ID.

    Returns
    -------
    task_logs : str
        The job output logs.
    """
    try:
      task_logs = jobs.read_output(task_id)
    except Exception:
      return ""
    return task_logs


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
            },
            'verbose': {
                'type': 'bool',
                'required': False,
                'default': False
            },
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
            'arg_type': 'str',
            'required': False
        },
        'verbose': {
            'arg_type': 'bool',
            'required': False
        },
    }

    # Validate input parameters
    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        stderr = str(err)
        module.fail_json(
            changed=False,
            rc=4,
            msg='Parameter verification failed.',
            stderr=stderr,
            stderr_lines=stderr.splitlines()
        )

    # Initialize logging module
    module_verbosity_level = module._verbosity
    SingletonLogger().get_logger(module_verbosity_level)

    # Create DISPLAY command
    started_task_name, asidx, cmd = prepare_display_command(module)

    # Initialize variables and execute DISPLAY command
    rc, out, err = execute_command(cmd)
    out, err = out or "", err or ""

    # Validate the sysout of opercmd with the above listed error codes to find if any error occured
    rc, msg, stdout, stderr, is_error = classify_err_response(rc, out, err)

    fail_result = dict(
      changed=False,
      rc=rc,
      msg=msg,
      stderr=stderr,
      stderr_lines=stderr.splitlines()
    )

    if is_error:
        module.fail_json(**fail_result)

    # Extract return fields from STDOUT
    task_params = extract_keys(out, asidx)
    if not task_params:
        fail_result.update(
          rc=1,
          msg="No started task is active with the given name {0}.".format(started_task_name)
        )
        module.fail_json(**fail_result)

    task_output_logs = ""
    if module.params.get('verbose'):
      task_output_logs = get_task_logs(task_params[0].get('task_id'))

    success_result = dict(
      changed=False,
      cmd=cmd,
      tasks=task_params,
      rc=rc,
      msg=msg,
      stdout=stdout,
      stderr=stderr,
      stdout_lines=stdout.splitlines(),
      stderr_lines=stderr.splitlines(),
      verbose_output=task_output_logs
    )

    module.exit_json(**success_result)


if __name__ == '__main__':
    run_module()
