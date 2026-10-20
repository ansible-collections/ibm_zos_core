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
    required: false
    type: str

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
- name: Display a started task using a started task name.
  zos_started_task_info:
    job_name: "PROCAPP"

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
    - The return code is 5 when any parameter validation failed.
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
