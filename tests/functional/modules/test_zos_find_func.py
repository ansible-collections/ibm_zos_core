# -*- coding: utf-8 -*-

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

def test_find_sequential_data_sets_containing_single_string(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "hello"
    try:
        hosts.all.zos_data_set(batch=[dict(name=i, type='seq', state='present') for i in SEQ_NAMES])
        for ds in SEQ_NAMES:
            hosts.all.zos_lineinfile(src=ds, line=search_string)

        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], contains=search_string)
        for val in find_res.contacted.values():
            assert val.get('data_sets') is not None
            for ds in val.get('data_sets').keys():
                assert ds in SEQ_NAMES
            assert val.get('matched') == len(SEQ_NAMES)
    finally:
        hosts.all.zos_data_set(batch=[dict(name=i, state='absent') for i in SEQ_NAMES])


def test_find_sequential_data_sets_multiple_patterns(ansible_zos_module):
    hosts = ansible_zos_module
    search_string = "dummy string"
    new_ds ="TEST.FIND.SEQ.FUNCTEST.FOURTH"
    try:
        for ds in SEQ_NAMES:
            hosts.all.zos_data_set(name=ds, type='seq', state='present')
            hosts.all.zos_lineinfile(src=ds, line=search_string)
        hosts.all.zos_data_set(name=new_ds, type='seq', state='present')
        hosts.all.zos_lineinfile(src=new_ds, line="incorrect string")
        
        find_res = hosts.all.zos_find(
            patterns=['TEST.FIND.SEQ.*.*', "TEST.INVALID.*"],
            contains=search_string
        )
        for val in find_res.contacted.values():
            for ds in val.get('data_sets').keys():
                assert ds in SEQ_NAMES
            assert val.get('matched') == len(SEQ_NAMES)
    finally:
        for ds in SEQ_NAMES:
            hosts.all.zos_data_set(name=ds, state='absent')
        hosts.all.zos_data_set(name=new_ds, state='absent')


def test_find_pds_members_containing_string(ansible_zos_module):
    pass


def test_exclude_data_sets_from_matched_list(ansible_zos_module):
    pass


def test_exclude_members_from_matched_list(ansible_zos_module):
    pass


def test_find_data_sets_older_than_age(ansible_zos_module):
    pass


def test_find_data_sets_younger_than_age(ansible_zos_module):
    pass


def test_find_data_sets_larger_than_size(ansible_zos_module):
    pass


def test_find_data_sets_smaller_than_size(ansible_zos_module):
    pass


def test_find_data_sets_in_volume(ansible_zos_module):
    pass


def test_find_data_sets_in_multiple_volumes(ansible_zos_module):
    pass


def test_find_vsam_in_volume(ansible_zos_module):
    pass
