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

from unittest import result
import pytest

__metaclass__ = type


def test_gather_facts(ansible_zos_module):

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts()
    for result in results.contacted.values():
        assert result is not None
        # something was returned -- most basic test case.


def test_with_gather_subset(ansible_zos_module):
    hosts = ansible_zos_module
    ipl_only_subset = ['ipl']
    results = hosts.all.zos_gather_facts(gather_subset=ipl_only_subset)

    for result in results.contacted.values():
        assert result is not None
        # check certain known keys in ipl subset are present
        assert "ieasym_card" in result.get('ansible_facts').keys()
        assert "ipaloadxx" in result.get('ansible_facts').keys()
        assert "master_catalog_dsn" in result.get('ansible_facts').keys()

        # check certain known keys not in ipl subset are not present
        assert "hw_name" not in result.get('ansible_facts').keys()
        assert "iodf_name" not in result.get('ansible_facts').keys()
        assert "cpc_nd_manufacturer" not in result.get('ansible_facts').keys()


# test with filter=name and no gather_subset
def test_with_filter(ansible_zos_module):
    hosts = ansible_zos_module
    filter_list = ['*name*']
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
        assert "master_catalog_dsn" not in result.get('ansible_facts').keys()
        assert "arch_level" not in result.get('ansible_facts').keys()
        assert "product_owner" not in result.get('ansible_facts').keys()
        assert "iotime" not in result.get('ansible_facts').keys()
        assert "cpc_nd_manufacturer" not in result.get('ansible_facts').keys()


# test with filter=*name* and gather_subset=iodf
def test_with_subset_and_filter(ansible_zos_module):
    hosts = ansible_zos_module
    ipl_only_subset = ['iodf']
    filter_list = ['*name*']
    results = hosts.all.zos_gather_facts(
        gather_subset=ipl_only_subset, filter=filter_list)
    for result in results.contacted.values():
        assert result is not None
        assert result.get('ansible_facts') is not None

        assert "iodf_name" in result.get('ansible_facts').keys()

        # sys_name is not in the iodf subset.
        assert "sys_name" not in result.get('ansible_facts').keys()


def test_with_filter_asterisk(ansible_zos_module):

    subset = ['ipl']  # to cut down on list of facts returned

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts(gather_subset=subset, filter=['*'])
    for result in results.contacted.values():
        # known facts in ipl subset should still be in ansible_facts
        assert "ieasym_card" in result.get('ansible_facts').keys()
        assert "ipaloadxx" in result.get('ansible_facts').keys()
        assert "master_catalog_dsn" in result.get('ansible_facts').keys()

# erroneous output:
# ansible handles input in wrong format so we can expect gather_subset
# and filter to always be lists of str.

# bad subsets -


# nonsense subset
test_data = [
    (['   asdf']),
    (['asdfasdf']),
]


@pytest.mark.parametrize("gather_subset", test_data)
def test_with_gather_subset_bad(ansible_zos_module, gather_subset):
    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts(gather_subset=gather_subset)
    for result in results.contacted.values():
        assert result.get('failed') is True
        assert result.get('zinfo_err_msg') is not None


# attempted injection through subset
def test_with_gather_subset_injection(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts(gather_subset=['ipl; cat /.bashrc'])
    for result in results.contacted.values():
        assert result.get('failed') is True


# whitespace subsets
test_data = [
    (['   ']),
    (['']),
    (["\t"]),
]


@pytest.mark.parametrize("gather_subset", test_data)
def test_with_gather_subset_empty_str(
        ansible_zos_module, gather_subset):

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts(gather_subset=gather_subset)
    for result in results.contacted.values():
        assert result.get('failed') is True


test_data = [
    # bad filters -
    ([' ']),  # space
    (['    ']),  # spaces
    (['']),  # empty str
    (['asdfasdf'])  # nonsense
]


@pytest.mark.parametrize("filter_list", test_data)
def test_with_bad_filter(ansible_zos_module, filter_list):

    subset = ['ipl']

    hosts = ansible_zos_module
    results = hosts.all.zos_gather_facts(
        gather_subset=subset, filter=filter_list)

    for result in results.contacted.values():
        # known facts in ipl subset should not be in ansible_facts
        assert "ieasym_card" not in result.get('ansible_facts').keys()
        assert "ipaloadxx" not in result.get('ansible_facts').keys()
        assert "master_catalog_dsn" not in result.get('ansible_facts').keys()
