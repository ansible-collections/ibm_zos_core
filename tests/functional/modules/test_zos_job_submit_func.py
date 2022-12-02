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
import pytest
import re

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

JCL_FILE_CONTENTS_30_SEC = """//BPXSLEEP JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//USSCMD EXEC PGM=BPXBATCH
//STDERR  DD SYSOUT=*
//STDOUT  DD SYSOUT=*
//STDPARM DD *
SH ls -la /;
sleep 30;
/*
//
"""

JCL_FILE_CONTENTS_05_SEC = """//BPXSLEEP JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//USSCMD EXEC PGM=BPXBATCH
//STDERR  DD SYSOUT=*
//STDOUT  DD SYSOUT=*
//STDPARM DD *
SH ls -la /;
sleep 05;
/*
//
"""
# Should return a max RC of 8
JCL_FILE_CONTENTS_RC_8 = """//RCBADJCL JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//S1 EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN DD *
 DELETE THIS.DATASET.DOES.NOT.EXIST
/*
"""

TEMP_PATH = "/tmp/jcl"
DATA_SET_NAME = "imstestl.ims1.test05"
DATA_SET_NAME_SPECIAL_CHARS = "imstestl.im@1.xxx05"
DEFAULT_VOLUME = "000000"


def test_job_submit_PDS(ansible_zos_module):
    try:
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
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME, state="absent")


def test_job_submit_PDS_special_characters(ansible_zos_module):
    try:
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
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME_SPECIAL_CHARS, state="absent")


def test_job_submit_USS(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )
        results = hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_PATH), location="USS", wait=True, volume=None
        )
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")


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
        # Expecting: The job completion code (CC) was not in the job log....."
        assert result.get("changed") is False
        assert re.search(r'completion code', repr(result.get("msg")))


def test_job_submit_PDS_volume(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True, volumes=DEFAULT_VOLUME
        )

        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, DATA_SET_NAME)
        )

        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="uncataloged", type="pds"
        )

        results = hosts.all.zos_job_submit(src = DATA_SET_NAME+"(SAMPLE)", location = "DATA_SET", volume = DEFAULT_VOLUME)
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME, state="absent")


def test_job_submit_PDS_5_SEC_JOB_WAIT_15(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 15

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_05_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, DATA_SET_NAME)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src = DATA_SET_NAME + "(BPXSLEEP)",
                                           location = "DATA_SET", wait_time_s = wait_time_s)

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
            assert result.get('duration') <= wait_time_s
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME, state="absent")


def test_job_submit_PDS_30_SEC_JOB_WAIT_60(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 60

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_30_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, DATA_SET_NAME)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src = DATA_SET_NAME + "(BPXSLEEP)",
                                           location = "DATA_SET", wait_time_s = wait_time_s)

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
            assert result.get('duration') <= wait_time_s
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME, state="absent")


def test_job_submit_PDS_30_SEC_JOB_WAIT_10_negative(ansible_zos_module):
    """This submits a 30 second job and only waits 10 seconds"""
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 10

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_30_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=DATA_SET_NAME, state="present", type="pds", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, DATA_SET_NAME)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src = DATA_SET_NAME + "(BPXSLEEP)",
                                           location = "DATA_SET", wait_time_s = wait_time_s)

        for result in results.contacted.values():
            assert result.get("msg") is not None
            assert result.get('changed') is False
            assert result.get('duration') >= wait_time_s
            # expecting at least "long running job that exceeded its maximum wait"
            assert re.search(r'exceeded', repr(result.get("msg")))
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("args", [
    dict(max_rc=None, wait_time_s=10),
    dict(max_rc=4, wait_time_s=10),
    dict(max_rc=12, wait_time_s=20)
])
def test_job_submit_max_rc(ansible_zos_module, args):
    """This"""
    try:
        hosts = ansible_zos_module
        tmp_file = tempfile.NamedTemporaryFile(delete=True)
        with open(tmp_file.name, "w") as f:
            f.write(JCL_FILE_CONTENTS_RC_8)

        results = hosts.all.zos_job_submit(
            src=tmp_file.name, location="LOCAL", max_rc=args["max_rc"], wait_time_s=args["wait_time_s"]
        )

        for result in results.contacted.values():
            # Should fail normally as a non-zero RC will result in job submit failure
            if args["max_rc"] is None:
                assert result.get("msg") is not None
                assert result.get('changed') is False
                # On busy systems, it is possible that the duration even for a job with a non-zero return code
                # will take considerable time to obtain the job log and thus you could see either error msg below
                # Expecting: - "The job return code 8 was non-zero in the job output, this job has failed"
                #           - Consider using module zos_job_query to poll for a long running job or
                #             increase option \\'wait_times_s` to a value greater than 10.",
                if result.get('duration') >= args["wait_time_s"]:
                    re.search(r'long running job', repr(result.get("msg")))
                else:
                    assert re.search(r'non-zero', repr(result.get("msg")))

            # Should fail with normally as well, job fails with an RC 8 yet max is set to 4
            elif args["max_rc"] == 4:
                assert result.get("msg") is not None
                assert result.get('changed') is False
                # Expecting "The job return code, 'ret_code[code]' 8 for the submitted job is greater
                # than the value set for option 'max_rc' 4. Increase the value for 'max_rc' otherwise
                # this job submission has failed.
                assert re.search(r'the submitted job is greater than the value set for option', repr(result.get("msg")))

            elif args["max_rc"] == 12:
                # Will not fail but changed will be false for the non-zero RC, there
                # are other possibilities like an ABEND or JCL ERROR will fail this even
                # with a MAX RC
                assert result.get("msg") is None
                assert result.get('changed') is False
                assert result.get("jobs")[0].get("ret_code").get("code") < 12

    finally:
        hosts.all.file(path=tmp_file.name, state="absent")
