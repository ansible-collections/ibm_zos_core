# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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
import tempfile


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

TEMP_PATH = "/tmp/ansible/jcl"


# def test_zos_job_output_no_job_id(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_job_output(job_id="NO_JOBID")
#     for result in results.contacted.values():
#         print(result)
#         assert result.get("changed") is False
#         assert result.get("jobs") is not None


# def test_zos_job_output_no_job_name(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_job_output(job_name="NO_JOBNAME")
#     for result in results.contacted.values():
#         print(result)
#         assert result.get("changed") is False
#         assert result.get("jobs") is not None


# def test_zos_job_output_no_owner(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_job_output(owner="NO_OWNER")
#     for result in results.contacted.values():
#         print(result)
#         assert result.get("changed") is False
#         assert result.get("jobs") is not None


def test_zos_job_output_reject(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_output()
    for result in results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("msg") is not None


def test_zos_job_output_job_exists(ansible_zos_module):
    # adding verification that at least 1 step was returned
    hosts = ansible_zos_module
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(
        cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
    )
    hosts.all.zos_job_submit(
        src="{0}/SAMPLE".format(TEMP_PATH), location="USS", wait=True, volume=None
    )
    hosts.all.file(path=TEMP_PATH, state="absent")
    results = hosts.all.zos_job_output(job_name="HELLO")  # was SAMPLE?!
    for result in results.contacted.values():
        print("\nZJOJE..............")
        print(result)
        assert result.get("changed") is False
        assert result.get("jobs") is not None
        assert result.get("jobs")[0].get("ret_code").get("steps") is not None
        assert (
            result.get("jobs")[0].get("ret_code").get("steps")[0].get("step_name")
            == "STEP0001"
        )


def test_zos_job_output_job_exists_with_filtered_ddname(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(
        cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
    )
    hosts.all.zos_job_submit(
        src="{0}/SAMPLE".format(TEMP_PATH), location="USS", wait=True, volume=None
    )
    hosts.all.file(path=TEMP_PATH, state="absent")
    dd_name = "JESMSGLG"
    results = hosts.all.zos_job_output(job_name="HELLO", ddname=dd_name)
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs") is not None
        for job in result.get("jobs"):
            assert len(job.get("ddnames")) == 1
            print(job)
            assert job.get("ddnames")[0].get("ddname") == dd_name
