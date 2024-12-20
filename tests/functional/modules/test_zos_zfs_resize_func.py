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
import os
from shellescape import quote

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

NO_AUTO_INCREMENT= """hosts : zvm
  collections :
    - ibm.ibm_zos_core
  gather_facts: False
  vars:
    ZOAU: "{0}"
    PYZ: "{1}"
  environment:
    _BPXK_AUTOCVT: "ON"
    ZOAU_HOME: "{0}"
    PYTHONPATH: "{0}/lib/{2}"
    LIBPATH: "{0}/lib:{1}/lib:/lib:/usr/lib:."
    PATH: "{0}/bin:/bin:/usr/lpp/rsusr/ported/bin:/var/bin:/usr/lpp/rsusr/ported/bin:/usr/lpp/java/java180/J8.0_64/bin:{1}/bin:"
    _CEE_RUNOPTS: "FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)"
    _TAG_REDIR_ERR: "txt"
    _TAG_REDIR_IN: "txt"
    _TAG_REDIR_OUT: "txt"
    LANG: "C"
  tasks:
    - name: Create ZFS.
      block:
        - name: Create data set to ZFS
          zos_data_set:
            name: {3}
            type: zfs
            space_primary: 1
            space_type: m
            replace: true

        - name: Create mount dir on z/OS USS.
          file:
            path: {4}
            state: directory

        - name: Mount ZFS data set.
          command: /usr/sbin/mount -t zfs -f {3} {4}

        - name: Create folder.
          shell: mkdir {4}/folder

        - name: Create a folder.
          shell: touch {4}/folder/test.txt
        - name: Write bytes on file.
          shell: head -c 150000 /dev/urandom > {4}/folder/test.txt

        - name: Create a folder.
          shell: touch {4}/folder/test1.txt
        - name: Write bytes on file.
          shell: head -c 100000 /dev/urandom > {4}/folder/test1.txt

        - name: Create a folder.
          shell: touch {4}/folder/test3.txt
        - name: Write bytes on file.
          shell: head -c 1000000 /dev/urandom > {4}/folder/test3.txt

        - name: Create a folder.
          shell: touch {4}/folder/test4.txt
        - name: Write bytes on file.
          shell: head -c 100000 /dev/urandom > {4}/folder/test4.txt

        - name: Create a folder.
          shell: touch {4}/folder/test5.txt
        - name: Write bytes on file.
          shell: head -c 100000 /dev/urandom > {4}/folder/test5.txt

        - name: Create a folder.
          shell: touch {4}/folder/test7.txt
        - name: Write bytes on file.
          shell: head -c 100000 /dev/urandom > {4}/folder/test7.txt

        - name: Remove a folder.
          shell: rm  {4}/folder/test3.txt

        - name:  Shrink ZFS aggregate in k and auto_increment.
          zos_zfs_resize:
            target: {3}
            size: 900
            no_auto_increment: {5}
          poll: 0
          register: shrink_output

        - name: Create a folder.
          shell: touch {4}/folder/test6.txt
        - name: Write bytes on file.
          shell: head -c 100000 /dev/urandom > {4}/folder/test6.txt
          poll: 0

      always:
        - name: Unmount ZFS data set.
          command: "/usr/sbin/unmount {4}"

        - name: Delete ZFS data set.
          zos_data_set:
            name: {3}
            state: absent

        - name: Unmount ZFS data set.
          command: rm {4}"
"""

INVENTORY = """all:
  hosts:
    zvm:
      ansible_host: {0}
      ansible_ssh_private_key_file: {1}
      ansible_user: {2}
      ansible_python_interpreter: /allpython/3.11/usr/lpp/IBM/cyp/v3r11/pyz/bin/python3"""

def make_temp_folder(hosts):
    """ Create temporary file on z/OS system and return the path """
    tempfile_name = ""
    results = hosts.all.tempfile(state="directory")
    for result in results.contacted.values():
        tempfile_name = result.get("path", "")
    return tempfile_name

def set_environment(ansible_zos_module, ds_name, space=1, space_type='m'):
    """Create ZFS data set, mount folder and populate space of the zfs

    Parameters
    ----------
        ansible_zos_module : object
            Ansible object to execute commands.
        ds_name : str
            ZFS name.
        space : int
            space of ZFS data set.
        space_type : str
            space type use to create the ZFS.

    Returns
    -------
        temp_dir_name : str
            The folder where the zfs is mount.
    """
    hosts = ansible_zos_module

    hosts.all.zos_data_set(name=ds_name, type="zfs", space_primary=space, space_type=space_type)
    temp_dir_name = make_temp_folder(hosts=hosts)
    hosts.all.command(
                cmd="usr/sbin/mount -t zfs -f {0} {1}".format(
                    ds_name,
                    temp_dir_name
                )
            )
    if space_type == "m":
        bits_wr = 1000000
    else:
        bits_wr = 10000

    hosts.all.command(
                cmd="head -c {0} /dev/urandom > {1}/test.txt".format(
                    bits_wr,
                    temp_dir_name
                )
    )

    return temp_dir_name

def clean_up_environment(hosts, ds_name, temp_dir_name):
    """Unmount delete ZFS and delete folder.

    Parameters
    ----------
        hosts : object
            Ansible object to execute commands.
        ds_name : str
            ZFS name.
        temp_dir_name : str
            Folder where the ZFS is mounted.
    """
    hosts.all.command(cmd=f"usr/sbin/unmount {temp_dir_name}")
    hosts.all.zos_data_set(name=ds_name, state="absent")
    hosts.all.file(path=temp_dir_name, state="absent")

#########################
# Positive test cases
#########################

def test_grow_operation(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 2500
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('new_size') >= size
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_shrink_operation(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 1200
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('new_size') <= size
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_grow_n_shrink_operations_space_type_m(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 3
    shrink_size = 2
    space_type = "m"
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                                size=grow_size,
                                                space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('space_type') == space_type
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('new_size') >= grow_size

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('space_type') == space_type
            assert result.get('new_size') <= shrink_size
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_grow_n_shrink_operations_space_type_trk(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 400
    shrink_size = 200
    space_type = "trk"
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= grow_size
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('space_type') == space_type

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('new_size') <= shrink_size
            assert result.get('space_type') == space_type
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_grow_n_shrink_operations_space_type_cyl(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 3
    shrink_size = 2
    space_type = "cyl"
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('new_size') >= grow_size
            assert result.get('space_type') == space_type

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            space_type=space_type)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('new_size') <= shrink_size
            assert result.get('space_type') == space_type
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)


def test_grow_n_shrink_operation_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 2000
    shrink_size = 1800
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            verbose=True)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= grow_size
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert result.get("verbose_output") is not None

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            verbose=True)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= shrink_size
            assert result.get('space_type') == "k"
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get("verbose_output") is not None
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_grow_n_shrink_operations_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 1800
    shrink_size = 1200
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            verbose=True)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= grow_size
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert result.get("verbose_output") is not None
            assert "Printing contents of table at address" in result.get("stdout")

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            verbose=True)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= grow_size
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert result.get("verbose_output") is not None
            assert "print of in-memory trace table has completed" in result.get('stdout')

    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_grow_n_shrink_operations_trace_uss(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 1800
    shrink_size = 1200
    trace_destination_file = "/" + get_random_file_name(dir="tmp")
    trace_destination_file_s = "/" + get_random_file_name(dir="tmp")
    try:
        hosts.all.shell(cmd="touch {0}".format(trace_destination_file))
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            trace_destination=trace_destination_file)

        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= grow_size
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert "Printing contents of table at address" in result.get("stdout")
            cmd = "cat {0}".format(trace_destination_file)
            output_of_trace_file = hosts.all.shell(cmd=cmd)
            for out in output_of_trace_file.contacted.values():
                assert out.get("stdout") is not None

        hosts.all.shell(cmd="touch {0}".format(trace_destination_file_s))
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            trace_destination=trace_destination_file_s)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= grow_size
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert "print of in-memory trace table has completed" in result.get('stdout')
            cmd = "cat {0}".format(trace_destination_file_s)
            output_of_trace_file = hosts.all.shell(cmd=cmd)
            for out in output_of_trace_file.contacted.values():
                assert out.get("stdout") is not None

    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

@pytest.mark.parametrize("trace_destination", ["seq", "pds", "pdse"])
def test_grow_n_shrink_operations_trace_ds(ansible_zos_module, trace_destination):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    grow_size = 1800
    shrink_size = 1200

    trace_destination_ds = get_tmp_ds_name()
    trace_destination_ds_s= get_tmp_ds_name()
    try:
        if trace_destination == "seq":
            hosts.all.zos_data_set(name=trace_destination_ds, type=trace_destination, record_length=200)
        else:
            hosts.all.zos_data_set(name=trace_destination_ds, type=trace_destination, record_length=200)
            trace_destination_ds = trace_destination_ds + "(MEM)"
            hosts.all.zos_data_set(name=trace_destination_ds, state="present", type="member")

        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=grow_size,
                                            trace_destination=trace_destination_ds)

        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "grown" in result.get('stdout')
            assert result.get('new_size') >= grow_size
            assert result.get('new_size') >= result.get('old_size')
            assert result.get('new_free_space') >= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert "Printing contents of table at address" in result.get("stdout")
            cmd = "cat \"//'{0}'\" ".format(trace_destination_ds)
            output_of_trace_file = hosts.all.shell(cmd=cmd)
            for out in output_of_trace_file.contacted.values():
                assert out.get("stdout") is not None

        if trace_destination == "seq":
            hosts.all.zos_data_set(name=trace_destination_ds_s, type=trace_destination, record_length=200)
        else:
            hosts.all.zos_data_set(name=trace_destination_ds_s, type=trace_destination, record_length=200)
            trace_destination_ds_s = trace_destination_ds_s + "(MEM)"
            hosts.all.zos_data_set(name=trace_destination_ds_s, state="present", type="member")

        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=shrink_size,
                                            trace_destination=trace_destination_ds_s)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert "shrunk" in result.get('stdout')
            assert result.get('new_size') <= grow_size
            assert result.get('new_size') <= result.get('old_size')
            assert result.get('new_free_space') <= result.get('old_free_space')
            assert result.get('space_type') == "k"
            assert "print of in-memory trace table has completed" in result.get('stdout')
            cmd = "cat \"//'{0}'\" ".format(trace_destination_ds_s)
            output_of_trace_file = hosts.all.shell(cmd=cmd)
            for out in output_of_trace_file.contacted.values():
                assert out.get("stdout") is not None

    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)
        if trace_destination == "pds" or trace_destination == "pdse":
            trace_destination_ds = trace_destination_ds.split("(")[0]
            trace_destination_ds_s = trace_destination_ds_s.split("(")[0]
        hosts.all.zos_data_set(name=trace_destination_ds, state="absent")
        hosts.all.zos_data_set(name=trace_destination_ds_s, state="absent")

#########################
# Negative test cases
#########################

@pytest.mark.parametrize("space_type", ["K", "TRK", "CYL", "M", "G"])
def test_space_type_not_accept(ansible_zos_module, space_type):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 2500
    results = hosts.all.zos_zfs_resize(target=ds_name,
                                        size=size,
                                        space_type=space_type)
    for result in results.contacted.values():
        assert result.get('failed') == True
        assert result.get('msg') == "value of space_type must be one of: k, m, g, cyl, trk, got: {0}".format(space_type)

def test_target_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 2500
    results = hosts.all.zos_zfs_resize(target=ds_name,
                                        size=size,)
    for result in results.contacted.values():
        assert result.get('target') == ds_name
        assert result.get('size') == size
        assert result.get('rc') == 1
        assert result.get('changed') is False
        assert result.get('msg') == "ZFS Target {0} does not exist".format(ds_name)

def test_mount_point_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 2500
    try:
        hosts.all.zos_data_set(name=ds_name, type="zfs", space_primary=1, space_type="m")
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size,)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('size') == size
            assert result.get('rc') == 1
            assert result.get('changed') is False
            assert  "No mount points were found in the following output:" in result.get('msg')
    finally:
        hosts.all.zos_data_set(name=ds_name, state="absent")

def test_no_operation_executed(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 1440
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size,)
        for result in results.contacted.values():
            assert result.get("changed") == False
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 0
            assert result.get('size') == size
            assert result.get('space_type') == "k"
            assert result.get('stdout') == "Same size as size of the file {0}".format(ds_name)
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_no_space_to_operate(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 100
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size,)
        for result in results.contacted.values():
            assert result.get("changed") == False
            assert result.get('target') == ds_name
            assert result.get('mount_target') == "/SYSTEM" + mount_folder
            assert result.get('rc') == 1
            assert result.get('size') == size
            assert result.get('space_type') == "k"
            assert result.get('msg') == "Not enough free space in the filesystem to shrink."
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

@pytest.mark.parametrize("trace_destination", ["uss", "dataset", "member"])
def test_trace_operation_fail(ansible_zos_module, trace_destination):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    trace_destination_file= "/" + get_random_file_name(dir="tmp") if trace_destination == "uss" else get_tmp_ds_name()
    size = 2500
    if trace_destination == "member":
        trace_destination_file = trace_destination_file + "(MEM)"
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size,
                                            trace_destination=trace_destination_file)
        for result in results.contacted.values():
            assert result.get('target') == ds_name
            assert result.get('size') == size
            assert result.get('rc') == 1
            assert result.get('changed') is False
            if trace_destination == "uss":
                assert result.get('msg') == "Destination trace {0} does not exist".format("file")
            elif trace_destination == "dataset":
                assert result.get('msg') == "Destination trace {0} does not exist".format("dataset")
            else:
                assert result.get('msg') == "Destination trace {0} does not exist".format("member")
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

def test_fail_operation(ansible_zos_module):
    hosts = ansible_zos_module
    ds_name = get_tmp_ds_name()
    mount_folder = ""
    size = 200
    try:
        mount_folder = set_environment(ansible_zos_module=hosts, ds_name=ds_name)
        results = hosts.all.zos_zfs_resize(target=ds_name,
                                            size=size,)
        for result in results.contacted.values():
            assert result.get("failed") == True
            assert result.get('changed') == False
            assert "resize command returned non-zero code" in result.get("module_stdout")
            assert result.get('rc') == 1
    finally:
        clean_up_environment(hosts=hosts, ds_name=ds_name, temp_dir_name=mount_folder)

#############################
# No auto increment playbook
#############################

def test_no_auto_increment(get_config):
    ds_name = get_tmp_ds_name()
    mount_point = "/" + get_random_file_name(dir="tmp")
    path = get_config
    with open(path, 'r') as file:
        enviroment = yaml.safe_load(file)
    ssh_key = enviroment["ssh_key"]
    hosts = enviroment["host"].upper()
    user = enviroment["user"].upper()
    python_path = enviroment["python_path"]
    cut_python_path = python_path[:python_path.find('/bin')].strip()
    zoau = enviroment["environment"]["ZOAU_ROOT"]
    python_version = cut_python_path.split('/')[2]

    try:
        playbook = "playbook.yml"
        inventory = "inventory.yml"
        os.system("echo {0} > {1}".format(quote(NO_AUTO_INCREMENT.format(
            zoau,
            cut_python_path,
            python_version,
            ds_name,
            mount_point,
            "True"
        )), playbook))
        os.system("echo {0} > {1}".format(quote(INVENTORY.format(
            hosts,
            ssh_key,
            user,
        )), inventory))
        command = "ansible-playbook -i {0} {1}".format(
            inventory,
            playbook
        )
        stdout = os.system(command)
        assert stdout == 1
    finally:
        os.remove("inventory.yml")
        os.remove("playbook.yml")

def test_no_auto_increment_accept(get_config):
    ds_name = get_tmp_ds_name()
    mount_point = "/" + get_random_file_name(dir="tmp")
    path = get_config
    with open(path, 'r') as file:
        enviroment = yaml.safe_load(file)
    ssh_key = enviroment["ssh_key"]
    hosts = enviroment["host"].upper()
    user = enviroment["user"].upper()
    python_path = enviroment["python_path"]
    cut_python_path = python_path[:python_path.find('/bin')].strip()
    zoau = enviroment["environment"]["ZOAU_ROOT"]
    python_version = cut_python_path.split('/')[2]

    try:
        playbook = "playbook.yml"
        inventory = "inventory.yml"
        os.system("echo {0} > {1}".format(quote(NO_AUTO_INCREMENT.format(
            zoau,
            cut_python_path,
            python_version,
            ds_name,
            mount_point,
            "False"
        )), playbook))
        os.system("echo {0} > {1}".format(quote(INVENTORY.format(
            hosts,
            ssh_key,
            user,
        )), inventory))
        command = "ansible-playbook -i {0} {1}".format(
            inventory,
            playbook
        )
        stdout = os.system(command)
        assert stdout == 0
    finally:
        os.remove("inventory.yml")
        os.remove("playbook.yml")