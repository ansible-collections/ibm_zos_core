# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2024
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

import ansible.constants
import ansible.errors
import ansible.utils
import pytest
from shellescape import quote

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name

def get_job_id(hosts, len_id=9):
    """
    Returns a job id that is on the system by searching all jobs on system.

    Parameters
    ----------
    hosts : obj
        Connection to host machine
    len_id : int
        Size for search and job_id of specific or lower size
    """
    results = hosts.all.shell(cmd="jls")
    for result in results.contacted.values():
        all_jobs = result.get("stdout_lines")
    for job_n_info in all_jobs:
        job = job_n_info.split()
        if len(job[2]) <= len_id:
            return job[2]

# Make sure job list * returns something
def test_zos_job_query_func(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_query(job_name="*", owner="*")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs") is not None

JCLQ_FILE_CONTENTS = """//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
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

TEMP_PATH = "/tmp/"

# test to show multi wildcard in Job_id query won't crash the search
def test_zos_job_id_query_multi_wildcards_func(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        jdata_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TEMP_PATH)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.zos_data_set(
            name=jdata_set_name, state="present", type="pds", replace=True
        )
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{jdata_set_name}(SAMPLE)'\""
        )
        results = hosts.all.zos_job_submit(
            src=f"{jdata_set_name}(SAMPLE)", location="data_set", wait_time_s=10
        )
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("jobs")[0].get("execution_time") is not None

            fulljobid = result.get("jobs")[0].get("job_id")
            jobmask = fulljobid[0:3] + '*' + fulljobid[5:6] + '*'
            qresults = hosts.all.zos_job_query(job_id=jobmask)
            for qresult in qresults.contacted.values():
                assert qresult.get("jobs") is not None
                assert qresult.get("jobs")[0].get("execution_time") is not None
                assert qresult.get("jobs")[0].get("system") is not None
                assert qresult.get("jobs")[0].get("subsystem") is not None
                assert "cpu_time" in result.get("jobs")[0]
                assert "execution_node" in result.get("jobs")[0]
                assert "origin_node" in result.get("jobs")[0]

    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.zos_data_set(name=jdata_set_name, state="absent")


# test to show multi wildcard in Job_name query won't crash the search
def test_zos_job_name_query_multi_wildcards_func(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        ndata_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TEMP_PATH)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.zos_data_set(
            name=ndata_set_name, state="present", type="pds", replace=True
        )
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{ndata_set_name}(SAMPLE)'\""
        )
        results = hosts.all.zos_job_submit(
            src=f"{ndata_set_name}(SAMPLE)", location="data_set", wait_time_s=10
        )
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("jobs")[0].get("execution_time") is not None
            assert result.get("jobs")[0].get("system") is not None
            assert result.get("jobs")[0].get("subsystem") is not None

            jobname = "HE*L*"
            qresults = hosts.all.zos_job_query(job_name=jobname, owner="*")
            for qresult in qresults.contacted.values():
                assert qresult.get("jobs") is not None
                assert qresult.get("jobs")[0].get("execution_time") is not None

    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.zos_data_set(name=ndata_set_name, state="absent")


def test_zos_job_id_query_short_ids_func(ansible_zos_module):
    hosts = ansible_zos_module
    len_id = 9
    job_id = get_job_id(hosts, len_id)
    qresults = hosts.all.zos_job_query(job_id=job_id)
    for qresult in qresults.contacted.values():
        assert qresult.get("jobs") is not None


def test_zos_job_id_query_short_ids_with_wilcard_func(ansible_zos_module):
    hosts = ansible_zos_module
    len_id = 9
    job_id = get_job_id(hosts, len_id)
    job_id = job_id[0:4] + '*'
    qresults = hosts.all.zos_job_query(job_id=job_id)

    # Assuming we'll mostly deal with started tasks or normal jobs.
    if "STC" in job_id:
        content_type = "STC"
    else:
        content_type = "JOB"

    for qresult in qresults.contacted.values():
        assert qresult.get("jobs") is not None
        assert qresult.get("jobs")[0].get("content_type") == content_type
