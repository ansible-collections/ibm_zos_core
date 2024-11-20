#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
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

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

__metaclass__ = type

def make_temp_folder(hosts):
    """ Create temporary file on z/OS system and return the path """
    tempfile_name = ""
    results = hosts.all.tempfile(state="directory")
    for result in results.contacted.values():
        tempfile_name = result.get("path", "")
    return tempfile_name

def set_environment(ansible_zos_module, ds_name, space=1, space_type='m'):
    hosts = ansible_zos_module

    hosts.all.zos_data_set(name=ds_name, type="zfs", space_primary=space, space_type=space_type)
    temp_dir_name = make_temp_folder(hosts=hosts)
    hosts.all.command(
                cmd="usr/sbin/mount -t zfs -f {0} {1}".format(
                    ds_name, temp_dir_name
                )
            )
    hosts.all.command(
                cmd="head -c 1000000 /dev/urandom > {0}/test.txt".format(
                    temp_dir_name
                )
    )

    return temp_dir_name

def clean_up_environment(hosts, ds_name, temp_dir_name):
    hosts.all.command(cmd=f"usr/sbin/unmount {temp_dir_name}")
    hosts.all.zos_data_set(name=ds_name, state="absent")
    hosts.all.file(path=temp_dir_name, state="absent")

def test_grow_operation(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 2500
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name, size=size)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= size
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_shrink_operation(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 1400
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name, size=size)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= size
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)