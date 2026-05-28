# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2026
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

import tempfile
import ansible.constants
import ansible.errors
import ansible.utils
import pytest
from shellescape import quote

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name
from ibm_zos_core.tests.helpers.users import ManagedUser, ManagedUserType

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

def get_job(hosts):
    """
    Returns job that is on the system by searching all jobs on system.

    Parameters
    ----------
    hosts : obj
        Connection to host machine
    """
    results = hosts.all.shell(cmd="jls")
    for result in results.contacted.values():
        all_jobs = result.get("stdout_lines")
    for job_n_info in all_jobs:
        job = job_n_info.split()
        return job

# Make sure job list * returns something
def test_zos_job_query_func(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_job_query(job_name="*", owner="*")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("jobs") is not None
        assert result.get("msg", False) is False

        job = result.get("jobs")[0]
        assert job.get("job_name") is not None
        assert job.get("owner") is not None
        assert job.get("job_id") is not None
        assert job.get("content_type") is not None
        assert job.get("system") is not None
        assert job.get("subsystem") is not None
        assert job.get("origin_node") is not None
        assert job.get("execution_node") is not None
        assert job.get("cpu_time") is not None
        assert job.get("job_class") is not None
        assert job.get("priority") is not None
        assert job.get("asid") is not None
        assert job.get("creation_date") is not None
        assert job.get("creation_time") is not None
        assert job.get("program_name") is not None
        assert job.get("execution_time") is not None
        assert job.get("svc_class") is None
        assert job.get("steps") is not None

        rc = job.get("ret_code")
        assert rc.get("msg") is not None
        assert rc.get("code") is not None
        assert rc.get("msg_code") is not None
        assert rc.get("msg_txt") is not None

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
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TEMP_PATH)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.shell(cmd=f"dtouch -tpds '{data_set_name}'")
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{data_set_name}(SAMPLE)'\""
        )
        results = hosts.all.zos_job_submit(
            src=f"{data_set_name}(SAMPLE)", remote_src=True, wait_time=10
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("jobs") is not None

            job = result.get("jobs")[0]
            assert job.get("job_id") is not None
            assert job.get("job_name") is not None
            assert job.get("content_type") is not None
            assert job.get("duration") is not None
            assert job.get("execution_time") is not None
            assert job.get("job_class") is not None
            assert job.get("svc_class") is None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("queue_position") is not None
            assert job.get("program_name") is not None

            dds = job.get("dds")[0]
            assert dds.get("dd_name") is not None
            assert dds.get("record_count") != 0
            assert dds.get("id") is not None
            assert dds.get("stepname") is not None
            assert dds.get("procstep") is not None
            assert dds.get("byte_count") != 0
            assert dds.get("content") is not None

            step = job.get("steps")[0]
            assert step.get("step_name") is not None
            assert step.get("step_cc") is not None

            rc = job.get("ret_code")
            assert rc.get("msg") == "CC"
            assert rc.get("code") == 0
            assert rc.get("msg_code") == "0000"
            assert rc.get("msg_txt") == "CC"

            fulljobid = job.get("job_id")
            jobmask = fulljobid[0:3] + '*' + fulljobid[5:6] + '*'
            qresults = hosts.all.zos_job_query(job_id=jobmask)
            for qresult in qresults.contacted.values():
                assert qresult.get("changed") is True
                assert qresult.get("jobs") is not None
                assert qresult.get("msg", False) is False

                job = qresult.get("jobs")[0]
                assert job.get("job_name") is not None
                assert job.get("owner") is not None
                assert job.get("job_id") == fulljobid
                assert job.get("content_type") is not None
                assert job.get("system") is not None
                assert job.get("subsystem") is not None
                assert job.get("origin_node") is not None
                assert job.get("execution_node") is not None
                assert job.get("cpu_time") is not None
                assert job.get("job_class") is not None
                assert job.get("priority") is not None
                assert job.get("asid") is not None
                assert job.get("creation_date") is not None
                assert job.get("creation_time") is not None
                assert job.get("program_name") is not None
                assert job.get("execution_time") is not None
                assert job.get("svc_class") is None
                assert job.get("steps") is not None

                rc = job.get("ret_code")
                assert rc.get("msg") is not None
                assert rc.get("msg_code") == "0000"
                assert rc.get("code") == 0
                assert rc.get("msg_txt") == "CC"

    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(cmd=f"drm '{data_set_name}'")


# test to show multi wildcard in Job_name query won't crash the search
def test_zos_job_name_query_multi_wildcards_func(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TEMP_PATH)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.shell(cmd=f"dtouch -tpds '{data_set_name}'")
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{data_set_name}(SAMPLE)'\""
        )
        results = hosts.all.zos_job_submit(
            src=f"{data_set_name}(SAMPLE)", remote_src=True, wait_time=10
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("jobs") is not None

            job = result.get("jobs")[0]
            assert job.get("job_id") is not None
            assert job.get("job_name") is not None
            assert job.get("content_type") is not None
            assert job.get("duration") is not None
            assert job.get("execution_time") is not None
            assert job.get("job_class") is not None
            assert job.get("svc_class") is None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("queue_position") is not None
            assert job.get("program_name") is not None

            dds = job.get("dds")[0]
            assert dds.get("dd_name") is not None
            assert dds.get("record_count") != 0
            assert dds.get("id") is not None
            assert dds.get("stepname") is not None
            assert dds.get("procstep") is not None
            assert dds.get("byte_count") != 0
            assert dds.get("content") is not None

            step = job.get("steps")[0]
            assert step.get("step_name") is not None
            assert step.get("step_cc") is not None

            rc = job.get("ret_code")
            assert rc.get("msg") == "CC"
            assert rc.get("code") == 0
            assert rc.get("msg_code") == "0000"
            assert rc.get("msg_txt") == "CC"

            jobname = "HE*L*"
            qresults = hosts.all.zos_job_query(job_name=jobname, owner="*")
            for qresult in qresults.contacted.values():
                assert qresult.get("changed") is True
                assert qresult.get("jobs") is not None
                assert qresult.get("msg", False) is False

                job = qresult.get("jobs")[0]
                assert job.get("job_name") == "HELLO"
                assert job.get("owner") is not None
                assert job.get("job_id") is not None
                assert job.get("content_type") is not None
                assert job.get("system") is not None
                assert job.get("subsystem") is not None
                assert job.get("origin_node") is not None
                assert job.get("execution_node") is not None
                assert job.get("cpu_time") is not None
                assert job.get("job_class") is not None
                assert job.get("priority") is not None
                assert job.get("asid") is not None
                assert job.get("creation_date") is not None
                assert job.get("creation_time") is not None
                assert job.get("program_name") is not None
                assert job.get("execution_time") is not None
                assert job.get("svc_class") is None
                assert job.get("steps") is not None

                rc = job.get("ret_code")
                assert rc.get("msg") is not None
                assert rc.get("msg_code") == "0000"
                assert rc.get("code") == 0
                assert rc.get("msg_txt") == "CC"
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(cmd=f"drm '{data_set_name}'")


def test_zos_job_id_query_short_ids_func(ansible_zos_module):
    hosts = ansible_zos_module
    len_id = 9
    job_id = get_job_id(hosts, len_id)
    qresults = hosts.all.zos_job_query(job_id=job_id)
    for qresult in qresults.contacted.values():
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        job = qresult.get("jobs")[0]
        assert job.get("job_name") is not None
        assert job.get("owner") is not None
        assert job.get("job_id") is not None
        assert job.get("content_type") is not None
        assert job.get("system") is not None
        assert job.get("subsystem") is not None
        assert job.get("origin_node") is not None
        assert job.get("execution_node") is not None
        assert job.get("cpu_time") is not None
        assert job.get("job_class") is not None
        assert job.get("priority") is not None
        assert job.get("asid") is not None
        assert job.get("creation_date") is not None
        assert job.get("creation_time") is not None
        assert job.get("program_name") is not None
        assert job.get("svc_class") is None
        assert job.get("steps") is not None

        rc = job.get("ret_code")
        assert rc.get("msg") is not None
        assert rc.get("msg_code") == "0000"
        assert rc.get("code") == 0
        assert rc.get("msg_txt") == "CC"


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
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        job = qresult.get("jobs")[0]
        assert job.get("job_name") is not None
        assert job.get("owner") is not None
        assert job.get("job_id") is not None
        assert job.get("content_type") == content_type
        assert job.get("system") is not None
        assert job.get("subsystem") is not None
        assert job.get("origin_node") is not None
        assert job.get("execution_node") is not None
        assert job.get("cpu_time") is not None
        assert job.get("job_class") is not None
        assert job.get("priority") is not None
        assert job.get("asid") is not None
        assert job.get("creation_date") is not None
        assert job.get("creation_time") is not None
        assert job.get("program_name") is not None
        assert job.get("svc_class") is None
        assert job.get("steps") is not None

        rc = job.get("ret_code")
        assert rc.get("msg") is not None
        assert rc.get("msg_code") == "0000"
        assert rc.get("code") == 0


# zos_job_query should not return jobs user is not authorized to view when defaults are specified
def test_zos_job_query_return_only_authorized_jobs(ansible_zos_module, z_python_interpreter):
    hosts = ansible_zos_module
    managed_user = None
    data_set_name = None
    temp_path = None

    try:
        # Submit a job as the original user (with full permissions)
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TEMP_PATH)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.shell(cmd=f"dtouch -tpds '{data_set_name}'")
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{data_set_name}(SAMPLE)'\""
        )
        results = hosts.all.zos_job_submit(
            src=f"{data_set_name}(SAMPLE)", remote_src=True, wait_time=10
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("jobs") is not None

            job = result.get("jobs")[0]
            assert job.get("job_id") is not None
            assert job.get("job_name") is not None

        # Initialize the managed user with limited job viewing permissions
        managed_user = ManagedUser.from_fixture(ansible_zos_module, z_python_interpreter)

        # Create Ansible temp directory with permissions for managed user
        ansible_tmp_dir = "/tmp/ibmz/ansible"
        hosts.all.shell(cmd=f"mkdir -p {ansible_tmp_dir}")
        hosts.all.shell(cmd=f"chmod 777 {ansible_tmp_dir}")

        # Execute the test with the managed user
        managed_user.execute_managed_user_test(
            managed_user_test_case="managed_user_test_query_unauthorized_jobs",
            debug=False,
            verbose=False,
            managed_user_type=ManagedUserType.ZOS_LIMITED_JOB_VIEW
        )

    finally:
        if managed_user:
            managed_user.delete_managed_user()
        if temp_path:
            hosts.all.file(path=temp_path, state="absent")
        if data_set_name:
            hosts.all.shell(cmd=f"drm '{data_set_name}'")
        if ansible_tmp_dir:
            hosts.all.file(path=ansible_tmp_dir, state="absent")


def managed_user_test_query_unauthorized_jobs(ansible_zos_module):
    hosts = ansible_zos_module
    
    # Get the current user from the fixture options (set by ManagedUser class)
    current_user = hosts["options"]["user"]
    assert current_user is not None and current_user != ""

    data_set_name = get_tmp_ds_name()
    temp_path = get_random_file_name(dir=TEMP_PATH)

    try:
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.shell(cmd=f"dtouch -tpds '{data_set_name}'")
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{data_set_name}(SAMPLE)'\""
        )
        
        # Submit job as the managed user
        submit_results = hosts.all.zos_job_submit(
            src=f"{data_set_name}(SAMPLE)", remote_src=True, wait_time=10
        )
        
        MANAGED_USER_JOB_NAME = "HELLO"
        managed_user_job_id = None
        for result in submit_results.contacted.values():
            # Verify job submission succeeded
            assert result.get("changed") is True
            assert result.get("jobs") is not None
            
            job = result.get("jobs")[0]
            managed_user_job_id = job.get("job_id")
            assert managed_user_job_id is not None
            assert job.get("job_name") == MANAGED_USER_JOB_NAME 
            
            rc = job.get("ret_code")
            assert rc.get("code") == 0
            
        # Test owner and job_id defaults - job query should only return job of managed user
        # Job submitted with the same name by a different user should not appear
        job_name_query_results = hosts.all.zos_job_query(job_name=MANAGED_USER_JOB_NAME)

        for result in job_name_query_results.contacted.values():
            assert result.get("changed") is True
            jobs = result.get("jobs")
            assert jobs is not None and len(jobs) > 0
            
            for job in jobs:
                assert job.get("owner") == current_user, \
                    f"Retrieved job owner mismatch: expected {current_user}"
                assert job.get("job_id") == managed_user_job_id

    finally:
        if temp_path:
            hosts.all.file(path=temp_path, state="absent")
        if data_set_name:
            hosts.all.shell(cmd=f"drm '{data_set_name}'")


def test_zos_job_query_no_ceedump_created(ansible_zos_module, z_python_interpreter):
    hosts = ansible_zos_module
    managed_user = None

    try:
        # Initialize the managed user with limited job viewing permissions
        managed_user = ManagedUser.from_fixture(ansible_zos_module, z_python_interpreter)

        # Create Ansible temp directory with permissions for managed user
        ansible_tmp_dir = "/tmp/ibmz/ansible"
        hosts.all.shell(cmd=f"mkdir -p {ansible_tmp_dir}")
        hosts.all.shell(cmd=f"chmod 777 {ansible_tmp_dir}")

        # Execute the test with the managed user
        managed_user.execute_managed_user_test(
            managed_user_test_case="managed_user_test_query_ceedump",
            debug=False,
            verbose=False,
            managed_user_type=ManagedUserType.ZOS_LIMITED_JOB_VIEW
        )
    finally:
        if managed_user:
            managed_user.delete_managed_user()


def managed_user_test_query_ceedump(ansible_zos_module):
    hosts = ansible_zos_module
    
    # Get the current user from the fixture options (set by ManagedUser class)
    current_user = hosts["options"]["user"]
    assert current_user is not None and current_user != ""

    data_set_name = get_tmp_ds_name()
    temp_path = get_random_file_name(dir=TEMP_PATH)

    try:
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(JCLQ_FILE_CONTENTS)} > {temp_path}/SAMPLE"
        )
        hosts.all.shell(cmd=f"dtouch -tpds '{data_set_name}'")
        hosts.all.shell(
            cmd=f"cp {temp_path}/SAMPLE \"//'{data_set_name}(SAMPLE)'\""
        )
        
        # Submit job as the managed user
        submit_results = hosts.all.zos_job_submit(
            src=f"{data_set_name}(SAMPLE)", remote_src=True, wait_time=10
        )
        
        MANAGED_USER_JOB_NAME = "HELLO"
        managed_user_job_id = None
        for result in submit_results.contacted.values():
            # Verify job submission succeeded
            assert result.get("changed") is True
            assert result.get("jobs") is not None
            
            job = result.get("jobs")[0]
            managed_user_job_id = job.get("job_id")
            assert managed_user_job_id is not None
            assert job.get("job_name") == MANAGED_USER_JOB_NAME 
            
            rc = job.get("ret_code")
            assert rc.get("code") == 0
            
        job_name_query_results = hosts.all.zos_job_query(job_name="H*", owner=current_user)

        for result in job_name_query_results.contacted.values():
            assert result.get("changed") is True
            jobs = result.get("jobs")
            assert jobs is not None and len(jobs) > 0
            
            for job in jobs:
                assert job.get("owner") == current_user, \
                    f"Retrieved job owner mismatch: expected {current_user}"
                assert job.get("job_id") == managed_user_job_id

    finally:
        if temp_path:
            hosts.all.file(path=temp_path, state="absent")
        if data_set_name:
            hosts.all.shell(cmd=f"drm '{data_set_name}'")


# test to show job_id="*" and job_id=None has the same results if job_name and owner are specified
def test_zos_job_query_null_vs_wildcard_job_id(ansible_zos_module):
    hosts = ansible_zos_module
    job = get_job(hosts)
    job_owner = job[0]
    job_name = job[1]

    assert job_owner is not None
    assert job_name is not None

    qresults_null = hosts.all.zos_job_query(job_id=None, job_name=job_name, owner=job_owner)
    
    qresults_null_jobs_len = 0
    for qresult in qresults_null.contacted.values():
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        for job in qresult.get("jobs"):
            qresults_null_jobs_len += 1

    qresults_all = hosts.all.zos_job_query(job_id="*", job_name=job_name, owner=job_owner)

    qresults_all_jobs_len = 0
    for qresult in qresults_all.contacted.values():
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        for job in qresult.get("jobs"):
            qresults_all_jobs_len += 1

    # Assert length of results for both queries is the same
    qresults_null_jobs_len == qresults_all_jobs_len


def test_zos_job_query_with_null_job_owner(ansible_zos_module):
    hosts = ansible_zos_module
    len_id = 9
    job = get_job(hosts)
    job_name = job[1]
    job_id = job[2]

    assert job_name is not None
    assert job_id is not None

    qresults_null = hosts.all.zos_job_query(job_id=job_id, job_name=job_name, owner=None)
    
    for qresult in qresults_null.contacted.values():
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        # Verify all jobs match either job_id or job_name parameter
        for job in qresult.get("jobs"):
            assert job.get("job_name") == job_name
            assert job.get("owner") is not None
            assert job.get("job_id") == job_id
            assert job.get("content_type") is not None
            assert job.get("system") is not None
            assert job.get("subsystem") is not None
            assert job.get("origin_node") is not None
            assert job.get("execution_node") is not None
            assert job.get("cpu_time") is not None
            assert job.get("job_class") is not None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("program_name") is not None
            assert job.get("svc_class") is None
            assert job.get("steps") is not None

            rc = job.get("ret_code")
            assert rc.get("msg") is not None
            assert rc.get("msg_code") == "0000"
            assert rc.get("code") == 0


def test_zos_job_query_with_null_job_id(ansible_zos_module):
    hosts = ansible_zos_module
    len_id = 9
    job = get_job(hosts)
    job_owner = job[0]
    job_name = job[1]

    assert job_owner is not None
    assert job_name is not None

    qresults_null = hosts.all.zos_job_query(job_id=None, job_name=job_name, owner=job_owner)
    
    for qresult in qresults_null.contacted.values():
        assert qresult.get("changed") is True
        assert qresult.get("jobs") is not None
        assert qresult.get("msg", False) is False

        # Verify all jobs match either job_name or job_owner parameter
        for job in qresult.get("jobs"):
            assert job.get("job_name") == job_name
            assert job.get("owner") == job_owner
            assert job.get("job_id") is not None
            assert job.get("content_type") is not None
            assert job.get("system") is not None
            assert job.get("subsystem") is not None
            assert job.get("origin_node") is not None
            assert job.get("execution_node") is not None
            assert job.get("cpu_time") is not None
            assert job.get("job_class") is not None
            assert job.get("priority") is not None
            assert job.get("asid") is not None
            assert job.get("creation_date") is not None
            assert job.get("creation_time") is not None
            assert job.get("program_name") is not None
            assert job.get("svc_class") is None
            assert job.get("steps") is not None

            rc = job.get("ret_code")
            assert rc.get("msg") is not None
            assert rc.get("msg_code") == "0000"
            assert rc.get("code") == 0