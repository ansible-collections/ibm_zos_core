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

import datetime
import json
import os
import tempfile
import pytest

from ibm_zos_core.tests.helpers.users import ManagedUserType, ManagedUser
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name
__metaclass__ = type


EXPECTED_ATTRS = {
    'aggregate': {
        'flat': [
            'total_size',
            'free',
            'version',
            'auditfid',
            'free_8k_blocks',
            'free_1k_fragments',
            'log_file_size',
            'filesystem_table_size',
            'bitmap_file_size',
            'sysplex_aware',
            'converttov5'
        ],
        'nested': [
            ['quiesced', ['job', 'system', 'timestamp']]
        ]
    },

    'file': {
        'flat': [
            'mode', 'atime', 'mtime', 'ctime', 'checksum',
            'uid', 'gid', 'size', 'inode', 'dev',
            'nlink', 'isdir', 'ischr', 'isblk', 'isreg', 'isfifo',
            'islnk', 'issock', 'isuid', 'isgid',
            'wusr', 'rusr', 'xusr', 'wgrp', 'rgrp', 'xgrp', 'woth', 'roth', 'xoth',
            'writeable', 'readable', 'executable',
            'pw_name', 'gr_name', 'lnk_source', 'lnk_target', 'charset',
            'mimetype', 'audit_bits', 'file_format'
        ],
        'nested': []
    },

    'data_set': {
        'flat': [
            'dsorg', 'type', 'record_format', 'record_length', 'block_size',
            'has_extended_attrs', 'creation_time', 'expiration_date',
            'last_reference', 'updated_since_backup',
            'volser', 'num_volumes', 'volumes', 'missing_volumes', 'device_type',
            'space_units', 'primary_space', 'secondary_space',
            'allocation_available', 'allocation_used', 'tracks_per_cylinder',
            'extents_allocated', 'extents_used', 'blocks_per_track',
            'sms_data_class', 'sms_mgmt_class', 'sms_storage_class',
            'encrypted', 'key_status', 'racf', 'key_label', 'members'
        ],
        'nested': [
            ['jcl_attrs', ['creation_job', 'creation_step']]
        ]
    },

    'seq': {
        'flat': [
            'seq_type'
        ],
        'nested': []
    },

    'pds': {
        'flat': [
            'dir_blocks_allocated',
            'dir_blocks_used',
        ],
        'nested': []
    },

    'pdse': {
        'flat': [
            'pages_allocated',
            'pages_used',
            'perc_pages_used',
            'pdse_version',
            'max_pdse_generation'
        ],
        'nested': []
    },

    'vsam': {
        'flat': [],
        'nested': [
            ['data', [
                'key_length', 'key_offset', 'max_record_length', 'avg_record_length',
                'bufspace', 'total_records', 'spanned', 'volser', 'device_type'
            ]],
            ['index', [
                'key_length', 'key_offset', 'max_record_length', 'avg_record_length',
                'bufspace', 'total_records', 'volser', 'device_type'
            ]]
        ]
    },

    'gdg': {
        'flat': [
            'limit',
            'scratch',
            'empty',
            'order',
            'purge',
            'extended',
            'active_gens'
        ],
        'nested': []
    }
}


def assert_invalid_attrs_are_none(attrs, resource_type):
    """Given the attrs and resource_type, asserts all attributes that should
    be None are indeed None.

    Arguments:
        attrs (dict) -- Dictionary containing the output from zos_stat.
        resource_type (str) -- One of 'data_set', 'file', 'aggregate' or 'gdg'.
    """
    for current_type in EXPECTED_ATTRS.keys():
        if resource_type == current_type:
            continue
        elif resource_type in ('seq', 'pds', 'pdse', 'vsam') and current_type == 'data_set':
            continue

        for attr in EXPECTED_ATTRS[current_type]['flat']:
            assert attrs[attr] is None

        for nest in EXPECTED_ATTRS[current_type]['nested']:
            for sub_key in nest[1]:
                assert attrs[nest[0]][sub_key] is None


def test_query_data_set_seq_no_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_pds_no_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    dir_blocks = 4
    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -b{dir_blocks} -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tpds -V{available_vol} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'po'
            assert stat['attributes'].get('type') == 'pds'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('dir_blocks_allocated') == dir_blocks
            assert stat['attributes'].get('dir_blocks_used') is not None
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'pds')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_pdse_no_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tpdse -V{available_vol} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'po'
            assert stat['attributes'].get('type') == 'pdse'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('pages_allocated') is not None
            assert stat['attributes'].get('pages_used') is not None
            assert stat['attributes'].get('perc_pages_used') is not None
            assert stat['attributes'].get('pdse_version') is not None
            assert stat['attributes'].get('max_pdse_generation') is not None
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'pdse')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_vsam_ksds(ansible_zos_module):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    key_length = 3
    key_offset = 4
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -k{key_length}:{key_offset} -tksds {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'vsam'
            assert stat['attributes'].get('type') == 'ksds'
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None

            assert stat['attributes'].get('data') is not None
            assert stat['attributes']['data'].get('key_length') == key_length
            assert stat['attributes']['data'].get('key_offset') == key_offset
            assert stat['attributes']['data'].get('avg_record_length') is not None
            assert stat['attributes']['data'].get('max_record_length') is not None
            assert stat['attributes']['data'].get('bufspace') is not None
            assert stat['attributes']['data'].get('name') is not None
            assert stat['attributes']['data'].get('spanned') is not None
            assert stat['attributes']['data'].get('volser') is not None
            assert stat['attributes']['data'].get('device_type') is not None

            assert stat['attributes'].get('index') is not None
            assert stat['attributes']['data'].get('key_length') == key_length
            assert stat['attributes']['data'].get('key_offset') == key_offset
            assert stat['attributes']['data'].get('avg_record_length') is not None
            assert stat['attributes']['data'].get('max_record_length') is not None
            assert stat['attributes']['data'].get('bufspace') is not None
            assert stat['attributes']['data'].get('name') is not None
            assert stat['attributes']['data'].get('volser') is not None
            assert stat['attributes']['data'].get('device_type') is not None

            assert_invalid_attrs_are_none(stat['attributes'], 'vsam')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_gds(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name()

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    limit = 3
    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        gdg_creation_result = hosts.all.shell(
            cmd=f'dtouch -L{limit} -tgdg {name}'
        )

        for result in gdg_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        data_set_creation_result = hosts.all.shell(
            cmd=f"""dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol} "{name}(+1)" """
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=f"{name}(0)",
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert name in stat.get('name')
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f"""drm '{name}(0)' """
        )

        hosts.all.shell(
            cmd=f'drm {name}'
        )


def test_query_data_set_seq_with_correct_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            volume=available_vol,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_seq_with_wrong_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            volume="ERRVOL",
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed', False) is False
            assert result.get('failed', False) is False
            assert result.get('stat') is not None
            assert result.get('stat').get('exists') is False
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_seq_multi_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol_1 = volumes.get_available_vol()
    available_vol_2 = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol_1},{available_vol_2} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            volumes=[available_vol_1, available_vol_2],
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol_1.lower()
            assert stat['attributes'].get('volumes') == [available_vol_1.lower(), available_vol_2.lower()]
            assert stat['attributes'].get('num_volumes') == 2
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'
            assert stat['attributes'].get('missing_volumes') == []

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_data_set_seq_multi_volume_missing_one(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(llq_size=4)
    name = f"{name}$#@"
    escaped_name = name.replace('$', '\$')

    volumes = Volume_Handler(volumes_on_systems)
    available_vol_1 = volumes.get_available_vol()
    available_vol_2 = volumes.get_available_vol()
    missing_vol = 'ERRVOL'

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol_1},{available_vol_2} {escaped_name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            volumes=[
                available_vol_1,
                available_vol_2,
                missing_vol
            ],
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol_1.lower()
            assert stat['attributes'].get('volumes') == [available_vol_1.lower(), available_vol_2.lower()]
            assert stat['attributes'].get('num_volumes') == 2
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'
            assert stat['attributes'].get('missing_volumes') == [missing_vol.lower()]

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f'drm {escaped_name}'
        )


def test_query_gdg(ansible_zos_module):
    hosts = ansible_zos_module
    name = get_tmp_ds_name()

    limit = 3
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        gdg_creation_result = hosts.all.shell(
            cmd=f'dtouch -L{limit} -tgdg {name}'
        )

        for result in gdg_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=f'{name}',
            type='gdg'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'gdg'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is False
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is True
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('limit') == limit
            assert stat['attributes'].get('scratch') is not None
            assert stat['attributes'].get('empty') is not None
            assert stat['attributes'].get('order') is not None
            assert stat['attributes'].get('purge') is not None
            assert stat['attributes'].get('extended') is not None
            assert stat['attributes'].get('active_gens') == []

            assert_invalid_attrs_are_none(stat['attributes'], 'gdg')
    finally:
        hosts.all.shell(
            cmd=f'drm {name}'
        )


def test_query_aggregate(ansible_zos_module):
    hosts = ansible_zos_module
    aggregate_name = ""

    zfsadm_result = hosts.all.shell(
        cmd='zfsadm aggrinfo'
    )

    for result in zfsadm_result.contacted.values():
        assert result.get('failed', False) is False
        assert result.get('stdout_lines') is not None

        aggregate_name = result['stdout_lines'][1].split()[0]

    zos_stat_result = hosts.all.zos_stat(
        name=aggregate_name,
        type='aggregate'
    )

    for result in zos_stat_result.contacted.values():
        assert result.get('changed') is True
        assert result.get('failed', False) is False
        assert result.get('stat') is not None

        stat = result['stat']
        assert stat.get('resource_type') == 'aggregate'
        assert stat.get('name') == aggregate_name
        assert stat.get('exists') is True
        assert stat.get('isfile') is False
        assert stat.get('isdataset') is False
        assert stat.get('isaggregate') is True
        assert stat.get('isgdg') is False
        assert stat.get('attributes') is not None

        assert stat['attributes'].get('total_size') is not None
        assert stat['attributes'].get('free') is not None
        assert stat['attributes'].get('version') is not None
        assert stat['attributes'].get('auditfid') is not None
        assert stat['attributes'].get('free_8k_blocks') is not None
        assert stat['attributes'].get('free_1k_fragments') is not None
        assert stat['attributes'].get('log_file_size') is not None
        assert stat['attributes'].get('filesystem_table_size') is not None
        assert stat['attributes'].get('bitmap_file_size') is not None
        assert stat['attributes'].get('sysplex_aware') is not None
        assert stat['attributes'].get('converttov5') is not None
        assert stat['attributes'].get('quiesced') is not None

        assert_invalid_attrs_are_none(stat['attributes'], 'aggregate')


def test_query_file_no_symlink(ansible_zos_module):
    hosts = ansible_zos_module
    test_file = '/etc/profile'

    zos_stat_result = hosts.all.zos_stat(
        src=test_file,
        get_checksum=True,
        get_mime=True,
        checksum_algorithm='sha512',
        type='file'
    )

    for result in zos_stat_result.contacted.values():
        assert result.get('changed') is True
        assert result.get('failed', False) is False
        assert result.get('stat') is not None

        stat = result['stat']
        assert stat.get('resource_type') == 'file'
        assert stat.get('name') == test_file
        assert stat.get('exists') is True
        assert stat.get('isfile') is True
        assert stat.get('isdataset') is False
        assert stat.get('isaggregate') is False
        assert stat.get('isgdg') is False
        assert stat.get('attributes') is not None

        for attr in EXPECTED_ATTRS['file']['flat']:
            # Skipping symlink attributes as we're not querying one.
            # We're also not querying a record file, so we skip file_format.
            if attr == 'lnk_source' or attr == 'lnk_target' or attr == 'file_format':
                continue
            assert stat['attributes'].get(attr) is not None

        assert_invalid_attrs_are_none(stat['attributes'], 'file')


def test_query_file_no_checksum_no_mime(ansible_zos_module):
    hosts = ansible_zos_module
    test_file = '/etc/profile'

    zos_stat_result = hosts.all.zos_stat(
        src=test_file,
        get_checksum=False,
        get_mime=False,
        type='file'
    )

    for result in zos_stat_result.contacted.values():
        assert result.get('changed') is True
        assert result.get('failed', False) is False
        assert result.get('stat') is not None

        stat = result['stat']
        assert stat.get('resource_type') == 'file'
        assert stat.get('name') == test_file
        assert stat.get('exists') is True
        assert stat.get('isfile') is True
        assert stat.get('isdataset') is False
        assert stat.get('isaggregate') is False
        assert stat.get('isgdg') is False
        assert stat.get('attributes') is not None

        for attr in EXPECTED_ATTRS['file']['flat']:
            # Skipping symlink attributes as we're not querying one.
            # We're also not querying a record file, so we skip file_format.
            if attr == 'lnk_source' or attr == 'lnk_target' or attr == 'file_format':
                continue

            if attr == 'mimetype' or attr == 'checksum':
                assert stat['attributes'].get(attr) is None
            else:
                assert stat['attributes'].get(attr) is not None

        assert_invalid_attrs_are_none(stat['attributes'], 'file')


def test_query_file_symlink_follow_on(ansible_zos_module):
    hosts = ansible_zos_module
    test_src = '/etc/profile'
    test_file = '/tmp/zos_stat_symlink'

    try:
        symlink_result = hosts.all.shell(
            cmd=f'ln -s {test_src} {test_file}'
        )

        for result in symlink_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=test_file,
            get_checksum=True,
            get_mime=True,
            checksum_algorithm='sha512',
            type='file',
            follow=True
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'file'
            assert stat.get('name') == test_file
            assert stat.get('exists') is True
            assert stat.get('isfile') is True
            assert stat.get('isdataset') is False
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            # When following links, these two attributes should be None.
            assert stat['attributes'].get('lnk_source') is None
            assert stat['attributes'].get('lnk_target') is None

            for attr in EXPECTED_ATTRS['file']['flat']:
                # Skipping symlink attributes here.
                # We're also not querying a record file, so we skip file_format.
                if attr == 'lnk_source' or attr == 'lnk_target' or attr == 'file_format':
                    continue
                assert stat['attributes'].get(attr) is not None

            assert_invalid_attrs_are_none(stat['attributes'], 'file')
    finally:
        hosts.all.file(path=test_file, state='absent')


def test_query_file_symlink_follow_off(ansible_zos_module):
    hosts = ansible_zos_module
    test_src = '/etc/profile'
    test_file = '/tmp/zos_stat_symlink'

    try:
        symlink_result = hosts.all.shell(
            cmd=f'ln -s {test_src} {test_file}'
        )

        for result in symlink_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=test_file,
            get_checksum=True,
            get_mime=True,
            checksum_algorithm='sha512',
            type='file',
            follow=False
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'file'
            assert stat.get('name') == test_file
            assert stat.get('exists') is True
            assert stat.get('isfile') is True
            assert stat.get('isdataset') is False
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            for attr in EXPECTED_ATTRS['file']['flat']:
                # We're also not querying a record file, so we skip file_format.
                if attr == 'file_format':
                    continue
                assert stat['attributes'].get(attr) is not None

            assert_invalid_attrs_are_none(stat['attributes'], 'file')
    finally:
        hosts.all.file(path=test_file, state='absent')


@pytest.mark.parametrize('resource_type', ['data_set', 'file', 'aggregate', 'gdg'])
def test_query_data_set_non_existent(ansible_zos_module, resource_type):
    hosts = ansible_zos_module
    name = get_tmp_ds_name()

    if resource_type == 'file':
        name = f"/tmp/{name}"

    zos_stat_result = hosts.all.zos_stat(
        src=name,
        type=resource_type
    )

    for result in zos_stat_result.contacted.values():
        assert result.get('changed', False) is False
        assert result.get('failed', False) is False
        assert result.get('stat') is not None
        assert result.get('stat').get('exists') is False


def test_query_data_set_tmp_hlq(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    try:
        name = get_tmp_ds_name()
        tmphlq = "TMPHLQ"

        volumes = Volume_Handler(volumes_on_systems)
        available_vol = volumes.get_available_vol()

        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -tseq -V{available_vol} {name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=name,
            type='data_set',
            tmp_hlq=tmphlq
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == name
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None
    finally:
        hosts.all.shell(cmd=f'drm {name}')


def test_query_data_set_seq_with_alias(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module

    name = get_tmp_ds_name(mlq_size=3, llq_size=3)
    alias = get_tmp_ds_name(mlq_size=3, llq_size=3)
    # Getting rid of the MLQ so that both names fit inside the
    # 80 columns available for the IDCAMS command.
    # Resulting names will be of the form ANSIBLE.TXXXXXXX.XXXX.
    name = f'{name[:7]}.{name[13:]}'
    alias = f'{alias[:7]}.{alias[13:]}'

    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()

    block_size = 85
    primary_space = 15
    secondary_space = 5
    size_units = 'T'
    record_length = 100
    record_format = 'fb'
    creation_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -B{block_size} -e{secondary_space}{size_units} -l{record_length} -r{record_format} -s{primary_space}{size_units} -tseq -V{available_vol} {name}'
        )

        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        alias_creation_result = hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({alias}) RELATE({name}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )

        for result in alias_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False

        zos_stat_result = hosts.all.zos_stat(
            src=alias,
            type='data_set'
        )

        for result in zos_stat_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get('stat') is not None

            stat = result['stat']
            assert stat.get('resource_type') == 'data_set'
            assert stat.get('name') == alias
            assert stat.get('exists') is True
            assert stat.get('isfile') is False
            assert stat.get('isdataset') is True
            assert stat.get('isaggregate') is False
            assert stat.get('isgdg') is False
            assert stat.get('attributes') is not None

            assert stat['attributes'].get('dsorg') == 'ps'
            assert stat['attributes'].get('type') == 'seq'
            assert stat['attributes'].get('record_format') == record_format
            assert stat['attributes'].get('record_length') == record_length
            assert stat['attributes'].get('block_size') == block_size
            assert stat['attributes'].get('has_extended_attrs') is False
            assert stat['attributes'].get('creation_date') == creation_date
            assert stat['attributes'].get('creation_time') is None
            assert stat['attributes'].get('volser') == available_vol.lower()
            assert stat['attributes'].get('volumes') == [available_vol.lower()]
            assert stat['attributes'].get('num_volumes') == 1
            assert stat['attributes'].get('device_type') == '3390'
            assert stat['attributes'].get('primary_space') == primary_space
            assert stat['attributes'].get('allocation_available') == primary_space
            assert stat['attributes'].get('secondary_space') == secondary_space
            assert stat['attributes'].get('space_units') == 'track'

            assert_invalid_attrs_are_none(stat['attributes'], 'seq')
    finally:
        hosts.all.shell(
            cmd=f'drm {alias}'
        )

        hosts.all.shell(
            cmd=f'drm {name}'
        )


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('data_set') }}")

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

        # Checking for generic data set information.
        assert 'type' in stat['attributes']
        assert 'dsorg' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']
        assert 'extended_attrs_bits' in stat['attributes']
        assert 'creation_date' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']

        # Checking for sequential-data-set-specific information.
        assert 'record_format' in stat['attributes']
        assert 'record_length' in stat['attributes']
        assert 'block_size' in stat['attributes']
        assert 'creation_time' in stat['attributes']
        assert 'last_reference' in stat['attributes']
        assert 'updated_since_backup' in stat['attributes']
        assert 'jcl_attrs' in stat['attributes']
        assert 'volser' in stat['attributes']
        assert 'num_volumes' in stat['attributes']
        assert 'volumes' in stat['attributes']
        assert 'missing_volumes' in stat['attributes']
        assert 'device_type' in stat['attributes']
        assert 'space_units' in stat['attributes']
        assert 'primary_space' in stat['attributes']
        assert 'secondary_space' in stat['attributes']
        assert 'allocation_available' in stat['attributes']
        assert 'allocation_used' in stat['attributes']
        assert 'extents_allocated' in stat['attributes']
        assert 'extents_used' in stat['attributes']
        assert 'blocks_per_track' in stat['attributes']
        assert 'tracks_per_cylinder' in stat['attributes']
        assert 'seq_type' in stat['attributes']

        # There are a total of 35 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 35


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('data_set') }}")

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

        # Checking for generic data set information.
        assert 'type' in stat['attributes']
        assert 'dsorg' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']
        assert 'extended_attrs_bits' in stat['attributes']
        assert 'creation_date' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']

        # Checking for partitioned-data-set-specific information.
        assert 'record_format' in stat['attributes']
        assert 'record_length' in stat['attributes']
        assert 'block_size' in stat['attributes']
        assert 'creation_time' in stat['attributes']
        assert 'last_reference' in stat['attributes']
        assert 'updated_since_backup' in stat['attributes']
        assert 'jcl_attrs' in stat['attributes']
        assert 'volser' in stat['attributes']
        assert 'num_volumes' in stat['attributes']
        assert 'volumes' in stat['attributes']
        assert 'missing_volumes' in stat['attributes']
        assert 'device_type' in stat['attributes']
        assert 'space_units' in stat['attributes']
        assert 'primary_space' in stat['attributes']
        assert 'secondary_space' in stat['attributes']
        assert 'allocation_available' in stat['attributes']
        assert 'allocation_used' in stat['attributes']
        assert 'extents_allocated' in stat['attributes']
        assert 'extents_used' in stat['attributes']
        assert 'blocks_per_track' in stat['attributes']
        assert 'tracks_per_cylinder' in stat['attributes']
        assert 'dir_blocks_allocated' in stat['attributes']
        assert 'dir_blocks_used' in stat['attributes']
        assert 'members' in stat['attributes']
        assert 'pages_allocated' in stat['attributes']
        assert 'pages_used' in stat['attributes']
        assert 'perc_pages_used' in stat['attributes']
        assert 'pdse_version' in stat['attributes']
        assert 'max_pdse_generation' in stat['attributes']

        # There are a total of 42 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 42


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('data_set') }}")

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

        # Checking for generic data set information.
        assert 'type' in stat['attributes']
        assert 'dsorg' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']
        assert 'extended_attrs_bits' in stat['attributes']
        assert 'creation_date' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']

        # Checking for partitioned-data-set-specific information.
        assert 'data' in stat['attributes']
        assert 'index' in stat['attributes']

        # There are a total of 15 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 15


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('data_set') }}")

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

        # Checking for generic data set information.
        assert 'type' in stat['attributes']
        assert 'dsorg' in stat['attributes']
        assert 'has_extended_attrs' in stat['attributes']
        assert 'extended_attrs_bits' in stat['attributes']
        assert 'creation_date' in stat['attributes']
        assert 'expiration_date' in stat['attributes']
        assert 'sms_data_class' in stat['attributes']
        assert 'sms_mgmt_class' in stat['attributes']
        assert 'sms_storage_class' in stat['attributes']
        assert 'encrypted' in stat['attributes']
        assert 'key_label' in stat['attributes']
        assert 'key_status' in stat['attributes']
        assert 'racf' in stat['attributes']

        # There are a total of 13 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 13


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('file') }}")

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

        # Checking for generic file information.
        assert 'mode' in stat['attributes']
        assert 'atime' in stat['attributes']
        assert 'mtime' in stat['attributes']
        assert 'ctime' in stat['attributes']
        assert 'checksum' in stat['attributes']
        assert 'uid' in stat['attributes']
        assert 'gid' in stat['attributes']
        assert 'size' in stat['attributes']
        assert 'inode' in stat['attributes']
        assert 'dev' in stat['attributes']
        assert 'nlink' in stat['attributes']
        assert 'isdir' in stat['attributes']
        assert 'ischr' in stat['attributes']
        assert 'isblk' in stat['attributes']
        assert 'isreg' in stat['attributes']
        assert 'isfifo' in stat['attributes']
        assert 'islnk' in stat['attributes']
        assert 'issock' in stat['attributes']
        assert 'isuid' in stat['attributes']
        assert 'isgid' in stat['attributes']
        assert 'wusr' in stat['attributes']
        assert 'rusr' in stat['attributes']
        assert 'xusr' in stat['attributes']
        assert 'wgrp' in stat['attributes']
        assert 'rgrp' in stat['attributes']
        assert 'xgrp' in stat['attributes']
        assert 'woth' in stat['attributes']
        assert 'roth' in stat['attributes']
        assert 'xoth' in stat['attributes']
        assert 'writeable' in stat['attributes']
        assert 'readable' in stat['attributes']
        assert 'executable' in stat['attributes']
        assert 'pw_name' in stat['attributes']
        assert 'gr_name' in stat['attributes']
        assert 'lnk_source' in stat['attributes']
        assert 'lnk_target' in stat['attributes']
        assert 'charset' in stat['attributes']
        assert 'mimetype' in stat['attributes']
        assert 'audit_bits' in stat['attributes']
        assert 'file_format' in stat['attributes']

        # There are a total of 40 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 40


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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('aggregate') }}")

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

        # Checking for generic aggregate information.
        assert 'auditfid' in stat['attributes']
        assert 'bitmap_file_size' in stat['attributes']
        assert 'converttov5' in stat['attributes']
        assert 'filesystem_table_size' in stat['attributes']
        assert 'free' in stat['attributes']
        assert 'free_1k_fragments' in stat['attributes']
        assert 'free_8k_blocks' in stat['attributes']
        assert 'log_file_size' in stat['attributes']
        assert 'sysplex_aware' in stat['attributes']
        assert 'total_size' in stat['attributes']
        assert 'version' in stat['attributes']
        assert 'quiesced' in stat['attributes']

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
    filter_results = hosts.all.debug(msg="{{ zos_stat_output | ibm.ibm_zos_core.stat('gdg') }}")

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

        # Checking for generic generation data group information.
        assert 'limit' in stat['attributes']
        assert 'scratch' in stat['attributes']
        assert 'empty' in stat['attributes']
        assert 'order' in stat['attributes']
        assert 'purge' in stat['attributes']
        assert 'extended' in stat['attributes']
        assert 'active_gens' in stat['attributes']

        # There are a total of 7 attributes above, so the resulting dictionary
        # should not have a different number of them after the filter.
        assert len(stat['attributes'].keys()) == 7
