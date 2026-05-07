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

from ansible.errors import AnsibleFilterError

__metaclass__ = type

DOCUMENTATION = r"""
name: filter_by_resource_type
author: Alex Moreno (@rexemin)
version_added: "2.0.0"
short_description: Filter returned fields from zos_stat
description:
  - Extract only the relevant fields for a resource from the output of zos_stat.
  - Choose between data set, file, aggregate or GDG fields.
options:
  attributes:
    description:
      - Output from zos_stat.
    type: dict
    required: true
  resource:
    description:
      - Type of resource whose fields should be filtered from the zos_stat JSON output.
      - If the resource is a data set, the filter will only include the relevant fields for
        the specific type of data set queried by zos_stat, which can be sequential, PDS, or VSAM.
        When C(isdataset=False), only common data set attribute fields will be returned.
    type: str
    required: true
    choices:
      - data_set
      - file
      - aggregate
      - gdg
"""

EXAMPLES = r"""
- name: Get only data set specific attributes.
  set_fact:
    clean_output: "{{ zos_stat_output | ibm.ibm_zos_core.filter_by_resource_type('data_set') }}"
"""

RETURN = r"""
  _value:
    description: Stripped-down dictionary containing the fields relevant for the selected resource.
    type: dict
"""

COMMON_DS_FIELDS = [
    'record_format',
    'record_length',
    'block_size',
    'creation_time',
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
]
VALID_FIELDS = {
    'data_set': [
        'type',
        'dsorg',
        'has_extended_attrs',
        'extended_attrs_bits',
        'creation_date',
        'expiration_date',
        'sms_data_class',
        'sms_mgmt_class',
        'sms_storage_class',
        'encrypted',
        'key_label',
        'key_status',
        'racf',
    ],
    'seq': COMMON_DS_FIELDS + ['seq_type'],
    'pds': COMMON_DS_FIELDS +
    [
        'dir_blocks_allocated',
        'dir_blocks_used',
        'members',
        'pages_allocated',
        'pages_used',
        'perc_pages_used',
        'pdse_version',
        'max_pdse_generation',
    ],
    'vsam': [
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
VALID_RESOURCES = ['data_set', 'file', 'aggregate', 'gdg']
DSORG_SEQ = 'ps'
DSORG_PARTITIONED = 'po'
DSORG_VSAM = 'vsam'


def _extract_fields(src_attrs, field_list, target_dict):
    """ Extracts the fields from the source_attrs and adds them to the target_dict. """
    for field in field_list:
        target_dict['attributes'][field] = src_attrs.get('attributes', {}).get(field)


def filter_stat(attributes, resource):
    """Filter a dictionary that was output by zos_stat.

    Arguments:
        attributes {dict} -- Dictionary containing all the stat attributes returned by zos_stat.
        resource {str} -- One of 'data_set', 'file', 'aggregate' or 'gdg'.

    Returns:
        dict -- A reduced attributes dictionary.
    """
    if not isinstance(attributes, dict):
        raise AnsibleFilterError("The 'attributes' object passed is not a dictionary. A dictionary is required for filtering.")
    if resource not in VALID_RESOURCES:
        raise AnsibleFilterError(f"Invalid resource '{resource}'. Must be one of the following: {', '.join(VALID_RESOURCES)}")
    if 'stat' not in attributes:
        raise AnsibleFilterError("Input dictionary missing required 'stat' key. Verify valid output from zos_stat module is being passed.")
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

    for field in VALID_FIELDS[resource]:
        cleaned_attributes['attributes'][field] = attributes.get('attributes', {}).get(field)

    if resource == 'data_set' and cleaned_attributes['attributes'].get('dsorg') is not None:
        if DSORG_SEQ in cleaned_attributes['attributes']['dsorg']:
            _extract_fields(attributes, VALID_FIELDS['seq'], cleaned_attributes)
        if DSORG_PARTITIONED in cleaned_attributes['attributes']['dsorg']:
            _extract_fields(attributes, VALID_FIELDS['pds'], cleaned_attributes)
        if cleaned_attributes['attributes']['dsorg'] == DSORG_VSAM:
            _extract_fields(attributes, VALID_FIELDS['vsam'], cleaned_attributes)

    return cleaned_attributes


class FilterModule(object):
    """ Jinja2 filter for the returned JSON by the zos_stat module. """

    def filters(self):
        filters = {
            "filter_by_resource_type": filter_stat,
        }
        return filters
