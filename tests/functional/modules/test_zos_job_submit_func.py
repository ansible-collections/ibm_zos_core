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

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from shellescape import quote
import tempfile
import pytest
import re
import os

from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

# ##############################################################################
# Configure the job card as needed, most common keyword parameters:
#   CLASS: Used to achieve a balance between different types of jobs and avoid
#          contention between jobs that use the same resources.
#   MSGLEVEL: controls hpw the allocation messages and termination messages are
#             printed in the job's output listing (SYSOUT).
#   MSGCLASS: assign an output class for your output listing (SYSOUT)
# ##############################################################################

JCL_FILE_CONTENTS = """//*
//******************************************************************************
//* Happy path job that prints hello world, returns RC 0 as is.
//******************************************************************************
//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
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

JCL_FILE_CONTENTS_BACKSLASH_R = """//*
//******************************************************************************
//* Happy path job containing backslash r's, returns RC 0 after
//* zos_job_sbumit strips backslash r's, prints Hello world.
//******************************************************************************
//HELLOR    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
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

JCL_FILE_CONTENTS_BAD = """//*
//******************************************************************************
//* Negative path job containing !!'s.
//* Returns:
//*   ret_code->(code=null, msg=JCL ERROR <int>, msg_text=JCLERR)
//*   msg --> The JCL submitted with job id JOB00604 but there was an error,
//*           please review the error for further details: The job completion
//*           code (CC) was not in the job log. Please review the error
//*           JCL ERROR  555 and the job log.",
//******************************************************************************
//HELLO    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
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

JCL_FILE_CONTENTS_30_SEC = """//SLEEP30 JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//USSCMD EXEC PGM=BPXBATCH
//STDERR  DD SYSOUT=*
//STDOUT  DD SYSOUT=*
//STDPARM DD *
SH ls -la /;
sleep 30;
/*
//
"""

JCL_FILE_CONTENTS_05_SEC = """//SLEEP05 JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
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

JCL_TEMPLATES = {
    "Default": """//{{ pgm_name }}    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
{# This comment should not be part of the JCL #}
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD {{ input_dataset }}
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
{{ message  }}
/*
//SYSUT2   DD SYSOUT=*
//
""",

    "Custom": """//(( pgm_name ))    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEBGENER
(# This comment should not be part of the JCL #)
//SYSIN    DD (( input_dataset ))
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
(( message  ))
/*
//SYSUT2   DD SYSOUT=*
//
""",

    "Loop": """//JINJA    JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP0001 EXEC PGM=IEFBR14
{% for item in steps %}
//SYS{{ item.step_name }}    DD {{ item.dd }}
{% endfor %}
Hello, world!
/*
//SYSUT2   DD SYSOUT=*
//
"""
}

JCL_FILE_CONTENTS_NO_DSN = """//*
//******************************************************************************
//* Job containing a non existent DSN that will force an error.
//* Returns:
//*   ret_code->(code=null, msg=JCLERR, msg_txt=JCLERR, msg_code=None)
//*   msg --> The JCL submitted with job id JOB00532 but there was an error,
//*           please review the error for further details: The job completion
//*           code (CC) was not in the job log. Please review the error
//*           JCLERR ? and the job log.",
//******************************************************************************
//JOBLIBPM JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//JOBLIB DD DSN=DATASET.NOT.EXIST,DISP=SHR
//STEP1    EXEC PGM=HELLOPGM
//SYSPRINT DD SYSOUT=*
//SYSOUT   DD SYSOUT=*
//
"""

# Do not use this test case, although its fine, the problem is it does not trigger
# the correct behavior because ZOAU has a bug such that it will return the last
# job when it can not find what we requested, so this causes the wrong job
# go be found and analyzed. See JCL_FILE_CONTENTS_JCL_ERROR_INT that does actually
# force the code properly find the correct job.
# Fix coming in zoau 1.2.3
# JCL_FILE_CONTENTS_NO_JOB_CARD = """//STEP0001 EXEC PGM=IEBGENER
# //SYSIN    DD DUMMY
# //SYSPRINT DD SYSOUT=*
# //SYSUT1   DD *
# HELLO, WORLD
# /*
# //SYSUT2   DD SYSOUT=*
# //
# """

JCL_FILE_CONTENTS_JCL_ERROR_INT = """//*
//******************************************************************************
//* Another job containing no job card resulting in a JCLERROR with an value. It
//* won't always be 952, it will increment.
//* Returns:
//*   ret_code->(code=null, msg=JCLERR, msg_text=JCLERR, msg_code=null)
//*   msg --> The JCL submitted with job id JOB00728 but there was an error,
//*           please review the error for further details: The job completion
//*           code (CC) was not in the job log. Please review the error
//*           JCL ERROR  952 and the job log.
//******************************************************************************
//CLGP JOB
//CLG EXEC IGYWCLG
//COBOL.SYSIN DD DSN=IBMUSER.ANSIBLE.COBOL(HELLO),DISP=SHR
"""

JCL_FILE_CONTENTS_INVALID_USER = """//*
//******************************************************************************
//* Job containing a USER=FOOBAR that will cause JES to return a SEC ERROR which
//* is a security error.
//* Returns:
//*   ret_code->(code=None, msg=SEC, msg_txt=<msg>, msg_code=?)
//*   msg --> The JCL submitted with job id JOB01062 but there was an error,
//*           please review the error for further details: The job return code
//*           was not available in the job log, please review the job log and
//*           status SEC.
//******************************************************************************
//INVUSER JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM,USER=FOOBAR
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD
/*
//SYSUT2   DD SYSOUT=*
//
"""

JCL_FILE_CONTENTS_TYPRUN_SCAN = """//*
//******************************************************************************
//* Job containing a TYPRUN=SCAN will cause JES to run a syntax check and
//* not actually run the JCL. The job will be put on the H output queue, DDs
//* JESJCL and JESMSGLG are available. Ansible considers this a passing job.
//* Returns:
//*   ret_code->(code=null, msg=TYPRUN=SCAN, msg_txt=<msg>, msg_code=null)
//*   msg --> The job JOB00551 was run with special job processing TYPRUN=SCAN.
//*           This will result in no completion, return code or job steps and
//*           changed will be false."
//******************************************************************************
//SCAN JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=H,MSGLEVEL=1,NOTIFY=S0JM,TYPRUN=SCAN
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD. SCAN OPERATION
/*
//SYSUT2   DD SYSOUT=*
//
"""

JCL_FILE_CONTENTS_TYPRUN_COPY = """//*
//******************************************************************************
//* Job containing a TYPRUN=COPY will cause JES to copy the input job
//* (source content) stream directly to a sysout data set (device specified in
//* the message class parameter (H)) and schedule it for output processing, in
//* other words, the job will be put on the H output queue; DD's
//* JESMSGLG and JESJCLIN are available. Ansible considers this a failing job
//* given currently the jobs status can not be determined so it times out.
//* Returns:
//*   ret_code->(code=None, msg=None, msg_txt=<msg>, msg_code=None)
//*   msg --> The JCL submitted with job id JOB00555 but appears to be a long
//*           running job that exceeded its maximum wait time of 10 second(s).
//*           Consider using module zos_job_query to poll for a long running
//*           job or increase option 'wait_times_s' to a value greater than 11.
//******************************************************************************
//COPY JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=H,MSGLEVEL=1,NOTIFY=S0JM,TYPRUN=COPY
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD. COPY OPERATION
/*
//SYSUT2   DD SYSOUT=*
//
"""

JCL_FILE_CONTENTS_TYPRUN_HOLD = """//*
//******************************************************************************
//* Job containing a TYPRUN=HOLD will cause JES to hold this JCL without
//* executing it until a special event occurs at which time, the operator will
//* release the job from HOLD and allow the job to continue processing.
//* Ansible considers this a failing job
//* given currently the jobs status can not be determined so it times out.
//* Returns:
//*   ret_code->(code=None, msg=None, msg_txt=<msg>, msg_code=None)
//*   msg --> The JCL submitted with job id JOB00555 but appears to be a long
//*           running job that exceeded its maximum wait time of 10 second(s).
//*           Consider using module zos_job_query to poll for a long running
//*           job or increase option 'wait_times_s' to a value greater than 11.
//******************************************************************************
//HOLD JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=H,MSGLEVEL=1,NOTIFY=S0JM,TYPRUN=HOLD
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD. HOLD OPERATION
/*
//SYSUT2   DD SYSOUT=*
//
"""

JCL_FILE_CONTENTS_TYPRUN_JCLHOLD = """//*
//******************************************************************************
//* Job containing a TYPRUN=JCLHOLD will cause JES to will keep the submitted
//* job in the input queue until it's released by an operator or by the default
//* time assigned to the class parameter. As the operator you enter 'A' or 'R'
//* to release it from the queue.
//* Ansible considers this a failing job
//* given currently the jobs status can not be determined so it times out.
//* Returns:
//*   ret_code->(code=None, msg=None, msg_txt=<msg>, msg_code=None)
//*   msg --> The JCL submitted with job id JOB00555 but appears to be a long
//*           running job that exceeded its maximum wait time of 10 second(s).
//*           Consider using module zos_job_query to poll for a long running
//*           job or increase option 'wait_times_s' to a value greater than 11.
//******************************************************************************
//JCLHOLD JOB (T043JM,JM00,1,0,0,0),'HELLO WORLD - JRM',CLASS=R,
//             MSGCLASS=H,MSGLEVEL=1,NOTIFY=S0JM,TYPRUN=JCLHOLD
//STEP0001 EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSPRINT DD SYSOUT=*
//SYSUT1   DD *
HELLO, WORLD. JCLHOLD OPERATION
/*
//SYSUT2   DD SYSOUT=*
//
"""

JCL_FULL_INPUT = """//HLQ0  JOB MSGLEVEL=(1,1),
//  MSGCLASS=A,CLASS=A,NOTIFY=&SYSUID
//STEP1 EXEC PGM=BPXBATCH,PARM='PGM /bin/sleep 5'"""

C_SRC_INVALID_UTF8 = """#include <stdio.h>
int main()
{
    unsigned char a=0x64;
    unsigned char b=0x2A;
    unsigned char c=0xB8;
    unsigned char d=0xFF;
    unsigned char e=0x81;
    unsigned char f=0x82;
    unsigned char g=0x83;
    unsigned char h=0x00;
    /* The following are non-printables from DBB. */
    unsigned char nl=0x15;
    unsigned char cr=0x0D;
    unsigned char lf=0x25;
    unsigned char shiftOut=0x0E;
    unsigned char shiftIn=0x0F;

    printf("Value of a: Hex: %X, character: %c",a,a);
    printf("Value of b: Hex: %X, character: %c",b,b);
    printf("Value of c: Hex: %X, character: %c",c,c);
    printf("Value of d: Hex: %X, character: %c",d,d);
    printf("Value of e: Hex: %X, character: %c",e,e);
    printf("Value of f: Hex: %X, character: %c",f,f);
    printf("Value of g: Hex: %X, character: %c",g,g);
    printf("Value of h: Hex: %X, character: %c",h,h);
    printf("Value of NL: Hex: %X, character: %c",nl,nl);
    printf("Value of CR: Hex: %X, character: %c",cr,cr);
    printf("Value of LF: Hex: %X, character: %c",lf,lf);
    printf("Value of Shift-Out: Hex: %X, character: %c",shiftOut,shiftOut);
    printf("Value of Shift-In: Hex: %X, character: %c",shiftIn,shiftIn);

    return 0;
}
"""

JCL_INVALID_UTF8_CHARS_EXC = """//*
//******************************************************************************
//* Job that runs a C program that returns characters outside of the UTF-8 range
//* expected by Python. This job tests a bugfix present in ZOAU v1.3.0 and
//* later that deals properly with these chars.
//* The JCL needs to be formatted to give it the directory where the C program
//* is located.
//******************************************************************************
//NOEBCDIC JOB (T043JM,JM00,1,0,0,0),'NOEBCDIC - JRM',
//             MSGCLASS=H,MSGLEVEL=1,NOTIFY=&SYSUID
//NOPRINT  EXEC PGM=BPXBATCH
//STDPARM DD *
SH (
cd {0};
./noprint;
exit 0;
)
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//
"""

TEMP_PATH = "/tmp/jcl"
DATA_SET_NAME_SPECIAL_CHARS = "imstestl.im@1.xxx05"

@pytest.mark.parametrize(
    "location", [
        dict(default_location=True),
        dict(default_location=False),
        ]
)
def test_job_submit_PDS(ansible_zos_module, location):
    """
    Test zos_job_submit with a PDS(MEMBER), also test the default
    value for 'location', ensure it works with and without the
    value "DATA_SET". If default_location is True, then don't
    pass a 'location:DATA_SET' allow its default to come through.
    """
    try:
        results = None
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="present", type="PDS", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, data_set_name)
        )
        if bool(location.get("default_location")):
            results = hosts.all.zos_job_submit(
                src="{0}(SAMPLE)".format(data_set_name), wait_time_s=30
            )
        else:
            results = hosts.all.zos_job_submit(
                src="{0}(SAMPLE)".format(data_set_name), location="DATA_SET", wait_time_s=30
            )

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
       hosts.all.file(path=TEMP_PATH, state="absent")
       hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_job_submit_PDS_special_characters(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )
        hosts.all.zos_data_set(
            name=DATA_SET_NAME_SPECIAL_CHARS, state="present", type="PDS", replace=True
        )
        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(
                TEMP_PATH, DATA_SET_NAME_SPECIAL_CHARS
            )
        )
        results = hosts.all.zos_job_submit(
            src="{0}(SAMPLE)".format(DATA_SET_NAME_SPECIAL_CHARS),
            location="DATA_SET",
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
            src="{0}/SAMPLE".format(TEMP_PATH), location="USS", volume=None
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
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait_time_s=10)

    for result in results.contacted.values():
        print(result)
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0
        assert result.get("changed") is True


def test_job_submit_LOCAL_extraR(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_BACKSLASH_R)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait_time_s=10)

    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        assert result.get("jobs")[0].get("ret_code").get("code") == 0
        assert result.get("changed") is True


def test_job_submit_LOCAL_BADJCL(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_BAD)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL", wait_time_s=10)

    for result in results.contacted.values():
        # Expecting: The job completion code (CC) was not in the job log....."
        assert result.get("changed") is False
        assert re.search(r'completion code', repr(result.get("msg")))


def test_job_submit_PDS_volume(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        hosts.all.file(path=TEMP_PATH, state="directory")

        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FILE_CONTENTS), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="present", type="PDS", replace=True, volumes=volume_1
        )

        hosts.all.shell(
            cmd="cp {0}/SAMPLE \"//'{1}(SAMPLE)'\"".format(TEMP_PATH, data_set_name)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="uncataloged", type="PDS"
        )

        results = hosts.all.zos_job_submit(src=data_set_name+"(SAMPLE)", location="DATA_SET", volume=volume_1)
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_job_submit_PDS_5_SEC_JOB_WAIT_15(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 15

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_05_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="present", type="PDS", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, data_set_name)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src=data_set_name+"(BPXSLEEP)",
                    location="DATA_SET", wait_time_s=wait_time_s)

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
            assert result.get('duration') <= wait_time_s
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_job_submit_PDS_30_SEC_JOB_WAIT_60(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 60

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_30_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="present", type="PDS", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, data_set_name)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src=data_set_name+"(BPXSLEEP)",
                    location="DATA_SET", wait_time_s=wait_time_s)

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get('changed') is True
            assert result.get('duration') <= wait_time_s
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=data_set_name, state="absent")

def test_job_submit_PDS_30_SEC_JOB_WAIT_10_negative(ansible_zos_module):
    """This submits a 30 second job and only waits 10 seconds"""
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        hosts.all.file(path=TEMP_PATH, state="directory")
        wait_time_s = 10

        hosts.all.shell(
            cmd="echo {0} > {1}/BPXSLEEP".format(quote(JCL_FILE_CONTENTS_30_SEC), TEMP_PATH)
        )

        hosts.all.zos_data_set(
            name=data_set_name, state="present", type="PDS", replace=True
        )

        hosts.all.shell(
            cmd="cp {0}/BPXSLEEP \"//'{1}(BPXSLEEP)'\"".format(TEMP_PATH, data_set_name)
        )

        hosts = ansible_zos_module
        results = hosts.all.zos_job_submit(src=data_set_name+"(BPXSLEEP)",
                    location="DATA_SET", wait_time_s=wait_time_s)

        for result in results.contacted.values():
            assert result.get("msg") is not None
            assert result.get('changed') is False
            assert result.get('duration') >= wait_time_s
            # expecting at least "long running job that exceeded its maximum wait"
            assert re.search(r'exceeded', repr(result.get("msg")))
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=data_set_name, state="absent")


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
                #Expecting: - "The job return code 8 was non-zero in the job output, this job has failed"
                #           - Consider using module zos_job_query to poll for a long running job or
                #             increase option \\'wait_times_s` to a value greater than 10.",
                if result.get('duration'):
                    duration = result.get('duration')
                else:
                    duration = 0

                if duration >= args["wait_time_s"]:
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


@pytest.mark.template
@pytest.mark.parametrize("args", [
    dict(
        template="Default",
        options=dict(
            keep_trailing_newline=False
        )
    ),
    dict(
        template="Custom",
        options=dict(
            keep_trailing_newline=False,
            variable_start_string="((",
            variable_end_string="))",
            comment_start_string="(#",
            comment_end_string="#)"
        )
    ),
    dict(
        template="Loop",
        options=dict(
            keep_trailing_newline=False
        )
    )
])
def test_job_submit_jinja_template(ansible_zos_module, args):
    try:
        hosts = ansible_zos_module

        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(tmp_file.name, "w") as f:
            f.write(JCL_TEMPLATES[args["template"]])

        template_vars = dict(
            pgm_name="HELLO",
            input_dataset="DUMMY",
            message="Hello, world",
            steps=[
                dict(step_name="IN", dd="DUMMY"),
                dict(step_name="PRINT", dd="SYSOUT=*"),
                dict(step_name="UT1", dd="*")
            ]
        )
        for host in hosts["options"]["inventory_manager"]._inventory.hosts.values():
            host.vars.update(template_vars)

        results = hosts.all.zos_job_submit(
            src=tmp_file.name,
            location="LOCAL",
            use_template=True,
            template_parameters=args["options"]
        )

        for result in results.contacted.values():
            assert result.get('changed') is True
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0

    finally:
        os.remove(tmp_file.name)


def test_job_submit_full_input(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(JCL_FULL_INPUT), TEMP_PATH)
        )
        results = hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_PATH),
            location="USS",
            volume=None,
            # This job used to set wait=True, but since it has been deprecated
            # and removed, it now waits up to 30 seconds.
            wait_time_s=30
        )
        for result in results.contacted.values():
            print(result)
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")


def test_negative_job_submit_local_jcl_no_dsn(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_NO_DSN)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, wait_time_s=20, location="LOCAL")
    import pprint
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert re.search(r'completion code', repr(result.get("msg")))
        assert result.get("jobs")[0].get("job_id") is not None


def test_negative_job_submit_local_jcl_invalid_user(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_INVALID_USER)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name, location="LOCAL")

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert re.search(r'please review the error for further details', repr(result.get("msg")))
        assert re.search(r'please review the job log for status SEC', repr(result.get("msg")))
        assert result.get("jobs")[0].get("job_id") is not None
        assert re.search(r'please review the job log for status SEC', repr(result.get("jobs")[0].get("ret_code").get("msg_txt")))


def test_job_submit_local_jcl_typrun_scan(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_TYPRUN_SCAN)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name,
                                       location="LOCAL",
                                       wait_time_s=20,
                                       encoding={
                                            "from": "UTF-8",
                                            "to": "IBM-1047"
                                        },)
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs")[0].get("job_id") is not None
        assert re.search(r'run with special job processing TYPRUN=SCAN', repr(result.get("jobs")[0].get("ret_code").get("msg_txt")))
        assert result.get("jobs")[0].get("ret_code").get("code") is None
        assert result.get("jobs")[0].get("ret_code").get("msg") == "TYPRUN=SCAN"
        assert result.get("jobs")[0].get("ret_code").get("msg_code") is None


def test_job_submit_local_jcl_typrun_copy(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_TYPRUN_COPY)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name,
                                       location="LOCAL",
                                       wait_time_s=20,
                                       encoding={
                                            "from": "UTF-8",
                                            "to": "IBM-1047"
                                        },)
    import pprint
    for result in results.contacted.values():
        pprint.pprint(result)
        assert result.get("changed") is False
        assert result.get("jobs")[0].get("job_id") is not None
        assert re.search(r'please review the job log', repr(result.get("jobs")[0].get("ret_code").get("msg_txt")))
        assert result.get("jobs")[0].get("ret_code").get("code") is None
        assert result.get("jobs")[0].get("ret_code").get("msg") is None
        assert result.get("jobs")[0].get("ret_code").get("msg_code") is None


def test_job_submit_local_jcl_typrun_hold(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_TYPRUN_HOLD)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name,
                                       location="LOCAL",
                                       wait_time_s=20,
                                       encoding={
                                            "from": "UTF-8",
                                            "to": "IBM-1047"
                                        },)
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs")[0].get("job_id") is not None
        assert re.search(r'long running job', repr(result.get("jobs")[0].get("ret_code").get("msg_txt")))
        assert result.get("jobs")[0].get("ret_code").get("code") is None
        assert result.get("jobs")[0].get("ret_code").get("msg") == "AC"
        assert result.get("jobs")[0].get("ret_code").get("msg_code") is None


def test_job_submit_local_jcl_typrun_jclhold(ansible_zos_module):
    tmp_file = tempfile.NamedTemporaryFile(delete=True)
    with open(tmp_file.name, "w") as f:
        f.write(JCL_FILE_CONTENTS_TYPRUN_JCLHOLD)
    hosts = ansible_zos_module
    results = hosts.all.zos_job_submit(src=tmp_file.name,
                                       location="LOCAL",
                                       wait_time_s=20,
                                       encoding={
                                            "from": "UTF-8",
                                            "to": "IBM-1047"
                                        },)
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("jobs")[0].get("job_id") is not None
        assert re.search(r'long running job', repr(result.get("jobs")[0].get("ret_code").get("msg_txt")))
        assert result.get("jobs")[0].get("ret_code").get("code") is None
        assert result.get("jobs")[0].get("ret_code").get("msg") == "AC"
        assert result.get("jobs")[0].get("ret_code").get("msg_code") is None


# This test case is related to the following GitHub issues:
# - https://github.com/ansible-collections/ibm_zos_core/issues/677
# - https://github.com/ansible-collections/ibm_zos_core/issues/972
# - https://github.com/ansible-collections/ibm_zos_core/issues/1160
# - https://github.com/ansible-collections/ibm_zos_core/issues/1255
def test_zoau_bugfix_invalid_utf8_chars(ansible_zos_module):
    try:
        hosts = ansible_zos_module

        # Copy C source and compile it.
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/noprint.c".format(quote(C_SRC_INVALID_UTF8), TEMP_PATH)
        )
        hosts.all.shell(cmd="xlc -o {0}/noprint {0}/noprint.c".format(TEMP_PATH))

        # Create local JCL and submit it.
        tmp_file = tempfile.NamedTemporaryFile(delete=True)
        with open(tmp_file.name, "w") as f:
            f.write(JCL_INVALID_UTF8_CHARS_EXC.format(TEMP_PATH))

        results = hosts.all.zos_job_submit(
            src=tmp_file.name,
            location="LOCAL",
            wait_time_s=15
        )

        for result in results.contacted.values():
            # We shouldn't get an error now that ZOAU handles invalid/unprintable
            # UTF-8 chars correctly.
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")