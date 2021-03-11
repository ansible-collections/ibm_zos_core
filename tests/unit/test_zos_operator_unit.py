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
IMPORT_NAME = "ibm_zos_core.plugins.modules.zos_operator"


# * Tests for zos_operator

dummy_dict1 = {
    "verbose": False,
}

dummy_dict2 = {
    "cmd": 123,
    "verbose": True,
}

dummy_dict3 = {"cmd": "d u,all"}

dummy_dict4 = {"cmd": "d u,all", "verbose": True}

dummy_dict5 = {"cmd": "d u,all", "verbose": "NotTrueOrFalse"}

dummy_return_dict1 = {"rc": 0, "message": "good result"}

dummy_return_dict2 = {"rc": 1, "message": None}

test_data = [
    (dummy_dict1, False),
    (dummy_dict2, False),
    (dummy_dict3, True),
    (dummy_dict4, True),
    (dummy_dict5, False),
]


@pytest.mark.parametrize("args,expected", test_data)
def test_zos_opreator_various_args(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    zos_operator = importer(IMPORT_NAME)
    passed = True
    try:
        zos_operator.parse_params(args)
    except Exception as e:
        passed = False
    assert passed == expected
