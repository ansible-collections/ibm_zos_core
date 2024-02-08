# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2022 - 2024
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

from ibm_zos_core.plugins.modules.zos_gather_facts import flatten_zinfo_json

__metaclass__ = type

import pytest

# Used my some mock modules, should match import directly below
IMPORT_NAME = "ibm_zos_core.plugins.modules.zos_gather_facts"

# Tests for zos_father_facts helper functions

test_data = [
    (["ipl"], ["ipl"]),
    (["ipl  "], ["ipl"]),
    (["  ipl"], ["ipl"]),
    (["ipl", "sys"], ["ipl", "sys"]),
    (["all"], ["all"]),
    (None, ["all"]),
    (["ipl", "all", "sys"], ["all"]),
    # function does not validate legal vs illegal subsets
    (["asdf"], ["asdf"]),
    ([""], None),
    (["ipl; cat /.bashrc"], None),  # attemtped injection
    # for now, 'all' with some other invalid subset resolves to 'all'
    (["ipl", "all", "ipl; cat /.ssh/id_rsa"], ["all"]),
]


@pytest.mark.parametrize("args,expected", test_data)
def test_zos_gather_facts_zinfo_facts_list_builder(
        zos_import_mocker, args, expected):

    mocker, importer = zos_import_mocker
    zos_gather_facts = importer(IMPORT_NAME)

    try:
        result = zos_gather_facts.zinfo_facts_list_builder(args)
        # add more logic here as the function evolves.
    except Exception:
        result = None
    assert result == expected


test_data = [
    (
        {'x': {'a': 'aa', 'b': 'bb', 'c': 'cc'},
            'y': {'d': True}},
        {'a': 'aa', 'b': 'bb', 'c': 'cc', 'd': True}
    ),
    ({}, {})
]


@pytest.mark.parametrize("args,expected", test_data)
def test_zos_gather_facts_flatten_zinfo_json(
        zos_import_mocker, args, expected):

    mocker, importer = zos_import_mocker
    zos_gather_facts = importer(IMPORT_NAME)

    try:
        result = zos_gather_facts.flatten_zinfo_json(args)
    except Exception:
        result = None
    assert result == expected


test_data = [
    # actual dict, filter_list, expected dict

    # empty filter list
    ({'a': 1, 'b': 2}, [], {'a': 1, 'b': 2}),
    # filter with * at end
    (
        {'dog_1': 1, 'dog_2': 2, 'cat_1': 1, 'cat_2': 2},
        ['dog*'],
        {'dog_1': 1, 'dog_2': 2}
    ),
    # filter with * at front
    (
        {'dog_1': 1, 'dog_2': 2, 'cat_1': 1, 'cat_2': 2},
        ['*_2'],
        {'dog_2': 2, 'cat_2': 2}
    ),
    # filter wtih exact match
    (
        {'dog_1': 1, 'dog_2': 2, 'cat_1': 1, 'cat_2': 2},
        ['cat_2'],
        {'cat_2': 2}
    ),
    # empty dict, empty filter
    ({}, [], {}),
    # empty dict, non-empty filter
    ({}, ['a*'], {}),

]


@pytest.mark.parametrize("actual,filter_list,expected", test_data)
def test_zos_gather_facts_apply_filter(
        zos_import_mocker, actual, filter_list, expected):

    mocker, importer = zos_import_mocker
    zos_gather_facts = importer(IMPORT_NAME)

    try:
        result = zos_gather_facts.apply_filter(actual, filter_list)
    except Exception:
        result = None
    assert result == expected
