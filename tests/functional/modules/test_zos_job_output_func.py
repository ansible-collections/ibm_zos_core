# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2025
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

from shellescape import quote


JCL_FILE_CONTENTS = """//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD
/*
//SYSUT2   DD SYSOUT=*
//
"""

TEMP_PATH = "/tmp/jcl"

def test_zos_job_output_no_job_id(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_id="")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("msg") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_invalid_job_id(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_id="INVALID")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("msg") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_no_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_name="")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("msg") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_invalid_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_name="INVALID")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg", False) is False
        assert result.get("jobs") is not None

        job = result.get("jobs")[0]
        assert job.get("job_id") is not None
        assert job.get("job_name") is not None
        assert job.get("subsystem") is None
        assert job.get("system") is None
        assert job.get("owner") is not None
        assert job.get("cpu_time") is None
        assert job.get("execution_node") is None
        assert job.get("origin_node") is None
        assert job.get("content_type") is None
        assert job.get("creation_date") is None
        assert job.get("creation_time") is None
        assert job.get("execution_time") is None
        assert job.get("job_class") is None
        assert job.get("svc_class") is None
        assert job.get("priority") is None
        assert job.get("asid") is None
        assert job.get("queue_position") is None
        assert job.get("program_name") is None
        assert job.get("class") is None
        assert job.get("steps") is not None
        assert job.get("dds") is not None

        rc = job.get("ret_code")
        assert rc.get("msg") is None
        assert rc.get("code") is None
        assert rc.get("msg_code") is None
        assert rc.get("msg_txt") is not None

        dds = job.get("dds")[0]
        assert dds.get("dd_name") == "unavailable"
        assert dds.get("record_count") == 0
        assert dds.get("id") is None
        assert dds.get("stepname") is None
        assert dds.get("procstep") is None
        assert dds.get("byte_count") == 0
        assert dds.get("content") is None


def test_zos_job_output_no_owner(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(owner="")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg") is not None
        assert result.get("stderr") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_invalid_owner(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(owner="INVALID")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("msg") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_reject(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output()
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg") is not None
        assert result.get("stderr") is not None
        assert result.get("failed") is True
        assert result.get("jobs") is None


def test_zos_job_output_job_exists(ansible_zos_module):
    try:
        # adding verification that at least 1 step was returned
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCL_FILE_CONTENTS)} > {TEMP_PATH}/SAMPLE"
        )

        jobs = hosts.all.zos_job_submit(
            src=f"{TEMP_PATH}/SAMPLE", remote_src=True, volume=None
        )
        for job in jobs.contacted.values():
            assert job.get("changed") is True
            assert job.get("msg", False) is False
            assert job.get("jobs") is not None

            job_ = job.get("jobs")[0]
            assert job_.get("job_id") is not None
            submitted_job_id = job_.get("job_id")
            assert job_.get("job_name") is not None
            assert job_.get("content_type") is not None
            assert job_.get("duration") is not None
            assert job_.get("execution_time") is not None
            assert job_.get("job_class") is not None
            assert job_.get("svc_class") is None
            assert job_.get("priority") is not None
            assert job_.get("asid") is not None
            assert job_.get("creation_date") is not None
            assert job_.get("creation_time") is not None
            assert job_.get("queue_position") is not None
            assert job_.get("program_name") is not None

            dds = job_.get("dds")[0]
            assert dds.get("dd_name") is not None
            assert dds.get("record_count") != 0
            assert dds.get("id") is not None
            assert dds.get("stepname") is not None
            assert dds.get("procstep") is not None
            assert dds.get("byte_count") != 0
            assert dds.get("content") is not None

            step = job_.get("steps")[0]
            assert step.get("step_name") is not None
            assert step.get("step_cc") is not None

            rc = job_.get("ret_code")
            assert rc.get("msg") == "CC"
            assert rc.get("code") == 0
            assert rc.get("msg_code") == "0000"
            assert rc.get("msg_txt") == "CC"

        results = hosts.all.zos_job_output(job_id=submitted_job_id)  # was SAMPLE?!
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("jobs") is not None

            job = result.get("jobs")[0]
            assert job.get("job_id") == submitted_job_id
            assert job.get("job_name") is not None
            assert job.get("subsystem") is not None
            assert job.get("system") is not None
            assert job.get("owner") is not None
            assert job.get("cpu_time") is not None
            assert job.get("execution_node") is not None
            assert job.get("origin_node") is not None
            assert job.get("content_type") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("execution_time") is not None
            assert job.get("job_class") is not None
            assert job.get("svc_class") is None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("queue_position") is not None
            assert job.get("program_name") is not None
            assert job.get("class") is not None
            assert job.get("steps") is not None
            assert job.get("dds") is not None

            step = job.get("steps")[0]
            assert step.get("step_name") is not None
            assert step.get("step_cc") is not None

            rc = job.get("ret_code")
            assert rc.get("msg") == "CC"
            assert rc.get("code") == 0
            assert rc.get("msg_code") == "0000"
            assert rc.get("msg_txt") == "CC"

            dds = job.get("dds")[0]
            assert dds.get("dd_name") is not None
            assert dds.get("record_count") != 0
            assert dds.get("id") is not None
            assert dds.get("stepname") is not None
            assert dds.get("procstep") is not None
            assert dds.get("byte_count") != 0
            assert dds.get("content") is not None

    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")


def test_zos_job_output_job_exists_with_filtered_ddname(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCL_FILE_CONTENTS)} > {TEMP_PATH}/SAMPLE"
        )
        result = hosts.all.zos_job_submit(
            src=f"{TEMP_PATH}/SAMPLE", remote_src=True, volume=None
        )
        hosts.all.file(path=TEMP_PATH, state="absent")
        dd_name = "JESMSGLG"
        results = hosts.all.zos_job_output(job_name="HELLO", ddname=dd_name)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("jobs") is not None

            job = result.get("jobs")[0]
            assert job.get("job_id") is not None
            assert job.get("job_name") is not None
            assert job.get("subsystem") is not None
            assert job.get("system") is not None
            assert job.get("owner") is not None
            assert job.get("cpu_time") is not None
            assert job.get("execution_node") is not None
            assert job.get("origin_node") is not None
            assert job.get("content_type") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("execution_time") is not None
            assert job.get("job_class") is not None
            assert job.get("svc_class") is None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("queue_position") is not None
            assert job.get("program_name") is not None
            assert job.get("class") is not None
            assert job.get("steps") is not None
            assert job.get("dds") is not None
            assert len(job.get("dds")) == 1

            rc = job.get("ret_code")
            assert rc.get("msg") == "CC"
            assert rc.get("code") == 0
            assert rc.get("msg_code") == "0000"
            assert rc.get("msg_txt") == "CC"

            dds = job.get("dds")[0]
            assert dds.get("dd_name") == dd_name
            assert dds.get("record_count") != 0
            assert dds.get("id") is not None
            assert dds.get("stepname") is not None
            assert dds.get("procstep") is not None
            assert dds.get("byte_count") != 0
            assert dds.get("content") is not None

    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")


def test_zos_job_submit_job_id_and_owner_included(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_id="STC00*", owner="MASTER")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg", False) is False
        assert result.get("jobs") is not None

        job = result.get("jobs")[0]
        assert job.get("job_id") is not None
        assert job.get("job_name") is not None
        assert job.get("subsystem") is None
        assert job.get("system") is None
        assert job.get("owner") is not None
        assert job.get("cpu_time") is None
        assert job.get("execution_node") is None
        assert job.get("origin_node") is None
        assert job.get("content_type") is None
        assert job.get("creation_date") is None
        assert job.get("creation_time") is None
        assert job.get("execution_time") is None
        assert job.get("job_class") is None
        assert job.get("svc_class") is None
        assert job.get("priority") is None
        assert job.get("asid") is None
        assert job.get("queue_position") is None
        assert job.get("program_name") is None
        assert job.get("class") is None
        assert job.get("steps") is not None
        assert job.get("dds") is not None

        rc = job.get("ret_code")
        assert rc.get("msg") is None
        assert rc.get("code") is None
        assert rc.get("msg_code") is None
        assert rc.get("msg_txt") is not None

        dds = job.get("dds")[0]
        assert dds.get("dd_name") == "unavailable"
        assert dds.get("record_count") == 0
        assert dds.get("id") is None
        assert dds.get("stepname") is None
        assert dds.get("procstep") is None
        assert dds.get("byte_count") == 0
        assert dds.get("content") is None
