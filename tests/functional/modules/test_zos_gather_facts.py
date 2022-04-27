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

# To minimize the number of times the same facts are repeatedly gathered, the tests have been divided into a check against just the base collectors, just the python collector, and the remaining ansible core engine collectors are lumped into a single test. The facts defined in the base collectors should always be collected because they are dependencies for some of the subsequent collectors. The python collector is separated to double check that the gather_subset parameter works as expected.

# The following values are defined in the module and could be changed later:


# this one is defined as a param to PrefixFactNamespace, which gets passed into the get_ansible_collector method.
# FACTS_PREFIX = 'ansible_'


def test_gather_facts(ansible_zos_module):

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts()
    for result in results.contacted.values():
        print(result)
        assert result is not None
        # something was returned -- most basic test case.

        # assert result.get(ansible_facts).get(FACTS_PREFIX+'architecture') is not None

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

        assert "iodf_name" in result.get('ansible_facts').keys()
        assert "lpar_name" in result.get('ansible_facts').keys()
        assert "product_name" in result.get('ansible_facts').keys()
        assert "smf_name" in result.get('ansible_facts').keys()
        assert "sys_name" in result.get('ansible_facts').keys()
        assert "sysplex_name" in result.get('ansible_facts').keys()
        assert "vm_name" in result.get('ansible_facts').keys()

# test with filter=master* and gather_subset=ipl
def test_gather_facts_with_subset_and_filter(ansible_zos_module):
    hosts = ansible_zos_module
    ipl_only_subset = ['ipl']
    filter_list=['master*']
    results = hosts.all.zos_gather_facts(gather_subset=ipl_only_subset, filter=filter_list)
    for result in results.contacted.values():
        assert result is not None
        assert result.get('ansible_facts') is not None

        assert "master_catalog_dsn" in result.get('ansible_facts').keys()
        assert "master_catalog_volser" in result.get('ansible_facts').keys()

