# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division
from shellescape import quote
from pprint import pprint
import tempfile

__metaclass__ = type

uss_file         = '/u/zlbjlu/zos_encode/ebcdic.txt'
uss_none_file    = '/u/zlbjlu/zos_encode/none'
uss_dest_file    = '/u/zlbjlu/zos_encode_out/ascii.txt'
uss_path         = '/u/zlbjlu/zos_encode'
uss_dest_path    = '/u/zlbjlu/zos_encode_out'
mvs_ps           = 'zlbjlu.zoautest.ps'
mvs_vps          = 'zlbjlu.zoautest.vvps'
mvs_none_ps      = 'zlbjlu.zoautest.none.ps'
mvs_pds          = 'zlbjlu.zoautest.pds'
mvs_pds_member   = 'zlbjlu.zoautest.pds(test)'
mvs_vs           = 'zlbjlu.zoautest.vs'
from_encoding    = 'IBM-1047'
invalid_encoding = 'EBCDIC'
to_encoding      = 'ISO8859-1'

def test_uss_encoding_conversion_with_invalid_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        from_encoding = invalid_encoding, 
        to_encoding   = to_encoding,
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == None
        assert result.get('backup_file') == None
        assert result.get('changed') == False
        assert result.get('msg') == ("Invalid codeset: Please check the value "
            "of the from_encoding!")

def test_uss_encoding_conversion_with_the_same_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        from_encoding = from_encoding, 
        to_encoding   = from_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == None
        assert result.get('backup_file') == None
        assert result.get('changed') == False
        assert result.get('msg') == ("The value of the from_encoding and to_encoding "
            "are the same, no need to do the conversion!")

def test_uss_encoding_conversion_without_dest(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_file
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_when_dest_not_exists_01(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = uss_none_file,
        from_encoding = from_encoding, 
        to_encoding   = to_encoding, 
        backup        = True
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_none_file
        assert result.get('backup_file') == None
        assert result.get('changed') == True

# def test_uss_encoding_conversion_when_dest_not_exists_02(ansible_zos_module):
    # hosts = ansible_zos_module
    # results = hosts.all.zos_encode(
        # src           = mvs_ps, 
        # dest          = mvs_none_ps,
        # from_encoding = from_encoding, 
        # to_encoding   = to_encoding, 
    # )
    # pprint(vars(results))
    # for result in results.contacted.values():
        # assert result.get('src') == mvs_ps
        # assert result.get('dest') == mvs_none_ps
        # assert result.get('backup_file') == None
        # assert result.get('changed') == False

def test_uss_encoding_conversion_uss_USS_file_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = uss_dest_file, 
        from_encoding = from_encoding, 
        to_encoding   = to_encoding)
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') == None
        assert result.get('changed') == True
       
def test_uss_encoding_conversion_USS_file_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = uss_dest_path, 
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_path_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_path, 
        dest          = uss_dest_path, 
        from_encoding = from_encoding, 
        to_encoding   = to_encoding, 
        backup        = True
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_path
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') != None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_file_to_MVS_ps(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = mvs_ps, 
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_ps
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_PS_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_ps, 
        dest          = uss_dest_file,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding,
        backup        = True
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_ps
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') != None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_file_to_MVS_PDS(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = mvs_pds,
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_pds
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_file_to_MVS_PDS_member(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = mvs_pds_member,
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_pds_member
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_path_to_MVS_PDS(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_path, 
        dest          = mvs_pds,
        from_encoding = from_encoding, 
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_path
        assert result.get('dest') == mvs_pds
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_USS_file_to_MVS_VSAM(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = uss_file, 
        dest          = mvs_vs,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == uss_file
        assert result.get('dest') == mvs_vs
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_PDS_member_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_pds_member, 
        dest          = uss_dest_file,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding,
        backup        = True
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_pds_member
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') != None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_PDS_to_USS_path(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_pds, 
        dest          = uss_dest_path,
        from_encoding = from_encoding,
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_pds
        assert result.get('dest') == uss_dest_path
        assert result.get('backup_file') == None
        assert result.get('changed') == True
        
def test_uss_encoding_conversion_MVS_VSAM_to_USS_file(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_vs, 
        dest          = uss_dest_file,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding,
        backup        = True
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_vs
        assert result.get('dest') == uss_dest_file
        assert result.get('backup_file') != None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_VSAM_to_MVS_PS(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_vs, 
        dest          = mvs_ps,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_vs
        assert result.get('dest') == mvs_ps
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_PS_to_MVS_PDS_member(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_ps, 
        dest          = mvs_pds_member,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_ps
        assert result.get('dest') == mvs_pds_member
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_VSAM_to_MVS_PDS_member(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_vs, 
        dest          = mvs_pds_member,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_vs
        assert result.get('dest') == mvs_pds_member
        assert result.get('backup_file') == None
        assert result.get('changed') == True

def test_uss_encoding_conversion_MVS_PS_to_MVS_VSAM(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_encode(
        src           = mvs_vps, 
        dest          = mvs_vs,
        from_encoding = from_encoding,        
        to_encoding   = to_encoding
    )
    pprint(vars(results))
    for result in results.contacted.values():
        assert result.get('src') == mvs_vps
        assert result.get('dest') == mvs_vs
        assert result.get('backup_file') == None
        assert result.get('changed') == True
