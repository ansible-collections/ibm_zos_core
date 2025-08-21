# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2025
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
from ibm_zos_core.tests.helpers.version import get_zoau_version

__metaclass__ = type

ADD_EXPECTED = """/*BEGINAPFLIST*/
/*BEGINBLOCK*/
APFADDDSNAME({0})VOLUME({1})
/*ENDBLOCK*/
/*ENDAPFLIST*/"""

# ADD_SMS_EXPECTED = """/*BEGINAPFLIST*/
# /*BEGINBLOCK*/
# APFADDDSNAME({0})SMS
# /*ENDBLOCK*/
# /*ENDAPFLIST*/"""

ADD_BATCH_EXPECTED = """/*BEGINAPFLIST*/
/*BEGINBLOCK*/
APFADDDSNAME({0})VOLUME({1})
APFADDDSNAME({2})VOLUME({3})
APFADDDSNAME({4})VOLUME({5})
/*ENDBLOCK*/
/*ENDAPFLIST*/"""

DEL_EXPECTED = """/*BEGINAPFLIST*/
/*ENDAPFLIST*/"""

TEST_HLQ = "ANSIBLE"


def clean_test_env(hosts, test_info):
    cmd_str = f"drm '{test_info['library']}' "
    hosts.all.shell(cmd=cmd_str)
    if test_info.get('persistent'):
        cmd_str = f"drm '{test_info['persistent']['target']}' "
        hosts.all.shell(cmd=cmd_str)


def test_add_del(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "state":"present",
            "force_dynamic":True
        }
        ds = get_tmp_ds_name(3,2)
        hosts.all.shell(f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)


def test_add_del_with_tmp_hlq_option(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        tmphlq = "TMPHLQ"
        test_info = {
            "library":"",
            "state":"present",
            "force_dynamic":True,
            "tmp_hlq":"",
            "persistent":{
                "target":"",
                "backup":True
            }
        }
        test_info['tmp_hlq'] = tmphlq
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("backup_name")[:6] == tmphlq
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)


def test_add_del_volume(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "volume":"",
            "state":"present",
            "force_dynamic":True
        }
        ds = get_tmp_ds_name(1,1,True)

        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)

        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
    finally:
        clean_test_env(hosts, test_info)



#This test case was removed 3 years ago in the following PR :
#https://github.com/ansible-collections/ibm_zos_core/pull/197
#def test_add_del_persist(ansible_zos_module):
#    hosts = ansible_zos_module
#    test_info = TEST_INFO['test_add_del_persist']
#    set_test_env(hosts, test_info)
#    results = hosts.all.zos_apf(**test_info)
#    pprint(vars(results))
#    for result in results.contacted.values():
#        assert result.get("rc") == 0
#    add_exptd = ADD_SMS_EXPECTED.format(test_info['library'])
#    add_exptd = add_exptd.replace(" ", "")
#    cmd_str = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
#    actual = run_shell_cmd(hosts, cmd_str).replace(" ", "")
#    assert actual == add_exptd
#    test_info['state'] = 'absent'
#    results = hosts.all.zos_apf(**test_info)
#    pprint(vars(results))
#    for result in results.contacted.values():
#        assert result.get("rc") == 0
#    del_exptd = DEL_EXPECTED.replace(" ", "")
#    cmd_str = "cat \"//'{0}'\" ".format(test_info['persistent']['data_set_name'])
#    actual = run_shell_cmd(hosts, cmd_str).replace(" ", "")
#    assert actual == del_exptd
#    clean_test_env(hosts, test_info)



def test_add_del_volume_persist(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "volume":"",
            "persistent":{
                "target":"",
                "marker":"/* {mark} BLOCK */"},
            "state":"present",
            "force_dynamic":True
        }
        ds = get_tmp_ds_name(1,1,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
        add_exptd = ADD_EXPECTED.format(test_info['library'], test_info['volume'])
        add_exptd = add_exptd.replace(" ", "")
        cmd_str = f"cat \"//'{test_info['persistent']['target']}'\" "
        results = hosts.all.shell(cmd=cmd_str)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == add_exptd
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        del_exptd = DEL_EXPECTED.replace(" ", "")
        cmd_str = f"cat \"//'{test_info['persistent']['target']}'\" "
        results = hosts.all.shell(cmd=cmd_str)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == del_exptd
    finally:
        clean_test_env(hosts, test_info)


def test_batch_add_del(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "batch":[
                {
                    "library":"",
                    "volume":" "
                },
                {
                    "library":"",
                    "volume":" "
                },
                {
                    "library":"",
                    "volume":" "
                }
            ],
            "persistent":{
                "target":"",
                "marker":"/* {mark} BLOCK */"
            },
            "state":"present",
            "force_dynamic":True
        }
        for item in test_info['batch']:
            ds = get_tmp_ds_name(1,1,True)
            hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
            item['library'] = ds
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            item['volume'] = vol
        prstds = get_tmp_ds_name(5,5,True)
        cmd_str = f"dtouch -tseq '{prstds}' "
        hosts.all.shell(cmd=cmd_str)

        test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        add_exptd = ADD_BATCH_EXPECTED.format(
            test_info['batch'][0]['library'],
            test_info['batch'][0]['volume'],
            test_info['batch'][1]['library'],
            test_info['batch'][1]['volume'],
            test_info['batch'][2]['library'],
            test_info['batch'][2]['volume']
        )
        add_exptd = add_exptd.replace(" ", "")
        cmd_str = f"""dcat '{test_info["persistent"]["target"]}' """
        results = hosts.all.shell(cmd=cmd_str)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == add_exptd
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        del_exptd = DEL_EXPECTED.replace(" ", "")
        cmd_str = f"""dcat '{test_info["persistent"]["target"]}' """
        results = hosts.all.shell(cmd=cmd_str)
        for result in results.contacted.values():
            actual = result.get("stdout")
        actual = actual.replace(" ", "")
        assert actual == del_exptd
    finally:
        for item in test_info['batch']:
            clean_test_env(hosts, item)
        hosts.all.shell(cmd=f"drm '{test_info['persistent']['target']}' ")


def test_operation_list(ansible_zos_module):
    import json
    hosts = ansible_zos_module
    test_info = {
        "operation":"list"
    }
    results = hosts.all.zos_apf(**test_info)
    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("stdout") is not None
        assert result.get("stderr") == ''
        assert result.get("stdout_lines") is not None
        assert result.get("stderr_lines") == ['']
        list_json = result.get("stdout")
    data = json.loads(list_json)
    assert data['format'] in ['DYNAMIC', 'STATIC']
    del json


def test_operation_list_with_filter(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        hosts.all.zos_apf(**test_info)
        ti = {
            "operation":"list",
            "library":""
        }
        ti['library'] = "ANSIBLE.*"
        results = hosts.all.zos_apf(**ti)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
            list_filtered = result.get("stdout")
        assert test_info['library'] in list_filtered
        test_info['state'] = 'absent'
        hosts.all.zos_apf(**test_info)
    finally:
        clean_test_env(hosts, test_info)

#
# Negative tests
#

def test_add_already_present(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") == ''
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") == ['']
        # Second call to zos_apf, same as first but with different expectations
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
        test_info['state'] = 'absent'
        hosts.all.zos_apf(**test_info)
    finally:
        clean_test_env(hosts, test_info)


def test_del_not_present(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "state":"present",
            "force_dynamic":True
        }
        ds = get_tmp_ds_name(1,1,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        test_info['state'] = 'absent'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
    finally:
        clean_test_env(hosts, test_info)


def test_add_not_found(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = {
        "library":"",
        "state":"present",
        "force_dynamic":True
    }
    test_info['library'] = f'{TEST_HLQ}.FOO.BAR'
    results = hosts.all.zos_apf(**test_info)
    for result in results.contacted.values():
        print(result)
        assert result.get("stdout") is not None
        assert result.get("stderr") is not None
        assert result.get("stdout_lines") is not None
        assert result.get("stderr_lines") is not None
        assert result.get("rc") == 16 or result.get("rc") == 8


def test_add_with_wrong_volume(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "volume":"",
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        test_info['volume'] = 'T12345'
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
            assert result.get("rc") == 16 or result.get("rc") == 8
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_ds_format(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "persistent":{
                "target":"",
                "marker":"/* {mark} BLOCK */"
            },
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        ds_name = test_info['persistent']['target']
        cmd_str =f"decho \"some text to test persistent data_set format validation.\" \"{ds_name}\""
        hosts.all.shell(cmd=cmd_str)
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 8
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_marker(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "persistent":{
                "target":"",
                "marker":"/* {mark} BLOCK */"
            },
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        test_info['persistent']['marker'] = "# Invalid marker format"
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            assert result.get("rc") == 4
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
    finally:
        clean_test_env(hosts, test_info)


def test_persist_invalid_marker_len(ansible_zos_module, volumes_with_vvds):
    try:
        hosts = ansible_zos_module
        volume_handler = Volume_Handler(volumes_with_vvds)
        volume = volume_handler.get_available_vol()
        test_info = {
            "library":"",
            "persistent":{
                "target":"",
                "marker":"/* {mark} BLOCK */"
            },
            "state":"present",
            "force_dynamic":True
        }
        test_info['state'] = 'present'
        ds = get_tmp_ds_name(3,2,True)
        hosts.all.shell(cmd=f"dtouch -tseq -V{volume} '{ds}' ")
        test_info['library'] = ds
        if test_info.get('volume') is not None:
            cmd_str = "dls -l '" + ds + "' | awk '{print $5}' "
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                vol = result.get("stdout")
            test_info['volume'] = vol
        if test_info.get('persistent'):
            cmd_str = f"mvstmp {TEST_HLQ}.PRST"
            results = hosts.all.shell(cmd=cmd_str)
            for result in results.contacted.values():
                prstds = result.get("stdout")
            prstds = prstds[:30]
            cmd_str = f"dtouch -tseq '{prstds}' "
            hosts.all.shell(cmd=cmd_str)
            test_info['persistent']['target'] = prstds
        test_info['persistent']['marker'] = "/* {mark} This is a awfully lo%70sng marker */" % ("o")
        results = hosts.all.zos_apf(**test_info)
        for result in results.contacted.values():
            print(result)
            assert result.get("stdout") is not None
            assert result.get("stderr") is not None
            assert result.get("stdout_lines") is not None
            assert result.get("stderr_lines") is not None
            assert result.get("msg") == 'marker length may not exceed 72 characters'
    finally:
        clean_test_env(hosts, test_info)
