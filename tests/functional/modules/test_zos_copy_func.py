# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2021, 2023
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

import pytest
import os
import shutil
import re
import tempfile
from tempfile import mkstemp

__metaclass__ = type


DUMMY_DATA = """DUMMY DATA ---- LINE 001 ------
DUMMY DATA ---- LINE 002 ------
DUMMY DATA ---- LINE 003 ------
DUMMY DATA ---- LINE 004 ------
DUMMY DATA ---- LINE 005 ------
DUMMY DATA ---- LINE 006 ------
DUMMY DATA ---- LINE 007 ------"""

DUMMY_DATA_SPECIAL_CHARS = """DUMMY DATA ---- LINE 001 ------
DUMMY DATA ---- LINE ÁÁÁ------
DUMMY DATA ---- LINE ÈÈÈ ------
DUMMY DATA ---- LINE 004 ------
DUMMY DATA ---- LINE 005 ------
DUMMY DATA ---- LINE 006 ------
DUMMY DATA ---- LINE 007 ------
"""

DUMMY_DATA_CRLF = b"00000001 DUMMY DATA\r\n00000002 DUMMY DATA\r\n"

VSAM_RECORDS = """00000001A record
00000002A record
00000003A record
"""

# SHELL_EXECUTABLE = "/usr/lpp/rsusr/ported/bin/bash"
SHELL_EXECUTABLE = "/bin/sh"
TEST_PS = "IMSTESTL.IMS01.DDCHKPT"
TEST_PDS = "IMSTESTL.COMNUC"
TEST_PDS_MEMBER = "IMSTESTL.COMNUC(ATRQUERY)"
TEST_VSAM = "IMSTESTL.LDS01.WADS2"
TEST_VSAM_KSDS = "SYS1.STGINDEX"
TEST_PDSE = "SYS1.NFSLIBE"
TEST_PDSE_MEMBER = "SYS1.NFSLIBE(GFSAMAIN)"

COBOL_SRC = """
       IDENTIFICATION DIVISION.\n
       PROGRAM-ID. HELLOWRD.\n
\n
       PROCEDURE DIVISION.\n
           DISPLAY "SIMPLE HELLO WORLD".\n
           STOP RUN.\n
"""

LINK_JCL = """
//COMPLINK  JOB MSGCLASS=H,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//STEP1     EXEC PGM=IGYCRCTL
//STEPLIB   DD DSN=IGYV5R10.SIGYCOMP,DISP=SHR
//          DD DSN=IGYV5R10.SIGYMAC,DISP=SHR
//SYSIN     DD DISP=SHR,DSN={0}
//SYSPRINT  DD SYSOUT=*
//SYSLIN   DD  UNIT=SYSDA,DISP=(MOD),
//             SPACE=(CYL,(1,1)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=27920),
//             DSN=&&LOADSET
//SYSUT1    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT2    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT3    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT4    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT5    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT6    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT7    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT8    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT9    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT10   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT11   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT12   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT13   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT14   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT15   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSMDECK  DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//*
//LKED     EXEC PGM=IEWL,REGION=0M
//SYSPRINT DD  SYSOUT=*
//SYSLIB   DD  DSN=CEE.SCEELKED,DISP=SHR
//         DD  DSN=CEE.SCEELKEX,DISP=SHR
//SYSLMOD  DD  DSN={1},
//             DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,DCB=BLKSIZE=1024,
//             SPACE=(TRK,(3,3))
//SYSTERM  DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSLIN   DD  DSN=&&LOADSET,DISP=(OLD,KEEP)
//SYSIN    DD  DUMMY
//*

"""

def populate_dir(dir_path):
    for i in range(5):
        with open(dir_path + "/" + "file" + str(i + 1), "w") as infile:
            infile.write(DUMMY_DATA)


def populate_dir_crlf_endings(dir_path):
    for i in range(5):
        with open(os.path.join(dir_path, "file{0}".format(i)), "wb") as infile:
            infile.write(DUMMY_DATA_CRLF)


def populate_partitioned_data_set(hosts, name, ds_type, members=None):
    """Creates a new partitioned data set and inserts records into various
    members of it.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the data set.
        ds_type (str) -- Type of the data set (either PDS or PDSE).
        members (list, optional) -- List of member names to create.
    """
    if not members:
        members = ["MEMBER1", "MEMBER2", "MEMBER3"]
    ds_list = ["{0}({1})".format(name, member) for member in members]

    hosts.all.zos_data_set(name=name, type=ds_type, state="present")

    for member in ds_list:
        hosts.all.shell(
            cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
            executable=SHELL_EXECUTABLE
        )


def get_listcat_information(hosts, name, ds_type):
    """Runs IDCAMS to get information about a data set.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the data set.
        ds_type (str) -- Type of data set ("SEQ", "PDS", "PDSE", "KSDS").
    """
    if ds_type.upper() == "KSDS":
        idcams_input = " LISTCAT ENT('{0}') DATA ALL".format(name)
    else:
        idcams_input = " LISTCAT ENTRIES('{0}')".format(name)

    return hosts.all.zos_mvs_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(dd_output=dict(
                dd_name="sysprint",
                return_content=dict(type="text")
            )),
            dict(dd_input=dict(
                dd_name="sysin",
                content=idcams_input
            ))
        ]
    )


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

        hosts.all.zos_copy(content=VSAM_RECORDS, dest=record_src)
        hosts.all.zos_encode(src=record_src, dest=name, encoding={"from": "ISO8859-1", "to": "IBM-1047"})
        hosts.all.file(path=record_src, state="absent")


def link_loadlib_from_cobol(hosts, ds_name, cobol_pds):
    """
    Given a PDSE, links a cobol program making allocated in a temp ds resulting in ds_name
    as a loadlib.

    Arguments:
        ds_name (str) -- PDS/E to be linked with the cobol program.
        cobol_src (str) -- Cobol source code to be used as the program.

        Notes: PDS names are in the format of SOME.PDSNAME(MEMBER)
    """
    # Copy the Link program
    temp_jcl = "/tmp/link.jcl"
    rc = 0
    try:
        cp_res = hosts.all.zos_copy(
            content=LINK_JCL.format(cobol_pds, ds_name),
            dest="/tmp/link.jcl",
            force=True,
        )
        for res in cp_res.contacted.values():
            print("copy link program result {0}".format(res))
        # Link the temp ds with ds_name
        job_result = hosts.all.zos_job_submit(
            src="/tmp/link.jcl",
            location="USS",
            wait_time_s=60
        )
        for result in job_result.contacted.values():
            print("link job submit result {0}".format(result))
            rc = result.get("jobs")[0].get("ret_code").get("code")
    finally:
        hosts.all.file(path=temp_jcl, state="absent")
    return rc


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_uss_file(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = "/tmp/zos_copy_test_profile"

    try:
        hosts.all.file(path=dest_path, state="absent")

        if src["is_file"]:
            copy_res = hosts.all.zos_copy(src=src["src"], dest=dest_path, is_binary=src["is_binary"], remote_src=src["is_remote"])
        else:
            copy_res = hosts.all.zos_copy(content=src["src"], dest=dest_path, is_binary=src["is_binary"])

        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, force=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=True, is_remote=False),
    dict(src="Example inline content", is_file=False, force=False, is_remote=False),
    dict(src="Example inline content", is_file=False, force=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, force=True, is_remote=True),
])
def test_copy_file_to_existing_uss_file(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = "/tmp/test_profile"

    try:
        hosts.all.file(path=dest_path, state="absent")
        hosts.all.file(path=dest_path, state="touch")
        stat_res = list(hosts.all.stat(path=dest_path).contacted.values())
        timestamp = stat_res[0].get("stat").get("atime")
        assert timestamp is not None

        if src["is_file"]:
            copy_res = hosts.all.zos_copy(src=src["src"], dest=dest_path, force=src["force"], remote_src=src["is_remote"])
        else:
            copy_res = hosts.all.zos_copy(content=src["src"], dest=dest_path, force=src["force"])

        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            if src["force"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_path
                assert result.get("state") == "file"
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_binary=False, is_remote=False),
    dict(src="/etc/profile", is_binary=True, is_remote=False),
    dict(src="/etc/profile", is_binary=False, is_remote=True),
    dict(src="/etc/profile", is_binary=True, is_remote=True),
])
def test_copy_file_to_uss_dir(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = "/tmp"
    dest_path = "/tmp/profile"

    try:
        hosts.all.file(path=dest_path, state="absent")

        copy_res = hosts.all.zos_copy(src=src["src"], dest=dest, is_binary=src["is_binary"], remote_src=src["is_remote"])

        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
        for st in stat_res.contacted.values():
            assert st.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_file_to_uss_dir_missing_parents(ansible_zos_module):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest_dir = "/tmp/parent_dir"
    dest = "{0}/subdir/profile".format(dest_dir)

    try:
        hosts.all.file(path=dest_dir, state="absent")
        copy_res = hosts.all.zos_copy(src=src, dest=dest)
        stat_res = hosts.all.stat(path=dest)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("state") == "file"
        for st in stat_res.contacted.values():
            assert st.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
def test_copy_local_symlink_to_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_lnk = "/tmp/etclnk"
    dest_path = "/tmp/profile"
    try:
        try:
            os.symlink("/etc/profile", src_lnk)
        except FileExistsError:
            pass
        copy_res = hosts.all.zos_copy(src=src_lnk, dest=dest_path, local_follow=True)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest_path), executable=SHELL_EXECUTABLE
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest_path, state="absent")
        os.remove(src_lnk)


@pytest.mark.uss
def test_copy_local_file_to_uss_file_convert_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/profile"
    try:
        hosts.all.file(path=dest_path, state="absent")
        copy_res = hosts.all.zos_copy(
            src="/etc/profile",
            dest=dest_path,
            encoding={"from": "ISO8859-1", "to": "IBM-1047"},
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_inline_content_to_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    dest = "/tmp/"
    dest_path = "/tmp/inline_copy"

    try:
        copy_res = hosts.all.zos_copy(content="Inline content", dest=dest)
        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_dir_to_existing_uss_dir_not_forced(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = "/tmp/new_dir/"
    src_file = "{0}profile".format(src_dir)
    dest_dir = "/tmp/test_dir"
    dest_old_content = "{0}/old_dir".format(dest_dir)

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")
        hosts.all.file(path=dest_old_content, state="directory")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True,
            force=False
        )

        for result in copy_result.contacted.values():
            assert result.get("msg") is not None
            assert result.get("changed") is False
            assert "Error" in result.get("msg")
            assert "EDC5117I" in result.get("stdout")
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
def test_copy_subdirs_folders_and_validate_recursive_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/test/"
    text_outer_file = "Hi I am point A"
    text_inner_file = "Hi I am point B"
    src_path = "/tmp/level_1/"
    outer_file = "/tmp/level_1/text_A.txt"
    inner_src_path = "/tmp/level_1/level_2/"
    inner_file = "/tmp/level_1/level_2/text_B.txt"

    try:
        hosts.all.file(path=inner_src_path, state="directory")
        hosts.all.file(path=inner_file, state = "touch")
        hosts.all.file(path=outer_file, state = "touch")
        hosts.all.shell(cmd="echo '{0}' > '{1}'".format(text_outer_file, outer_file))
        hosts.all.shell(cmd="echo '{0}' > '{1}'".format(text_inner_file, inner_file))
        
        copy_res = hosts.all.zos_copy(src=src_path, dest=dest_path, encoding={"from": "ISO8859-1", "to": "IBM-1047"}, remote_src=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

        stat_res = hosts.all.stat(path="/tmp/test/level_2/")
        for st in stat_res.contacted.values():
            assert st.get("stat").get("exists") is True

        full_inner_path = dest_path + "/level_2/text_B.txt"
        full_outer_path = dest_path + "/text_A.txt"
        inner_file_text_aft_encoding = hosts.all.shell(cmd="cat {0}".format(full_inner_path))
        outer_file_text_aft_encoding = hosts.all.shell(cmd="cat {0}".format(full_outer_path))
        for text in outer_file_text_aft_encoding.contacted.values():
            text_outer = text.get("stdout")
        for text in inner_file_text_aft_encoding.contacted.values():
            text_inner = text.get("stdout")

        assert text_inner == text_inner_file
        assert text_outer == text_outer_file
    finally:
        hosts.all.file(path=src_path, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_subdirs_folders_and_validate_recursive_encoding_local(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/test/"

    try:
        source_1 = tempfile.TemporaryDirectory(prefix="level_", suffix="_1")
        source = source_1.name
        source_2 = tempfile.TemporaryDirectory(dir = source, prefix="level_", suffix="_2")
        full_source = source_2.name
        populate_dir(source)
        populate_dir(full_source)
        level_1 = os.path.basename(source)
        level_2 = os.path.basename(full_source)

        copy_res = hosts.all.zos_copy(src=source, dest=dest_path, encoding={"from": "ISO8859-1", "to": "IBM-1047"})

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

        full_outer_file= "{0}/{1}/file3".format(dest_path, level_1)
        full_iner_file= "{0}/{1}/{2}/file3".format(dest_path, level_1, level_2)
        verify_copy_1 = hosts.all.shell(cmd="cat {0}".format(full_outer_file))
        verify_copy_2 = hosts.all.shell(cmd="cat {0}".format(full_iner_file))

        for result in verify_copy_1.contacted.values():
            print(result)
            assert result.get("stdout") == DUMMY_DATA
        for result in verify_copy_2.contacted.values():
            print(result)
            assert result.get("stdout") == DUMMY_DATA
    finally:
        hosts.all.file(name=dest_path, state="absent")
        source_1.cleanup(ignore_cleanup_errors = True)


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_to_non_existing_dir(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    dest_path = "/tmp/new_dir"

    temp_path = tempfile.mkdtemp()
    src_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(temp_path, src_basename)

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        copy_result = hosts.all.zos_copy(src=source_path, dest=dest_path)

        stat_source_res = hosts.all.stat(path="{0}/{1}".format(dest_path, src_basename))
        if copy_directory:
            stat_file_res = hosts.all.stat(path="{0}/{1}/file3".format(dest_path, src_basename))
        else:
            stat_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_path, src_basename)
            else:
                assert result.get("dest") == dest_path

        for result in stat_source_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(temp_path)


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_to_non_existing_dir(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    src_basename = "source_dir" if copy_directory else "source_dir/"
    src_dir = "/tmp/{0}".format(src_basename)
    src_file = os.path.normpath("{0}/profile".format(src_dir))
    dest_dir = "/tmp/dest_dir"

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True
        )

        stat_dir_res = hosts.all.stat(path="{0}/{1}".format(dest_dir, src_basename))
        if copy_directory:
            stat_file_res = hosts.all.stat(path="{0}/{1}/profile".format(dest_dir, src_basename))
        else:
            stat_file_res = hosts.all.stat(path="{0}/profile".format(dest_dir))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_dir, src_basename)
            else:
                assert result.get("dest") == dest_dir

        for result in stat_dir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_to_existing_dir_forced(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    dest_path = "/tmp/new_dir"
    dest_file = "{0}/profile".format(dest_path)

    temp_path = tempfile.mkdtemp()
    source_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(temp_path, source_basename)

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        hosts.all.file(path=dest_path, state="directory")
        hosts.all.file(path=dest_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            force=True
        )

        stat_source_res = hosts.all.stat(path="{0}/{1}".format(dest_path, source_basename))
        stat_old_file_res = hosts.all.stat(path=dest_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/{1}/file3".format(dest_path, source_basename))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_path, source_basename)
            else:
                assert result.get("dest") == dest_path

        for result in stat_source_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        shutil.rmtree(temp_path)
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_to_existing_dir_forced(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    src_basename = "source_dir" if copy_directory else "source_dir/"
    src_dir = "/tmp/{0}".format(src_basename)
    src_file = os.path.normpath("{0}/profile".format(src_dir))
    dest_dir = "/tmp/dest_dir"
    dest_file = "{0}/file".format(dest_dir)

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")

        hosts.all.file(path=dest_dir, state="directory")
        hosts.all.file(path=dest_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True,
            force=True
        )

        stat_dir_res = hosts.all.stat(path="{0}/{1}".format(dest_dir, src_basename))
        stat_old_file_res = hosts.all.stat(path=dest_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/{1}/profile".format(dest_dir, src_basename))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/profile".format(dest_dir))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_dir, src_basename)
            else:
                assert result.get("dest") == dest_dir

        for result in stat_dir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("create_dest", [False, True])
def test_copy_local_nested_dir_to_uss(ansible_zos_module, create_dest):
    hosts = ansible_zos_module
    dest_path = "/tmp/new_dir"

    source_path = tempfile.mkdtemp()
    if not source_path.endswith("/"):
        source_path = "{0}/".format(source_path)
    subdir_a_path = "{0}subdir_a".format(source_path)
    subdir_b_path = "{0}subdir_b".format(source_path)

    try:
        os.mkdir(subdir_a_path)
        os.mkdir(subdir_b_path)
        populate_dir(subdir_a_path)
        populate_dir(subdir_b_path)

        if create_dest:
            hosts.all.file(path=dest_path, state="directory")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            force=create_dest
        )

        stat_subdir_a_res = hosts.all.stat(path="{0}/subdir_a".format(dest_path))
        stat_subdir_b_res = hosts.all.stat(path="{0}/subdir_b".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
        for result in stat_subdir_a_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
        for result in stat_subdir_b_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(source_path)


@pytest.mark.uss
@pytest.mark.parametrize("create_dest", [False, True])
def test_copy_uss_nested_dir_to_uss(ansible_zos_module, create_dest):
    hosts = ansible_zos_module
    source_path = "/tmp/old_dir/"
    dest_path = "/tmp/new_dir"

    subdir_a_path = "{0}subdir_a".format(source_path)
    subdir_b_path = "{0}subdir_b".format(source_path)

    try:
        hosts.all.file(path=subdir_a_path, state="directory")
        hosts.all.file(path=subdir_b_path, state="directory")
        if create_dest:
            hosts.all.file(path=dest_path, state="directory")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            remote_src=True,
            force=create_dest
        )

        stat_subdir_a_res = hosts.all.stat(path="{0}/subdir_a".format(dest_path))
        stat_subdir_b_res = hosts.all.stat(path="{0}/subdir_b".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
        for result in stat_subdir_a_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
        for result in stat_subdir_b_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

    finally:
        hosts.all.file(path=source_path, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_and_change_mode(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module

    source_parent_path = tempfile.mkdtemp()
    source_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(source_parent_path, source_basename)
    mode = "0755"

    dest_path = "/tmp/new_dir"
    dest_profile = "{0}/profile".format(dest_path)
    dest_subdir = "{0}/{1}".format(dest_path, source_basename)
    if copy_directory:
        dest_old_file = "{0}/file1".format(dest_subdir)
    else:
        dest_old_file = "{0}/file1".format(dest_path)
    dest_mode = "0644"

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        if copy_directory:
            hosts.all.file(path=dest_subdir, state="directory", mode=dest_mode)
        else:
            hosts.all.file(path=dest_path, state="directory", mode=dest_mode)
        hosts.all.file(path=dest_profile, state="touch", mode=dest_mode)
        hosts.all.file(path=dest_old_file, state="touch", mode=dest_mode)

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            force=True,
            mode=mode
        )

        stat_dir_res = hosts.all.stat(path=dest_path)
        stat_subdir_res = hosts.all.stat(path=dest_subdir)
        stat_old_file_res = hosts.all.stat(path=dest_profile)
        stat_overwritten_file_res = hosts.all.stat(path=dest_old_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_subdir))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == dest_subdir
            else:
                assert result.get("dest") == dest_path

        for result in stat_dir_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

            if copy_directory:
                assert result.get("stat").get("mode") == dest_mode
            else:
                assert result.get("stat").get("mode") == mode

        for result in stat_subdir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
                assert result.get("stat").get("mode") == mode
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_overwritten_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(source_parent_path)


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_and_change_mode(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module

    source_basename = "source" if copy_directory else "source/"
    source_path = "/tmp/{0}".format(source_basename)
    mode = "0755"

    dest_path = "/tmp/new_dir"
    dest_subdir = "{0}/{1}".format(dest_path, source_basename)
    dest_profile = "{0}/profile".format(dest_path)
    if copy_directory:
        dest_old_file = "{0}/file1".format(dest_subdir)
    else:
        dest_old_file = "{0}/file1".format(dest_path)
    dest_mode = "0644"

    try:
        hosts.all.file(path=source_path, state="directory")
        for i in range(1, 4):
            current_file_path = os.path.normpath("{0}/file{1}".format(source_path, i))
            hosts.all.file(path=current_file_path, state="touch")

        if copy_directory:
            hosts.all.file(path=dest_subdir, state="directory", mode=dest_mode)
        else:
            hosts.all.file(path=dest_path, state="directory", mode=dest_mode)
        hosts.all.file(path=dest_profile, state="touch", mode=dest_mode)
        hosts.all.file(path=dest_old_file, state="touch", mode=dest_mode)

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            force=True,
            remote_src=True,
            mode=mode
        )

        stat_dir_res = hosts.all.stat(path=dest_path)
        stat_subdir_res = hosts.all.stat(path=dest_subdir)
        stat_old_file_res = hosts.all.stat(path=dest_profile)
        stat_overwritten_file_res = hosts.all.stat(path=dest_old_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_subdir))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

            if copy_directory:
                assert result.get("dest") == dest_subdir
            else:
                assert result.get("dest") == dest_path

        for result in stat_dir_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

            if copy_directory:
                assert result.get("stat").get("mode") == dest_mode
            else:
                assert result.get("stat").get("mode") == mode

        for result in stat_subdir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
                assert result.get("stat").get("mode") == mode
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_overwritten_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

    finally:
        hosts.all.file(path=source_path, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("backup", [None, "/tmp/uss_backup"])
def test_backup_uss_file(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "/tmp/profile"
    backup_name = None

    try:
        hosts.all.file(path=dest, state="touch")
        if backup:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True, backup_name=backup)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            backup_name = result.get("backup_name")

            if backup:
                assert backup_name == backup
            else:
                assert backup_name is not None

        stat_res = hosts.all.stat(path=backup_name)
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True

    finally:
        hosts.all.file(path=dest, state="absent")
        if backup_name:
            hosts.all.file(path=backup_name, state="absent")


@pytest.mark.uss
def test_copy_file_insufficient_read_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    src_path = "/tmp/testfile"
    dest = "/tmp"
    try:
        open(src_path, "w").close()
        os.chmod(src_path, 0)
        copy_res = hosts.all.zos_copy(src=src_path, dest=dest)
        for result in copy_res.contacted.values():
            assert result.get("msg") is not None
            assert "read permission" in result.get("msg")
    finally:
        if os.path.exists(src_path):
            os.remove(src_path)


@pytest.mark.uss
@pytest.mark.parametrize("is_remote", [False, True])
def test_copy_non_existent_file_fails(ansible_zos_module, is_remote):
    hosts = ansible_zos_module
    src_path = "/tmp/non_existent_src"
    dest = "/tmp"

    copy_res = hosts.all.zos_copy(src=src_path, dest=dest, remote_src=is_remote)
    for result in copy_res.contacted.values():
        assert result.get("msg") is not None
        assert "does not exist" in result.get("msg")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_remote=False),
    dict(src="/etc/profile", is_remote=True),])
def test_ensure_copy_file_does_not_change_permission_on_dest(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = "/tmp/test/"
    try:
        hosts.all.file(path=dest_path, state="directory", mode="750")
        permissions_before = hosts.all.shell(cmd="ls -la {0}".format(dest_path))
        hosts.all.zos_copy(content=src["src"], dest=dest_path)
        permissions = hosts.all.shell(cmd="ls -la {0}".format(dest_path))

        for before in permissions_before.contacted.values():
            permissions_be_copy = before.get("stdout")
            
        for after in permissions.contacted.values():
            permissions_af_copy = after.get("stdout") 

        permissions_be_copy = permissions_be_copy.splitlines()[1].split()[0]
        permissions_af_copy = permissions_af_copy.splitlines()[1].split()[0]
                
        assert permissions_be_copy == permissions_af_copy
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/", is_remote=False),
    dict(src="/etc/", is_remote=True),])
def test_ensure_copy_directory_does_not_change_permission_on_dest(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = "/tmp/test/"
    try:
        hosts.all.file(path=dest_path, state="directory", mode="750")
        permissions_before = hosts.all.shell(cmd="ls -la {0}".format(dest_path))
        hosts.all.zos_copy(content=src["src"], dest=dest_path)
        permissions = hosts.all.shell(cmd="ls -la {0}".format(dest_path))

        for before in permissions_before.contacted.values():
            permissions_be_copy = before.get("stdout")

        for after in permissions.contacted.values():
            permissions_af_copy = after.get("stdout") 

        permissions_be_copy = permissions_be_copy.splitlines()[1].split()[0]
        permissions_af_copy = permissions_af_copy.splitlines()[1].split()[0]
                
        assert permissions_be_copy == permissions_af_copy
    finally:
        hosts.all.file(path=dest_path, state="absent")
        

@pytest.mark.uss
@pytest.mark.seq
def test_copy_file_record_length_to_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "w") as infile:
        infile.write(DUMMY_DATA)

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            is_binary=False
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        verify_recl = hosts.all.shell(
            cmd="dls -l {0}".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
        for v_recl in verify_recl.contacted.values():
            assert v_recl.get("rc") == 0
            stdout = v_recl.get("stdout").split()
            assert len(stdout) == 5
            # Verifying the dataset type (sequential).
            assert stdout[1] == "PS"
            # Verifying the record format is Fixed Block.
            assert stdout[2] == "FB"
            # Verifying the record length is 31. The dummy data has 31
            # characters per line.
            assert stdout[3] == "31"
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)


@pytest.mark.uss
@pytest.mark.seq
def test_copy_file_crlf_endings_to_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "wb") as infile:
        infile.write(DUMMY_DATA_CRLF)

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            is_binary=False
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        verify_recl = hosts.all.shell(
            cmd="dls -l {0}".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert len(v_cp.get("stdout_lines")) == 2
        for v_recl in verify_recl.contacted.values():
            assert v_recl.get("rc") == 0
            stdout = v_recl.get("stdout").split()
            assert len(stdout) == 5
            # Verifying the dataset type (sequential).
            assert stdout[1] == "PS"
            # Verifying the record format is Fixed Block.
            assert stdout[2] == "FB"
            # Verifying the record length is 19. The dummy data has 19
            # characters per line.
            assert stdout[3] == "19"
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], is_binary=src["is_binary"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, remote_src=src["is_remote"], is_binary=src["is_binary"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("is_binary") == src["is_binary"]
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, force=True, is_remote=False),
    dict(src="Example inline content", is_file=False, force=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=True, is_remote=True),
    dict(src="/etc/profile", is_file=True, force=False, is_remote=False),
    dict(src="Example inline content", is_file=False, force=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=False, is_remote=True),
])
def test_copy_file_to_empty_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], force=src["force"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, remote_src=src["is_remote"], force=src["force"])

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", force=False, is_remote=False),
    dict(src="/etc/profile", force=True, is_remote=False),
    dict(src="/etc/profile", force=False, is_remote=True),
    dict(src="/etc/profile", force=True, is_remote=True),
])
def test_copy_file_to_non_empty_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="absent")
        hosts.all.zos_copy(content="Inline content", dest=dest)

        copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], force=src["force"])

        for result in copy_result.contacted.values():
            if src["force"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
def test_copy_ps_to_non_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "/tmp/ddchkpt"

    try:
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("force", [False, True])
def test_copy_ps_to_existing_uss_file(ansible_zos_module, force):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "/tmp/ddchkpt"

    try:
        hosts.all.file(path=dest, state="touch")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, force=force)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if force:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
def test_copy_ps_to_existing_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "/tmp/ddchkpt"
    dest_path = dest + "/" + TEST_PS

    try:
        hosts.all.file(path=dest, state="directory")
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest_path), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.seq
def test_copy_ps_to_non_existing_ps(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, state="absent")
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("force", [False, True])
def test_copy_ps_to_empty_ps(ansible_zos_module, force):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, force=force)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("force", [False, True])
def test_copy_ps_to_non_empty_ps(ansible_zos_module, force):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="absent")
        hosts.all.zos_copy(content="Inline content", dest=dest)

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, force=force)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if force:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("force", [False, True])
def test_copy_ps_to_non_empty_ps_with_special_chars(ansible_zos_module, force):
    hosts = ansible_zos_module
    src_ds = TEST_PS
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="absent")
        hosts.all.zos_copy(content=DUMMY_DATA_SPECIAL_CHARS, dest=dest)

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, force=force)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if force:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("backup", [None, "USER.TEST.SEQ.FUNCTEST.BACK"])
def test_backup_sequential_data_set(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")

        if backup:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True, backup_name=backup)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            backup_name = result.get("backup_name")
            assert backup_name is not None

        stat_res = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(backup_name),
            executable=SHELL_EXECUTABLE,
        )
        for result in stat_res.contacted.values():
            assert result.get("rc") == 0
            assert "NOT IN CATALOG" not in result.get("stdout")
            assert "NOT IN CATALOG" not in result.get("stderr")

    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup_name:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, is_binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, is_binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, is_binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_member(ansible_zos_module, src):
    hosts = ansible_zos_module
    data_set = "USER.TEST.PDS.FUNCTEST"
    dest = "{0}(PROFILE)".format(data_set)

    try:
        hosts.all.zos_data_set(
            name=data_set,
            type="pdse",
            space_primary=5,
            space_type="M",
            record_format="fba",
            record_length=80,
            replace=True
        )

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, is_binary=src["is_binary"], remote_src=src["is_remote"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, is_binary=src["is_binary"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, force=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=True, is_remote=False),
    dict(src="Example inline content", is_file=False, force=False, is_remote=False),
    dict(src="Example inline content", is_file=False, force=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, force=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, force=True, is_remote=True)
])
def test_copy_file_to_existing_member(ansible_zos_module, src):
    hosts = ansible_zos_module
    data_set = "USER.TEST.PDS.FUNCTEST"
    dest = "{0}(PROFILE)".format(data_set)

    try:
        hosts.all.zos_data_set(
            name=data_set,
            type="pdse",
            space_primary=5,
            space_type="M",
            record_format="fba",
            record_length=80,
            replace=True
        )
        hosts.all.zos_data_set(name=dest, type="member", state="present")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, force=src["force"], remote_src=src["is_remote"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, force=src["force"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            if src["force"]:
                assert cp_res.get("msg") is None
                assert cp_res.get("changed") is True
                assert cp_res.get("dest") == dest
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="seq", is_binary=False),
    dict(type="seq", is_binary=True),
    dict(type="pds", is_binary=False),
    dict(type="pds", is_binary=True),
    dict(type="pdse", is_binary=False),
    dict(type="pdse", is_binary=True)
])
def test_copy_data_set_to_non_existing_member(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_data_set = "USER.TEST.PDS.SOURCE"
    src = src_data_set if args["type"] == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = "USER.TEST.PDS.FUNCTEST"
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=args["type"])
        if args["type"] != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, type="pdse", replace=True)
        copy_result = hosts.all.zos_copy(src=src, dest=dest, is_binary=args["is_binary"], remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="seq", force=False),
    dict(type="seq", force=True),
    dict(type="pds", force=False),
    dict(type="pds", force=True),
    dict(type="pdse", force=False),
    dict(type="pdse", force=True)
])
def test_copy_data_set_to_existing_member(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_data_set = "USER.TEST.PDS.SOURCE"
    src = src_data_set if args["type"] == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = "USER.TEST.PDS.FUNCTEST"
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=args["type"])
        if args["type"] != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, type="pdse", replace=True)
        hosts.all.zos_data_set(name=dest, type="member")
        copy_result = hosts.all.zos_copy(src=src, dest=dest, force=args["force"], remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            if args["force"]:
                assert cp_res.get("msg") is None
                assert cp_res.get("changed") is True
                assert cp_res.get("dest") == dest
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            if args["force"]:
                assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("is_remote", [False, True])
def test_copy_file_to_non_existing_pdse(ansible_zos_module, is_remote):
    hosts = ansible_zos_module
    dest = "USER.TEST.PDS.FUNCTEST"
    dest_path = "{0}(PROFILE)".format(dest)
    src_file = "/etc/profile"

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(src=src_file, dest=dest_path, remote_src=is_remote)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest_path),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_path
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
def test_copy_dir_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = "/tmp/testdir"
    dest = "USER.TEST.PDSE.FUNCTEST"

    try:
        hosts.all.file(path=src_dir, state="directory")
        for i in range(5):
            hosts.all.file(path=src_dir + "/" + "file" + str(i), state="touch")

        copy_res = hosts.all.zos_copy(src=src_dir, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
def test_copy_dir_crlf_endings_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    dest = "USER.TEST.PDSE.FUNCTEST"

    temp_path = tempfile.mkdtemp()
    src_basename = "source/"
    source_path = "{0}/{1}".format(temp_path, src_basename)

    try:
        os.mkdir(source_path)
        populate_dir_crlf_endings(source_path)

        copy_res = hosts.all.zos_copy(src=source_path, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}({1})'\"".format(dest, "FILE2"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert len(result.get("stdout_lines")) == 2
    finally:
        shutil.rmtree(temp_path)
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_dir_to_existing_pdse(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_dir = "/tmp/testdir"
    dest = "USER.TEST.PDS.FUNCTEST"

    try:
        hosts.all.file(path=src_dir, state="directory")
        for i in range(5):
            hosts.all.file(path=src_dir + "/" + "file" + str(i), state="touch")

        hosts.all.zos_data_set(
            name=dest,
            type=src_type,
            space_primary=5,
            space_type="M",
            record_format="fba",
            record_length=80,
        )

        copy_result = hosts.all.zos_copy(src=src_dir, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["seq", "pds", "pdse"])
def test_copy_data_set_to_non_existing_pdse(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_data_set = "USER.TEST.PDS.SOURCE"
    src = src_data_set if src_type == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = "USER.TEST.PDS.FUNCTEST"
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=src_type)
        if src_type != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, state="absent")
        copy_result = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(src_type="pds", dest_type="pds"),
    dict(src_type="pds", dest_type="pdse"),
    dict(src_type="pdse", dest_type="pds"),
    dict(src_type="pdse", dest_type="pdse"),
])
def test_copy_pds_to_existing_pds(ansible_zos_module, args):
    hosts = ansible_zos_module
    src = "USER.TEST.PDS.SRC"
    dest = "USER.TEST.PDS.DEST"

    try:
        populate_partitioned_data_set(hosts, src, args["src_type"])
        hosts.all.zos_data_set(name=dest, type=args["dest_type"])

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 3
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_pds_loadlib_member_to_pds_loadlib_member(ansible_zos_module,):
    hosts = ansible_zos_module
    # The volume for this dataset should use a system symbol.
    # This dataset and member should be available on any z/OS system.
    src = "USER.LOAD.SRC"
    dest = "USER.LOAD.DEST"
    cobol_pds = "USER.COBOL.SRC"
    try:
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="pdse",
            record_format="U",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="M",
            replace=True
        )

        hosts.all.zos_data_set(
            name=dest,
            state="present",
            type="pdse",
            record_format="U",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="M",
            replace=True
        )

        hosts.all.zos_data_set(
            name=cobol_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="FB",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        member = "HELLOSRC"
        cobol_pds = "{0}({1})".format(cobol_pds, member)
        rc = hosts.all.zos_copy(
            content=COBOL_SRC,
            dest=cobol_pds,
        )
        dest_name = "{0}({1})".format(dest, member)
        src_name = "{0}({1})".format(src, member)
        # both src and dest need to be a loadlib
        rc = link_loadlib_from_cobol(hosts, dest_name, cobol_pds)
        assert rc == 0
        # make sure is executable
        cmd = "mvscmd --pgm={0}  --steplib={1} --sysprint=* --stderr=* --stdout=*"
        exec_res = hosts.all.shell(
            cmd=cmd.format(member, dest)
        )
        for result in exec_res.contacted.values():
            assert result.get("rc") == 0
        rc = link_loadlib_from_cobol(hosts, src_name, cobol_pds)
        assert rc == 0

        exec_res = hosts.all.shell(
            cmd=cmd.format(member, src)
        )
        for result in exec_res.contacted.values():
            assert result.get("rc") == 0

        copy_res = hosts.all.zos_copy(
            src="{0}({1})".format(src, member), 
            dest="{0}({1})".format(dest, "MEM1"), 
            remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest, "MEM1")

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            # number of members
            assert len(stdout.splitlines()) == 2

    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=cobol_pds, state="absent")


@pytest.mark.pdse
def test_copy_pds_member_with_system_symbol(ansible_zos_module,):
    """This test is for bug #543 in GitHub. In some versions of ZOAU,
    datasets.listing can't handle system symbols in volume names and
    therefore fails to get details from a dataset.

    Note: `listcat ent('SYS1.SAMPLIB') all` will display 'volser = ******'
    and `D SYMBOLS` will show you that `&SYSR2. = "RES80A"` where
    the symbols for this volume correspond to volume `RES80A`
    """
    hosts = ansible_zos_module
    # The volume for this dataset should use a system symbol.
    # This dataset and member should be available on any z/OS system.
    src = "SYS1.SAMPLIB(IZUPRM00)"
    dest = "USER.TEST.PDS.DEST"

    try:
        hosts.all.zos_data_set(
            name=dest,
            state="present",
            type="pdse",
            replace=True
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 1

    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_multiple_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    src = "USER.FUNCTEST.SRC.PDS"
    src_wildcard = "{0}(ABC*)".format(src)

    dest = "USER.FUNCTEST.DEST.PDS"
    member_list = ["MEMBER1", "ABCXYZ", "ABCASD"]
    ds_list = ["{0}({1})".format(src, member) for member in member_list]

    try:
        hosts.all.zos_data_set(name=src, type="pds")
        hosts.all.zos_data_set(name=dest, type="pds")

        for member in ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
                executable=SHELL_EXECUTABLE
            )

        copy_res = hosts.all.zos_copy(src=src_wildcard, dest=dest, remote_src=True)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest

        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 2

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_multiple_data_set_members_in_loop(ansible_zos_module):
    """
    This test case was included in case the module is called inside a loop,
    issue was discovered in https://github.com/ansible-collections/ibm_zos_core/issues/560.
    """
    hosts = ansible_zos_module
    src = "USER.FUNCTEST.SRC.PDS"

    dest = "USER.FUNCTEST.DEST.PDS"
    member_list = ["MEMBER1", "ABCXYZ", "ABCASD"]
    src_ds_list = ["{0}({1})".format(src, member) for member in member_list]
    dest_ds_list = ["{0}({1})".format(dest, member) for member in member_list]

    try:
        hosts.all.zos_data_set(name=src, type="pds")
        hosts.all.zos_data_set(name=dest, type="pds")

        for src_member in src_ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, src_member),
                executable=SHELL_EXECUTABLE
            )

        for src_member, dest_member in zip(src_ds_list, dest_ds_list):
            copy_res = hosts.all.zos_copy(src=src_member, dest=dest_member, remote_src=True)
            for result in copy_res.contacted.values():
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_member

        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 3

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("ds_type", ["pds", "pdse"])
def test_copy_member_to_non_existing_uss_file(ansible_zos_module, ds_type):
    hosts = ansible_zos_module
    data_set = "USER.TEST.PDSE.SOURCE"
    src = "{0}(MEMBER)".format(data_set)
    dest = "/tmp/member"

    try:
        hosts.all.file(path=dest, state="absent")
        hosts.all.zos_data_set(name=data_set, state="present", type=ds_type)
        hosts.all.shell(
            cmd="decho 'Record for data set' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(path=data_set, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(ds_type="pds", force=False),
    dict(ds_type="pds", force=True),
    dict(ds_type="pdse", force=False),
    dict(ds_type="pdse", force=True)
])
def test_copy_member_to_existing_uss_file(ansible_zos_module, args):
    hosts = ansible_zos_module
    data_set = "USER.TEST.PDSE.SOURCE"
    src = "{0}(MEMBER)".format(data_set)
    dest = "/tmp/member"

    try:
        hosts.all.file(path=dest, state="touch")
        hosts.all.zos_data_set(name=data_set, state="present", type=args["ds_type"])
        hosts.all.shell(
            cmd="decho 'Record for data set' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True, force=args["force"])
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if args["force"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            if args["force"]:
                assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_pdse_to_uss_dir(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = "USER.TEST.FUNCTEST"
    dest = "/tmp/"
    dest_path = "/tmp/{0}".format(src_ds)

    try:
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        members = ["MEMBER1", "MEMBER2", "MEMBER3"]
        ds_list = ["{0}({1})".format(src_ds, member) for member in members]
        for member in ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
                executable=SHELL_EXECUTABLE
            )

        hosts.all.file(path=dest_path, state="directory")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_member_to_uss_dir(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = "USER.TEST.FUNCTEST"
    src = "{0}(MEMBER)".format(src_ds)
    dest = "/tmp/"
    dest_path = "/tmp/MEMBER"

    try:
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        hosts.all.shell(
            cmd="decho '{0}' '{1}'".format(DUMMY_DATA, src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest_path),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_member_to_non_existing_seq_data_set(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = "USER.TEST.PDS.SOURCE"
    src = "{0}(MEMBER)".format(src_ds)
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, state="absent")
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        hosts.all.shell(
            cmd="decho 'A record' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="pds", force=False),
    dict(type="pds", force=True),
    dict(type="pdse", force=False),
    dict(type="pdse", force=True),
])
def test_copy_member_to_existing_seq_data_set(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_ds = "USER.TEST.PDS.SOURCE"
    src = "{0}(MEMBER)".format(src_ds)
    dest = "USER.TEST.SEQ.FUNCTEST"

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present", replace=True)
        hosts.all.zos_data_set(name=src_ds, type=args["type"], state="present")

        for data_set in [src, dest]:
            hosts.all.shell(
                cmd="decho 'A record' '{0}'".format(data_set),
                executable=SHELL_EXECUTABLE
            )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, force=args["force"], remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if args["force"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            if args["force"]:
                assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("dest_type", ["pds", "pdse"])
def test_copy_file_to_member_convert_encoding(ansible_zos_module, dest_type):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "USER.TEST.PDS.FUNCTEST"

    try:
        hosts.all.zos_data_set(
            type=dest_type,
            space_primary=5,
            space_type="M",
            record_format="fba",
            record_length=25,
        )

        copy_res = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            encoding={
                "from": "UTF-8",
                "to": "IBM-1047"
            },
        )

        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest + "(PROFILE)"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="pds", backup=None),
    dict(type="pds", backup="USER.TEST.PDS.BACKUP"),
    dict(type="pdse", backup=None),
    dict(type="pdse", backup="USER.TEST.PDSE.BACKUP"),
])
def test_backup_pds(ansible_zos_module, args):
    hosts = ansible_zos_module
    src = tempfile.mkdtemp()
    dest = "USER.TEST.PDS.FUNCTEST"
    members = ["FILE1", "FILE2", "FILE3", "FILE4", "FILE5"]
    backup_name = None

    try:
        populate_dir(src)
        populate_partitioned_data_set(hosts, dest, args["type"], members)

        if args["backup"]:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True, backup_name=args["backup"])
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, force=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest

            backup_name = result.get("backup_name")
            assert backup_name is not None
            if args["backup"]:
                assert backup_name == args["backup"]

        verify_copy = get_listcat_information(hosts, backup_name, args["type"])

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output

    finally:
        shutil.rmtree(src)
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup_name:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["seq", "pds", "pdse"])
def test_copy_data_set_to_volume(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    source = "USER.TEST.FUNCTEST.SRC"
    dest = "USER.TEST.FUNCTEST.DEST"

    try:
        hosts.all.zos_data_set(name=source, type=src_type, state='present')
        copy_res = hosts.all.zos_copy(
            src=source,
            dest=dest,
            remote_src=True,
            volume='000000'
        )

        for cp in copy_res.contacted.values():
            assert cp.get('msg') is None
            assert cp.get('changed') is True
            assert cp.get('dest') == dest

        check_vol = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cv in check_vol.contacted.values():
            assert cv.get('rc') == 0
            assert "000000" in cv.get('stdout')
    finally:
        hosts.all.zos_data_set(name=source, state='absent')
        hosts.all.zos_data_set(name=dest, state='absent')


@pytest.mark.vsam
def test_copy_ksds_to_non_existing_ksds(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = TEST_VSAM_KSDS
    dest_ds = "USER.TEST.VSAM.KSDS"

    try:
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest_ds, remote_src=True)
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_ds
        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
    finally:
        hosts.all.zos_data_set(name=dest_ds, state="absent")


@pytest.mark.vsam
@pytest.mark.parametrize("force", [False, True])
def test_copy_ksds_to_existing_ksds(ansible_zos_module, force):
    hosts = ansible_zos_module
    src_ds = "USER.TEST.VSAM.SOURCE"
    dest_ds = "USER.TEST.VSAM.KSDS"

    try:
        create_vsam_data_set(hosts, src_ds, "KSDS", add_data=True, key_length=12, key_offset=0)
        create_vsam_data_set(hosts, dest_ds, "KSDS", add_data=True, key_length=12, key_offset=0)

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest_ds, remote_src=True, force=force)
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            if force:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_ds
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest_ds, state="absent")


@pytest.mark.vsam
@pytest.mark.parametrize("backup", [None, "USER.TEST.VSAM.KSDS.BACK"])
def test_backup_ksds(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = "USER.TEST.VSAM.SOURCE"
    dest = "USER.TEST.VSAM.KSDS"
    backup_name = None

    try:
        create_vsam_data_set(hosts, src, "KSDS", add_data=True, key_length=12, key_offset=0)
        create_vsam_data_set(hosts, dest, "KSDS", add_data=True, key_length=12, key_offset=0)

        if backup:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, backup=True, backup_name=backup, remote_src=True, force=True)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, backup=True, remote_src=True, force=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            backup_name = result.get("backup_name")
            assert backup_name is not None

            if backup:
                assert backup_name == backup

        verify_copy = get_listcat_information(hosts, dest, "ksds")
        verify_backup = get_listcat_information(hosts, backup_name, "ksds")

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
        for result in verify_backup.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup_name:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.vsam
def test_copy_ksds_to_volume(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = TEST_VSAM_KSDS
    dest_ds = "USER.TEST.VSAM.KSDS"

    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest_ds,
            remote_src=True,
            volume="000000"
        )
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_ds
        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
            assert re.search(r"\b000000\b", output)
    finally:
        hosts.all.zos_data_set(name=dest_ds, state="absent")


def test_dest_data_set_parameters(ansible_zos_module):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "USER.TEST.DEST"
    volume = "000000"
    space_primary = 3
    space_secondary = 2
    space_type = "K"
    record_format = "VB"
    record_length = 100
    block_size = 21000

    try:
        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            volume=volume,
            dest_data_set=dict(
                type="SEQ",
                space_primary=space_primary,
                space_secondary=space_secondary,
                space_type=space_type,
                record_format=record_format,
                record_length=record_length,
                block_size=block_size
            )
        )

        verify_copy = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
        for result in verify_copy.contacted.values():
            # The tsocmd returns 5 lines like this:
            # USER.TEST.DEST
            # --RECFM-LRECL-BLKSIZE-DSORG
            #   VB    100   21000   PS
            # --VOLUMES--
            #   000000
            assert result.get("rc") == 0
            output_lines = result.get("stdout").split("\n")
            assert len(output_lines) == 5
            data_set_attributes = output_lines[2].strip().split()
            assert len(data_set_attributes) == 4
            assert data_set_attributes[0] == record_format
            assert data_set_attributes[1] == str(record_length)
            assert data_set_attributes[2] == str(block_size)
            assert data_set_attributes[3] == "PS"
            assert volume in output_lines[4]
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


def test_ensure_tmp_cleanup(ansible_zos_module):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "/tmp"
    dest_path = "/tmp/profile"

    temp_files_patterns = [
        re.compile(r"\bansible-zos-copy-payload"),
        re.compile(r"\bconverted"),
        re.compile(r"\bansible-zos-copy-data-set-dump")
    ]

    try:
        copy_res = hosts.all.zos_copy(src=src, dest=dest)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True

        stat_dir = hosts.all.shell(
            cmd="ls",
            executable=SHELL_EXECUTABLE,
            chdir="/tmp/"
        )

        for result in stat_dir.contacted.values():
            tmp_files = result.get("stdout")
            for pattern in temp_files_patterns:
                assert not pattern.search(tmp_files)

    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.vsam
@pytest.mark.parametrize("force", [False, True])
def test_copy_uss_file_to_existing_sequential_data_set_twice_with_tmphlq_option(ansible_zos_module, force):
    hosts = ansible_zos_module
    dest = "USER.TEST.SEQ.FUNCTEST"
    src_file = "/etc/profile"
    tmphlq = "TMPHLQ"
    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest, remote_src=True, force=force)
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest, remote_src=True, backup=True, tmp_hlq=tmphlq, force=force)

        verify_copy = None
        if force:
            verify_copy = hosts.all.shell(
                cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
                executable=SHELL_EXECUTABLE,
            )

        for cp_res in copy_result.contacted.values():
            if force:
                assert cp_res.get("msg") is None
                assert cp_res.get("backup_name")[:6] == tmphlq
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        if force:
            for v_cp in verify_copy.contacted.values():
                assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        