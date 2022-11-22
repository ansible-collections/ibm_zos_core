# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
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

from ansible.module_utils.basic import AnsibleModule
import pytest
import sys
from mock import call

# Used my some mock modules, should match import directly below
IMPORT_NAME = "ibm_zos_core.plugins.modules.zos_ickdsf_command"


# * Tests for zos_ickdsf_command

dummy_dict1 = {
    "init": { 'volume_address' : None },
}

dummy_dict2 = {
    "init": { 'volume_address' : '$$$' },
}

dummy_dict3 = {
    "init": {
        'volume_address' : '0903',
        'verify_offline' : False,
        'volid': "KTN003",
        'index': True,
        'verify_no_data_sets_exist': False,
        }
}
dummy_command_3 = [' init unit(0903) noverify noverifyoffline volid(KTN003) - ', '   ds ']

dummy_dict4 = {
    "init": {
        'volume_address' : '0903',
        'verify_offline' : False,
        'volid': "KTN003",
        'index': True,
        'verify_no_data_sets_exist': True,
        }
}
dummy_command_4 = [' init unit(0903) noverify noverifyoffline volid(KTN003) - ', '   nods ']

bad_test_data = [
    (dummy_dict1, 'Volume address must be defined'),
    (dummy_dict2, 'Volume address must be a valid 64-bit hex value'),
]

dummy_dict5 = {
    "init": {
        'volume_address' : '0903',
        'verify_offline' : True,
        'volid': "KTN003",
        'index': True,
        'verify_no_data_sets_exist': False,
        }
}
dummy_command_5 = [' init unit(0903) noverify verifyoffline volid(KTN003) - ', '   ds ']


test_data = [
    (dummy_dict1, 'Volume address must be defined'),
    (dummy_dict2, 'Volume address must be a valid 64-bit hex value'),
    (dummy_dict3, dummy_command_3),
    (dummy_dict4, dummy_command_4),
    (dummy_dict5, dummy_command_5),
]


from pprint import pprint

@pytest.mark.parametrize("args,expected", test_data)
def test_zos_ickdsf_command_init_convert_happy(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    zos_ickdsf_command = importer(IMPORT_NAME)
    actual = None
    try:
        actual = zos_ickdsf_command.CommandInit.convert(args)
    except Exception as e:
        actual = str(e)
    assert actual == expected

@pytest.mark.parametrize("args,expected", bad_test_data)
def test_zos_ickdsf_command_init_convert_unhappy(zos_import_mocker, args, expected):

    mocker, importer = zos_import_mocker
    zos_ickdsf_command = importer(IMPORT_NAME)
    with pytest.raises(zos_ickdsf_command.IckdsfError) as ickdsf_error:
        zos_ickdsf_command.CommandInit.convert(args)
    assert str(ickdsf_error.value) == expected
