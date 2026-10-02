#!/usr/bin/python
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

import json
import pytest

__metaclass__ = type

# The following tests are for the stat filter found in plugins/filter/stat.py.
# You may notice that the dictionary used in the majority of testing contains
# attributes about a sequential data set. The actual content of the return JSON is not
# important for verifying the filter for files, aggregates or GDGs. What's important
# are the attributes leftover after executing the filter.
# The test JSON does matter for verifying the filter with data sets, as each type affects
# the fields that remain.

def test_filter_seq_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null, "allocation_available": 93,
    "allocation_used": 0, "atime": null, "audit_bits": null, "auditfid": null, "bitmap_file_size": null,
    "block_size": 27920, "blocks_per_track": 2, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-03", "creation_time": null, "ctime": null, "data": {"avg_record_length": null,
    "bufspace": null, "device_type": null, "key_length": null, "key_offset": null, "max_record_length": null,
    "spanned": null, "total_records": null, "volser": null}, "dev": null, "device_type": "3390",
    "dir_blocks_allocated": null, "dir_blocks_used": null, "dsorg": "ps", "empty": null, "encrypted": false,
    "executable": null, "expiration_date": null, "extended": null, "extended_attrs_bits": null, "extents_allocated": 1,
    "extents_used": 0, "file_format": null, "filesystem_table_size": null, "free": null, "free_1k_fragments": null,
    "free_8k_blocks": null, "gid": null, "gr_name": null, "has_extended_attrs": false,
    "index": {"avg_record_length": null, "bufspace": null, "device_type": null, "key_length": null, "key_offset": null,
    "max_record_length": null, "total_records": null, "volser": null}, "inode": null, "isblk": null, "ischr": null,
    "isdir": null, "isfifo": null, "isgid": null, "islnk": null, "isreg": null, "issock": null, "isuid": null,
    "jcl_attrs": {"creation_job": null, "creation_step": null}, "key_label": null, "key_status": "none",
    "last_reference": null, "limit": null, "lnk_source": null, "lnk_target": null, "log_file_size": null,
    "max_pdse_generation": null, "members": null, "mimetype": null, "missing_volumes": [], "mode": null,
    "mtime": null, "nlink": null, "num_volumes": 1, "order": null, "pages_allocated": null, "pages_used": null,
    "pdse_version": null, "perc_pages_used": null, "primary_space": 93, "purge": null, "pw_name": null,
    "quiesced": {"job": null, "system": null, "timestamp": null}, "racf": "none", "readable": null,
    "record_format": "fb", "record_length": 80, "rgrp": null, "roth": null, "rusr": null, "scratch": null,
    "secondary_space": 56, "seq_type": "basic", "size": null, "sms_data_class": null, "sms_mgmt_class": null,
    "sms_storage_class": null, "space_units": "track", "sysplex_aware": null, "total_size": null,
    "tracks_per_cylinder": 15, "type": "seq", "uid": null, "updated_since_backup": false, "version": null,
    "volser": "222222", "volumes": ["222222"], "wgrp": null, "woth": null, "writeable": null, "wusr": null,
    "xgrp": null, "xoth": null, "xusr": null}, "exists": true, "isaggregate": false, "isdataset": true,
    "isfile": false, "isgdg": false, "name": "omvsadm.stat.test.seq", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic data set information (12 attributes).
        assert 'creation_date' in stat['attributes']      
        assert 'dsorg' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']        
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']        
        assert 'type' in stat['attributes']

        # Checking for sequential-data-set-specific information (22 attributes).
        assert 'allocation_available' in stat['attributes']
        assert 'allocation_used' in stat['attributes']
        assert 'block_size' in stat['attributes']
        assert 'blocks_per_track' in stat['attributes']
        assert 'creation_time' in stat['attributes']  
        assert 'device_type' in stat['attributes']
        assert 'extents_allocated' in stat['attributes']
        assert 'extents_used' in stat['attributes']
        assert 'jcl_attrs' in stat['attributes']
        assert 'last_reference' in stat['attributes']
        assert 'missing_volumes' in stat['attributes']
        assert 'num_volumes' in stat['attributes']
        assert 'primary_space' in stat['attributes']    
        assert 'record_format' in stat['attributes']
        assert 'record_length' in stat['attributes']
        assert 'secondary_space' in stat['attributes']
        assert 'space_units' in stat['attributes']
        assert 'tracks_per_cylinder' in stat['attributes']
        assert 'updated_since_backup' in stat['attributes']
        assert 'volser' in stat['attributes']
        assert 'volumes' in stat['attributes']

        assert 'seq_type' in stat['attributes']

        # There are a total of 34 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 34


def test_filter_pdse_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null,
    "allocation_available": 93, "allocation_used": null, "atime": null, "audit_bits": null,
    "auditfid": null, "bitmap_file_size": null, "block_size": 32720,
    "blocks_per_track": null, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-03", "creation_time": null, "ctime": null,
    "data": {"avg_record_length": null, "bufspace": null, "device_type": null,
    "key_length": null, "key_offset": null, "max_record_length": null, "spanned": null,
    "total_records": null, "volser": null}, "dev": null, "device_type": "3390",
    "dir_blocks_allocated": null, "dir_blocks_used": null, "dsorg": "po",
    "empty": null, "encrypted": false, "executable": null, "expiration_date": null,
    "extended": null, "extended_attrs_bits": null, "extents_allocated": 1,
    "extents_used": null, "file_format": null, "filesystem_table_size": null,
    "free": null, "free_1k_fragments": null, "free_8k_blocks": null, "gid": null,
    "gr_name": null, "has_extended_attrs": false, "index": {"avg_record_length": null,
    "bufspace": null, "device_type": null, "key_length": null, "key_offset": null,
    "max_record_length": null, "total_records": null, "volser": null}, "inode": null,
    "isblk": null, "ischr": null, "isdir": null, "isfifo": null, "isgid": null,
    "islnk": null, "isreg": null, "issock": null, "isuid": null,
    "jcl_attrs": {"creation_job": null, "creation_step": null}, "key_label": null,
    "key_status": "none", "last_reference": null, "limit": null, "lnk_source": null,
    "lnk_target": null, "log_file_size": null, "max_pdse_generation": 0,
    "members": 0, "mimetype": null, "missing_volumes": [], "mode": null,
    "mtime":null, "nlink": null, "num_volumes": 1, "order": null,
    "pages_allocated": 1116, "pages_used": 5, "pdse_version": 1, "perc_pages_used": 0,
    "primary_space": 93, "purge": null, "pw_name": null,
    "quiesced": {"job": null, "system": null, "timestamp": null},
    "racf": "none", "readable": null, "record_format": "fb", "record_length": 80,
    "rgrp": null, "roth": null, "rusr": null, "scratch": null, "secondary_space": 56,
    "seq_type": null, "size": null, "sms_data_class": null, "sms_mgmt_class": null,
    "sms_storage_class": null, "space_units": "track", "sysplex_aware": null,
    "total_size": null, "tracks_per_cylinder": 15, "type": "pdse", "uid": null,
    "updated_since_backup": false, "version": null, "volser": "222222",
    "volumes": ["222222"], "wgrp": null, "woth": null, "writeable": null,
    "wusr": null, "xgrp": null, "xoth": null, "xusr": null}, "exists": true,
    "isaggregate": false, "isdataset": true, "isfile": false, "isgdg": false,
    "name": "omvsadm.stat.test.pdse", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic data set information (12 attributes).
        assert 'creation_date' in stat['attributes']      
        assert 'dsorg' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']        
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']        
        assert 'type' in stat['attributes']

        # Checking for partitioned-data-set-specific information (30 attributes).
        assert 'allocation_available' in stat['attributes']
        assert 'allocation_used' in stat['attributes']
        assert 'block_size' in stat['attributes']
        assert 'blocks_per_track' in stat['attributes']
        assert 'creation_time' in stat['attributes']
        assert 'device_type' in stat['attributes']
        assert 'extents_allocated' in stat['attributes']
        assert 'extents_used' in stat['attributes']
        assert 'jcl_attrs' in stat['attributes']
        assert 'last_reference' in stat['attributes']
        assert 'missing_volumes' in stat['attributes']
        assert 'num_volumes' in stat['attributes']
        assert 'primary_space' in stat['attributes']
        assert 'record_format' in stat['attributes']
        assert 'record_length' in stat['attributes']
        assert 'secondary_space' in stat['attributes']
        assert 'space_units' in stat['attributes']
        assert 'tracks_per_cylinder' in stat['attributes']
        assert 'updated_since_backup' in stat['attributes']
        assert 'volser' in stat['attributes']
        assert 'volumes' in stat['attributes']

        assert 'dir_blocks_allocated' in stat['attributes']
        assert 'dir_blocks_used' in stat['attributes']
        assert 'max_pdse_generation' in stat['attributes']
        assert 'member_details' in stat['attributes']
        assert 'members' in stat['attributes']
        assert 'pages_allocated' in stat['attributes']
        assert 'pages_used' in stat['attributes']
        assert 'pdse_version' in stat['attributes']
        assert 'perc_pages_used' in stat['attributes']

        # There are a total of 42 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 42


# Full VSAM component sub-keys expected by zos_stat (matching assert_vsam_component
# in test_zos_stat_func.py).
VSAM_COMPONENT_KEYS = [
    'name',
    'avg_record_length',
    'max_record_length',
    'bufspace',
    'total_records',
    'spanned',
    'volser',
    'device_type',
    'key_length',
    'key_offset',
    'control_interval_size',
    'share_option_region',
    'share_option_system',
    'erase',
    'reuse',
    'recovery',
    'speed',
    'statistics',
]

# Keys inside the statistics sub-dict of a VSAM component.
VSAM_STATISTICS_KEYS = [
    'total_records',
    'deleted_records',
    'inserted_records',
    'updated_records',
    'retrieved_records',
    'control_interval_splits',
    'control_area_splits',
    'free_space_percentage_ci',
    'free_space_percentage_ca',
    'free_space',
]


def _assert_vsam_component_keys(component, label):
    """Assert that a VSAM component dict contains all expected sub-keys and that
    the statistics sub-dict has the correct shape.

    Arguments:
        component (dict) -- The data or index component from stat['attributes'].
        label (str) -- Human-readable label used in assertion failure messages.
    """
    assert isinstance(component, dict), f"{label} must be a dict"
    for key in VSAM_COMPONENT_KEYS:
        assert key in component, f"{label} missing key '{key}'"

    stats = component.get('statistics')
    assert isinstance(stats, dict), f"{label}.statistics must be a dict"
    for field in VSAM_STATISTICS_KEYS:
        assert field in stats, f"{label}.statistics missing field '{field}'"
        assert stats[field] is None or isinstance(stats[field], int), (
            f"{label}.statistics['{field}'] must be int or None, "
            f"got {type(stats[field])}"
        )


def test_filter_vsam_ksds(ansible_zos_module):
    """KSDS: both data and index components present; filter retains 14 keys
    (12 generic data_set + data + index) and all component sub-keys survive."""
    hosts = ansible_zos_module

    # Full modern shape as returned by zos_stat for a KSDS.
    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": null,
                "allocation_used": null, "atime": null, "audit_bits": null,
                "auditfid": null, "bitmap_file_size": null, "block_size": null,
                "blocks_per_track": null, "charset": null, "checksum": null,
                "converttov5": null, "creation_date": "2025-11-06",
                "creation_time": null, "ctime": null,
                "data": {
                    "avg_record_length": 80,
                    "bufspace": 37376,
                    "control_interval_size": 4096,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": 5,
                    "key_offset": 1,
                    "max_record_length": 80,
                    "name": "OMVSADM.STAT.FILTER.VSAM.DATA",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 0,
                        "deleted_records": 0,
                        "inserted_records": 0,
                        "updated_records": 0,
                        "retrieved_records": 0,
                        "control_interval_splits": 0,
                        "control_area_splits": 0,
                        "free_space_percentage_ci": 0,
                        "free_space_percentage_ca": 0,
                        "free_space": 0
                    },
                    "total_records": 0,
                    "volser": "333333"
                },
                "dev": null, "device_type": null,
                "dir_blocks_allocated": null, "dir_blocks_used": null,
                "dsorg": "vsam", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": null,
                "extents_used": null, "file_format": null,
                "filesystem_table_size": null, "free": null,
                "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": {
                    "avg_record_length": 505,
                    "bufspace": 0,
                    "control_interval_size": 512,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": 5,
                    "key_offset": 1,
                    "max_record_length": 0,
                    "name": "OMVSADM.STAT.FILTER.VSAM.INDEX",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 0,
                        "deleted_records": 0,
                        "inserted_records": 0,
                        "updated_records": 0,
                        "retrieved_records": 0,
                        "control_interval_splits": 0,
                        "control_area_splits": 0,
                        "free_space_percentage_ci": 0,
                        "free_space_percentage_ca": 0,
                        "free_space": 0
                    },
                    "total_records": 0,
                    "volser": "333333"
                },
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": null,
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "member_details": null, "members": null, "mimetype": null,
                "missing_volumes": null, "mode": null, "mtime": null,
                "nlink": null, "num_volumes": null, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": null, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "no", "readable": null, "record_format": null,
                "record_length": null, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": null, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": null,
                "sysplex_aware": null, "total_size": null,
                "tracks_per_cylinder": null, "type": "ksds", "uid": null,
                "updated_since_backup": null, "version": null, "volser": null,
                "volumes": null, "wgrp": null, "woth": null, "writeable": null,
                "wusr": null, "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.STAT.FILTER.VSAM",
            "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic data set information (12 attributes).
        assert 'creation_date' in stat['attributes']
        assert 'dsorg' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']
        assert 'type' in stat['attributes']

        # Checking for VSAM-specific information (2 top-level attributes).
        assert 'data' in stat['attributes']
        assert 'index' in stat['attributes']

        # There are a total of 14 attributes, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 14

        # Verify data component sub-keys and statistics shape.
        _assert_vsam_component_keys(stat['attributes']['data'], 'data')
        assert stat['attributes']['data']['key_length'] == 5
        assert stat['attributes']['data']['key_offset'] == 1

        # Verify index component sub-keys and statistics shape.
        _assert_vsam_component_keys(stat['attributes']['index'], 'index')


def test_filter_vsam_esds(ansible_zos_module):
    """ESDS: index is None; filter retains 14 keys (12 generic + data + index).
    The data component carries all expected sub-keys; index passes through as None."""
    hosts = ansible_zos_module

    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": null,
                "allocation_used": null, "atime": null, "audit_bits": null,
                "auditfid": null, "bitmap_file_size": null, "block_size": null,
                "blocks_per_track": null, "charset": null, "checksum": null,
                "converttov5": null, "creation_date": "2025-11-06",
                "creation_time": null, "ctime": null,
                "data": {
                    "avg_record_length": 80,
                    "bufspace": 37376,
                    "control_interval_size": 4096,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": null,
                    "key_offset": null,
                    "max_record_length": 80,
                    "name": "OMVSADM.STAT.FILTER.ESDS.DATA",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 0,
                        "deleted_records": 0,
                        "inserted_records": 0,
                        "updated_records": 0,
                        "retrieved_records": 0,
                        "control_interval_splits": 0,
                        "control_area_splits": 0,
                        "free_space_percentage_ci": 0,
                        "free_space_percentage_ca": 0,
                        "free_space": 0
                    },
                    "total_records": 0,
                    "volser": "333333"
                },
                "dev": null, "device_type": null,
                "dir_blocks_allocated": null, "dir_blocks_used": null,
                "dsorg": "vsam", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": null,
                "extents_used": null, "file_format": null,
                "filesystem_table_size": null, "free": null,
                "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": null,
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": null,
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "member_details": null, "members": null, "mimetype": null,
                "missing_volumes": null, "mode": null, "mtime": null,
                "nlink": null, "num_volumes": null, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": null, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "no", "readable": null, "record_format": null,
                "record_length": null, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": null, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": null,
                "sysplex_aware": null, "total_size": null,
                "tracks_per_cylinder": null, "type": "esds", "uid": null,
                "updated_since_backup": null, "version": null, "volser": null,
                "volumes": null, "wgrp": null, "woth": null, "writeable": null,
                "wusr": null, "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.STAT.FILTER.ESDS",
            "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is True
        assert stat.get('isdataset') is True
        assert stat.get('attributes') is not None

        # 12 generic data_set + data + index = 14 total.
        assert len(stat['attributes'].keys()) == 14

        # Verify type.
        assert stat['attributes']['type'] == 'esds'
        assert stat['attributes']['dsorg'] == 'vsam'

        # ESDS has no index component — must be None after filter.
        assert stat['attributes']['index'] is None, (
            "index must be None for ESDS"
        )

        # data component must be present with all expected sub-keys.
        _assert_vsam_component_keys(stat['attributes']['data'], 'data')

        # ESDS has no keys — key_length and key_offset must be None.
        assert stat['attributes']['data']['key_length'] is None, (
            "ESDS key_length must be None"
        )
        assert stat['attributes']['data']['key_offset'] is None, (
            "ESDS key_offset must be None"
        )


def test_filter_vsam_rrds(ansible_zos_module):
    """RRDS: index is None; data component present but key fields are None.
    Filter retains 14 keys (12 generic + data + index)."""
    hosts = ansible_zos_module

    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": null,
                "allocation_used": null, "atime": null, "audit_bits": null,
                "auditfid": null, "bitmap_file_size": null, "block_size": null,
                "blocks_per_track": null, "charset": null, "checksum": null,
                "converttov5": null, "creation_date": "2025-11-06",
                "creation_time": null, "ctime": null,
                "data": {
                    "avg_record_length": 80,
                    "bufspace": 37376,
                    "control_interval_size": 4096,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": null,
                    "key_offset": null,
                    "max_record_length": 80,
                    "name": "OMVSADM.STAT.FILTER.RRDS.DATA",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 0,
                        "deleted_records": 0,
                        "inserted_records": 0,
                        "updated_records": 0,
                        "retrieved_records": 0,
                        "control_interval_splits": 0,
                        "control_area_splits": 0,
                        "free_space_percentage_ci": 0,
                        "free_space_percentage_ca": 0,
                        "free_space": 0
                    },
                    "total_records": 0,
                    "volser": "333333"
                },
                "dev": null, "device_type": null,
                "dir_blocks_allocated": null, "dir_blocks_used": null,
                "dsorg": "vsam", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": null,
                "extents_used": null, "file_format": null,
                "filesystem_table_size": null, "free": null,
                "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": null,
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": null,
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "member_details": null, "members": null, "mimetype": null,
                "missing_volumes": null, "mode": null, "mtime": null,
                "nlink": null, "num_volumes": null, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": null, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "no", "readable": null, "record_format": null,
                "record_length": null, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": null, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": null,
                "sysplex_aware": null, "total_size": null,
                "tracks_per_cylinder": null, "type": "rrds", "uid": null,
                "updated_since_backup": null, "version": null, "volser": null,
                "volumes": null, "wgrp": null, "woth": null, "writeable": null,
                "wusr": null, "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.STAT.FILTER.RRDS",
            "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        assert stat.get('exists') is True
        assert stat.get('isdataset') is True
        assert stat.get('attributes') is not None

        # 12 generic data_set + data + index = 14 total.
        assert len(stat['attributes'].keys()) == 14

        assert stat['attributes']['type'] == 'rrds'
        assert stat['attributes']['dsorg'] == 'vsam'

        # RRDS has no index component.
        assert stat['attributes']['index'] is None, (
            "index must be None for RRDS"
        )

        # data component must carry all expected sub-keys.
        _assert_vsam_component_keys(stat['attributes']['data'], 'data')

        # RRDS records have no keys.
        assert stat['attributes']['data']['key_length'] is None, (
            "RRDS key_length must be None"
        )
        assert stat['attributes']['data']['key_offset'] is None, (
            "RRDS key_offset must be None"
        )


def test_filter_vsam_statistics_values_survive_filter(ansible_zos_module):
    """Verify that non-zero statistics values in the data component survive
    the filter unchanged — the filter must not zero or null them out."""
    hosts = ansible_zos_module

    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": null,
                "allocation_used": null, "atime": null, "audit_bits": null,
                "auditfid": null, "bitmap_file_size": null, "block_size": null,
                "blocks_per_track": null, "charset": null, "checksum": null,
                "converttov5": null, "creation_date": "2025-11-06",
                "creation_time": null, "ctime": null,
                "data": {
                    "avg_record_length": 80,
                    "bufspace": 37376,
                    "control_interval_size": 4096,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": 5,
                    "key_offset": 1,
                    "max_record_length": 80,
                    "name": "OMVSADM.STAT.FILTER.VSAM.DATA",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 500,
                        "deleted_records": 10,
                        "inserted_records": 510,
                        "updated_records": 5,
                        "retrieved_records": 200,
                        "control_interval_splits": 2,
                        "control_area_splits": 1,
                        "free_space_percentage_ci": 34,
                        "free_space_percentage_ca": 50,
                        "free_space": 1024
                    },
                    "total_records": 500,
                    "volser": "333333"
                },
                "dev": null, "device_type": null,
                "dir_blocks_allocated": null, "dir_blocks_used": null,
                "dsorg": "vsam", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": null,
                "extents_used": null, "file_format": null,
                "filesystem_table_size": null, "free": null,
                "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": {
                    "avg_record_length": 505,
                    "bufspace": 0,
                    "control_interval_size": 512,
                    "device_type": "3390",
                    "erase": false,
                    "key_length": 5,
                    "key_offset": 1,
                    "max_record_length": 0,
                    "name": "OMVSADM.STAT.FILTER.VSAM.INDEX",
                    "recovery": false,
                    "reuse": false,
                    "share_option_region": 1,
                    "share_option_system": 3,
                    "spanned": false,
                    "speed": false,
                    "statistics": {
                        "total_records": 12,
                        "deleted_records": 0,
                        "inserted_records": 12,
                        "updated_records": 0,
                        "retrieved_records": 50,
                        "control_interval_splits": 0,
                        "control_area_splits": 0,
                        "free_space_percentage_ci": 80,
                        "free_space_percentage_ca": 75,
                        "free_space": 512
                    },
                    "total_records": 12,
                    "volser": "333333"
                },
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": null,
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "member_details": null, "members": null, "mimetype": null,
                "missing_volumes": null, "mode": null, "mtime": null,
                "nlink": null, "num_volumes": null, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": null, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "no", "readable": null, "record_format": null,
                "record_length": null, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": null, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": null,
                "sysplex_aware": null, "total_size": null,
                "tracks_per_cylinder": null, "type": "ksds", "uid": null,
                "updated_since_backup": null, "version": null, "volser": null,
                "volumes": null, "wgrp": null, "woth": null, "writeable": null,
                "wusr": null, "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.STAT.FILTER.VSAM",
            "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        assert stat.get('attributes') is not None

        # data statistics values must pass through unchanged.
        data_stats = stat['attributes']['data']['statistics']
        assert data_stats['total_records'] == 500
        assert data_stats['deleted_records'] == 10
        assert data_stats['inserted_records'] == 510
        assert data_stats['updated_records'] == 5
        assert data_stats['retrieved_records'] == 200
        assert data_stats['control_interval_splits'] == 2
        assert data_stats['control_area_splits'] == 1
        assert data_stats['free_space_percentage_ci'] == 34
        assert data_stats['free_space_percentage_ca'] == 50
        assert data_stats['free_space'] == 1024

        # index statistics values must pass through unchanged.
        index_stats = stat['attributes']['index']['statistics']
        assert index_stats['total_records'] == 12
        assert index_stats['inserted_records'] == 12
        assert index_stats['retrieved_records'] == 50
        assert index_stats['free_space_percentage_ci'] == 80
        assert index_stats['free_space_percentage_ca'] == 75
        assert index_stats['free_space'] == 512


def test_filter_data_set_option_no_data_set_output(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null,
    "allocation_available": null, "allocation_used": null, "atime": null, "audit_bits": null,
    "auditfid": "C8C6E2D7 D7F7DFE1 0000", "bitmap_file_size": 16, "block_size": null,
    "blocks_per_track": null, "charset": null, "checksum": null, "converttov5": false, 
    "creation_date": null, "creation_time": null, "ctime": null,
    "data": {"avg_record_length": null, "bufspace": null, "device_type": null, "key_length": null,
    "key_offset": null, "max_record_length": null, "spanned": null, "total_records": null,
    "volser": null}, "dev": null, "device_type": null, "dir_blocks_allocated": null,
    "dir_blocks_used": null, "dsorg": null, "empty": null, "encrypted": null, "executable": null,
    "expiration_date": null, "extended": null, "extended_attrs_bits": null, "extents_allocated": null,
    "extents_used": null, "file_format": null, "filesystem_table_size": 40, "free": 59087,
    "free_1k_fragments": 7, "free_8k_blocks": 7385, "gid": null, "gr_name": null,
    "has_extended_attrs": null, "index": {"avg_record_length": null, "bufspace": null,
    "device_type": null, "key_length": null, "key_offset": null, "max_record_length": null,
    "total_records": null, "volser": null}, "inode": null, "isblk": null, "ischr": null,
    "isdir": null, "isfifo": null, "isgid": null, "islnk": null, "isreg": null, "issock": null,
    "isuid": null, "jcl_attrs": {"creation_job": null, "creation_step": null},
    "key_label": null, "key_status": null, "last_reference": null, "limit": null,
    "lnk_source": null, "lnk_target": null, "log_file_size": 776, "max_pdse_generation": null,
    "members": null, "mimetype": null, "missing_volumes": null, "mode": null, "mtime": null,
    "nlink": null, "num_volumes": null, "order": null, "pages_allocated": null,
    "pages_used": null, "pdse_version": null, "perc_pages_used": null, "primary_space": null,
    "purge": null, "pw_name": null, "quiesced": {"job": null, "system": null,
    "timestamp": null}, "racf": null, "readable": null, "record_format": null,
    "record_length": null, "rgrp": null, "roth": null, "rusr": null, "scratch": null,
    "secondary_space": null, "seq_type": null, "size": null, "sms_data_class": null,
    "sms_mgmt_class": null, "sms_storage_class": null, "space_units": null, "sysplex_aware": false,
    "total_size": 77040, "tracks_per_cylinder": null, "type": null, "uid": null,
    "updated_since_backup": null, "version": "1.5", "volser": null, "volumes": null, "wgrp": null,
    "woth": null, "writeable": null, "wusr": null, "xgrp": null, "xoth": null, "xusr": null},
    "exists": true, "isaggregate": true, "isdataset": false, "isfile": false,
    "isgdg": false, "name": "zoau.v130.zfs", "resource_type": "aggregate"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic data set information (12 attributes).
        assert 'creation_date' in stat['attributes']      
        assert 'dsorg' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']        
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']        
        assert 'type' in stat['attributes']

        # There are a total of 12 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 12


def test_filter_file(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null, "allocation_available": 93,
    "allocation_used": 0, "atime": null, "audit_bits": null, "auditfid": null, "bitmap_file_size": null,
    "block_size": 27920, "blocks_per_track": 2, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-03", "creation_time": null, "ctime": null, "data": {"avg_record_length": null,
    "bufspace": null, "device_type": null, "key_length": null, "key_offset": null, "max_record_length": null,
    "spanned": null, "total_records": null, "volser": null}, "dev": null, "device_type": "3390",
    "dir_blocks_allocated": null, "dir_blocks_used": null, "dsorg": "ps", "empty": null, "encrypted": false,
    "executable": null, "expiration_date": null, "extended": null, "extended_attrs_bits": null, "extents_allocated": 1,
    "extents_used": 0, "file_format": null, "filesystem_table_size": null, "free": null, "free_1k_fragments": null,
    "free_8k_blocks": null, "gid": null, "gr_name": null, "has_extended_attrs": false,
    "index": {"avg_record_length": null, "bufspace": null, "device_type": null, "key_length": null, "key_offset": null,
    "max_record_length": null, "total_records": null, "volser": null}, "inode": null, "isblk": null, "ischr": null,
    "isdir": null, "isfifo": null, "isgid": null, "islnk": null, "isreg": null, "issock": null, "isuid": null,
    "jcl_attrs": {"creation_job": null, "creation_step": null}, "key_label": null, "key_status": "none",
    "last_reference": null, "limit": null, "lnk_source": null, "lnk_target": null, "log_file_size": null,
    "max_pdse_generation": null, "members": null, "mimetype": null, "missing_volumes": [], "mode": null,
    "mtime": null, "nlink": null, "num_volumes": 1, "order": null, "pages_allocated": null, "pages_used": null,
    "pdse_version": null, "perc_pages_used": null, "primary_space": 93, "purge": null, "pw_name": null,
    "quiesced": {"job": null, "system": null, "timestamp": null}, "racf": "none", "readable": null,
    "record_format": "fb", "record_length": 80, "rgrp": null, "roth": null, "rusr": null, "scratch": null,
    "secondary_space": 56, "seq_type": "basic", "size": null, "sms_data_class": null, "sms_mgmt_class": null,
    "sms_storage_class": null, "space_units": "track", "sysplex_aware": null, "total_size": null,
    "tracks_per_cylinder": 15, "type": "seq", "uid": null, "updated_since_backup": false, "version": null,
    "volser": "222222", "volumes": ["222222"], "wgrp": null, "woth": null, "writeable": null, "wusr": null,
    "xgrp": null, "xoth": null, "xusr": null}, "exists": true, "isaggregate": false, "isdataset": true,
    "isfile": false, "isgdg": false, "name": "omvsadm.stat.test.seq", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('file') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for file-specific information (41 attributes).
        assert 'atime' in stat['attributes']
        assert 'audit_bits' in stat['attributes']
        assert 'charset' in stat['attributes']
        assert 'checksum' in stat['attributes']
        assert 'ctime' in stat['attributes']
        assert 'dev' in stat['attributes']
        assert 'executable' in stat['attributes']
        assert 'extended_attrs_bits' in stat['attributes']
        assert 'file_format' in stat['attributes']
        assert 'gid' in stat['attributes']
        assert 'gr_name' in stat['attributes']
        assert 'inode' in stat['attributes']
        assert 'isblk' in stat['attributes']
        assert 'ischr' in stat['attributes']
        assert 'isdir' in stat['attributes']
        assert 'isfifo' in stat['attributes']
        assert 'isgid' in stat['attributes']
        assert 'islnk' in stat['attributes']
        assert 'isreg' in stat['attributes']
        assert 'issock' in stat['attributes']
        assert 'isuid' in stat['attributes']
        assert 'lnk_source' in stat['attributes']
        assert 'lnk_target' in stat['attributes']
        assert 'mimetype' in stat['attributes']
        assert 'mode' in stat['attributes']
        assert 'mtime' in stat['attributes']
        assert 'nlink' in stat['attributes']
        assert 'pw_name' in stat['attributes']
        assert 'readable' in stat['attributes']
        assert 'rgrp' in stat['attributes']
        assert 'roth' in stat['attributes']
        assert 'rusr' in stat['attributes']
        assert 'size' in stat['attributes']
        assert 'uid' in stat['attributes']
        assert 'wgrp' in stat['attributes']
        assert 'woth' in stat['attributes']
        assert 'writeable' in stat['attributes']
        assert 'wusr' in stat['attributes']
        assert 'xgrp' in stat['attributes']
        assert 'xoth' in stat['attributes']
        assert 'xusr' in stat['attributes']

        # There are a total of 41 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 41


def test_filter_aggregate(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null, "allocation_available": 93,
    "allocation_used": 0, "atime": null, "audit_bits": null, "auditfid": null, "bitmap_file_size": null,
    "block_size": 27920, "blocks_per_track": 2, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-03", "creation_time": null, "ctime": null, "data": {"avg_record_length": null,
    "bufspace": null, "device_type": null, "key_length": null, "key_offset": null, "max_record_length": null,
    "spanned": null, "total_records": null, "volser": null}, "dev": null, "device_type": "3390",
    "dir_blocks_allocated": null, "dir_blocks_used": null, "dsorg": "ps", "empty": null, "encrypted": false,
    "executable": null, "expiration_date": null, "extended": null, "extended_attrs_bits": null, "extents_allocated": 1,
    "extents_used": 0, "file_format": null, "filesystem_table_size": null, "free": null, "free_1k_fragments": null,
    "free_8k_blocks": null, "gid": null, "gr_name": null, "has_extended_attrs": false,
    "index": {"avg_record_length": null, "bufspace": null, "device_type": null, "key_length": null, "key_offset": null,
    "max_record_length": null, "total_records": null, "volser": null}, "inode": null, "isblk": null, "ischr": null,
    "isdir": null, "isfifo": null, "isgid": null, "islnk": null, "isreg": null, "issock": null, "isuid": null,
    "jcl_attrs": {"creation_job": null, "creation_step": null}, "key_label": null, "key_status": "none",
    "last_reference": null, "limit": null, "lnk_source": null, "lnk_target": null, "log_file_size": null,
    "max_pdse_generation": null, "members": null, "mimetype": null, "missing_volumes": [], "mode": null,
    "mtime": null, "nlink": null, "num_volumes": 1, "order": null, "pages_allocated": null, "pages_used": null,
    "pdse_version": null, "perc_pages_used": null, "primary_space": 93, "purge": null, "pw_name": null,
    "quiesced": {"job": null, "system": null, "timestamp": null}, "racf": "none", "readable": null,
    "record_format": "fb", "record_length": 80, "rgrp": null, "roth": null, "rusr": null, "scratch": null,
    "secondary_space": 56, "seq_type": "basic", "size": null, "sms_data_class": null, "sms_mgmt_class": null,
    "sms_storage_class": null, "space_units": "track", "sysplex_aware": null, "total_size": null,
    "tracks_per_cylinder": 15, "type": "seq", "uid": null, "updated_since_backup": false, "version": null,
    "volser": "222222", "volumes": ["222222"], "wgrp": null, "woth": null, "writeable": null, "wusr": null,
    "xgrp": null, "xoth": null, "xusr": null}, "exists": true, "isaggregate": false, "isdataset": true,
    "isfile": false, "isgdg": false, "name": "omvsadm.stat.test.seq", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('aggregate') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic aggregate information (12 attributes).
        assert 'auditfid' in stat['attributes']
        assert 'bitmap_file_size' in stat['attributes']
        assert 'converttov5' in stat['attributes']
        assert 'filesystem_table_size' in stat['attributes']
        assert 'free' in stat['attributes']
        assert 'free_1k_fragments' in stat['attributes']
        assert 'free_8k_blocks' in stat['attributes']
        assert 'log_file_size' in stat['attributes']
        assert 'quiesced' in stat['attributes']
        assert 'sysplex_aware' in stat['attributes']
        assert 'total_size' in stat['attributes']
        assert 'version' in stat['attributes']

        # There are a total of 12 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 12


def test_filter_gdg(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null, "allocation_available": 93,
    "allocation_used": 0, "atime": null, "audit_bits": null, "auditfid": null, "bitmap_file_size": null,
    "block_size": 27920, "blocks_per_track": 2, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-03", "creation_time": null, "ctime": null, "data": {"avg_record_length": null,
    "bufspace": null, "device_type": null, "key_length": null, "key_offset": null, "max_record_length": null,
    "spanned": null, "total_records": null, "volser": null}, "dev": null, "device_type": "3390",
    "dir_blocks_allocated": null, "dir_blocks_used": null, "dsorg": "ps", "empty": null, "encrypted": false,
    "executable": null, "expiration_date": null, "extended": null, "extended_attrs_bits": null, "extents_allocated": 1,
    "extents_used": 0, "file_format": null, "filesystem_table_size": null, "free": null, "free_1k_fragments": null,
    "free_8k_blocks": null, "gid": null, "gr_name": null, "has_extended_attrs": false,
    "index": {"avg_record_length": null, "bufspace": null, "device_type": null, "key_length": null, "key_offset": null,
    "max_record_length": null, "total_records": null, "volser": null}, "inode": null, "isblk": null, "ischr": null,
    "isdir": null, "isfifo": null, "isgid": null, "islnk": null, "isreg": null, "issock": null, "isuid": null,
    "jcl_attrs": {"creation_job": null, "creation_step": null}, "key_label": null, "key_status": "none",
    "last_reference": null, "limit": null, "lnk_source": null, "lnk_target": null, "log_file_size": null,
    "max_pdse_generation": null, "members": null, "mimetype": null, "missing_volumes": [], "mode": null,
    "mtime": null, "nlink": null, "num_volumes": 1, "order": null, "pages_allocated": null, "pages_used": null,
    "pdse_version": null, "perc_pages_used": null, "primary_space": 93, "purge": null, "pw_name": null,
    "quiesced": {"job": null, "system": null, "timestamp": null}, "racf": "none", "readable": null,
    "record_format": "fb", "record_length": 80, "rgrp": null, "roth": null, "rusr": null, "scratch": null,
    "secondary_space": 56, "seq_type": "basic", "size": null, "sms_data_class": null, "sms_mgmt_class": null,
    "sms_storage_class": null, "space_units": "track", "sysplex_aware": null, "total_size": null,
    "tracks_per_cylinder": 15, "type": "seq", "uid": null, "updated_since_backup": false, "version": null,
    "volser": "222222", "volumes": ["222222"], "wgrp": null, "woth": null, "writeable": null, "wusr": null,
    "xgrp": null, "xoth": null, "xusr": null}, "exists": true, "isaggregate": false, "isdataset": true,
    "isfile": false, "isgdg": false, "name": "omvsadm.stat.test.seq", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('gdg') }}")

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        # Checking for general information.
        assert stat.get('resource_type') is not None
        assert stat.get('name') is not None
        assert stat.get('exists') is not None
        assert stat.get('isfile') is not None
        assert stat.get('isdataset') is not None
        assert stat.get('isaggregate') is not None
        assert stat.get('isgdg') is not None
        assert stat.get('attributes') is not None

        # Checking for generic generation data group information (8 attributes).
        assert 'active_gens' in stat['attributes']
        assert 'creation_date' in stat['attributes']
        assert 'empty' in stat['attributes']
        assert 'extended' in stat['attributes']
        assert 'limit' in stat['attributes']
        assert 'order' in stat['attributes']
        assert 'purge' in stat['attributes']
        assert 'scratch' in stat['attributes']
        
        # There are a total of 8 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 8


def test_filter_nonexistent_resource(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{
        "changed": true, 
        "stat": {
            "name": "NONEXIST.DATA.SET",
            "resource_type": "data_set",
            "exists": false,
            "isfile": false,
            "isdataset": false,
            "isaggregate": false,
            "isgdg": false,
            "attributes": {}
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)
    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}")

    for result in filter_results.contacted.values():
        stat = result['msg']
        
        # Verify root attribute defaults are present
        assert stat.get('name') == 'NONEXIST.DATA.SET'
        assert stat.get('resource_type') == 'data_set'
        assert stat.get('exists') == False
        assert stat.get('isfile') == False
        assert stat.get('isdataset') == False
        assert stat.get('isaggregate') == False
        assert stat.get('isgdg') == False


def test_filter_pds_data_set_member_details_present(ansible_zos_module):
    """Positive: member_details key survives the filter when present in input."""
    hosts = ansible_zos_module

    # Represents zos_stat output from the PR branch where member_details
    # is populated for a PDS with two members.
    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": 5, "allocation_used": 1,
                "atime": null, "audit_bits": null, "auditfid": null,
                "bitmap_file_size": null, "block_size": 3120, "blocks_per_track": 15,
                "charset": null, "checksum": null, "converttov5": null,
                "creation_date": "2026-07-23", "creation_time": null, "ctime": null,
                "data": {"avg_record_length": null, "bufspace": null, "device_type": null,
                    "key_length": null, "key_offset": null, "max_record_length": null,
                    "spanned": null, "total_records": null, "volser": null},
                "dev": null, "device_type": "3390",
                "dir_blocks_allocated": 10, "dir_blocks_used": 1,
                "dsorg": "po", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": 1, "extents_used": 1,
                "file_format": null, "filesystem_table_size": null,
                "free": null, "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": {"avg_record_length": null, "bufspace": null, "device_type": null,
                    "key_length": null, "key_offset": null, "max_record_length": null,
                    "total_records": null, "volser": null},
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": "2026-07-23",
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "member_details": [
                    {"extended_attributes": null, "ispf_statistics": {"changed": "2026/07/28 08:20:54",
                    "created": "2026/07/28", "id": "OMVSADM", "init": 1, "mod": 0, "version": "01.00"},
                    "name": "HELLO"},
                    {"extended_attributes": null, "ispf_statistics": {"changed": "2026/07/28 08:21:20",
                    "created": "2026/07/28", "id": "OMVSADM", "init": 1, "mod": 0, "version": "01.00"},
                    "name": "WORLD"}
                ],
                "members": 2, "mimetype": null, "missing_volumes": [], "mode": null,
                "mtime": null, "nlink": null, "num_volumes": 1, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": 5, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "none", "readable": null, "record_format": "fb",
                "record_length": 80, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": 2, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": "track",
                "sysplex_aware": null, "total_size": null, "tracks_per_cylinder": 15,
                "type": "pds", "uid": null, "updated_since_backup": true,
                "version": null, "volser": "000000", "volumes": ["000000"],
                "wgrp": null, "woth": null, "writeable": null, "wusr": null,
                "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.PR2518.DEMO.PDS", "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        assert stat.get('attributes') is not None

        # member_details must survive the filter
        assert 'member_details' in stat['attributes']
        member_details = stat['attributes']['member_details']
        assert isinstance(member_details, list)
        assert len(member_details) == 2

        assert member_details[0]['name'] == 'HELLO'
        assert 'extended_attributes' in member_details[0]
        assert 'ispf_statistics' in member_details[0]
        assert 'changed' in member_details[0]['ispf_statistics']
        assert 'created' in member_details[0]['ispf_statistics']
        assert 'id' in member_details[0]['ispf_statistics']
        assert 'init' in member_details[0]['ispf_statistics']
        assert 'mod' in member_details[0]['ispf_statistics']
        assert 'version' in member_details[0]['ispf_statistics']

        assert member_details[1]['name'] == 'WORLD'
        assert 'extended_attributes' in member_details[1]
        assert 'ispf_statistics' in member_details[1]
        assert 'changed' in member_details[1]['ispf_statistics']
        assert 'created' in member_details[1]['ispf_statistics']
        assert 'id' in member_details[1]['ispf_statistics']
        assert 'init' in member_details[1]['ispf_statistics']
        assert 'mod' in member_details[1]['ispf_statistics']
        assert 'version' in member_details[1]['ispf_statistics']

        # Sanity: other pds fields still present
        assert 'members' in stat['attributes']
        assert 'dir_blocks_allocated' in stat['attributes']
        assert 'dir_blocks_used' in stat['attributes']

        # Total attribute count: 42 existing pds fields + member_details = 42
        assert len(stat['attributes'].keys()) == 42


def test_filter_pds_data_set_member_details_absent(ansible_zos_module):
    """Negative: member_details key is present but null when not in input
    (e.g. output from the dev branch before PR #2518 was merged).
    The filter must still include the key — returning null — so that
    automation relying on the key's presence does not break.
    """
    hosts = ansible_zos_module

    # Simulates zos_stat output from before this PR: member_details absent
    # from the raw output. The filter should still include it as null.
    zos_stat_result = """{
        "changed": true,
        "stat": {
            "attributes": {
                "active_gens": null, "allocation_available": 5, "allocation_used": 1,
                "atime": null, "audit_bits": null, "auditfid": null,
                "bitmap_file_size": null, "block_size": 3120, "blocks_per_track": 15,
                "charset": null, "checksum": null, "converttov5": null,
                "creation_date": "2026-07-23", "creation_time": null, "ctime": null,
                "data": {"avg_record_length": null, "bufspace": null, "device_type": null,
                    "key_length": null, "key_offset": null, "max_record_length": null,
                    "spanned": null, "total_records": null, "volser": null},
                "dev": null, "device_type": "3390",
                "dir_blocks_allocated": 10, "dir_blocks_used": 1,
                "dsorg": "po", "empty": null, "encrypted": false,
                "executable": null, "expiration_date": null, "extended": null,
                "extended_attrs_bits": null, "extents_allocated": 1, "extents_used": 1,
                "file_format": null, "filesystem_table_size": null,
                "free": null, "free_1k_fragments": null, "free_8k_blocks": null,
                "gid": null, "gr_name": null, "has_extended_attrs": false,
                "index": {"avg_record_length": null, "bufspace": null, "device_type": null,
                    "key_length": null, "key_offset": null, "max_record_length": null,
                    "total_records": null, "volser": null},
                "inode": null, "isblk": null, "ischr": null, "isdir": null,
                "isfifo": null, "isgid": null, "islnk": null, "isreg": null,
                "issock": null, "isuid": null,
                "jcl_attrs": {"creation_job": null, "creation_step": null},
                "key_label": null, "key_status": "none", "last_reference": "2026-07-23",
                "limit": null, "lnk_source": null, "lnk_target": null,
                "log_file_size": null, "max_pdse_generation": null,
                "members": 2, "mimetype": null, "missing_volumes": [], "mode": null,
                "mtime": null, "nlink": null, "num_volumes": 1, "order": null,
                "pages_allocated": null, "pages_used": null, "pdse_version": null,
                "perc_pages_used": null, "primary_space": 5, "purge": null,
                "pw_name": null,
                "quiesced": {"job": null, "system": null, "timestamp": null},
                "racf": "none", "readable": null, "record_format": "fb",
                "record_length": 80, "rgrp": null, "roth": null, "rusr": null,
                "scratch": null, "secondary_space": 2, "seq_type": null,
                "size": null, "sms_data_class": null, "sms_mgmt_class": null,
                "sms_storage_class": null, "space_units": "track",
                "sysplex_aware": null, "total_size": null, "tracks_per_cylinder": 15,
                "type": "pds", "uid": null, "updated_since_backup": true,
                "version": null, "volser": "000000", "volumes": ["000000"],
                "wgrp": null, "woth": null, "writeable": null, "wusr": null,
                "xgrp": null, "xoth": null, "xusr": null
            },
            "exists": true, "isaggregate": false, "isdataset": true,
            "isfile": false, "isgdg": false,
            "name": "OMVSADM.PR2518.DEMO.PDS", "resource_type": "data_set"
        }
    }"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(
        msg="{{ zos_stat_output | ibm.ibm_zos_core.zos_stat_by_type('data_set') }}"
    )

    for result in filter_results.contacted.values():
        assert result.get('msg') is not None
        stat = result['msg']

        assert stat.get('attributes') is not None

        # Key must be present even when absent from source — filter uses
        # dict.get() which returns None, preserving the key for automation
        assert 'member_details' in stat['attributes']
        assert stat['attributes']['member_details'] is None

        # Total attribute count still 42 — key present, value null
        assert len(stat['attributes'].keys()) == 42
