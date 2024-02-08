# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020 - 2024
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
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from shellescape import quote
from pprint import pprint

__metaclass__ = type

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

def clean_test_env(hosts, test_info):
    cmdStr = "drm {0}".format(test_info['library'])
    hosts.all.shell(cmd=cmdStr)
    if test_info.get('persistent'):
        cmdStr = "drm {0}".format(test_info['persistent']['data_set_name'])
        hosts.all.shell(cmd=cmdStr)


def test_add_del(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", state="present", force_dynamic=True)
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)


def test_add_del_with_tmp_hlq_option(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        tmphlq = "TMPHLQ"
        test_info = dict(library="", state="present", force_dynamic=True, tmp_hlq="", persistent=dict(data_set_name="", backup=True))
        test_info['tmp_hlq'] = tmphlq
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("backup_name")[:6] == tmphlq
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)


def test_add_del_volume(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", volume="", state="present", force_dynamic=True)
        ds = get_tmp_ds_name(1,1)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)


"""
This test case was removed 3 years ago in the following PR : https://github.com/ansible-collections/ibm_zos_core/pull/197
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


def test_add_del_volume_persist(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", volume="", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True)
        ds = get_tmp_ds_name(1,1)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        add_exptd = add_expected.format(test_info['library'], test_info['volume'])
        add_exptd = add_exptd.replace(" ", "")
        cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == add_exptd
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        del_exptd = del_expected.replace(" ", "")
        cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == del_exptd
    finally:
        clean_test_env(hosts, test_info)

"""
keyword: ENABLE-FOR-1-3
Test commented because there is a failure in ZOAU 1.2.x, that should be fixed in 1.3.x, so
whoever works in issue https://github.com/ansible-collections/ibm_zos_core/issues/726
should uncomment this test as part of the validation process.
"""
def test_batch_add_del(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(
            batch=[dict(library="", volume=" "), dict(library="", volume=" "), dict(library="", volume=" ")],
            persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True
        )
        for item in test_info['batch']:
            ds = get_tmp_ds_name(1,1)
            hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
            item['library'] = ds
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            item['volume'] = vol
        prstds = get_tmp_ds_name(5,5)
        cmdStr = "dtouch -tseq {0}".format(prstds)
        hosts.all.shell(cmd=cmdStr)
        test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("rc") == 0
        add_exptd = add_batch_expected.format(test_info['batch'][0]['library'], test_info['batch'][0]['volume'],
                                                test_info['batch'][1]['library'], test_info['batch'][1]['volume'],
                                                test_info['batch'][2]['library'], test_info['batch'][2]['volume'])
        add_exptd = add_exptd.replace(" ", "")
        cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == add_exptd
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        pprint(vars(results))
        for result in results.contacted.values():
            assert result.get("rc") == 0
        del_exptd = del_expected.replace(" ", "")
        cmdStr = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == del_exptd
    finally:
        for item in test_info['batch']:
            clean_test_env(hosts, item)
        hosts.all.shell(cmd="drm {0}".format(test_info['persistent']['data_set_name']))


def test_operation_list(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = dict(operation="list")
    results = hosts.all.zos_apf(**test_info)
    for result in results.contacted.values():
        listJson = result.get("stdout")
    import json
    data = json.loads(listJson)
    assert data['data']['format'] in ['DYNAMIC', 'STATIC']
    del json


def test_operation_list_with_filter(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        hosts.all.zos_apf(**test_info)
        ti = dict(operation="list", library="")
        ti['library'] = "ANSIBLE.*"
        results = hosts.all.zos_apf(**ti)
        for result in results.contacted.values():
            listFiltered = result.get("stdout")
        assert test_info['library'] in listFiltered
        test_info['state'] = 'absent'
        hosts.all.zos_apf(**test_info)
    finally:
        clean_test_env(hosts, test_info)

#
# Negative tests
#


def test_add_already_present(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            # Return code 16 if ZOAU < 1.2.0 and RC is 8 if ZOAU >= 1.2.0
            assert result.get("rc") == 16 or result.get("rc") == 8
        test_info['state'] = 'absent'
        hosts.all.zos_apf(**test_info)
    finally:
        clean_test_env(hosts, test_info)


def test_del_not_present(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", state="present", force_dynamic=True)
        ds = get_tmp_ds_name(1,1)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            # Return code 16 if ZOAU < 1.2.0 and RC is 8 if ZOAU >= 1.2.0
            assert result.get("rc") == 16 or result.get("rc") == 8
    finally:
        clean_test_env(hosts, test_info)


def test_add_not_found(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = dict(library="", state="present", force_dynamic=True)
    test_info['library'] = 'APFTEST.FOO.BAR'
    results = hosts.all.zos_apf(**test_info)
    for result in results.contacted.values():
        # Return code 16 if ZOAU < 1.2.0 and RC is 8 if ZOAU >= 1.2.0
        assert result.get("rc") == 16 or result.get("rc") == 8


def test_add_with_wrong_volume(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", volume="", state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        test_info['volume'] = 'T12345'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            # Return code 16 if ZOAU < 1.2.0 and RC is 8 if ZOAU >= 1.2.0
            assert result.get("rc") == 16 or result.get("rc") == 8
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_ds_format(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        cmdStr = "decho \"some text to test persistent data_set format validattion.\" \"{0}\"".format(test_info['persistent']['data_set_name'])
        hosts.all.shell(cmd=cmdStr)
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 8
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_marker(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        test_info['persistent']['marker'] = "# Invalid marker format"
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 4
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_marker_len(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        VolumeHandler = Volume_Handler(volumes_on_systems)
        volume = VolumeHandler.get_volume_with_vvds(hosts, volumes_on_systems)
        test_info = dict(library="", persistent=dict(data_set_name="", marker="/* {mark} BLOCK */"), state="present", force_dynamic=True)
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} {ds} ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmdStr = "dls -l " + ds + " | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmdStr = "mvstmp APFTEST.PRST"
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmdStr = "dtouch -tseq {0}".format(prstds)
            hosts.all.shell(cmd=cmdStr)
            test_info['persistent']['data_set_name'] = prstds
        test_info['persistent']['marker'] = "/* {mark} This is a awfully lo%70sng marker */" % ("o")
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("msg") == 'marker length may not exceed 72 characters'
    finally:
        clean_test_env(hosts, test_info)