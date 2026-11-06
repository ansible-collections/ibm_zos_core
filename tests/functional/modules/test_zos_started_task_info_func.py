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
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name
from ibm_zos_core.tests.helpers.dataset import get_tmp_member
from shellescape import quote
import re
import pytest

TMP_DIRECTORY = "/tmp/"
PROC_PDS = "USER.PRIVATE.PROCLIB"
TASK_JCL_CONTENT="""//STEP1    EXEC PGM=BPXBATCH
//STDOUT   DD   SYSOUT=*
//STDERR   DD   SYSOUT=*
//STDPARM  DD *
SH sleep 600
/*"""
EXPECTED_KEYS = {
    "address_space_aste", "address_space_flag", "address_space_type", "asidx",
    "cpu_time", "data_spaces", "elapsed_time", "per_trap",
    "quiesced", "resource_group", "server",
    "service_class", "service_class_period", "smc_requests",
    "started_time", "step_name", "task_id", "task_identifier",
    "task_name", "task_status", "unix_address_space",
    "user_id", "workload_name"
}

def _skip_if_task_not_running(hosts, job_name):
    query_results = hosts.all.zos_job_query(job_name=job_name)
    has_tasks = any(result.get("jobs") for result in query_results.contacted.values())
    if not has_tasks:
        pytest.skip(f"Started task '{job_name}' is not active on target LPAR")

# Get info for started task using job_name
def test_get_started_task_info_using_job_name(ansible_zos_module):
    job_name = "TESTTSK"
    time_pattern = re.compile(r'^\d{5}\.\d{2}\.\d{2}\.\d{3}$|^\*{8}$|^NOTAVAIL$')

    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        member_name = "S" + get_tmp_member()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        # Write JCL to USS file
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        # USS file is copied to a sequential data set
        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        # The data set is copied to the PDS member
        hosts.all.shell(
            cmd="dcp {0} \"//'{1}({2})'\"".format(data_set_name, PROC_PDS, member_name)
        )

        # Start a started task
        start_results = hosts.all.zos_started_task(
            state="started",
            member=member_name,
            job_name=job_name
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""

        # Get started task info using job name
        info_results = hosts.all.zos_started_task_info(
            job_name=job_name
        )

        for result in info_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""
            assert result.get("cmd") == f"D A,{job_name}"
            assert result.get("stdout") != ""
            for task in result.get("tasks"):
                assert EXPECTED_KEYS.issubset(task.keys())
                # Bool parameters
                assert isinstance(task.get("per_trap"), bool)
                assert isinstance(task.get("quiesced"), bool)
                assert isinstance(task.get("server"), bool)
                assert isinstance(task.get("unix_address_space"), bool)
                # Data space as list
                assert isinstance(task.get("data_spaces"), list)
                # Address space type as started task
                assert task.get("address_space_type") == "S"
                # Task status
                assert task.get("task_status") in {"IN", "OUT", "OWT", "OU*", "IN*", "NSW"}
                # STC in task ID
                assert task.get("task_id").startswith("STC")
                # asidx must be a 4-character uppercase hex string
                assert re.match(r'^[0-9A-F]{4}$', task.get("asidx", ""))
                # cpu_time and elapsed_time must match hhhhh.mm.ss.SSS or be the sentinel values
                assert time_pattern.match(task.get("cpu_time", ""))
                assert time_pattern.match(task.get("elapsed_time", ""))
                # started_time must be a non-empty ISO timestamp (YYYY-MM-DD hh:mm:ss.SSSSSS±hh:mm)
                assert re.match(
                    r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}[+-]\d{2}:\d{2}$',
                    task.get("started_time", "")
                )
                assert task.get("task_name", "").upper() == job_name.upper()

    finally:
        # Cancel the started task
        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task=job_name
        )
        # Remove USS temp directory containing the USS file
        hosts.all.file(path=temp_path, state="absent")
        # Remove the temp sequential data set
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        # Remove the member from the PDS
        hosts.all.shell(
            cmd="mrm '{0}({1})'".format(PROC_PDS, member_name)
        )

# Display address space flag
def test_get_started_task_info_address_space_flag(ansible_zos_module):
    job_name = "SPROC"
    per_trap_id = "PER1"

    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        member_name = "S" + get_tmp_member()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        # Write JCL to USS file
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        # USS file is copied to a sequential data set
        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        # The data set is copied to the PDS member
        hosts.all.shell(
            cmd="dcp {0} \"//'{1}({2})'\"".format(data_set_name, PROC_PDS, member_name)
        )

        # Start a started task
        start_results = hosts.all.zos_started_task(
            state="started",
            member=member_name,
            job_name=job_name
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""

        # Set PER trap
        per_trap_results = hosts.all.zos_operator(
            cmd=f"SLIP SET,IF,ID={per_trap_id},JOBNAME={job_name},RANGE=1B0000,ACTION=SVCD,MATCHLIM=5,END"
        )

        for result in per_trap_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert f"SLIP TRAP ID={per_trap_id} SET" in result.get("stdout")

        # Get started task info using job name
        info_results = hosts.all.zos_started_task_info(
            job_name=job_name
        )

        for result in info_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""
            assert result.get("cmd") == f"D A,{job_name}"
            assert result.get("stdout") != ""
            for task in result.get("tasks"):
                assert EXPECTED_KEYS.issubset(task.keys())
                assert task.get("address_space_flag") == "PR"

    finally:
        # Delete PER trap
        del_trap_results = hosts.all.zos_operator(
            cmd=f"SLIP DEL,ID={per_trap_id}"
        )
        # Stop started task
        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task=job_name
        )
        # Remove USS temp directory containing the USS file
        hosts.all.file(path=temp_path, state="absent")
        # Remove the temp sequential data set
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        # Remove the member from the PDS
        hosts.all.shell(
            cmd="mrm '{0}({1})'".format(PROC_PDS, member_name)
        )

# Get info for started task using job_name with wildcard
def test_get_started_task_info_using_job_name_with_wildcard(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "I*"

    _skip_if_task_not_running(hosts, job_name)

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name}"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())
            assert task.get("task_name").startswith("I")

# Get info for started task with job_name and identifier
def test_get_started_task_info_using_job_name_and_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "ICSF"
    identifier_name = "ICSF"

    _skip_if_task_not_running(hosts, job_name)

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name,
        identifier_name=identifier_name
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name}.{identifier_name}"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())
            assert task.get("task_name", "").upper() == job_name.upper()
            assert task.get("task_identifier", "").upper() == identifier_name.upper()

# Get info for all started tasks
def test_get_info_for_all_started_tasks(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "*"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "D A,ALL"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())

# Get info for started task using task_id
def test_get_started_task_info_using_task_id(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "ICSF"

    query_results = hosts.all.zos_job_query(job_name=job_name)

    task_id = None
    for result in query_results.contacted.values():
        for job in result.get("jobs", []):
            task_id = job.get("job_id")
    if task_id is None:
        pytest.skip(f"No active started task found for {job_name}")

    info_results = hosts.all.zos_started_task_info(
        task_id=task_id
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name}"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())

# Get info for started task with multiple data spaces
def test_get_info_for_started_task_with_multiple_data_spaces(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "IMSVTAM"

    _skip_if_task_not_running(hosts, job_name)

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name}"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())
            assert task.get("task_name", "").upper() == job_name.upper()
            for data_space in task.get("data_spaces"):
                assert data_space.get("data_space_aste") is not None
                assert data_space.get("data_space_name") is not None

# Verbose output is returned when verbose is set to true
def test_get_started_task_info_verbose_output(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "ICSF"

    _skip_if_task_not_running(hosts, job_name)

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name,
        verbose=True
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name}"
        assert result.get("stdout") != ""
        assert result.get("verbose_output") != ""

# Get info for started task with lower case job name
def test_get_started_task_info_using_lowercase_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "icsf"
    job_name_uppercase = job_name.upper()

    _skip_if_task_not_running(hosts, job_name)

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"D A,{job_name_uppercase}"
        assert result.get("stdout") != ""
        for task in result.get("tasks"):
            assert EXPECTED_KEYS.issubset(task.keys())
            assert task.get("task_name") == job_name_uppercase

# Get info for started task using invalid job_name (failure case)
def test_get_started_task_info_using_invalid_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "a&bc"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 1
        assert result.get("tasks") is None
        assert "INVALID PARAMETER" in result.get("stderr")
        assert result.get("msg") == "A parameter is not valid."

# Get info for started task using invalid wildcard in job_name (failure case)
def test_get_started_task_info_using_job_name_with_invalid_wildcard(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "*CSF"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 1
        assert result.get("tasks") is None
        assert "INVALID PARAMETER" in result.get("stderr")
        assert result.get("msg") == "A parameter is not valid."

# Get info for started task using job_name that cannot be found (failure case)
def test_get_started_task_info_job_name_not_found(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "INVALID"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 1
        assert result.get("tasks") is None
        assert f"{job_name} NOT FOUND" in result.get("stderr")
        assert result.get("msg") == "Started task could not be found."

# Get info for started task using invalid task_id (failure case)
def test_get_started_task_info_using_invalid_task_id(ansible_zos_module):
    hosts = ansible_zos_module
    task_id="STC99999"

    info_results = hosts.all.zos_started_task_info(
        task_id=task_id
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 8
        assert result.get("tasks") is None
        assert f"BGYSC3503E Failed to retrieve job list." in result.get("stderr")
        assert result.get("msg") == f"Fetching started task details using task_id {task_id} failed."

# Get info for a started using task_id that does not exist (failure case)
def test_get_started_task_info_using_nonexistent_task_id(ansible_zos_module):
    hosts = ansible_zos_module
    task_id="STC0012345"

    info_results = hosts.all.zos_started_task_info(
        task_id=task_id
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 4
        assert result.get("tasks") is None
        assert f"BGYSC3506E Invalid job id format {task_id}" in result.get("stderr")
        assert result.get("msg") == f"Fetching started task details using task_id {task_id} failed."

# Get info for started task using task_id that is not active (failure case)
def test_get_started_task_info_task_id_not_active(ansible_zos_module):
    job_name = "NTASKID"

    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        member_name = "S" + get_tmp_member()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        # Write JCL to USS file
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        # USS file is copied to a sequential data set
        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        # The data set is copied to the PDS member
        hosts.all.shell(
            cmd="dcp {0} \"//'{1}({2})'\"".format(data_set_name, PROC_PDS, member_name)
        )

        # Start a started task
        start_results = hosts.all.zos_started_task(
            state="started",
            member=member_name,
            job_name=job_name
        )
        
        task_id = None
        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""
            for task in result.get("tasks", []):
                task_id = task.get("task_id")
        
        assert task_id is not None, f"No task_id found in start_results for {job_name}"

        # Cancel the started task
        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task=job_name
        )

        for result in stop_results.contacted.values():
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""

        info_results = hosts.all.zos_started_task_info(
            task_id=task_id
        )

        # The cancelled task is still known to JES, so the task_id lookup succeeds,
        # but the task is no longer active so the display command cannot find it.
        for result in info_results.contacted.values():
            assert result.get("failed") is True
            assert result.get("changed") is False
            assert result.get("rc") == 1
            assert result.get("tasks") is None
            assert f"{job_name} NOT FOUND" in result.get("stderr")
            assert result.get("msg") == "Started task could not be found."
        
    finally:
        # Remove USS temp directory containing the USS file
        hosts.all.file(path=temp_path, state="absent")
        # Remove the temp sequential data set
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        # Remove the member from the PDS
        hosts.all.shell(
            cmd="mrm '{0}({1})'".format(PROC_PDS, member_name)
        )

# Get info for started task without specifying parameters (failure case)
def test_get_started_task_info_without_parameters(ansible_zos_module):
    hosts = ansible_zos_module

    info_results = hosts.all.zos_started_task_info(
        verbose=True
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") is None
        assert result.get("tasks") is None
        assert result.get("stderr") == ""
        assert result.get("msg") == "Either 'job_name' or 'task_id' is mandatory to display started task details."

# Get info for started task using identifier (failure case)
def test_get_started_task_info_using_identifier_only(ansible_zos_module):
    hosts = ansible_zos_module
    identifier_name = "ICSF"

    info_results = hosts.all.zos_started_task_info(
        identifier_name=identifier_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") is None
        assert result.get("tasks") is None
        assert result.get("msg") == "missing parameter(s) required by 'identifier_name': job_name"

# Get info for started task using invalid wildcard in identifier (failure case)
def test_get_started_task_info_using_identifier_name_with_invalid_wildcard(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "JES2"
    identifier_name = "*ES2"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name,
        identifier_name=identifier_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") is None
        assert result.get("tasks") is None
        assert f'Invalid argument "{identifier_name}" for type "identifier_name".' in result.get("stderr")
        assert result.get("msg") == f"Parameter verification failed."

# Get info for started task using identifier that does not match with job name (failure case)
def test_get_started_task_info_using_invalid_job_name_and_identifier_name_pairing(ansible_zos_module):
    hosts = ansible_zos_module
    job_name = "JES2"
    identifier_name = "ICSF"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name,
        identifier_name=identifier_name
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") == 1
        assert result.get("tasks") is None
        assert f"{job_name}.{identifier_name} NOT FOUND" in result.get("stderr")
        assert result.get("msg") == f"Started task could not be found."

# Get info for started task with job_name and task_id (failure case)
def test_get_started_task_info_using_job_name_and_task_id(ansible_zos_module):
    hosts = ansible_zos_module
    task_id = "STC00010"
    job_name = "ICSF"

    info_results = hosts.all.zos_started_task_info(
        job_name=job_name,
        task_id=task_id
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") is None
        assert result.get("tasks") is None
        assert result.get("msg") == "parameters are mutually exclusive: job_name|task_id"

# Get info for started task with task_id and identifier_name (failure case)
def test_get_started_task_info_using_task_id_and_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    task_id = "STC00010"
    identifier_name = "ICSF"

    info_results = hosts.all.zos_started_task_info(
        identifier_name=identifier_name,
        task_id=task_id
    )

    for result in info_results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert result.get("rc") is None
        assert result.get("tasks") is None
        assert result.get("msg") == "parameters are mutually exclusive: identifier_name|task_id"
