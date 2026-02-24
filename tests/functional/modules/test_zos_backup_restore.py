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

__metaclass__ = type

from ibm_zos_core.tests.helpers.users import ManagedUserType, ManagedUser
from ibm_zos_core.tests.helpers.dataset import (
    get_tmp_ds_name,
    get_random_q,
)
import pytest
from re import search, IGNORECASE, MULTILINE
import string
import random
import time
import json
from ibm_zos_core.tests.helpers.utils import get_random_file_name
from ibm_zos_core.tests.helpers.volumes import Volume_Handler

DATA_SET_CONTENTS = "HELLO WORLD"
TMP_DIRECTORY = "/tmp/"

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
SH {1}/pdse-lock '{0}'
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""


# ---------------------------------------------------------------------------- #
#                               Helper functions                               #
# ---------------------------------------------------------------------------- #


def create_data_set_or_file_with_contents(hosts, name, contents):
    if name.startswith("/"):
        create_file_with_contents(hosts, name, contents)
    else:
        create_sequential_data_set_with_contents(hosts, name, contents)


def create_sequential_data_set_with_contents(
    hosts, data_set_name, contents, volume=None
):
    if volume is not None:
        results = hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{data_set_name}'")
    else:
        results = hosts.all.shell(cmd=f"dtouch -tseq '{data_set_name}'")
    assert_module_did_not_fail(results)
    results = hosts.all.shell("decho '{0}' {1}".format(contents, data_set_name))
    assert_module_did_not_fail(results)


def create_file_with_contents(hosts, path, contents):
    results = hosts.all.shell("echo '{0}' > {1}".format(contents, path))
    assert_module_did_not_fail(results)


def create_vsam(hosts, data_set_name):
    results = hosts.all.shell(cmd=f"dtouch -tksds -k4:0 {data_set_name}")
    assert_module_did_not_fail(results)


def delete_data_set_or_file(hosts, name):
    if name.startswith("/"):
        delete_file(hosts, name)
    else:
        delete_data_set(hosts, name)


def delete_data_set(hosts, data_set_name):
    hosts.all.shell(cmd=f"drm -F '{data_set_name}'")


def delete_file(hosts, path):
    hosts.all.file(path=path, state="absent")

def delete_remnants(hosts, list=None):
    hosts.all.shell(cmd="drm 'ANSIBLE.*'")
    hosts.all.shell(cmd="drm 'TEST.*'")
    hosts.all.shell(cmd="drm 'TMPHLQ.*'")
    if list:
        for object in list:
            hosts.all.shell(cmd="drm '{0}.*'".format(object))

def get_unused_volume_serial(hosts):
    found = False
    volume = ""
    while not found:
        volume = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not is_volume(hosts, volume):
            found = True


def is_volume(hosts, volume):
    results = hosts.all.shell(cmd="vtocls ${volume}")
    failed = False
    for result in results.contacted.values():
        if result.get("failed", False) is True:
            failed = True
        if result.get("rc", 0) > 0:
            failed = True
    return not failed


def assert_module_did_not_fail(results):
    for result in results.contacted.values():
        assert (
            result.get("failed", False) is not True
            and not result.get("exception", "")
            and "error" not in result.get("msg", "").lower()
        )


def assert_module_failed(results):
    for result in results.contacted.values():
        assert (
            result.get("failed", False) is True
            or result.get("exception", "")
            or "error" in result.get("msg", "").lower()
        )


def assert_data_set_or_file_exists(hosts, name):
    if name.startswith("/"):
        assert_file_exists(hosts, name)
    else:
        assert_data_set_exists(hosts, name)


def assert_data_set_or_file_does_not_exist(hosts, name):
    if name.startswith("/"):
        assert_file_does_not_exist(hosts, name)
    else:
        assert_data_set_does_not_exist(hosts, name)


def assert_data_set_exists(hosts, data_set_name):
    results = hosts.all.shell("dls '{0}'".format(data_set_name.upper()))
    for result in results.contacted.values():
        found = search(
            "^{0}$".format(data_set_name), result.get("stdout"), IGNORECASE | MULTILINE
        )
        assert found


def assert_data_set_does_not_exist(hosts, data_set_name):
    results = hosts.all.shell("dls '{0}'".format(data_set_name.upper()))
    for result in results.contacted.values():
        found = search(
            "^{0}$".format(data_set_name), result.get("stdout"), IGNORECASE | MULTILINE
        )
        assert not found


def assert_data_set_exists_on_volume(hosts, data_set_name, volume):
    results = hosts.all.shell("dls -s '{0}'".format(data_set_name.upper()))
    for result in results.contacted.values():
        found = search(
            r"^"
            + data_set_name
            + r"\s+[A-Z]+\s+[A-Z]+\s+[0-9]+\s+"
            + volume
            + r"\s+[0-9]+\s[0-9]+$",
            result.get("stdout"),
            IGNORECASE | MULTILINE,
        )
        assert not found


def assert_file_exists(hosts, path):
    results = hosts.all.stat(path=path)
    for result in results.contacted.values():
        assert result.get("stat").get("exists") is True


def assert_file_does_not_exist(hosts, path):
    results = hosts.all.stat(path=path)
    for result in results.contacted.values():
        assert result.get("stat").get("exists") is False


# ---------------------------------------------------------------------------- #
#                                Start of tests                                #
# ---------------------------------------------------------------------------- #

@pytest.mark.ds
@pytest.mark.parametrize(
    "backup_name,overwrite,recover",
    [
        ("DATA_SET", False, False),
        ("DATA_SET", True, True),
        ("DATA_SET", False, True),
        ("DATA_SET", True, False),
        ("UNIX", False, False),
        ("UNIX", True, True),
        ("UNIX", False, True),
        ("UNIX", True, False),
    ],
)
def test_backup_of_data_set(ansible_zos_module, backup_name, overwrite, recover):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        if not overwrite:
            delete_data_set_or_file(hosts, backup_name)
        delete_data_set_or_file(hosts, data_set_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=overwrite,
            recover=recover,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in output"
        assert_data_set_or_file_exists(hosts, backup_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts)

@pytest.mark.parametrize(
    "backup_name, terse",
    [
        #Only testing with Terse False as terse True is implicitly tested in all other test cases.
        ("DATA_SET", False),
    ],
)
def test_backup_and_restore_of_data_set_with_compression_and_terse(ansible_zos_module, backup_name, terse):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    backup_name_uncompressed = get_tmp_ds_name(1, 1)
    backup_name_compressed = get_tmp_ds_name(1, 1)
    size_uncompressed = 0
    size_compressed = 0

    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name_uncompressed)
        delete_data_set_or_file(hosts, backup_name_compressed)

        # Create large data set using decho
        shell_script_content = f"""#!/bin/bash
for i in {{1..100}}
do
  decho -a "this is a test line to make it big" "{data_set_name}"
done
"""
        hosts.all.shell(f"echo '{shell_script_content}' > shell_script.sh")
        hosts.all.shell("chmod +x shell_script.sh")
        hosts.all.shell("./shell_script.sh")

        cmd_result_dataset = hosts.all.shell(f"dls -j -s {data_set_name}")
        for result in cmd_result_dataset.contacted.values():
            output_dataset = json.loads(result.get("stdout"))
            size_dataset = int(output_dataset["data"]["datasets"][0]["used"])

        results_uncompressed = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name_uncompressed,
            compress=False,
            terse=True,
        )
        assert_module_did_not_fail(results_uncompressed)
        assert_data_set_or_file_exists(hosts, backup_name_uncompressed)

        cmd_result_uncompressed = hosts.all.shell(f"dls -j -s {backup_name_uncompressed}")
        for result in cmd_result_uncompressed.contacted.values():
            output = json.loads(result.get("stdout"))
            size_uncompressed = int(output["data"]["datasets"][0]["used"])

        results_compressed = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name_compressed,
            compress=True,
            terse=terse,
        )
        assert_module_did_not_fail(results_compressed)
        assert_data_set_or_file_exists(hosts, backup_name_compressed)

        cmd_result_compressed = hosts.all.shell(f"dls -j -s {backup_name_compressed}")
        for result in cmd_result_compressed.contacted.values():
            output_compressed = json.loads(result.get("stdout"))
            size_compressed = int(output_compressed["data"]["datasets"][0]["used"])

        #When using compress=True with terse=True(default), two different algorithms are used.
        #The zEDC hardware compresses the data, and then AMATERSE reprocess that compressed data.
        #It's not designed to compress already highly compressed data. The overhead of the AMATERSE,
        #combined with zEDC hardware compress, can outweigh the benefits.
        #This lead to a final file size larger than if you had only used Terse.

        # if size_uncompressed > 0:
        #     assert size_compressed > size_uncompressed, \
        #         f"Compressed size ({size_compressed}) is not smaller ({size_uncompressed})"\
        #         f"Dataset size is ({size_dataset})"

        # Restore testing is blocked due to ZOAU ISSUE NAZARE-11000

        #deleting dataset to test the restore.
        # delete_data_set_or_file(hosts, data_set_name)

        # hosts.all.zos_backup_restore(
        #     operation="restore",
        #     backup_name=backup_name_compressed
        # )
        # cmd_result_restored = hosts.all.shell(f"dls -j -s {data_set_name}")
        # for result in cmd_result_restored.contacted.values():
        #     output_restored = json.loads(result.get("stdout"))
        #     size_restored_compressed = int(output_restored["data"]["datasets"][0]["used"])

        # #deleting dataset to test the restore
        # delete_data_set_or_file(hosts, data_set_name)

        # hosts.all.zos_backup_restore(
        #     operation="restore",
        #     backup_name=backup_name_uncompressed,
        #     overwrite=True,
        # )
        # cmd_result_restored = hosts.all.shell(f"dls -j -s {data_set_name}")
        # for result in cmd_result_restored.contacted.values():
        #     output_restored = json.loads(result.get("stdout"))
        #     size_restored_uncompressed = int(output_restored["data"]["datasets"][0]["used"])
        # if size_dataset > 0:
        #     assert (size_dataset == size_restored_compressed == size_restored_uncompressed), \
        #         f"Restoration of {data_set_name} was not done properly. Unable to restore datasets."

    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name_uncompressed)
        delete_data_set_or_file(hosts, backup_name_compressed)
        delete_remnants(hosts)

# Commenting these tests because of issue https://github.com/ansible-collections/ibm_zos_core/issues/2235
# which likely is a zoau bug that needs to be fixed.
# @pytest.mark.parametrize(
#     "backup_name,overwrite",
#     [
#         ("DATA_SET", False),
#         ("DATA_SET", True),
#         ("UNIX", False),
#         ("UNIX", True),
#     ],
# )
# def test_backup_of_data_set_when_backup_dest_exists(
#     ansible_zos_module, backup_name, overwrite
# ):
#     hosts = ansible_zos_module
#     data_set_name = get_tmp_ds_name()
#     if backup_name == "DATA_SET":
#         backup_name = get_tmp_ds_name(1,1)
#     else:
#         backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
#     try:
#         create_data_set_or_file_with_contents(hosts, backup_name, DATA_SET_CONTENTS)
#         assert_data_set_or_file_exists(hosts, backup_name)
#         create_sequential_data_set_with_contents(
#             hosts, data_set_name, DATA_SET_CONTENTS
#         )
#         results = hosts.all.zos_backup_restore(
#             operation="backup",
#             data_sets=dict(include=data_set_name),
#             backup_name=backup_name,
#             overwrite=overwrite,
#         )
#         if overwrite:
#             assert_module_did_not_fail(results)
#             for result in results.contacted.values():
#                 assert result.get("backup_name") == backup_name, \
#                     f"Backup name '{backup_name}' not found in output"
#         else:
#             assert_module_failed(results)
#         assert_data_set_or_file_exists(hosts, backup_name)
#     finally:
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, backup_name)
#         delete_remnants(hosts)


@pytest.mark.parametrize(
    "backup_name,overwrite,recover",
    [
        ("DATA_SET", False, False),
        ("DATA_SET", True, True),
        ("DATA_SET", False, True),
        ("DATA_SET", True, False),
        ("UNIX", False, False),
        ("UNIX", True, True),
        ("UNIX", False, True),
        ("UNIX", True, False),
    ],
)
def test_backup_and_restore_of_data_set(
    ansible_zos_module, backup_name, overwrite, recover
):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    new_hlq  = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=overwrite,
            recover=recover,
        )
        assert_module_did_not_fail(results)
        # NEW: Assert backup_name appears in output
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in output"
        # Verify backup file/dataset exists
        assert_data_set_or_file_exists(hosts, backup_name)
        if not overwrite:
            new_hlq = "N" + get_random_q(4)
            hlqs.append(new_hlq)
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, backup_name)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
            overwrite=overwrite,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                "Backup name '{backup_name}' not found in restore output"
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts, hlqs)


@pytest.mark.parametrize(
    "backup_name,space,space_type",
    [
        ("DATA_SET", 10, "m"),
        ("DATA_SET", 10000, "k"),
        ("DATA_SET", 10, None),
        ("DATA_SET", 2, "cyl"),
        ("DATA_SET", 10, "trk"),
        ("UNIX", 10, "m"),
        ("UNIX", 10000, "k"),
        ("UNIX", 10, None),
        ("UNIX", 2, "cyl"),
        ("UNIX", 10, "trk"),
    ],
)
def test_backup_and_restore_of_data_set_various_space_measurements(
    ansible_zos_module, backup_name, space, space_type
):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        args = dict(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=True,
            space=space,
        )
        if space_type:
            args["space_type"] = space_type
        results = hosts.all.zos_backup_restore(**args)
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in backup output"
        assert_data_set_or_file_exists(hosts, backup_name)
        args = dict(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
            overwrite=True,
            space=space,
        )
        if space_type:
            args["space_type"] = space_type
        results = hosts.all.zos_backup_restore(**args)
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in restore output"
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts)


@pytest.mark.parametrize(
    "backup_name,overwrite",
    [
        ("DATA_SET", False),
        ("DATA_SET", True),
        ("UNIX", False),
        ("UNIX", True),
    ],
)
def test_backup_and_restore_of_data_set_when_restore_location_exists(
    ansible_zos_module, backup_name, overwrite
):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in backup output"
        assert_data_set_or_file_exists(hosts, backup_name)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in restore output"
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
            overwrite=overwrite,
        )
        if overwrite:
            assert_module_did_not_fail(results)
            for result in results.contacted.values():
                assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in restore output"
        else:
            assert_module_failed(results)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts, hlqs)


def test_backup_and_restore_of_multiple_data_sets(ansible_zos_module):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_name2 = get_tmp_ds_name()
    data_set_include = [data_set_name, data_set_name2]
    data_set_backup_location = get_tmp_ds_name(1, 1)
    new_hlq = get_random_q()
    hlqs.append(new_hlq)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        create_sequential_data_set_with_contents(
            hosts, data_set_name2, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_include),
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in backup output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in restore output"
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts, hlqs)


def test_backup_and_restore_of_multiple_data_sets_by_hlq(ansible_zos_module):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_name2 = get_tmp_ds_name()
    data_sets_hlq = "ANSIBLE.**"
    data_set_backup_location = get_tmp_ds_name(1, 1)
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        create_sequential_data_set_with_contents(
            hosts, data_set_name2, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_sets_hlq),
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in backup output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in restore output"
        assert_data_set_exists(hosts, data_set_backup_location)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts, hlqs)


def test_backup_and_restore_exclude_from_pattern(ansible_zos_module):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_name2 = get_tmp_ds_name()
    data_set_restore_location2 = get_tmp_ds_name(1, 1)
    data_set_backup_location = get_tmp_ds_name(1, 1)
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_restore_location2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        create_sequential_data_set_with_contents(
            hosts, data_set_name2, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include="ANSIBLE.**", exclude=data_set_name2),
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in backup output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in restore output"
        assert_data_set_exists(hosts, data_set_backup_location)
        assert_data_set_does_not_exist(hosts, data_set_restore_location2)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_name2)
        delete_data_set_or_file(hosts, data_set_restore_location2)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts, hlqs)


@pytest.mark.parametrize(
    "backup_name",
    [
        "DATA_SET",
        "DATA_SET",
        "UNIX",
        "UNIX",
    ],
)
def test_restore_of_data_set_when_backup_does_not_exist(
    ansible_zos_module, backup_name
):
    hlqs = []
    hosts = ansible_zos_module
    data_set_restore_location = get_tmp_ds_name(2, 2)
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    try:
        delete_data_set_or_file(hosts, data_set_restore_location)
        delete_data_set_or_file(hosts, backup_name)

        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
        )
        assert_module_failed(results)
    finally:
        delete_data_set_or_file(hosts, data_set_restore_location)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts, hlqs)


@pytest.mark.parametrize(
    "backup_name",
    [
        "DATA_SET",
        "DATA_SET",
        "UNIX",
        "UNIX",
    ],
)
def test_backup_of_data_set_when_data_set_does_not_exist(
    ansible_zos_module, backup_name
):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
        )
        assert_module_failed(results)
        assert_data_set_or_file_does_not_exist(hosts, backup_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts)

def test_backup_of_data_set_when_volume_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name(1, 1)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            # volume=get_unused_volume_serial(hosts),
            volume="@@@@",
            backup_name=data_set_backup_location,
        )
        assert_module_failed(results)
        assert_data_set_does_not_exist(hosts, data_set_backup_location)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts)


def test_restore_of_data_set_when_volume_does_not_exist(ansible_zos_module):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_restore_location = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name(1, 1)
    new_hlq = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_restore_location)
        delete_data_set_or_file(hosts, data_set_backup_location)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in backup output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            hlq=new_hlq,
            # volume=get_unused_volume_serial(hosts),
            volume="@@@@",
        )
        assert_module_failed(results)
        assert_data_set_does_not_exist(hosts, data_set_restore_location)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_restore_location)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts, hlqs)


def test_backup_and_restore_a_data_set_with_same_hlq(ansible_zos_module):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name()
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)
        hosts.all.shell(cmd="""decho "HELLO WORLD" {0}""".format(data_set_name))
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=data_set_backup_location,
        )
        delete_data_set_or_file(hosts, data_set_name)
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in restore output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_set_backup_location, \
                f"Backup name '{data_set_backup_location}' not found in restore output"
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        # Check the HLQ in the response
        assert_data_set_or_file_exists(hosts, data_set_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts)

# Commented this test because it was commented previously and keeps failing. Tracked on https://github.com/ansible-collections/ibm_zos_core/issues/2348
# def test_backup_and_restore_of_data_set_from_volume_to_new_volume(ansible_zos_module, volumes_on_systems):
#     hosts = ansible_zos_module
#     data_set_name = get_tmp_ds_name()
#     data_set_restore_location = get_tmp_ds_name()
#     hlqs = "TMPHLQ"
#     try:
#         volumes = Volume_Handler(volumes_on_systems)
#         volume_1 = volumes.get_available_vol()
#         volume_2 = volumes.get_available_vol()
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, data_set_restore_location)
#         create_sequential_data_set_with_contents(
#             hosts, data_set_name, DATA_SET_CONTENTS, volume_1
#         )
#         results = hosts.all.zos_backup_restore(
#             operation="backup",
#             data_sets=dict(include=data_set_name),
#             volume=volume_1,
#             backup_name=data_set_restore_location,
#             overwrite=True,
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_or_file_exists(hosts, data_set_restore_location)
#         results = hosts.all.zos_backup_restore(
#             operation="restore",
#             backup_name=data_set_restore_location,
#             overwrite=True,
#             volume=volume_2,
#             hlq=hlqs,
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_exists(hosts, data_set_restore_location)
#     finally:
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, data_set_restore_location)
#         delete_remnants(hosts, hlqs)


def test_backup_and_restore_of_sms_group(ansible_zos_module, volumes_sms_systems):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name()
    try:
        volumes = Volume_Handler(volumes_sms_systems)
        volume, smsgrp = volumes.get_available_vol_with_sms()
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS, volume
        )
        sms = {"storage_class":smsgrp}
        results = hosts.all.zos_backup_restore(
            data_sets=dict(include=data_set_name),
            operation="backup",
            volume=volume,
            backup_name=data_set_backup_location,
            overwrite=True,
            sms=sms,
        )
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        sms = {
            "disable_automatic_class":[data_set_name],
            "disable_automatic_storage_class":True
            }
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            volume=volume,
            sms=sms,
        )
        assert_module_did_not_fail(results)
        assert_data_set_exists_on_volume(hosts, data_set_name, volume)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)


def test_backup_and_restore_all_of_sms_group(ansible_zos_module, volumes_sms_systems):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name()
    try:
        volumes = Volume_Handler(volumes_sms_systems)
        volume, smsgrp = volumes.get_available_vol_with_sms()
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS, volume
        )
        sms = {"storage_class":smsgrp}
        for attempt in range(2):
            results = hosts.all.zos_backup_restore(
                data_sets=dict(include=data_set_name),
                operation="backup",
                volume=volume,
                backup_name=data_set_backup_location,
                overwrite=True,
                sms=sms,
            )
            for result in results.contacted.values():
                if result.get("failed", False) is not True:
                    break
                else:
                    if smsgrp == "PRIMARY":
                        sms = {"storage_class":"DB2SMS10"}
                    else:
                        sms = {"storage_class":"PRIMARY"}
        sc = sms["storage_class"]
        if sc not in {"DB2SMS10", "PRIMARY"}:
            pytest.skip(f"Skipping test: unsupported storage_class {sc}")
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        sms = {
            "disable_automatic_class":['**'],
            "disable_automatic_storage_class":True
            }
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            volume=volume,
            sms=sms,
        )
        assert_module_did_not_fail(results)
        assert_data_set_exists_on_volume(hosts, data_set_name, volume)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)


@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_backup_gds(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        # We need to replace hyphens because of NAZARE-10614: dzip fails archiving data set names with '-'
        data_set_name = get_tmp_ds_name(symbols=True).replace("-", "")
        backup_dest = get_tmp_ds_name(symbols=True).replace("-", "")
        results = hosts.all.shell(cmd=f"dtouch -tGDG -L3 '{data_set_name}'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dtouch -t{dstype} '{data_set_name}(+1)'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dtouch -t{dstype} '{data_set_name}(+1)'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=[f"{data_set_name}(-1)", f"{data_set_name}(0)"]),
            backup_name=backup_dest,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert result.get("backup_name") == backup_dest, \
                f"Backup_name '{backup_dest}' not found in backup output"
    finally:
        hosts.all.shell(cmd=f"drm ANSIBLE.* ")


@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_backup_into_gds(ansible_zos_module, dstype):
    """This test will create a dataset and backup it into a new generation of
    backup data sets.
    """
    try:
        hosts = ansible_zos_module
        # We need to replace hyphens because of NAZARE-10614: dzip fails archiving data set names with '-'
        data_set_name = get_tmp_ds_name(symbols=True).replace("-", "")
        ds_name = get_tmp_ds_name(symbols=True).replace("-", "")
        results = hosts.all.shell(cmd=f"dtouch -tGDG -L3 '{data_set_name}'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dtouch -t{dstype} '{data_set_name}(+1)'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.shell(cmd=f"dtouch -t{dstype} '{ds_name}'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        ds_to_write = f"{ds_name}(MEM)" if dstype in ['pds', 'pdse'] else ds_name
        results = hosts.all.shell(cmd=f"decho 'test line' '{ds_to_write}'")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        backup_target = f"{data_set_name}.G0002V00"
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=[ds_name]),
            backup_name=backup_target,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert result.get("backup_name") == backup_target, \
                f"Expected backup_name '{backup_target}' not found in backup output"
        escaped_ds_name = ds_name.replace('$', '\$')
        results = hosts.all.shell(cmd=f"drm \"{escaped_ds_name}\"")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        restore_source = f"{data_set_name}(0)"
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=restore_source,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert result.get("backup_name") == restore_source, \
                f"Backup_name '{restore_source}' not found in output"

    finally:
        hosts.all.shell(cmd=f"drm ANSIBLE.* ; drm OMVSADM.*")


def test_backup_tolerate_enqueue(ansible_zos_module):
    hosts = ansible_zos_module
    default_data_set_name_1 =  get_tmp_ds_name()
    default_data_set_name_2 =  get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    data_sets_hlq = "ANSIBLE.**"
    data_sets_backup_location = get_tmp_ds_name()
    try:
        hosts.all.shell(cmd="dtouch {0}".format(default_data_set_name_1))
        hosts.all.shell(cmd="dtouch {0}".format(default_data_set_name_2))
        hosts.all.shell(cmd="""decho "HELLO WORLD" "{0}" """.format(default_data_set_name_1))
        hosts.all.shell(cmd="""decho "HELLO WORLD" "{0}" """.format(default_data_set_name_2))
        hosts.all.file(path=temp_file, state="directory")
        hosts.all.shell(cmd=f"echo \"{c_pgm}\"  > {temp_file}/pdse-lock.c")
        hosts.all.shell(
            cmd=f"echo \"{call_c_jcl.format(default_data_set_name_1, temp_file)}\""+ " > {0}/call_c_pgm.jcl".format(temp_file)
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=temp_file)
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=temp_file)
        time.sleep(5)
        results = hosts.all.zos_backup_restore(
            operation="backup",
            recover=True,
            data_sets=dict(include=data_sets_hlq),
            backup_name=data_sets_backup_location,
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == data_sets_backup_location, \
                f"Backup name '{data_sets_backup_location}' not found in backup output"
        assert_data_set_or_file_exists(hosts, data_sets_backup_location)
    finally:
        hosts.all.shell(cmd="rm -rf " + temp_file)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(temp_file))
        hosts.all.shell(cmd=f"drm ANSIBLE.* ")


@pytest.mark.parametrize(
    "backup_name,overwrite,recover",
    [
        ("DATA_SET", True, True)
    ],
)
def test_backup_and_restore_of_data_set_tmphlq(
    ansible_zos_module, backup_name, overwrite, recover
):
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    new_hlq  = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=overwrite,
            tmp_hlq="TMPHLQ",
            recover=recover,
        )
        assert_module_did_not_fail(results)
        # NEW: Assert backup_name appears in output
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in output"
        # Verify backup file/dataset exists
        assert_data_set_or_file_exists(hosts, backup_name)
        if not overwrite:
            new_hlq = "N" + get_random_q(4)
            hlqs.append(new_hlq)
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, backup_name)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
            overwrite=overwrite,
            tmp_hlq="TMPHLQ",
        )
        assert_module_did_not_fail(results)
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                "Backup name '{backup_name}' not found in restore output"
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts, hlqs)

def test_list_cat_for_existing_data_set_with_tmp_hlq_option_restricted_user(ansible_zos_module, z_python_interpreter):
    """
    This tests the error message when a user cannot create data sets with a given HLQ.
    """
    managed_user = None
    managed_user_test_case_name = "managed_user_backup_of_data_set_tmphlq_restricted_user"
    try:
        # Initialize the Managed user API from the pytest fixture.
        managed_user = ManagedUser.from_fixture(ansible_zos_module, z_python_interpreter)

        # Important: Execute the test case with the managed users execution utility.
        managed_user.execute_managed_user_test(
            managed_user_test_case = managed_user_test_case_name, debug = True,
            verbose = True, managed_user_type=ManagedUserType.ZOS_LIMITED_HLQ)

    finally:
        # Delete the managed user on the remote host to avoid proliferation of users.
        managed_user.delete_managed_user()

def managed_user_backup_of_data_set_tmphlq_restricted_user(ansible_zos_module):
    backup_name = "DATA_SET"
    overwrite = True
    recover  = True
    hlqs = []
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    new_hlq  = "N" + get_random_q(4)
    hlqs.append(new_hlq)
    tmphlq = "NOPERMIT"
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    try:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=overwrite,
            tmp_hlq=tmphlq,
            recover=recover,
        )
        # NEW: Assert backup_name appears in output
        for result in results.contacted.values():
            assert result.get("backup_name") == '', \
                f"Backup name '{backup_name}' is there in output so tmphlq failed."
            assert result.get("changed", False) is False

    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts, hlqs)


def test_backup_of_vsam_index(ansible_zos_module, volumes_with_vvds):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    alternate_index = get_tmp_ds_name()
    backup_name = get_tmp_ds_name()

    try:
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        # Create VSAM KSDS
        create_vsam(
            hosts, data_set_name
        )
        # Create alternate indexes
        aix_cmd = f"""
echo '  DEFINE ALTERNATEINDEX (NAME({alternate_index}) -
  RELATE({data_set_name}) -
  KEYS(4 0) -
  VOLUMES({volume}) -
  CYLINDERS(10 1) -
  FREESPACE(10 10) -
  NONUNIQUEKEY) -
  DATA (NAME({alternate_index}.DATA)) -
  INDEX (NAME({alternate_index}.INDEX))  ' | mvscmdauth --pgm=IDCAMS --sysprint=* --sysin=stdin

        """
        results = hosts.all.shell(cmd=f"{aix_cmd}")
        assert_module_did_not_fail(results)


        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            index=True,
        )
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, backup_name)

        # Delete the vsam data set and alternate index
        delete_data_set(hosts, data_set_name)
        delete_data_set(hosts, alternate_index)

        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            index=True,
        )

        # Validate that both original vsam and alternate index exist
        vls_result = hosts.all.shell(f"vls {alternate_index}")
        assert_module_did_not_fail(vls_result)
        for result in vls_result.contacted.values():
            assert alternate_index in result.get("stdout")
            assert f"{alternate_index}.DATA" in result.get("stdout")
            assert f"{alternate_index}.INDEX" in result.get("stdout")
        vls_result = hosts.all.shell(f"vls {data_set_name}")
        assert_module_did_not_fail(vls_result)
        for result in vls_result.contacted.values():
            assert data_set_name in result.get("stdout")
            assert f"{data_set_name}.DATA" in result.get("stdout")
            assert f"{data_set_name}.INDEX" in result.get("stdout")
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, alternate_index)
        delete_data_set_or_file(hosts, backup_name)


def test_backup_and_restore_of_auth_shr_group(ansible_zos_module, volumes_sms_systems):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    data_set_backup_location = get_tmp_ds_name()
    try:
        volumes = Volume_Handler(volumes_sms_systems)
        volume, smsgrp = volumes.get_available_vol_with_sms()
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS, volume
        )
        results = hosts.all.zos_backup_restore(
            data_sets=dict(include=data_set_name),
            operation="backup",
            backup_name=data_set_backup_location,
            overwrite=True,
        )
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        delete_data_set_or_file(hosts, data_set_name)
        access = {
            "share":True,
            "auth":True
            }
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            access=access,
        )
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, data_set_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)