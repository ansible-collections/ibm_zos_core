# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2025
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
import re
import pytest
import string
import random
import tempfile

from hashlib import sha256
from ansible.utils.hashing import checksum
from datetime import datetime

from shellescape import quote

# pylint: disable-next=import-error
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
# pylint: disable-next=import-error
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

TMP_DIRECTORY = '/tmp/'
DUMMY_DATA = """DUMMY DATA == LINE 01 ==
DUMMY DATA == LINE 02 ==
DUMMY DATA == LINE 03 ==
"""

FROM_ENCODING = "IBM-1047"
TO_ENCODING = "ISO8859-1"

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
    SET MAXCC=0
    DEFINE CLUSTER                          -
    (NAME({1})                  -
    INDEXED                                -
    KEYS(4 0)                            -
    RECSZ(200 200)                         -
    RECORDS(100)                           -
    SHAREOPTIONS(2 3)                      -
    VOLUMES({0}) )                      -
    DATA (NAME({1}.DATA))       -
    INDEX (NAME({1}.INDEX))
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

VSAM_RECORDS = """00000001A record
00000002A record
00000003A record
"""


def extract_member_name(data_set):
    start = data_set.find("(")
    member = ""
    for i in range(start + 1, len(data_set)):
        if data_set[i] == ")":
            break
        member += data_set[i]
    return member

def create_and_populate_test_ps_vb(ansible_zos_module, name):
    params={
        "name":name,
        "type":'seq',
        "record_format":'vb',
        "record_length":'3180',
        "block_size":'3190'
    }
    ansible_zos_module.all.zos_data_set(**params)
    ansible_zos_module.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{name}\"")


def delete_test_ps_vb(ansible_zos_module, name):
    params={
        "name":name,
        "state":'absent'
    }
    ansible_zos_module.all.zos_data_set(**params)


def create_vsam_data_set(hosts, name, ds_type, key_length=None, key_offset=None):
    """Creates a new VSAM on the system.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the VSAM data set.
        type (str) -- Type of the VSAM (ksds, esds, rrds, lds)
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


def create_vsam_data_set(hosts, name, ds_type, key_length=None, key_offset=None):
    """Creates a new VSAM on the system.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the VSAM data set.
        type (str) -- Type of the VSAM (ksds, esds, rrds, lds)
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


def test_fetch_uss_file_not_present_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "src":"/etc/profile",
        "dest":"/tmp/",
        "flat":True
    }
    dest_path = "/tmp/profile"
    results = None

    try:
        results = hosts.all.zos_fetch(**params)

        for result in results.contacted.values():

            assert result.get("changed") is True
            assert result.get("data_set_type") == "USS"
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_uss_file_replace_on_local_machine(ansible_zos_module):
    with open("/tmp/profile", "w",encoding="utf-8") as file:
        file.close()
    hosts = ansible_zos_module
    params = {
        "src":"/etc/profile",
        "dest":"/tmp/",
        "flat":True
    }
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
    params = {
        "src":"/etc/profile",
        "dest": "/tmp/",
        "flat":True
    }
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
    TEST_PS = get_tmp_ds_name()
    hosts.all.zos_data_set(
        name=TEST_PS,
        state="present",
        type="seq",
        space_type="m",
        space_primary=5
    )
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PS}\"")
    params = {
        "src":TEST_PS,
        "dest":"/tmp/",
        "flat":True
    }
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
    TEST_PS_VB = get_tmp_ds_name(3)
    create_and_populate_test_ps_vb(ansible_zos_module, TEST_PS_VB)
    params = {
        "src":TEST_PS_VB,
        "dest":"/tmp/",
        "flat":True
    }
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
        delete_test_ps_vb(ansible_zos_module, TEST_PS_VB)


def test_fetch_partitioned_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PDS = get_tmp_ds_name()
    hosts.all.zos_data_set(name=TEST_PDS, state="present", type="pdse")
    TEST_PDS_MEMBER = TEST_PDS + "(MEM)"
    hosts.all.zos_data_set(name=TEST_PDS_MEMBER, type="member")
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PDS_MEMBER}\"")
    params = {
        "src":TEST_PDS,
        "dest":"/tmp/",
        "flat":True
    }
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


def test_fetch_vsam_data_set(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    temp_jcl_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='FE')
    test_vsam = get_tmp_ds_name()
    dest_path = "/tmp/" + test_vsam
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    uss_file = get_random_file_name(dir=TMP_DIRECTORY, prefix='FE')
    try:
        # start by creating the vsam dataset (could use a helper instead? )
        hosts.all.file(path=temp_jcl_path, state="directory")
        hosts.all.shell(
            cmd=f"echo {quote(KSDS_CREATE_JCL.format(volume_1, test_vsam))} > {temp_jcl_path}/SAMPLE"
        )
        hosts.all.zos_job_submit(
            src=f"{temp_jcl_path}/SAMPLE", remote_src=True, wait_time=30
        )
        hosts.all.shell(cmd=f"echo \"{TEST_DATA}\\c\" > {uss_file}")
        hosts.all.zos_encode(
            src=uss_file,
            dest=test_vsam,
            encoding={
                "from": FROM_ENCODING,
                "to": TO_ENCODING,
            },
        )

        params = {
            "src":test_vsam,
            "dest":"/tmp/",
            "flat":True,
            "is_binary":True
        }
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "VSAM"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
            file = open(dest_path, 'r',encoding="utf-8")
            read_file = file.read()
            assert read_file == TEST_DATA

    finally:
        if os.path.exists(dest_path):
            None
            os.remove(dest_path)
        hosts.all.file(path=uss_file, state="absent")
        hosts.all.file(path=temp_jcl_path, state="absent")


def test_fetch_vsam_empty_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = "TEST.VSAM.DATA"
    create_vsam_data_set(hosts, src_ds, "ksds", key_length=12, key_offset=0)
    params = {
        "src":src_ds,
        "dest":"/tmp/",
        "flat":True
    }
    dest_path = "/tmp/" + src_ds
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "VSAM"
            assert result.get("module_stderr") is None
            assert result.get("dest") == dest_path
            assert os.path.exists(dest_path)
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def test_fetch_partitioned_data_set_member_in_binary_mode(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PDS = get_tmp_ds_name()
    hosts.all.zos_data_set(name=TEST_PDS, state="present")
    TEST_PDS_MEMBER = TEST_PDS + "(MEM)"
    hosts.all.zos_data_set(name=TEST_PDS_MEMBER, type="member")
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PDS_MEMBER}\"")
    params = {
        "src":TEST_PDS_MEMBER,
        "dest":"/tmp/",
        "flat":True,
        "is_binary":True
    }
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
    TEST_PS = get_tmp_ds_name()
    hosts.all.zos_data_set(
        name=TEST_PS,
        state="present",
        type="seq",
        space_type="m",
        space_primary=5
    )
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PS}\"")
    params = {
        "src":TEST_PS,
        "dest":"/tmp/",
        "flat":True,
        "is_binary":True
    }
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
    TEST_PDS = get_tmp_ds_name()
    hosts.all.zos_data_set(name=TEST_PDS, state="present", type="pdse")
    TEST_PDS_MEMBER = TEST_PDS + "(MEM)"
    hosts.all.zos_data_set(name=TEST_PDS_MEMBER, type="member")
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PDS_MEMBER}\"")
    params = {
        "src":TEST_PDS,
        "dest":"/tmp/",
        "flat":True,
        "is_binary":True
    }
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
    src = get_tmp_ds_name()
    params = {
        "src":src,
        "dest":"/tmp/",
        "flat":True
    }
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
    pds_name = get_tmp_ds_name()
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="m",
        record_format="fba",
        record_length=25,
    )
    params = {
        "src":pds_name,
        "dest":"/tmp/",
        "flat":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert "stderr" in result.keys()
    finally:
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_fetch_partitioned_data_set_member_empty(ansible_zos_module):
    hosts = ansible_zos_module
    pds_name = get_tmp_ds_name()
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="m",
        record_format="fba",
        record_length=25,
    )
    dest_path = get_random_file_name(dir=TMP_DIRECTORY, prefix='FE')
    hosts.all.zos_data_set(name=pds_name, type="pds")
    hosts.all.zos_data_set(name=pds_name + "(MYDATA)", type="member", replace="yes")
    params = {
        "src":pds_name + "(MYDATA)",
        "dest": dest_path,
        "flat":True
    }
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
    params = {
        "src":"/tmp/dummy_file_on_remote_host",
        "dest":"/tmp/",
        "flat":True,
        "fail_on_missing":False,
    }
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
    params = {
        "src":"/tmp/dummy_file_on_remote_host",
        "dest":"/tmp/",
        "flat":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
    except Exception:
        raise


def test_fetch_missing_mvs_data_set_does_not_fail(ansible_zos_module):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()
    params = {
        "src":src,
        "dest":"/tmp/",
        "flat":True,
        "fail_on_missing":False
    }
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
    TEST_PDS = get_tmp_ds_name()
    params = {
        "src":TEST_PDS + "(DUMMY)",
        "dest":"/tmp/",
        "flat":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert "stderr" in result.keys()
    except Exception:
        raise


def test_fetch_mvs_data_set_missing_fails(ansible_zos_module):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()
    params = {
        "src":src,
        "dest":"/tmp/",
        "flat":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
            assert result.get("stderr") != ""
    except Exception:
        raise


def test_fetch_sequential_data_set_replace_on_local_machine(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PS = get_tmp_ds_name()
    hosts.all.zos_data_set(
        name=TEST_PS,
        state="present",
        type="seq",
        space_type="m",
        space_primary=5
    )
    hosts.all.zos_data_set(name=TEST_PS, state="present")
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PS}\"")
    dest_path = "/tmp/" + TEST_PS
    with open(dest_path, "w", encoding="utf-8") as infile:
        infile.write(DUMMY_DATA)

    local_checksum = checksum(dest_path, hash_func=sha256)
    params = {
        "src":TEST_PS,
        "dest":"/tmp/",
        "flat":True
    }
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
    pds_name = get_tmp_ds_name()
    dest_path = "/tmp/" + pds_name
    full_path = dest_path + "/MYDATA"
    pds_name_mem = pds_name + "(MYDATA)"
    hosts.all.zos_data_set(
        name=pds_name,
        type="pds",
        space_primary=5,
        space_type="m",
        record_format="fba",
        record_length=25,
    )
    hosts.all.zos_data_set(name=pds_name + "(MYDATA)", type="member", replace="yes")
    os.mkdir(dest_path)
    with open(full_path, "w", encoding="utf-8") as infile:
        infile.write(DUMMY_DATA)
    with open(dest_path + "/NEWMEM", "w", encoding="utf-8") as infile:
        infile.write(DUMMY_DATA)

    prev_timestamp = os.path.getmtime(dest_path)
    params = {
        "src":pds_name,
        "dest":"/tmp/",
        "flat":True
    }
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
    dest_path = tempfile.NamedTemporaryFile(mode='r+b')
    os.chmod(dest_path.name, stat.S_IREAD)
    params = {
        "src":"/etc/profile",
        "dest": dest_path.name,
        "flat":True
    }
    results = hosts.all.zos_fetch(**params)
    for result in results.contacted.values():
        assert "msg" in result.keys()
    dest_path.close()


def test_fetch_pds_dir_insufficient_write_permission_fails(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PDS = get_tmp_ds_name()
    dest_path = "/tmp/" + TEST_PDS
    os.mkdir(dest_path)
    os.chmod(dest_path, stat.S_IREAD)
    params = {
        "src":TEST_PDS,
        "dest":"/tmp/",
        "flat":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert "msg" in result.keys()
    finally:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


def test_fetch_use_data_set_qualifier(ansible_zos_module):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()[:25]
    dest_path = "/tmp/"+ src
    results = hosts.all.shell(cmd="echo $USER")
    for result in results.contacted.values():
            hlq = result.get("stdout")
    hosts.all.zos_data_set(name=hlq + '.' + src, type="seq", state="present")
    params = {
        "src":src,
        "dest":"/tmp/",
        "flat":True,
        "use_qualifier":True
    }
    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None
            assert os.path.exists(dest_path)
    finally:
        if os.path.exists(dest_path):
            os.remove(dest_path)
        hosts.all.zos_data_set(name="{0}.".format(hlq) + src, state="absent")


def test_fetch_flat_create_dirs(ansible_zos_module, z_python_interpreter):
    z_int = z_python_interpreter
    hosts = ansible_zos_module
    remote_host = z_int[2].get("inventory").strip(",")
    dest_path = f"/tmp/{remote_host}/etc/ssh/ssh_config"
    params = {
        "src":"/etc/ssh/ssh_config",
        "dest":"/tmp/",
        "flat":False
    }
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


def test_fetch_sequential_data_set_with_special_chars(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PS = get_tmp_ds_name(symbols=True)

    hosts.all.zos_data_set(
        name=TEST_PS,
        state="present",
        type="seq",
        space_type="m",
        space_primary=5
    )
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_PS}\"")
    params = dict(src=TEST_PS, dest="/tmp/", flat=True)
    dest_path = f"/tmp/{TEST_PS}"

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


@pytest.mark.parametrize("generation", ["0", "-1"])
def test_fetch_gds_from_gdg(ansible_zos_module, generation):
    hosts = ansible_zos_module
    TEST_GDG = get_tmp_ds_name()
    TEST_GDS = f"{TEST_GDG}({generation})"

    hosts.all.zos_data_set(name=TEST_GDG, state="present", type="gdg", limit=3)
    hosts.all.zos_data_set(name=f"{TEST_GDG}(+1)", state="present", type="seq")
    hosts.all.zos_data_set(name=f"{TEST_GDG}(+1)", state="present", type="seq")

    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_GDS}\"")
    params = dict(src=TEST_GDS, dest="/tmp/", flat=True)
    dest_path = ""

    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Sequential"
            assert result.get("module_stderr") is None

            # Checking that we got a dest of the form: ANSIBLE.DATA.SET.G0001V01.
            dest_path = result.get("dest", "")
            dest_pattern = r"G[0-9]+V[0-9]+"

            assert TEST_GDG in dest_path
            assert re.fullmatch(dest_pattern, dest_path.split(".")[-1])
            assert os.path.exists(dest_path)
    finally:
        hosts.all.zos_data_set(name=f"{TEST_GDG}(-1)", state="absent")
        hosts.all.zos_data_set(name=f"{TEST_GDG}(0)", state="absent")
        hosts.all.zos_data_set(name=TEST_GDG, state="absent")

        if dest_path != "" and os.path.exists(dest_path):
            os.remove(dest_path)


def test_error_fetch_inexistent_gds(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_GDG = get_tmp_ds_name()
    TEST_GDS = f"{TEST_GDG}(+1)"

    hosts.all.zos_data_set(name=TEST_GDG, state="present", type="gdg", limit=3)
    hosts.all.zos_data_set(name=f"{TEST_GDG}(+1)", state="present", type="seq")

    params = dict(src=TEST_GDS, dest="/tmp/", flat=True)

    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed") is True
            assert "does not exist" in result.get("msg", "")

    finally:
        hosts.all.zos_data_set(name=f"{TEST_GDG}(0)", state="absent")
        hosts.all.zos_data_set(name=TEST_GDG, state="absent")


def test_fetch_gdg(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_GDG = get_tmp_ds_name()

    hosts.all.zos_data_set(name=TEST_GDG, state="present", type="gdg", limit=3)
    hosts.all.zos_data_set(name=f"{TEST_GDG}(+1)", state="present", type="seq")
    hosts.all.zos_data_set(name=f"{TEST_GDG}(+1)", state="present", type="seq")

    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_GDG}(-1)\"")
    hosts.all.shell(cmd=f"decho \"{TEST_DATA}\" \"{TEST_GDG}(0)\"")

    params = dict(src=TEST_GDG, dest="/tmp/", flat=True)

    try:
        results = hosts.all.zos_fetch(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "Generation Data Group"
            assert result.get("module_stderr") is None

            # Checking that we got a dest of the form: ANSIBLE.DATA.SET.G0001V01.
            dest_path = result.get("dest", "")
            dest_pattern = r"G[0-9]+V[0-9]+"

            assert TEST_GDG in dest_path
            assert os.path.exists(dest_path)

            # Checking that the contents of the dir match with what we would expect to get:
            # Multiple generation data sets conforming to the pattern defined above.
            for file_name in os.listdir(dest_path):
                assert re.fullmatch(dest_pattern, file_name.split(".")[-1])
                assert os.path.exists(os.path.join(dest_path, file_name))

    finally:
        hosts.all.zos_data_set(name=f"{TEST_GDG}(-1)", state="absent")
        hosts.all.zos_data_set(name=f"{TEST_GDG}(0)", state="absent")
        hosts.all.zos_data_set(name=TEST_GDG, state="absent")

        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)


@pytest.mark.parametrize("relative_path", ["tmp/", ".", "../tmp/", "~/tmp/"])
def test_fetch_uss_file_relative_path_not_present_on_local_machine(ansible_zos_module, relative_path):
    hosts = ansible_zos_module
    current_working_directory = os.getcwd()
    src = "/etc/profile"

    # If the test suite is running on root to avoid an issue we check the current directory
    # Also, user can run the tests from ibm_zos_core or tests folder, so this will give us the absolute path of our working dir.
    if relative_path == "../tmp/":
        aux = os.path.basename(os.path.normpath(current_working_directory))
        relative_path = "../" + aux + "/tmp/"

    params = {
        "src": src,
        "dest": relative_path,
        "flat":True
    }

    # Case to create the dest path to verify allow running on any path.
    # There are some relative paths for which we need to change our cwd to be able to validate that
    # the path returned by the module is correct.
    if relative_path == "~/tmp/":
        dest = os.path.expanduser("~")
        dest = dest + "/tmp"
    elif relative_path == ".":
        dest = current_working_directory + "/profile"
    else:
        dest = current_working_directory + "/tmp"

    try:
        results = hosts.all.zos_fetch(**params)

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("data_set_type") == "USS"
            assert result.get("module_stderr") is None
            assert dest == result.get("dest")
            dest = result.get("dest")

    finally:
        if os.path.exists(dest):
            os.remove(dest)
