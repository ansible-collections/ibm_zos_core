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

__metaclass__ = type

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


def create_vsam_ksds(ds_name, ansible_zos_module, volume="000000"):
    hosts = ansible_zos_module
    alloc_cmd = """     DEFINE CLUSTER (NAME({0})  -
    INDEXED                 -
    RECSZ(80,80)            -
    TRACKS(1,1)             -
    KEYS(5,0)               -
    CISZ(4096)              -
    VOLUMES({1})         -
    FREESPACE(3,3) )        -
    DATA (NAME({0}.DATA))   -
    INDEX (NAME({0}.INDEX))""".format(
        ds_name, volume
    )

    return hosts.all.shell(
        cmd="mvscmdauth --pgm=idcams --sysprint=* --sysin=stdin",
        executable='/bin/sh',
        stdin=alloc_cmd,
    )


def test_find_sequential_data_sets_containing_single_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='seq', state='present') for i in SEQ_NAMES]
        )
        for ds in SEQ_NAMES:
            hosts.all.zos_lineinfile(src=ds, line=search_string)

        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*'],
            contains=search_string
        )
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in SEQ_NAMES]
        )


def test_find_sequential_data_sets_multiple_patterns(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "dummy string"
    new_ds = "TEST.FIND.SEQ.FUNCTEST.FOURTH"
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='seq', state='present') for i in SEQ_NAMES]
        )
        hosts.all.zos_data_set(name=new_ds, type='seq', state='present')
        hosts.all.zos_lineinfile(src=new_ds, line="incorrect string")
        for ds in SEQ_NAMES:
            hosts.all.zos_lineinfile(src=ds, line=search_string)

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
            batch=[dict(name=i, state='absent') for i in SEQ_NAMES]
        )
        hosts.all.zos_data_set(
            name=new_ds, state='absent'
        )


def test_find_pds_members_containing_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='pds') for i in PDS_NAMES]
        )
        hosts.all.zos_data_set(
            batch=[
                dict(
                    name=i + "(MEMBER)",
                    type="MEMBER",
                    state='present',
                    replace='yes'
                ) for i in PDS_NAMES
            ]
        )
        for ds in PDS_NAMES:
            hosts.all.zos_lineinfile(src=ds + "(MEMBER)", line=search_string)

        find_res = hosts.all.zos_find(
            pds_paths=['TEST.FIND.PDS.FUNCTEST.*'],
            contains=search_string,
            patterns=['.*']
        )
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in PDS_NAMES
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in PDS_NAMES]
        )


def test_exclude_data_sets_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[
                dict(
                    name=i,
                    type='seq',
                    record_length=80,
                    state='present'
                ) for i in SEQ_NAMES
            ]
        )
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*'],
            excludes=['.*THIRD$']
        )
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in SEQ_NAMES]
        )


def test_exclude_members_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='pds', state='present') for i in PDS_NAMES]
        )
        hosts.all.zos_data_set(
            batch=[dict(name=i + "(MEMBER)", type="MEMBER") for i in PDS_NAMES]
        )
        hosts.all.zos_data_set(
            batch=[dict(name=i + "(FILE)", type="MEMBER") for i in PDS_NAMES]
        )
        find_res = hosts.all.zos_find(
            pds_paths=['TEST.FIND.PDS.FUNCTEST.*'], excludes=['.*FILE$'], patterns=['.*']
        )
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in PDS_NAMES]
        )


def test_find_data_sets_older_than_age(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(
        patterns=['IMSTESTL.IMS01.RESTART', 'IMSTESTL.IMS01.LGMSGL'],
        age='2d'
    )
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 2
        assert val.get('matched') == 2


def test_find_data_sets_larger_than_size(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['IMSTESTL.MQBATCH.*'], size='100k')
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 2
        assert val.get('matched') == 2


def test_find_data_sets_smaller_than_size(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(patterns=['IMSTESTL.MQBATCH.*'], size='-1m')
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 1
        assert val.get('matched') == 1


def test_find_data_sets_in_volume(ansible_zos_module):
    hosts = ansible_zos_module

    find_res = hosts.all.zos_find(
        patterns=['USER.*'], volumes=['IMSSUN']
    )
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) >= 1
        assert val.get('matched') >= 1


def test_find_vsam_pattern(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        for vsam in VSAM_NAMES:
            create_vsam_ksds(vsam, hosts)
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.VSAM.*.*'], resource_type='cluster'
        )
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in VSAM_NAMES]
        )


def test_find_vsam_in_volume(ansible_zos_module):
    hosts = ansible_zos_module
    alternate_vsam = "TEST.FIND.ALTER.VSAM"
    try:
        for vsam in VSAM_NAMES:
            create_vsam_ksds(vsam, hosts, volume="222222")
        create_vsam_ksds(alternate_vsam, hosts, volume="000000")
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.*.*.*'], volumes=['222222'], resource_type='cluster'
        )
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 1
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(
            batch=[dict(name=i, state='absent') for i in VSAM_NAMES]
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
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0


def test_find_non_existent_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    find_res = hosts.all.zos_find(pds_paths=['TEST.NONE.PDS.*'], patterns=['.*'])
    print(vars(find_res))
    for val in find_res.contacted.values():
        assert len(val.get('data_sets')) == 0
        assert val.get('matched') == 0
