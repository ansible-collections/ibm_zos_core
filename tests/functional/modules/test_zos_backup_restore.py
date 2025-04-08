# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2024
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

from ibm_zos_core.tests.helpers.dataset import (
    get_tmp_ds_name,
    get_random_q,
)
import pytest
from re import search, IGNORECASE, MULTILINE
import string
import random
import time
from ibm_zos_core.tests.helpers.utils import get_random_file_name

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
        results = hosts.all.zos_data_set(name=data_set_name, type="seq", volumes=volume)
    else:
        results = hosts.all.zos_data_set(name=data_set_name, type="seq")
    assert_module_did_not_fail(results)
    results = hosts.all.shell("decho '{0}' {1}".format(contents, data_set_name))
    assert_module_did_not_fail(results)


def create_file_with_contents(hosts, path, contents):
    results = hosts.all.shell("echo '{0}' > {1}".format(contents, path))
    assert_module_did_not_fail(results)


def delete_data_set_or_file(hosts, name):
    if name.startswith("/"):
        delete_file(hosts, name)
    else:
        delete_data_set(hosts, name)


def delete_data_set(hosts, data_set_name):
    hosts.all.zos_data_set(name=data_set_name, state="absent")


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
        for result in results.contacted.values():
            assert result.get("backup_name") == backup_name, \
                f"Backup name '{backup_name}' not found in output"
        assert_module_did_not_fail(results)
        assert_data_set_or_file_exists(hosts, backup_name)
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
def test_backup_of_data_set_when_backup_dest_exists(
    ansible_zos_module, backup_name, overwrite
):
    hosts = ansible_zos_module
    data_set_name = get_tmp_ds_name()
    if backup_name == "DATA_SET":
        backup_name = get_tmp_ds_name(1,1)
    else:
        backup_name = get_random_file_name(dir=TMP_DIRECTORY, prefix='.dzp')
    try:
        create_data_set_or_file_with_contents(hosts, backup_name, DATA_SET_CONTENTS)
        assert_data_set_or_file_exists(hosts, backup_name)
        create_sequential_data_set_with_contents(
            hosts, data_set_name, DATA_SET_CONTENTS
        )
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=data_set_name),
            backup_name=backup_name,
            overwrite=overwrite,
        )
        if overwrite:
            assert_module_did_not_fail(results)
            for result in results.contacted.values():
                assert result.get("backup_name") == backup_name, \
                    f"Backup name '{backup_name}' not found in output"
        else:
            assert_module_failed(results)
        assert_data_set_or_file_exists(hosts, backup_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, backup_name)
        delete_remnants(hosts)


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
                f"Expected backup_name '{backup_name}' in output"
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
        assert_data_set_or_file_exists(hosts, backup_name)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=backup_name,
            hlq=new_hlq,
            overwrite=overwrite,
        )
        if overwrite:
            assert_module_did_not_fail(results)
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
            assert result.get("backup_name") == data_set_backup_location
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
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
            assert result.get("backup_name") == data_set_backup_location
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
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
            assert result.get("backup_name") == data_set_backup_location  # Critical Line
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
            overwrite=True,
            recover=True,
            hlq=new_hlq,
        )
        assert_module_did_not_fail(results)
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
        assert_data_set_or_file_exists(hosts, data_set_backup_location)
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=data_set_backup_location,
        )
        assert_module_did_not_fail(results)
        # Check the HLQ in the response
        assert_data_set_or_file_exists(hosts, data_set_name)
    finally:
        delete_data_set_or_file(hosts, data_set_name)
        delete_data_set_or_file(hosts, data_set_backup_location)
        delete_remnants(hosts)


# def test_backup_and_restore_of_data_set_from_volume_to_new_volume(ansible_zos_module):
#     hosts = ansible_zos_module
#     try:
#         delete_data_set_or_file(hosts, DATA_SET_BACKUP_LOCATION)
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, data_set_name2)
#         delete_data_set_or_file(hosts, DATA_SET_RESTORE_LOCATION)
#         delete_data_set_or_file(hosts, DATA_SET_RESTORE_LOCATION2)
#         create_sequential_data_set_with_contents(
#             hosts, data_set_name, DATA_SET_CONTENTS, VOLUME
#         )
#         create_sequential_data_set_with_contents(
#             hosts, data_set_name2, DATA_SET_CONTENTS, VOLUME2
#         )
#         results = hosts.all.zos_backup_restore(
#             operation="backup",
#             data_sets=dict(include=DATA_SET_PATTERN),
#             volume=VOLUME,
#             backup_name=DATA_SET_BACKUP_LOCATION,
#             overwrite=True,
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_or_file_exists(hosts, DATA_SET_BACKUP_LOCATION)
#         results = hosts.all.zos_backup_restore(
#             operation="restore",
#             backup_name=DATA_SET_BACKUP_LOCATION,
#             overwrite=True,
#             volume=VOLUME,
#             hlq=NEW_HLQ,
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_exists(hosts, DATA_SET_RESTORE_LOCATION)
#         assert_data_set_does_not_exist(hosts, DATA_SET_RESTORE_LOCATION2)
#     finally:
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, data_set_name2)
#         delete_data_set_or_file(hosts, DATA_SET_RESTORE_LOCATION)
#         delete_data_set_or_file(hosts, DATA_SET_RESTORE_LOCATION2)
#         delete_data_set_or_file(hosts, DATA_SET_BACKUP_LOCATION)


# def test_backup_and_restore_of_full_volume(ansible_zos_module):
#     hosts = ansible_zos_module
#     try:
#         delete_data_set_or_file(hosts, DATA_SET_BACKUP_LOCATION)
#         delete_data_set_or_file(hosts, data_set_name)
#         create_sequential_data_set_with_contents(
#             hosts, data_set_name, DATA_SET_CONTENTS, VOLUME
#         )
#         results = hosts.all.zos_backup_restore(
#             operation="backup",
#             volume=VOLUME,
#             full_volume=True,
#             sms_storage_class="DB2SMS10",
#             backup_name=DATA_SET_BACKUP_LOCATION,
#             overwrite=True,
#             space=500,
#             space_type="m",
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_or_file_exists(hosts, DATA_SET_BACKUP_LOCATION)
#         delete_data_set_or_file(hosts, data_set_name)
#         results = hosts.all.zos_backup_restore(
#             operation="restore",
#             backup_name=DATA_SET_BACKUP_LOCATION,
#             overwrite=True,
#             volume=VOLUME,
#             full_volume=True,
#             sms_storage_class="DB2SMS10",
#             space=500,
#             space_type="m",
#         )
#         assert_module_did_not_fail(results)
#         assert_data_set_exists_on_volume(hosts, data_set_name, VOLUME)
#     finally:
#         delete_data_set_or_file(hosts, data_set_name)
#         delete_data_set_or_file(hosts, DATA_SET_BACKUP_LOCATION)


@pytest.mark.parametrize("dstype", ["seq", "pds", "pdse"])
def test_backup_gds(ansible_zos_module, dstype):
    try:
        hosts = ansible_zos_module
        # We need to replace hyphens because of NAZARE-10614: dzip fails archiving data set names with '-'
        data_set_name = get_tmp_ds_name(symbols=True).replace("-", "")
        backup_dest = get_tmp_ds_name(symbols=True).replace("-", "")
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
        results = hosts.all.zos_backup_restore(
            operation="backup",
            data_sets=dict(include=[f"{data_set_name}(-1)", f"{data_set_name}(0)"]),
            backup_name=backup_dest,
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
            assert result.get("backup_name") == backup_dest, \
                f"Expected backup_name '{backup_dest}' in output"
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
        results = hosts.all.zos_data_set(name=data_set_name, state="present", type="gdg", limit=3)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=f"{data_set_name}(+1)", state="present", type=dstype)
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_data_set(name=ds_name, state="present", type=dstype)
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
                f"Expected backup_name '{backup_target}' in output"
        escaped_ds_name = ds_name.replace('$', '\$')
        results = hosts.all.shell(cmd=f"drm \"{escaped_ds_name}\"")
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
        results = hosts.all.zos_backup_restore(
            operation="restore",
            backup_name=f"{data_set_name}(0)",
        )
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("module_stderr") is None
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
            assert result.get("backup_name") == data_sets_backup_location
        assert_data_set_or_file_exists(hosts, data_sets_backup_location)
    finally:
        hosts.all.shell(cmd="rm -rf " + temp_file)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(temp_file))
        hosts.all.shell(cmd=f"drm ANSIBLE.* ")
