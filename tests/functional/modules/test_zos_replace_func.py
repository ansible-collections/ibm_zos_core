#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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

import pytest

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

def test_uss(ansible_zos_module):
    hosts = ansible_zos_module

@pytest.mark.parametrize("ds_type", ["seq", "pds", "pdse"])
def test_dataset_types(ansible_zos_module):
    hosts = ansible_zos_module