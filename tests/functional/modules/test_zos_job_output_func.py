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
        assert result.get("jobs") is None


def test_zos_job_output_invalid_job_id(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_id="INVALID")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("failed") is True


def test_zos_job_output_no_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_name="")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs") is None


def test_zos_job_output_invalid_job_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_name="INVALID")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs")[0].get("ret_code").get("msg_txt") is not None


def test_zos_job_output_no_owner(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(owner="")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg") is not None


def test_zos_job_output_invalid_owner(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(owner="INVALID")
    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("stderr") is not None


def test_zos_job_output_reject(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output()
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg") is not None


def test_zos_job_output_job_exists(ansible_zos_module):
    try:
        # adding verification that at least 1 step was returned
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCL_FILE_CONTENTS)} > {TEMP_PATH}/SAMPLE"
        )

        jobs = hosts.all.zos_job_submit(
            src=f"{TEMP_PATH}/SAMPLE", location="uss", volume=None
        )
        for job in jobs.contacted.values():
            print(job)
            assert job.get("jobs") is not None

        for job in jobs.contacted.values():
            submitted_job_id = job.get("jobs")[0].get("job_id")
            assert submitted_job_id is not None

        results = hosts.all.zos_job_output(job_id=submitted_job_id)  # was SAMPLE?!
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("jobs") is not None
            assert result.get("jobs")[0].get("ret_code").get("steps") is not None
            assert result.get("jobs")[0].get("ret_code").get("steps")[0].get("step_name") == "STEP0001"
            assert result.get("jobs")[0].get("content_type") == "JOB"
            assert result.get("jobs")[0].get("execution_time") is not None
            assert "system" in result.get("jobs")[0]
            assert "subsystem" in result.get("jobs")[0]
            assert "cpu_time" in result.get("jobs")[0]
            assert "execution_node" in result.get("jobs")[0]
            assert "origin_node" in result.get("jobs")[0]
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
            src=f"{TEMP_PATH}/SAMPLE", location="uss", volume=None
        )
        hosts.all.file(path=TEMP_PATH, state="absent")
        dd_name = "JESMSGLG"
        results = hosts.all.zos_job_output(job_name="HELLO", ddname=dd_name)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("jobs") is not None
            for job in result.get("jobs"):
                assert len(job.get("ddnames")) == 1
                assert job.get("ddnames")[0].get("ddname") == dd_name
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")


def test_zos_job_submit_job_id_and_owner_included(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output(job_id="STC00*", owner="MASTER")
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_txt") is not None
