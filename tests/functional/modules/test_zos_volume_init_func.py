# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023, 2025
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

from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

# To run the test suite is a recommendation to use the volumes in order
# 'USER02', '01A2'
# new list of similar volumes will be added in next iteration

INDEX_CREATION_SUCCESS_MSG = 'VTOC INDEX CREATION SUCCESSFUL'
VTOC_LOC_MSG = "ICK01314I VTOC IS LOCATED AT CCHH=X'0000 0001' AND IS  {:4d} TRACKS."

def clear_volume(hosts, volume):
    datasets_in_volume = hosts.all.shell(cmd="vtocls {0}".format(volume))
    for dataset in datasets_in_volume.contacted.values():
        datasets = str(dataset.get("stdout")).split("\n")
    for dataset in datasets:
        dataset_t_del = dataset.split(' ', 1)[0]
        hosts.all.shell(cmd="""drm "{0}" """.format(dataset_t_del))

# Guard Rail to prevent unintentional initialization of targeted volume.
# If this test fails, either reset target volume serial to match
# verify_volid below or change value to match current volume serial on
# target.

def test_guard_rail_and_setup(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        "address":address,
        "verify_offline":False,
        "volid":volume,
        "verify_volid":volume
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(
        address=params['address'],
        verify_offline=params['verify_offline'],
        volid=params['volid'],
        verify_volid=params['verify_volid']
        )

    for result in results.contacted.values():
        # assert result.get('changed') is True
        assert result['rc'] == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_index_param_index(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    params = {
        "address": address,
        "verify_offline": False,
        "volid": volume,
        "index" : True
    }

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0
        content_str = ''.join(result.get("content"))
        if params['index']:
            assert INDEX_CREATION_SUCCESS_MSG in content_str
        else:
            assert INDEX_CREATION_SUCCESS_MSG not in content_str

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_index_param_index_sms_false(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    params = {
        "address": address,
        "verify_offline": False,
        "volid": volume,
        "index" : True,
        "sms_managed" : False
    }

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0
        content_str = ''.join(result.get("content"))
        if params['index']:
            assert INDEX_CREATION_SUCCESS_MSG in content_str
        else:
            assert INDEX_CREATION_SUCCESS_MSG not in content_str

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


# check that correct volume_addr is assigned to correct volid
def test_volid_address_assigned_correctly(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0

    # The display command issued queries a volume called $TEST_VOL_SER. The
    # expected return values are: 'IEE455I UNIT STATUS NO DEVICES WITH REQUESTED
    # ATTRIBUTES' or a line with several attributes including unit address
    # example output:
    # 'UNIT TYPE STATUS        VOLSER     VOLSTATE      SS'
    # '0903 3390 O             DEMO01     PRIV/RSDNT     0'
    # or:
    # 'IEE455I UNIT STATUS NO DEVICES WITH REQUESTED ATTRIBUTES'
    # (expected value $TEST_VOL_ADDR) and volume serial
    # (expected value $TEST_VOL_SER). If those two match, then the 'volid'
    # parameter is correctly assigned to the 'address' parameter.

    # Display command to print device status, volser and addr should correspond
    display_cmd_output = list(
        hosts.all.zos_operator(cmd=f"D U,VOL={volume}").contacted.values()
    )[0]

    # zos_operator output contains the command as well, only the last line of
    # the output is relevant for the needs of this test case.
    display_cmd_output = display_cmd_output.get('content')[-1]

    assert volume in display_cmd_output

def test_no_index_sms_managed_mutually_exclusive(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'index' : False,
        'sms_managed' : True
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert "'Index' cannot be False" in result.get("msg")


def test_vtoc_size_parm(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'vtoc_size' : 8
        # 'vtoc_size' : 11 # test to test that this test handles 2 digit vtoc_index
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0
        content_str = ''.join(result.get("content"))
        assert VTOC_LOC_MSG.format(params.get('vtoc_size')) in content_str


def test_good_param_values_only_volid(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_good_param_values_volid_n_verify_volid(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'verify_volid' : volume
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_good_param_values_volid_n_verify_volume_empty(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'verify_volume_empty' : True
    }
    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get('rc') == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_values_address_not_hexadecimal(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    expected_rc = 12

    params = {
        "address": 'XYZ',
        "verify_offline": False,
        "volid": volume
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_values_address_length_too_short(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)
    expected_rc = 12

    params = {
        "address": '01',
        "verify_offline": False,
        "volid": volume
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_values_address_specified_is_not_accesible_to_current(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)
    expected_rc = 12

    params = {
        "address": '0000',
        "verify_offline": False,
        "volid": volume
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_values_negative_value_for_vtoc_size(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    expected_rc = 12

    params = {
        "address": address,
        "verify_offline": False,
        "volid": volume,
        "vtoc_size": -10
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_incorrect_existing_volid(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)
    expected_rc = 12

    params = {
        "address": address,
        "verify_offline": False,
        "volid": volume,
        "verify_volid": '000000'
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


def test_bad_param_volid_value_too_long(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    expected_rc = 12

    params = {
        "address": 'ABCDEFGHIJK',
        "verify_offline": False,
        "volid": volume,
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(**params)

    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get('failed') is True
        assert result.get('rc') == expected_rc

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")


# Note - volume needs to be sms managed for zos_data_set to work. Possible
#        points of failure are:
#        unable to init volume first time around
#        unable to allocate data set
#        unable to bring vol back online to delete data set
#        If there is a data set remaining on the volume, that would interfere
#        with other tests!

def test_no_existing_data_sets_check(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)
    dataset = get_tmp_ds_name()

    setup_params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'sms_managed': False # need non-sms managed to add data set on ECs
    }
    test_params = {
        'address': address,
        'verify_offline': False,
        'volid': volume,
        'verify_volume_empty': True,
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    try:
        # set up/initialize volume properly so a data set can be added
        hosts.all.zos_volume_init(**setup_params)

        # bring volume back online
        hosts.all.zos_operator(cmd=f"vary {address},online")

        # allocate data set to volume
        hosts.all.shell(cmd=f"dtouch -tpds -V{volume} '{name}'")
        # hosts.all.zos_data_set(name=dataset, type='pds', volumes=volume)

        # take volume back offline
        hosts.all.zos_operator(cmd=f"vary {address},offline")

        # run vol_init against vol with data set on it.
        results = hosts.all.zos_volume_init(**test_params)

        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get('failed') is True
            assert result.get('rc') == 12

    # clean up just in case of failures, volume needs to be reset for other
    # tests. Not sure what to do for DatasetDeleteError
    finally:
        # bring volume back online
        hosts.all.zos_operator(cmd=f"vary {address},online")

        # remove data set
        hosts.all.shell(cmd=f"drm '{name}'")
        # hosts.all.zos_data_set(name=dataset, state='absent')


# Note - technically verify_offline is not REQUIRED but it defaults to True
#        and the volumes on the EC systems do not seem to go fully offline.
#        Therefore, while testing against the EC machines, the verify_offline
#        check needs to be skipped in order for ickdsf to be invoked.

def test_minimal_params(ansible_zos_module, volumes_unit_on_systems):
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    volume, address = volumes.get_available_vol_addr()
    # remove all data sets from target volume. Expected to be the following 3
    clear_volume(hosts, volume)

    params = {
        "address":address,
        "verify_offline":False,
        "volid":volume
    }

    # take volume offline
    hosts.all.zos_operator(cmd=f"vary {address},offline")

    results = hosts.all.zos_volume_init(
        address=params['address'],
        verify_offline=params['verify_offline'],
        volid=params['volid']
        )

    for result in results.contacted.values():
        assert result.get('changed') is True
        assert result['rc'] == 0

    # bring volume back online
    hosts.all.zos_operator(cmd=f"vary {address},online")
