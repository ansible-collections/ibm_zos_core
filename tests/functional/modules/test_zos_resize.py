# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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

import pytest
from pipes import quote

# TODO: determine if data set names need to be more generic for testcases
# TODO: add additional tests to check additional data set creation parameter combinations


DEFAULT_VOLUME = "000000"
DEFAULT_VOLUME2 = "222222"

BOGUS_RESIZE_DSNAME = "notaggregatename"
DEFAULT_RESIZE_DSNAME = "USER.PRIVATE.RESZDS"
TEMP_RESIZE_PATH = "/tmp/ansible/jcl"


def test_resize_bad_aggname(ansible_zos_module):
    # Try to resize an aggregate that can not exist
    hosts = ansible_zos_module
    results = hosts.all.zos_resize(
        target=BOGUS_RESIZE_DSNAME,
        size=200,
    )
    for result in results.contacted.values():
        assert result.get("changed") is False

def test_resize_missing_aggname(ansible_zos_module):
    # Try to resize an aggregate that does not exist
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_RESIZE_DSNAME, state="absent")

    results = hosts.all.zos_resize(
        target=DEFAULT_RESIZE_DSNAME,
        size=200,
    )
    for result in results.contacted.values():
        assert result.get("changed") is False

def test_resize_actual_shrink(ansible_zos_module):
    hosts = ansible_zos_module
    defstr = "zfsadm define -aggregate {0} -volumes {1} -kilobytes 100 1".format(DEFAULT_RESIZE_DSNAME, DEFAULT_VOLUME)
    formstr = "zfsadm format -aggregate {0}".format(DEFAULT_RESIZE_DSNAME)
    mountstr = "/usr/sbin/mount -t zfs -f {0} {1}".format(DEFAULT_RESIZE_DSNAME, TEMP_RESIZE_PATH)

    hosts.all.command(defstr)
    hosts.all.command(formstr)
    hosts.all.file(path=TEMP_RESIZE_PATH, state="directory")
    hosts.all.command(mountstr)

    # This should only work if the data set was created, mounted rw
    # Testing shrink so we don't have to deal with out-of-space scenarios, leading to false-positive failure
    results = hosts.all.zos_resize(
        target=DEFAULT_RESIZE_DSNAME,
        size=50,
    )

    hosts.all.zos_data_set(name=DEFAULT_RESIZE_DSNAME, state="absent")
    hosts.all.file(path=TEMP_RESIZE_PATH, state="absent")

    for result in results.contacted.values():
        assert result.get("changed") is True


