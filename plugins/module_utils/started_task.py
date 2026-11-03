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

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import re
import traceback
from datetime import datetime, timedelta
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError
)

try:
    from zoautil_py import opercmd, jobs
except ImportError:
    opercmd = ZOAUImportError(traceback.format_exc())


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
    msg = f"Fetching started task details using task_id {task_id} failed."
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
        module.fail_json(changed=False, rc=1, msg=msg)

    task_name = task_details.name
    asidx = f"{task_details.asid:04X}" if isinstance(task_details.asid, int) else ""
    return task_name, asidx


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
        # Case 1: sss.tttS (example: 000.005seconds)
        sec_match = re.match(r"^(\d+\.?\d*)\s*S?$", ts_str, re.IGNORECASE)
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