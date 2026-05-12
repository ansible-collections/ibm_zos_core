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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}")

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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}")

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

        # Checking for partitioned-data-set-specific information (29 attributes).
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
        assert 'members' in stat['attributes']
        assert 'pages_allocated' in stat['attributes']
        assert 'pages_used' in stat['attributes']
        assert 'pdse_version' in stat['attributes']
        assert 'perc_pages_used' in stat['attributes']

        # There are a total of 41 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 41


def test_filter_vsam_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    zos_stat_result = """{"changed": true, "stat": {"attributes": {"active_gens": null,
    "allocation_available": null, "allocation_used": null, "atime": null,
    "audit_bits": null, "auditfid": null, "bitmap_file_size": null, "block_size": null,
    "blocks_per_track": null, "charset": null, "checksum": null, "converttov5": null,
    "creation_date": "2025-11-06", "creation_time": null, "ctime": null, "data":
    {"avg_record_length": 80, "bufspace": 37376, "device_type": "3390",
    "key_length": 5, "key_offset": 1, "max_record_length": 80,
    "name": "omvsadm.stat.filter.vsam.data", "spanned": false, "total_records": 0,
    "volser": "333333"}, "dev": null, "device_type":null, "dir_blocks_allocated": null,
    "dir_blocks_used": null, "dsorg": "vsam", "empty": null, "encrypted": false,
    "executable": null, "expiration_date": null, "extended": null, "extended_attrs_bits": null,
    "extents_allocated": null, "extents_used": null, "file_format": null,
    "filesystem_table_size": null, "free": null, "free_1k_fragments": null,
    "free_8k_blocks": null, "gid": null, "gr_name": null, "has_extended_attrs": false,
    "index": {"avg_record_length": 505, "bufspace": 0, "device_type": "3390", "key_length": 5,
    "key_offset": 1, "max_record_length": 0, "name": "omvsadm.stat.filter.vsam.index",
    "total_records": 0, "volser": "333333"}, "inode": null, "isblk": null,
    "ischr": null, "isdir": null, "isfifo": null, "isgid": null, "islnk": null,
    "isreg": null, "issock": null, "isuid": null, "jcl_attrs": {"creation_job": null,
    "creation_step": null}, "key_label": null, "key_status": "none",
    "last_reference": null, "limit": null, "lnk_source": null, "lnk_target": null,
    "log_file_size": null, "max_pdse_generation": null, "members": null,
    "mimetype": null, "missing_volumes": null, "mode": null, "mtime": null,
    "nlink": null, "num_volumes": null, "order": null, "pages_allocated": null,
    "pages_used": null, "pdse_version": null, "perc_pages_used": null,
    "primary_space": null, "purge": null, "pw_name": null, "quiesced": {"job": null,
    "system": null, "timestamp": null}, "racf": "no", "readable": null,
    "record_format": null, "record_length": null, "rgrp": null, "roth": null,
    "rusr": null, "scratch": null, "secondary_space": null, "seq_type": null,
    "size": null, "sms_data_class": null, "sms_mgmt_class": null, "sms_storage_class": null,
    "space_units": null, "sysplex_aware": null, "total_size": null,
    "tracks_per_cylinder": null, "type": "ksds", "uid": null, "updated_since_backup": null,
    "version": null, "volser": null, "volumes": null, "wgrp": null, "woth": null,
    "writeable": null, "wusr": null, "xgrp": null, "xoth": null, "xusr": null},
    "exists": true, "isaggregate": false, "isdataset": true, "isfile": false,
    "isgdg": false, "name": "OMVSADM.STAT.FILTER.VSAM", "resource_type": "data_set"}}"""
    zos_stat_result_dict = json.loads(zos_stat_result)

    hosts.all.set_fact(zos_stat_output=zos_stat_result_dict)
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}")

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

        # Checking for partitioned-data-set-specific information (2 attributes).
        assert 'data' in stat['attributes']
        assert 'index' in stat['attributes']

        # There are a total of 14 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 14


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}")

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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('file') }}")

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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('aggregate') }}")

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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('gdg') }}")

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
