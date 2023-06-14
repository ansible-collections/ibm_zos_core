#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2022
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

SHELL_EXECUTABLE = "/bin/sh"
USS_TEMP_DIR = "/tmp/archive"
USS_TEST_FILES = {  f"{USS_TEMP_DIR}/foo.txt" : "foo sample content",
                    f"{USS_TEMP_DIR}/bar.txt": "bar sample content", 
                    f"{USS_TEMP_DIR}/empty.txt":""}
USS_EXCLUSION_FILE = f"{USS_TEMP_DIR}/foo.txt"
TEST_PS = "USER.PRIVATE.TESTDS"
TEST_PDS = "USER.PRIVATE.TESTPDS"
HLQ = "USER"
MVS_DEST_ARCHIVE = "USER.PRIVATE.ARCHIVE"

USS_DEST_ARCHIVE = "testarchive.dzp"

STATE_ABSENT = 'absent'
STATE_ARCHIVED = 'archive'
STATE_COMPRESSED = 'compress'
STATE_INCOMPLETE = 'incomplete'

USS_FORMATS = ['tar', 'gz', 'bz2', 'zip', 'pax']
# USS_FORMATS = ['pax']

def set_uss_test_env(ansible_zos_module, test_files):
    for key, value in test_files.items():
        ansible_zos_module.all.shell(
            cmd=f"echo \"{value}\" > \"{key}\"",
            executable=SHELL_EXECUTABLE,
        )


def create_multiple_data_sets(ansible_zos_module, base_name, n, type, ):
    test_data_sets = []
    for i in range(n):
        curr_ds = dict(name=base_name+str(i),
                       type=type,
                       state="present",
                       replace=True,
                       force=True)
        test_data_sets.append(curr_ds)

        
    # Create data sets in batch
    ansible_zos_module.all.zos_data_set(
        batch=test_data_sets
    )
    return test_data_sets


def create_multiple_members(ansible_zos_module, pds_name, member_base_name, n):
    test_members = []
    for i in range(n):
        curr_ds = dict(name="{0}({1})".format(pds_name, member_base_name+str(i)),
                       type="member",
                       state="present",
                       replace=True,
                       force=True)
        test_members.append(curr_ds)
    ansible_zos_module.all.zos_data_set(
        batch=test_members
    )
    return test_members


######################################################
#
# USS TEST
#
######################################################
"""
List of tests:
- test_uss_unarchive
- test_uss_unarchive_include
- test_uss_unarchive_exclude
- test_uss_unarchive_list
"""


# Core functionality tests
# Test unarchive with no options
@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_unarchive(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive( path=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        print(archive_result.contacted.values())
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            path=dest,
            format=dict(
                name=format
            ),
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                print(c_result)
                for file in USS_TEST_FILES.keys():
                    assert file[len(USS_TEMP_DIR)+1:] in c_result.get("stdout")
                
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")

@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_unarchive_include(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive( path=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        print(archive_result.contacted.values())
        uss_files = [file[len(USS_TEMP_DIR)+1:] for file in USS_TEST_FILES]
        include_list = uss_files[:2]
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            path=dest,
            format=dict(
                name=format
            ),
            include=include_list,
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                print(c_result)
                for file in uss_files:
                    if file in include_list:
                        assert file in c_result.get("stdout")
                    else:
                        assert file not in c_result.get("stdout")
                
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")

@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_unarchive_exclude(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive( path=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        print(archive_result.contacted.values())
        # remove files
        uss_files = [file[len(USS_TEMP_DIR)+1:] for file in USS_TEST_FILES]
        exclude_list = uss_files[:2]
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            path=dest,
            format=dict(
                name=format
            ),
            exclude=exclude_list,
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("failed", False) is False
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                print(c_result)
                for file in uss_files:
                    if file in exclude_list:
                        assert file not in c_result.get("stdout")
                    else:
                        assert file in c_result.get("stdout")
                
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")

@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_unarchive_list(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive( path=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        print(archive_result.contacted.values())
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            path=dest,
            format=dict(
                name=format
            ),
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            for file in USS_TEST_FILES.keys():
                    assert file[len(USS_TEMP_DIR)+1:] in result.get("targets")
                
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


######################################################################
#
#   MVS data sets tests
#
######################################################################

"""
List of tests:
- test_mvs_unarchive_single_data_set
- test_mvs_unarchive_single_data_set_use_adrdssu
- test_mvs_unarchive_multiple_data_sets_use_adrdssu
- test_mvs_unarchive_multiple_data_sets_include
- test_mvs_unarchive_multiple_data_sets_exclude
- test_mvs_unarchive_list
- test_mvs_unarchive_force
- test_mvs_unarchive_remote_src

"""



@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ", members=[""]),
        dict(name=TEST_PDS, dstype="PDS", members=["MEM1", "MEM2"]),
        dict(name=TEST_PDS, dstype="PDSE", members=["MEM1", "MEM2"]),
        ]
)
@pytest.mark.parametrize(
    "record_length", [80, 120, 1024]
)
@pytest.mark.parametrize(
    # "record_format", ["FB", "VB", "FBA", "VBA", "U"],
    "record_format", ["FB", "VB",],
)
def test_mvs_unarchive_single_dataset(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        # Clean env
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=data_set.get("name"),
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{data_set.get('name')}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src
        test_line = "this is a test line"
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{data_set.get('name')}"
            else:
                ds_to_write = f"{data_set.get('name')}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="SPACK")
        archive_result = hosts.all.zos_archive(
            path=data_set.get("name"),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        
        # assert response is positive 
        for result in archive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("dest") == MVS_DEST_ARCHIVE
            assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert MVS_DEST_ARCHIVE in c_result.get("stdout")
        
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        
        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            dest_data_set=dict(name=data_set.get("name"),
                               type=data_set.get("dstype"),
                               record_format=record_format, 
                               record_length=record_length)
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            # assert result.get("dest") == MVS_DEST_ARCHIVE
            # assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert data_set.get("name") in c_result.get("stdout")
        
    finally:
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ", members=[""]),
        dict(name=TEST_PDS, dstype="PDS", members=["MEM1", "MEM2"]),
        dict(name=TEST_PDS, dstype="PDSE", members=["MEM1", "MEM2"]),
        ]
)
@pytest.mark.parametrize(
    "record_length", [80, 120, 1024]
)
@pytest.mark.parametrize(
    # "record_format", ["FB", "VB", "FBA", "VBA", "U"],
    "record_format", ["FB", "VB",],
)
def test_mvs_unarchive_single_dataset_use_adrdssu(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        # Clean env
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=data_set.get("name"),
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{data_set.get('name')}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src
        test_line = "this is a test line"
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{data_set.get('name')}"
            else:
                ds_to_write = f"{data_set.get('name')}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        format_dict["format_options"] = dict(use_adrdssu=True)
        if format == "terse":
            format_dict["format_options"].update(terse_pack="SPACK")
        archive_result = hosts.all.zos_archive(
            path=data_set.get("name"),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        
        # assert response is positive 
        for result in archive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("dest") == MVS_DEST_ARCHIVE
            assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert MVS_DEST_ARCHIVE in c_result.get("stdout")
        
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        
        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            # assert result.get("dest") == MVS_DEST_ARCHIVE
            # assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert data_set.get("name") in c_result.get("stdout")
        
    finally:
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ"),
        dict(name=TEST_PDS, dstype="PDS"),
        dict(name=TEST_PDS, dstype="PDSE"),
        ]
)
def test_mvs_unarchive_multiple_dataset_use_adrdssu(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=data_set.get("name"),
                                    n=1,
                                    type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["PDS", "PDSE"]:
            target_member_list = []
            for ds in target_ds_list:
                target_member_list.extend(
                    create_multiple_members(ansible_zos_module=hosts,
                                        pds_name=ds.get("name"),
                                        member_base_name="MEM",
                                        n=3
                    )
                )
            ds_to_write = target_member_list
        # Write some content into src
        test_line = "this is a test line"
        for ds in ds_to_write:
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds.get("name")))
        
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="SPACK")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            path="{0}*".format(data_set.get("name")),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote datasets from host
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            force=True
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("path") == MVS_DEST_ARCHIVE
            
            cmd_result = hosts.all.shell(cmd="dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                print("dls result : {0}".format(c_result))
                for target_ds in target_ds_list:
                    assert target_ds.get("name") in result.get("targets")
                    assert target_ds.get("name") in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ"),
        dict(name=TEST_PDS, dstype="PDS"),
        dict(name=TEST_PDS, dstype="PDSE"),
        ]
)
def test_mvs_unarchive_multiple_dataset_use_adrdssu_include(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=data_set.get("name"),
                                    n=2,
                                    type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["PDS", "PDSE"]:
            target_member_list = []
            for ds in target_ds_list:
                target_member_list.extend(
                    create_multiple_members(ansible_zos_module=hosts,
                                        pds_name=ds.get("name"),
                                        member_base_name="MEM",
                                        n=3
                    )
                )
            ds_to_write = target_member_list
        # Write some content into src
        test_line = "this is a test line"
        for ds in ds_to_write:
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds.get("name")))
        
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="SPACK")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            path="{0}*".format(data_set.get("name")),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote datasets from host
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        include_ds = "{0}0".format(data_set.get("name"))
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            include=[include_ds],
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("path") == MVS_DEST_ARCHIVE
            
            cmd_result = hosts.all.shell(cmd="dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                print("dls result : {0}".format(c_result))
                for target_ds in target_ds_list:
                    if target_ds.get("name") == include_ds:
                        assert target_ds.get("name") in result.get("targets")
                        assert target_ds.get("name") in c_result.get("stdout")
                    else:
                        assert target_ds.get("name") not in result.get("targets")
                        assert target_ds.get("name") not in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ"),
        dict(name=TEST_PDS, dstype="PDS"),
        dict(name=TEST_PDS, dstype="PDSE"),
        ]
)
def test_mvs_unarchive_multiple_dataset_use_adrdssu_exclude(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=data_set.get("name"),
                                    n=2,
                                    type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["PDS", "PDSE"]:
            target_member_list = []
            for ds in target_ds_list:
                target_member_list.extend(
                    create_multiple_members(ansible_zos_module=hosts,
                                        pds_name=ds.get("name"),
                                        member_base_name="MEM",
                                        n=3
                    )
                )
            ds_to_write = target_member_list
        # Write some content into src
        test_line = "this is a test line"
        for ds in ds_to_write:
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds.get("name")))
        
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="SPACK")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            path="{0}*".format(data_set.get("name")),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote datasets from host
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        exclude_ds = "{0}0".format(data_set.get("name"))
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            exclude=[exclude_ds],
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("path") == MVS_DEST_ARCHIVE
            
            cmd_result = hosts.all.shell(cmd="dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                print("dls result : {0}".format(c_result))
                for target_ds in target_ds_list:
                    if target_ds.get("name") == exclude_ds:
                        assert target_ds.get("name") not in result.get("targets")
                        assert target_ds.get("name") not in c_result.get("stdout")
                    else:
                        assert target_ds.get("name") in result.get("targets")
                        assert target_ds.get("name") in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="SEQ"),
        dict(name=TEST_PDS, dstype="PDS"),
        dict(name=TEST_PDS, dstype="PDSE"),
        ]
)
def test_mvs_unarchive_multiple_dataset_list(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=data_set.get("name"),
                                    n=2,
                                    type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["PDS", "PDSE"]:
            target_member_list = []
            for ds in target_ds_list:
                target_member_list.extend(
                    create_multiple_members(ansible_zos_module=hosts,
                                        pds_name=ds.get("name"),
                                        member_base_name="MEM",
                                        n=3
                    )
                )
            ds_to_write = target_member_list
        # Write some content into src
        test_line = "this is a test line"
        for ds in ds_to_write:
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds.get("name")))
        
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="SPACK")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            path="{0}*".format(data_set.get("name")),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote datasets from host
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            path=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            list=True
        )
        
        # assert response is positive 
        for result in unarchive_result.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("failed", False) is False
            assert result.get("path") == MVS_DEST_ARCHIVE
            
            cmd_result = hosts.all.shell(cmd="dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                print("dls result : {0}".format(c_result))
                for target_ds in target_ds_list:
                    assert target_ds.get("name") in result.get("targets")
                    assert target_ds.get("name") not in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(data_set.get("name")))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

