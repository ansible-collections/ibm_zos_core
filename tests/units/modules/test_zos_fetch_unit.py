# -*- coding: utf-8 -*-

# Copyright (c) 2019, 2020 Asif Mahmud <asif.mahmud@ibm.com>
# Copyright (c) 2020 Blake Becker <blake.becker@ibm.com>
# Copyright (c) IBM Corporation 2020
# LICENSE: [GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.module_utils.basic import AnsibleModule
from mock import call, mock_open, patch 

MODULE_IMPORT = "ansible_collections_ibm_zos_core.plugins.modules.zos_fetch"
BASIC_MODULE = 'ansible.module_utils.basic.AnsibleModule'

# Test fetch USS file
test_data = [
    ('/path/to/file.txt', True, False),
    ('/path/to/file.log', False, False)
]

@pytest.mark.parametrize("src,validate_checksum,is_binary", test_data)
def test_fetch_uss_file(zos_import_mocker, src, validate_checksum, is_binary):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    with patch(MODULE_IMPORT + '.open', mock_open(), create=True):
        module._fetch_uss_file(src, validate_checksum, is_binary)
    
    assert patched_method.call_count == 0


# Test fetch z/OS data set
test_data = [
    ('some.data.set', True, 'dummy data', 0),
    ('some.data.set', False, None, 1)
]

@pytest.mark.parametrize("zos_data_set,is_binary,return_value,expected", test_data)
def test_fetch_zos_data_set(zos_import_mocker, zos_data_set, is_binary, return_value, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    mocker.patch('zoautil_py.Datasets.read', create=True, return_value=return_value)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    module._fetch_zos_data_set(zos_data_set, is_binary)
    assert patched_method.call_count == expected


test_data = [
    ('test1.test.test2', (0,'PS',''), 0),
    ('test.test1.test2', (1,'NOT IN CATALOG',''), 0),
    ('test.test1.test2', (-1,'INVALID DATA SET NAME',''), 0),
    ('test.test1.test2', (-1,'garbage',''), 1)
]

@pytest.mark.parametrize("ds_name,return_value,expected", test_data)
def test_determine_data_set_type(zos_import_mocker, ds_name, return_value, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    mocker.patch(MODULE_IMPORT + '._run_command', create=True, return_value=return_value)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    try:
        module._determine_data_set_type(ds_name)
    except module.UncatalogedDatasetError:
        pass
    assert patched_method.call_count == expected


test_data = [
    ('test1.test.test2', 'temp.data.set', 'dummy data', 0, 0),
    ('test1.test.test2', 'temp.data.set', None, 0, 1),
    ('test1.test.test2', 'temp.data.set', 'dummy data', 2, 1)
]

@pytest.mark.parametrize("src,temp_ds,content,del_rc,expected", test_data)
def test_fetch_vsam(zos_import_mocker, src, temp_ds, content, del_rc, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    mocker.patch(MODULE_IMPORT + '._copy_vsam_to_temp_data_set', create=True, return_value=temp_ds)
    mocker.patch(MODULE_IMPORT + '._fetch_zos_data_set', create=True, return_value=content)
    mocker.patch('zoautil_py.Datasets.delete', create=True, return_value=del_rc)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    module._fetch_vsam(src, True, True)
    assert patched_method.call_count == expected



test_data = [
    ('test1.test.test2', False, (0,'',''), 0),
    ('test1.test.test2(member)', True, (1,'','stderr'), 1)
]

@pytest.mark.parametrize("src,fetch_member,return_value,expected", test_data)
def test_fetch_pdse(zos_import_mocker, src, fetch_member, return_value, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    mocker.patch(MODULE_IMPORT + '._run_command', create=True, return_value=return_value)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    module._fetch_pdse(src, True, fetch_member)
    assert patched_method.call_count == expected


test_data = [
    ('test1.test.test2', 'dummy data', 0),
    ('test1.test.test2', None, 1)
]
@pytest.mark.parametrize("src,return_value,expected", test_data)
def test_fetch_ps(zos_import_mocker, src, return_value, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    mocker.patch(MODULE_IMPORT + '._fetch_zos_data_set', create=True, return_value=return_value)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    module._fetch_ps(src, True, True)
    assert patched_method.call_count == expected


test_data = [
    ('USER.TEST.SEQ', True),
    ('USER.ABCDEFGJSJSJSJS.SEQ', False),
    ('ABC.123.XYZ', False),
    ('ABC..XYZ', False),
    ('1DATA.HELLO', False)
]
@pytest.mark.parametrize("src,expected", test_data)
def test_validate_dsname(zos_import_mocker, src, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    assert module._validate_dsname(src) == expected


test_data = [
    ('TESTER.TEST.TEST1', False, 'ASCII', True, None, False, 0),
    ('TESTER.TEST.TEST1', True, 'EBCDIC', True, None, False, 1),
    ('TESTER.TEST.TEST1', True, 'dummy_enc', True, None, False, 1),
    ('TESTER.TEST.TEST1', True, 'EBCDIC', False, None, False, 1),
    ('TESTER.TEST.TEST1', True, 'EBCDIC', True, None, False, 1),
    ('1TESTER.TEST.TEST1', True, 'EBCDIC', True, None, False, 1),
]

@pytest.mark.parametrize("src,is_binary,encoding,is_catalog,volume,is_uss,expected", test_data)
def test_validate_params(zos_import_mocker, src, is_binary, encoding, is_catalog, volume, is_uss, expected):
    mocker, importer = zos_import_mocker
    module = importer(MODULE_IMPORT)
    patched_method = mocker.patch(MODULE_IMPORT + '._fail_json', create=True)
    module._validate_params(src, is_binary, encoding, is_catalog, volume, is_uss)
    assert patched_method.call_count == expected



    

