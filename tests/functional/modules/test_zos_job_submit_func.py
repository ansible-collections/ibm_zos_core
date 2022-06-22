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

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest
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
JCL_FILE_CONTENTS_R = """//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=* \r
//SYSUT1   DD * \r
HELLO, WORLD
/*
//SYSUT2   DD SYSOUT=*
//
"""
JCL_FILE_CONTENTS_BAD = """//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*!!
//SYSUT1   DD *
HELLO, WORLD
/*
//SYSUT2   DD SYSOUT=*
//
"""


TEMP_PATH = "/tmp/ansible/jcl"
DATA_SET_NAME = "imstestl.ims1.test05"
DATA_SET_NAME_SPECIAL_CHARS = "imstestl.im@1.xxx05"


def test_job_submit_PDS(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(
        cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
    )
    hosts.all.zos_data_set(
        name=DATA_SET_NAME, state="present", type="pds", replace=True
    )
    hosts.all.shell(
        cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, DATA_SET_NAME)
    )
    results = hosts.all.zos_job_submit(
        src="{0}(SAMPLE)".format(DATA_SET_NAME), location="DATA_SET", wait=True
    )
    hosts.all.file(path=TEMP_PATH, state="absent")
    for result in results.contacted.values():
        print("\nTJSP.................\n")
        print(result)
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0
        assert result.get("changed") is True


def test_job_submit_PDS_special_characters(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(
        cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
    )
    hosts.all.zos_data_set(
        name=DATA_SET_NAME_SPECIAL_CHARS, state="present", type="pds", replace=True
    )
    hosts.all.shell(
        cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(
            TEMP_PATH, DATA_SET_NAME_SPECIAL_CHARS
        )
    )
    results = hosts.all.zos_job_submit(
        src="{0}(SAMPLE)".format(DATA_SET_NAME_SPECIAL_CHARS),
        location="DATA_SET",
        wait=True,
    )
    hosts.all.file(path=TEMP_PATH, state="absent")
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0
        assert result.get("changed") is True


def test_job_submit_USS(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(
        cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
    )
    results = hosts.all.zos_job_submit(
        src="{0}/SAMPLE".format(TEMP_PATH), location="USS", wait=True, volume=None
    )
    hosts.all.file(path=TEMP_PATH, state="absent")
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0
        assert result.get("changed") is True


def test_job_submit_LOCAL(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait=True)

    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0

        assert result.get("changed") is True


def test_job_submit_LOCAL_extraR(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_R)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait=True)

    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0

        assert result.get("changed") is True


def test_job_submit_LOCAL_BADJCL(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_BAD)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait=True)

    for result in results.contacted.values():

        assert result.get("changed") is False


# * currently don't have volume support from ZOAU python API, so this will not be reproduceable
# * in CI/CD testing environment (for now)
# def test_job_submit_PDS_volume(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_job_submit(src='BJMAXY.UNCATLOG.JCL(SAMPLE)', location="DATA_SET", wait=False, volume='P2SS01')
#     for result in results.contacted.values():
#         assert result.get('jobs')[0].get('ret_code').get('code') == '0000'
#         assert result.get('changed') is True


# * short run in some other environments would fail, so "normal" run currently has wait=True specified
# def test_job_submit_PDS_long(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_job_submit(src='BJMAXY.HILL3(LONGRUN)', location="DATA_SET", wait=True, volume=None)
#     for result in results.contacted.values():
#         assert result.get('jobs')[0].get('ret_code').get('code')== '0000'
#         assert result.get('changed') is True
