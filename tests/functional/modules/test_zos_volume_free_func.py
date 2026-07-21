# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2026
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

import pytest

from ibm_zos_core.tests.helpers.volumes import Volume_Handler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VOLUME_RETURN_KEYS = {
    'volser', 'device_number', 'device_type', 'status',
    'total_space', 'free_space', 'used_space',
    'percent_free', 'percent_used',
    'total_bytes', 'free_bytes',
    'device_status', 'vtoc_info',
}

DEVICE_STATUS_KEYS = {
    'is_online', 'status_changing', 'is_reserved', 'is_unloaded',
    'is_allocated', 'is_present', 'is_system_residence', 'is_dasd',
}

VTOC_INFO_KEYS = {'index_vtoc', 'vtoc_active', 'is_cylinder_managed'}


def _assert_volume_structure(vol):
    """Assert that a single volume entry has all expected keys and valid types."""
    assert VOLUME_RETURN_KEYS.issubset(set(vol.keys())), (
        "Missing keys in volume entry: {0}".format(VOLUME_RETURN_KEYS - set(vol.keys()))
    )
    assert isinstance(vol['volser'], str)
    assert isinstance(vol['device_number'], str)
    assert vol['status'] in ('online', 'offline', 'pending')
    assert isinstance(vol['total_space'], int)
    assert isinstance(vol['free_space'], int)
    assert isinstance(vol['used_space'], int)
    assert isinstance(vol['percent_free'], float)
    assert isinstance(vol['percent_used'], float)
    assert isinstance(vol['total_bytes'], int)
    assert isinstance(vol['free_bytes'], int)
    assert 0.0 <= vol['percent_free'] <= 100.0
    assert 0.0 <= vol['percent_used'] <= 100.0
    assert vol['total_space'] >= 0
    assert vol['free_space'] >= 0
    assert vol['used_space'] >= 0
    # used + free must equal total
    assert vol['used_space'] + vol['free_space'] == vol['total_space']
    # device_status sub-keys
    ds = vol['device_status']
    assert DEVICE_STATUS_KEYS.issubset(set(ds.keys()))
    for k in DEVICE_STATUS_KEYS:
        assert isinstance(ds[k], bool)
    # vtoc_info sub-keys
    vi = vol['vtoc_info']
    assert VTOC_INFO_KEYS.issubset(set(vi.keys()))
    for k in VTOC_INFO_KEYS:
        assert isinstance(vi[k], bool)


# ---------------------------------------------------------------------------
# Tests: basic invocations
# ---------------------------------------------------------------------------

def test_query_all_volumes(ansible_zos_module):
    """Querying with no parameters should return at least one volume."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        vols = result.get('volumes', [])
        assert isinstance(vols, list)
        assert len(vols) > 0, "Expected at least one volume when querying all"
        for vol in vols:
            _assert_volume_structure(vol)
        assert 'msg' in result


def test_query_specific_volumes(ansible_zos_module, volumes_on_systems):
    """Querying by known VOLSER should return only that volume."""
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_on_systems)
    vol_name = volumes.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        vols = result.get('volumes', [])
        assert len(vols) == 1, "Expected exactly one volume for VOLSER {0}".format(vol_name)
        _assert_volume_structure(vols[0])
        assert vols[0]['volser'] == vol_name
    volumes.free_vol(vol_name)


def test_query_nonexistent_volume_returns_empty(ansible_zos_module):
    """Querying a non-existent VOLSER should return an empty list without failing."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(volumes=["XXXXXX"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        vols = result.get('volumes', [])
        assert vols == []


def test_query_by_device_number(ansible_zos_module, volumes_unit_on_systems):
    """Querying by device number should return at least one matching volume."""
    hosts = ansible_zos_module
    volumes = Volume_Handler(volumes_unit_on_systems)
    vol_name, device_addr = volumes.get_available_vol_addr()

    results = hosts.all.zos_volume_free(device_numbers=[device_addr])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        vols = result.get('volumes', [])
        assert len(vols) >= 1
        device_numbers = [v['device_number'].upper() for v in vols]
        assert device_addr.upper() in device_numbers
        for vol in vols:
            _assert_volume_structure(vol)
    volumes.free_vol(vol_name)


def test_query_union_volser_and_device(ansible_zos_module, volumes_unit_on_systems):
    """Querying with both volumes and device_numbers should return a deduplicated union."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_unit_on_systems)
    vol_name_1, device_addr_1 = vols.get_available_vol_addr()
    vol_name_2, device_addr_2 = vols.get_available_vol_addr()

    results = hosts.all.zos_volume_free(
        volumes=[vol_name_1],
        device_numbers=[device_addr_2]
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        result_vols = result.get('volumes', [])
        # No duplicate VOLSERs
        volsers = [v['volser'] for v in result_vols]
        assert len(volsers) == len(set(volsers)), "Duplicate VOLSERs found in union result"
        for vol in result_vols:
            _assert_volume_structure(vol)

    vols.free_vol(vol_name_1)
    vols.free_vol(vol_name_2)


# ---------------------------------------------------------------------------
# Tests: filter by status
# ---------------------------------------------------------------------------

def test_filter_online_only(ansible_zos_module):
    """All returned volumes should report status=online when filter is applied."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['online']}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        vols = result.get('volumes', [])
        for vol in vols:
            assert vol['status'] == 'online', (
                "Expected status=online but got {0} for {1}".format(
                    vol['status'], vol['volser']
                )
            )


# ---------------------------------------------------------------------------
# Tests: filter by free space
# ---------------------------------------------------------------------------

def test_filter_free_space_min_tracks(ansible_zos_module):
    """All returned volumes should have free_space >= free_space_min (tracks)."""
    hosts = ansible_zos_module
    min_tracks = 100
    results = hosts.all.zos_volume_free(
        filter={'free_space_min': min_tracks, 'unit': 'tracks'}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['free_space'] >= min_tracks, (
                "Volume {0} has free_space={1}, expected >= {2}".format(
                    vol['volser'], vol['free_space'], min_tracks
                )
            )


def test_filter_free_space_min_cylinders(ansible_zos_module):
    """Filter with cylinder unit should be converted to tracks for comparison."""
    hosts = ansible_zos_module
    min_cylinders = 10
    min_tracks_expected = min_cylinders * 15
    results = hosts.all.zos_volume_free(
        filter={'free_space_min': min_cylinders, 'unit': 'cylinders'}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['free_space'] >= min_tracks_expected, (
                "Volume {0} has free_space={1} tracks, expected >= {2}".format(
                    vol['volser'], vol['free_space'], min_tracks_expected
                )
            )


def test_filter_free_space_max_tracks(ansible_zos_module):
    """All returned volumes should have free_space <= free_space_max (tracks)."""
    hosts = ansible_zos_module
    # Use a very large threshold so we expect at least some results.
    max_tracks = 999999
    results = hosts.all.zos_volume_free(
        filter={'free_space_max': max_tracks, 'unit': 'tracks'}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['free_space'] <= max_tracks


def test_filter_percent_free_min(ansible_zos_module):
    """All returned volumes should have percent_free >= percent_free_min."""
    hosts = ansible_zos_module
    min_pct = 1
    results = hosts.all.zos_volume_free(
        filter={'percent_free_min': min_pct}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['percent_free'] >= min_pct


def test_filter_percent_free_max(ansible_zos_module):
    """All returned volumes should have percent_free <= percent_free_max."""
    hosts = ansible_zos_module
    max_pct = 99
    results = hosts.all.zos_volume_free(
        filter={'percent_free_max': max_pct}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['percent_free'] <= max_pct


# ---------------------------------------------------------------------------
# Tests: filter by VTOC
# ---------------------------------------------------------------------------

def test_filter_vtoc_indexed_true(ansible_zos_module):
    """All returned volumes should have index_vtoc=True when vtoc_indexed=true."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'vtoc_indexed': True}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['vtoc_info']['index_vtoc'] is True, (
                "Volume {0} does not have index_vtoc=True".format(vol['volser'])
            )


def test_filter_vtoc_indexed_false(ansible_zos_module):
    """All returned volumes should have index_vtoc=False when vtoc_indexed=false."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'vtoc_indexed': False}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['vtoc_info']['index_vtoc'] is False, (
                "Volume {0} has index_vtoc=True but filter requested False".format(
                    vol['volser']
                )
            )


# ---------------------------------------------------------------------------
# Tests: combined filters
# ---------------------------------------------------------------------------

def test_filter_combined_status_and_percent(ansible_zos_module):
    """Combined status + percent_free_max filter: all results must satisfy both."""
    hosts = ansible_zos_module
    max_pct = 80
    results = hosts.all.zos_volume_free(
        filter={'status': ['online'], 'percent_free_max': max_pct}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['status'] == 'online'
            assert vol['percent_free'] <= max_pct


def test_filter_free_space_max_cylinders(ansible_zos_module):
    """Filter with free_space_max in cylinders should convert to tracks correctly."""
    hosts = ansible_zos_module
    max_cylinders = 10000
    max_tracks_expected = max_cylinders * 15
    results = hosts.all.zos_volume_free(
        filter={'free_space_max': max_cylinders, 'unit': 'cylinders'}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['free_space'] <= max_tracks_expected, (
                "Volume {0} has free_space={1} tracks, expected <= {2}".format(
                    vol['volser'], vol['free_space'], max_tracks_expected
                )
            )


def test_filter_percent_free_range(ansible_zos_module):
    """All returned volumes should satisfy both percent_free_min and percent_free_max."""
    hosts = ansible_zos_module
    min_pct = 1
    max_pct = 99
    results = hosts.all.zos_volume_free(
        filter={'percent_free_min': min_pct, 'percent_free_max': max_pct}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['percent_free'] >= min_pct, (
                "Volume {0} percent_free={1} is below min {2}".format(
                    vol['volser'], vol['percent_free'], min_pct
                )
            )
            assert vol['percent_free'] <= max_pct, (
                "Volume {0} percent_free={1} is above max {2}".format(
                    vol['volser'], vol['percent_free'], max_pct
                )
            )


def test_filter_no_match_returns_empty(ansible_zos_module):
    """A filter that matches no volumes should return an empty list without failing."""
    hosts = ansible_zos_module
    # free_space_min > any real volume will ever have
    results = hosts.all.zos_volume_free(
        filter={'free_space_min': 999999999}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        assert result.get('volumes') == []


# ---------------------------------------------------------------------------
# Tests: multiple VOLSERs / device numbers
# ---------------------------------------------------------------------------

def test_query_multiple_volsers(ansible_zos_module, volumes_on_systems):
    """Querying with a list of VOLSERs should return all matching volumes."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_on_systems)
    vol_name_1 = vols.get_available_vol()
    vol_name_2 = vols.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name_1, vol_name_2])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        result_volsers = [v['volser'] for v in result.get('volumes', [])]
        assert vol_name_1 in result_volsers
        assert vol_name_2 in result_volsers
        for vol in result.get('volumes', []):
            _assert_volume_structure(vol)

    vols.free_vol(vol_name_1)
    vols.free_vol(vol_name_2)


def test_query_nonexistent_device_number_returns_empty(ansible_zos_module):
    """Querying a non-existent device number should return an empty list without failing."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(device_numbers=["FFFF"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        assert result.get('volumes') == []


def test_volser_input_is_case_insensitive(ansible_zos_module, volumes_on_systems):
    """VOLSER matching should be case-insensitive — lowercase input must match."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_on_systems)
    vol_name = vols.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name.lower()])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        result_vols = result.get('volumes', [])
        assert len(result_vols) == 1, (
            "Expected 1 volume for lowercase VOLSER {0}".format(vol_name.lower())
        )
        assert result_vols[0]['volser'] == vol_name

    vols.free_vol(vol_name)


# ---------------------------------------------------------------------------
# Tests: return structure
# ---------------------------------------------------------------------------

def test_return_msg_present(ansible_zos_module):
    """The 'msg' key should always be present in the result."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert 'msg' in result
        assert isinstance(result['msg'], str)
        assert len(result['msg']) > 0


def test_return_changed_always_false(ansible_zos_module):
    """changed should always be False since this module is read-only."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('changed') is False


def test_return_stdout_present(ansible_zos_module):
    """stdout is always an empty string — present for API consistency only."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert 'stdout' in result
        assert result['stdout'] == '', (
            "stdout should always be empty string, got: {0!r}".format(result['stdout'])
        )


def test_return_stderr_present(ansible_zos_module):
    """stderr should always be present in the result (empty string on success)."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert 'stderr' in result
        assert isinstance(result['stderr'], str)


# ---------------------------------------------------------------------------
# Tests: filter.status input validation
# ---------------------------------------------------------------------------

def test_filter_status_invalid_value_fails(ansible_zos_module):
    """An invalid status value should cause the module to fail with a clear error."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['onlin']}  # intentional typo
    )
    for result in results.contacted.values():
        assert result.get('failed') is True, (
            "Expected module to fail on invalid status value 'onlin' but it succeeded"
        )
        # Ansible's choices validation message always contains the bad value.
        msg = result.get('msg', '') + result.get('stderr', '')
        assert 'onlin' in msg, (
            "Expected error message to reference the invalid value 'onlin', got: {0}".format(msg)
        )


def test_filter_status_valid_values_accepted(ansible_zos_module):
    """Each valid status value should be accepted individually without failure."""
    hosts = ansible_zos_module
    for status_val in ('online', 'offline', 'pending'):
        results = hosts.all.zos_volume_free(
            filter={'status': [status_val]}
        )
        for result in results.contacted.values():
            assert result.get('failed') is not True, (
                "Module unexpectedly failed for valid status value '{0}': {1}".format(
                    status_val, result.get('msg', '')
                )
            )
