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
IMPORT_NAME = "ibm_zos_core.plugins.modules.zos_ickdsf_init"


# * Tests for zos_ickdsf_init

no_volume_addr = { 'volume_address' : None }
invalid_vol_addr = {'volume_address' : '$$$' }

default_opts = {
    'volume_address' : '0903',
    'verify_offline' : True,
    'verify_existing_volid' : None,
    'volid' : None,
    'vtoc_tracks' : None,
    'index' : True,
    'verify_no_data_sets_exist' : True,
    'sms_managed' : True,
    'addr_range' : None,
    'volid_prefix' : None,

}
default_opts_cmd = [" init unit(0903) noverify verifyoffline  - ", "  storagegroup nods "]

# dummy_dict4 = {
    # 'volume_address' : '0903',
    # 'verify_offline' : False,
    # 'volid': "KTN003",
    # 'index': True,
    # 'verify_no_data_sets_exist': True,
# }
# dummy_command_4 = [' init unit(0903) noverify noverifyoffline volid(KTN003) - ', '   nods ']

# dummy_dict5 = {
    # 'volume_address' : '0903',
    # 'verify_offline' : True,
    # 'volid': "KTN003",
    # 'index': True,
    # 'verify_no_data_sets_exist': False,
# }
# dummy_command_5 = [' init unit(0903) noverify verifyoffline volid(KTN003) - ', '   ds ']

bad_test_data = [
    (no_volume_addr, 'Volume address must be defined'),
    (invalid_vol_addr, 'Volume address must be a valid 64-bit hex value'),
]

all_test_data = [
    (no_volume_addr, 'Volume address must be defined'),
    (invalid_vol_addr, 'Volume address must be a valid 64-bit hex value'),
    (default_opts, default_opts_cmd),
    # (dummy_dict4, dummy_command_4),
    # (dummy_dict5, dummy_command_5),
]

@pytest.mark.parametrize("args,expected", all_test_data)
def test_zos_ickdsf_init_convert_happy(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    zos_ickdsf_init = importer(IMPORT_NAME)
    actual = None
    try:
        actual = zos_ickdsf_init.CommandInit.convert(args)
    except Exception as e:
        actual = str(e)
    assert actual == expected

@pytest.mark.parametrize("args,expected", bad_test_data)
def test_zos_ickdsf_init_convert_unhappy(zos_import_mocker, args, expected):

    mocker, importer = zos_import_mocker
    zos_ickdsf_init = importer(IMPORT_NAME)
    with pytest.raises(zos_ickdsf_init.IckdsfError) as ickdsf_error:
        zos_ickdsf_init.CommandInit.convert(args)
    assert str(ickdsf_error.value) == expected
    