# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from pipes import quote

# TODO: determine if data set names need to be more generic for testcases
# TODO: add additional tests to check additional data set creation parameter combinations

data_set_types = [
    ("pds"),
    ("seq"),
    ("pdse"),
    ("esds"),
    ("rrds"),
    ("lds"),
    (None),
]

DEFAULT_VOLUME = "000000"
DEFAULT_VOLUME2 = "222222"
DEFAULT_DATA_SET_NAME = "USER.PRIVATE.TESTDS"
DEFAULT_DATA_SET_NAME_WITH_MEMBER = "USER.PRIVATE.TESTDS(TESTME)"
TEMP_PATH = "/tmp/ansible/jcl"

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
    hosts.all.file(path=TEMP_PATH, state="absent")
    # verify data set creation was successful
    for result in results.contacted.values():
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
    # clean up
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_present_when_uncataloged(ansible_zos_module, jcl):
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
    hosts.all.file(path=TEMP_PATH, state="absent")
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_replacement_when_uncataloged(ansible_zos_module, jcl):
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
    hosts.all.file(path=TEMP_PATH, state="absent")
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize(
    "jcl",
    [PDS_CREATE_JCL, KSDS_CREATE_JCL, RRDS_CREATE_JCL, ESDS_CREATE_JCL, LDS_CREATE_JCL],
)
def test_data_set_absent_when_uncataloged(ansible_zos_module, jcl):
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
    hosts.all.file(path=TEMP_PATH, state="absent")
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_no_replace(ansible_zos_module, dstype):
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


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_present_replace(ansible_zos_module, dstype):
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


@pytest.mark.parametrize("dstype", data_set_types)
def test_data_set_creation_when_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET_NAME, state="present", type=dstype
    )
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("module_stderr") is None


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


def test_batch_data_set_and_member_creation(ansible_zos_module):
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


def test_repeated_operations(ansible_zos_module):
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

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME_WITH_MEMBER, type="MEMBER")

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


def test_multi_volume_creation_uncatalog_and_catalog_nonvsam(ansible_zos_module):
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_multi_volume_creation_uncatalog_and_catalog_vsam(ansible_zos_module):
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


def test_data_set_old_aliases(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET_NAME,
        state="present",
        format="fb",
        size="5m",
        volume=DEFAULT_VOLUME,
    )
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("module_stderr") is None


def test_data_set_temp_data_set_name(ansible_zos_module):
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


def test_data_set_temp_data_set_name_batch(ansible_zos_module):
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


def test_data_set_creation_zero_values(ansible_zos_module):
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
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("module_stderr") is None
