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

TEST_CONTENT = """Line 1 This is an example line
Line 2 Each line is unique in this file
Line 3 Ansible makes automation easier
Line 4 Blockinfile module is quite versatile
Line 5 Heres another distinct line of text
Line 6 The file will contain over 50 lines
Line 7 Adding dynamic content to the file
Line 8 This file resides in tmpexamplefiletxt
Line 9 Automation is the key to efficiency
Line 10 Lines continue for completeness
Line 11 Unique messages for every entry
Line 12 Building a robust example playbook
Line 13 Tasks are modular and reusable
Line 14 Collaboration improves coding
Line 15 Keep your scripts efficient and clean
Line 16 Block structure organizes content well
Line 17 New ideas can be integrated seamlessly
Line 18 Use variables for greater flexibility
Line 19 Extend functionality as needed
Line 20 Write processes optimized for scale
Line 21 Take care of file permissions carefully
Line 22 Ansible modules provide many capabilities
Line 23 This content is for demonstration
Line 24 Its crucial to check syntax accuracy
Line 25 Errorhandling ensures smoother workflows
Line 26 Insert text programmatically via Ansible
Line 27 Keeping automation fast and reproducible
Line 28 Advanced configurations are possible
Line 29 Be methodical while executing changes
Line 30 Aim for best practices in automation
Line 31 Documentation is important for sharing knowledge
Line 32 Placeholder line inserted into this file
Line 33 Each line is independently structured
Line 34 Following YAML conventions strictly
Line 35 Stay open to experimentation with techniques
Line 36 Streamlined execution enhances performance
Line 37 Checking logs is vital for debugging
Line 38 A file with many diverse lines
Line 39 Files must serve practical purposes always
Line 40 Diverse content adds complexity intelligently
Line 41 Build files layer by layer strategically
Line 42 Start simple and expand logically
Line 43 Maintain steady practices with configuration
Line 44 Thoughtful lines reflecting utility often
Line 45 Programmatically inserted output aligns nicely
Line 46 Securing automation loop end validation
Line 47 Ensuring automation processes are stable
Line 48 Adding clarity to content is key
Line 49 Debugging is an essential step
Line 50 Final lines complete the example file"""

TEST_AFTER = """Line 1 This is an example line
Line 2 Each line is unique in this file
Line 3 Ansible makes automation easier
Line 4 Blockinfile module is quite versatile
Line 5 Heres another distinct line of text
Line 6 The file will contain over 50 lines
Line 7 Adding dynamic content to the file
Line 8 This file resides in tmpexamplefiletxt
Line 9 Automation is the key to efficiency
Line 10 Lines continue for completeness
"""

TEST_BEFORE = """Line 30 Aim for best practices in automation
Line 31 Documentation is important for sharing knowledge
Line 32 Placeholder line inserted into this file
Line 33 Each line is independently structured
Line 34 Following YAML conventions strictly
Line 35 Stay open to experimentation with techniques
Line 36 Streamlined execution enhances performance
Line 37 Checking logs is vital for debugging
Line 38 A file with many diverse lines
Line 39 Files must serve practical purposes always
Line 40 Diverse content adds complexity intelligently
Line 41 Build files layer by layer strategically
Line 42 Start simple and expand logically
Line 43 Maintain steady practices with configuration
Line 44 Thoughtful lines reflecting utility often
Line 45 Programmatically inserted output aligns nicely
Line 46 Securing automation loop end validation
Line 47 Ensuring automation processes are stable
Line 48 Adding clarity to content is key
Line 49 Debugging is an essential step
Line 50 Final lines complete the example file"""

TEST_BEFORE_AFTER = """Line 1 This is an example line
Line 2 Each line is unique in this file
Line 3 Ansible makes automation easier
Line 4 Blockinfile module is quite versatile
Line 5 Heres another distinct line of text
Line 6 The file will contain over 50 lines
Line 7 Adding dynamic content to the file
Line 8 This file resides in tmpexamplefiletxt
Line 9 Automation is the key to efficiency
Line 10 Lines continue for completeness
Line 30 Aim for best practices in automation
Line 31 Documentation is important for sharing knowledge
Line 32 Placeholder line inserted into this file
Line 33 Each line is independently structured
Line 34 Following YAML conventions strictly
Line 35 Stay open to experimentation with techniques
Line 36 Streamlined execution enhances performance
Line 37 Checking logs is vital for debugging
Line 38 A file with many diverse lines
Line 39 Files must serve practical purposes always
Line 40 Diverse content adds complexity intelligently
Line 41 Build files layer by layer strategically
Line 42 Start simple and expand logically
Line 43 Maintain steady practices with configuration
Line 44 Thoughtful lines reflecting utility often
Line 45 Programmatically inserted output aligns nicely
Line 46 Securing automation loop end validation
Line 47 Ensuring automation processes are stable
Line 48 Adding clarity to content is key
Line 49 Debugging is an essential step
Line 50 Final lines complete the example file"""

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
        "regexp":"^Line\s\d+\s.+$",
        "after":"Line 10 Lines continue for completeness",
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
            assert result.get("found") == 40
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^Line\s\d+\s.+$",
        "after":"Line 35 Lines continue for completeness",
        "replace":"# New empty line",
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
            assert result.get("found") == 40
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


def test_uss_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^Line\s\d+\s.+$",
        "before":"Line 30 Aim for best practices in automation",
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
            assert result.get("found") == 29
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^Line\s\d+\s.+$",
        "after":"Line 10 Lines continue for completeness",
        "before":"Line 30 Aim for best practices in automation",
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
            assert result.get("found") == 19
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            result.get("stdout") == TEST_BEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

# @pytest.mark.ds
# @pytest.mark.parametrize("dstype", DS_TYPE)
# def test_ds_file(ansible_zos_module, dstype):
#     hosts = ansible_zos_module
#     ds_type = dstype
#     params = {
#         "regexp":"^Line\s\d+\s.+$",
#         "after":"Line 18 Use variables for greater flexibility",
#         "before":"Line 38 A file with many diverse lines",
#     }
#     ds_name = get_tmp_ds_name()
#     temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#     content = TEST_CONTENT
#     try:
#         ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#         params["target"] = ds_full_name
#         results = hosts.all.zos_replace(**params)
#         for result in results.contacted.values():
#             print(result)
#         results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
#         for result in results.contacted.values():
#             print(result)
#     finally:
#         remove_ds_environment(ansible_zos_module, ds_name)