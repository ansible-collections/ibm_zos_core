#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023, 2024
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
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
import time

import pytest
__metaclass__ = type

SHELL_EXECUTABLE = "/bin/sh"
USS_TEMP_DIR = "/tmp/archive"
USS_TEST_FILES = {  f"{USS_TEMP_DIR}/foo.txt" : "foo sample content",
                    f"{USS_TEMP_DIR}/bar.txt": "bar sample content",
                    f"{USS_TEMP_DIR}/empty.txt":""}
USS_EXCLUSION_FILE = f"{USS_TEMP_DIR}/foo.txt"

USS_DEST_ARCHIVE = "testarchive.dzp"

STATE_ARCHIVED = 'archive'
STATE_INCOMPLETE = 'incomplete'

USS_FORMATS = ['tar', 'zip', 'gz', 'bz2', 'pax']

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
SH /tmp/disp_shr/pdse-lock '{0}'
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""

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
- test_uss_single_archive
- test_uss_single_archive_with_mode
- test_uss_single_archive_with_force_option
- test_uss_archive_multiple_files
- test_uss_archive_multiple_files_with_exclude
- test_uss_archive_remove_targets
"""


# Core functionality tests
# Test archive with no options
@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_single_archive(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))

        for result in archive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                assert "archive.{0}".format(format) in c_result.get("stdout")

    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_single_archive_with_mode(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        dest_mode = "0755"
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ),
                                        mode=dest_mode)
        stat_dest_res = hosts.all.stat(path=dest)
        for result in archive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED
            for stat_result in stat_dest_res.contacted.values():
                assert stat_result.get("stat").get("exists") is True
                assert stat_result.get("stat").get("mode") == dest_mode
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_single_archive_with_force_option(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))

        for result in archive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True

        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))

        for result in archive_result.contacted.values():
            assert result.get("failed", False) is True
            assert result.get("changed") is False

        set_uss_test_env(hosts, USS_TEST_FILES)
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ),
                                        force=True,)

        for result in archive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED

    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
@pytest.mark.parametrize("path", [
    dict(files= f"{USS_TEMP_DIR}/*.txt", size=len(USS_TEST_FILES)),
    dict(files=list(USS_TEST_FILES.keys()),  size=len(USS_TEST_FILES)),
    dict(files= f"{USS_TEMP_DIR}/" , size=len(USS_TEST_FILES) + 1),
    ])
def test_uss_archive_multiple_files(ansible_zos_module, format, path):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=USS_TEMP_DIR, state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive(src=path.get("files"),
                                        dest=dest,
                                        format=dict(name=format),)

        # resulting archived tag varies in size when a folder is archived using zip.
        size = path.get("size")

        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED
            assert len(result.get("archived")) == size
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                assert f"archive.{format}" in c_result.get("stdout")

    finally:
        hosts.all.file(path=USS_TEMP_DIR, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
@pytest.mark.parametrize("path", [
    dict(files=list(USS_TEST_FILES.keys()),  size=len(USS_TEST_FILES) - 1, exclude=[f'{USS_TEMP_DIR}/foo.txt']),
    dict(files= f"{USS_TEMP_DIR}/" , size=len(USS_TEST_FILES) + 1, exclude=[]),
    ])
def test_uss_archive_multiple_files_with_exclude(ansible_zos_module, format, path):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=USS_TEMP_DIR, state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        archive_result = hosts.all.zos_archive(src=path.get("files"),
                                        dest=dest,
                                        format=dict(name=format),
                                        exclude=path.get("exclude"))

        # resulting archived tag varies in size when a folder is archived using zip.
        size = path.get("size")

        for result in archive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED
            assert len(result.get("archived")) == size
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                assert f"archive.{format}" in c_result.get("stdout")
    finally:
        hosts.all.file(path=USS_TEMP_DIR, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_archive_remove_targets(ansible_zos_module, format):
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=USS_TEMP_DIR, state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        dest = f"{USS_TEMP_DIR}/archive.{format}"
        paths = list(USS_TEST_FILES.keys())
        archive_result = hosts.all.zos_archive(src=paths,
                                        dest=dest,
                                        format=dict(name=format),
                                        remove=True)

        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest_state") == STATE_ARCHIVED
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
                assert f"archive.{format}" in c_result.get("stdout")
                for path in paths:
                    assert path not in c_result.get("stdout")
    finally:
        hosts.all.file(path=USS_TEMP_DIR, state="absent")


######################################################################
#
#   MVS data sets tests
#
######################################################################

"""
List of tests:
- test_mvs_archive_single_dataset
- test_mvs_archive_single_dataset_use_adrdssu
- test_mvs_archive_single_data_set_remove_target
- test_mvs_archive_multiple_data_sets
- test_mvs_archive_multiple_data_sets_use_adrdssu
- test_mvs_archive_multiple_data_sets_remove_target
- test_mvs_archive_multiple_data_sets_with_exclusion
- test_mvs_archive_multiple_data_sets_with_missing

"""
@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq", members=[""]),
        dict(dstype="pds", members=["MEM1", "MEM2", "MEM3"]),
        dict(dstype="pdse", members=["MEM1", "MEM2", "MEM3"]),
        ]
)
@pytest.mark.parametrize(
    "record_length", [80, 120]
)
@pytest.mark.parametrize(
    "record_format", ["fb", "vb"],
)
def test_mvs_archive_single_dataset(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        src_data_set = get_tmp_ds_name()
        archive_data_set = get_tmp_ds_name()
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=src_data_set,
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
            replace=True,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{src_data_set}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src the same size of the record,
        # need to reduce 4 from V and VB due to RDW
        if record_format in ["v", "vb"]:
            test_line = "a" * (record_length - 4)
        else:
            test_line = "a" * record_length
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{src_data_set}"
            else:
                ds_to_write = f"{src_data_set}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=src_data_set,
            dest=archive_data_set,
            format=format_dict,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert src_data_set in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq", members=[""]),
        dict(dstype="pds", members=["MEM1", "MEM2", "MEM3"]),
        dict(dstype="pdse", members=["MEM1", "MEM2", "MEM3"]),
        ]
)
@pytest.mark.parametrize(
    "record_length", [80, 120]
)
@pytest.mark.parametrize(
    "record_format", ["fb", "vb"],
)
def test_mvs_archive_single_dataset_use_adrdssu(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name()
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=src_data_set,
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
            replace=True,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{src_data_set}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src the same size of the record,
        # need to reduce 4 from V and VB due to RDW
        if record_format in ["v", "vb"]:
            test_line = "a" * (record_length - 4)
        else:
            test_line = "a" * record_length
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{src_data_set}"
            else:
                ds_to_write = f"{src_data_set}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        format_dict["format_options"] = dict(use_adrdssu=True)
        if format == "terse":
            format_dict["format_options"].update(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=src_data_set,
            dest=archive_data_set,
            format=format_dict,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert src_data_set in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq", members=[""]),
        dict(dstype="pds", members=["MEM1", "MEM2", "MEM3"]),
        dict(dstype="pdse", members=["MEM1", "MEM2", "MEM3"]),
        ]
)
def test_mvs_archive_single_data_set_remove_target(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name()
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=src_data_set,
            type=data_set.get("dstype"),
            state="present",
            record_format="fb",
            replace=True,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{src_data_set}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src
        test_line = "this is a test line"
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{src_data_set}"
            else:
                ds_to_write = f"{src_data_set}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=src_data_set,
            dest=archive_data_set,
            format=format_dict,
            remove=True,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            print(result)
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert src_data_set in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
                assert src_data_set != c_result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq"),
        dict(dstype="pds"),
        dict(dstype="pdse"),
        ]
)
def test_mvs_archive_multiple_data_sets(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name(5, 4)
        HLQ = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                  base_name=src_data_set,
                                  n=3,
                                  type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["pds", "pdse"]:
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
            format_dict["format_options"].update(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src="{0}*".format(src_data_set),
            dest=archive_data_set,
            format=format_dict,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            for ds in target_ds_list:
                assert ds.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(src_data_set))
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq"),
        dict(dstype="pds"),
        dict(dstype="pdse"),
        ]
)
def test_mvs_archive_multiple_data_sets_with_exclusion(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name(5, 4)
        HLQ = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                  base_name=src_data_set,
                                  n=3,
                                  type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["pds", "pdse"]:
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
            format_dict["format_options"].update(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        exclude = "{0}1".format(src_data_set)
        archive_result = hosts.all.zos_archive(
            src="{0}*".format(src_data_set),
            dest=archive_data_set,
            format=format_dict,
            exclude=exclude,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            for ds in target_ds_list:
                if ds.get("name") == exclude:
                    assert exclude not in result.get("archived")
                else:
                    assert ds.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}*".format(src_data_set))
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq"),
        dict(dstype="pds"),
        dict(dstype="pdse"),
        ]
)
def test_mvs_archive_multiple_data_sets_and_remove(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name(symbols=True)
        src_data_set = get_tmp_ds_name(5, 4, symbols=True)
        HLQ = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                  base_name=src_data_set,
                                  n=3,
                                  type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["pds", "pdse"]:
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
            format_dict["format_options"].update(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src="{0}*".format(src_data_set),
            dest=archive_data_set,
            format=format_dict,
            remove=True,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
                for ds in target_ds_list:
                    assert ds.get("name") in result.get("archived")
                    assert ds.get("name") not in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="drm {0}.*".format(HLQ))


@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq"),
        dict(dstype="pds"),
        dict(dstype="pdse"),
        ]
)
def test_mvs_archive_multiple_data_sets_with_missing(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name(5, 4)
        HLQ = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                  base_name=src_data_set,
                                  n=3,
                                  type=data_set.get("dstype"))
        ds_to_write = target_ds_list
        if data_set.get("dstype") in ["pds", "pdse"]:
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

        # Remove ds to make sure is missing
        missing_ds = src_data_set+"1"
        hosts.all.zos_data_set(name=missing_ds, state="absent")
        path_list = [ds.get("name") for ds in target_ds_list]

        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src=path_list,
            dest=archive_data_set,
            format=format_dict,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert result.get("dest_state") == STATE_INCOMPLETE
            assert missing_ds in result.get("missing")
            for ds in target_ds_list:
                if ds.get("name") == missing_ds:
                    assert ds.get("name") not in result.get("archived")
                else:
                    assert ds.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")

    finally:
        hosts.all.shell(cmd="drm {0}*".format(src_data_set))
        hosts.all.zos_data_set(name=archive_data_set, state="absent")

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize(
    "data_set", [
        dict(dstype="seq", members=[""]),
        dict(dstype="pds", members=["MEM1", "MEM2"]),
        dict(dstype="pdse", members=["MEM1", "MEM2"]),
        ]
)
def test_mvs_archive_single_dataset_force_lock(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        archive_data_set = get_tmp_ds_name()
        src_data_set = get_tmp_ds_name(5, 4)
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=src_data_set,
            type=data_set.get("dstype"),
            state="present",
            replace=True,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{src_data_set}({member})",
                    type="member",
                    state="present"
                )
        # Write some content into src
        test_line = "this is a test line"
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{src_data_set}"
            else:
                ds_to_write = f"{src_data_set}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")

        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.shell(cmd="echo \"{0}\"  > {1}".format(c_pgm, '/tmp/disp_shr/pdse-lock.c'))
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(
            call_c_jcl.format(ds_to_write),
            '/tmp/disp_shr/call_c_pgm.jcl'))
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")

        # submit jcl
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")

        # pause to ensure c code acquires lock
        time.sleep(5)

        archive_result = hosts.all.zos_archive(
            src=src_data_set,
            dest=archive_data_set,
            format=format_dict,
        )

        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert src_data_set in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")

    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")

        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=archive_data_set, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_gdg_archive(ansible_zos_module, dstype, format):
    try:
        HLQ = "ANSIBLE"
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(symbols=True)
        archive_data_set = get_tmp_ds_name(symbols=True)
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
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src=[f"{data_set_name}(0)",f"{data_set_name}(-1)" ],
            dest=archive_data_set,
            format=format_dict,
        )
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == archive_data_set
            assert f"{data_set_name}.G0001V00" in result.get("archived")
            assert f"{data_set_name}.G0002V00" in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd=f"drm {HLQ}.*")


@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_archive_into_gds(ansible_zos_module, dstype, format):
    try:
        HLQ = "ANSIBLE"
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(symbols=True)
        archive_data_set = get_tmp_ds_name(symbols=True)
        results = hosts.all.zos_data_set(
            batch = [
                {"name":archive_data_set, "state":"present", "type":"gdg", "limit":3},
                {"name":data_set_name, "state":"present", "type":dstype}
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src=data_set_name,
            dest=f"{archive_data_set}(+1)",
            format=format_dict,
        )
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert data_set_name in result.get("archived")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert archive_data_set in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd=f"drm {HLQ}.*")

