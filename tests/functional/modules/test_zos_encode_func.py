# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
from shellescape import quote
from pprint import pprint
from os import path, remove
import tempfile

__metaclass__ = type

uss_file = '/tmp/encode.data'
uss_none_file = '/tmp/none'
uss_dest_file = '/tmp/converted.data'
uss_path = '/tmp/src/path'
uss_dest_path = '/tmp/dest/path'
mvs_ps = 'encode.ps'
mvs_vps = 'encode.vvps'
mvs_none_ps = 'encode.none.ps'
mvs_pds = 'encode.pds'
mvs_pds_member = 'encode.pds(test)'
mvs_vs = 'encode.vs'
from_encoding = 'IBM-1047'
invalid_encoding = 'EBCDIC'
to_encoding = 'ISO8859-1'
test_data = '''00000001This is for encode conversion testsing
00000002This is for encode conversion testsing
00000003This is for encode conversion testsing
00000004This is for encode conversion testsing
'''


def test_uss_encoding_conversion_with_invalid_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src=uss_file,
        from_encoding=invalid_encoding,
        to_encoding=to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') is None
        assert result.get('backup_file') is None
        assert result.get('changed') is False
        assert result.get('msg') == ("Invalid codeset: Please check the value "
                                     "of the from_encoding!")


def test_uss_encoding_conversion_with_the_same_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src=uss_file,
        from_encoding=from_encoding,
        to_encoding=from_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') is None
        assert result.get('backup_file') is None
        assert result.get('changed') is False
        assert result.get('msg') == ("The value of the from_encoding and to_encoding "
                                     "are the same, no need to do the conversion!")


def test_uss_encoding_conversion_without_dest(ansible_zos_module):
   hosts = ansible_zos_module
   hosts.all.copy(content=test_data, dest=uss_file)
   results = hosts.all.zos_encode(
       src=uss_file,
       from_encoding=from_encoding,
       to_encoding=to_encoding
   )
   hosts.all.file(path=uss_file, state="absent")
   pprint(vars(results))
   for result in results.contacted.values():
       assert result.get('src') == uss_file
       assert result.get('dest') == uss_file
       assert result.get('backup_file') is None
       assert result.get('changed') is True


def test_uss_encoding_conversion_when_dest_not_exists_01(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=test_data, dest=uss_file)
    hosts.all.file(path=uss_none_file, state="absent")
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=uss_none_file,
        from_encoding=from_encoding,
        to_encoding=to_encoding,
        backup=True
    )
    hosts.all.file(path=uss_file, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_none_file
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_when_dest_not_exists_02(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=mvs_ps, state="present", type="seq"
    )
    hosts.all.zos_data_set(
        name=mvs_none_ps, state="absent"
    )
    results = hosts.all.zos_encode(
        src=mvs_ps,
        dest=mvs_none_ps,
        from_encoding=from_encoding,
        to_encoding=to_encoding,
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_ps
        assert result.get('dest') == mvs_none_ps
        assert result.get('backup_file') == None
        assert result.get('changed') == False
   

def test_uss_encoding_conversion_uss_USS_file_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=test_data, dest=uss_file)
    hosts.all.copy(content='test', dest=uss_dest_file)
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=uss_dest_file,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    hosts.all.file(path=uss_file, state="absent")
    hosts.all.file(path=uss_dest_file, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_file_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=uss_dest_path, state="directory")
    hosts.all.copy(content=test_data, dest=uss_file)
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=uss_dest_path,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    hosts.all.file(path=uss_file, state="absent")
    hosts.all.file(path=uss_dest_path, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_path_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=uss_path, state="directory")
    hosts.all.copy(content=test_data, dest=uss_path+'/encode1')
    hosts.all.copy(content=test_data, dest=uss_path+'/encode2')
    hosts.all.file(path=uss_dest_path, state="directory")
    results = hosts.all.zos_encode(
        src=uss_path,
        dest=uss_dest_path,
        from_encoding=to_encoding,
        to_encoding=from_encoding,
        backup=True
    )
    hosts.all.file(path=uss_path, state="absent")
    hosts.all.file(path=uss_dest_path, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_path
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') is not None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_file_to_MVS_ps(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=test_data, dest=uss_file)
    hosts.all.zos_data_set(
        name=mvs_ps, state="present", type="seq"
    )
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=mvs_ps,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_ps
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_MVS_PS_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content='test', dest=uss_dest_file)
    results = hosts.all.zos_encode(
        src=mvs_ps,
        dest=uss_dest_file,
        from_encoding=from_encoding,
        to_encoding=to_encoding,
        backup=True
    )
    hosts.all.file(path=uss_dest_file, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_ps
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') is not None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_file_to_MVS_PDS(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=test_data, dest=uss_file)
    hosts.all.zos_data_set(
        name=mvs_pds,
        state="present",
        type="pds",
        record_length=50
    )
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=mvs_pds,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_pds
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_file_to_MVS_PDS_member(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content=test_data, dest=uss_file)
    hosts.all.zos_data_set(
        name=mvs_pds,
        state="present",
        type="pds",
        record_length=80
    )
    hosts.all.zos_data_set(
        name=mvs_pds_member, type="member"
    )
    results = hosts.all.zos_encode(
        src=uss_file,
        dest=mvs_pds_member,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    hosts.all.file(path=uss_file, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_pds_member
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_MVS_PDS_member_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.copy(content='test', dest=uss_dest_file)
    results = hosts.all.zos_encode(
        src=mvs_pds_member,
        dest=uss_dest_file,
        from_encoding=from_encoding,
        to_encoding=to_encoding,
        backup=True
    )
    hosts.all.file(path=uss_dest_file, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_pds_member
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') is not None
        assert result.get('changed') is True


def test_uss_encoding_conversion_USS_path_to_MVS_PDS(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=uss_path, state="directory")
    hosts.all.copy(content=test_data, dest=uss_path+'/encode1')
    hosts.all.copy(content=test_data, dest=uss_path+'/encode2')
    hosts.all.zos_data_set(
        name=mvs_pds,
        state="present", 
        type="pds",
        record_length=80
    )
    results = hosts.all.zos_encode(
        src=uss_path,
        dest=mvs_pds,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    hosts.all.file(path=uss_path, state="absent")
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_path
        assert result.get('dest') == mvs_pds
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_MVS_PDS_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.file(path=uss_dest_path, state="directory")
    results = hosts.all.zos_encode(
        src=mvs_pds,
        dest=uss_dest_path,
        from_encoding=to_encoding,
        to_encoding=from_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_pds
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') is None
        assert result.get('changed') is True


def test_uss_encoding_conversion_MVS_PS_to_MVS_PDS_member(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src=mvs_ps,
        dest=mvs_pds_member,
        from_encoding=from_encoding,
        to_encoding=to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_ps
        assert result.get('dest') == mvs_pds_member
        assert result.get('backup_file') is None
        assert result.get('changed') is True
