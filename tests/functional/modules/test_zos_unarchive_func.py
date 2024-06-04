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

import pytest
import tempfile
from tempfile import mkstemp
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

__metaclass__ = type

SHELL_EXECUTABLE = "/bin/sh"
USS_TEMP_DIR = "/tmp/archive"
USS_TEST_FILES = {  f"{USS_TEMP_DIR}/foo.txt" : "foo sample content",
                    f"{USS_TEMP_DIR}/bar.txt": "bar sample content",
                    f"{USS_TEMP_DIR}/empty.txt":""}
USS_EXCLUSION_FILE = f"{USS_TEMP_DIR}/foo.txt"

USS_DEST_ARCHIVE = "testarchive.dzp"

USS_FORMATS = ['tar', 'gz', 'bz2', 'zip', 'pax']

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
- test_uss_unarchive_copy_to_remote
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
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=dest,
            format=dict(
                name=format
            ),
            remote_src=True,
        )
        hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")

        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
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
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        uss_files = [file[len(USS_TEMP_DIR)+1:] for file in USS_TEST_FILES]
        include_list = uss_files[:2]
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=dest,
            format=dict(
                name=format
            ),
            include=include_list,
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
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
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        # remove files
        uss_files = [file[len(USS_TEMP_DIR)+1:] for file in USS_TEST_FILES]
        exclude_list = uss_files[:2]
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=dest,
            format=dict(
                name=format
            ),
            exclude=exclude_list,
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd=f"ls {USS_TEMP_DIR}")
            for c_result in cmd_result.contacted.values():
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
        archive_result = hosts.all.zos_archive(src=list(USS_TEST_FILES.keys()),
                                        dest=dest,
                                        format=dict(
                                            name=format
                                        ))
        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=dest,
            format=dict(
                name=format
            ),
            remote_src=True,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            for file in USS_TEST_FILES.keys():
                    assert file[len(USS_TEMP_DIR)+1:] in result.get("targets")
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("format", USS_FORMATS)
def test_uss_single_unarchive_with_mode(ansible_zos_module, format):
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
                                        ))
        for file in list(USS_TEST_FILES.keys()):
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=dest,
            format=dict(
                name=format
            ),
            remote_src=True,
            mode=dest_mode,
        )
        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            dest_files = list(USS_TEST_FILES.keys())
            for file in dest_files:
                stat_dest_res = hosts.all.stat(path=file)
                for stat_result in stat_dest_res.contacted.values():
                    assert stat_result.get("stat").get("exists") is True
                    assert stat_result.get("stat").get("mode") == dest_mode
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")

@pytest.mark.uss
def test_uss_unarchive_copy_to_remote(ansible_zos_module):
    try:
        import os
        import tarfile
        hosts = ansible_zos_module
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        hosts.all.file(path=USS_TEMP_DIR, state="directory")
        set_uss_test_env(hosts, USS_TEST_FILES)
        # create local tmp dir
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tar_file = tmp_dir.name + "/tmpfile.tar"
        # create local file
        with open(tmp_file.name, 'w') as f:
            f.write("This is a sample text for the file")
        # archive using different formats
        with tarfile.open(tar_file, 'w') as tar:
            tar.add(tmp_file.name)

        # remove files
        for file in USS_TEST_FILES.keys():
            hosts.all.file(path=file, state="absent")
        unarchive_result = hosts.all.zos_unarchive(
            src=tar_file,
            dest=USS_TEMP_DIR,
            format=dict(
                name="tar"
            ),
            force=True,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("failed", False) is False
            assert result.get("changed") is True
            # Command to assert the file is in place
            cmd_result = hosts.all.shell(cmd="ls {0}/{1}".format(USS_TEMP_DIR, tmp_file.name))
            for c_result in cmd_result.contacted.values():
                for file in USS_TEST_FILES.keys():
                    assert tmp_file.name in c_result.get("stdout")
    finally:
        hosts.all.file(path=f"{USS_TEMP_DIR}", state="absent")
        os.remove(tmp_file.name)

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
@pytest.mark.parametrize(
    "record_length", [80, 120]
)
@pytest.mark.parametrize(
    "record_format", ["fb", "vb",],
)
def test_mvs_unarchive_single_data_set(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3)
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=DATASET,
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
            replace=True
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{DATASET}({member})",
                    type="member",
                    state="present",
                    replace=True
                )
        # Write some content into src the same size of the record,
        # need to reduce 4 from V and VB due to RDW
        if record_format in ["v", "vb"]:
            test_line = "a" * (record_length - 4)
        else:
            test_line = "a" * record_length
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{DATASET}"
            else:
                ds_to_write = f"{DATASET}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=DATASET,
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
            dest_data_set=dict(name=DATASET,
                               type="seq",
                               record_format=record_format,
                               record_length=record_length),
        )
        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == MVS_DEST_ARCHIVE
            assert DATASET in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert MVS_DEST_ARCHIVE in c_result.get("stdout")

        hosts.all.zos_data_set(name=DATASET, state="absent")

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            dest_data_set=dict(name=DATASET,
                               type=data_set.get("dstype"),
                               record_format=record_format,
                               record_length=record_length),
        )
        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            # assert result.get("dest") == MVS_DEST_ARCHIVE
            # assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert DATASET in c_result.get("stdout")

        # Check data integrity after unarchive
        cat_result = hosts.all.shell(cmd=f"dcat \"{ds_to_write}\"")
        for result in cat_result.contacted.values():
            assert result.get("stdout") == test_line
    finally:
        hosts.all.zos_data_set(name=DATASET, state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
@pytest.mark.parametrize(
    "record_length", [80, 120]
)
@pytest.mark.parametrize(
    "record_format", ["fb", "vb",],
)
def test_mvs_unarchive_single_data_set_use_adrdssu(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3)
        HLQ = "ANSIBLE"
        # Clean env
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=DATASET,
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
            replace=True
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{DATASET}({member})",
                    type="member",
                    state="present",
                    replace=True
                )
        # Write some content into src the same size of the record,
        # need to reduce 4 from V and VB due to RDW
        if record_format in ["v", "vb"]:
            test_line = "a" * (record_length - 4)
        else:
            test_line = "a" * record_length
        for member in data_set.get("members"):
            if member == "":
                ds_to_write = f"{DATASET}"
            else:
                ds_to_write = f"{DATASET}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        format_dict["format_options"] = dict(use_adrdssu=True)
        if format == "terse":
            format_dict["format_options"].update(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=DATASET,
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        # assert response is positive
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == MVS_DEST_ARCHIVE
            assert DATASET in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert MVS_DEST_ARCHIVE in c_result.get("stdout")

        hosts.all.zos_data_set(name=DATASET, state="absent")

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True
        )

        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            # assert result.get("dest") == MVS_DEST_ARCHIVE
            # assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert DATASET in c_result.get("stdout")
    finally:
        hosts.all.zos_data_set(name=DATASET, state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
def test_mvs_unarchive_multiple_data_set_use_adrdssu(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name(symbols=True)
        DATASET = get_tmp_ds_name(3,3,symbols=True)
        HLQ ="ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=DATASET,
                                    n=1,
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
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds.get("name").replace('$', '\\$')))

        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"].update(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        archive_result = hosts.all.zos_archive(
            src="{0}*".format(DATASET),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        # remote data_sets from host
        hosts.all.shell(cmd="drm {0}*".format(DATASET.replace("$", "/$")))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            force=True
        )
        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("src") == MVS_DEST_ARCHIVE

            cmd_result = hosts.all.shell(cmd="""dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                for target_ds in target_ds_list:
                    assert target_ds.get("name") in result.get("targets")
                    assert target_ds.get("name") in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd=""" drm "{0}*" """.format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
def test_mvs_unarchive_multiple_data_set_use_adrdssu_include(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3,3)
        HLQUA = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=DATASET,
                                    n=2,
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
            src="{0}*".format(DATASET),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # remote data_sets from host
        hosts.all.shell(cmd="drm {0}*".format(DATASET))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        include_ds = "{0}0".format(DATASET)
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            include=[include_ds],
        )

        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("src") == MVS_DEST_ARCHIVE

            cmd_result = hosts.all.shell(cmd="""dls "{0}.*" """.format(HLQUA))
            for c_result in cmd_result.contacted.values():
                for target_ds in target_ds_list:
                    if target_ds.get("name") == include_ds:
                        assert target_ds.get("name") in result.get("targets")
                        assert target_ds.get("name") in c_result.get("stdout")
                    else:
                        assert target_ds.get("name") not in result.get("targets")
                        assert target_ds.get("name") not in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd=""" drm "{0}*" """.format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
def test_mvs_unarchive_multiple_data_set_use_adrdssu_exclude(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3,3)
        HLQUA = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=DATASET,
                                    n=2,
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
            src="{0}*".format(DATASET),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote data_sets from host
        hosts.all.shell(cmd=""" drm "{0}*" """.format(DATASET))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        exclude_ds = "{0}0".format(DATASET)
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            exclude=[exclude_ds],
        )
        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("src") == MVS_DEST_ARCHIVE

            cmd_result = hosts.all.shell(cmd=""" dls "{0}.*" """.format(HLQUA))
            for c_result in cmd_result.contacted.values():
                for target_ds in target_ds_list:
                    if target_ds.get("name") == exclude_ds:
                        assert target_ds.get("name") not in result.get("targets")
                        assert target_ds.get("name") not in c_result.get("stdout")
                    else:
                        assert target_ds.get("name") in result.get("targets")
                        assert target_ds.get("name") in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd=""" drm "{0}*" """.format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
def test_mvs_unarchive_multiple_data_set_list(ansible_zos_module, format, data_set):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3,3)
        HLQ = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=DATASET,
                                    n=2,
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
            src="{0}*".format(DATASET),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        # remote data_sets from host
        hosts.all.shell(cmd="drm {0}*".format(DATASET))

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            list=True
        )
        # assert response is positive
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed", False) is False
            assert result.get("src") == MVS_DEST_ARCHIVE

            cmd_result = hosts.all.shell(cmd="""dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                for target_ds in target_ds_list:
                    assert target_ds.get("name") in result.get("targets")
                    assert target_ds.get("name") not in c_result.get("stdout")
    finally:
        hosts.all.shell(cmd="""drm "{0}*" """.format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
@pytest.mark.parametrize(
    "force", [
        True,
        False,
        ])
def test_mvs_unarchive_multiple_data_set_use_adrdssu_force(ansible_zos_module, format, data_set, force):
    """
    This force test creates some data sets and attempt to extract using force flag as
    True and False, when True no issues are expected, as False proper error message should
    be displayed.
    """
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3,3)
        HLQUA = "ANSIBLE"
        target_ds_list = create_multiple_data_sets(ansible_zos_module=hosts,
                                    base_name=DATASET,
                                    n=1,
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
        hosts.all.zos_archive(
            src="{0}*".format(DATASET),
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=MVS_DEST_ARCHIVE,
            format=format_dict,
            remote_src=True,
            force=force
        )
        # assert response is positive
        for result in unarchive_result.contacted.values():
            if force:
                assert result.get("changed") is True
                assert result.get("failed", False) is False
                assert result.get("src") == MVS_DEST_ARCHIVE

                cmd_result = hosts.all.shell(cmd="""dls "{0}.*" """.format(HLQUA))
                for c_result in cmd_result.contacted.values():
                    for target_ds in target_ds_list:
                        assert target_ds.get("name") in result.get("targets")
                        assert target_ds.get("name") in c_result.get("stdout")
            else:
                assert result.get("changed") is False
                assert result.get("failed", False) is True
    finally:
        hosts.all.shell(cmd=""" drm "{0}*" """.format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")

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
@pytest.mark.parametrize(
    "record_length", [80, 120]
)
@pytest.mark.parametrize(
    "record_format", ["fb", "vb",],
)
def test_mvs_unarchive_single_data_set_remote_src(ansible_zos_module, format, data_set, record_length, record_format):
    try:
        hosts = ansible_zos_module
        MVS_DEST_ARCHIVE = get_tmp_ds_name()
        DATASET = get_tmp_ds_name(3)
        HLQ = "ANSIBLE"
        tmp_folder = tempfile.TemporaryDirectory(prefix="tmpfetch")
        # Clean env
        hosts.all.zos_data_set(name=DATASET, state="absent")
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        # Create source data set
        hosts.all.zos_data_set(
            name=DATASET,
            type=data_set.get("dstype"),
            state="present",
            record_length=record_length,
            record_format=record_format,
        )
        # Create members if needed
        if data_set.get("dstype") in ["pds", "pdse"]:
            for member in data_set.get("members"):
                hosts.all.zos_data_set(
                    name=f"{DATASET}({member})",
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
                ds_to_write = f"{DATASET}"
            else:
                ds_to_write = f"{DATASET}({member})"
            hosts.all.shell(cmd=f"decho '{test_line}' \"{ds_to_write}\"")

        format_dict = dict(name=format)
        format_dict["format_options"] = dict(use_adrdssu=True)
        if format == "terse":
            format_dict["format_options"].update(terse_pack="spack")
        archive_result = hosts.all.zos_archive(
            src=DATASET,
            dest=MVS_DEST_ARCHIVE,
            format=format_dict,
        )
        for result in archive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("dest") == MVS_DEST_ARCHIVE
            assert DATASET in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert MVS_DEST_ARCHIVE in c_result.get("stdout")

        hosts.all.zos_data_set(name=DATASET, state="absent")

        # fetch archive data set into tmp folder
        fetch_result = hosts.all.zos_fetch(src=MVS_DEST_ARCHIVE, dest=tmp_folder.name, is_binary=True)

        for res in fetch_result.contacted.values():
            source_path = res.get("dest")

        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=source_path,
            format=format_dict,
            remote_src=False,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            # assert result.get("dest") == MVS_DEST_ARCHIVE
            # assert data_set.get("name") in result.get("archived")
            cmd_result = hosts.all.shell(cmd = """dls "{0}.*" """.format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert DATASET in c_result.get("stdout")

        # Check data integrity after unarchive
        cat_result = hosts.all.shell(cmd=f"dcat \"{ds_to_write}\"")
        for result in cat_result.contacted.values():
            assert result.get("stdout") == test_line


    finally:
        hosts.all.shell(cmd="drm {0}*".format(DATASET))
        hosts.all.zos_data_set(name=MVS_DEST_ARCHIVE, state="absent")
        tmp_folder.cleanup()


def test_mvs_unarchive_fail_copy_remote_src(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        tmp_folder = tempfile.TemporaryDirectory(prefix="tmpfetch")
        # False path
        source_path = "/tmp/OMVSADM.NULL"

        format_dict = dict(name='terse')
        format_dict["format_options"] = dict(use_adrdssu=True)

        # Unarchive action
        unarchive_result = hosts.all.zos_unarchive(
            src=source_path,
            format=format_dict,
            remote_src=False,
        )

        for result in unarchive_result.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed", False) is True
    finally:
        tmp_folder.cleanup()

@pytest.mark.ds
@pytest.mark.parametrize(
    "format", [
        "terse",
        "xmit",
        ])
@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_gdg_unarchive(ansible_zos_module, dstype, format):
    try:
        HLQ = "ANSIBLE"
        hosts = ansible_zos_module
        data_set_name = get_tmp_ds_name(symbols=True)
        archive_data_set = get_tmp_ds_name(symbols=True)
        results = hosts.all.zos_data_set(
            batch = [
                { "name":data_set_name, "state":"present", "type":"gdg", "limit":3},
                { "name":f"{data_set_name}(+1)", "state":"present", "type":dstype},
                { "name":f"{data_set_name}(+1)", "state":"present", "type":dstype},
            ]
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None

        target_ds_list = [f"{data_set_name}.G0001V00", f"{data_set_name}.G0002V00"]
        if dstype in ["pds", "pdse"]:
            target_member_list = []
            for ds in target_ds_list:
                target_member_list.extend(
                    create_multiple_members(ansible_zos_module=hosts,
                                        pds_name=ds,
                                        member_base_name="MEM",
                                        n=2
                    )
                )
            ds_to_write = target_member_list
        # Write some content into src
        test_line = "this is a test line"
        for ds in ds_to_write:
            hosts.all.shell(cmd="decho '{0}' \"{1}\"".format(test_line, ds))

        format_dict = dict(name=format, format_options=dict())
        if format == "terse":
            format_dict["format_options"] = dict(terse_pack="spack")
        format_dict["format_options"].update(use_adrdssu=True)
        if format == "terse":
            del format_dict["format_options"]["terse_pack"]
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

        hosts.all.zos_data_set(
            batch=[
                {"name": f"{data_set_name}(-1)", "state": "absent", "type": "gdg"},
                {"name": f"{data_set_name}(0)", "state": "absent", "type": "gdg"},
            ]
        )
        unarchive_result = hosts.all.zos_unarchive(
            src=archive_data_set,
            format=format_dict,
            remote_src=True
        )
        for result in unarchive_result.contacted.values():
            assert result.get("changed") is True
            assert len(result.get("missing")) == 0
            assert f"{data_set_name}.G0001V00" in result.get("targets")
            assert f"{data_set_name}.G0002V00" in result.get("targets")
            cmd_result = hosts.all.shell(cmd = "dls {0}.*".format(HLQ))
            for c_result in cmd_result.contacted.values():
                assert f"{data_set_name}.G0001V00" in c_result.get("stdout")
                assert f"{data_set_name}.G0002V00" in c_result.get("stdout")
    finally:
        None
        # hosts.all.shell(cmd=f"drm {HLQ}.*")

