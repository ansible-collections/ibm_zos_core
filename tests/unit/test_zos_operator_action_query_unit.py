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
IMPORT_NAME = "ibm_zos_core.plugins.modules.zos_operator_action_query"


# * Tests for zos_operator_action_query

dummy_dict1 = {}

dummy_dict2 = {"system": "mv2c"}


dummy_dict3 = {"message_id": "DFH*"}

dummy_dict4_uppercase = {"message_id": "DFH*", "system": "MV28"}

dummy_dict4_lowercase = {"message_id": "DFH*", "system": "mv28"}

dummy_dict5 = {"message_filter": {"filter": "^.*IMS.*$", "use_regex": True}}

dummy_dict6 = {"system": "mv27", "message_id": "DFS*", "job_name": "IM5H*", "message_filter": {"filter": "IMS"}}

dummy_dict_invalid_message = {"message_id": "$$#$%#"}
dummy_dict_invalid_filter = {"message_filter": {"filter": "*IMS", "use_regex": True}}
dummy_dict_invalid_job_name = {"job_name": "IM5H123456"}
dummy_dict_invalid_system = {"system": "mv2712345"}


test_data = [
    (dummy_dict1, True),
    (dummy_dict2, True),
    (dummy_dict3, True),
    (dummy_dict4_uppercase, True),
    (dummy_dict4_lowercase, True),
    (dummy_dict5, True),
    (dummy_dict6, True),
    (dummy_dict_invalid_message, False),
    (dummy_dict_invalid_filter, False),
    (dummy_dict_invalid_job_name, False),
    (dummy_dict_invalid_system, False),
]


@pytest.mark.parametrize("args,expected", test_data)
def test_zos_operator_action_query_various_args(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    zos_operator_action_query = importer(IMPORT_NAME)
    passed = True
    try:
        zos_operator_action_query.parse_params(args)
    except Exception:
        passed = False
    assert passed == expected
