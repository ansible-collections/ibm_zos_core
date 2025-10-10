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
from os import path
from shellescape import quote
# pylint: disable-next=import-error
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
import pytest
import re
from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

TMP_DIRECTORY = "/tmp/"
USS_NONE_FILE = "/tmp/none"
SHELL_EXECUTABLE = "/bin/sh"
FROM_ENCODING = "IBM-1047"
INVALID_ENCODING = "EBCDIC"
TO_ENCODING = "ISO8859-1"

TEST_DATA = """0001 This is for encode conversion testing_____________________________________
0002 This is for encode conversion testing_____________________________________
0003 This is for encode conversion testing_____________________________________
0004 This is for encode conversion testing_____________________________________
0005 This is for encode conversion testing_____________________________________
0006 This is for encode conversion testing_____________________________________
"""
TEST_DATA_RECORD_LENGTH = 80
TEST_FILE_TEXT = "HELLO WORLD"

KSDS_CREATE_JCL = """//CREKSDS    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   SET MAXCC=0
   DEFINE CLUSTER                          -
    (NAME({0})                             -
    INDEXED                                -
    KEYS(4 0)                            -
    RECSZ(80 80)                         -
    RECORDS(100)                           -
    SHAREOPTIONS(2 3)                      -
    VOLUMES(000000) )                      -
    DATA (NAME({0}.DATA))                  -
    INDEX (NAME({0}.INDEX))
/*
"""

KSDS_REPRO_JCL = """//DOREPRO    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=E,MSGLEVEL=1,NOTIFY=OMVSADM
//REPROJOB   EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD   *
 REPRO -
  INFILE(SYS01) -
  OUTDATASET({0})
//SYS01    DD *
0001  DUMMY RECORD
0002  DUMMY RECORD ! ! DO NOT ALTER! !
/*
"""

VSAM_RECORDS = """00000001A record
00000002A record
00000003A record
"""

def create_vsam_data_set(hosts, name, ds_type, add_data=False, key_length=None, key_offset=None):
    """Creates a new VSAM on the system.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the VSAM data set.
        type (str) -- Type of the VSAM (KSDS, ESDS, RRDS, LDS)
        add_data (bool, optional) -- Whether to add records to the VSAM.
        key_length (int, optional) -- Key length (only for KSDS data sets).
        key_offset (int, optional) -- Key offset (only for KSDS data sets).
    """
    params = {
        "name":name,
        "type":ds_type,
        "state":"present"
    }
    if ds_type == "ksds":
        params["key_length"] = key_length
        params["key_offset"] = key_offset

    hosts.all.zos_data_set(**params)

    if add_data:
        record_src = "/tmp/zos_copy_vsam_record"

        hosts.all.shell(cmd=f"echo {quote(VSAM_RECORDS)} >> {record_src}")
        hosts.all.zos_encode(
            src=record_src,
            dest=name,
            encoding={"from": "ISO8859-1", "to": "IBM-1047"}
        )
        hosts.all.file(path=record_src, state="absent")

def test_uss_encoding_conversion_with_invalid_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        results = hosts.all.zos_encode(
            src=uss_file,
            encoding={
                "from": INVALID_ENCODING,
                "to": TO_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("msg") is not None
            assert result.get("backup_name") is None
            assert result.get("changed") is False
    finally:
        hosts.all.file(path=uss_file, state="absent")


def test_uss_encoding_conversion_with_the_same_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    hosts.all.copy(content=TEST_DATA, dest=uss_file)
    results = hosts.all.zos_encode(
        src=uss_file,
        encoding={
            "from": FROM_ENCODING,
            "to": FROM_ENCODING,
        },
    )
    for result in results.contacted.values():
        assert result.get("msg") is not None
        assert result.get("backup_name") is None
        assert result.get("changed") is False
    hosts.all.file(path=uss_file, state="absent")


def test_uss_encoding_conversion_without_dest(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        results = hosts.all.zos_encode(
            src=uss_file,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == uss_file
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_file}")
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_file, state="absent")


def test_uss_encoding_conversion_when_dest_not_exists_01(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.file(path=USS_NONE_FILE, state="absent")
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=USS_NONE_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == USS_NONE_FILE
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd=f"ls -T {USS_NONE_FILE}")
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.file(path=USS_NONE_FILE, state="absent")


def test_uss_encoding_conversion_when_dest_not_exists_02(ansible_zos_module):
    hosts = ansible_zos_module
    mvs_ps = get_tmp_ds_name()
    mvs_none_ps = get_tmp_ds_name()
    hosts.all.zos_data_set(name=mvs_ps, state="absent")
    hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
    hosts.all.zos_data_set(name=mvs_none_ps, state="absent")
    results = hosts.all.zos_encode(
        src=mvs_ps,
        dest=mvs_none_ps,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    for result in results.contacted.values():
        assert result.get("src") == mvs_ps
        assert result.get("dest") == mvs_none_ps
        assert result.get("backup_name") is None
        assert result.get("changed") is False
    hosts.all.zos_data_set(name=mvs_ps, state="absent")
    hosts.all.zos_data_set(name=mvs_none_ps, state="absent")


def test_uss_encoding_conversion_uss_file_to_uss_file(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    uss_dest_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.copy(content="test", dest=uss_dest_file)
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=uss_dest_file,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == uss_dest_file
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_file}")
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.file(path=uss_dest_file, state="absent")


def test_uss_encoding_conversion_uss_file_to_uss_path(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    uss_dest_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=uss_dest_path, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=uss_dest_path,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == uss_dest_path
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_path}/{path.basename(uss_file)}")
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.file(path=uss_dest_path, state="absent")


def test_uss_encoding_conversion_uss_path_to_uss_path(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        uss_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        uss_dest_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.file(path=uss_path, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=uss_path + "/encode1")
        hosts.all.copy(content=TEST_DATA, dest=uss_path + "/encode2")
        hosts.all.file(path=uss_dest_path, state="directory")
        results = hosts.all.zos_encode(
            src=uss_path,
            dest=uss_dest_path,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_path
            assert result.get("dest") == uss_dest_path
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_path}")
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
            assert TO_ENCODING not in result.get("stdout")
            assert "untagged" not in result.get("stdout")
    finally:
        hosts.all.file(path=uss_path, state="absent")
        hosts.all.file(path=uss_dest_path, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_ps(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == mvs_ps
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_uss_file(ansible_zos_module):
    uss_dest_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
        hosts.all.zos_copy(content=TEST_DATA, dest=mvs_ps)
        hosts.all.copy(content="test", dest=uss_dest_file)
        results = hosts.all.zos_encode(
            src=mvs_ps,
            dest=uss_dest_file,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == mvs_ps
            assert result.get("dest") == uss_dest_file
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == TO_ENCODING
            assert result.get("encoding").get("from") == FROM_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_file}")
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_dest_file, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_pds(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        results = hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.shell(
            cmd="dtouch -tpds -l {1} {0}".format(mvs_ps, TEST_DATA_RECORD_LENGTH),
        )
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == mvs_ps
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_pds_member(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        mvs_pds_member = mvs_ps + '(MEM)'
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.zos_data_set(
            name=mvs_ps,
            state="present",
            type="pds",
            record_length=TEST_DATA_RECORD_LENGTH
        )
        results = hosts.all.zos_data_set(
            name=mvs_pds_member, type="member", state="present"
        )
        for result in results.contacted.values():
            # documentation will return changed=False if ds exists and replace=False..
            # assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=mvs_pds_member,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == mvs_pds_member
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_mvs_pds_member_to_uss_file(ansible_zos_module):
    uss_dest_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        mvs_pds_member = mvs_ps + '(MEM)'
        hosts.all.zos_data_set(
            name=mvs_ps,
            state="present",
            type="pds",
            record_length=TEST_DATA_RECORD_LENGTH
        )
        hosts.all.zos_data_set(
            name=mvs_pds_member, type="member", state="present"
        )
        hosts.all.zos_copy(content=TEST_DATA, dest=mvs_pds_member)
        hosts.all.copy(content="test", dest=uss_dest_file)
        results = hosts.all.zos_encode(
            src=mvs_pds_member,
            dest=uss_dest_file,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == mvs_pds_member
            assert result.get("dest") == uss_dest_file
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == TO_ENCODING
            assert result.get("encoding").get("from") == FROM_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_file}")
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_dest_file, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_uss_path_to_mvs_pds(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        uss_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        uss_dest_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.file(path=uss_path, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=uss_path + "/encode1")
        hosts.all.copy(content=TEST_DATA, dest=uss_path + "/encode2")
        hosts.all.zos_data_set(
            name=mvs_ps,
            state="present",
            type="pds",
            record_length=TEST_DATA_RECORD_LENGTH
        )
        results = hosts.all.zos_encode(
            src=uss_path,
            dest=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_path
            assert result.get("dest") == mvs_ps
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        hosts.all.file(path=uss_dest_path, state="directory")
        results = hosts.all.zos_encode(
            src=mvs_ps,
            dest=uss_dest_path,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():

            assert result.get("src") == mvs_ps
            assert result.get("dest") == uss_dest_path
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_path}")
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
            assert "untagged" not in result.get("stdout")
    finally:
        hosts.all.file(path=uss_path, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.file(path=uss_dest_path, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_mvs_pds_member(ansible_zos_module):
    hosts = ansible_zos_module
    mvs_ps = get_tmp_ds_name()
    mvs_pds = get_tmp_ds_name()
    mvs_pds_member = mvs_pds + '(MEM)'
    hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
    hosts.all.shell(cmd=f"cp {quote(TEST_DATA)} \"//'{mvs_ps}'\" ")
    hosts.all.zos_data_set(name=mvs_pds, state="present", type="pds")
    hosts.all.zos_data_set(
        name=mvs_pds_member, type="member", state="present"
    )
    results = hosts.all.zos_encode(
        src=mvs_ps,
        dest=mvs_pds_member,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    for result in results.contacted.values():
        assert result.get("src") == mvs_ps
        assert result.get("dest") == mvs_pds_member
        assert result.get("backup_name") is None
        assert result.get("changed") is True
        assert isinstance(result.get("encoding"), dict)
        assert result.get("encoding").get("to") == TO_ENCODING
        assert result.get("encoding").get("from") == FROM_ENCODING
    hosts.all.zos_data_set(name=mvs_ps, state="absent")
    hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_vsam(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mvs_vs = get_tmp_ds_name(3)
        hosts.all.copy(content=TEST_DATA, dest=uss_file)
        hosts.all.file(path=temp_jcl_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(KSDS_CREATE_JCL.format(mvs_vs))} > {temp_jcl_path}/SAMPLE"
        )
        results = hosts.all.zos_job_submit(
            src=f"{temp_jcl_path}/SAMPLE", remote_src=True, wait_time=30
        )

        for result in results.contacted.values():
            print(result)
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
        results = hosts.all.zos_encode(
            src=uss_file,
            dest=mvs_vs,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == uss_file
            assert result.get("dest") == mvs_vs
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.zos_data_set(name=mvs_vs, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_uss_file(ansible_zos_module):
    uss_dest_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        mlq_size = 3
        mvs_vs = get_tmp_ds_name(mlq_size)
        create_vsam_data_set(hosts, mvs_vs, "ksds", add_data=True, key_length=12, key_offset=0)
        hosts.all.file(path=uss_dest_file, state="touch")
        results = hosts.all.zos_encode(
            src=mvs_vs,
            dest=uss_dest_file,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == mvs_vs
            assert result.get("dest") == uss_dest_file
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == TO_ENCODING
            assert result.get("encoding").get("from") == FROM_ENCODING

        tag_results = hosts.all.shell(cmd=f"ls -T {uss_dest_file}")
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_dest_file, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=mvs_vs, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_mvs_ps(ansible_zos_module):
    hosts = ansible_zos_module
    mvs_ps = get_tmp_ds_name()
    mvs_vs = get_tmp_ds_name()
    create_vsam_data_set(hosts, mvs_vs, "ksds", add_data=True, key_length=12, key_offset=0)
    hosts.all.zos_data_set(name=mvs_ps, state="absent")
    hosts.all.zos_data_set(
        name=mvs_ps,
        state="present",
        type="seq",
        record_length=TEST_DATA_RECORD_LENGTH
    )
    results = hosts.all.zos_encode(
        src=mvs_vs,
        dest=mvs_ps,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    for result in results.contacted.values():
        assert result.get("src") == mvs_vs
        assert result.get("dest") == mvs_ps
        assert result.get("backup_name") is None
        assert result.get("changed") is True
        assert isinstance(result.get("encoding"), dict)
        assert result.get("encoding").get("to") == TO_ENCODING
        assert result.get("encoding").get("from") == FROM_ENCODING

    hosts.all.zos_data_set(name=mvs_vs, state="absent")
    hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_mvs_pds_member(ansible_zos_module):
    hosts = ansible_zos_module
    mvs_vs = get_tmp_ds_name()
    mvs_ps = get_tmp_ds_name()
    create_vsam_data_set(hosts, mvs_vs, "ksds", add_data=True, key_length=12, key_offset=0)
    mvs_pds_member = mvs_ps + '(MEM)'
    hosts.all.zos_data_set(
        name=mvs_ps,
        state="present",
        type="pds",
        record_length=TEST_DATA_RECORD_LENGTH
    )
    hosts.all.zos_data_set(
        name=mvs_pds_member, type="member", state="present"
    )
    results = hosts.all.zos_encode(
        src=mvs_vs,
        dest=mvs_pds_member,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    hosts.all.zos_data_set(name=mvs_ps, state="absent")
    for result in results.contacted.values():
        assert result.get("src") == mvs_vs
        assert result.get("dest") == mvs_pds_member
        assert result.get("backup_name") is None
        assert result.get("changed") is True
        assert result.get("encoding") is not None
        assert isinstance(result.get("encoding"), dict)
        assert result.get("encoding").get("to") == TO_ENCODING
        assert result.get("encoding").get("from") == FROM_ENCODING
    hosts.all.zos_data_set(name=mvs_vs, state="absent")
    hosts.all.zos_data_set(name=mvs_ps, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_mvs_vsam(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_vs = get_tmp_ds_name(3)
        mvs_ps = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
        hosts.all.file(path=temp_jcl_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(KSDS_CREATE_JCL.format(mvs_vs))} > {temp_jcl_path}/SAMPLE"
        )
        results = hosts.all.zos_job_submit(
            src=f"{temp_jcl_path}/SAMPLE", remote_src=True, wait_time=30
        )
        for result in results.contacted.values():
            assert result.get("jobs") is not None
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
        #hosts.all.zos_copy(content=TEST_DATA, dest=MVS_PS)
        results = hosts.all.zos_encode(
            src=mvs_ps,
            dest=mvs_vs,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == mvs_ps
            assert result.get("dest") == mvs_vs
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_vs, state="absent")


def test_uss_encoding_conversion_src_with_special_chars(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src_data_set = get_tmp_ds_name(symbols=True)
        hosts.all.zos_data_set(name=src_data_set, state="present", type="seq")

        results = hosts.all.zos_encode(
            src=src_data_set,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        for result in results.contacted.values():
            assert result.get("src") == src_data_set
            assert result.get("dest") == src_data_set
            assert result.get("backup_name") is None
            assert result.get("changed") is True
            assert result.get("msg") is None
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == TO_ENCODING
            assert result.get("encoding").get("from") == FROM_ENCODING

    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")


def test_pds_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="pds")
        hosts.all.shell(cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE)'\"")
        hosts.all.zos_encode(
            src=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=backup_data_set,
        )
        contents = hosts.all.shell(cmd=f"cat \"//'{backup_data_set}(SAMPLE)'\"")
        for content in contents.contacted.values():
            # pprint(content)
            assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")


def test_pds_backup_with_tmp_hlq_option(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        tmphlq = "TMPHLQ"
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="pds")
        hosts.all.shell(cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE)'\"")
        encode_res = hosts.all.zos_encode(
            src=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            tmp_hlq=tmphlq,
        )
        for enc_res in encode_res.contacted.values():
            assert enc_res.get("backup_name")[:6] == tmphlq
            assert enc_res.get("encoding") is not None
            assert isinstance(enc_res.get("encoding"), dict)
            assert enc_res.get("encoding").get("to") == FROM_ENCODING
            assert enc_res.get("encoding").get("from") == TO_ENCODING
            contents = hosts.all.shell(cmd="cat \"//'{0}(SAMPLE)'\"".format(enc_res.get("backup_name")))
            hosts.all.file(path=temp_jcl_path, state="absent")
            hosts.all.zos_data_set(name=mvs_ps, state="absent")
            hosts.all.zos_data_set(name=backup_data_set, state="absent")
            for content in contents.contacted.values():
                # pprint(content)
                assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")


def test_ps_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
        hosts.all.shell(cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}'\"")
        hosts.all.zos_encode(
            src=mvs_ps,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=backup_data_set,
        )
        contents = hosts.all.shell(cmd=f"cat \"//'{backup_data_set}'\"")
        for content in contents.contacted.values():
            assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")


def test_vsam_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        backup_data_set = get_tmp_ds_name()
        mvs_vs = get_tmp_ds_name()
        mvs_ps = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.zos_data_set(name=mvs_vs, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(
            name=mvs_ps, state="present", record_length=TEST_DATA_RECORD_LENGTH, type="seq"
        )
        hosts.all.file(path=temp_jcl_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(KSDS_CREATE_JCL.format(mvs_vs))} > {temp_jcl_path}/SAMPLE"
        )
        hosts.all.zos_job_submit(
            src=f"{temp_jcl_path}/SAMPLE", remote_src=True, wait_time=30
        )
        hosts.all.file(path=temp_jcl_path, state="absent")
        # submit JCL to populate KSDS
        hosts.all.file(path=temp_jcl_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(KSDS_REPRO_JCL.format(mvs_vs.upper()))} > {temp_jcl_path}/SAMPLE"
        )
        hosts.all.zos_job_submit(
            src=f"{temp_jcl_path}/SAMPLE", remote_src=True, wait_time=30
        )

        hosts.all.zos_encode(
            src=mvs_vs,
            dest=mvs_ps,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        hosts.all.zos_encode(
            src=mvs_vs,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=backup_data_set,
        )
        hosts.all.zos_data_set(
            name=mvs_ps, state="present", record_length=TEST_DATA_RECORD_LENGTH, type="seq"
        )
        hosts.all.zos_encode(
            src=backup_data_set,
            dest=mvs_ps,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
    finally:
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_vs, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.file(path=temp_jcl_path, state="absent")


def test_uss_backup_entire_folder_to_default_backup_location(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        # create and fill PDS
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="pds")
        hosts.all.shell(cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE)'\"")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE2)'\"")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE3)'\"")
        # create and fill directory
        hosts.all.file(path=temp_jcl_path + "2", state="absent")
        hosts.all.file(path=temp_jcl_path + "2", state="directory")
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file1"
        )
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file2"
        )
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file3"
        )
        results = hosts.all.zos_encode(
            src=mvs_ps,
            dest=temp_jcl_path + "2",
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
        )
        backup_name = None
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING
        assert backup_name
        contents = hosts.all.shell(cmd=f"cat {backup_name}file1")
        content1 = ""
        for content in contents.contacted.values():
            content1 = content.get("stdout")
        contents = hosts.all.shell(cmd=f"cat {backup_name}file2")
        content2 = ""
        for content in contents.contacted.values():
            content2 = content.get("stdout")
        contents = hosts.all.shell(cmd=f"cat {backup_name}file3")
        content3 = ""
        for content in contents.contacted.values():
            content3 = content.get("stdout")
        assert (
            content1
            and content1 == content2
            and content2 == content3
            and content1 == TEST_FILE_TEXT
        )
    finally:
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.file(path=temp_jcl_path + "2", state="absent")
        hosts.all.file(path=backup_name, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")


def test_uss_backup_entire_folder_to_default_backup_location_compressed(
    ansible_zos_module
):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        # create and fill PDS
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="pds")
        hosts.all.shell(cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE)'\"")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE2)'\"")
        hosts.all.shell(cmd=f"cp {temp_jcl_path} \"//'{mvs_ps}(SAMPLE3)'\"")
        # create and fill directory
        hosts.all.file(path=temp_jcl_path + "2", state="absent")
        hosts.all.file(path=temp_jcl_path + "2", state="directory")
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file1"
        )
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file2"
        )
        hosts.all.shell(
            cmd=f"echo '{TEST_FILE_TEXT}' > {temp_jcl_path}2/file3"
        )
        results = hosts.all.zos_encode(
            src=mvs_ps,
            dest=temp_jcl_path + "2",
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_compress=True,
        )
        backup_name = None
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == FROM_ENCODING
            assert result.get("encoding").get("from") == TO_ENCODING

        results = hosts.all.shell(cmd=f"ls -la {backup_name[:-4]}*")
        for result in results.contacted.values():
            assert backup_name in result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.file(path=temp_jcl_path, state="absent")
        hosts.all.file(path=temp_jcl_path + "2", state="absent")
        hosts.all.file(path=backup_name, state="absent")


def test_return_backup_name_on_module_success_and_failure(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mvs_ps = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        hosts.all.zos_data_set(name=mvs_ps, state="present", type="seq")
        hosts.all.shell(cmd=f"decho \"{TEST_FILE_TEXT}\" \"{mvs_ps}\"")
        enc_ds = hosts.all.zos_encode(
            src=mvs_ps,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=backup_data_set,
        )
        for content in enc_ds.contacted.values():
            assert content.get("backup_name") is not None
            assert content.get("backup_name") == backup_data_set
            assert content.get("encoding") is not None
            assert isinstance(content.get("encoding"), dict)
            assert content.get("encoding").get("to") == TO_ENCODING
            assert content.get("encoding").get("from") == FROM_ENCODING

        hosts.all.zos_data_set(name=backup_data_set, state="absent")
        enc_ds = hosts.all.zos_encode(
            src=mvs_ps,
            encoding={
                "from": INVALID_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=backup_data_set,
        )

        for content in enc_ds.contacted.values():
            assert content.get("msg") is not None
            assert content.get("backup_name") is not None
            assert content.get("backup_name") == backup_data_set
            assert content.get("encoding") is not None
            assert isinstance(content.get("encoding"), dict)
            assert content.get("encoding").get("to") == TO_ENCODING
            assert content.get("encoding").get("from") == INVALID_ENCODING
    finally:
        hosts.all.zos_data_set(name=mvs_ps, state="absent")
        hosts.all.zos_data_set(name=backup_data_set, state="absent")


@pytest.mark.parametrize("generation", ["-1", "+1"])
def test_gdg_encoding_conversion_src_with_invalid_generation(ansible_zos_module, generation):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name(3, 2)

    try:
        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {ds_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{ds_name}(+1)" """)

        results = hosts.all.zos_encode(
            src=f"{ds_name}({generation})",
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        for result in results.contacted.values():
            assert result.get("msg") is not None
            assert "not cataloged" in result.get("msg")
            assert result.get("backup_name") is None
            assert result.get("changed") is False
            assert result.get("encoding") is not None
            assert isinstance(result.get("encoding"), dict)
            assert result.get("encoding").get("to") == TO_ENCODING
            assert result.get("encoding").get("from") == FROM_ENCODING
    finally:
        hosts.all.shell(cmd=f"""drm "{ds_name}(0)" """)
        hosts.all.shell(cmd=f"drm {ds_name}")


def test_gdg_encoding_conversion_invalid_gdg(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name(3, 2)

    try:
        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {ds_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{ds_name}(+1)" """)

        results = hosts.all.zos_encode(
            src=ds_name,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        for result in results.contacted.values():
            assert result.get("msg") is not None
            assert "Encoding of a whole generation data group is not supported." in result.get("msg")
            assert result.get("backup_name") is None
            assert result.get("changed") is False
            assert result.get("failed") is True
    finally:
        hosts.all.shell(cmd=f"""drm "{ds_name}(0)" """)
        hosts.all.shell(cmd=f"drm {ds_name}")


def test_encoding_conversion_gds_to_uss_file(ansible_zos_module):
    uss_dest_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        ds_name = get_tmp_ds_name()
        gds_name = f"{ds_name}(0)"

        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {ds_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{ds_name}(+1)" """)

        hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{gds_name}\"")

        results = hosts.all.zos_encode(
            src=gds_name,
            dest=uss_dest_file,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            }
        )

        # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
        gds_pattern = r"G[0-9]+V[0-9]+"

        for result in results.contacted.values():
            src = result.get("src", "")
            assert ds_name in src
            assert re.fullmatch(gds_pattern, src.split(".")[-1])

            assert result.get("dest") == uss_dest_file
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(uss_dest_file))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=uss_dest_file, state="absent")
        hosts.all.shell(cmd=f"""drm "{ds_name}(0)" """)
        hosts.all.shell(cmd=f"drm {ds_name}")


def test_encoding_conversion_gds_no_dest(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        ds_name = get_tmp_ds_name()
        gds_name = f"{ds_name}(0)"

        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {ds_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{ds_name}(+1)" """)
        hosts.all.shell(cmd=f"decho \"{TEST_DATA}\"  \"{gds_name}\"")

        results = hosts.all.zos_encode(
            src=gds_name,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            }
        )

        dest_existence_check = hosts.all.shell(
            cmd=f"""dcat "{gds_name}" | wc -l """,
            executable=SHELL_EXECUTABLE
        )

        # Checking that we got a dest of the form: ANSIBLE.DATA.SET.G0001V01.
        gds_pattern = r"G[0-9]+V[0-9]+"

        for result in results.contacted.values():
            src = result.get("src", "")
            dest = result.get("dest", "")

            assert ds_name in src
            assert re.fullmatch(gds_pattern, src.split(".")[-1])
            assert src == dest

            assert result.get("changed") is True

        for result in dest_existence_check.contacted.values():
            assert result.get("rc") == 0
            assert int(result.get("stdout")) > 0

    finally:
        hosts.all.shell(cmd=f"""drm "{gds_name}" """)
        hosts.all.shell(cmd=f"drm {ds_name}")


def test_encoding_conversion_uss_file_to_gds(ansible_zos_module):
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='EN')
    try:
        hosts = ansible_zos_module
        ds_name = get_tmp_ds_name()
        gds_name = f"{ds_name}(0)"

        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {ds_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{ds_name}(+1)" """)

        hosts.all.shell(cmd=f"echo \"{TEST_DATA}\" > {uss_file}")

        results = hosts.all.zos_encode(
            src=uss_file,
            dest=gds_name,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            }
        )

        dest_existence_check = hosts.all.shell(
            cmd=f"""dcat "{gds_name}" | wc -l """,
            executable=SHELL_EXECUTABLE
        )

        # Checking that we got a dest of the form: ANSIBLE.DATA.SET.G0001V01.
        gds_pattern = r"G[0-9]+V[0-9]+"

        for result in results.contacted.values():
            dest = result.get("dest", "")
            assert ds_name in dest
            assert re.fullmatch(gds_pattern, dest.split(".")[-1])

            assert result.get("src") == uss_file
            assert result.get("changed") is True

        for result in dest_existence_check.contacted.values():
            assert result.get("rc") == 0
            assert int(result.get("stdout")) > 0

    finally:
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.shell(cmd=f"""drm "{gds_name}" """)
        hosts.all.shell(cmd=f"drm {ds_name}")


def test_encoding_conversion_gds_to_mvs(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        src_name = get_tmp_ds_name()
        dest_name = get_tmp_ds_name()
        gds_name = f"{src_name}(0)"

        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_name}")
        hosts.all.shell(cmd=f"""dtouch -tseq "{src_name}(+1)" """)
        hosts.all.shell(cmd=f"dtouch -tseq {dest_name}")

        hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{gds_name}\"")

        results = hosts.all.zos_encode(
            src=gds_name,
            dest=dest_name,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            }
        )

        dest_existence_check = hosts.all.shell(
            cmd=f"""dcat "{dest_name}" | wc -l """,
            executable=SHELL_EXECUTABLE
        )

        # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
        gds_pattern = r"G[0-9]+V[0-9]+"

        for result in results.contacted.values():
            src = result.get("src", "")
            assert src_name in src
            assert re.fullmatch(gds_pattern, src.split(".")[-1])

            assert result.get("dest") == dest_name
            assert result.get("changed") is True

        for result in dest_existence_check.contacted.values():
            assert result.get("rc") == 0
            assert int(result.get("stdout")) > 0
    finally:
        hosts.all.shell(cmd=f"""drm "{src_name}(0)" """)
        hosts.all.shell(cmd=f"drm {src_name}")
        hosts.all.shell(cmd=f"drm {dest_name}")


def test_gds_encoding_conversion_when_gds_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        src = get_tmp_ds_name()
        gdg_name = get_tmp_ds_name()
        dest = f"{gdg_name}(+1)"

        hosts.all.shell(cmd=f"dtouch -tSEQ {src}")
        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {gdg_name}")

        results = hosts.all.zos_encode(
            src=src,
            dest=dest,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        for result in results.contacted.values():
            assert result.get("src") == src
            assert result.get("dest") == dest
            assert result.get("backup_name") is None
            assert result.get("changed") is False
            assert result.get("failed") is True
            assert "not cataloged" in result.get("msg", "")
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=gdg_name, state="absent")


def test_gds_backup(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src_data_set = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()

        hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {backup_data_set}")
        hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{src_data_set}\"")

        results = hosts.all.zos_encode(
            src=src_data_set,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=f"{backup_data_set}(+1)",
        )

        backup_check = hosts.all.shell(
            cmd=f"""dcat "{backup_data_set}(0)" | wc -l """
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg") is None

        for result in backup_check.contacted.values():
            assert result.get("rc") == 0
            assert int(result.get("stdout")) > 0

    finally:
        hosts.all.shell(cmd=f"""drm "{backup_data_set}(0)" """)
        hosts.all.shell(cmd=f"drm {backup_data_set}")
        hosts.all.shell(cmd=f"drm {src_data_set}")


def test_gds_backup_invalid_generation(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src_data_set = get_tmp_ds_name()
        backup_data_set = get_tmp_ds_name()

        hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
        hosts.all.shell(cmd=f"dtouch -tGDG -L3 {backup_data_set}")
        hosts.all.shell(cmd=f"""dtouch -tSEQ "{backup_data_set}(+1)" """)
        hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{src_data_set}\"")

        results = hosts.all.zos_encode(
            src=src_data_set,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=f"{backup_data_set}(0)",
        )

        for result in results.contacted.values():
            assert result.get("failed") is True
            assert result.get("changed") is False
            assert result.get("msg") is not None
            assert "cannot be used" in result.get("msg")

    finally:
        hosts.all.shell(cmd=f"""drm "{backup_data_set}(0)" """)
        hosts.all.shell(cmd=f"drm {backup_data_set}")
        hosts.all.shell(cmd=f"drm {src_data_set}")
