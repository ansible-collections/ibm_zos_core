#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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
from shellescape import quote

from ibm_zos_core.tests.helpers.dataset import (
    get_tmp_ds_name,
    get_random_q,
)

from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

TEST_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_AFTER = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
=/usr/lpp/zoautil/v100
export
export _BPXK_AUTOCVT"""

TEST_AFTER_REPLACE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
HOME_ROOT=/usr/lpp/zoautil/v100
export HOME_ROOT
export _BPXK_AUTOCVT"""

TEST_AFTER_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100"""

TEST_AFTER_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export TMP=tmp/etc
export TMP=tmp/etc"""

TEST_BEFORE = """if [ -z ] && tty -s;
then
    export =none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_REPLACE = """if [ -z STAND ] && tty -s;
then
    export STAND=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER = """if [ -z STEPLIB ] && tty -s;
then
    port STEPLIB=none
    ec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_REPLACE = """if [ -z STEPLIB ] && tty -s;
then
    ixport STEPLIB=none
    ixec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_LINE = """if [ -z STEPLIB ] && tty -s;
then
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export SHELL
    export SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

#####################
#  Set up testing
#####################

TMP_DIRECTORY = "/tmp/"

DS_TYPE = ['seq', 'pds', 'pdse']

def set_uss_environment(ansible_zos_module, content, file):
    hosts = ansible_zos_module
    hosts.all.file(path=file, state="touch")
    hosts.all.shell(cmd=f"echo \"{content}\" > {file}")

def remove_uss_environment(ansible_zos_module, file):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="rm " + file)

def set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
    hosts.all.zos_data_set(name=ds_name, type=ds_type)
    if ds_type in ["pds", "pdse"]:
        ds_full_name = ds_name + "(MEM)"
        hosts.all.zos_data_set(name=ds_full_name, state="present", type="member")
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
    else:
        ds_full_name = ds_name
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
    hosts.all.shell(cmd=cmd_str)
    hosts.all.shell(cmd="rm -rf " + temp_file)
    return ds_full_name

def remove_ds_environment(ansible_zos_module, ds_name):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=ds_name, state="absent")

#####################
# Testing
#####################

def test_uss_after(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == True
            assert result.get("target") == full_path
            #assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            print(result)
            result.get("stdout") == TEST_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "replace":"HOME_ROOT",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == True
            assert result.get("target") == full_path
            #assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            print(result)
            result.get("stdout") == TEST_AFTER_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_AFTER_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
        "replace":"export TMP=tmp/etc",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_AFTER_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"STEPLIB",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"STEPLIB",
        "replace":"STAND",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
        "replace":"PATH=/usr/lpp/zoautil/v100/bin",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
        "replace":"ix",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_AFTER_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
        "replace":"export SHELL",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_AFTER_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
        "replace":"export SHELL",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE_AFTER_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            #assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_AFTER
            print(result)
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)