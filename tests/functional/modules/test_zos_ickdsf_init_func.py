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

# TODO - positive tests:
# volume_addr -- confirm?
# volid - confirm value matches volid assigned
# vtoc_tracks - confirm value matches value assigned


@pytest.mark.parametrize(
    "params,expected_rc", [
        # volume_address not hexadecimal
        ({
            'volume_address': 'XYZ',
            'verify_offline': False,
            'volid': TEST_VOL_SER
        }, 12),
        # volume_address length too short
        ({
            'volume_address': '01',
            'verify_offline': False,
            'volid': TEST_VOL_SER
        }, 12),
        # volume_address specified is not accesible to current
        ({
            'volume_address': '0000',
            'verify_offline': False,
            'volid': TEST_VOL_SER
        }, 12),
        # negative value for vtoc_tracks
        ({
            'volume_address': TEST_VOL_ADDR,
            'verify_offline': False,
            'volid': TEST_VOL_SER,
            'vtoc_tracks': -10
        }, 12),
        # note - "'vtoc_tracks': 0" gets treated as vtoc_tracks wasn't defined and invokes default behavior.
        # ({}, 0)

    ]
)
def test_bad_param_values(ansible_zos_module, params, expected_rc):
    hosts = ansible_zos_module

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {TEST_VOL_ADDR},offline")

    results = hosts.all.zos_ickdsf_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {TEST_VOL_ADDR},online")


# Note - technically verify_offline is not REQUIRED but it defaults to True
#        and the volumes on the EC systems do not seem to go fully offline.
#        Therefore, while testing against the EC machines, the verify_offline
#        check needs to be skipped in order for ickdsf to be invoked.
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
        assert result.get('changed') is True
        assert result['rc'] == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {TEST_VOL_ADDR},online")
