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
PROC_JCL_CONTENT="""//TESTERS  PROC
//TEST     JOB MSGCLASS=A,NOTIFY=&SYSUID
//STEP1    EXEC PGM=BPXBATCH,PARM='SH'
//STDOUT   DD   SYSOUT=*                                               
//STDERR   DD   SYSOUT=*
//STDPARM  DD *,SYMBOLS=EXECSYS
SH sleep 60
/*
//PEND"""

# Input arguments validation
def test_start_task_with_invalid_member(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMTASK"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
    
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLETASK"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None

def test_start_task_with_jobname_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        job_name = "SAMTASK",
        identifier = "TESTER"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_task_with_invalid_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPTASK",
        identifier = "$HELLO"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None
    
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        identifier = "HELLO"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE.HELLO"

def test_start_task_with_invalid_jobaccount(ansible_zos_module):
    hosts = ansible_zos_module
    job_account = "(T043JM,JM00,1,0,0,This is the invalid job account information to test negative scenario)"
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        job_account = job_account
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_task_with_invalid_devicenum(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        device_number = "0870"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_task_with_invalid_volumeserial(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        volume_serial = "12345A"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE,,12345A"

def test_start_task_with_invalid_parameters(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        parameters = ["KEY1"]
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE,,,'KEY1'"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        parameters = ["KEY1", "KEY2", "KEY3"],
        volume_serial = "123456"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "S SAMPLE,,123456,(KEY1,KEY2,KEY3)"

def test_start_task_with_devicenum_devicetype_negative(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        device_number = "/0870",
        device_type = "TEST"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None


def test_start_task_with_invalid_subsystem_negative(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "VLF",
        subsystem = "MSTRS"
    )
    for result in start_results.contacted.values():
        print(result)
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
        print(result)
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
        print(result)
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
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == 'S VLF,KEY1=VALUE1,KEY2=VALUE2'


def test_start_task_using_nonexisting_devicenum_negative(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state = "started",
        member_name = "SAMPLE",
        device_number = "/ABCD"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == 'S SAMPLE,/ABCD'

def test_display_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    display_results = hosts.all.zos_started_task(
        state = "displayed",
        identifier = "SAMPLE"
    )
    for result in display_results.contacted.values():
        print(result)
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
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None

    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in stop_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "P TESTER.SAMPLE"

def test_modify_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    modify_results = hosts.all.zos_started_task(
        state = "modified",
        identifier = "SAMPLE"
    )
    for result in modify_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None
    
    modify_results = hosts.all.zos_started_task(
        state = "modified",
        job_name = "TESTER"
    )
    for result in modify_results.contacted.values():
        print(result)
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
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "F TESTER.SAMPLE,REPLACE,VX=10"

def test_cancel_task_negative(ansible_zos_module):
    hosts = ansible_zos_module
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        identifier = "SAMPLE"
    )
    for result in cancel_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in cancel_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "C TESTER.SAMPLE"
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        asid = "0012",
        userid = "OMVSTEST",
        dump = True,
        verbose=True
    )
    for result in cancel_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "C U=OMVSTEST,A=0012,DUMP"
    cancel_results = hosts.all.zos_started_task(
        state = "cancelled",
        userid = "OMVSADM",
        armrestart = True
    )
    for result in cancel_results.contacted.values():
        print(result)
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
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    force_results = hosts.all.zos_started_task(
        state = "forced",
        job_name = "TESTER",
        identifier = "SAMPLE"
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "FORCE TESTER.SAMPLE"
    force_results = hosts.all.zos_started_task(
        state = "forced",
        userid = "OMVSADM",
        armrestart = True
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

    force_results = hosts.all.zos_started_task(
        state = "forced",
        job_name = "TESTER",
        retry = "YES"
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None
    force_results = hosts.all.zos_started_task(
        state = "forced",
        job_name = "TESTER",
        tcb_address = "0006789",
        retry = "YES"
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None
    force_results = hosts.all.zos_started_task(
        state = "forced",
        job_name = "TESTER",
        identifier = "SAMPLE",
        tcb_address = "000678",
        retry = "YES"
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "FORCE TESTER.SAMPLE,TCB=000678,RETRY=YES"
    force_results = hosts.all.zos_started_task(
        state = "forced",
        userid = "OMVSTEST",
        tcb_address = "000678",
        retry = "YES",
        verbose=True
    )
    for result in force_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("stderr") is not None
        assert result.get("cmd") == "FORCE U=OMVSTEST,TCB=000678,RETRY=YES"


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
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is not None

        force_results = hosts.all.zos_started_task(
            state = "forced",
            task_name = "SAMPLE"
        )
        for result in force_results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("stderr") is not None
            assert result.get("cmd") == "FORCE SAMPLE"
            assert "CANCELABLE - ISSUE CANCEL BEFORE FORCE" in result.get("stderr")

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE"
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None

        # validate identifier
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            identifier = "TESTER",
            reus_asid = "YES"
        )
        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None
            assert result.get("cmd") == "S SAMPLE.TESTER,REUSASID=YES"

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE"
        )
        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("stderr") is not None
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE",
            identifier = "TESTER"
        )
        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None

        job_account = "(T043JM,JM00,1,0,0,)"
        start_results = hosts.all.zos_started_task(
            state = "started",
            member = "SAMPLE",
            job_account = job_account
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None

        display_result = hosts.all.zos_started_task(
            state = "displayed",
            task = "SAMPLE"
        )
        for result in display_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is None

        display_output = list(display_result.contacted.values())[0].get("stdout")
        asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)
        
        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task_name = "SAMPLE",
            asid = asid_val,
            verbose=True
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
            assert len(result.get("tasks")) > 0
            assert result.get("verbose_output") is not None

    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(SAMPLE)'".format(PROC_PDS)
        )

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
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task = "TESTTSK"
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
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
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "F VLF,REPLACE,NN=00"

    display_result = hosts.all.zos_started_task(
        state = "displayed",
        task = "VLF"
    )
    for result in display_result.contacted.values():
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert len(result.get("tasks")) > 0
        assert result.get("verbose_output") is None

    display_output = list(display_result.contacted.values())[0].get("stdout")
    asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)

    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        task = "VLF",
        asid = asid_val
    )
    for result in stop_results.contacted.values():
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == f"P VLF,A={asid_val}"

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "VLF",
        identifier = "TESTER",
        subsystem = "MSTR"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""

    modify_results = hosts.all.zos_started_task(
        state = "modified",
        task = "VLF",
        identifier = "TESTER",
        parameters = ["REPLACE" ,"NN=00"]
    )
    for result in modify_results.contacted.values():
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""
        assert result.get("cmd") == "F VLF.TESTER,REPLACE,NN=00"
    
    stop_results = hosts.all.zos_started_task(
        state = "stopped",
        task = "VLF",
        identifier = "TESTER"
    )
    for result in stop_results.contacted.values():
        print(result)
        assert result.get("changed") is True
        assert result.get("rc") == 0
        assert result.get("stderr") == ""

    start_results = hosts.all.zos_started_task(
        state = "started",
        member = "VLF",
        subsystem = "MSTR"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is True
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
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state = "cancelled",
            task = "SPROC"
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
        
    finally:
        hosts.all.file(path=temp_path, state="absent")
        hosts.all.shell(
            cmd="drm {0}".format(data_set_name)
        )
        hosts.all.shell(
            cmd="mrm '{0}(SAMPLE2)'".format(PROC_PDS)
        )