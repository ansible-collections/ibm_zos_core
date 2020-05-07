# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
from shellescape import quote
from pprint import pprint

__metaclass__ = type

USS_FILE = "/tmp/encode.data"
USS_NONE_FILE = "/tmp/none"
USS_DEST_FILE = "/tmp/converted.data"
USS_PATH = "/tmp/src/path"
USS_DEST_PATH = "/tmp/dest/path"
MVS_PS = "encode.ps"
MVS_NONE_PS = "encode.none.ps"
MVS_PDS = "encode.pds"
MVS_PDS_MEMBER = "encode.pds(test)"
MVS_VS = "encode.test.vs"
FROM_ENCODING = "IBM-1047"
INVALID_ENCODING = "EBCDIC"
TO_ENCODING = "ISO8859-1"
TEMP_JCL_PATH = "/tmp/ansible/jcl"
TEST_DATA = """00000001This is for encode conversion testsing
00000002This is for encode conversion testsing
00000003This is for encode conversion testsing
00000004This is for encode conversion testsing
"""
TEST_FILE_TEXT = "HELLO world"
BACKUP_DATA_SET = "USER.PRIVATE.BACK"

KSDS_CREATE_JCL = """//CREKSDS    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
   DELETE ENCODE.TEST.VS
   SET MAXCC=0
   DEFINE CLUSTER (NAME(ENCODE.TEST.VS)    -
   INDEXED                                 -
   KEYS(8 0)                               -
   RECSZ(47 47)                            -
   TRACKS(1,1)                             -
   CISZ(4096)                              -
   FREESPACE(3 3)                          -
   VOLUMES(000000) )                       -
   DATA (NAME(ENCODE.TEST.VS.DATA))        -
   INDEX (NAME(ENCODE.TEST.VS.INDEX))
/*
"""


# def test_uss_encoding_conversion_with_invalid_encoding(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_encode(
#         src=USS_FILE, from_encoding=INVALID_ENCODING, to_encoding=TO_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") is None
#         assert result.get("backup_file") is None
#         assert result.get("changed") is False
#         assert "Invalid codeset: Please check the value" in result.get("msg")


# def test_uss_encoding_conversion_with_the_same_encoding(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_encode(
#         src=USS_FILE, from_encoding=FROM_ENCODING, to_encoding=FROM_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") is None
#         assert result.get("backup_file") is None
#         assert result.get("changed") is False
#         assert (
#             "The value of the from_encoding and to_encoding "
#             "are the same, no need to do the conversion!"
#         ) in result.get("msg")


# def test_uss_encoding_conversion_without_dest(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     results = hosts.all.zos_encode(
#         src=USS_FILE, from_encoding=FROM_ENCODING, to_encoding=TO_ENCODING
#     )
#     hosts.all.file(path=USS_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == USS_FILE
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_when_dest_not_exists_01(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     hosts.all.file(path=USS_NONE_FILE, state="absent")
#     results = hosts.all.zos_encode(
#         src=USS_FILE,
#         dest=USS_NONE_FILE,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#         backup=True,
#     )
#     hosts.all.file(path=USS_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == USS_NONE_FILE
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_when_dest_not_exists_02(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.zos_data_set(name=MVS_PS, state="absent")
#     hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
#     hosts.all.zos_data_set(name=MVS_NONE_PS, state="absent")
#     results = hosts.all.zos_encode(
#         src=MVS_PS,
#         dest=MVS_NONE_PS,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PS
#         assert result.get("dest") == MVS_NONE_PS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is False


# def test_uss_encoding_conversion_uss_file_to_uss_file(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     hosts.all.copy(content="test", dest=USS_DEST_FILE)
#     results = hosts.all.zos_encode(
#         src=USS_FILE,
#         dest=USS_DEST_FILE,
#         from_encoding=TO_ENCODING,
#         to_encoding=FROM_ENCODING,
#     )
#     hosts.all.file(path=USS_FILE, state="absent")
#     hosts.all.file(path=USS_DEST_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == USS_DEST_FILE
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_file_to_uss_path(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.file(path=USS_DEST_PATH, state="directory")
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     results = hosts.all.zos_encode(
#         src=USS_FILE,
#         dest=USS_DEST_PATH,
#         from_encoding=TO_ENCODING,
#         to_encoding=FROM_ENCODING,
#     )
#     hosts.all.file(path=USS_FILE, state="absent")
#     hosts.all.file(path=USS_DEST_PATH, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == USS_DEST_PATH
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_path_to_uss_path(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.file(path=USS_PATH, state="directory")
#     hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode1")
#     hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode2")
#     hosts.all.file(path=USS_DEST_PATH, state="directory")
#     results = hosts.all.zos_encode(
#         src=USS_PATH,
#         dest=USS_DEST_PATH,
#         from_encoding=TO_ENCODING,
#         to_encoding=FROM_ENCODING,
#         backup=True,
#     )
#     hosts.all.file(path=USS_PATH, state="absent")
#     hosts.all.file(path=USS_DEST_PATH, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_PATH
#         assert result.get("dest") == USS_DEST_PATH
#         assert result.get("backup_file") is not None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_file_to_mvs_ps(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq")
#     results = hosts.all.zos_encode(
#         src=USS_FILE, dest=MVS_PS, from_encoding=TO_ENCODING, to_encoding=FROM_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == MVS_PS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_ps_to_uss_file(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content="test", dest=USS_DEST_FILE)
#     results = hosts.all.zos_encode(
#         src=MVS_PS,
#         dest=USS_DEST_FILE,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#         backup=True,
#     )
#     hosts.all.file(path=USS_DEST_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PS
#         assert result.get("dest") == USS_DEST_FILE
#         assert result.get("backup_file") is not None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_file_to_mvs_pds(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=80)
#     results = hosts.all.zos_encode(
#         src=USS_FILE, dest=MVS_PDS, from_encoding=TO_ENCODING, to_encoding=FROM_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == MVS_PDS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_file_to_mvs_pds_member(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     results = hosts.all.zos_data_set(
#         name=MVS_PDS_MEMBER, type="member", state="present"
#     )
#     for result in results.contacted.values():
#         assert result.get("changed") is True
#         assert result.get("module_stderr") is None
#     results = hosts.all.zos_encode(
#         src=USS_FILE,
#         dest=MVS_PDS_MEMBER,
#         from_encoding=TO_ENCODING,
#         to_encoding=FROM_ENCODING,
#     )
#     hosts.all.file(path=USS_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == MVS_PDS_MEMBER
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_pds_member_to_uss_file(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content="test", dest=USS_DEST_FILE)
#     results = hosts.all.zos_encode(
#         src=MVS_PDS_MEMBER,
#         dest=USS_DEST_FILE,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#         backup=True,
#     )
#     hosts.all.file(path=USS_DEST_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PDS_MEMBER
#         assert result.get("dest") == USS_DEST_FILE
#         assert result.get("backup_file") is not None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_path_to_mvs_pds(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.file(path=USS_PATH, state="directory")
#     hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode1")
#     hosts.all.copy(content=TEST_DATA, dest=USS_PATH + "/encode2")
#     hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds", record_length=80)
#     results = hosts.all.zos_encode(
#         src=USS_PATH, dest=MVS_PDS, from_encoding=TO_ENCODING, to_encoding=FROM_ENCODING
#     )
#     hosts.all.file(path=USS_PATH, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_PATH
#         assert result.get("dest") == MVS_PDS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_pds_to_uss_path(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.file(path=USS_DEST_PATH, state="directory")
#     results = hosts.all.zos_encode(
#         src=MVS_PDS,
#         dest=USS_DEST_PATH,
#         from_encoding=TO_ENCODING,
#         to_encoding=FROM_ENCODING,
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PDS
#         assert result.get("dest") == USS_DEST_PATH
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_ps_to_mvs_pds_member(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_encode(
#         src=MVS_PS,
#         dest=MVS_PDS_MEMBER,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PS
#         assert result.get("dest") == MVS_PDS_MEMBER
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_uss_file_to_mvs_vsam(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content=TEST_DATA, dest=USS_FILE)
#     hosts.all.file(path=TEMP_JCL_PATH, state="directory")
#     hosts.all.shell(
#         cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL), TEMP_JCL_PATH)
#     )
#     results = hosts.all.zos_job_submit(
#         src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
#     )
#     hosts.all.file(path=TEMP_JCL_PATH, state="absent")
#     for result in results.contacted.values():
#         assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
#         assert result.get("jobs")[0].get("ret_code").get("code") == 0
#         assert result.get("changed") is True
#     results = hosts.all.zos_encode(
#         src=USS_FILE, dest=MVS_VS, from_encoding=TO_ENCODING, to_encoding=FROM_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == USS_FILE
#         assert result.get("dest") == MVS_VS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_vsam_to_uss_file(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.copy(content="test", dest=USS_DEST_FILE)
#     results = hosts.all.zos_encode(
#         src=MVS_VS,
#         dest=USS_DEST_FILE,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#         backup=True,
#     )
#     hosts.all.file(path=USS_DEST_FILE, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_VS
#         assert result.get("dest") == USS_DEST_FILE
#         assert result.get("backup_file") is not None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_vsam_to_mvs_ps(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.zos_data_set(name=MVS_PS, state="absent")
#     hosts.all.zos_data_set(name=MVS_PS, state="present", type="seq", record_length=47)
#     results = hosts.all.zos_encode(
#         src=MVS_VS, dest=MVS_PS, from_encoding=FROM_ENCODING, to_encoding=TO_ENCODING
#     )
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_VS
#         assert result.get("dest") == MVS_PS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_vsam_to_mvs_pds_member(ansible_zos_module):
#     hosts = ansible_zos_module
#     results = hosts.all.zos_encode(
#         src=MVS_VS,
#         dest=MVS_PDS_MEMBER,
#         from_encoding=FROM_ENCODING,
#         to_encoding=TO_ENCODING,
#     )
#     hosts.all.zos_data_set(name=MVS_PDS, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_VS
#         assert result.get("dest") == MVS_PDS_MEMBER
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


# def test_uss_encoding_conversion_mvs_ps_to_mvs_vsam(ansible_zos_module):
#     hosts = ansible_zos_module
#     hosts.all.file(path=TEMP_JCL_PATH, state="directory")
#     hosts.all.shell(
#         cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL), TEMP_JCL_PATH)
#     )
#     results = hosts.all.zos_job_submit(
#         src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
#     )
#     hosts.all.file(path=TEMP_JCL_PATH, state="absent")
#     for result in results.contacted.values():
#         assert result.get("jobs")[0].get("ret_code").get("msg_code") == "0000"
#         assert result.get("jobs")[0].get("ret_code").get("code") == 0
#         assert result.get("changed") is True
#     results = hosts.all.zos_encode(
#         src=MVS_PS, dest=MVS_VS, from_encoding=TO_ENCODING, to_encoding=FROM_ENCODING
#     )
#     hosts.all.zos_data_set(name=MVS_PS, state="absent")
#     pprint(vars(results))
#     for result in results.contacted.values():
#         assert result.get("src") == MVS_PS
#         assert result.get("dest") == MVS_VS
#         assert result.get("backup_file") is None
#         assert result.get("changed") is True


def test_pds_backup(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
    hosts.all.zos_data_set(name=MVS_PDS, state="absent")
    hosts.all.zos_data_set(name=MVS_PDS, state="present", type="pds")
    hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
    hosts.all.shell(cmd="cp {0} \"//'{1}(SAMPLE)'\"".format(TEMP_JCL_PATH, MVS_PDS))
    hosts.all.zos_encode(
        src=MVS_PDS,
        from_encoding=TO_ENCODING,
        to_encoding=FROM_ENCODING,
        backup=True,
        backup_file=BACKUP_DATA_SET,
    )
    contents = hosts.all.shell(cmd="cat \"//'{0}(SAMPLE)'\"".format(BACKUP_DATA_SET))
    hosts.all.file(path=TEMP_JCL_PATH, state="absent")
    hosts.all.zos_data_set(name=MVS_PDS, state="absent")
    hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
    for content in contents.contacted.values():
        # pprint(content)
        assert TEST_FILE_TEXT in content.get("stdout")


def test_ps_backup(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="present", type="ps")
    hosts.all.shell(cmd="echo '{0}' > {1}".format(TEST_FILE_TEXT, TEMP_JCL_PATH))
    hosts.all.shell(cmd="cp {0} \"//'{1}'\"".format(TEMP_JCL_PATH, MVS_PS))
    hosts.all.zos_encode(
        src=MVS_PS,
        from_encoding=TO_ENCODING,
        to_encoding=FROM_ENCODING,
        backup=True,
        backup_file=BACKUP_DATA_SET,
    )
    contents = hosts.all.shell(cmd="cat \"//'{0}'\"".format(BACKUP_DATA_SET))
    hosts.all.file(path=TEMP_JCL_PATH, state="absent")
    hosts.all.zos_data_set(name=MVS_PS, state="absent")
    hosts.all.zos_data_set(name=BACKUP_DATA_SET, state="absent")
    for content in contents.contacted.values():
        assert TEST_FILE_TEXT in content.get("stdout")
