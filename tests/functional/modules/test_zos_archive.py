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

USS_FORMATS = ['tar', 'zip', 'gz']

def set_uss_test_env(ansible_zos_module, test_files):
    for key, value in test_files.items():
        ansible_zos_module.all.shell(
            cmd=f"echo \"{value}\" > \"{key}\"",
            executable=SHELL_EXECUTABLE,
        )

# Core functionality tests
# Test archive with no options
# @pytest.mark.uss
# @pytest.mark.parametrize("format", USS_FORMATS)
# @pytest.mark.parametrize("path", [
#     dict(files= f"{USS_TEMP_DIR}/*.txt" , size=len(USS_TEST_FILES)),
#     dict(files=list(USS_TEST_FILES.keys()),  size=len(USS_TEST_FILES)), 
#     dict(files=list(USS_TEST_FILES.keys())[0],  size=1),
#     dict(files= f"{USS_TEMP_DIR}/" , size=len(USS_TEST_FILES)),  ])
# def test_uss_archive(ansible_zos_module, format, path):
#     try:
#         hosts = ansible_zos_module
#         expected_state = STATE_ARCHIVED
#         hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
#         hosts.all.file(path=USS_TEMP_DIR, state="directory")
#         set_uss_test_env(hosts, USS_TEST_FILES)
#         dest = f"{USS_TEMP_DIR}/archive.{format}"
#         archive_result = hosts.all.zos_archive( path=path.get("files"),
#                                         dest=dest,
#                                         format=format)

#         # resulting archived tag varies in size when a folder is archived using zip.
#         size = path.get("size")
#         if format in ['zip', 'gz'] and path.get("files") == f"{USS_TEMP_DIR}/":
#             size += 1
        
#         for result in archive_result.contacted.values():
#             assert result.get("changed") is True
#             assert result.get("dest_state") == expected_state
#             assert len(result.get("archived")) == size
#             # Command to assert the file is in place
#             cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
#             for c_result in cmd_result.contacted.values():
#                 assert f"archive.{format}" in c_result.get("stdout")
                
#     finally:
#         hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


# @pytest.mark.uss
# @pytest.mark.parametrize("format", USS_FORMATS)
# @pytest.mark.parametrize("path", [
#     dict(files= f"{USS_TEMP_DIR}/*.txt", size=len(USS_TEST_FILES) - 1, exclude_path=USS_EXCLUSION_FILE),
#     dict(files=list(USS_TEST_FILES.keys()),  size=len(USS_TEST_FILES) - 1, exclude_path=USS_EXCLUSION_FILE), 
#     #dict(files= f"{USS_TEMP_DIR}/" , size=len(USS_TEST_FILES) - 1, exclude_path=USS_EXCLUSION_FILE), 
#     ])
# def test_uss_archive_with_exclusion_list(ansible_zos_module, format, path):
#     try:
#         hosts = ansible_zos_module
#         expected_state = STATE_ARCHIVED if format in ['tar', 'zip'] else STATE_COMPRESSED
#         hosts.all.file(path=USS_TEMP_DIR, state="absent")
#         hosts.all.file(path=USS_TEMP_DIR, state="directory")
#         set_uss_test_env(hosts, USS_TEST_FILES)
#         dest = f"{USS_TEMP_DIR}/archive.{format}"
#         archive_result = hosts.all.zos_archive( path=path.get("files"),
#                                         dest=dest,
#                                         format=format,
#                                         exclude_path=path.get("exclude_path"))

#         # resulting archived tag varies in size when a folder is archived using zip.
#         size = path.get("size")
#         if format == "zip" and path.get("files") == f"{USS_TEMP_DIR}/":
#             size += 1
        
#         for result in archive_result.contacted.values():
#             assert result.get("changed") is True
#             assert result.get("dest_state") == expected_state
#             assert len(result.get("archived")) == size
#             # Command to assert the file is in place
#             cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
#             for c_result in cmd_result.contacted.values():
#                 assert f"archive.{format}" in c_result.get("stdout")
                
#     finally:
#         hosts.all.file(path=USS_TEMP_DIR, state="absent")


@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(name=TEST_PS, dstype="seq", members=[""]),
        dict(name=TEST_PDS, dstype="pds", members=["MEM1", "MEM2", "MEM3"]),
        dict(name=TEST_PDS, dstype="pdse", members=["MEM1", "MEM2", "MEM3"]),
        ]
)
@pytest.mark.parametrize(
    "record_length", [80, 120, 1024]
)
@pytest.mark.parametrize(
    "record_format", ["FB", "VB", "FBA", "VBA", "U"]
)
def test_mvs_archive_single_dataset(ansible_zos_module, format, data_set, record_length, record_format):
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
        # archive it
        format_dict = dict(name=format)
        if format == "terse":
            format_dict["suboptions"] = dict(terse_pack="SPACK")
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
        
    finally:
        hosts.all.zos_data_set(name=data_set.get("name"), state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")