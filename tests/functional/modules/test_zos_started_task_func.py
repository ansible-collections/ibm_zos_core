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

def test_start_task_with_invalid_member(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state="started",
        member="SAMPLETASK"
    )
    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None

def test_start_task_with_invalid_identifier(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state="started",
        member="SAMPLE",
        identifier="$HELLO"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("stderr") is not None

def test_start_task_with_invalid_jobaccount(ansible_zos_module):
    hosts = ansible_zos_module
    job_account = "(T043JM,JM00,1,0,0,This is the invalid job account information to test negative scenario)"
    start_results = hosts.all.zos_started_task(
        state="started",
        member="SAMPLE",
        job_account=job_account
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_task_with_invalid_devicenum(ansible_zos_module):
    hosts = ansible_zos_module
    start_results = hosts.all.zos_started_task(
        state="started",
        member="SAMPLE",
        device_number="0870"
    )

    for result in start_results.contacted.values():
        print(result)
        assert result.get("changed") is False
        assert result.get("failed") is True
        assert result.get("msg") is not None

def test_start_and_cancel_zos_started_task(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        print(data_set_name)
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
            state="started",
            member="SAMPLE"
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task_name="SAMPLE"
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        job_account = "(T043JM,JM00,1,0,0,)"
        start_results = hosts.all.zos_started_task(
        state="started",
        member="SAMPLE",
        job_account=job_account
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        display_result = hosts.all.zos_started_task(
            state="display",
            task_name="SAMPLE"
        )
        for result in display_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""
        display_output = list(display_result.contacted.values())[0].get("stdout")
        asid_val =  re.search(r"\bA=([^ \n\r\t]+)", display_output).group(1)
        
        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task_name="SAMPLE",
            asid=asid_val
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
            state="started",
            member="SAMPLE",
            job_name="TESTTSK"
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task_name="TESTTSK"
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
        
        stop_results = hosts.all.zos_started_task(
            state="stopped",
            task_name="vlf"
        )

        for result in stop_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        start_results = hosts.all.zos_started_task(
            state="started",
            member="vlf",
            subsystem_name="mstr"
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        modify_results = hosts.all.zos_started_task(
            state="modified",
            task_name="vlf",
            parameters="replace,nn=00"
        )

        for result in modify_results.contacted.values():
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
            state="started",
            member="SAMPLE2",
            job_name="SPROC",
            verbose=True
        )

        for result in start_results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("stderr") == ""

        stop_results = hosts.all.zos_started_task(
            state="cancelled",
            task_name="SPROC"
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