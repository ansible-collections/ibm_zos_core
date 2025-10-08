#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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
from shellescape import quote
import re

TMP_DIRECTORY = "/tmp/"
PROC_PDS = "USER.PRIVATE.PROCLIB"
TASK_JCL_CONTENT="""//STEP1    EXEC PGM=BPXBATCH
//STDOUT   DD   SYSOUT=*                                               
//STDERR   DD   SYSOUT=*
//STDPARM  DD *
SH sleep 600
/*"""
PARAM_JCL_CONTENT="""//MSLEEP  PROC SECS=10
//STEP1    EXEC PGM=BPXBATCH,
//         PARM='SH sleep &SECS'
//STDOUT   DD SYSOUT=*
//STDERR   DD SYSOUT=*
//"""

# Input arguments validation
def test_start_task_with_invalid_member(ansible_zos_module):
    hosts = ansible_zos_module
    # Check with non-existing member
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMTASK"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("msg") is not None
    # Validating with member name more than 8 chars
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLETASK"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None

def test_start_task_with_jobname_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    # validate jobname and identifier with non-existing member
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        job_name = "SAMTASK",
        identifier = "TESTER"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_task_with_invalid_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    # validate using invalid identifier
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPTASK",
        identifier = "$HELLO"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None
        assert result.get("msg") is not None

    # validate using proper identifier and non-existing member
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        identifier = "HELLO"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE.HELLO"
        assert result.get("msg") is not None

def test_start_task_with_invalid_jobaccount(ansible_zos_module):
    hosts = ansible_zos_module
    job_account = "(T043JM,JM00,1,0,0,This is the invalid job account information to test negative scenario)"
    # validate invalid job_account with non-existing member
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        job_account = job_account
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

# def test_start_task_with_invalid_devicenum(ansible_zos_module):
#     hosts = ansible_zos_module
#     # validate invalid devicenum with non-existing member
#     start_results = hosts.all.zos_started_task(
#         state = "started",
#         member_name = "SAMPLE",
#         device_number = "0870"
#     )
#     for result in start_results.contacted.values():
#         assert result.get("changed") is False
#         assert result.get("failed") is True
#         assert result.get("msg") is not None

# def test_start_task_with_invalid_volumeserial(ansible_zos_module):
#     hosts = ansible_zos_module
#     start_results = hosts.all.zos_started_task(
#         state = "started",
#         member_name = "SAMPLE",
#         volume = "12345A"
#     )
#     for result in start_results.contacted.values():
#         assert result.get("changed") is False
#         assert result.get("stderr") is not None
#         assert result.get("cmd") == "S SAMPLE,,12345A"
#         assert result.get("msg") is not None

def test_start_task_with_invalid_parameters(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        parameters = ["KEY1"]
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE,,,'KEY1'"
        assert result.get("msg") is not None

    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        parameters = ["KEY1", "KEY2", "KEY3"]
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE,,,(KEY1,KEY2,KEY3)"
        assert result.get("msg") is not None

# def test_start_task_with_devicenum_devicetype_negative(ansible_zos_module):
#     hosts = ansible_zos_module
#     start_results = hosts.all.zos_started_task(
#         state = "started",
#         member_name = "SAMPLE",
#         device_number = "/0870",
#         device_type = "TEST"
#     )
#     for result in start_results.contacted.values():
#         assert result.get("changed") is False
#         assert result.get("failed") is True
#         assert result.get("msg") is not None


def test_start_task_with_invalid_subsystem_negative(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "VLF",
        subsystem = "MSTRS"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None


def test_start_task_with_invalid_keywordparams_negative(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "VLF",
        keyword_parameters = {
            "key1key1key1key1key1key1key1key1": "value1value1value1value1value1value1"
        }
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "VLF",
        keyword_parameters = {
            "key1key1key1key1key1key1key1key1key1key1key1key1": "value1"
        }
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "VLF",
        keyword_parameters = {
            "KEY1": "VALUE1",
            "KEY2": "VALUE2"
        }
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == 'S VLF,KEY1=VALUE1,KEY2=VALUE2'
        assert result.get("msg") is not None
        assert result.get("verbose_output") == ""


# def test_start_task_using_nonexisting_devicenum_negative(ansible_zos_module):
#     hosts = ansible_zos_module
#     start_results = hosts.all.zos_started_task(
#         state = "started",
#         member_name = "SAMPLE",
#         device_number = "/ABCD"
#     )
#     for result in start_results.contacted.values():
#         assert result.get("changed") is False
#         assert result.get("stderr") is not None
#         assert result.get("cmd") == 'S SAMPLE,/ABCD'
#         assert result.get("msg") is not None
#         assert result.get("verbose_output") == ""

def test_display_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    display_results = hosts.all.zos_started_task(
        state = "displayed",
        identifier = "SAMPLE"
    )
    for result in display_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None


def test_stop_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        job_name = "SAMPLE"
    )
    for result in stop_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None
        assert result.get("msg") is not None

    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in stop_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "P TESTER.SAMPLE"
        assert result.get("msg") is not None

def test_modify_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    modify_results = hosts.all.zos_started_task(
        state = "modified",
        identifier = "SAMPLE"
    )
    for result in modify_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None
    
    modify_results = hosts.all.zos_started_task(
        state = "modified",
        job_name = "TESTER"
    )
    for result in modify_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    modify_results = hosts.all.zos_started_task(
        state = "modified",
        job_name = "TESTER",
        identifier = "SAMPLE",
        parameters = ["REPLACE", "VX=10"]
    )
    for result in modify_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "F TESTER.SAMPLE,REPLACE,VX=10"
        assert result.get("msg") is not None

def test_cancel_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        identifier = "SAMPLE"
    )
    for result in cancel_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in cancel_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "C TESTER.SAMPLE"
        assert result.get("verbose_output") == ""
        assert result.get("msg") is not None

    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        asidx = "0012",
        userid = "OMVSTEST",
        dump = True,
        verbose=True
    )
    for result in cancel_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "C U=OMVSTEST,A=0012,DUMP"
        assert result.get("verbose_output") != ""
        assert result.get("msg") is not None
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        userid = "OMVSADM",
        armrestart = True
    )
    for result in cancel_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_force_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    force_results = hosts.all.zos_started_task(
        state = "forced",
        identifier = "SAMPLE"
    )
    for result in force_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    force_results = hosts.all.zos_started_task(
        state = "forced",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in force_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "FORCE TESTER.SAMPLE"
    force_results = hosts.all.zos_started_task(
        state = "forced",
        userid = "OMVSADM",
        armrestart = True
    )
    for result in force_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    # force_results = hosts.all.zos_started_task(
    #     state = "forced",
    #     job_name = "TESTER",
    #     retry_force = True
    # )
    # for result in force_results.contacted.values():
    #     assert result.get("changed") is False
    #     assert result.get("failed") is True
    #     assert result.get("msg") is not None
    # force_results = hosts.all.zos_started_task(
    #     state = "forced",
    #     job_name = "TESTER",
    #     tcb_address = "0006789",
    #     retry_force = True
    # )
    # for result in force_results.contacted.values():
    #     assert result.get("changed") is False
    #     assert result.get("failed") is True
    #     assert result.get("msg") is not None
    # force_results = hosts.all.zos_started_task(
    #     state = "forced",
    #     job_name = "TESTER",
    #     identifier = "SAMPLE",
    #     tcb_address = "000678",
    #     retry_force = True
    # )
    # for result in force_results.contacted.values():
    #     assert result.get("changed") is False
    #     assert result.get("stderr") is not None
    #     assert result.get("cmd") == "FORCE TESTER.SAMPLE,TCB=000678,RETRY=YES"
    # force_results = hosts.all.zos_started_task(
    #     state = "forced",
    #     userid = "OMVSTEST",
    #     tcb_address = "000678",
    #     retry_force = True,
    #     verbose=True
    # )
    # for result in force_results.contacted.values():
    #     assert result.get("changed") is False
    #     assert result.get("stderr") is not None
    #     assert result.get("cmd") == "FORCE U=OMVSTEST,TCB=000678,RETRY=YES"
    #     assert result.get("verbose_output") != ""


def test_start_and_cancel_zos_started_task(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        hosts.all.shell(
            cmd="dcp {0} '{1}(SAMPLE)'".format(data_set_name, PROC_PDS)
        )

        start_results = hosts.all.zos_started_task(
            state = "started",
            member_name = "SAMPLE",
            verbose=True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") != ""

        force_results = hosts.all.zos_started_task(
            state = "forced",
            task_name = "SAMPLE"
        )
        for result in force_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("stderr") is not None
            assert len(result.get("tasks")) > 0
            assert result.get("cmd") == "FORCE SAMPLE"
            assert result.get("msg") is not None
            assert "CANCELABLE - ISSUE CANCEL BEFORE FORCE" in result.get("stderr")

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE"
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""

        # validate identifier
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            identifier = "TESTER",
            reus_asid = True
        )
        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""
            assert result.get("cmd") == "S SAMPLE.TESTER,REUSASID=YES"

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE"
        )
        for result in stop_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("stderr") is not None
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE",
            identifier = "TESTER"
        )
        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""

        job_account = "(T043JM,JM00,1,0,0,)"
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            job_account = job_account
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            job_account = job_account
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""

        display_result = hosts.all.zos_started_task(
            state = "displayed",
            task = "SAMPLE"
        )
        for result in display_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") == ""

        display_output = list(display_result.contacted.values())[0].get("stdout")
        asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)
        
        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE",
            asidx = asid_val,
            verbose=True
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") != ""
        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE",
            verbose=True
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") != ""

    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        # hosts.all.shell(
        #     cmd="mrm '{0}(SAMPLE)'".format(PROC_PDS)
        # )

def test_start_with_jobname_and_cancel_zos_started_task(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        hosts.all.shell(
            cmd="dcp {0} \"//'{1}(SAMPLE)'\"".format(data_set_name, PROC_PDS)
        )

        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            job_name = "TESTTSK"
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task = "TESTTSK"
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) > 0
            assert result.get("stderr") == ""
        
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(SAMPLE)'".format(PROC_PDS)
        )

def test_stop_and_modify_with_vlf_task(ansible_zos_module):
    hosts = ansible_zos_module
    modify_results = hosts.all.zos_started_task(
        state = "modified",
        task = "VLF",
        parameters = ["REPLACE" ,"NN=00"]
    )
    for result in modify_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "F VLF,REPLACE,NN=00"

    display_result = hosts.all.zos_started_task(
        state = "displayed",
        task = "VLF"
    )
    for result in display_result.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert len(result.get("tasks")) > 0
        assert result.get("verbose_output") == ""

    display_output = list(display_result.contacted.values())[0].get("stdout")
    asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)

    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        task = "VLF",
        asidx = asid_val
    )
    for result in stop_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"P VLF,A={asid_val}"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "VLF",
        identifier = "TESTER",
        subsystem = "MSTR"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""

    modify_results = hosts.all.zos_started_task(
        state = "modified",
        task = "VLF",
        identifier = "TESTER",
        parameters = ["REPLACE" ,"NN=00"]
    )
    for result in modify_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert len(result.get("tasks")) > 0
        assert result.get("cmd") == "F VLF.TESTER,REPLACE,NN=00"
    
    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        task = "VLF",
        identifier = "TESTER"
    )
    for result in stop_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert len(result.get("tasks")) > 0

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "VLF",
        subsystem = "MSTR"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is True
        assert len(result.get("tasks")) > 0
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
 

def test_starting_and_cancel_zos_started_task_with_params(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(TASK_JCL_CONTENT), temp_path)
        )

        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        hosts.all.shell(
            cmd="dcp {0} \"//'{1}(SAMPLE2)'\"".format(data_set_name, PROC_PDS)
        )

        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE2",
            job_name = "SPROC",
            verbose=True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") != ""

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task = "SPROC"
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
        
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(SAMPLE2)'".format(PROC_PDS)
        )

def test_force_and_start_with_icsf_task(ansible_zos_module):
    hosts = ansible_zos_module
    display_results = hosts.all.zos_started_task(
        state = "displayed",
        task = "ICSF"
    )
    for result in display_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "D A,ICSF"
        assert len(result.get("tasks")) > 0
    
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        task = "ICSF"
    )
    for result in cancel_results.contacted.values():
        assert result.get("changed") is False
        assert result.get("rc") == 1
        assert result.get("stderr") != ""
        assert len(result.get("tasks")) > 0

    asidx = result.get("tasks")[0].get("asidx")
    force_results = hosts.all.zos_started_task(
        state = "forced",
        task = "ICSF",
        identifier = "ICSF",
        asidx = asidx,
        arm = True
    )
    for result in force_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"FORCE ICSF.ICSF,A={asidx},ARM"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "ICSF"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "S ICSF"
        assert len(result.get("tasks")) > 0

def test_start_with_keyword_param_and_cancel_zos_started_task(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(PARAM_JCL_CONTENT), temp_path)
        )

        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        hosts.all.shell(
            cmd="dcp {0} \"//'{1}(MSLEEP)'\"".format(data_set_name, PROC_PDS)
        )
        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task = "MSLEEP"
        )
        for result in display_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("rc") == 1
            assert len(result.get("tasks")) == 0
            assert result.get("stderr") != ""

        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "MSLEEP",
            keyword_parameters = {"SECS": "60"},
            verbose = True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
        
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "MSLEEP",
            keyword_parameters = {"SECS": "80"},
            verbose = True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""

        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task = "MSLEEP"
        )

        for result in display_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 2
            assert result.get("stderr") == ""

        display_output = list(display_results.contacted.values())[0].get("stdout")
        asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)
        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task = "MSLEEP",
            asidx = asid_val
        )

        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
        
        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task = "MSLEEP"
        )

        for result in display_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(MSLEEP)'".format(PROC_PDS)
        )
def test_start_and_cancel_zos_started_task_using_task_id(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        temp_path = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.file(path=temp_path, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(PARAM_JCL_CONTENT), temp_path)
        )

        hosts.all.shell(
            cmd="dcp {0}/SAMPLE {1}".format(temp_path, data_set_name)
        )

        hosts.all.shell(
            cmd="dcp {0} \"//'{1}(MSLEEP)'\"".format(data_set_name, PROC_PDS)
        )
        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task_id = "STCABCDEF"
        )
        for result in display_results.contacted.values():
            assert result.get("changed") is False
            assert result.get("rc") == 4
            assert result.get("msg") != ""

        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "MSLEEP",
            keyword_parameters = {"SECS": "60"},
            verbose = True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
        
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "MSLEEP",
            keyword_parameters = {"SECS": "80"},
            verbose = True
        )

        for result in start_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""

        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task = "MSLEEP"
        )

        for result in display_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 2
            assert result.get("stderr") == ""

        display_output = list(display_results.contacted.values())[0].get("stdout")
        task_id =  re.search(r"\bWUID=([^ \n\r\t]+)", display_output).group(1)
        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_id = task_id
        )
        for result in stop_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
        display_results = hosts.all.zos_started_task(
            state = "displayed",
            task = "MSLEEP"
        )

        for result in display_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert len(result.get("tasks")) == 1
            assert result.get("stderr") == ""
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(MSLEEP)'".format(PROC_PDS)
        )

def test_stop_and_force_with_ICSF_task_using_task_id(ansible_zos_module):
    hosts = ansible_zos_module
    display_result = hosts.all.zos_started_task(
        state = "displayed",
        task = "ICSF"
    )
    for result in display_result.contacted.values():
        task_id = result.get('tasks')[0]['task_id']
        asid_val = result.get('tasks')[0]['asidx']
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert len(result.get("tasks")) > 0
        assert result.get("verbose_output") == ""
    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        task_id = task_id
    )
    for result in stop_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"P ICSF.ICSF,A={asid_val}"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "ICSF"
    )
    for result in start_results.contacted.values():
        task_id = result.get('tasks')[0]['task_id']
        asid_val = result.get('tasks')[0]['asidx']
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
    force_results = hosts.all.zos_started_task(
        state = "forced",
        task_id = task_id,
        arm = True
    )
    for result in force_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"FORCE ICSF.ICSF,A={asid_val},ARM"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "ICSF"
    )
    for result in start_results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert len(result.get("tasks")) > 0
        assert result.get("stderr") == ""

# This testcase will be successful when a TSO session with user 'OMVSADM' is open.
# def test_cancel_using_userid(ansible_zos_module):
#     hosts = ansible_zos_module
#     display_results = hosts.all.zos_started_task(
#         state = "cancelled",
#         userid = "OMVSADM"
#     )
#     for result in display_results.contacted.values():
#         print(result)
#         assert result.get("changed") is True
#         assert result.get("rc") == 0
#         assert result.get("stderr") == ""
#         assert result.get("cmd") == "C U=OMVSADM"
#         assert len(result.get("tasks")) > 0
