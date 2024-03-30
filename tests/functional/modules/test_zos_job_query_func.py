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
from pprint import pprint
from shellescape import quote
import tempfile

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

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

TEMP_PATH = "/tmp/jcl"

# test to show multi wildcard in Job_id query won't crash the search
def test_zos_job_id_query_multi_wildcards_func(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        JDATA_SET_NAME = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCLQ_FILE_CONTENTS), TEMP_PATH)
        )
        hosts.all.zos_data_set(
            name=JDATA_SET_NAME, state="present", type="PDS", replace=True
        )
        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, JDATA_SET_NAME)
        )
        results = hosts.all.zos_job_submit(
            src="{0}(SAMPLE)".format(JDATA_SET_NAME), location="DATA_SET", wait_time_s=10
        )
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0

            fulljobid = result.get("jobs")[0].get("job_id")
            jobmask = fulljobid[0:3] + '*' + fulljobid[5:6] + '*'
            qresults = hosts.all.zos_job_query(job_id=jobmask)
            for qresult in qresults.contacted.values():
                assert qresult.get("jobs") is not None

    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=JDATA_SET_NAME, state="absent")


# test to show multi wildcard in Job_name query won't crash the search
def test_zos_job_name_query_multi_wildcards_func(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        NDATA_SET_NAME = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCLQ_FILE_CONTENTS), TEMP_PATH)
        )
        hosts.all.zos_data_set(
            name=NDATA_SET_NAME, state="present", type="PDS", replace=True
        )
        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, NDATA_SET_NAME)
        )
        results = hosts.all.zos_job_submit(
            src="{0}(SAMPLE)".format(NDATA_SET_NAME), location="DATA_SET", wait_time_s=10
        )
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0

            jobname = "HE*L*"
            qresults = hosts.all.zos_job_query(job_name=jobname, owner="*")
            for qresult in qresults.contacted.values():
                assert qresult.get("jobs") is not None

    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=NDATA_SET_NAME, state="absent")


def test_zos_job_id_query_short_ids_func(ansible_zos_module):
    hosts = ansible_zos_module
    qresults = hosts.all.zos_job_query(job_id="STC00002")
    for qresult in qresults.contacted.values():
        assert qresult.get("jobs") is not None


def test_zos_job_id_query_short_ids_with_wilcard_func(ansible_zos_module):
    hosts = ansible_zos_module
    qresults = hosts.all.zos_job_query(job_id="STC00*")
    for qresult in qresults.contacted.values():
        assert qresult.get("jobs") is not None
