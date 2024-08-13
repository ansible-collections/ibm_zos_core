# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2020, 2024
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

from ibm_zos_core.tests.helpers.volumes import Volume_Handler

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name


import pytest

SEQ_NAMES = [
    "TEST.FIND.SEQ.FUNCTEST.FIRST",
    "TEST.FIND.SEQ.FUNCTEST.SECOND",
    "TEST.FIND.SEQ.FUNCTEST.THIRD"
]

PDS_NAMES = [
    "TEST.FIND.PDS.FUNCTEST.FIRST",
    "TEST.FIND.PDS.FUNCTEST.SECOND",
    "TEST.FIND.PDS.FUNCTEST.THIRD"
]

VSAM_NAMES = [
    "TEST.FIND.VSAM.FUNCTEST.FIRST"
]

DATASET_TYPES = ['seq', 'pds', 'pdse']
# hlq used across the test suite.
TEST_SUITE_HLQ = "ANSIBLE"


def create_vsam_ksds(ds_name, ansible_zos_module, volume="000000"):
    hosts = ansible_zos_module
    alloc_cmd = f"""     DEFINE CLUSTER (NAME({ds_name})  -
    INDEXED                 -
    RECSZ(80,80)            -
    TRACKS(1,1)             -
    KEYS(5,0)               -
    CISZ(4096)              -
    VOLUMES({volume})         -
    FREESPACE(3,3) )        -
    DATA (NAME({ds_name}.DATA))   -
    INDEX (NAME({ds_name}.INDEX))"""
    return hosts.all.shell(
        cmd="mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin",
        executable='/bin/sh',
        stdin=alloc_cmd,
    )


def test_find_gdg_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        gdg_a = get_tmp_ds_name()
        gdg_b = get_tmp_ds_name()
        gdg_c = get_tmp_ds_name()
        gdg_names = [gdg_a, gdg_b, gdg_c]

        """
        Purge can only be true when scratch is, hence only one gdg for both.
        FIFO is disabled in the ECs and results in failure when trying to
        create a data set.
        one without flags and limit 3
        """
        hosts.all.shell(cmd=f"dtouch -tgdg -L3 {gdg_a}")
        # one with EXTENDED flag -X
        hosts.all.shell(cmd=f"dtouch -tgdg -L1 -X {gdg_b}")
        # one with PURGE flag -P and SCRATCH flag -S
        hosts.all.shell(cmd=f"dtouch -tgdg -L1 -P -S {gdg_c}")

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type="gdg",
            limit=3,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_a, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type="gdg",
            extended=True,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_b, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type="gdg",
            purge=True,
            scratch=True,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_c, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))

    finally:
        # Remove one by one to avoid using an HLQ.* cuz it could cause bugs when running in parallel.
        for ds in gdg_names:
            hosts.all.shell(cmd=f"drm {ds}")


def test_find_sequential_data_sets_containing_single_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'seq',
                    "state":'present'
                } for i in SEQ_NAMES
            ]
        )
        for ds in SEQ_NAMES:
            hosts.all.shell(cmd=f"decho '{search_string}' \"{ds}\" ")

        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*'],
            contains=search_string
        )
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in SEQ_NAMES
            ]
        )


def test_find_sequential_data_sets_multiple_patterns(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "dummy string"
    new_ds = "TEST.FIND.SEQ.FUNCTEST.FOURTH"
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'seq',
                    "state":'present'
                } for i in SEQ_NAMES
            ]
        )
        hosts.all.zos_data_set(name=new_ds, type='seq', state='present')
        hosts.all.shell(cmd=f"decho 'incorrect string' \"{new_ds}\" ")
        for ds in SEQ_NAMES:
            hosts.all.shell(cmd=f"decho '{search_string}' \"{ds}\" ")

        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*', 'TEST.INVALID.*'],
            contains=search_string
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in SEQ_NAMES
            ]
        )
        hosts.all.zos_data_set(
            name=new_ds, state='absent'
        )


def test_find_pds_members_containing_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'pds',
                    "space_primary":1,
                    "space_type":"m",
                } for i in PDS_NAMES
            ]
        )
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i + "(MEMBER)",
                    "type":"member",
                    "state":'present',
                    "replace":'yes',
                } for i in PDS_NAMES
            ]
        )
        for ds in PDS_NAMES:
            result = hosts.all.shell(cmd=f"decho '{search_string}' \"{ds}(MEMBER)\" ")

        find_res = hosts.all.zos_find(
            pds_paths=['TEST.FIND.PDS.FUNCTEST.*'],
            contains=search_string,
            patterns=['.*']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in PDS_NAMES
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in PDS_NAMES
            ]
        )


def test_exclude_data_sets_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'seq',
                    "record_length":80,
                    "state":'present'
                } for i in SEQ_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*'],
            excludes=['.*THIRD$']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in SEQ_NAMES
            ]
        )


def test_exclude_members_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'pds',
                    "state":'present'
                } for i in PDS_NAMES
            ]
        )
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i + "(MEMBER)",
                    "type":"member"
                } for i in PDS_NAMES
            ]
        )
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i + "(FILE)",
                    "type":"member"
                } for i in PDS_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            pds_paths=['TEST.FIND.PDS.FUNCTEST.*'], excludes=['.*FILE$'], patterns=['.*']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in PDS_NAMES
            ]
        )


def test_find_data_sets_older_than_age(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns=['SYS1.PARMLIB', "SYS1.PROCLIB".lower()],
        age='2d'
    )
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 2
        assert val.get('matched') == 2


@pytest.mark.parametrize("ds_type", DATASET_TYPES)
def test_find_data_sets_larger_than_size(ansible_zos_module, ds_type):
    hosts = ansible_zos_module
    TEST_PS1 = 'TEST.PS.ONE'
    TEST_PS2 = 'TEST.PS.TWO'
    try:
        res = hosts.all.zos_data_set(name=TEST_PS1, state="present", space_primary="1", space_type="m", type=ds_type)
        res = hosts.all.zos_data_set(name=TEST_PS2, state="present", space_primary="1", space_type="m", type=ds_type)
        find_res = hosts.all.zos_find(patterns=['TEST.PS.*'], size="1k")
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            assert val.get('matched') == 2
    finally:
        hosts.all.zos_data_set(name=TEST_PS1, state="absent")
        hosts.all.zos_data_set(name=TEST_PS2, state="absent")


def test_find_data_sets_smaller_than_size(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PS = 'USER.FIND.TEST'
    try:
        hosts.all.zos_data_set(name=TEST_PS, state="present", type="seq", space_primary="1", space_type="k")
        find_res = hosts.all.zos_find(patterns=['USER.FIND.*'], size='-1m')
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == 1
    finally:
        hosts.all.zos_data_set(name=TEST_PS, state="absent")


def test_find_data_sets_in_volume(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        data_set_name = "TEST.FIND.SEQ"
        volume = "000000"
        # Create temp data set
        hosts.all.zos_data_set(name=data_set_name, type="seq", state="present", volumes=[volume])
        find_res = hosts.all.zos_find(
            patterns=[data_set_name], volumes=[volume]
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) >= 1
            assert val.get('matched') >= 1
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent")



def test_find_vsam_pattern(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        for vsam in VSAM_NAMES:
            create_vsam_ksds(vsam, hosts)
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.VSAM.FUNCTEST.*'], resource_type='cluster'
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in VSAM_NAMES
            ]
        )


def test_find_vsam_in_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()
    volume_2 = volumes.get_available_vol()
    alternate_vsam = "TEST.FIND.VSAM.SECOND"
    try:
        for vsam in VSAM_NAMES:
            create_vsam_ksds(vsam, hosts, volume=volume_1)
        create_vsam_ksds(alternate_vsam, hosts, volume=volume_2)
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.VSAM.*.*'], volumes=[volume_1], resource_type='cluster'
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in VSAM_NAMES
            ]
        )
        hosts.all.zos_data_set(name=alternate_vsam, state='absent')


def test_find_invalid_age_indicator_fails(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['some.pattern'], age='3s')
    for val in find_res.contacted.values():
        assert val.get('msg') is not None


def test_find_invalid_size_indicator_fails(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['some.pattern'], size='5h')
    for val in find_res.contacted.values():
        assert val.get('msg') is not None


def test_find_non_existent_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['TEST.FIND.NONE.*.*'])
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0


def test_find_non_existent_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(pds_paths=['TEST.NONE.PDS.*'], patterns=['.*'])
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0


def test_find_mixed_members_from_pds_paths(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'pds',
                    "state":'present'
                } for i in PDS_NAMES
            ]
        )
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i + "(MEMBER)",
                    "type":"member"
                } for i in PDS_NAMES
            ]
        )
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i + "(FILE)",
                    "type":"member"
                } for i in PDS_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            pds_paths=['TEST.NONE.PDS.*','TEST.FIND.PDS.FUNCTEST.*'], excludes=['.*FILE$'], patterns=['.*']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in PDS_NAMES
            ]
        )


def test_find_sequential_special_data_sets_containing_single_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:

        special_chars = ["$", "-", "@", "#"]
        special_names = [ "".join([get_tmp_ds_name(mlq_size=7, llq_size=6, symbols=True), special_chars[i]]) for i in range(4)]
        # Creates a command like  dtouch dsname &&  dtouch dsname && dtouch dsname to avoid multiple ssh calls and improve test performance
        dtouch_command = " && ".join([f"dtouch -tseq '{item}'" for item in special_names])
        hosts.all.shell(cmd=dtouch_command)

        # Creates a command like decho dsname && decho dsname && decho dsname to avoid multiple ssh calls and improve test performance
        decho_command = " && ".join([f"decho '{search_string}' '{item}'" for item in special_names])
        hosts.all.shell(cmd=decho_command)

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            contains=search_string
        )
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) != 0
            for ds in special_names:
                assert {"name":ds, "type": "NONVSAM"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        for ds in special_names:
            hosts.all.shell(cmd=f"drm '{ds}'")
