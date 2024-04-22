# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
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

from ibm_zos_core.plugins.module_utils.data_set import (
    DataSet
)

import pytest

gds_test_data = [
    {"name": "USER.GDG(+1)", "valid_gds" : True},
    {"name": "USER.GDG(-3)", "valid_gds" : True},
    {"name": "USER.GDG(0)", "valid_gds" : True},
    {"name": "USER.GDG(+22)", "valid_gds" : True},
    {"name": "USER.GDG(-33)", "valid_gds" : True},
    {"name": "USER.GDG(MEMBER)", "valid_gds" : False},
    {"name": "USER.GDG.TEST", "valid_gds" : False},
    ]

@pytest.mark.parametrize("gds", gds_test_data)
def test_gds_valid_name(gds):
    # The 'is_zoau_version_higher_than' function calls 'get_zoau_version_str' to
    # get the ZOAU version string from the system. We mock that call and provide
    # our own "system" level ZOAU version str to compare against our provided
    # minimum ZOAU version string.
    print(gds)

    assert gds["valid_gds"] == DataSet.is_gds_relative_name(gds["name"])
