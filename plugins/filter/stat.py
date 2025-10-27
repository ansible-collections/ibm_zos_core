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

from ansible.errors import AnsibleFilterError


def filter_stat(attributes, resource):
    """Filter a dictionary that was output by zos_stat.

    Arguments:
        attributes {dict} -- Dictionary containing all the stat attributes returned by zos_stat.
        resource {str} -- One of 'data_set', 'file', 'aggregate' or 'gdg'.

    Returns:
        dict -- A reduced attributes dictionary.
    """
    if not isinstance(attributes, dict):
        raise AnsibleFilterError("The 'attributes' object passed is not a dictionary. This filter needs a dictionary to filter.")
    if not resource in ['data_set', 'file', 'aggregate', 'gdg']:
        raise AnsibleFilterError(f"The given resource {resource} is not one of 'data_set', 'file', 'aggregate' or 'gdg'.")

    attributes = attributes.get('stat', {})

    root_attrs = [
        'name',
        'resource_type',
        'exists',
        'isfile',
        'isdataset',
        'isaggregate',
        'isgdg'
    ]
    cleaned_attributes = {key: attributes.get(key) for key in root_attrs}
    cleaned_attributes['attributes'] = {}

    valid_fields = {
        'data_set': [
            'dsorg',
            'type',
            'record_format',
            'record_length',
            'block_size',
            'has_extended_attributes',
            'extended_attrs_bits',
            'creation_date',
            'creation_time',
            'expiration_date',
            'last_reference',
            'updated_since_backup',
            'jcl_attrs',
            'volser',
            'num_volumes',
            'volumes',
            'missing_volumes',
            'device_type',
            'space_units',
            'primary_space',
            'secondary_space',
            'allocation_available',
            'allocation_used',
            'extents_allocated',
            'extents_used',
            'blocks_per_track',
            'tracks_per_cylinder',
            'sms_data_class',
            'sms_mgmt_class',
            'sms_storage_class',
            'encrypted',
            'key_status',
            'racf',
            'key_label',
            'dir_blocks_allocated',
            'dir_blocks_used',
            'members',
            'pages_allocated',
            'pages_used',
            'perc_pages_used',
            'pdse_version',
            'max_pdse_generation',
            'seq_type',
            'data',
            'index'
        ],
        'file': [
            'mode',
            'atime',
            'mtime',
            'ctime',
            'checksum',
            'uid',
            'gid',
            'size',
            'inode',
            'dev',
            'nlink',
            'isdir',
            'ischr',
            'isblk',
            'isreg',
            'isfifo',
            'islnk',
            'issock',
            'isuid',
            'isgid',
            'wusr',
            'rusr',
            'xusr',
            'wgrp',
            'rgrp',
            'xgrp',
            'woth',
            'roth',
            'xoth',
            'writeable',
            'readable',
            'executable',
            'pw_name',
            'gr_name',
            'lnk_source',
            'lnk_target',
            'charset',
            'mimetype',
            'audit_bits',
            'file_format'
        ],
        'aggregate': [
            'auditfid',
            'bitmap_file_size',
            'converttov5',
            'filesystem_table_size',
            'free',
            'free_1k_fragments',
            'free_8k_blocks',
            'log_file_size',
            'sysplex_aware',
            'total_size',
            'version',
            'quiesced'
        ],
        'gdg': [
            'limit',
            'scratch',
            'empty',
            'order',
            'purge',
            'extended',
            'active_gens'
        ]
    }

    for field in valid_fields[resource]:
        cleaned_attributes['attributes'][field] = attributes.get('attributes', {}).get(field)

    return cleaned_attributes


class FilterModule(object):
    """ Jinja2 filter for the returned JSON by the zos_stat module. """

    def filters(self):
        filters = {
            "stat": filter_stat,
        }
        return filters
