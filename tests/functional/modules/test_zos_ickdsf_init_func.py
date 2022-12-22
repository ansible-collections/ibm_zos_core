# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2021
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

__metaclass__ = type

TEST_VOL_ADDR = '0903'
TEST_VOL_SER = 'KET999'


def test_minimal_params(ansible_zos_module):
    hosts = ansible_zos_module

    params = dict(
        volume_address=TEST_VOL_ADDR,
        verify_offline=False,
        volid=TEST_VOL_SER
    )

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {TEST_VOL_ADDR},offline")
    
    results = hosts.all.zos_ickdsf_init(
        volume_address=params['volume_address'],
        verify_offline=params['verify_offline'],
        volid=params['volid']
        )

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result['rc'] == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {TEST_VOL_ADDR},online")
