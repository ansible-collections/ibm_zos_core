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

import os
import shutil
import stat

from hashlib import sha256
from ansible.utils.hashing import checksum
from shellescape import quote

__metaclass__ = type


DUMMY_DATA = """DUMMY DATA == LINE 01 ==
DUMMY DATA == LINE 02 ==
DUMMY DATA == LINE 03 ==
"""


TEST_PS = "IMSTESTL.IMS01.DDCHKPT"
TEST_PS_VB = "USER.PRIV.PSVB"
TEST_PDS = "IMSTESTL.COMNUC"
TEST_PDS_MEMBER = "IMSTESTL.COMNUC(ATRQUERY)"
TEST_VSAM = "FETCH.TEST.VS"
TEST_EMPTY_VSAM = "IMSTESTL.LDS01.WADS0"
FROM_ENCODING = "IBM-1047"
TO_ENCODING = "ISO8859-1"
USS_FILE = "/tmp/fetch.data"
TEST_DATA = """0001This is for encode conversion testsing
0002This is for encode conversion testsing
0003This is for encode conversion testsing
0004This is for encode conversion testsing
"""
KSDS_CREATE_JCL = """//CREKSDS    JOB (T043JM,JM00,1,0,0,0),'CREATE KSDS',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=OMVSADM
//STEP1  EXEC PGM=IDCAMS
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
    DELETE FETCH.TEST.VS
    SET MAXCC=0
    DEFINE CLUSTER                          -
    (NAME(FETCH.TEST.VS)                  -
    INDEXED                                -
    KEYS(4 0)                            -
    RECSZ(200 200)                         -
    RECORDS(100)                           -
    SHAREOPTIONS(2 3)                      -
    VOLUMES(000000) )                      -
    DATA (NAME(FETCH.TEST.VS.DATA))       -
    INDEX (NAME(FETCH.TEST.VS.INDEX))
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
 DDUMMY   RECORD                      !! DO NOT ALTER !!
 EEXAMPLE RECORD   REMOVE THIS LINE IF EXAMPLES NOT REQUIRED
/*
"""

def extract_member_name(data_set):
    start = data_set.find("(")
    member = ""
    for i in range(start + 1, len(data_set)):
        if data_set[i] == ")":
            break
        member += data_set[i]
    return member

def create_and_populate_test_ps_vb(ansible_zos_module):
    params=dict(
        name=TEST_PS_VB,
        type='SEQ',
        record_format='VB',
        record_length='3180',
        block_size='3190'
    )
    ansible_zos_module.all.zos_data_set(**params)
    params = dict(
        src=TEST_PS_VB,
        block=TEST_DATA
    )
    ansible_zos_module.all.zos_blockinfile(**params)


def delete_test_ps_vb(ansible_zos_module):
    params=dict(
        name=TEST_PS_VB,
        state='absent'
    )
    ansible_zos_module.all.zos_data_set(**params)


def test_fetch_uss_file_not_present_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src="/etc/profile", dest="/tmp/", flat=True)
    dest_path = "/tmp/profile"
    results = None

    try:
        results = hosts.all.zos_fetch(**params)
        print(results.contacted.values())

        for result in results.contacted.values():

            assert result.get("changed") is True
            assert result.get("data_set_type") == "USS"
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_uss_file_replace_on_local_machine(ansible_zos_module):
    open("/tmp/profile", "w").close()
    hosts = ansible_zos_module
    params = dict(src="/etc/profile", dest="/tmp/", flat=True)
    dest_path = "/tmp/profile"
    local_checksum = checksum(dest_path, hash_func=sha256)

    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("checksum") != local_checksum
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
    finally:
        os.remove(dest_path)


def test_fetch_uss_file_present_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src="/etc/profile", dest="/tmp/", flat=True)
    dest_path = "/tmp/profile"
    hosts.all.zos_fetch(**params)
    local_checksum = checksum(dest_path, hash_func=sha256)

    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("checksum") == local_checksum
            assert result.get("module_stderr") is None
    finally:
        os.remove(dest_path)


def test_fetch_sequential_data_set_fixed_block(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=TEST_PS, state="present", size="5m")
    hosts.all.zos_lineinfile(path=TEST_PS, line="unset ZOAU_ROOT", state="present")
    params = dict(src=TEST_PS, dest="/tmp/", flat=True)
    dest_path = "/tmp/" + TEST_PS
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
    finally:
        hosts.all.zos_data_set(name=TEST_PS, state="absent")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_sequential_data_set_variable_block(ansible_zos_module):
    hosts = ansible_zos_module
    create_and_populate_test_ps_vb(ansible_zos_module)
    params = dict(src=TEST_PS_VB, dest="/tmp/", flat=True)
    dest_path = "/tmp/" + TEST_PS_VB
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        delete_test_ps_vb(ansible_zos_module)


def test_fetch_partitioned_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=TEST_PDS, state="present")
    hosts.all.zos_lineinfile(path=TEST_PDS, line="unset ZOAU_ROOT", state="present")
    params = dict(src=TEST_PDS, dest="/tmp/", flat=True)
    dest_path = "/tmp/" + TEST_PDS
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Partitioned"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
            assert os.path.isdir(dest_path)
    finally:
        hosts.all.zos_data_set(name=TEST_PDS, state="absent")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


def test_fetch_vsam_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    TEMP_JCL_PATH = "/tmp/ansible"
    dest_path = "/tmp/" + TEST_VSAM
    try:
        # start by creating the vsam dataset (could use a helper instead? )
        hosts.all.file(path=TEMP_JCL_PATH, state="directory")
        hosts.all.shell(
            cmd="echo {0} > {1}/SAMPLE".format(quote(KSDS_CREATE_JCL), TEMP_JCL_PATH)
        )
        hosts.all.zos_job_submit(
            src="{0}/SAMPLE".format(TEMP_JCL_PATH), location="USS", wait=True
        )
        hosts.all.zos_copy(content=TEST_DATA, dest=USS_FILE)
        hosts.all.zos_encode(
            src=USS_FILE,
            dest=TEST_VSAM,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        params = dict(src=TEST_VSAM, dest="/tmp/", flat=True, is_binary=True)
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "VSAM"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
            file = open(dest_path, 'r')
            read_file = file.read()
            print(read_file)
            assert read_file == TEST_DATA

    finally:
        if os.path.exists(dest_path):
            None
            os.remove(dest_path)
        hosts.all.file(path=USS_FILE, state="absent")
        hosts.all.file(path=TEMP_JCL_PATH, state="absent")


def test_fetch_vsam_empty_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src=TEST_EMPTY_VSAM, dest="/tmp/", flat=True)
    dest_path = "/tmp/" + TEST_EMPTY_VSAM
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "VSAM"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_member_in_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=TEST_PDS, state="present")
    hosts.all.zos_data_set(name=TEST_PDS_MEMBER, type="member")
    hosts.all.zos_lineinfile(path=TEST_PDS_MEMBER, line="unset ZOAU_ROOT", state="present")
    params = dict(
        src=TEST_PDS_MEMBER, dest="/tmp/", flat=True, is_binary=True
    )
    dest_path = "/tmp/" + extract_member_name(TEST_PDS_MEMBER)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Partitioned"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert result.get("is_binary") is True
            assert os.path.exists(dest_path)
            assert os.path.isfile(dest_path)
    finally:
        hosts.all.zos_data_set(name=TEST_PDS, state="absent")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_sequential_data_set_in_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=TEST_PS, state="present")
    hosts.all.zos_lineinfile(path=TEST_PS, line="unset ZOAU_ROOT", state="present")
    params = dict(src=TEST_PS, dest="/tmp/", flat=True, is_binary=True)
    dest_path = "/tmp/" + TEST_PS
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert result.get("is_binary") is True
            assert os.path.exists(dest_path)
    finally:
        hosts.all.zos_data_set(name=TEST_PS, state="absent")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=TEST_PDS, state="present")
    hosts.all.zos_lineinfile(path=TEST_PDS, line="unset ZOAU_ROOT", state="present")
    params = dict(src=TEST_PDS, dest="/tmp/", flat=True, is_binary=True)
    dest_path = "/tmp/" + TEST_PDS
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Partitioned"
            assert result.get("module_stderr") is None
            assert result.get("is_binary") is True
            assert os.path.exists(dest_path)
            assert os.path.isdir(dest_path)
    finally:
        hosts.all.zos_data_set(name=TEST_PDS, state="absent")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


def test_fetch_sequential_data_set_empty(ansible_zos_module):
    hosts = ansible_zos_module
    src = "USER.TEST.EMPTY.SEQ"
    params = dict(src=src, dest="/tmp/", flat=True)
    dest_path = "/tmp/" + src
    try:
        hosts.all.zos_data_set(name=src, type='seq', state='present')
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
            assert os.stat(dest_path).st_size == 0
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        hosts.all.zos_data_set(name=src, state='absent')


def test_fetch_partitioned_data_set_empty_fails(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="M",
        record_format="fba",
        record_length=25,
    )
    params = dict(src=pds_name, dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert "stderr" in result.keys()
    finally:
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_fetch_partitioned_data_set_member_empty(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="M",
        record_format="fba",
        record_length=25,
    )
    hosts.all.zos_data_set(name=pds_name + "(MYDATA)", type="MEMBER", replace="yes")
    params = dict(src="ZOS.FETCH.TEST.PDS(MYDATA)", dest="/tmp/", flat=True)
    dest_path = "/tmp/MYDATA"
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Partitioned"
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
            assert os.stat(dest_path).st_size == 0
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_fetch_missing_uss_file_does_not_fail(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src="/tmp/dummy_file_on_remote_host",
        dest="/tmp/",
        flat=True,
        fail_on_missing=False,
    )
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert "note" in result.keys()
            assert result.get("module_stderr") is None
    except Exception:
        raise


def test_fetch_missing_uss_file_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src="/tmp/dummy_file_on_remote_host", dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
    except Exception:
        raise


def test_fetch_missing_mvs_data_set_does_not_fail(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(
        src="FETCH.TEST.DATA.SET", dest="/tmp/", flat=True, fail_on_missing=False
    )
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert "note" in result.keys()
            assert result.get("module_stderr") is None
            assert not os.path.exists("/tmp/FETCH.TEST.DATA.SET")
    except Exception:
        raise


def test_fetch_partitioned_data_set_member_missing_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src=TEST_PDS + "(DUMMY)", dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert "stderr" in result.keys()
    except Exception:
        raise


def test_fetch_mvs_data_set_missing_fails(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(src="ZOS.FETCH.TEST.PDS", dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert result.get("stderr") != ""
    except Exception:
        raise


def test_fetch_sequential_data_set_replace_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = TEST_PS
    hosts.all.zos_data_set(name=TEST_PS, state="present")
    hosts.all.zos_lineinfile(path=TEST_PS, line="unset ZOAU_ROOT", state="present")
    dest_path = "/tmp/" + ds_name
    with open(dest_path, "w") as infile:
        infile.write(DUMMY_DATA)

    local_checksum = checksum(dest_path, hash_func=sha256)
    params = dict(src=ds_name, dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert checksum(dest_path, hash_func=sha256) != local_checksum
    finally:
        hosts.all.zos_data_set(name=TEST_PS, state="absent")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_replace_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = "ZOS.FETCH.TEST.PDS"
    dest_path = "/tmp/" + pds_name
    full_path = dest_path + "/MYDATA"
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="M",
        record_format="fba",
        record_length=25,
    )
    hosts.all.zos_data_set(name=pds_name + "(MYDATA)", type="MEMBER", replace="yes")
    os.mkdir(dest_path)
    with open(full_path, "w") as infile:
        infile.write(DUMMY_DATA)
    with open(dest_path + "/NEWMEM", "w") as infile:
        infile.write(DUMMY_DATA)

    prev_timestamp = os.path.getmtime(dest_path)
    params = dict(src=pds_name, dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert os.path.getmtime(dest_path) != prev_timestamp
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_fetch_uss_file_insufficient_write_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/profile"
    with open(dest_path, "w"):
        pass
    os.chmod(dest_path, stat.S_IREAD)
    params = dict(src="/etc/profile", dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_pds_dir_insufficient_write_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/" + TEST_PDS
    os.mkdir(dest_path)
    os.chmod(dest_path, stat.S_IREAD)
    params = dict(src=TEST_PDS, dest="/tmp/", flat=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


def test_fetch_use_data_set_qualifier(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = "/tmp/TEST.USER.QUAL"
    hosts.all.zos_data_set(name="OMVSADM.TEST.USER.QUAL", type="seq", state="present")
    params = dict(src="TEST.USER.QUAL", dest="/tmp/", flat=True, use_qualifier=True)
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        hosts.all.zos_data_set(src="OMVSADM.TEST.USER.QUAL", state="absent")


def test_fetch_flat_create_dirs(ansible_zos_module, z_python_interpreter):
    z_int = z_python_interpreter
    hosts = ansible_zos_module
    remote_host = z_int[1].get("inventory").strip(",")
    dest_path = "/tmp/{0}/etc/ssh/ssh_config".format(remote_host)
    params = dict(src="/etc/ssh/ssh_config", dest="/tmp/", flat=False)
    try:
        shutil.rmtree("/tmp/" + remote_host)
    except FileNotFoundError:
        pass
    try:
        assert not os.path.exists(dest_path)
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree("/tmp/" + remote_host)
