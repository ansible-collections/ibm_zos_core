# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2022
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
from shellescape import quote
from pprint import pprint
from os import path
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

__metaclass__ = type

USS_FILE = "/tmp/encode_data"
USS_NONE_FILE = "/tmp/none"
USS_DEST_FILE = "/tmp/converted_data"
USS_PATH = "/tmp/src"
USS_DEST_PATH = "/tmp/dest"
MVS_PS = "encode.ps"
MVS_NONE_PS = "encode.none.ps"
MVS_PDS = "encode.pds"
MVS_PDS_MEMBER = "encode.pds(test)"
MVS_VS = "encode.test.vs"
FROM_ENCODING = "IBM-1047"
INVALID_ENCODING = "EBCDIC"
TO_ENCODING = "ISO8859-1"
TEMP_JCL_PATH = "/tmp/jcl"
TEST_DATA = """0001 This is for encode conversion testing_____________________________________
0002 This is for encode conversion testing_____________________________________
0003 This is for encode conversion testing_____________________________________
0004 This is for encode conversion testing_____________________________________
0005 This is for encode conversion testing_____________________________________
0006 This is for encode conversion testing_____________________________________
"""
TEST_DATA_RECORD_LENGTH = 80
TEST_FILE_TEXT = "HELLO world"
BACKUP_DATA_SET = "USER.PRIVATE.BACK"

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
    params = dict(
        name=name,
        type=ds_type,
        state="present"
    )
    if ds_type == "KSDS":
        params["key_length"] = key_length
        params["key_offset"] = key_offset

    hosts.all.zos_data_set(**params)

    if add_data:
        record_src = "/tmp/zos_copy_vsam_record"

        hosts.all.shell(cmd="cp -CM {0} \"//'{1}'\" ").format(VSAM_RECORDS, record_src)
        hosts.all.zos_encode(src=record_src, dest=name, encoding={"from": "ISO8859-1", "to": "IBM-1047"})
        hosts.all.file(path=record_src, state="absent")

def test_uss_encoding_conversion_with_invalid_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        results = hosts.all.zos_encode(
            src=USS_FILE,
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
        hosts.all.file(path=USS_FILE, state="absent")


def test_uss_encoding_conversion_with_the_same_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
    results = hosts.all.zos_encode(
        src=USS_FILE,
        encoding={
            "from": FROM_ENCODING,
            "to": FROM_ENCODING,
        },
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("msg") is not None
        assert result.get("backup_name") is None
        assert result.get("changed") is False
    hosts.all.file(path=USS_FILE, state="absent")


def test_uss_encoding_conversion_without_dest(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        results = hosts.all.zos_encode(
            src=USS_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == USS_FILE
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_FILE))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_FILE, state="absent")


def test_uss_encoding_conversion_when_dest_not_exists_01(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.file(path=USS_NONE_FILE, state="absent")
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=USS_NONE_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == USS_NONE_FILE
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_NONE_FILE))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.file(path=USS_NONE_FILE, state="absent")


def test_uss_encoding_conversion_when_dest_not_exists_02(ansible_zos_module):
    hosts = ansible_zos_module
    MVS_PS = get_tmp_ds_name()
    MVS_NONE_PS = get_tmp_ds_name()
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
    hosts.all.zos_data_set(name=MVS_NONE_PS, state="absent")
    results = hosts.all.zos_encode(
        src=MVS_PS,
        dest=MVS_NONE_PS,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("src") == MVS_PS
        assert result.get("dest") == MVS_NONE_PS
        assert result.get("backup_name") is None
        assert result.get("changed") is False
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=MVS_NONE_PS, state="absent")


def test_uss_encoding_conversion_uss_file_to_uss_file(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.copy(content="test", dest=USS_DEST_FILE)
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=USS_DEST_FILE,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == USS_DEST_FILE
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_FILE))
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.file(path=USS_DEST_FILE, state="absent")


def test_uss_encoding_conversion_uss_file_to_uss_path(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=USS_DEST_PATH, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=USS_DEST_PATH,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == USS_DEST_PATH
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}/{1}".format(USS_DEST_PATH, path.basename(USS_FILE)))
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.file(path=USS_DEST_PATH, state="absent")


def test_uss_encoding_conversion_uss_path_to_uss_path(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=USS_PATH, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode1")
        hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode2")
        hosts.all.file(path=USS_DEST_PATH, state="directory")
        results = hosts.all.zos_encode(
            src=USS_PATH,
            dest=USS_DEST_PATH,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_PATH
            assert result.get("dest") == USS_DEST_PATH
            assert result.get("backup_name") is not None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_PATH))
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
            assert TO_ENCODING not in result.get("stdout")
            assert "untagged" not in result.get("stdout")
    finally:
        hosts.all.file(path=USS_PATH, state="absent")
        hosts.all.file(path=USS_DEST_PATH, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_ps(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PS = get_tmp_ds_name()
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=MVS_PS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == MVS_PS
            assert result.get("backup_name") is None
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_uss_file(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
        hosts.all.copy(content=TEST_DATA, dest=MVS_PS)
        hosts.all.copy(content="test", dest=USS_DEST_FILE)
        results = hosts.all.zos_encode(
            src=MVS_PS,
            dest=USS_DEST_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == MVS_PS
            assert result.get("dest") == USS_DEST_FILE
            assert result.get("backup_name") is not None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_FILE))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_DEST_FILE, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_pds(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=TEST_DATA_RECORD_LENGTH)
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=MVS_PDS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == MVS_PDS
            assert result.get("backup_name") is None
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")


def test_uss_encoding_conversion_uss_file_to_mvs_pds_member(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        MVS_PDS_MEMBER = MVS_PDS + '(MEM)'
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=TEST_DATA_RECORD_LENGTH)
        results = hosts.all.zos_data_set(
            name=MVS_PDS_MEMBER, type="member", state="present"
        )
        for result in results.contacted.values():
            # documentation will return changed=False if ds exists and replace=False..
            # assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=MVS_PDS_MEMBER,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == MVS_PDS_MEMBER
            assert result.get("backup_name") is None
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")


def test_uss_encoding_conversion_mvs_pds_member_to_uss_file(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        MVS_PDS_MEMBER = MVS_PDS + '(MEM)'
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=TEST_DATA_RECORD_LENGTH)
        hosts.all.zos_data_set(
            name=MVS_PDS_MEMBER, type="member", state="present"
        )
        hosts.all.copy(content=TEST_DATA, dest=MVS_PDS_MEMBER)
        hosts.all.copy(content="test", dest=USS_DEST_FILE)
        results = hosts.all.zos_encode(
            src=MVS_PDS_MEMBER,
            dest=USS_DEST_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == MVS_PDS_MEMBER
            assert result.get("dest") == USS_DEST_FILE
            assert result.get("backup_name") is not None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_FILE))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_DEST_FILE, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")


def test_uss_encoding_conversion_uss_path_to_mvs_pds(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        hosts.all.file(path=USS_PATH, state="directory")
        hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode1")
        hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode2")
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=TEST_DATA_RECORD_LENGTH)
        results = hosts.all.zos_encode(
            src=USS_PATH,
            dest=MVS_PDS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_PATH
            assert result.get("dest") == MVS_PDS
            assert result.get("backup_name") is None
            assert result.get("changed") is True
        hosts.all.file(path=USS_DEST_PATH, state="directory")
        results = hosts.all.zos_encode(
            src=MVS_PDS,
            dest=USS_DEST_PATH,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():

            assert result.get("src") == MVS_PDS
            assert result.get("dest") == USS_DEST_PATH
            assert result.get("backup_name") is None
            assert result.get("changed") is True

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_PATH))
        for result in tag_results.contacted.values():
            assert FROM_ENCODING in result.get("stdout")
            assert "untagged" not in result.get("stdout")
    finally:
        hosts.all.file(path=USS_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.file(path=USS_DEST_PATH, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_mvs_pds_member(ansible_zos_module):
    hosts = ansible_zos_module
    MVS_PDS = get_tmp_ds_name()
    MVS_PDS_MEMBER = MVS_PDS + '(MEM)'
    MVS_PS = get_tmp_ds_name()
    hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
    hosts.all.shell(cmd="cp {0} \"//'{1}'\" ".format(quote(TEST_DATA), MVS_PS))
    hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
    hosts.all.zos_data_set(
        name=MVS_PDS_MEMBER, type="member", state="present"
    )
    results = hosts.all.zos_encode(
        src=MVS_PS,
        dest=MVS_PDS_MEMBER,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    for result in results.contacted.values():
        print(result)
        assert result.get("src") == MVS_PS
        assert result.get("dest") == MVS_PDS_MEMBER
        assert result.get("backup_name") is None
        assert result.get("changed") is True
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=MVS_PDS, state="absent")

def test_uss_encoding_conversion_uss_file_to_mvs_vsam(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_VS = get_tmp_ds_name(3)
        hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.file(path=TEMP_JCL_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL.format(MVS_VS)), TEMP_JCL_PATH)
        )
        results = hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
        )

        for result in results.contacted.values():
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
        results = hosts.all.zos_encode(
            src=USS_FILE,
            dest=MVS_VS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == USS_FILE
            assert result.get("dest") == MVS_VS
            assert result.get("backup_name") is None
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.zos_data_set(name=MVS_VS, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_uss_file(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        mlq_size = 3
        MVS_VS = get_tmp_ds_name(mlq_size)
        create_vsam_data_set(hosts, MVS_VS, "KSDS", add_data=True, key_length=12, key_offset=0)
        hosts.all.file(path=USS_DEST_FILE, state="touch")
        results = hosts.all.zos_encode(
            src=MVS_VS,
            dest=USS_DEST_FILE,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
        )
        for result in results.contacted.values():
            assert result.get("src") == MVS_VS
            assert result.get("dest") == USS_DEST_FILE
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            # How can we add a content validation without having to encode again ?
            # cat_result = hosts.all.shell(cmd="iconv -f {0} -t {1} {2}".format(TO_ENCODING, FROM_ENCODING, USS_DEST_FILE))
            # print(cat_result.contacted.values())
            # for uss_file_result in cat_result.contacted.values():
            #     assert TEST_DATA in uss_file_result.get("stdout")

        tag_results = hosts.all.shell(cmd="ls -T {0}".format(USS_DEST_FILE))
        for result in tag_results.contacted.values():
            assert TO_ENCODING in result.get("stdout")
    finally:
        hosts.all.file(path=USS_DEST_FILE, state="absent")
        hosts.all.file(path=result.get("backup_name"), state="absent")
        hosts.all.zos_data_set(name=MVS_VS, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_mvs_ps(ansible_zos_module):
    hosts = ansible_zos_module
    MVS_PS = get_tmp_ds_name()
    MVS_VS = get_tmp_ds_name()
    create_vsam_data_set(hosts, MVS_VS, "KSDS", add_data=True, key_length=12, key_offset=0)
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq", record_length=TEST_DATA_RECORD_LENGTH)
    results = hosts.all.zos_encode(
        src=MVS_VS,
        dest=MVS_PS,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    for result in results.contacted.values():
        assert result.get("src") == MVS_VS
        assert result.get("dest") == MVS_PS
        assert result.get("backup_name") is None
        assert result.get("changed") is True
    hosts.all.zos_data_set(name=MVS_VS, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="absent")


def test_uss_encoding_conversion_mvs_vsam_to_mvs_pds_member(ansible_zos_module):
    hosts = ansible_zos_module
    MVS_VS = get_tmp_ds_name()
    MVS_PDS = get_tmp_ds_name()
    create_vsam_data_set(hosts, MVS_VS, "KSDS", add_data=True, key_length=12, key_offset=0)
    MVS_PDS_MEMBER = MVS_PDS + '(MEM)'
    hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=TEST_DATA_RECORD_LENGTH)
    hosts.all.zos_data_set(
        name=MVS_PDS_MEMBER, type="member", state="present"
    )
    results = hosts.all.zos_encode(
        src=MVS_VS,
        dest=MVS_PDS_MEMBER,
        encoding={
            "from": FROM_ENCODING,
            "to": TO_ENCODING,
        },
    )
    hosts.all.zos_data_set(name=MVS_PDS, state="absent")
    for result in results.contacted.values():
        print(result)
        assert result.get("src") == MVS_VS
        assert result.get("dest") == MVS_PDS_MEMBER
        assert result.get("backup_name") is None
        assert result.get("changed") is True
    hosts.all.zos_data_set(name=MVS_VS, state="absent")
    hosts.all.zos_data_set(name=MVS_PDS, state="absent")


def test_uss_encoding_conversion_mvs_ps_to_mvs_vsam(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_VS = get_tmp_ds_name(3)
        MVS_PS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
        hosts.all.file(path=TEMP_JCL_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL.format(MVS_VS)), TEMP_JCL_PATH)
        )
        results = hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
        )
        for result in results.contacted.values():
            assert result.get("jobs") is not None
            assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
            assert result.get("jobs")[0].get("ret_code").get("code") == 0
            assert result.get("changed") is True
        #hosts.all.zos_copy(content=TEST_DATA, dest=MVS_PS)
        results = hosts.all.zos_encode(
            src=MVS_PS,
            dest=MVS_VS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
        )
        for result in results.contacted.values():
            assert result.get("src") == MVS_PS
            assert result.get("dest") == MVS_VS
            assert result.get("backup_name") is None
            assert result.get("changed") is True
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=MVS_VS, state="absent")


def test_pds_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        hosts.all.zos_encode(
            src=MVS_PDS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=BACKUP_DATA_SET,
        )
        contents = hosts.all.shell(cmd="cat \"//'{0}(SAMPLE)'\"".format(BACKUP_DATA_SET))
        for content in contents.contacted.values():
            # pprint(content)
            assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")


def test_pds_backup_with_tmp_hlq_option(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        tmphlq = "TMPHLQ"
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        encode_res = hosts.all.zos_encode(
            src=MVS_PDS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            tmp_hlq=tmphlq,
        )
        for enc_res in encode_res.contacted.values():
            assert enc_res.get("backup_name")[:6] == tmphlq
            contents = hosts.all.shell(cmd="cat \"//'{0}(SAMPLE)'\"".format(enc_res.get("backup_name")))
            hosts.all.file(path=TEMP_JCL_PATH, state="absent")
            hosts.all.zos_data_set(name=MVS_PDS, state="absent")
            hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
            for content in contents.contacted.values():
                # pprint(content)
                assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")


def test_ps_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.shell(cmd="cp {0} \"//'{1}'\"".format(TEMP_JCL_PATH, MVS_PS))
        hosts.all.zos_encode(
            src=MVS_PS,
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
            backup_name=BACKUP_DATA_SET,
        )
        contents = hosts.all.shell(cmd="cat \"//'{0}'\"".format(BACKUP_DATA_SET))
        for content in contents.contacted.values():
            assert TEST_FILE_TEXT in content.get("stdout")
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")


def test_vsam_backup(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_VS = get_tmp_ds_name()
        MVS_PS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.zos_data_set(name=MVS_VS, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(
            name=MVS_PS, state="present", record_length=TEST_DATA_RECORD_LENGTH, type="seq"
        )
        hosts.all.file(path=TEMP_JCL_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL.format(MVS_VS)), TEMP_JCL_PATH)
        )
        hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
        )
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        # submit JCL to populate KSDS
        hosts.all.file(path=TEMP_JCL_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(
                quote(KSDS_REPRO_JCL.format(MVS_VS.upper())), TEMP_JCL_PATH
            )
        )
        hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
        )

        hosts.all.zos_encode(
            src=MVS_VS,
            dest=MVS_PS,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
        hosts.all.zos_encode(
            src=MVS_VS,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=BACKUP_DATA_SET,
        )
        hosts.all.zos_data_set(
            name=MVS_PS, state="present", record_length=TEST_DATA_RECORD_LENGTH, type="seq"
        )
        hosts.all.zos_encode(
            src=BACKUP_DATA_SET,
            dest=MVS_PS,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )
    finally:
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=MVS_VS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")


def test_uss_backup_entire_folder_to_default_backup_location(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        # create and fill PDS
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE2)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE3)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        # create and fill directory
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="absent")
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="directory")
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file1")
        )
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file2")
        )
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file3")
        )
        results = hosts.all.zos_encode(
            src=MVS_PDS,
            dest=TEMP_JCL_PATH + "2",
            encoding={
                "from": TO_ENCODING,
                "to": FROM_ENCODING,
            },
            backup=True,
        )
        backup_name = None
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
        assert backup_name
        contents = hosts.all.shell(cmd="cat {0}".format(backup_name + "file1"))
        content1 = ""
        for content in contents.contacted.values():
            content1 = content.get("stdout")
        contents = hosts.all.shell(cmd="cat {0}".format(backup_name + "file2"))
        content2 = ""
        for content in contents.contacted.values():
            content2 = content.get("stdout")
        contents = hosts.all.shell(cmd="cat {0}".format(backup_name + "file3"))
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
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="absent")
        hosts.all.file(path=backup_name, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")


def test_uss_backup_entire_folder_to_default_backup_location_compressed(
    ansible_zos_module
):
    try:
        hosts = ansible_zos_module
        MVS_PDS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        # create and fill PDS
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE2)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE3)'\"".format(TEMP_JCL_PATH, MVS_PDS))
        # create and fill directory
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="absent")
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="directory")
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file1")
        )
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file2")
        )
        hosts.all.shell(
            cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH + "2/file3")
        )
        results = hosts.all.zos_encode(
            src=MVS_PDS,
            dest=TEMP_JCL_PATH + "2",
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

        results = hosts.all.shell(cmd="ls -la {0}".format(backup_name[:-4] + "*"))
        for result in results.contacted.values():
            assert backup_name in result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=MVS_PDS, state="absent")
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.file(path=TEMP_JCL_PATH + "2", state="absent")
        hosts.all.file(path=backup_name, state="absent")


def test_return_backup_name_on_module_success_and_failure(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        MVS_PS = get_tmp_ds_name()
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
        hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
        hosts.all.zos_copy(src=TEMP_JCL_PATH, dest=MVS_PS, remote_src=True)
        enc_ds = hosts.all.zos_encode(
            src=MVS_PS,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=BACKUP_DATA_SET,
        )
        for content in enc_ds.contacted.values():
            assert content.get("backup_name") is not None
            assert content.get("backup_name") == BACKUP_DATA_SET

        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
        enc_ds = hosts.all.zos_encode(
            src=MVS_PS,
            encoding={
                "from": INVALID_ENCODING,
                "to": TO_ENCODING,
            },
            backup=True,
            backup_name=BACKUP_DATA_SET,
        )

        for content in enc_ds.contacted.values():
            assert content.get("msg") is not None
            assert content.get("backup_name") is not None
            assert content.get("backup_name") == BACKUP_DATA_SET
    finally:
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")
        hosts.all.zos_data_set(name=MVS_PS, state="absent")
        hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")