# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2025
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

import time
from shlex import quote
from pprint import pprint
import pytest

# pylint: disable-next=import-error
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
# pylint: disable-next=import-error
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

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

TEMP_PATH = "/tmp/jcl"

ECHO_COMMAND = "echo {0} > {1}/SAMPLE"

KSDS_CREATE_JCL = """//CREKSDS    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME({1}) -
   INDEXED                                 -
   KEYS(6 1)                               -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   FREESPACE(3 3)                          -
   VOLUMES({0}) )                       -
   DATA (NAME({1}.DATA))     -
   INDEX (NAME({1}.INDEX))
/*
"""

RRDS_CREATE_JCL = """//CRERRDS    JOB (T043JM,JM00,1,0,0,0),'CREATE RRDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('{1}') -
   NUMBERED                                -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   REUSE                                   -
   FREESPACE(3 3)                          -
   VOLUMES({0}) )                       -
   DATA (NAME('{1}.DATA'))
/*
"""

ESDS_CREATE_JCL = """//CREESDS    JOB (T043JM,JM00,1,0,0,0),'CREATE ESDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('{1}') -
   NONINDEXED                              -
   RECSZ(80 80)                            -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   FREESPACE(3 3)                          -
   VOLUMES({0}) )                       -
   DATA (NAME('{1}.DATA'))
/*
"""

LDS_CREATE_JCL = """//CRELDS    JOB (T043JM,JM00,1,0,0,0),'CREATE LDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DEFINE CLUSTER (NAME('{1}') -
   LINEAR                                  -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   VOLUMES({0}) )                       -
   DATA (NAME({1}.DATA))
/*
"""

PDS_CREATE_JCL = """
//CREPDS    JOB (T043JM,JM00,1,0,0,0),'CREATE PDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD   *
     ALLOC -
           DSNAME('{1}') -
           NEW -
           VOL({0}) -
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
                data_set_names.append(name)
    return data_set_names

def print_results(results):
    for result in results.contacted.values():
        pprint(result)

@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
    ids=['PDS_CREATE_JCL', 'KSDS_CREATE_JCL', 'RRDS_CREATE_JCL', 'ESDS_CREATE_JCL', 'LDS_CREATE_JCL']
)
def test_data_set_catalog_and_uncatalog(ansible_zos_module, jcl, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    dataset = get_tmp_ds_name(2, 2)
    try:
        hosts.all.zos_data_set(
             name=dataset, state="cataloged", volumes=volume_1
        )
        hosts.all.zos_data_set(name=dataset, state="absent")

        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume_1, dataset)), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30
        )
        # verify data set creation was successful

        for result in results.contacted.values():
            if result.get("jobs")[0].get("ret_code") is None:
                submitted_job_id = result.get("jobs")[0].get("job_id")
                assert submitted_job_id is not None
                results = hosts.all.zos_job_output(job_id=submitted_job_id)
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"

        # verify first uncatalog was performed
        results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # verify second uncatalog shows uncatalog already performed
        results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is False
        # recatalog the data set
        results = hosts.all.zos_data_set(
            name=dataset, state="cataloged", volumes=volume_1
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
        # verify second catalog shows catalog already performed
        results = hosts.all.zos_data_set(
            name=dataset, state="cataloged", volumes=volume_1
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
    finally:
        # clean up
        hosts.all.file(path=TEMP_PATH, state="absent")
        # Added volumes to force a catalog in case they were
        # somehow uncataloged to avoid an duplicate on volume error
        hosts.all.zos_data_set(name=dataset, state="absent", volumes=volume_1)


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
    ids=['PDS_CREATE_JCL', 'KSDS_CREATE_JCL', 'RRDS_CREATE_JCL', 'ESDS_CREATE_JCL', 'LDS_CREATE_JCL']
)
def test_data_set_present_when_uncataloged(ansible_zos_module, jcl, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    dataset = get_tmp_ds_name(2, 2)
    try:
        hosts.all.zos_data_set(
            name=dataset, state="cataloged", volumes=volume_1
        )
        hosts.all.zos_data_set(name=dataset, state="absent")

        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume_1, dataset)), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=dataset, state="present", volumes=volume_1
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=dataset, state="present", volumes=volume_1
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=dataset, state="absent", volumes=volume_1)


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
    ids=['PDS_CREATE_JCL', 'KSDS_CREATE_JCL', 'RRDS_CREATE_JCL', 'ESDS_CREATE_JCL', 'LDS_CREATE_JCL']
)
def test_data_set_replacement_when_uncataloged(ansible_zos_module, jcl, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume = volumes.get_available_vol()
    dataset = get_tmp_ds_name(2, 2)
    try:
        hosts.all.zos_data_set(
            name=dataset, state="cataloged", volumes=volume
        )
        hosts.all.zos_data_set(name=dataset, state="absent")

        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume, dataset)), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=dataset, state="present", volumes=volume
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set present
        results = hosts.all.zos_data_set(
            name=dataset,
            state="present",
            volumes=volume,
            replace=True,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=dataset, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
    ids=['PDS_CREATE_JCL', 'KSDS_CREATE_JCL', 'RRDS_CREATE_JCL', 'ESDS_CREATE_JCL', 'LDS_CREATE_JCL']
)
def test_data_set_absent_when_uncataloged(ansible_zos_module, jcl, volumes_on_systems):
    try:
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(
            name=dataset, state="cataloged", volumes=volume_1
        )
        hosts.all.zos_data_set(name=dataset, state="absent")

        hosts.all.file(path=TEMP_PATH, state="directory")
        hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume_1, dataset)), TEMP_PATH))
        results = hosts.all.zos_job_submit(
            src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30
        )
        # verify data set creation was successful
        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
        # uncatalog the data set
        results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
        # ensure data set absent
        results = hosts.all.zos_data_set(
            name=dataset, state="absent", volumes=volume_1
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_PATH, state="absent")
        hosts.all.zos_data_set(name=dataset, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
    ids=['PDS_CREATE_JCL', 'KSDS_CREATE_JCL', 'RRDS_CREATE_JCL', 'ESDS_CREATE_JCL', 'LDS_CREATE_JCL']
)
def test_data_set_absent_when_uncataloged_and_same_name_cataloged_is_present(
    ansible_zos_module,
    jcl,
    volumes_on_systems
):
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    volume_2 = volumes.get_available_vol()
    hosts = ansible_zos_module
    dataset = get_tmp_ds_name(2, 2)
    hosts.all.zos_data_set(name=dataset, state="cataloged", volumes=volume_1)

    hosts.all.zos_data_set(name=dataset, state="absent")

    hosts.all.file(path=TEMP_PATH, state="directory")
    hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume_1, dataset)), TEMP_PATH))
    results = hosts.all.zos_job_submit(src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30)

    # verify data set creation was successful
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"

    # uncatalog the data set
    results = hosts.all.zos_data_set(name=dataset, state="uncataloged")
    for result in results.contacted.values():
        assert result.get("changed") is True

    # Create the same dataset name in different volume

    hosts.all.file(path=TEMP_PATH + "/SAMPLE", state="absent")
    hosts.all.shell(cmd=ECHO_COMMAND.format(quote(jcl.format(volume_2, dataset)), TEMP_PATH))
    results = hosts.all.zos_job_submit(src=TEMP_PATH + "/SAMPLE", location="uss", wait_time_s=30)

    # verify data set creation was successful
    for result in results.contacted.values():
        assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"

    hosts.all.file(path=TEMP_PATH, state="absent")

    # ensure second data set absent
    results = hosts.all.zos_data_set(name=dataset, state="absent", volumes=volume_2)
    for result in results.contacted.values():
        assert result.get("changed") is True

    # ensure first data set absent
    hosts.all.zos_data_set(name=dataset, state="cataloged")
    results = hosts.all.zos_data_set(name=dataset, state="absent", volumes=volume_1)
    for result in results.contacted.values():
        assert result.get("changed") is True


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_no_replace(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(
            name=dataset, state="present", type=dstype, replace=True
        )
        results = hosts.all.zos_data_set(
            name=dataset, state="present", type=dstype
        )
        hosts.all.zos_data_set(name=dataset, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=dataset, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_replace(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        results = hosts.all.zos_data_set(
            name=dataset, state="present", type=dstype, replace=True
        )
        results = hosts.all.zos_data_set(
            name=dataset, state="present", type=dstype, replace=True
        )
        hosts.all.zos_data_set(name=dataset, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=dataset, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_absent(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(name=dataset, state="absent")
        results = hosts.all.zos_data_set(
            name=dataset, state="present", type=dstype
        )
        hosts.all.zos_data_set(name=dataset, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=dataset, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_deletion_when_present(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    dataset = get_tmp_ds_name(2, 2)
    hosts.all.zos_data_set(name=dataset, state="present", type=dstype)
    results = hosts.all.zos_data_set(name=dataset, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("module_stderr") is None


def test_data_set_deletion_when_absent(ansible_zos_module):
    hosts = ansible_zos_module
    dataset = get_tmp_ds_name(2, 2)
    hosts.all.zos_data_set(name=dataset, state="absent")
    results = hosts.all.zos_data_set(name=dataset, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("module_stderr") is None


def test_batch_data_set_creation_and_deletion(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        results = hosts.all.zos_data_set(
            batch=[
                {"name": dataset, "state": "absent"},
                {"name": dataset, "type": "pds", "state": "present"},
                {"name": dataset, "state": "absent"},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=dataset, state="absent")


def test_batch_data_set_and_member_creation(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        dataset = get_tmp_ds_name(2, 2)
        results = hosts.all.zos_data_set(
            batch=[
                {"name": dataset, "type": "pds", "directory_blocks": 5},
                {"name": dataset + "(newmem1)", "type": "member"},
                {
                    "name": dataset + "(newmem2)",
                    "type": "member",
                    "state": "present",
                },
                {"name": dataset, "state": "absent"},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=dataset, state="absent")


c_pgm="""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char** argv)
{
    char dsname[ strlen(argv[1]) + 4];
    sprintf(dsname, \\\"//'%s'\\\", argv[1]);
    FILE* member;
    member = fopen(dsname, \\\"rb,type=record\\\");
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
    member_1, member_2, member_3, member_4 = "MEM1", "MEM2", "MEM3", "MEM4"
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        # set up:
        # create pdse
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            state="present",
            type="pdse",
            replace=True
        )
        for result in results.contacted.values():
            assert result.get("changed") is True

        #add members
        results = hosts.all.zos_data_set(
            batch=[
                {
                    "name": f"{default_data_set_name}({member_1})",
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": f"{default_data_set_name}({member_2})",
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": f"{default_data_set_name}({member_3})",
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": f"{default_data_set_name}({member_4})",
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
            ]
        )
        # ensure data set/members create successful
        for result in results.contacted.values():
            assert result.get("changed") is True

        hosts.all.file(path="/tmp/disp_shr/", state="directory")
        hosts.all.shell(cmd=f"echo \"{c_pgm}\"  > /tmp/disp_shr/pdse-lock.c")
        hosts.all.shell(
            cmd=f"echo \"{call_c_jcl.format(default_data_set_name, member_1)}\""+
            " > /tmp/disp_shr/call_c_pgm.jcl"
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")

        # submit jcl
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")

        # pause to ensure c code acquires lock
        time.sleep(5)

        # non-force attempt to delete member_2 - should fail since pdse in in use.
        results = hosts.all.zos_data_set(
            name=f"{default_data_set_name}({member_2})",
            state="absent",
            type="member"
        )
        for result in results.contacted.values():
            assert result.get("failed") is True
            assert "DatasetMemberDeleteError" in result.get("msg")

        # attempt to delete member_3 with force option.
        results = hosts.all.zos_data_set(
            name=f"{default_data_set_name}({member_3})",
            state="absent",
            type="member",
            force=True
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        # attempt to delete member_4 with force option in batch mode.
        results = hosts.all.zos_data_set(
            batch=[
                {
                    "name": f"{default_data_set_name}({member_4})",
                    "state": "absent",
                    "type": "member",
                    "force": True
                }
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        # confirm member deleted with mls -- mem1 and mem2 should be present but no mem3 and no mem4
        results = hosts.all.command(cmd=f"mls {default_data_set_name}")
        for result in results.contacted.values():
            assert member_1 in result.get("stdout")
            assert member_2 in result.get("stdout")
            assert member_3 not in result.get("stdout")
            assert member_4 not in result.get("stdout")

    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")

        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        # clean up c code/object/executable files, jcl
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        # remove pdse
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


def test_repeated_operations(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        default_data_set_name_with_member = default_data_set_name + "(MEM)"
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            type="pds",
            space_primary=5,
            space_type="cyl",
            record_length=15,
            replace=True,
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            type="pds",
            replace=True,
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name_with_member, type="member", replace=True
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name_with_member, type="member"
        )

        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name_with_member, type="member", state="absent"
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name_with_member, type="member", state="absent"
        )

        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


def test_multi_volume_creation_uncatalog_and_catalog_nonvsam(ansible_zos_module, volumes_on_systems):
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    volume_2 = volumes.get_available_vol()
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            type="seq",
            space_primary=5,
            space_type="cyl",
            record_length=15,
            volumes=[volume_1, volume_2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(name=default_data_set_name, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            state="cataloged",
            volumes=[volume_1, volume_2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")

def test_multi_volume_creation_uncatalog_and_catalog_vsam(ansible_zos_module, volumes_on_systems):
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    volume_2 = volumes.get_available_vol()
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            type="ksds",
            key_length=5,
            key_offset=0,
            space_primary=5,
            space_type="cyl",
            volumes=[volume_1, volume_2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(name=default_data_set_name, state="uncataloged")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            state="cataloged",
            volumes=[volume_1, volume_2],
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")

def test_creation_conflict_same_name_diff_volume(ansible_zos_module, volumes_on_systems):
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    volume_2 = volumes.get_available_vol()
    assert volume_1 != volume_2, "Need two different volumes for this test"

    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    try:
        # Step 1: Create PDS on volume_1
        results = hosts.all.zos_data_set(
            name=data_set_name,
            state="present",
            type="pds",
            volumes=[volume_1]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
        results = hosts.all.zos_data_set(
            name=data_set_name,
            state="present",
            type="pds",
            volumes=[volume_2]
        )
        for result in results.contacted.values():
            assert result.get("failed") is True
            assert "datasetcatalogedondifferentvolumeerror" in result.get("msg", "").lower()
    finally:
        # Cleanup
        hosts.all.zos_data_set(name=data_set_name, state="absent")

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
        default_data_set_name = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        results = hosts.all.zos_data_set(
            batch=[
                {
                    "state":"present",
                },
                {
                    "state":"present",
                },
                {
                    "state":"present",
                },
                {
                    "name":default_data_set_name,
                    "state":"present"
                },
            ]
        )
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        data_set_names = retrieve_data_set_names(results)
        assert len(data_set_names) == 4
        for name in data_set_names:
            if name != default_data_set_name:
                results2 = hosts.all.zos_data_set(name=name, state="absent")
            for result in results2.contacted.values():
                assert result.get("changed") is True
                assert result.get("module_stderr") is None
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        if isinstance(data_set_names, list):
            for name in data_set_names:
                results2 = hosts.all.zos_data_set(name=name, state="absent")


@pytest.mark.parametrize(
    "filesystem",
    ["hfs", "zfs"],
)
def test_filesystem_create_and_mount(ansible_zos_module, filesystem):
    fulltest = True
    hosts = ansible_zos_module
    default_data_set_name = get_tmp_ds_name(1, 1)
    try:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")

        if filesystem == "hfs":
            result0 = hosts.all.shell(cmd="zinfo -t sys")
            for result in result0.contacted.values():
                sys_info = result.get("stdout_lines")
            product_version = sys_info[4].split()[1].strip("'")
            product_release = sys_info[5].split()[1].strip("'")
            if product_release >= "05" or product_version > "02":
                fulltest = False
                print( "skipping HFS test: zOS > 02.04" )

        if fulltest:
            hosts = ansible_zos_module
            hosts.all.zos_data_set(name=default_data_set_name, state="absent")
            results = hosts.all.zos_data_set(name=default_data_set_name, type=filesystem)
            temp_dir_name = make_tempfile(hosts, directory=True)
            results2 = hosts.all.command(
                cmd="usr/sbin/mount -t {0} -f {1} {2}".format(
                    filesystem, default_data_set_name, temp_dir_name
                )
            )
            results3 = hosts.all.shell(cmd=f"cd {temp_dir_name} ; df .")

            # clean up
            results4 = hosts.all.command(cmd=f"usr/sbin/unmount {temp_dir_name}")
            results5 = hosts.all.zos_data_set(name=default_data_set_name, state="absent")
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
                assert default_data_set_name.upper() in result.get("stdout", "")
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
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


def test_data_set_creation_zero_values(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            state="present",
            type="ksds",
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
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


def test_data_set_creation_with_tmp_hlq(ansible_zos_module):
    try:
        tmphlq = "ANSIBLE"
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        results = hosts.all.zos_data_set(state="present", tmp_hlq=tmphlq)
        dsname = None
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            for dsname in result.get("names"):
                assert dsname[:7] == tmphlq
    finally:
        if dsname:
            hosts.all.zos_data_set(name=default_data_set_name, state="absent")

@pytest.mark.parametrize(
    "formats",
    ["f","fb", "vb", "fba", "vba", "u"],
)
def test_data_set_f_formats(ansible_zos_module, formats, volumes_on_systems):
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    try:
        hosts = ansible_zos_module
        default_data_set_name = get_tmp_ds_name(2, 2)
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
        results = hosts.all.zos_data_set(
            name=default_data_set_name,
            state="present",
            format=formats,
            space_primary="5",
            space_type="m",
            volume=volume_1,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")

"""
GDG base tests:
- Create a new GDG.

- Create a new GDS (src_type: seq, pds, pdse).
- Delete an empty GDG.

"""
@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_gdg_create_and_delete(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        results = hosts.all.zos_data_set(name=data_set_name, state="present", type="gdg", limit=3)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=f"{data_set_name}(+1)", state="present", type=dstype)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=f"{data_set_name}(+1)", state="present", type=dstype)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=f"{data_set_name}(-1)", state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=f"{data_set_name}(0)", state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=data_set_name, state="absent")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent", force=True)


def test_gdg_create_and_delete_force(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        results = hosts.all.zos_data_set(name=data_set_name, state="present", type="gdg", limit=3)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name="{0}(+1)".format(data_set_name), state="present", type="seq")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=data_set_name, state="absent", type="gdg")
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed", False) is True
            assert "DatasetDeleteError" in result.get("msg")
        results = hosts.all.zos_data_set(name=data_set_name, state="absent", force=True, type="gdg")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent", force=True, type="gdg")


def test_gdg_create_and_delete_force(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(2,2, symbols=True)
        data_set_list = ["{0}A".format(data_set_name), "{0}B".format(data_set_name), "{0}C".format(data_set_name)]
        results = hosts.all.zos_data_set(
            batch=[
                {"name":data_set_list[0], "state":"present", "type":"gdg", "limit":3},
                {"name":data_set_list[1], "state":"present", "type":"gdg", "limit":3},
                {"name":data_set_list[2], "state":"present", "type":"gdg", "limit":3},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dls -tGDG 'ANSIBLE.*'")
        for result in results.contacted.values():
            for ds_name in data_set_list:
                assert ds_name in result.get("stdout")
    finally:
        results = hosts.all.shell(cmd=f"drm ANSIBLE.*")


def test_create_special_chars(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(symbols=True)
        results = hosts.all.zos_data_set(name=data_set_name, state="present", type="seq")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dls 'ANSIBLE.*'")
        for result in results.contacted.values():
            assert data_set_name in result.get("stdout")
        results = hosts.all.zos_data_set(name=data_set_name, state="absent",)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_create_member_special_chars(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(symbols=True)
        results = hosts.all.zos_data_set(name=data_set_name, state="present", type="pds")
        results = hosts.all.zos_data_set(name=data_set_name+ "(M@M#R)", state="present", type="member")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dls 'ANSIBLE.*'")
        for result in results.contacted.values():
            assert data_set_name in result.get("stdout")
        results = hosts.all.zos_data_set(name=data_set_name, state="absent",)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_gdg_create_and_replace(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name()
        results = hosts.all.zos_data_set(name=data_set_name, empty=False, force=True, record_format="u", 
                                         record_length=0, replace=True, space_primary=5, space_secondary=3, 
                                         space_type="cyl", state="present", type="gdg", limit=3)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=data_set_name, empty=False, force=True, record_format="u", 
                                         record_length=0, replace=True, space_primary=5, space_secondary=3, 
                                         space_type="cyl", state="present", type="gdg", limit=3)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent", force=True, type="gdg")

def test_gdg_deletion_when_absent(ansible_zos_module):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    results = hosts.all.zos_data_set(name=data_set_name, force=False, record_format="fb", replace=False, 
                                    space_primary=5, space_secondary=3, space_type="m", state="absent", type="gdg")
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("module_stderr") is None
        assert result.get("failed") is None

def test_data_set_delete_with_noscratch(ansible_zos_module, volumes_on_systems):
    """
    Tests that 'state: absent' with 'noscratch: true' correctly uncatalogs
    a data set but leaves its physical entry in the VTOC.
    """
    volumes = Volume_Handler(volumes_on_systems)
    volume = volumes.get_available_vol()
    hosts = ansible_zos_module
    dataset = get_tmp_ds_name(2, 2)

    try:
        # Arrange: Create the test data set on the specific volume
        hosts.all.zos_data_set(
            name=dataset,
            type='seq',
            state='present',
            volumes=[volume],
            space_primary=1,
            space_type='m'
        )

        # Act: Delete the dataset using the noscratch option
        results = hosts.all.zos_data_set(
            name=dataset,
            state='absent',
            noscratch=True
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        # Assert 1: Verify the data set is GONE from the catalog.
        # This is the first part of the test, where we check that the data set
        results = hosts.all.zos_data_set(
            name=dataset,
            state='absent',
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        # catalog_check = hosts.all.command(f"dls '{dataset}'", failed_when=False)
        # for result in catalog_check.contacted.values():
        #     # Assert that the command failed (non-zero return code)
        #     assert result.get("rc") != 0
        # Assert 2: Verify the data set is STILL on the volume's VTOC.
        # This is the crucial second half of the test.
        # We can do this by trying to delete it again, but specifying the volume.
        # If this delete reports "changed: true", it's proof that it found and
        # deleted the uncataloged data set from the VTOC.
        vtoc_check_and_delete = hosts.all.zos_data_set(
            name=dataset,
            state='absent',
            volumes=volume
        )
        for result in vtoc_check_and_delete.contacted.values():
            # This assertion proves the data set existed on the volume's VTOC.
            assert result.get("changed") is True
    finally:
        # Cleanup: Perform a final, full delete from the volume since it's still there.
        # We provide the volume to ensure it can be found and deleted.
        hosts.all.zos_data_set(
            name=dataset,
            state='absent',
            volumes=[volume]
        )

def test_batch_uncatalog_with_noscratch_suboption(ansible_zos_module, volumes_on_systems):
    """
    Tests that the 'noscratch: true' sub-option works correctly when used inside a
    batch list to uncatalog multiple data sets.
    """
    hosts = ansible_zos_module
    volume = Volume_Handler(volumes_on_systems).get_available_vol()
    
    # Define two separate data sets for the batch operation
    dataset_1 = get_tmp_ds_name()
    dataset_2 = get_tmp_ds_name()

    try:
        # --- Arrange ---
        # Create both data sets in a preliminary batch operation so they exist
        setup_results = hosts.all.zos_data_set(
            batch=[
                {'name': dataset_1, 'type': 'seq', 'state': 'present', 'volumes': volume},
                {'name': dataset_2, 'type': 'seq', 'state': 'present', 'volumes': volume}
            ]
        )
        for result in setup_results.contacted.values():
            assert result.get("changed") is True

        # --- Act ---
        # Run the main test: a batch uncatalog where both items use noscratch
        act_results = hosts.all.zos_data_set(
            batch=[
                {'name': dataset_1, 'state': 'absent', 'noscratch': True},
                {'name': dataset_2, 'state': 'absent', 'noscratch': True}
            ]
        )
        # # Assert on the main action results
        for result in act_results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(
            name=dataset_1,
            state='absent',
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        results = hosts.all.zos_data_set(
            name=dataset_2,
            state='absent',
        )
        for result in results.contacted.values():
            assert result.get("changed") is False
        
        # # --- Verification Assertions ---
        # Assert 2: Verify the data set is STILL on the volume's VTOC.
        # This is the crucial second half of the test.
        # We can do this by trying to delete it again, but specifying the volume.
        # If this delete reports "changed: true", it's proof that it found and
        # deleted the uncataloged data set from the VTOC.
        
        vtoc_check_and_delete = hosts.all.zos_data_set(
            name=dataset_1,
            state='absent',
            volumes=volume
        )
        for result in vtoc_check_and_delete.contacted.values():
            # This assertion proves the data set existed on the volume's VTOC
            assert result.get("changed") is True
        
        vtoc_check_and_delete = hosts.all.zos_data_set(
            name=dataset_2,
            state='absent',
            volumes=volume
        )
        for result in vtoc_check_and_delete.contacted.values():
            # This assertion proves the data set existed on the volume's VTOC
            assert result.get("changed") is True
    finally:
        # --- Cleanup ---
        # Ensure both data sets are fully deleted from the volume's VTOC.
        # This is critical because the test's main action leaves them on disk.
        hosts.all.zos_data_set(
            batch=[
                {'name': dataset_1, 'state': 'absent', 'volumes': [volume]},
                {'name': dataset_2, 'state': 'absent', 'volumes': [volume]}
            ]
        )
