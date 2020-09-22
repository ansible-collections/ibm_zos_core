# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

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
        hosts.all.zos_data_set(batch=[dict(name=i, type='seq', state='present') for i in SEQ_NAMES])
        for ds in SEQ_NAMES:
            hosts.all.zos_lineinfile(src=ds, line=search_string)

        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], contains=search_string)
        for val in find_res.contacted.values():
            assert val.get('msg') is None
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])


def test_find_sequential_data_sets_multiple_patterns(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "dummy string"
    new_ds ="TEST.FIND.SEQ.FUNCTEST.FOURTH"
    try:
        hosts.all.zos_data_set(batch=[dict(name=i, type='seq', state='present') for i in SEQ_NAMES])
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
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])
        hosts.all.zos_data_set(name=new_ds, state='absent')


def test_find_pds_members_containing_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(batch=[dict(name=i, type='pds', record_length=80) for i in PDS_NAMES])
        hosts.all.zos_data_set(batch=[dict(name=i + "(MEMBER)", type="MEMBER") for i in PDS_NAMES])
        for ds in SEQ_NAMES:
            hosts.all.zos_lineinfile(src=ds + "(MEMBER)", line=search_string)

        find_res = hosts.all.zos_find(pds_paths=['TEST.FIND.PDS.*.*'], contains=search_string)
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) != 0
            for ds in val.get('data_sets'):
                assert ds.get('name') in PDS_NAMES
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in PDS_NAMES])


def test_exclude_data_sets_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(batch=[dict(name=i, type='seq', record_length=80, state='present') for i in SEQ_NAMES])
        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], excludes=['.*THIRD$'])
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 2
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])


def test_exclude_members_from_matched_list(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(batch=[dict(name=i, type='pds', record_length=80) for i in PDS_NAMES])
        hosts.all.zos_data_set(batch=[dict(name=i + "(MEMBER)", type="MEMBER") for i in PDS_NAMES])
        hosts.all.zos_data_set(batch=[dict(name=i + "(FILE)", type="MEMBER") for i in PDS_NAMES])
        find_res = hosts.all.zos_find(pds_paths=['TEST.FIND.PDS.*.*'], excludes=['.*FILE$'], patterns=['.*'])
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert ds.get('name') in PDS_NAMES
                assert len(ds.get('members')) == 1
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in PDS_NAMES])


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
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='seq', space_primary=10, state='present') for i in SEQ_NAMES]
        )
        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], size='6m')
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == 3
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])


def test_find_data_sets_smaller_than_size(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='seq', space_primary=10, state='present') for i in SEQ_NAMES]
        )
        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], size='-12m')
        print(vars(find_res))
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])


def test_find_data_sets_in_volume(ansible_zos_module):
    hosts = ansible_zos_module
    try:
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='seq', volumes='000000', state='present') for i in SEQ_NAMES]
        )
        hosts.all.zos_data_set(
            batch=[dict(name=i, type='pds', volumes='222222', state='present') for i in PDS_NAMES]
        )
        find_res = hosts.all.zos_find(patterns=['TEST.FIND.*.*.*'], volumes=['000000'])
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 3
            for ds in val.get('data_sets'):
                assert ds.get('name') in SEQ_NAMES
            assert val.get('matched') == len(val.get('data_sets'))

        find_res = hosts.all.zos_find(patterns=['TEST.FIND.*.*.*'], volumes=['000000', '222222'])
        for val in find_res.contacted.values():
            assert len(val.get('data_sets')) == 6
            assert val.get('matched') == len(val.get('data_sets'))
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in PDS_NAMES])


# def test_find_vsam_pattern(ansible_zos_module):
#     hosts = ansible_zos_module
#     try:
#         for vsam in VSAM_NAMES:
#             create_vsam_ksds(vsam, hosts)
#         find_res = hosts.all.zos_find(patterns=['TEST.FIND.VSAM.*.*'])
#         for val in find_res.contacted.values():
#             assert len(val.get('data_sets')) == 1
#             assert val.get('matched') == len(val.get('data_sets'))
#     finally:
#         hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in VSAM_NAMES])


# def test_find_vsam_in_volume(ansible_zos_module):
#     hosts = ansible_zos_module
#     alternate_vsam = "TEST.FIND.ALTER.VSAM"
#     try:
#         for vsam in VSAM_NAMES:
#             create_vsam_ksds(vsam, hosts, volume="222222")
#         create_vsam_ksds(alternate_vsam, hosts, volume="000000")
#         find_res = hosts.all.zos_find(patterns=['TEST.FIND.*.*.*'], volumes=['222222'])
#         for val in find_res.contacted.values():
#             assert len(val.get('data_sets')) == 1
#             assert val.get('matched') == len(val.get('data_sets'))
#     finally:
#         hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in VSAM_NAMES])
#         hosts.all.zos_data_set(name=alternate_vsam, state='absent')


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
