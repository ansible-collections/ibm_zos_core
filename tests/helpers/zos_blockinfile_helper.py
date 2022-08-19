# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
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
from shellescape import quote
from pprint import pprint

__metaclass__ = type


def set_uss_test_env(test_name, hosts, test_env):
    test_env["TEST_FILE"] = test_env["TEST_DIR"] + test_name
    try:
        hosts.all.shell(cmd="mkdir -p {0}".format(test_env["TEST_DIR"]))
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], test_env["TEST_FILE"]))
    except Exception:
        clean_uss_test_env(test_env["TEST_DIR"], hosts)
        assert 1 == 0, "Failed to set the test env"


def clean_uss_test_env(test_dir, hosts):
    try:
        hosts.all.shell(cmd="rm -rf " + test_dir)
    except Exception:
        assert 1 == 0, "Failed to clean the test env"


def UssGeneral(test_name, ansible_zos_module, test_env, test_info, expected):
    hosts = ansible_zos_module
    set_uss_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["TEST_FILE"]
    results = hosts.all.zos_blockinfile(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") == 1
    cmdStr = "cat {0}".format(test_info["path"])
    results = hosts.all.shell(cmd=cmdStr)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("stdout") == expected
    clean_uss_test_env(test_env["TEST_DIR"], hosts)


def set_ds_test_env(test_name, hosts, test_env):
    TEMP_FILE = test_env["TEST_DIR"] + test_name
    hosts.all.shell(cmd="mkdir -p {0}".format(test_env["TEST_DIR"]))
    results = hosts.all.shell(cmd='hlq')
    for result in results.contacted.values():
        hlq = result.get("stdout")
    if(len(hlq) > 8):
        hlq = hlq[:8]
    test_env["DS_NAME"] = hlq + "." + test_name.upper() + "." + test_env["DS_TYPE"]

    try:
        hosts.all.zos_data_set(name=test_env["DS_NAME"], type=test_env["DS_TYPE"])
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], TEMP_FILE))
        if test_env["DS_TYPE"] in ["PDS", "PDSE"]:
            test_env["DS_NAME"] = test_env["DS_NAME"] + "(MEM)"
            hosts.all.zos_data_set(name=test_env["DS_NAME"], state="present", type="member")
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), test_env["DS_NAME"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), test_env["DS_NAME"])

        if test_env["ENCODING"] != "IBM-1047":
            hosts.all.zos_encode(src=TEMP_FILE, dest=test_env["DS_NAME"], from_encoding="IBM-1047", to_encoding=test_env["ENCODING"])
            # cmdStr = "/u/behnam/tools/cp_withencoding/bin/cp2 {0} {1} {2}".format(test_env["ENCODING"], quote(TEMP_FILE), quote(test_env["DS_NAME"]))
            # hosts.all.shell(cmd=cmdStr)
        else:
            hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + test_env["TEST_DIR"])
        cmdStr = "cat \"//'{0}'\" | wc -l ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        pprint(vars(results))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
    except Exception:
        clean_ds_test_env(test_env["DS_NAME"], hosts)
        assert 1 == 0, "Failed to set the test env"


def clean_ds_test_env(ds_name, hosts):
    ds_name = ds_name.replace("(MEM)", "")
    try:
        hosts.all.zos_data_set(name=ds_name, state="absent")
    except Exception:
        assert 1 == 0, "Failed to clean the test env"


def DsGeneral(test_name, ansible_zos_module, test_env, test_info, expected):
    hosts = ansible_zos_module
    set_ds_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["DS_NAME"]
    if test_env["ENCODING"]:
        test_info["encoding"] = test_env["ENCODING"]
    results = hosts.all.zos_blockinfile(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") == 1
    if test_env["ENCODING"] == 'IBM-1047':
        cmdStr = "cat \"//'{0}'\" ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("stdout") == expected
            # assert result.get("stdout").replace('\n', '').replace(' ', '') == expected.replace('\n', '').replace(' ', '')
    clean_ds_test_env(test_env["DS_NAME"], hosts)


def DsNotSupportedHelper(test_name, ansible_zos_module, test_env, test_info):
    hosts = ansible_zos_module
    results = hosts.all.shell(cmd='hlq')
    for result in results.contacted.values():
        hlq = result.get("stdout")
    assert len(hlq) <= 8 or hlq != ''
    test_env["DS_NAME"] = hlq + "." + test_name.upper() + "." + test_env["DS_TYPE"]
    results = hosts.all.zos_data_set(name=test_env["DS_NAME"], type=test_env["DS_TYPE"], replace='yes')
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") is True
    test_info["path"] = test_env["DS_NAME"]
    results = hosts.all.zos_blockinfile(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("msg") == "VSAM data set type is NOT supported"
    clean_ds_test_env(test_env["DS_NAME"], hosts)
