# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
from shellescape import quote
from pprint import pprint
import os
import sys
import pytest

__metaclass__ = type


TEST_INFO = dict(
    test_add_del=dict(
        dsname="", state="present", force_dynamic=True
    ),
    test_add_del_volume=dict(
        dsname="", volume=" ", state="present", force_dynamic=True
    ),
    test_add_del_persist=dict(
        dsname="", persistent=dict(persistds="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_add_del_volume_persist=dict(
        dsname="", volume=" ", persistent=dict(persistds="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_batch_add_del=dict(
        batch=[dict(dsname="", volume=" "), dict(dsname="", volume=" "), dict(dsname="", volume=" ")],
        persistent=dict(persistds="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
    ),
    test_operation_list=dict(
        operation="list"
    ),
    test_operation_list_with_filter=dict(
        operation="list", dsname=""
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
    test_info['dsname'] = ds
    if test_info.get('volume'):
        cmdStr = "dls -l " + ds + " | awk '{print $5}' "
        vol = run_shell_cmd(hosts, cmdStr)
        test_info['volume'] = vol
    if test_info.get('persistent'):
        test_info['persistent']['persistds'] = persistds_create(hosts)


def clean_test_env(hosts, test_info):
    # hosts.all.zos_data_set(name=test_info['dsname'], state='absent')
    cmdStr = "drm {0}".format(test_info['dsname'])
    run_shell_cmd(hosts, cmdStr)
    if test_info.get('persistent'):
        # hosts.all.zos_data_set(name=test_info['persistent']['persistds'], state='absent')
        persistds_delele(hosts, test_info['persistent']['persistds'])


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


def test_add_del_persist(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_persist']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_sms_expected.format(test_info['dsname'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    clean_test_env(hosts, test_info)


def test_add_del_volume_persist(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_add_del_volume_persist']
    set_test_env(hosts, test_info)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_expected.format(test_info['dsname'], test_info['volume'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    clean_test_env(hosts, test_info)


def test_batch_add_del(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO['test_batch_add_del']
    for item in test_info['batch']:
        set_test_env(hosts, item)
    test_info['persistent']['persistds'] = persistds_create(hosts)
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    add_exptd = add_batch_expected.format(test_info['batch'][0]['dsname'], test_info['batch'][0]['volume'],
                                          test_info['batch'][1]['dsname'], test_info['batch'][1]['volume'],
                                          test_info['batch'][2]['dsname'], test_info['batch'][2]['volume'])
    add_exptd = add_exptd.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == add_exptd
    test_info['state'] = 'absent'
    results = hosts.all.zos_apf(**test_info)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get("rc") == 0
    del_exptd = del_expected.replace(" ", "")
    cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['persistds'])
    actual = run_shell_cmd(hosts, cmdStr).replace(" ", "")
    assert actual == del_exptd
    for item in test_info['batch']:
        clean_test_env(hosts, item)
    persistds_delele(hosts, test_info['persistent']['persistds'])


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
    ti['dsname'] = "APFTEST.*"
    results = hosts.all.zos_apf(**ti)
    pprint(vars(results))
    for result in results.contacted.values():
        listFiltered = result.get("stdout")
    assert test_info['dsname'] in listFiltered
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
    test_info['dsname'] = 'APFTEST.FOO.BAR'
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
    cmdStr = "decho \"some text to test persistds format validattion.\" \"{0}\"".format(test_info['persistent']['persistds'])
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
