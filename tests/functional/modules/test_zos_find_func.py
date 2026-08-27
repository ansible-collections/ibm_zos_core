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

__metaclass__ = type

from ibm_zos_core.tests.helpers.volumes import Volume_Handler

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

import re
import pytest

# hlq used across the test suite.
TEST_SUITE_HLQ = "ANSIBLE"

SEQ_NAMES = [
    f"{TEST_SUITE_HLQ}.FIND.SEQ.FUNCTEST.FIRST",
    f"{TEST_SUITE_HLQ}.FIND.SEQ.FUNCTEST.SECOND",
    f"{TEST_SUITE_HLQ}.FIND.SEQ.FUNCTEST.THIRD"
]

PDS_NAMES = [
    f"{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.FIRST",
    f"{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.SECOND",
    f"{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.THIRD"
]

VSAM_NAMES = [
    f"{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.FIRST"
]

MIGRATED_DATASETS_PATTERNS = ['IMSBLD.I15STSMM.*','IMSBLD.DCC71QPP.*']

DATASET_TYPES = ['seq', 'pds', 'pdse']

LOCK_VSAM_JCL = """//SLEEP    JOB (T043JM,JM00,1,0,0,0),'SLEEP - JRM',CLASS=R,
//             MSGCLASS=X,MSGLEVEL=1,NOTIFY=S0JM
//STEP1     EXEC PGM=BPXBATCH,PARM='SH sleep 60'
//VSAM1   DD DISP=OLD,DSN={0}
//STDOUT    DD SYSOUT=*
//STDERR    DD SYSOUT=*
"""

def create_vsam_ksds(ds_name, ansible_zos_module, volume):
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
            resource_type=["gdg"],
            limit=3,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_a, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type=["gdg"],
            extended=True,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_b, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type=["gdg"],
            purge=True,
            scratch=True,
        )

        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) == 1
            assert {"name":gdg_c, "type": "GDG"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None

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
            patterns=[f'{TEST_SUITE_HLQ}.FIND.SEQ.*.*'],
            contains=search_string
        )
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
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
    new_ds = f"{TEST_SUITE_HLQ}.FIND.SEQ.FUNCTEST.FOURTH"
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
            patterns=[f'{TEST_SUITE_HLQ}.FIND.SEQ.*.*', f'{TEST_SUITE_HLQ}.INVALID.*'],
            contains=search_string
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
            contains=search_string,
            patterns=[f'{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.*']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in PDS_NAMES
                assert len(ds.get('members')) == 1
            assert val.get('matched') is not None
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
            patterns=[f'{TEST_SUITE_HLQ}.FIND.SEQ.*.*'],
            excludes=['.*THIRD$']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') is not None
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
            excludes=['(.*FILE$)'],
            patterns=[f'{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.*']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert len(ds.get('members')) == 1
            assert val.get('matched') is not None
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
        assert val.get('examined') is not None
        assert val.get('msg') is None


@pytest.mark.parametrize("ds_type", DATASET_TYPES)
def test_find_data_sets_larger_than_size(ansible_zos_module, ds_type):
    hosts = ansible_zos_module
    TEST_PS1 = f'{TEST_SUITE_HLQ}.PS.ONE'
    TEST_PS2 = f'{TEST_SUITE_HLQ}.PS.TWO'
    try:
        res = hosts.all.zos_data_set(name=TEST_PS1, state="present", space_primary="1", space_type="m", type=ds_type)
        res = hosts.all.zos_data_set(name=TEST_PS2, state="present", space_primary="1", space_type="m", type=ds_type)
        find_res = hosts.all.zos_find(patterns=[f'{TEST_SUITE_HLQ}.PS.*'], size="1k")
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            assert val.get('matched') == 2
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.zos_data_set(name=TEST_PS1, state="absent")
        hosts.all.zos_data_set(name=TEST_PS2, state="absent")


def test_find_data_sets_smaller_than_size(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_PS = f'{TEST_SUITE_HLQ}.FIND.TEST'
    try:
        hosts.all.zos_data_set(name=TEST_PS, state="present", type="seq", space_primary="1", space_type="k")
        find_res = hosts.all.zos_find(patterns=[f'{TEST_SUITE_HLQ}.FIND.*'], size='-1m')
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == 1
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.zos_data_set(name=TEST_PS, state="absent")


def test_find_data_sets_in_volume(ansible_zos_module, volumes_on_systems):
    try:
        hosts = ansible_zos_module
        data_set_name = f"{TEST_SUITE_HLQ}.FIND.SEQ"
        volumes = Volume_Handler(volumes_on_systems)
        volume = volumes.get_available_vol()
        # Create temp data set
        hosts.all.zos_data_set(name=data_set_name, type="seq", state="present", volumes=[volume])
        find_res = hosts.all.zos_find(
            patterns=[data_set_name], volumes=[volume]
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) >= 1
            assert val.get('matched') >= 1
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.zos_data_set(name=data_set_name, state="absent")


def test_find_vsam_pattern(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    try:
        volumes = Volume_Handler(volumes_on_systems)

        for vsam in VSAM_NAMES:
            volume = volumes.get_available_vol()
            create_vsam_ksds(vsam, hosts, volume)

        # A KSDS VSAM has 3 different components, cluster, data and index
        # This test should find all three
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['cluster']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('data_sets')[0].get("name", None) == VSAM_NAMES[0]
            assert val.get('examined') is not None
            assert val.get('msg') is None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['data']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('data_sets')[0].get("name", None) == f"{VSAM_NAMES[0]}.DATA"
            assert val.get('examined') is not None
            assert val.get('msg') is None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['data', 'cluster']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
            assert val.get('msg') is None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['index']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('data_sets')[0].get("name", None) == f"{VSAM_NAMES[0]}.INDEX"
            assert val.get('examined') is not None
            assert val.get('msg') is None

        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['cluster', 'data', 'index']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') == 1
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in VSAM_NAMES
            ]
        )


def test_find_vsam_pattern_disp_old(ansible_zos_module, volumes_on_systems):
    """
    Creates a VSAM cluster and runs a JCL to lock the data set with DISP=OLD.
    Then make sure that we can query the VSAM. Currently, if using age + cluster
    resource_type the module will not find the vsam.
    """
    hosts = ansible_zos_module
    try:
        volumes = Volume_Handler(volumes_on_systems)
        jcl_ds = get_tmp_ds_name()
        for vsam in VSAM_NAMES:
            volume = volumes.get_available_vol()
            create_vsam_ksds(vsam, hosts, volume)

        hosts.all.shell(cmd=f"decho \"{LOCK_VSAM_JCL.format(VSAM_NAMES[0])}\" '{jcl_ds}'; jsub '{jcl_ds}'")
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.FUNCTEST.*'],
            resource_type=['cluster']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.shell(cmd=f"drm '{jcl_ds}'")
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
    alternate_vsam = f"{TEST_SUITE_HLQ}.FIND.VSAM.SECOND"
    try:
        for vsam in VSAM_NAMES:
            create_vsam_ksds(vsam, hosts, volume_1)
        create_vsam_ksds(alternate_vsam, hosts, volume_2)
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.FIND.VSAM.*.*'],
            volumes=[volume_1],
            resource_type=['cluster']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
        assert val.get('changed') is False


def test_find_invalid_size_indicator_fails(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['some.pattern'], size='5h')
    for val in find_res.contacted.values():
        assert val.get('msg') is not None
        assert val.get('changed') is False


def test_find_non_existent_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=[f'{TEST_SUITE_HLQ}.FIND.NONE.*.*'])
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0
        assert val.get('examined') is not None
        assert val.get('msg') is None


def test_find_non_existent_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns=[f'{TEST_SUITE_HLQ}.NONE.PDS.*'],
    )
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0
        assert val.get('examined') is not None
        assert val.get('msg') is None


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
            excludes=['(.*FILE$)'],
            patterns=[f'{TEST_SUITE_HLQ}.NONE.PDS.*',f'{TEST_SUITE_HLQ}.FIND.PDS.FUNCTEST.*'],
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert len(ds.get('members')) == 1
            assert val.get('examined') is not None
            assert val.get('msg') is None
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
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        for ds in special_names:
            hosts.all.shell(cmd=f"drm '{ds}'")


def test_find_vsam_and_gdg_data_sets(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    try:
        # Create GDG
        gdg_a = get_tmp_ds_name()
        hosts.all.shell(cmd=f"dtouch -tgdg -L3 {gdg_a}")
        # Create VSAM Dataset
        volumes = Volume_Handler(volumes_on_systems)
        for vsam in VSAM_NAMES:
            volume = volumes.get_available_vol()
            create_vsam_ksds(vsam, hosts, volume)
        # This test should cluster and gdg datasets
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*'],
            resource_type=['cluster', 'gdg']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) >= 2
            assert val.get('matched') == len(val.get('data_sets'))
            assert {"name":VSAM_NAMES[0], "type": "CLUSTER"} in val.get('data_sets')
            assert {"name":gdg_a, "type": "GDG"} in val.get('data_sets')
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in VSAM_NAMES
            ]
        )
        hosts.all.shell(cmd=f"drm {gdg_a}")


def test_find_gdg_and_nonvsam_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        gdg_b = get_tmp_ds_name()
        # one with EXTENDED flag -X
        hosts.all.shell(cmd=f"dtouch -tgdg -L1 -X {gdg_b}")
        # Create 3 sequential datasets
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'seq',
                    "state":'present'
                } for i in SEQ_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type=["gdg", "nonvsam"],
        )
        data_sets = [{"name":data_set_name, "type": "NONVSAM"} for data_set_name in SEQ_NAMES]
        data_sets.append({"name":gdg_b, "type": "GDG"})
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) >= 4
            for data_set in data_sets:
                assert data_set in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
    finally:
        # Remove GDG.
        hosts.all.shell(cmd=f"drm {gdg_b}")
        # Remove SEQ Datasets
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in SEQ_NAMES
            ]
        )


def test_find_vsam_and_nonvsam_data_sets(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    try:
        # Create VSAM Dataset
        volumes = Volume_Handler(volumes_on_systems)
        for vsam in VSAM_NAMES:
            volume = volumes.get_available_vol()
            create_vsam_ksds(vsam, hosts, volume)
        # Create 3 sequential datasets
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "type":'seq',
                    "state":'present'
                } for i in SEQ_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            patterns=[f'{TEST_SUITE_HLQ}.*.*'],
            resource_type=["data", "nonvsam"],
        )
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) >= 4
            assert {"name":f'{VSAM_NAMES[0]}.DATA', "type": "DATA"} in val.get('data_sets')
            assert val.get('matched') == len(val.get('data_sets'))
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        # Remove VSAM.
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in VSAM_NAMES
            ]
        )
        # Remove SEQ Datasets
        hosts.all.zos_data_set(
            batch=[
                {
                    "name":i,
                    "state":'absent'
                } for i in SEQ_NAMES
            ]
        )


def test_find_migrated_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns = MIGRATED_DATASETS_PATTERNS,
        resource_type = ['migrated']
    )
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) != 0
        for ds in val.get('data_sets'):
            assert ds.get("type") == "MIGRATED"
        assert val.get('examined') is not None
        assert val.get('msg') is None


def test_find_migrated_data_sets_with_excludes(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns = MIGRATED_DATASETS_PATTERNS,
        resource_type = ['migrated'],
        excludes = '.*F4'
    )
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) != 0
        for ds in val.get('data_sets'):
            assert not re.fullmatch(r".*F4", ds.get("name"))
        assert val.get('examined') is not None
        assert val.get('msg') is None


def test_find_migrated_data_sets_with_migrated_type(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns = MIGRATED_DATASETS_PATTERNS,
        resource_type = ['migrated'],
        migrated_type = ['nonvsam']
    )
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) != 0
        for ds in val.get('data_sets'):
            assert ds.get("type") == "MIGRATED"
            assert ds.get("migrated_resource_type") == "NONVSAM"
        assert val.get('examined') is not None
        assert val.get('msg') is None


def test_find_migrated_and_gdg_data_sets(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        gdg_a = get_tmp_ds_name()
        # Create GDG with limit 3
        hosts.all.shell(cmd=f"dtouch -tgdg -L3 {gdg_a}")
        MIGRATED_DATASETS_PATTERNS.append(gdg_a)
        find_res = hosts.all.zos_find(
            patterns = MIGRATED_DATASETS_PATTERNS,
            resource_type = ['migrated', 'gdg'],
            migrated_type = ['nonvsam']
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            assert {"name":gdg_a, "type": "GDG"} in val.get('data_sets')
            for ds in val.get('data_sets'):
                assert ds.get("type") in ["MIGRATED", "GDG"]
            assert val.get('examined') is not None
            assert val.get('msg') is None
    finally:
        # Remove GDG.
        hosts.all.shell(cmd=f"drm {gdg_a}")


# ---------------------------------------------------------------------------
# Alias test suite (Enhancement #2446)
# ---------------------------------------------------------------------------
_IDCAMS_CMD = "mvscmdauth --pgm=IDCAMS --sysprint=* --sysin=stdin"

def test_find_two_gdg_bases(ansible_zos_module):
    """Create two GDG bases with limit=5 and verify both are returned by zos_find
    with resource_type=gdg and matched==2."""
    hosts = ansible_zos_module
    gdg_a = get_tmp_ds_name()
    gdg_b = get_tmp_ds_name()
    try:
        hosts.all.shell(
            cmd=_IDCAMS_CMD,
            executable='/bin/sh',
            stdin=f"""
  DEFINE GDG (NAME({gdg_a}) LIMIT(5) NOEMPTY SCRATCH)
  DEFINE GDG (NAME({gdg_b}) LIMIT(5) NOEMPTY SCRATCH)
""",
        )
        find_res = hosts.all.zos_find(
            patterns=[gdg_a, gdg_b],
            resource_type=["gdg"],
            limit=5,
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None
            assert val.get("matched") == 2
            returned_names = {ds["name"] for ds in data_sets}
            assert gdg_a in returned_names
            assert gdg_b in returned_names
            for ds in data_sets:
                assert ds.get("type") == "GDG"
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {gdg_a} GDG\n  DELETE {gdg_b} GDG\n",
        ) 


def test_find_alias_for_ps(ansible_zos_module):
    """Alias for a Sequential (PS) dataset.
    Creates a PS dataset and one catalog ALIAS entry pointing to it.
    Verifies:
    - Returned entry has type=ALIAS, correct name, and alias_of == PS dataset name.
    - No member_aliases key (PS datasets have no members).
    - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    ps_name   = f"{hlq}.SEQ"
    ali_name  = f"{hlq}.SEQ.ALI"
    # Pattern must end with .* at the qualifier level of the alias name.
    # get_tmp_ds_name() returns 4 qualifiers; alias is 6 qualifiers deep,
    # so {hlq}.SEQ.* (5 qualifiers + *) targets the alias level exactly.
    ali_pattern = f"{hlq}.SEQ.*"
    try:
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 {ps_name}")
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({ps_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
        )
        print(find_res.contacted.values())
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == ps_name
            assert "members" not in ds
            assert val.get("matched") == 1
            assert val.get("examined") is not None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.shell(cmd=f"drm {ps_name}")


def test_find_alias_for_pds(ansible_zos_module):
    """Alias for a PDS dataset — without include_member_aliases.
    Creates a PDS with members MBR1 and MBR2, then creates a catalog ALIAS.
    Verifies:
    - Returned entry has type=ALIAS, correct name, and alias_of == PDS name.
    - No 'members' key in result (include_member_aliases defaults to False).
    - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pds_name  = f"{hlq}.PDS"
    ali_name  = f"{hlq}.PDS.ALI"
    ali_pattern = f"{hlq}.PDS.*"
    try:
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
        ])
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == pds_name
            assert "members" not in ds
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_find_alias_for_pds_include_member_aliases(ansible_zos_module):
    """Alias for a PDS dataset — with include_member_aliases=True.
    Creates a PDS with members MBR1 and MBR2, creates a member alias MALIAS1
    pointing to MBR1, then creates a catalog ALIAS pointing to the PDS.
    Verifies:
    - Returned entry has type=ALIAS, correct name, and alias_of == PDS name.
    - 'members' key is present; all members are listed (MBR1 and MBR2).
    - MBR1 has MALIAS1 in its aliases list.
    - MBR2 has no member aliases (empty aliases list).
    - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pds_name  = f"{hlq}.PDS"
    ali_name  = f"{hlq}.PDS.ALI"
    ali_pattern = f"{hlq}.PDS.*"
    try:
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
        ])
        # Create member alias MALIAS1 → MBR1 inside the PDS directory
        hosts.all.shell(
            cmd=f"tso \"RENAME '{pds_name}(MBR1)' (MALIAS1) ALIAS\""
        )
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            include_member_aliases=True,
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == pds_name
            assert "members" in ds
            member_names = [m["name"] for m in ds["members"]]
            assert "MBR1" in member_names
            assert "MBR2" in member_names
            for m in ds["members"]:
                assert "name" in m
                assert "aliases" in m
                assert isinstance(m["aliases"], list)
                if m["name"] == "MBR1":
                    assert "MALIAS1" in m["aliases"], (
                        f"Expected MALIAS1 in MBR1 aliases but got {m['aliases']}"
                    )
                elif m["name"] == "MBR2":
                    assert m["aliases"] == [], (
                        f"Expected no member aliases for MBR2 but got {m['aliases']}"
                    )
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_find_alias_for_pdse_include_member_alias(ansible_zos_module):
    """Alias for a PDSE dataset that contains a member alias — with include_member_aliases=True.
    Creates a PDSE with members MEM1 and MEM2, creates member alias ALIAS1 → MEM1,
    then creates a catalog ALIAS for the PDSE itself.
    Verifies:
    - type=ALIAS, correct name, alias_of == PDSE name.
    - 'members' key is present; all members are listed (MEM1 and MEM2).
    - MEM1 has ALIAS1 in its aliases list.
    - MEM2 has no member aliases (empty aliases list).
    - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pdse_name = f"{hlq}.PDSE"
    ali_name  = f"{hlq}.PDSE.ALI"
    ali_pattern = f"{hlq}.PDSE.*"
    try:
        hosts.all.zos_data_set(name=pdse_name, type="pdse", state="present",
                               space_primary=5, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pdse_name}(MEM1)", "type": "member", "state": "present"},
            {"name": f"{pdse_name}(MEM2)", "type": "member", "state": "present"},
        ])
        rename_res = hosts.all.shell(cmd=f"tso \"RENAME '{pdse_name}(MEM1)' (ALIAS1) ALIAS\"")
        for v in rename_res.contacted.values():
            assert v.get("rc") == 0, f"RENAME alias failed: {v.get('stdout')} {v.get('stderr')}"
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pdse_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            include_member_aliases=True,
        )
        print(find_res.contacted.values())
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == pdse_name
            # All members must appear; MEM1 has ALIAS1, MEM2 has none.
            assert "members" in ds, "PDSE alias must carry 'members' when include_member_aliases=True"
            member_names = [m["name"] for m in ds["members"]]
            assert "MEM1" in member_names, "MEM1 must appear in members"
            assert "MEM2" in member_names, "MEM2 must appear in members"
            mem1 = next(m for m in ds["members"] if m["name"] == "MEM1")
            assert "ALIAS1" in mem1["aliases"], "ALIAS1 must be listed under MEM1"
            mem2 = next(m for m in ds["members"] if m["name"] == "MEM2")
            assert mem2["aliases"] == [], "MEM2 has no aliases; list must be empty"
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pdse_name, state="absent")


def test_find_alias_for_gdg_generation(ansible_zos_module):
    """Alias for a GDG generation dataset (G0001V00).
    GDG *base* entries cannot be aliased — only physical generations can.
    Creates a GDG base, allocates the first generation, then creates a catalog
    ALIAS pointing to that generation.
    Verifies:
    - type=ALIAS, correct name, alias_of == resolved generation name (G0001V00).
    - No member_aliases key (sequential dataset).
    - matched == 1.
    """
    hosts = ansible_zos_module
    # mlq_size=3, llq_size=3 keeps the HLQ at 26 chars so that appending
    # .GDG.G0001V00 (13 chars) stays within the 44-char z/OS name limit.
    hlq      = get_tmp_ds_name(mlq_size=3, llq_size=3)
    gdg_base = f"{hlq}.GDG"
    gdg_gen  = f"{hlq}.GDG.G0001V00"
    ali_name = f"{hlq}.GDG.ALI"
    ali_pattern = f"{hlq}.GDG.*"
    try:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE GDG -\n"
                f"    (NAME({gdg_base}) -\n"
                f"     LIMIT(5) NOEMPTY SCRATCH)\n"
            ),
        )
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 '{gdg_base}(+1)'")
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({gdg_gen}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == gdg_gen
            assert "members" not in ds
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {gdg_base} -\n    GDG\n",
        )


def test_find_alias_excludes_pds_and_pdse(ansible_zos_module):
    """Aliases for PS, PDS, and PDSE created under one HLQ.
    PDS and PDSE catalog aliases are excluded by pattern; only the PS alias is returned.
    Setup:
      - PS  dataset with catalog alias  <hlq>.SEQ.ALI
      - PDS dataset with two members:
            MBR1  → member alias MEMALI1
            MBR2  (no member alias)
        catalog alias <hlq>.PDS.ALI
      - PDSE dataset with two members:
            MEM1  → member alias ALIAS1
            MEM2  → member alias ALIAS2
        catalog alias <hlq>.PDSE.ALI
    zos_find is called with:
      patterns:  [<hlq>.*]   -- matches all three catalog aliases
      excludes:  ['.*\\.PDS\\.ALI', '.*\\.PDSE\\.ALI']
                 -- fullmatch regexes against the alias dataset name
    Expected: only <hlq>.SEQ.ALI returned; matched == 1.
    PDS and PDSE aliases are excluded; 'members' is not present on the PS result
    (include_member_aliases defaults to False).
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    ps_name   = f"{hlq}.SEQ"
    pds_name  = f"{hlq}.PDS"
    pdse_name = f"{hlq}.PDSE"
    ps_ali    = f"{hlq}.SEQ.ALI"
    pds_ali   = f"{hlq}.PDS.ALI"
    pdse_ali  = f"{hlq}.PDSE.ALI"
    # Single pattern covers all three alias names (hlq = 4 qualifiers,
    # alias names are 6 qualifiers: hlq + .TYPE.ALI → hlq.* covers them).
    ali_pattern = f"{hlq}.*"
    # Exclude the PDS and PDSE catalog alias names using fullmatch regex.
    # _match_regex uses re.fullmatch so the pattern must span the entire name.
    excludes = [r".*\.PDS\.ALI", r".*\.PDSE\.ALI"]
    try:
        # --- Create PS ---
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 {ps_name}")
        # --- Create PDS with MBR1 (has member alias MEMALI1) and MBR2 (no alias) ---
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
        ])
        hosts.all.shell(cmd=f"tso \"RENAME '{pds_name}(MBR1)' (MEMALI1) ALIAS\"")
        # --- Create PDSE with MEM1 → ALIAS1 and MEM2 → ALIAS2 ---
        hosts.all.zos_data_set(name=pdse_name, type="pdse", state="present",
                               space_primary=5, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pdse_name}(MEM1)", "type": "member", "state": "present"},
            {"name": f"{pdse_name}(MEM2)", "type": "member", "state": "present"},
        ])
        hosts.all.shell(cmd=f"tso \"RENAME '{pdse_name}(MEM1)' (ALIAS1) ALIAS\"")
        hosts.all.shell(cmd=f"tso \"RENAME '{pdse_name}(MEM2)' (ALIAS2) ALIAS\"")
        # --- Define catalog aliases for all three datasets ---
        for define_stdin, label in [
            (
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ps_ali}) -\n"
                f"     RELATE({ps_name}))\n",
                "PS"
            ),
            (
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n",
                "PDS"
            ),
            (
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pdse_ali}) -\n"
                f"     RELATE({pdse_name}))\n",
                "PDSE"
            ),
        ]:
            res = hosts.all.shell(cmd=_IDCAMS_CMD, executable='/bin/sh', stdin=define_stdin)
            for v in res.contacted.values():
                assert v.get("rc") == 0, (
                    f"DEFINE ALIAS for {label} failed: {v.get('stdout')} {v.get('stderr')}"
                )
        # --- Find with excludes ---
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            excludes=excludes,
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected 1 alias (PS only), got {data_sets}"
            )
            ds = data_sets[0]
            # Only the PS alias must survive the excludes filter
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ps_ali
            assert ds["alias_of"] == ps_name
            # include_member_aliases defaults to False — 'members' must not be present
            assert "members" not in ds
            assert val.get("matched") == 1
            # Confirm neither PDS nor PDSE alias is in the result
            names = [d["name"] for d in data_sets]
            assert pds_ali  not in names, "PDS alias should have been excluded"
            assert pdse_ali not in names, "PDSE alias should have been excluded"
    finally:
        for ali in (ps_ali, pds_ali, pdse_ali):
            hosts.all.shell(
                cmd=_IDCAMS_CMD, executable='/bin/sh',
                stdin=f"  DELETE {ali} -\n    ALIAS\n",
            )
        hosts.all.shell(cmd=f"drm {ps_name}")
        hosts.all.zos_data_set(name=pds_name,  state="absent")
        hosts.all.zos_data_set(name=pdse_name, state="absent")


def test_find_alias_data_sets_no_match(ansible_zos_module):
    """A pattern that matches no aliases must return an empty data_sets list."""
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns=["ANSIBLE.ALIAS.NONEXISTENT.*"],
        resource_type=["alias"]
    )
    for val in find_res.contacted.values():
        assert val.get("data_sets") == []
        assert val.get("matched") == 0


def test_find_alias_excludes_alias_dataset_by_name(ansible_zos_module):
    """Exclude a catalog alias entry by its dataset name using a plain regex.

    Setup:
      - PDS  ``<hlq>.PDS``  with catalog alias ``<hlq>.PDS.ALI``
      - PDSE ``<hlq>.PDSE`` with catalog alias ``<hlq>.PDSE.ALI``

    zos_find is called with:
      patterns:  [``<hlq>.*``]        -- matches both catalog aliases
      excludes:  [r'.*\\.PDS\\.ALI']  -- fullmatch regex; drops only the PDS alias

    Expected:
      - Only ``<hlq>.PDSE.ALI`` is returned (matched == 1).
      - ``<hlq>.PDS.ALI`` is absent from data_sets.
      - ``members`` key is absent (include_member_aliases defaults to False,
        no parenthesised exclude either).
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pds_name  = f"{hlq}.PDS"
    pdse_name = f"{hlq}.PDSE"
    pds_ali   = f"{hlq}.PDS.ALI"
    pdse_ali  = f"{hlq}.PDSE.ALI"
    ali_pattern = f"{hlq}.*"
    try:
        # --- Create PDS with two members ---
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
        ])
        # --- Create PDSE with two members ---
        hosts.all.shell(cmd=f"dtouch -tpdse -l80 -rFB -s5 -e5 {pdse_name}")
        hosts.all.shell(cmd=f"dcp 'Test' \"//'{ pdse_name }(MEM1)'\"")
        hosts.all.shell(cmd=f"dcp 'Test' \"//'{ pdse_name }(MEM2)'\"")
        # --- Define catalog aliases ---
        for stdin, label in [
            (
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n",
                "PDS",
            ),
            (
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pdse_ali}) -\n"
                f"     RELATE({pdse_name}))\n",
                "PDSE",
            ),
        ]:
            res = hosts.all.shell(cmd=_IDCAMS_CMD, executable='/bin/sh', stdin=stdin)
            for v in res.contacted.values():
                assert v.get("rc") == 0, (
                    f"DEFINE ALIAS for {label} failed: {v.get('stdout')} {v.get('stderr')}"
                )
        # --- Find: exclude the PDS catalog alias by its name ---
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            excludes=[r".*\.PDS\.ALI"],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected 1 alias (PDSE only), got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == pdse_ali
            assert ds["alias_of"] == pdse_name
            # No parenthesised exclude and include_member_aliases is False
            assert "members" not in ds
            # Confirm PDS alias is absent
            names = [d["name"] for d in data_sets]
            assert pds_ali not in names, "PDS alias should have been excluded"
            assert val.get("matched") == 1
    finally:
        for ali in (pds_ali, pdse_ali):
            hosts.all.shell(
                cmd=_IDCAMS_CMD, executable='/bin/sh',
                stdin=f"  DELETE {ali} -\n    ALIAS\n",
            )
        hosts.all.zos_data_set(name=pds_name, state="absent")
        hosts.all.shell(cmd=f"drm {pdse_name}")


def test_find_alias_excludes_member_aliases_by_pattern(ansible_zos_module):
    """Exclude PDS members whose in-directory alias name matches a parenthesised pattern.

    Setup:
      - PDS ``<hlq>.PDS`` with:
          MBR1  → member alias ALIAS1
          MBR2  → member alias ALIAS2
          MBR3  (no member alias)
      - Catalog alias ``<hlq>.PDS.ALI`` pointing to the PDS.

    zos_find is called with:
      patterns:  [``<hlq>.PDS.*``]
      excludes:  ['(^ALIAS.*)']   -- parenthesised regex; matches any alias name
                                     starting with "ALIAS"

    Expected:
      - The catalog alias entry ``<hlq>.PDS.ALI`` is still returned (dataset-level
        exclude does not apply).
      - ``members`` key IS present (forced on whenever a parenthesised exclude is used).
      - MBR1 and MBR2 are absent from ``members`` (their alias names matched the pattern).
      - MBR3 is present in ``members`` with an empty ``aliases`` list (it has no
        member alias, so it could not have matched and is kept).
      - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pds_name  = f"{hlq}.PDS"
    ali_name  = f"{hlq}.PDS.ALI"
    ali_pattern = f"{hlq}.PDS.*"
    try:
        # --- Create PDS with three members ---
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR3)", "type": "member", "state": "present"},
        ])
        # Create in-directory member aliases: ALIAS1 → MBR1, ALIAS2 → MBR2
        hosts.all.shell(cmd=f"tso \"RENAME '{pds_name}(MBR1)' (ALIAS1) ALIAS\"")
        hosts.all.shell(cmd=f"tso \"RENAME '{pds_name}(MBR2)' (ALIAS2) ALIAS\"")
        # --- Define catalog alias for the PDS ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find: parenthesised exclude removes members with alias names matching ALIAS.* ---
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            excludes=["(^ALIAS.*)"],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"catalog alias entry must still be returned, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == pds_name
            # members key is forced into output by the parenthesised exclude
            assert "members" in ds, (
                "parenthesised exclude must force 'members' into output"
            )
            member_names = [m["name"] for m in ds["members"]]
            # MBR1 and MBR2 had alias names matching ^ALIAS.* → removed
            assert "MBR1" not in member_names, "MBR1 should be excluded (its alias ALIAS1 matched)"
            assert "MBR2" not in member_names, "MBR2 should be excluded (its alias ALIAS2 matched)"
            # MBR3 has no alias → cannot match the alias-name exclude → kept
            assert "MBR3" in member_names, "MBR3 has no alias name so it must survive"
            mbr3 = next(m for m in ds["members"] if m["name"] == "MBR3")
            assert mbr3["aliases"] == [], "MBR3 has no member aliases"
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_find_alias_excludes_all_member_aliases(ansible_zos_module):
    """Exclude ALL members that carry any alias using the catch-all pattern (^.*$).

    Setup:
      - PDS ``<hlq>.PDS`` with:
          MBR1  → member alias ALIAS1
          MBR2  → member alias ALIAS2
          MBR3  (no member alias)
      - Catalog alias ``<hlq>.PDS.ALI`` pointing to the PDS.

    zos_find is called with:
      patterns:  [``<hlq>.PDS.*``]
      resource_type: [alias]
      excludes:  ['(^.*$)']   -- parenthesised catch-all: matches any non-empty
                                 alias name, so every member that has at least
                                 one alias is removed.

    Expected:
      - The catalog alias entry ``<hlq>.PDS.ALI`` is still returned (dataset-level
        exclude does not apply — the pattern is fully parenthesised with nothing
        outside the parens).
      - ``members`` key IS present (forced by the parenthesised exclude).
      - MBR1 and MBR2 are absent (their alias names ALIAS1 / ALIAS2 matched ``^.*$``).
      - MBR3 is present with ``aliases: []`` — it has no alias name so ``^.*$``
        never runs against it; it cannot be excluded.
      - matched == 1.
    """
    hosts = ansible_zos_module
    hlq       = get_tmp_ds_name()
    pds_name  = f"{hlq}.PDS"
    ali_name  = f"{hlq}.PDS.ALI"
    ali_pattern = f"{hlq}.PDS.*"
    try:
        # --- Create PDS with three members ---
        hosts.all.zos_data_set(name=pds_name, type="pds", state="present",
                               space_primary=1, space_type="m")
        hosts.all.zos_data_set(batch=[
            {"name": f"{pds_name}(MBR1)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR2)", "type": "member", "state": "present"},
            {"name": f"{pds_name}(MBR3)", "type": "member", "state": "present"},
        ])
        # Give MBR1 and MBR2 in-directory aliases; leave MBR3 with none
        rename1 = hosts.all.shell(cmd=f"tso \"RENAME '{pds_name}(MBR1)' (ALIAS1) ALIAS\"")
        for v in rename1.contacted.values():
            assert v.get("rc") == 0, f"RENAME ALIAS1 failed: {v.get('stdout')} {v.get('stderr')}"
        rename2 = hosts.all.shell(cmd=f"tso \"RENAME '{pds_name}(MBR2)' (ALIAS2) ALIAS\"")
        for v in rename2.contacted.values():
            assert v.get("rc") == 0, f"RENAME ALIAS2 failed: {v.get('stdout')} {v.get('stderr')}"
        # --- Define catalog alias ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find: catch-all exclude removes every member that has any alias ---
        find_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            excludes=["(^.*$)"],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"catalog alias entry must still be returned, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == ali_name
            assert ds["alias_of"] == pds_name
            # members key is forced on by the parenthesised exclude
            assert "members" in ds, (
                "parenthesised exclude must force 'members' into output for a PDS target"
            )
            member_names = [m["name"] for m in ds["members"]]
            # MBR1 and MBR2 had aliases → matched (^.*$) → excluded
            assert "MBR1" not in member_names, "MBR1 should be excluded (ALIAS1 matched ^.*$)"
            assert "MBR2" not in member_names, "MBR2 should be excluded (ALIAS2 matched ^.*$)"
            # MBR3 has no alias → (^.*$) never tested against it → always survives
            assert "MBR3" in member_names, (
                "MBR3 has no alias so (^.*$) is never tested; it must survive"
            )
            mbr3 = next(m for m in ds["members"] if m["name"] == "MBR3")
            assert mbr3["aliases"] == [], "MBR3 carries no in-directory aliases"
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pds_name, state="absent")


def test_find_alias_filter_by_volume(ansible_zos_module, volumes_on_systems):
    """Volume filter for aliases: create two dataset aliases (PS, PDS) each
    on a different volume, then verify that filtering by one or both volumes
    returns the expected number of alias entries.

    Setup:
      - PS   ``<hlq>.PS``  on vol1  → catalog alias ``<hlq>.PS.ALI``
      - PDS  ``<hlq>.PDS`` on vol2  → catalog alias ``<hlq>.PDS.ALI``

    zos_find is called with:
      patterns:       [``<hlq>.*.*``]
      resource_type:  [alias]
      volumes:        [vol1]        → must return exactly 1 entry (PS alias)
      volumes:        [vol1, vol2]  → must return exactly 2 entries
    """
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    vol1 = volumes.get_available_vol()
    vol2 = volumes.get_available_vol()

    hlq      = get_tmp_ds_name()
    ps_name  = f"{hlq}.PS"
    pds_name = f"{hlq}.PDS"
    ps_ali   = f"{hlq}.PS.ALI"
    pds_ali  = f"{hlq}.PDS.ALI"
    pattern  = f"{hlq}.*.*"

    try:
        # --- Create the two target datasets, one per volume ---
        # zos_data_set is used for both so each dataset is catalogued;
        # dtouch -v allocates on a specific volume but does not create a
        # catalog entry, which causes IDCAMS DEFINE ALIAS to fail with
        # IDC3022I (INVALID RELATED OBJECT).
        hosts.all.zos_data_set(
            name=ps_name, type="seq", state="present",
            space_primary=1, space_type="m",
            record_format="fb", record_length=80,
            volumes=[vol1]
        )
        hosts.all.zos_data_set(
            name=pds_name, type="pds", state="present",
            space_primary=1, space_type="m", volumes=[vol2]
        )
        # --- Define one catalog alias per dataset ---
        # Each DEFINE ALIAS is split across continuation lines ('-') to stay
        # within the 80-byte stdin record limit enforced by IDCAMS.
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ps_ali}) -\n"
                f"     RELATE({ps_name}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )

        # --- Filter by vol1 only: must return exactly the PS alias ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            volumes=[vol1],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None
            assert len(data_sets) == 1, (
                f"Expected 1 alias entry for volume {vol1}, got {data_sets}"
            )
            assert data_sets[0]["name"]     == ps_ali
            assert data_sets[0]["alias_of"] == ps_name
            assert data_sets[0]["type"]     == "ALIAS"
            assert val.get("matched") == 1

        # --- Filter by vol1 + vol2: must return both aliases ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            volumes=[vol1, vol2],
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None
            assert len(data_sets) == 2, (
                f"Expected 2 alias entries for volumes {[vol1, vol2]}, got {data_sets}"
            )
            returned_names = {ds["name"] for ds in data_sets}
            assert ps_ali  in returned_names, f"{ps_ali} not found in {returned_names}"
            assert pds_ali in returned_names, f"{pds_ali} not found in {returned_names}"
            assert val.get("matched") == 2
            for ds in data_sets:
                assert ds["type"] == "ALIAS"

    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {ps_ali}  ALIAS\n"
                f"  DELETE {pds_ali} ALIAS\n"
            ),
        )
        hosts.all.shell(cmd=f"drm {ps_name}")
        hosts.all.zos_data_set(name=pds_name, state="absent")

def test_find_alias_filters_by_target_size(ansible_zos_module):
    """Alias size filtering uses the target sequential dataset allocated size.

    Creates two PS datasets and catalog aliases pointing to them:
    - one target smaller than 2 MB
    - one target larger than 4 MB

    Verifies alias filtering by size returns the alias whose target is:
    - > 2 MB
    - < 2 MB
    """
    hosts = ansible_zos_module
    hlq = get_tmp_ds_name(mlq_size=3, llq_size=3)
    small_ps_name = f"{hlq}.SMALL"
    large_ps_name = f"{hlq}.LARGE"
    small_ali_name = f"{hlq}.SMALL.ALI"
    large_ali_name = f"{hlq}.LARGE.ALI"
    alias_pattern = f"{hlq}.*.*"

    try:
        hosts.all.zos_data_set(
            batch=[
                {
                    "name": small_ps_name,
                    "type": "seq",
                    "state": "present",
                    "space_primary": 1,
                    "space_type": "m",
                    "record_length": 80,
                    "record_format": "fb",
                },
                {
                    "name": large_ps_name,
                    "type": "seq",
                    "state": "present",
                    "space_primary": 5,
                    "space_type": "m",
                    "record_length": 80,
                    "record_format": "fb",
                },
            ]
        )
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({small_ali_name}) -\n"
                f"     RELATE({small_ps_name}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({large_ali_name}) -\n"
                f"     RELATE({large_ps_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )

        larger_find_res = hosts.all.zos_find(
            patterns=[alias_pattern],
            resource_type=["alias"],
            size="2m",
        )
        print(larger_find_res.contacted.values())
        for val in larger_find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected only alias for target > 2 MB, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"] == "ALIAS"
            assert ds["name"] == large_ali_name
            assert ds["alias_of"] == large_ps_name
            assert val.get("matched") == 1
            assert val.get("examined") is not None
            assert val.get("msg") is None

        smaller_find_res = hosts.all.zos_find(
            patterns=[alias_pattern],
            resource_type=["alias"],
            size="-2m",
        )
        for val in smaller_find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected only alias for target < 2 MB, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"] == "ALIAS"
            assert ds["name"] == small_ali_name
            assert ds["alias_of"] == small_ps_name
            assert val.get("matched") == 1
            assert val.get("examined") is not None
            assert val.get("msg") is None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {small_ali_name} -\n    ALIAS\n"
                f"  DELETE {large_ali_name} -\n    ALIAS\n"
            ),
        )
        hosts.all.shell(cmd=f"drm {small_ps_name}")
        hosts.all.shell(cmd=f"drm {large_ps_name}")


def test_find_alias_filters_by_target_creation_date(ansible_zos_module):
    """Alias age filtering via creation_date uses the target sequential dataset
    creation date.
    Creates a PS dataset with dtouch (creation_date = today) and a catalog
    alias pointing to it, then verifies:
    - age="-2d" (created within last 2 days) matches the alias.
    - age="2d"  (created more than 2 days ago) does not match.
    """
    hosts = ansible_zos_module
    hlq = get_tmp_ds_name(mlq_size=3, llq_size=3)
    ps_name = f"{hlq}.SEQ"
    ali_name = f"{hlq}.SEQ.ALI"
    ali_pattern = f"{hlq}.SEQ.*"
    try:
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 {ps_name}")
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({ps_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # creation_date is today — alias should match "newer than 2 days"
        creation_recent_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="-2d",
            age_stamp="creation_date",
        )
        print(creation_recent_res.contacted.values())

        for val in creation_recent_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected alias to match creation_date < 2d, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"] == "ALIAS"
            assert ds["name"] == ali_name
            assert ds["alias_of"] == ps_name
            assert val.get("matched") == 1
            assert val.get("examined") is not None
            assert val.get("msg") is None
        # creation_date is today — alias should NOT match "older than 2 days"
        creation_old_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="2d",
            age_stamp="creation_date",
        )
        for val in creation_old_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets == [], (
                f"expected no alias to match creation_date > 2d, got {data_sets}"
            )
            assert val.get("matched") == 0
            assert val.get("examined") is not None
            assert val.get("msg") is None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.shell(cmd=f"drm {ps_name}")


def test_find_alias_filters_by_target_ref_date_default(ansible_zos_module):
    """Alias age filtering via ref_date when the target has ref_date = 0000/01/01.
    dtouch allocates a sequential dataset without writing any data.  DFSMS
    reports ref_date as 0000/01/01 for such a dataset (confirmed via dls -u).
    Because ref_date has never been updated, any age filter using age_stamp=
    ref_date cannot meaningfully compare the date, and the alias is not returned
    for either direction:
    Verifies:
    - age="-2d" (newer than 2 days) returns 0 matches — ref_date 0000/01/01
      is not a valid recent date.
    - age="2d"  (older than 2 days) returns 0 matches — ref_date 0000/01/01
      is not a valid historical date either.
    """
    hosts = ansible_zos_module
    hlq = get_tmp_ds_name(mlq_size=3, llq_size=3)
    ps_name = f"{hlq}.SEQ"
    ali_name = f"{hlq}.SEQ.ALI"
    ali_pattern = f"{hlq}.SEQ.*"
    try:
        # dtouch only — leaves ref_date as 0000/01/01 (no data written)
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 {ps_name}")
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({ps_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # ref_date == 0000/01/01 — not a valid recent date, should not match
        ref_default_recent_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="-2d",
            age_stamp="ref_date",
        )
        print(ref_default_recent_res.contacted.values())
        for val in ref_default_recent_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets == [], (
                f"expected no alias to match ref_date 0000/01/01 with age='-2d', got {data_sets}"
            )
            assert val.get("matched") == 0
            assert val.get("examined") is not None
            assert val.get("msg") is None
        # ref_date == 0000/01/01 — not a valid historical date, should not match
        ref_default_old_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="2d",
            age_stamp="ref_date",
        )
        for val in ref_default_old_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets == [], (
                f"expected no alias to match ref_date 0000/01/01 with age='2d', got {data_sets}"
            )
            assert val.get("matched") == 0
            assert val.get("examined") is not None
            assert val.get("msg") is None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.shell(cmd=f"drm {ps_name}")

def test_find_alias_filters_by_target_ref_date_current(ansible_zos_module):
    """Alias age filtering via ref_date after the target dataset has been written.
    Writing a record to the target PS with decho updates ref_date to today.
    With ref_date == today:
    - age="-2d" (newer than 2 days) matches the alias.
    - age="2d"  (older than 2 days) does not match.
    """
    hosts = ansible_zos_module
    hlq = get_tmp_ds_name(mlq_size=3, llq_size=3)
    ps_name = f"{hlq}.SEQ"
    ali_name = f"{hlq}.SEQ.ALI"
    ali_pattern = f"{hlq}.SEQ.*"
    try:
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 {ps_name}")
        # Write a record so ref_date is updated to today
        hosts.all.shell(cmd=f"decho 'alias ref_date test record' '{ps_name}'")
        hosts.all.shell(cmd=f"dcat '{ps_name}'")
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({ps_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # ref_date == today — alias should match "newer than 2 days"
        ref_recent_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="-2d",
            age_stamp="ref_date",
        )
        for val in ref_recent_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected alias to match ref_date < 2d after write, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"] == "ALIAS"
            assert ds["name"] == ali_name
            assert ds["alias_of"] == ps_name
            assert val.get("matched") == 1
            assert val.get("examined") is not None
            assert val.get("msg") is None
        # ref_date == today — alias should NOT match "older than 2 days"
        ref_old_res = hosts.all.zos_find(
            patterns=[ali_pattern],
            resource_type=["alias"],
            age="2d",
            age_stamp="ref_date",
        )
        for val in ref_old_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets == [], (
                f"expected no alias to match ref_date > 2d after write, got {data_sets}"
            )
            assert val.get("matched") == 0
            assert val.get("examined") is not None
            assert val.get("msg") is None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.shell(cmd=f"drm {ps_name}")


def test_find_alias_contains_filters_by_target_ps_content(ansible_zos_module):
    """Alias contains filter searches the content of the target dataset.

    Setup:
      - PS ``<hlq>.MATCH``  — written with search string "hello world"
        catalog alias ``<hlq>.MATCH.ALI`` pointing to it.
      - PS ``<hlq>.NOMATCH`` — written with a different string "no match here"
        catalog alias ``<hlq>.NOMATCH.ALI`` pointing to it.

    zos_find is called with:
      patterns:       [``<hlq>.*.*``]
      resource_type:  [alias]
      contains:       'hello world'

    Expected:
      - Only the alias whose target contains "hello world" is returned
        (``<hlq>.MATCH.ALI``).
      - matched == 1.
    """
    hosts = ansible_zos_module
    hlq = get_tmp_ds_name(mlq_size=3, llq_size=3)
    match_ps    = f"{hlq}.MATCH"
    nomatch_ps  = f"{hlq}.NOMATCH"
    match_ali   = f"{hlq}.MATCH.ALI"
    nomatch_ali = f"{hlq}.NOMATCH.ALI"
    pattern     = f"{hlq}.*.*"
    search_str  = "hello world"
    try:
        # --- Create and populate both target PS datasets ---
        hosts.all.zos_data_set(
            batch=[
                {
                    "name": match_ps,
                    "type": "seq",
                    "state": "present",
                    "space_primary": 1,
                    "space_type": "m",
                    "record_format": "fb",
                    "record_length": 80,
                },
                {
                    "name": nomatch_ps,
                    "type": "seq",
                    "state": "present",
                    "space_primary": 1,
                    "space_type": "m",
                    "record_format": "fb",
                    "record_length": 80,
                },
            ]
        )
        hosts.all.shell(cmd=f"decho '{search_str}' '{match_ps}'")
        hosts.all.shell(cmd=f"decho 'no match here' '{nomatch_ps}'")
        # --- Define one catalog alias per target ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({match_ali}) -\n"
                f"     RELATE({match_ps}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({nomatch_ali}) -\n"
                f"     RELATE({nomatch_ps}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find: only the alias whose target contains the search string ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search_str,
        )
        for val in find_res.contacted.values():
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected exactly 1 alias (target contains '{search_str}'), got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == match_ali
            assert ds["alias_of"] == match_ps
            assert val.get("matched") == 1
            assert val.get("msg") is None
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {match_ali}   -\n    ALIAS\n"
                f"  DELETE {nomatch_ali} -\n    ALIAS\n"
            ),
        )
        hosts.all.shell(cmd=f"drm {match_ps}")
        hosts.all.shell(cmd=f"drm {nomatch_ps}")


def test_find_alias_contains_with_include_member_aliases_prunes_members(ansible_zos_module):
    """contains + include_member_aliases prunes members list to only those that matched.

    Both a PDS and a PDSE alias are exercised in one test, matching the two-entry
    output shape confirmed during manual testing:

      data_sets:
        - {name: <hlq>.PDS.ALI,  alias_of: <hlq>.PDS,  type: ALIAS,
           members: [{name: MEM2, aliases: []}]}
        - {name: <hlq>.PDSE.ALI, alias_of: <hlq>.PDSE, type: ALIAS,
           members: [{name: MEM2, aliases: []}]}

    Setup:
      - PDS  ``<hlq>.PDS``  — MEM1 ("no match"), MEM2 ("find me").
      - PDSE ``<hlq>.PDSE`` — MEM1 ("no match"), MEM2 ("find me").
      - Catalog alias ``<hlq>.PDS.ALI``  → PDS.
      - Catalog alias ``<hlq>.PDSE.ALI`` → PDSE.

    zos_find is called with:
      patterns:               [``<hlq>.*.*``]
      resource_type:          [alias]
      contains:               'find me'
      include_member_aliases: true

    Expected:
      - Two alias entries returned (PDS + PDSE).
      - Each ds['members'] contains exactly MEM2 only.
      - MEM1 is absent from every ds['members'].
      - matched == 2, msg is None.
    """
    hosts    = ansible_zos_module
    hlq      = get_tmp_ds_name(mlq_size=3, llq_size=3)
    pds_name  = f"{hlq}.PDS"
    pdse_name = f"{hlq}.PDSE"
    pds_ali   = f"{hlq}.PDS.ALI"
    pdse_ali  = f"{hlq}.PDSE.ALI"
    pattern   = f"{hlq}.*.*"
    search    = "find me"
    mem_match    = "MEM2"
    mem_no_match = "MEM1"
    try:
        # --- Create PDS + members ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pds_name, "type": "pds", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pds_name}({mem_match})",    "type": "member", "state": "present"},
                {"name": f"{pds_name}({mem_no_match})", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho '{search}' \"{pds_name}({mem_match})\"")
        hosts.all.shell(cmd=f"decho 'no match' \"{pds_name}({mem_no_match})\"")
        # --- Create PDSE + members ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pdse_name, "type": "pdse", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pdse_name}({mem_match})",    "type": "member", "state": "present"},
                {"name": f"{pdse_name}({mem_no_match})", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho '{search}' \"{pdse_name}({mem_match})\"")
        hosts.all.shell(cmd=f"decho 'no match' \"{pdse_name}({mem_no_match})\"")
        # --- Define catalog aliases ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pdse_ali}) -\n"
                f"     RELATE({pdse_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search,
            include_member_aliases=True,
        )
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 2, (
                f"expected 2 alias entries (PDS + PDSE), got {data_sets}"
            )
            by_name = {ds["name"]: ds for ds in data_sets}
            assert pds_ali  in by_name, f"PDS alias {pds_ali} missing"
            assert pdse_ali in by_name, f"PDSE alias {pdse_ali} missing"
            for ali, target in ((pds_ali, pds_name), (pdse_ali, pdse_name)):
                ds = by_name[ali]
                assert ds["type"]     == "ALIAS"
                assert ds["alias_of"] == target
                assert "members" in ds, f"'members' key missing from {ali}"
                returned = {m["name"] for m in ds["members"]}
                assert returned == {mem_match}, (
                    f"{ali}: expected only {mem_match!r}, got {returned}"
                )
                assert mem_no_match not in returned, (
                    f"{ali}: non-matching member {mem_no_match!r} should be absent"
                )
            assert val.get("matched") == 2
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {pds_ali}  -\n    ALIAS\n"
                f"  DELETE {pdse_ali} -\n    ALIAS\n"
            ),
        )
        hosts.all.zos_data_set(
            batch=[
                {"name": pds_name,  "state": "absent"},
                {"name": pdse_name, "state": "absent"},
            ]
        )


def test_find_alias_contains_without_include_member_aliases(ansible_zos_module):
    """contains without include_member_aliases filters aliases correctly, no members key.

    include_member_aliases is NOT required for contains to work.  When omitted
    (default False), dls is called without -a so no member data is fetched.
    The alias entry is still correctly included or excluded based on whether
    its target PDS/PDSE has any member containing the search string — but the
    output entry has no 'members' key.

    Setup:
      - PDS  ``<hlq>.PDS``  — MEM1 has "needle", MEM2 does not.
      - PDSE ``<hlq>.PDSE`` — neither member has "needle".
      - Catalog alias ``<hlq>.PDS.ALI``  → PDS  (target has a matching member).
      - Catalog alias ``<hlq>.PDSE.ALI`` → PDSE (target has no matching member).

    zos_find is called with:
      patterns:               [``<hlq>.*.*``]
      resource_type:          [alias]
      contains:               'needle'
      (include_member_aliases omitted — defaults to false)

    Expected:
      - Only ``<hlq>.PDS.ALI`` is returned.
      - ``<hlq>.PDSE.ALI`` is absent.
      - The returned entry has NO 'members' key.
      - matched == 1, msg is None.
    """
    hosts    = ansible_zos_module
    hlq      = get_tmp_ds_name(mlq_size=3, llq_size=3)
    pds_name  = f"{hlq}.PDS"
    pdse_name = f"{hlq}.PDSE"
    pds_ali   = f"{hlq}.PDS.ALI"
    pdse_ali  = f"{hlq}.PDSE.ALI"
    pattern   = f"{hlq}.*.*"
    search    = "needle"
    try:
        # --- Create PDS: MEM1 has the search string, MEM2 does not ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pds_name, "type": "pds", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pds_name}(MEM1)", "type": "member", "state": "present"},
                {"name": f"{pds_name}(MEM2)", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho '{search}' \"{pds_name}(MEM1)\"")
        hosts.all.shell(cmd=f"decho 'haystack' \"{pds_name}(MEM2)\"")
        # --- Create PDSE: neither member has the search string ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pdse_name, "type": "pdse", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pdse_name}(MEM1)", "type": "member", "state": "present"},
                {"name": f"{pdse_name}(MEM2)", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho 'haystack' \"{pdse_name}(MEM1)\"")
        hosts.all.shell(cmd=f"decho 'haystack' \"{pdse_name}(MEM2)\"")
        # --- Define catalog aliases ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pdse_ali}) -\n"
                f"     RELATE({pdse_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find: include_member_aliases not set (defaults to False) ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search,
        )
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected only the PDS alias, got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == pds_ali
            assert ds["alias_of"] == pds_name
            # No members key — include_member_aliases was not set
            assert "members" not in ds, (
                "'members' key must be absent when include_member_aliases=False"
            )
            names = [d["name"] for d in data_sets]
            assert pdse_ali not in names, (
                "PDSE alias must be absent (no member contains the search string)"
            )
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {pds_ali}  -\n    ALIAS\n"
                f"  DELETE {pdse_ali} -\n    ALIAS\n"
            ),
        )
        hosts.all.zos_data_set(
            batch=[
                {"name": pds_name,  "state": "absent"},
                {"name": pdse_name, "state": "absent"},
            ]
        )


def test_find_alias_contains_gdg_generation(ansible_zos_module):
    """contains on an alias pointing to a GDG generation filters by target content.

    GDG *generations* (e.g. HLQ.GDG.G0001V00) are sequential datasets.
    A catalog alias can point to a specific generation.  The contains filter
    is applied against the target generation (alias_of), not the alias entry.

    Setup:
      - GDG base ``<hlq>.GDG`` with limit=3.
      - Generation G0001V00 — written with "gdg search content".
        Catalog alias ``<hlq>.GDG.MATCH.ALI`` → G0001V00.
      - Generation G0002V00 — written with "different content".
        Catalog alias ``<hlq>.GDG.NOMATCH.ALI`` → G0002V00.

    zos_find is called with:
      patterns:       [``<hlq>.GDG.*.*``]
      resource_type:  [alias]
      contains:       'gdg search content'

    Expected:
      - Only ``<hlq>.GDG.MATCH.ALI`` is returned (alias_of == G0001V00).
      - ``<hlq>.GDG.NOMATCH.ALI`` is absent.
      - matched == 1, msg is None.
    """
    hosts = ansible_zos_module
    # mlq_size=3, llq_size=3 keeps HLQ short enough so that appending
    # .GDG.G0001V00 (13 chars) stays within the 44-char z/OS name limit.
    hlq          = get_tmp_ds_name(mlq_size=3, llq_size=3)
    gdg_base     = f"{hlq}.GDG"
    gen1         = f"{hlq}.GDG.G0001V00"
    gen2         = f"{hlq}.GDG.G0002V00"
    match_ali    = f"{hlq}.GDG.MATCH.ALI"
    nomatch_ali  = f"{hlq}.GDG.NOMATCH.ALI"
    pattern      = f"{hlq}.GDG.*.*"
    search       = "gdg search content"
    try:
        # --- Create GDG base and two generations ---
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE GDG -\n"
                f"    (NAME({gdg_base}) -\n"
                f"     LIMIT(3) NOEMPTY SCRATCH)\n"
            ),
        )
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 '{gdg_base}(+1)'")
        hosts.all.shell(cmd=f"decho '{search}' '{gen1}'")
        hosts.all.shell(cmd=f"dtouch -tseq -l80 -rFB -s1 -e1 '{gdg_base}(+1)'")
        hosts.all.shell(cmd=f"decho 'different content' '{gen2}'")
        # --- Define one catalog alias per generation ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({match_ali}) -\n"
                f"     RELATE({gen1}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({nomatch_ali}) -\n"
                f"     RELATE({gen2}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find: only the alias whose target generation contains the string ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search,
        )
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 1, (
                f"expected exactly 1 alias (matching generation), got {data_sets}"
            )
            ds = data_sets[0]
            assert ds["type"]     == "ALIAS"
            assert ds["name"]     == match_ali
            assert ds["alias_of"] == gen1
            names = [d["name"] for d in data_sets]
            assert nomatch_ali not in names, (
                "alias pointing to non-matching generation must be absent"
            )
            assert val.get("matched") == 1
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {match_ali}   -\n    ALIAS\n"
                f"  DELETE {nomatch_ali} -\n    ALIAS\n"
            ),
        )
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {gdg_base} -\n    GDG\n",
        )



def test_find_alias_contains_no_match_returns_empty(ansible_zos_module):
    """contains with no matching member in the target PDSE returns zero results.

    Setup:
      - PDSE ``<hlq>.PDSE`` with two members — neither contains the search string.
      - Catalog alias ``<hlq>.PDSE.ALI`` → PDSE.

    zos_find is called with:
      patterns:               [``<hlq>.*.*``]
      resource_type:          [alias]
      contains:               'ghost string'
      include_member_aliases: true

    Expected:
      - data_sets == [] (no alias returned).
      - matched == 0, msg is None.
    """
    hosts     = ansible_zos_module
    hlq       = get_tmp_ds_name(mlq_size=3, llq_size=3)
    pdse_name = f"{hlq}.PDSE"
    ali_name  = f"{hlq}.PDSE.ALI"
    pattern   = f"{hlq}.*.*"
    search    = "ghost string"
    try:
        # --- Create PDSE with two members, neither containing the search string ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pdse_name, "type": "pdse", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pdse_name}(MEM1)", "type": "member", "state": "present"},
                {"name": f"{pdse_name}(MEM2)", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho 'irrelevant' \"{pdse_name}(MEM1)\"")
        hosts.all.shell(cmd=f"decho 'irrelevant' \"{pdse_name}(MEM2)\"")
        # --- Define catalog alias ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ali_name}) -\n"
                f"     RELATE({pdse_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search,
            include_member_aliases=True,
        )
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            assert val.get("data_sets") == [], (
                f"expected no alias when no member matches, got {val.get('data_sets')}"
            )
            assert val.get("matched") == 0
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=f"  DELETE {ali_name} -\n    ALIAS\n",
        )
        hosts.all.zos_data_set(name=pdse_name, state="absent")


def test_find_alias_contains_mixed_ps_and_pds(ansible_zos_module):
    """contains with a mix of PS and PDS aliases — PS matches, PDS partially matches.

    Setup:
      - PS  ``<hlq>.PS``  written with "search term".
        Catalog alias ``<hlq>.PS.ALI`` → PS.
      - PDS ``<hlq>.PDS`` with two members:
          MEM1 written with "search term"  (matches)
          MEM2 written with "other content" (no match)
        Catalog alias ``<hlq>.PDS.ALI`` → PDS.

    zos_find is called with:
      patterns:               [``<hlq>.*.*``]
      resource_type:          [alias]
      contains:               'search term'
      include_member_aliases: true

    Expected:
      - Both aliases are returned (matched == 2).
      - PS alias: no 'members' key (sequential target).
      - PDS alias: 'members' pruned to [MEM1] only; MEM2 absent.
      - msg is None.
    """
    hosts    = ansible_zos_module
    hlq      = get_tmp_ds_name(mlq_size=3, llq_size=3)
    ps_name  = f"{hlq}.PS"
    pds_name = f"{hlq}.PDS"
    ps_ali   = f"{hlq}.PS.ALI"
    pds_ali  = f"{hlq}.PDS.ALI"
    pattern  = f"{hlq}.*.*"
    search   = "search term"
    try:
        # --- Create PS ---
        hosts.all.zos_data_set(
            batch=[
                {"name": ps_name, "type": "seq", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
            ]
        )
        hosts.all.shell(cmd=f"decho '{search}' '{ps_name}'")
        # --- Create PDS with two members ---
        hosts.all.zos_data_set(
            batch=[
                {"name": pds_name, "type": "pds", "state": "present",
                 "space_primary": 1, "space_type": "m",
                 "record_format": "fb", "record_length": 80},
                {"name": f"{pds_name}(MEM1)", "type": "member", "state": "present"},
                {"name": f"{pds_name}(MEM2)", "type": "member", "state": "present"},
            ]
        )
        hosts.all.shell(cmd=f"decho '{search}' \"{pds_name}(MEM1)\"")
        hosts.all.shell(cmd=f"decho 'other content' \"{pds_name}(MEM2)\"")
        # --- Define catalog aliases ---
        define_res = hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DEFINE ALIAS -\n"
                f"    (NAME({ps_ali}) -\n"
                f"     RELATE({ps_name}))\n"
                f"  DEFINE ALIAS -\n"
                f"    (NAME({pds_ali}) -\n"
                f"     RELATE({pds_name}))\n"
            ),
        )
        for v in define_res.contacted.values():
            assert v.get("rc") == 0, (
                f"DEFINE ALIAS failed: {v.get('stdout')} {v.get('stderr')}"
            )
        # --- Find ---
        find_res = hosts.all.zos_find(
            patterns=[pattern],
            resource_type=["alias"],
            contains=search,
            include_member_aliases=True,
        )
        for val in find_res.contacted.values():
            assert val.get("msg") is None
            data_sets = val.get("data_sets")
            assert data_sets is not None and len(data_sets) == 2, (
                f"expected 2 aliases (PS + PDS), got {data_sets}"
            )
            by_name = {ds["name"]: ds for ds in data_sets}
            assert ps_ali  in by_name, f"PS alias {ps_ali} missing"
            assert pds_ali in by_name, f"PDS alias {pds_ali} missing"
            # PS alias: sequential target — no members key
            ps_entry = by_name[ps_ali]
            assert ps_entry["type"]     == "ALIAS"
            assert ps_entry["alias_of"] == ps_name
            assert "members" not in ps_entry, (
                "PS alias must have no 'members' key (sequential target)"
            )
            # PDS alias: members pruned to only MEM1
            pds_entry = by_name[pds_ali]
            assert pds_entry["type"]     == "ALIAS"
            assert pds_entry["alias_of"] == pds_name
            assert "members" in pds_entry, "PDS alias must have 'members' key"
            returned = {m["name"] for m in pds_entry["members"]}
            assert returned == {"MEM1"}, (
                f"expected only MEM1 in PDS alias members, got {returned}"
            )
            assert "MEM2" not in returned
            assert val.get("matched") == 2
    finally:
        hosts.all.shell(
            cmd=_IDCAMS_CMD, executable='/bin/sh',
            stdin=(
                f"  DELETE {ps_ali}  -\n    ALIAS\n"
                f"  DELETE {pds_ali} -\n    ALIAS\n"
            ),
        )
        hosts.all.zos_data_set(
            batch=[
                {"name": ps_name,  "state": "absent"},
                {"name": pds_name, "state": "absent"},
            ]
        )
