# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2022
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

import os
import sys
from unittest import result
import pytest

from pprint import pprint

__metaclass__ = type

def test_gather_facts(ansible_zos_module):

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts()
    for result in results.contacted.values():
        print(result)
        assert result is not None
        # something was returned -- most basic test case.

def test_gather_facts_with_gather_subset(ansible_zos_module):
    hosts = ansible_zos_module
    ipl_only_subset = ['ipl']
    results = hosts.all.zos_gather_facts(gather_subset=ipl_only_subset)

    for result in results.contacted.values():
        assert result is not None

# test with filter=name and no gather_subset
def test_gather_facts_with_filter(ansible_zos_module):
    hosts = ansible_zos_module
    filter_list=['*name*']
    results = hosts.all.zos_gather_facts(filter=filter_list)
    for result in results.contacted.values():
        assert result is not None
        assert result.get('ansible_facts') is not None

        # check certain known keys fitting the pattern are in dict
        assert "iodf_name" in result.get('ansible_facts').keys()
        assert "lpar_name" in result.get('ansible_facts').keys()
        assert "product_name" in result.get('ansible_facts').keys()
        assert "smf_name" in result.get('ansible_facts').keys()
        assert "sys_name" in result.get('ansible_facts').keys()
        assert "sysplex_name" in result.get('ansible_facts').keys()
        assert "vm_name" in result.get('ansible_facts').keys()

        # check that other known keys not fitting the pattern are not in dict
        assert "load_param_dsn" not in result.get('ansible_facts').keys()
        assert "master_catalog_volser" not in result.get('ansible_facts').keys()
        assert "arch_level" not in result.get('ansible_facts').keys()
        assert "product_owner" not in result.get('ansible_facts').keys()
        assert "iotime" not in result.get('ansible_facts').keys()
        assert "cpc_nd_manufacturer" not in result.get('ansible_facts').keys()


# test with filter=*name* and gather_subset=iodf
def test_gather_facts_with_subset_and_filter(ansible_zos_module):
    hosts = ansible_zos_module
    ipl_only_subset = ['iodf']
    filter_list=['*name*']
    results = hosts.all.zos_gather_facts(gather_subset=ipl_only_subset, filter=filter_list)
    for result in results.contacted.values():
        assert result is not None
        assert result.get('ansible_facts') is not None

        assert "iodf_name" in result.get('ansible_facts').keys()

        # sys_name is not in the iodf subset.
        assert "sys_name" not in result.get('ansible_facts').keys()


# erroneous output:
# ansible handles wrong format so we can expect gather_subset and filter to always be lists of str.

# # bad subsets -
#     results = hosts.all.zos_gather_facts(gather_subset=['']) # empty string
#     results = hosts.all.zos_gather_facts(gather_subset=['    ']) # space chars
#     results = hosts.all.zos_gather_facts(gather_subset=['asdfasdf']) # nonsense
#     # space and other good chars
#     results = hosts.all.zos_gather_facts(gather_subset=['   ipl'])
#     # space and other bad chars
#     results = hosts.all.zos_gather_facts(gather_subset=['   asdf '])

# # bad filters -
#     # '*' should be same output as default
#     results = hosts.all.zos_gather_facts(filter=['*'])
#     results = hosts.all.zos_gather_facts(filter=['']) # empty
#     results = hosts.all.zos_gather_facts(filter=[' ']) # space
#     results = hosts.all.zos_gather_facts(filter=['asdfasdf']) # nonsense
