# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from typing_extensions import final

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
        for ds in SEQ_NAMES:
            hosts.all.zos_data_set(name=ds, type='seq', state='present')
            hosts.all.zos_lineinfile(src=ds, line=search_string)
    
        find_res = hosts.all.zos_find(patterns=['TEST.FIND.SEQ.*.*'], contains=search_string)
        for val in find_res.contacted.values():
            for ds in val.get('data_sets').keys():
                assert ds in SEQ_NAMES
            assert val.get('matched') == len(SEQ_NAMES)
    finally:
        for ds in SEQ_NAMES:
            hosts.all.zos_data_set(name=ds, state='absent')
    

def test_find_sequential_data_sets_multiple_patterns():
    pass


def test_find_pds_members_containing_string():
    pass


def test_exclude_data_sets_from_matched_list():
    pass


def test_exclude_members_from_matched_list():
    pass


def test_find_data_sets_older_than_age():
    pass


def test_find_data_sets_younger_than_age():
    pass


def test_find_data_sets_larger_than_size():
    pass


def test_find_data_sets_smaller_than_size():
    pass


def test_find_data_sets_in_volume():
    pass


def test_find_data_sets_in_multiple_volumes():
    pass


def test_find_vsam_in_volume():
    pass
