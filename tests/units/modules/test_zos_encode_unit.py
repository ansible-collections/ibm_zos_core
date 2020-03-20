# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

import sys
import pytest
from unittest.mock import MagicMock, Mock
from unittest import mock
from pytest_mock import mocker

IMPORT_NAME = 'ibm_zos_core.plugins.modules.zos_encode'

cp1_cmd_return = [
    (0, '', ''),
    (1, '', '*')
]

cp2_cmd_return = [
    (0, '', ''),
    (1, '', 'EDC5061I'),
    (1, '', '*')
]

run_rexx_return = [
    (0, 'NONVSAM', ''),
    (0, 'VSAM', ''),
    (255, 'NONVSAM', 'BPXW9018I'),
    (255, 'VSAM', 'BPXW9018I'),
    (1, '', '*')
]

test_data_set = [
    ('ZLBJLU.TEST.PS', run_rexx_return[0], True),
    ('ZLBJLU.TEST1.VS', run_rexx_return[1], True),
    ('ZLBJLU.TEST.PDS', run_rexx_return[2], True),
    ('ZLBJLU.TEST2.VS', run_rexx_return[3], True),
    ('ZLBJLU.TEST3.PS', run_rexx_return[4], True)
]

check_mvs_data = [
    ('ZLBJLU.TEST.PS', (True, 'NONVSAM'), run_rexx_return[0], True),
    ('ZLBJLU.TEST.VS', (True, 'VSAM'), run_rexx_return[1], True),
    ('ZLBJLU.TEST3.PS',(False, ''), run_rexx_return[4], True)
]

test_pds_member = [
     ('ZLBJLU.TEST.PDS', 'TEST', 'TEST\nTEST1\n', True),
     ('ZLBJLU.TEST.PDS', 'TEST1','TEST\nTEST2\n', True)
]

mvs_convert_data = [
    ('ZLBJLU.TEST.PS', 'ZLBJLU.TEST.PS', 'EBCDIC', 'ASCII', cp1_cmd_return[0], (True, ''), cp2_cmd_return[0],True),
    ('ZLBJLU.TEST.PS', 'ZLBJLU.TEST.PS', 'ASCII', 'EBCDIC', cp1_cmd_return[0], (False, '*'), cp2_cmd_return[0], True),
    ('ZLBJLU.TEST.PS', 'ZLBJLU.TEST.PS', 'EBCDIC', 'ASCII', cp1_cmd_return[0], (True, '*'), cp2_cmd_return[1], True),
    ('ZLBJLU.TEST.PS', 'ZLBJLU.TEST.PS', 'ASCII', 'EBCDIC', cp1_cmd_return[0], (True, '*'), cp2_cmd_return[2], True),
    ('ZLBJLU.TEST.PS', 'ZLBJLU.TEST1.PS', 'ASCII', 'EBCDIC', cp1_cmd_return[1], (1, ''), cp2_cmd_return[2], True)
]

uss_convert_data = [
    ('/u/test', '/u/test', 'EBCDIC', 'ASCII', cp1_cmd_return[1], cp2_cmd_return[2],True),
    ('/u/test', '/u/test1', 'ASCII', 'EBCDIC', cp1_cmd_return[0], cp2_cmd_return[0], True),
    ('/u/test1', '/u/test1', 'EBCDIC', 'ASCII', cp1_cmd_return[0], cp2_cmd_return[2], True),
]

@pytest.mark.parametrize("file, return_value, cmd_return, expected", check_mvs_data)
def test_check_mvs_dataset(zos_import_mocker, file, return_value, cmd_return, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    passed = True
    module = Mock()
    module.run_command = Mock(return_value = cmd_return)
    mocker.patch('{0}.data_set_exists'.format(IMPORT_NAME), create=True, return_value=return_value)    
    try:
        ds.check_mvs_dataset(file, module)
    except:
        passed = False
    assert passed == expected

@pytest.mark.parametrize("src, return_value, expected", test_data_set)
def test_data_set_exists(zos_import_mocker, src, return_value, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    passed = True
    module = Mock()
    module.run_command = Mock(return_value = return_value)
    mocker.patch('{0}.run_rexx'.format(IMPORT_NAME), create=True, return_value = return_value)    
    try:
        ds.data_set_exists(src, module)
    except:
        passed = False
    assert passed == expected

@pytest.mark.parametrize("pds, member, return_value, expected", test_pds_member)
def test_check_pds_member(zos_import_mocker, pds, member, return_value, expected):
    mocker, importer = zos_import_mocker
    ds = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.Datasets.list_members', create=True, return_value=return_value)
    try:
        ds.check_pds_member(pds, member)
    except:
        passed = False
    assert passed == expected

@pytest.mark.parametrize("src, dest, from_encoding, to_encoding, cp1_return_value, uss_return_value, cp2_return_value, expected", mvs_convert_data)
def test_mvs_convert_encoding(zos_import_mocker, src, dest, from_encoding, to_encoding, cp1_return_value, uss_return_value, cp2_return_value, expected):
    mocker, importer = zos_import_mocker
    conv = importer(IMPORT_NAME)
    passed = True
    module = Mock()
    return_values = [cp1_return_value, cp2_return_value]
    module.run_command = Mock(return_value=return_values[module.run_command.call_count-1])
    try:
        conv.mvs_convert_encoding(src, dest, from_encoding, to_encoding, module)
    except:
        passed = False
    assert passed == expected

@pytest.mark.parametrize("src, dest, from_encoding, to_encoding, cp1_return_value, cp2_return_value, expected", uss_convert_data)
def test_uss_convert_encoding(zos_import_mocker, src, dest, from_encoding, to_encoding, cp1_return_value, cp2_return_value, expected):
    mocker, importer = zos_import_mocker
    conv = importer(IMPORT_NAME)
    passed = True
    module = Mock()
    return_values = [cp1_return_value, cp2_return_value]
    module.run_command = Mock(return_value=return_values[module.run_command.call_count-1])
    try:
        conv.mvs_convert_encoding(src, dest, from_encoding, to_encoding, module)
    except:
        passed = False
    assert passed == expected

