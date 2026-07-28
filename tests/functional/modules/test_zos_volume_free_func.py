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
    'volser', 'device_number',
    'total_space', 'free_space', 'used_space',
    'percent_free', 'percent_used',
    'total_kilobytes', 'free_kilobytes',
    'is_cylinder_managed',
    'status', 'vtoc_info',
}

STATUS_KEYS = {
    'online', 'offline_pending', 'mount_reserved', 'unload_pending',
    'allocated', 'permanently_resident', 'system_residence', 'status_indicator',
}

VTOC_INFO_KEYS = {'index_vtoc', 'vtoc_active'}


def _assert_volume_structure(vol):
    """Assert that a single volume entry has all expected keys and valid types."""
    assert VOLUME_RETURN_KEYS.issubset(set(vol.keys())), (
        "Missing keys in volume entry: {0}".format(VOLUME_RETURN_KEYS - set(vol.keys()))
    )
    assert isinstance(vol['volser'], str)
    assert isinstance(vol['device_number'], str)
    assert isinstance(vol['total_space'], int)
    assert isinstance(vol['free_space'], int)
    assert isinstance(vol['used_space'], int)
    assert isinstance(vol['percent_free'], float)
    assert isinstance(vol['percent_used'], float)
    assert isinstance(vol['total_kilobytes'], int)
    assert isinstance(vol['free_kilobytes'], int)
    assert isinstance(vol['is_cylinder_managed'], bool)
    assert 0.0 <= vol['percent_free'] <= 100.0
    assert 0.0 <= vol['percent_used'] <= 100.0
    assert vol['total_space'] >= 0
    assert vol['free_space'] >= 0
    assert vol['used_space'] + vol['free_space'] == vol['total_space']
    # status sub-keys
    st = vol['status']
    assert STATUS_KEYS.issubset(set(st.keys()))
    for k in STATUS_KEYS:
        assert isinstance(st[k], bool)
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
    """A single non-existent VOLSER should return an empty list without failing."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(volumes=["XXXXXX"])
    for result in results.contacted.values():
        assert result.get('failed') is not True, (
            "Expected module to succeed for non-existent single VOLSER 'XXXXXX' but it failed"
        )
        assert result.get('changed') is False
        assert result.get('volumes') == [], (
            "Expected empty volumes list for non-existent VOLSER, got: {0}".format(
                result.get('volumes')
            )
        )
        msg = result.get('msg', '')
        assert 'No matching volumes found.' in msg, (
            "Expected 'No matching volumes found.' in msg, got: {0!r}".format(msg)
        )
        assert 'XXXXXX' in msg, (
            "Expected unavailable volser 'XXXXXX' listed in msg, got: {0!r}".format(msg)
        )


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
    """Querying with both volumes and device_numbers should return a deduplicated union.

    vol_name_1 is matched by VOLSER; vol_name_2 is matched by device number.
    Both must appear in results, with no duplicate VOLSERs.
    """
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_unit_on_systems)
    vol_name_1, _ = vols.get_available_vol_addr()
    vol_name_2, device_addr_2 = vols.get_available_vol_addr()

    results = hosts.all.zos_volume_free(
        volumes=[vol_name_1],
        device_numbers=[device_addr_2]
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        result_vols = result.get('volumes', [])
        volsers = [v['volser'] for v in result_vols]
        # Both sides of the union must be present.
        assert vol_name_1 in volsers, (
            "Expected VOLSER-matched volume {0} in results".format(vol_name_1)
        )
        assert vol_name_2 in volsers, (
            "Expected device-matched volume {0} (device {1}) in results".format(
                vol_name_2, device_addr_2
            )
        )
        # No duplicate VOLSERs.
        assert len(volsers) == len(set(volsers)), "Duplicate VOLSERs found in union result"
        for vol in result_vols:
            _assert_volume_structure(vol)

    vols.free_vol(vol_name_1)
    vols.free_vol(vol_name_2)


# ---------------------------------------------------------------------------
# Tests: filter by status
# ---------------------------------------------------------------------------

def test_filter_online_only(ansible_zos_module):
    """All returned volumes should have status.online=True when filter is applied."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['online']}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['status']['online'] is True, (
                "Expected status.online=True for {0}".format(vol['volser'])
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
            assert vol['status']['online'] is True
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
    """Querying a non-existent device number should return an empty list without failing.

    The module appends a 'Device numbers not found or inaccessible' notice to
    msg listing any device numbers that matched no volume.
    """
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(device_numbers=["FFFF"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('changed') is False
        assert result.get('volumes') == []
        msg = result.get('msg', '')
        assert 'Device numbers not found or inaccessible' in msg, (
            "Expected unavailability notice in msg, got: {0!r}".format(msg)
        )
        assert 'FFFF' in msg.upper(), (
            "Expected device number 'FFFF' listed in msg, got: {0!r}".format(msg)
        )


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

def test_return_rc_success(ansible_zos_module):
    """rc should be 0 on a successful query."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('rc') == 0, (
            "Expected rc=0 on success, got rc={0}".format(result.get('rc'))
        )


def test_return_rc_present(ansible_zos_module):
    """rc should always be present in the result."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert 'rc' in result, "Expected 'rc' key in result"
        assert isinstance(result['rc'], int), (
            "Expected 'rc' to be int, got {0}".format(type(result['rc']))
        )


def test_return_rc_5_on_param_validation_failure(ansible_zos_module):
    """rc=5 when BetterArgParser rejects an invalid VOLSER.

    Ansible's argument_spec accepts any string for 'volumes', but
    BetterArgParser's 'volume' element type rejects names that violate
    z/OS VOLSER rules (e.g. longer than 6 characters), raising ValueError
    which maps to rc=5.
    """
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        volumes=['TOOLONGVOLSERVALUE']
    )
    for result in results.contacted.values():
        assert result.get('failed') is True, (
            "Expected module to fail for invalid VOLSER but it succeeded"
        )
        assert result.get('rc') == 5, (
            "Expected rc=5 for BetterArgParser validation failure, got rc={0}".format(
                result.get('rc')
            )
        )


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
# Tests: filter.status (UCB flag filtering)
# ---------------------------------------------------------------------------

def test_filter_status_invalid_value_fails(ansible_zos_module):
    """An invalid status flag should cause the module to fail with a clear error."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['not_a_flag']}
    )
    for result in results.contacted.values():
        assert result.get('failed') is True, (
            "Expected module to fail on invalid status flag 'not_a_flag' but it succeeded"
        )
        msg = result.get('msg', '') + result.get('stderr', '')
        assert 'not_a_flag' in msg, (
            "Expected error message to reference the invalid value, got: {0}".format(msg)
        )


def test_filter_status_is_online(ansible_zos_module):
    """All returned volumes must have status.online=True."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['online']}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['status']['online'] is True, (
                "Volume {0} has online=False but passed the filter".format(vol['volser'])
            )


def test_filter_status_multiple_flags(ansible_zos_module):
    """All returned volumes must satisfy every flag listed in the status filter."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['online', 'allocated']}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            st = vol['status']
            assert st['online'] is True, (
                "Volume {0} has online=False".format(vol['volser'])
            )
            assert st['allocated'] is True, (
                "Volume {0} has allocated=False".format(vol['volser'])
            )


def test_filter_status_valid_choices_accepted(ansible_zos_module):
    """Every valid status flag name should be accepted without failure."""
    hosts = ansible_zos_module
    valid_flags = [
        'online', 'offline_pending', 'mount_reserved',
        'unload_pending', 'allocated', 'permanently_resident',
        'system_residence', 'status_indicator',
    ]
    for flag in valid_flags:
        results = hosts.all.zos_volume_free(
            filter={'status': [flag]}
        )
        for result in results.contacted.values():
            assert result.get('failed') is not True, (
                "Module unexpectedly failed for valid status flag '{0}': {1}".format(
                    flag, result.get('msg', '')
                )
            )


# ---------------------------------------------------------------------------
# Gap 1: device number case-insensitivity
# ---------------------------------------------------------------------------

def test_query_device_number_case_insensitive(ansible_zos_module, volumes_unit_on_systems):
    """Device number matching should be case-insensitive — lowercase input must match."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_unit_on_systems)
    vol_name, device_addr = vols.get_available_vol_addr()

    results = hosts.all.zos_volume_free(device_numbers=[device_addr.lower()])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        device_numbers = [v['device_number'].upper() for v in result.get('volumes', [])]
        assert device_addr.upper() in device_numbers, (
            "Expected device {0} in results for lowercase input {1}".format(
                device_addr.upper(), device_addr.lower()
            )
        )

    vols.free_vol(vol_name)


# ---------------------------------------------------------------------------
# Gap 2: empty status list returns all volumes (no filter applied)
# ---------------------------------------------------------------------------

def test_filter_status_empty_list_returns_all(ansible_zos_module):
    """An empty status list should apply no UCB filter — all volumes are returned."""
    hosts = ansible_zos_module
    # Baseline: total volumes with no filter.
    baseline_results = hosts.all.zos_volume_free()
    # Filtered: empty status list.
    filtered_results = hosts.all.zos_volume_free(filter={'status': []})

    for host in baseline_results.contacted:
        baseline_count = len(baseline_results.contacted[host].get('volumes', []))
        filtered_count = len(filtered_results.contacted[host].get('volumes', []))
        assert filtered_results.contacted[host].get('failed') is not True
        assert filtered_count == baseline_count, (
            "Expected {0} volumes with empty status filter but got {1}".format(
                baseline_count, filtered_count
            )
        )


# ---------------------------------------------------------------------------
# Gap 3: free_space_min + free_space_max range together
# ---------------------------------------------------------------------------

def test_filter_free_space_range(ansible_zos_module):
    """All returned volumes should satisfy both free_space_min and free_space_max."""
    hosts = ansible_zos_module
    min_tracks = 10
    max_tracks = 999999
    results = hosts.all.zos_volume_free(
        filter={'free_space_min': min_tracks, 'free_space_max': max_tracks, 'unit': 'tracks'}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['free_space'] >= min_tracks, (
                "Volume {0} free_space={1} is below min {2}".format(
                    vol['volser'], vol['free_space'], min_tracks
                )
            )
            assert vol['free_space'] <= max_tracks, (
                "Volume {0} free_space={1} is above max {2}".format(
                    vol['volser'], vol['free_space'], max_tracks
                )
            )


# ---------------------------------------------------------------------------
# Gap 4: status + vtoc_indexed combined filter
# ---------------------------------------------------------------------------

def test_filter_combined_status_and_vtoc(ansible_zos_module):
    """Combined status + vtoc_indexed filter: all results must satisfy both."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(
        filter={'status': ['online'], 'vtoc_indexed': True}
    )
    for result in results.contacted.values():
        assert result.get('failed') is not True
        for vol in result.get('volumes', []):
            assert vol['status']['online'] is True, (
                "Volume {0} has online=False but passed the filter".format(vol['volser'])
            )
            assert vol['vtoc_info']['index_vtoc'] is True, (
                "Volume {0} has index_vtoc=False but passed the vtoc_indexed filter".format(
                    vol['volser']
                )
            )


# ---------------------------------------------------------------------------
# Gap 5: msg count matches len(volumes) and singular/plural is correct
# ---------------------------------------------------------------------------

def test_return_msg_volume_count(ansible_zos_module, volumes_on_systems):
    """msg should use singular 'matching volume' or plural 'matching volumes' correctly."""
    hosts = ansible_zos_module

    # Case 1: query returning exactly one volume — expect singular.
    vols = Volume_Handler(volumes_on_systems)
    vol_name = vols.get_available_vol()
    results = hosts.all.zos_volume_free(volumes=[vol_name])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        msg = result.get('msg', '')
        assert 'Found 1 matching volume.' in msg, (
            "Expected 'Found 1 matching volume.' in msg, got: {0!r}".format(msg)
        )
    vols.free_vol(vol_name)

    # Case 2: query all — expect plural when count > 1.
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        count = len(result.get('volumes', []))
        msg = result.get('msg', '')
        if count > 1:
            assert 'Found {0} matching volumes.'.format(count) in msg, (
                "Expected 'Found {0} matching volumes.' in msg, got: {1!r}".format(count, msg)
            )


# ---------------------------------------------------------------------------
# Gap 6: consistent messaging — "Found N matching volume(s)" / "No matching volumes found."
# ---------------------------------------------------------------------------

def test_msg_single_existing_volser(ansible_zos_module, volumes_on_systems):
    """Single existing VOLSER: msg should say 'Found 1 matching volume.'"""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_on_systems)
    vol_name = vols.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        msg = result.get('msg', '')
        assert 'Found 1 matching volume.' in msg, (
            "Expected 'Found 1 matching volume.' in msg, got: {0!r}".format(msg)
        )
        assert 'not found or inaccessible' not in msg, (
            "Unexpected unavailability notice in msg for existing volume: {0!r}".format(msg)
        )

    vols.free_vol(vol_name)


def test_msg_single_nonexistent_volser_no_fail(ansible_zos_module):
    """Single nonexistent VOLSER: module succeeds, rc=0, volumes=[], msg lists unavailable."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(volumes=["XXXXXX"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('rc') == 0, (
            "Expected rc=0 for nonexistent single VOLSER, got rc={0}".format(result.get('rc'))
        )
        assert result.get('volumes') == []
        msg = result.get('msg', '')
        assert 'No matching volumes found.' in msg, (
            "Expected 'No matching volumes found.' in msg, got: {0!r}".format(msg)
        )
        assert 'XXXXXX' in msg, (
            "Expected unavailable volser 'XXXXXX' listed in msg, got: {0!r}".format(msg)
        )


def test_msg_multi_volser_one_missing(ansible_zos_module, volumes_on_systems):
    """Two VOLSERs, one exists, one does not: msg says 'Found 1 matching volume.' and lists missing."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_on_systems)
    vol_name = vols.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name, "XXXXXX"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('rc') == 0
        result_volsers = [v['volser'] for v in result.get('volumes', [])]
        assert vol_name in result_volsers, (
            "Expected existing volser {0} in results".format(vol_name)
        )
        assert len(result.get('volumes', [])) == 1, (
            "Expected exactly 1 volume in results, got {0}".format(len(result.get('volumes', [])))
        )
        msg = result.get('msg', '')
        assert 'Found 1 matching volume.' in msg, (
            "Expected 'Found 1 matching volume.' in msg, got: {0!r}".format(msg)
        )
        assert 'XXXXXX' in msg, (
            "Expected unavailable volser 'XXXXXX' listed in msg, got: {0!r}".format(msg)
        )
        assert 'Volumes not found or inaccessible' in msg, (
            "Expected unavailability notice in msg, got: {0!r}".format(msg)
        )

    vols.free_vol(vol_name)


def test_msg_multi_volser_both_missing(ansible_zos_module):
    """Two nonexistent VOLSERs: module succeeds, volumes=[], msg lists both as unavailable."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(volumes=["XXXXXX", "YYYYYY"])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        assert result.get('rc') == 0
        assert result.get('volumes') == [], (
            "Expected empty volumes list, got: {0}".format(result.get('volumes'))
        )
        msg = result.get('msg', '')
        assert 'No matching volumes found.' in msg, (
            "Expected 'No matching volumes found.' in msg, got: {0!r}".format(msg)
        )
        assert 'XXXXXX' in msg, (
            "Expected 'XXXXXX' in unavailable list in msg, got: {0!r}".format(msg)
        )
        assert 'YYYYYY' in msg, (
            "Expected 'YYYYYY' in unavailable list in msg, got: {0!r}".format(msg)
        )
        assert 'Volumes not found or inaccessible' in msg, (
            "Expected unavailability notice in msg, got: {0!r}".format(msg)
        )


def test_msg_multi_volser_all_found(ansible_zos_module, volumes_on_systems):
    """Two existing VOLSERs: msg says 'Found 2 matching volumes.' with no unavailability notice."""
    hosts = ansible_zos_module
    vols = Volume_Handler(volumes_on_systems)
    vol_name_1 = vols.get_available_vol()
    vol_name_2 = vols.get_available_vol()

    results = hosts.all.zos_volume_free(volumes=[vol_name_1, vol_name_2])
    for result in results.contacted.values():
        assert result.get('failed') is not True
        msg = result.get('msg', '')
        assert 'Found 2 matching volumes.' in msg, (
            "Expected 'Found 2 matching volumes.' in msg, got: {0!r}".format(msg)
        )
        assert 'not found or inaccessible' not in msg, (
            "Unexpected unavailability notice in msg when all volumes exist: {0!r}".format(msg)
        )

    vols.free_vol(vol_name_1)
    vols.free_vol(vol_name_2)


def test_msg_query_all_plural(ansible_zos_module):
    """Query-all: msg should say 'Found N matching volumes.' (plural) when more than one volume exists."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        count = len(result.get('volumes', []))
        msg = result.get('msg', '')
        if count > 1:
            assert 'Found {0} matching volumes.'.format(count) in msg, (
                "Expected 'Found {0} matching volumes.' in msg, got: {1!r}".format(count, msg)
            )
        elif count == 1:
            assert 'Found 1 matching volume.' in msg, (
                "Expected 'Found 1 matching volume.' in msg, got: {0!r}".format(msg)
            )
        else:
            assert 'No matching volumes found.' in msg


def test_msg_nonexistent_volser_no_unavailable_when_query_all(ansible_zos_module):
    """Query-all with no filter: msg must not contain unavailability notice (no specific volser requested)."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free()
    for result in results.contacted.values():
        assert result.get('failed') is not True
        msg = result.get('msg', '')
        assert 'not found or inaccessible' not in msg, (
            "Unexpected unavailability notice in query-all msg: {0!r}".format(msg)
        )


def test_rc_zero_on_nonexistent_volser(ansible_zos_module):
    """rc should be 0 for a nonexistent single VOLSER — BGYSC6606E is treated as not-found, not error."""
    hosts = ansible_zos_module
    results = hosts.all.zos_volume_free(volumes=["XXXXXX"])
    for result in results.contacted.values():
        assert result.get('rc') == 0, (
            "Expected rc=0 for nonexistent VOLSER, got rc={0}".format(result.get('rc'))
        )
        assert result.get('failed') is not True


# ---------------------------------------------------------------------------
# Cross-validation: compare module output against vf -j CLI
# ---------------------------------------------------------------------------

# UCB flag mapping: module key -> vf JSON status key (uppercase in vf output)
_UCB_MAP = [
    ('online',               'UCBONLI'),
    ('offline_pending',      'UCBCHGS'),
    ('mount_reserved',       'UCBRESV'),
    ('unload_pending',       'UCBUNLD'),
    ('allocated',            'UCBALOC'),
    ('permanently_resident', 'UCBPRES'),
    ('system_residence',     'UCBSYSR'),
    ('status_indicator',     'UCBDADI'),
]


def _get_vf_vol(hosts, vol_name):
    """Run ``vf -j -- <vol_name>`` and return the matching volume dict.

    Returns None if vf fails or returns no entry for the volser (e.g. the
    volume name is invalid or not active as a DASD volume).
    """
    import json
    cli_results = hosts.all.shell(cmd="vf -j -- {0}".format(vol_name))
    for result in cli_results.contacted.values():
        if result.get('rc') != 0:
            print("Skipping {0}: vf rc={1} — {2}".format(
                vol_name, result.get('rc'), result.get('stdout', '').strip()
            ))
            return None
        cli_json = json.loads(result.get('stdout', '{}'))
        cli_volumes = cli_json.get('data', {}).get('volumes', [])
        return next(
            (v for v in cli_volumes if v.get('volser', '').upper() == vol_name.upper()),
            None
        )
    return None


def _assert_vol_matches_vf(mod_vol, cli_vol):
    """Assert every comparable field in mod_vol matches the vf CLI output."""
    assert mod_vol['volser'].upper() == cli_vol['volser'].upper(), (
        "volser: module={0}, vf={1}".format(mod_vol['volser'], cli_vol['volser'])
    )
    assert mod_vol['device_number'].upper() == cli_vol['unit'].upper(), (
        "device_number: module={0}, vf={1}".format(mod_vol['device_number'], cli_vol['unit'])
    )
    assert mod_vol['total_space'] == int(cli_vol['total_tracks']), (
        "total_space: module={0}, vf={1}".format(mod_vol['total_space'], cli_vol['total_tracks'])
    )
    assert mod_vol['free_space'] == int(cli_vol['free_tracks']), (
        "free_space: module={0}, vf={1}".format(mod_vol['free_space'], cli_vol['free_tracks'])
    )
    # vf free_kilobytes/total_kilobytes are already in KB — compare directly
    assert mod_vol['total_kilobytes'] == int(cli_vol['total_kilobytes']), (
        "total_kilobytes: module={0}, vf={1}".format(mod_vol['total_kilobytes'], cli_vol['total_kilobytes'])
    )
    assert mod_vol['free_kilobytes'] == int(cli_vol['free_kilobytes']), (
        "free_kilobytes: module={0}, vf={1}".format(mod_vol['free_kilobytes'], cli_vol['free_kilobytes'])
    )
    assert mod_vol['vtoc_info']['index_vtoc'] == bool(cli_vol['index_vtoc']), (
        "index_vtoc: module={0}, vf={1}".format(
            mod_vol['vtoc_info']['index_vtoc'], cli_vol['index_vtoc'])
    )
    assert mod_vol['vtoc_info']['vtoc_active'] == bool(cli_vol['vtoc_active']), (
        "vtoc_active: module={0}, vf={1}".format(
            mod_vol['vtoc_info']['vtoc_active'], cli_vol['vtoc_active'])
    )
    assert mod_vol['is_cylinder_managed'] == bool(cli_vol['is_cylinder_managed']), (
        "is_cylinder_managed: module={0}, vf={1}".format(
            mod_vol['is_cylinder_managed'], cli_vol['is_cylinder_managed'])
    )
    cli_status = cli_vol['status']
    for flag, ucb_key in _UCB_MAP:
        expected = bool(cli_status.get(ucb_key, False))
        actual = mod_vol['status'][flag]
        assert actual == expected, (
            "status.{0}: module={1}, vf[{2}]={3}".format(flag, actual, ucb_key, expected)
        )


def test_volume_info_matches_vf_command(ansible_zos_module, volumes_on_systems):
    """Module output must match 'vf -j -- <volser>' CLI output for up to 5 volumes.

    For each volume:
      1. Run ``vf -j -- <volser>`` and parse data.volumes[0].
      2. Run zos_volume_free for the same volser.
      3. Compare every numeric, boolean, and identity field.

    vf -j JSON structure (confirmed from live run):
      data.volumes[0]: unit, volser, free_tracks, total_tracks,
      free_kilobytes, total_kilobytes, index_vtoc, vtoc_active,
      is_cylinder_managed, status{UCBONLI..UCBSYSR}
    """
    hosts = ansible_zos_module
    vol_handler = Volume_Handler(volumes_on_systems)

    acquired = []
    validated = 0
    try:
        for _ in range(len(volumes_on_systems)):
            if validated >= 5:
                break
            vol_name = vol_handler.get_available_vol()
            acquired.append(vol_name)

            # ── Step 1: vf CLI — skip volumes vf cannot query ─────────────────
            cli_vol = _get_vf_vol(hosts, vol_name)
            if cli_vol is None:
                print("Skipping {0}: vf -j returned no data.".format(vol_name))
                continue

            # ── Step 2: module ────────────────────────────────────────────────
            mod_results = hosts.all.zos_volume_free(volumes=[vol_name])
            for result in mod_results.contacted.values():
                assert result.get('failed') is not True, (
                    "zos_volume_free failed for {0}: {1}".format(vol_name, result.get('msg', ''))
                )
                mod_vols = result.get('volumes', [])
                assert len(mod_vols) == 1, (
                    "Expected 1 volume for {0}, got {1}".format(vol_name, len(mod_vols))
                )
                # ── Step 3: compare ───────────────────────────────────────────
                _assert_vol_matches_vf(mod_vols[0], cli_vol)

            validated += 1

        assert validated > 0, (
            "No valid volumes found in fixture to compare against vf CLI."
        )

    finally:
        for vol_name in acquired:
            vol_handler.free_vol(vol_name)
