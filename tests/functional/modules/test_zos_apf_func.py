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
import os
import sys
import pytest

__metaclass__ = type


TEST_INFO = dict(
    test_add_del=dict(
        library="", state="present", force_dynamic=True
    ),
    test_add_del_volume=dict(
        library="", volume=" ", state="present", force_dynamic=True
    ),
    test_add_del_persist=dict(
        library="", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_add_del_volume_persist=dict(
        library="", volume=" ", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_batch_add_del=dict(
        batch=[dict(library="", volume=" "), dict(library="", volume=" "), dict(library="", volume=" ")],
        persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_operation_list=dict(
        operation="list"
    ),
    test_operation_list_with_filter=dict(
        operation="list", library=""
    )
)

add_expected = """/*BEGINAPFLIST*/
/*BEGINBLOCK*/
APFADDDSNAME({0})VOLUME({1})
/*ENDBLOCK*/
/*ENDAPFLIST*/"""

add_sms_expected = """/*BEGINAPFLIST*/
/*BEGINBLOCK*/
APFADDDSNAME({0})SMS
/*ENDBLOCK*/
/*ENDAPFLIST*/"""

add_batch_expected = """/*BEGINAPFLIST*/
/*BEGINBLOCK*/
APFADDDSNAME({0})VOLUME({1})
APFADDDSNAME({2})VOLUME({3})
APFADDDSNAME({4})VOLUME({5})
/*ENDBLOCK*/
/*ENDAPFLIST*/"""

del_expected = """/*BEGINAPFLIST*/
/*ENDAPFLIST*/"""


def run_shell_cmd(hosts, cmdStr):
    results = hosts.all.shell(cmd=cmdStr)
    pprint(vars(results))
    for result in results.contacted.values():
        out = result.get("stdout")
    return out


def persistds_create(hosts):
    cmdStr = "mvstmp APFTEST.PRST"
    prstds = run_shell_cmd(hosts, cmdStr)[:30]
    cmdStr = "dtouch -tseq {0}".format(prstds)
    run_shell_cmd(hosts, cmdStr)
    return prstds


def persistds_delele(hosts, ds):
    cmdStr = "drm {0}".format(ds)
    run_shell_cmd(hosts, cmdStr)


def set_test_env(hosts, test_info):
    # results = hosts.all.zos_data_set(name=ds, type="SEQ")
    cmdStr = "mvstmp APFTEST"
    ds = run_shell_cmd(hosts, cmdStr)[:25]
    cmdStr = "dtouch -tseq {0}".format(ds)
    run_shell_cmd(hosts, cmdStr)
    test_info['library'] = ds
    if test_info.get('volume'):
        cmdStr = "dls -l " + ds + " | awk '{print $5}' "
        vol = run_shell_cmd(hosts, cmdStr)
        test_info['volume'] = vol
    if test_info.get('persistent'):
        test_info['persistent']['data_set_name'] = persistds_create(hosts)


def clean_test_env(hosts, test_info):
    # hosts.all.zos_data_set(name=test_info['library'], state='absent')
    cmdStr = "drm {0}".format(test_info['library'])
    run_shell_cmd(hosts, cmdStr)
    if test_info.get('persistent'):
        # hosts.all.zos_data_set(name=test_info['persistent']['data_set_name'], state='absent')
        persistds_delele(hosts, test_info['persistent']['data_set_name'])


def test_add_del(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    clean_test_env(hosts, test_info)


def test_add_del_volume(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_volume']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    clean_test_env(hosts, test_info)


"""
def test_add_del_persist(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_persist']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_sms_expected.format(test_info['library'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    clean_test_env(hosts, test_info)
"""


def test_add_del_volume_persist(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_volume_persist']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_expected.format(test_info['library'], test_info['volume'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    clean_test_env(hosts, test_info)


def test_batch_add_del(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_batch_add_del']
    for item in test_info['batch']:
        set_test_env(hosts, item)
    test_info['persistent']['data_set_name'] = persistds_create(hosts)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_batch_expected.format(test_info['batch'][0]['library'], test_info['batch'][0]['volume'],
                                          test_info['batch'][1]['library'], test_info['batch'][1]['volume'],
                                          test_info['batch'][2]['library'], test_info['batch'][2]['volume'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    for item in test_info['batch']:
        clean_test_env(hosts, item)
    persistds_delele(hosts, test_info['persistent']['data_set_name'])


def test_operation_list(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_operation_list']
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        listJson = result.get("stdout")
    import json
    data = json.loads(listJson)
    assert data[0]['format'] in ['DYNAMIC', 'STATIC']
    del json


def test_operation_list_with_filter(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    hosts.all.zos_apf(**test_info)
    ti = TEST_INFO['test_operation_list_with_filter']
    ti['library'] = "APFTEST.*"
    results = hosts.all.zos_apf(**ti)
    pprint(vars(results))
    for result in results.contacted.values():
        listFiltered = result.get("stdout")
    assert test_info['library'] in listFiltered
    test_info['state'] = 'absent'
    hosts.all.zos_apf(**test_info)
    clean_test_env(hosts, test_info)

#
# Negative tests
#


def test_add_already_present(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 16
    test_info['state'] = 'absent'
    hosts.all.zos_apf(**test_info)
    clean_test_env(hosts, test_info)


def test_del_not_present(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del']
    set_test_env(hosts, test_info)
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 16
    clean_test_env(hosts, test_info)


def test_add_not_found(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del']
    test_info['library'] = 'APFTEST.FOO.BAR'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 16


def test_add_with_wrong_volume(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_volume']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    test_info['volume'] = 'T12345'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 16
    clean_test_env(hosts, test_info)


def test_persist_invalid_ds_format(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_persist']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    cmdStr = "decho \"some text to test persistent data_set format validattion.\" \"{0}\"".format(test_info['persistent']['data_set_name'])
    run_shell_cmd(hosts, cmdStr)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 8
    clean_test_env(hosts, test_info)


def test_persist_invalid_marker(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_persist']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    test_info['persistent']['marker'] = "# Invalid marker format"
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 4
    clean_test_env(hosts, test_info)


def test_persist_invalid_marker_len(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_persist']
    test_info['state'] = 'present'
    set_test_env(hosts, test_info)
    test_info['persistent']['marker'] = "/* {mark} This is a awfully lo%70sng marker */" % ("o")
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("msg") == 'marker length may not exceed 72 characters'
    clean_test_env(hosts, test_info)
