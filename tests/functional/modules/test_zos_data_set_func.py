# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2023
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

import pytest
import time
import subprocess
from pipes import quote
from pprint import pprint


# TODO: determine if data set names need to be more generic for testcases
# TODO: add additional tests to check additional data set creation parameter combinations

data_set_types = [
    ("pds"),
    ("seq"),
    ("pdse"),
    ("esds"),
    ("rrds"),
    ("lds"),
]

DEFAULT_VOLUME = "000000"
DEFAULT_VOLUME2 = "222222"
DEFAULT_DATA_SET_NAME = "USER.PRIVATE.TESTDS"
DEFAULT_DATA_SET_NAME_WITH_MEMBER = "USER.PRIVATE.TESTDS(TESTME)"
TEMP_PATH = "/tmp/jcl"

ECHO_COMMAND = "echo {0} > {1}/SAMPLE"

KSDS_CREATE_JCL = """//CREKSDS    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME(USER.PRIVATE.TESTDS) -
   INDEXED                                 -
   KEYS(6 1)                               -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   FREESPACE(3 3)                          -
   VOLUMES(000000) )                       -
   DATA (NAME(USER.PRIVATE.TESTDS.DATA))     -
   INDEX (NAME(USER.PRIVATE.TESTDS.INDEX))
/*
"""

RRDS_CREATE_JCL = """//CRERRDS    JOB (T043JM,JM00,1,0,0,0),'CREATE RRDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('USER.PRIVATE.TESTDS') -
   NUMBERED                                -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   REUSE                                   -
   FREESPACE(3 3)                          -
   VOLUMES(000000) )                       -
   DATA (NAME('USER.PRIVATE.TESTDS.DATA'))
/*
"""

ESDS_CREATE_JCL = """//CREESDS    JOB (T043JM,JM00,1,0,0,0),'CREATE ESDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('USER.PRIVATE.TESTDS') -
   NONINDEXED                              -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   FREESPACE(3 3)                          -
   VOLUMES(000000) )                       -
   DATA (NAME('USER.PRIVATE.TESTDS.DATA'))
/*
"""

LDS_CREATE_JCL = """//CRELDS    JOB (T043JM,JM00,1,0,0,0),'CREATE LDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('USER.PRIVATE.TESTDS') -
   LINEAR                                  -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   VOLUMES(000000) )                       -
   DATA (NAME(USER.PRIVATE.TESTDS.DATA))
/*
"""

PDS_CREATE_JCL = """
//CREPDS    JOB (T043JM,JM00,1,0,0,0),'CREATE PDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD   *
     ALLOC -
           DSNAME('USER.PRIVATE.TESTDS') -
           NEW -
           VOL(000000) -
           DSNTYPE(PDS)
/*
"""


def make_tempfile(hosts, directory=False):
    """ Create temporary file on z/OS system and return the path """
    tempfile_name = ""
    results = hosts.all.tempfile(state="directory")
    for result in results.contacted.values():
        tempfile_name = result.get("path", "")
    return tempfile_name


def retrieve_data_set_names(results):
    """ Retrieve system generated data set names """
    data_set_names = []
    for result in results.contacted.values():
        if len(result.get("names", [])) > 0:
            for name in result.get("names"):
                if name.lower() != DEFAULT_DATA_SET_NAME.lower():
                    data_set_names.append(name)
    return data_set_names


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_catalog_and_uncatalog(ansible_zos_module, jcl):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="USS", wait=True, wait_time_s=30
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            pprint(result)
            if(result.get("jobs")[0].get("ret_code") is None):
                submitted_job_id = result.get("jobs")[0].get("job_id")
                assert submitted_job_id is not None
                results = hosts.all.zos_job_output(job_id=submitted_job_id)
                print("Getting failed JOB")
                pprint(vars(results))
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # verify first uncatalog was performed
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # verify second uncatalog shows uncatalog already performed
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is False
        # recatalog the data set
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
        # verify second catalog shows catalog already performed
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
    finally:
        # clean up
        hosts.all.file(path=TEMP_PATH, state="absent")
        # Added volumes to force a catalog in case they were somehow uncataloged to avoid an duplicate on volume error
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent", volumes=[DEFAULT_VOLUME, DEFAULT_VOLUME2])


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_present_when_uncataloged(ansible_zos_module, jcl):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="USS", wait=True
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent", volumes=DEFAULT_VOLUME)


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_replacement_when_uncataloged(ansible_zos_module, jcl):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="USS", wait=True
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            state="present",
            volumes=DEFAULT_VOLUME,
            replace=True,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_absent_when_uncataloged(ansible_zos_module, jcl):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="USS", wait=True
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set absent
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="absent", volumes=DEFAULT_VOLUME
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_absent_when_uncataloged_and_same_name_cataloged_is_present(ansible_zos_module, jcl):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET_NAME, state="cataloged", volumes=DEFAULT_VOLUME
    )
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
    results = hosts.all.zos_job_submit(
        src=TEMP_PATH + "/SAMPLE", location="USS", wait=True
    )
    # verify data set creation was successful
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
    # uncatalog the data set
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
    for result in results.contacted.values():
        assert result.get("changed") is True
    # Create the same dataset name in different volume
    jcl = jcl.replace(DEFAULT_VOLUME, DEFAULT_VOLUME2)
    hosts.all.file(path=TEMP_PATH + "/SAMPLE", state="absent")
    hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl), TEMP_PATH))
    results = hosts.all.zos_job_submit(
        src=TEMP_PATH + "/SAMPLE", location="USS", wait=True
    )
    # verify data set creation was successful
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
    hosts.all.file(path=TEMP_PATH, state="absent")
    # ensure data set absent
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET_NAME, state="absent", volumes=DEFAULT_VOLUME
    )
    for result in results.contacted.values():
        assert result.get("changed") is True
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_no_replace(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", type=dstype, replace=True
        )
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", type=dstype
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_replace(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", type=dstype, replace=True
        )
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", type=dstype, replace=True
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_absent(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME, state="present", type=dstype
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_deletion_when_present(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=dstype)
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("module_stderr") is None


def test_data_set_deletion_when_absent(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("module_stderr") is None


def test_batch_data_set_creation_and_deletion(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            batch=[
                {"name": DEFAULT_DATA_SET_NAME, "state": "absent"},
                {"name": DEFAULT_DATA_SET_NAME, "type": "pds", "state": "present"},
                {"name": DEFAULT_DATA_SET_NAME, "state": "absent"},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_batch_data_set_and_member_creation(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            batch=[
                {"name": DEFAULT_DATA_SET_NAME, "type": "pds", "directory_blocks": 5},
                {"name": DEFAULT_DATA_SET_NAME + "(newmem1)", "type": "member"},
                {
                    "name": DEFAULT_DATA_SET_NAME + "(newmem2)",
                    "type": "member",
                    "state": "present",
                },
                {"name": DEFAULT_DATA_SET_NAME, "state": "absent"},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


c_pgm="""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char** argv)
{
    char dsname[ strlen(argv[1]) + 4];
    sprintf(dsname, "//'%s'", argv[1]);
    FILE* member;
    member = fopen(dsname, "rb,type=record");
    sleep(300);
    fclose(member);
    return 0;
}
"""

call_c_jcl="""//PDSELOCK JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//LOCKMEM  EXEC PGM=BPXBATCH
//STDPARM DD *
SH /tmp/disp_shr/pdse-lock '{0}({1})'
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""

def test_data_member_force_delete(ansible_zos_module):
    MEMBER_1, MEMBER_2, MEMBER_3, MEMBER_4 = "MEM1", "MEM2", "MEM3", "MEM4"
    try:
        hosts = ansible_zos_module

        # set up:
        # create pdse
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type="pdse", replace=True)
        for result in results.contacted.values():
            assert result.get("changed") is True

        # add members
        results = hosts.all.zos_data_set(
            batch=[
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_2),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_3),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_4),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
            ]
        )
        # ensure data set/members create successful
        for result in results.contacted.values():
            assert result.get("changed") is True

        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.zos_copy(content=c_pgm, dest='/tmp/disp_shr/pdse-lock.c', force=True)
        hosts.all.zos_copy(
            content=call_c_jcl.format(DEFAULT_DATA_SET_NAME, MEMBER_1),
            dest='/tmp/disp_shr/call_c_pgm.jcl',
            force=True
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")

        # submit jcl
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")

        # pause to ensure c code acquires lock
        time.sleep(5)

        # non-force attempt to delete MEMBER_2 - should fail since pdse in in use.
        results = hosts.all.zos_data_set(
            name="{0}({1})".format(DEFAULT_DATA_SET_NAME, MEMBER_2),
            state="absent",
            type="MEMBER"
        )
        for result in results.contacted.values():
            assert result.get("failed") is True
            assert "DatasetMemberDeleteError" in result.get("msg")

        # attempt to delete MEMBER_3 with force option.
        results = hosts.all.zos_data_set(
            name="{0}({1})".format(DEFAULT_DATA_SET_NAME, MEMBER_3), state="absent", type="MEMBER", force=True
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        # attempt to delete MEMBER_4 with force option in batch mode.
        results = hosts.all.zos_data_set(
            batch=[
                {
                    "name": "{0}({1})".format(DEFAULT_DATA_SET_NAME, MEMBER_4),
                    "state": "absent",
                    "type": "MEMBER",
                    "force": True
                }
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        # confirm member deleted with mls -- mem1 and mem2 should be present but no mem3 and no mem4
        results = hosts.all.command(cmd="mls {0}".format(DEFAULT_DATA_SET_NAME))
        for result in results.contacted.values():
            assert MEMBER_1 in result.get("stdout")
            assert MEMBER_2 in result.get("stdout")
            assert MEMBER_3 not in result.get("stdout")
            assert MEMBER_4 not in result.get("stdout")

    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")

        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        # remove pdse
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_repeated_operations(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            type="PDS",
            space_primary=5,
            space_type="CYL",
            record_length=15,
            replace=True,
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            type="PDS",
            replace=True,
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME_WITH_MEMBER, type="MEMBER", replace=True
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME_WITH_MEMBER, type="MEMBER"
        )

        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME_WITH_MEMBER, type="MEMBER", state="absent"
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME_WITH_MEMBER, type="MEMBER", state="absent"
        )

        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_multi_volume_creation_uncatalog_and_catalog_nonvsam(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            type="SEQ",
            space_primary=5,
            space_type="CYL",
            record_length=15,
            volumes=[DEFAULT_VOLUME, DEFAULT_VOLUME2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            state="cataloged",
            volumes=[DEFAULT_VOLUME, DEFAULT_VOLUME2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_multi_volume_creation_uncatalog_and_catalog_vsam(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            type="KSDS",
            key_length=5,
            key_offset=0,
            space_primary=5,
            space_type="CYL",
            volumes=[DEFAULT_VOLUME, DEFAULT_VOLUME2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            state="cataloged",
            volumes=[DEFAULT_VOLUME, DEFAULT_VOLUME2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_data_set_old_aliases(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            state="present",
            format="fb",
            size="5m",
            volume=DEFAULT_VOLUME,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_data_set_temp_data_set_name(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            state="present",
        )
        data_set_names = retrieve_data_set_names(results)
        assert len(data_set_names) == 1
        for name in data_set_names:
            results2 = hosts.all.zos_data_set(name=name, state="absent")
            for result in results2.contacted.values():
                assert result.get("changed") is True
                assert result.get("module_stderr") is None
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        if isinstance(data_set_names, list):
            for name in data_set_names:
                results2 = hosts.all.zos_data_set(name=name, state="absent")


def test_data_set_temp_data_set_name_batch(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(
            batch=[
                dict(
                    state="present",
                ),
                dict(
                    state="present",
                ),
                dict(
                    state="present",
                ),
                dict(name=DEFAULT_DATA_SET_NAME, state="present"),
            ]
        )
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        data_set_names = retrieve_data_set_names(results)
        assert len(data_set_names) == 3
        for name in data_set_names:
            results2 = hosts.all.zos_data_set(name=name, state="absent")
            for result in results2.contacted.values():
                assert result.get("changed") is True
                assert result.get("module_stderr") is None
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        if isinstance(data_set_names, list):
            for name in data_set_names:
                results2 = hosts.all.zos_data_set(name=name, state="absent")


@pytest.mark.parametrize(
    "filesystem",
    ["HFS", "ZFS"],
)
def test_filesystem_create_and_mount(ansible_zos_module, filesystem):
    try:
        hosts = ansible_zos_module
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, type=filesystem)
        temp_dir_name = make_tempfile(hosts, directory=True)
        results2 = hosts.all.command(
            cmd="mount -t {0} -f {1} {2}".format(
                filesystem, DEFAULT_DATA_SET_NAME, temp_dir_name
            )
        )
        results3 = hosts.all.shell(cmd="cd {0} ; df .".format(temp_dir_name))

        # clean up
        results4 = hosts.all.command(cmd="unmount {0}".format(temp_dir_name))
        results5 = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
        results6 = hosts.all.file(path=temp_dir_name, state="absent")

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        for result in results2.contacted.values():
            assert result.get("changed") is True
            assert result.get("stderr") == ""
        for result in results3.contacted.values():
            assert result.get("changed") is True
            assert result.get("stderr") == ""
            assert DEFAULT_DATA_SET_NAME.upper() in result.get("stdout", "")
        for result in results4.contacted.values():
            assert result.get("changed") is True
            assert result.get("stderr") == ""
        for result in results5.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        for result in results6.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_data_set_creation_zero_values(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(
            name=DEFAULT_DATA_SET_NAME,
            state="present",
            type="KSDS",
            replace=True,
            space_primary=5,
            space_secondary=0,
            key_length=32,
            key_offset=0,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_data_set_creation_with_tmp_hlq(ansible_zos_module):
    try:
        tmphlq = "TMPHLQ"
        hosts = ansible_zos_module
        results = hosts.all.zos_data_set(state="present", tmp_hlq=tmphlq)
        dsname = None
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            for dsname in result.get("names"):
                assert dsname[:6] == tmphlq
    finally:
        if dsname:
            hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
