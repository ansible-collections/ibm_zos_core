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
__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_volume_free
version_added: '2.2.0'
author:
  - "Ravella Surendra Babu (@surendrababuravella)"
short_description: Query free space and status information for z/OS DASD volumes
description:
  - The L(zos_volume_free,./zos_volume_free.html) module retrieves free space
    and status information for one or more z/OS DASD volumes.
  - Volumes can be queried by volume serial number (VOLSER), by device number,
    or both. When neither is specified, all active DASD volumes are queried.
  - When both I(volumes) and I(device_numbers) are specified, the module
    returns volumes that match B(either) criterion (union), with automatic
    deduplication by VOLSER.
  - Results can be filtered by volume status, free space thresholds, percentage
    free space, and VTOC index status.
  - This module does not make any changes to the z/OS system and always returns
    C(changed=false).
options:
  volumes:
    description:
      - List of volume serial numbers (VOLSERs) to query.
      - Can be a single volume or a list of volumes.
      - When combined with I(device_numbers), returns volumes matching
        B(either) criterion.
      - If neither I(volumes) nor I(device_numbers) is specified, all active
        DASD volumes are queried.
    type: list
    elements: str
    required: false
  device_numbers:
    description:
      - List of device numbers (unit addresses) to query.
      - Examples - C(0A80), C(0941), C(1234).
      - When specified, the module queries all volumes and filters by device
        number.
      - When combined with I(volumes), returns volumes matching B(either)
        criterion, deduplicated by VOLSER.
    type: list
    elements: str
    required: false
  filter:
    description:
      - Dictionary of filter criteria to apply to the volume results.
    type: dict
    required: false
    suboptions:
      status:
        description:
          - Filter by volume status.
          - C(online) - volume is online (ucbonli=True).
          - C(offline) - volume is offline (ucbonli=False).
          - C(pending) - volume status is changing (ucbchgs=True).
        type: list
        elements: str
        choices:
          - online
          - offline
          - pending
      free_space_min:
        description:
          - Minimum free space threshold.
          - Value is in the unit specified by I(filter.unit) (default tracks).
          - Volumes with free space below this threshold are excluded.
        type: int
      free_space_max:
        description:
          - Maximum free space threshold.
          - Value is in the unit specified by I(filter.unit) (default tracks).
          - Volumes with free space above this threshold are excluded.
        type: int
      percent_free_min:
        description:
          - Minimum percentage of free space.
          - Volumes with a lower percentage of free space are excluded.
        type: int
      percent_free_max:
        description:
          - Maximum percentage of free space.
          - Volumes with a higher percentage of free space are excluded.
        type: int
      vtoc_indexed:
        description:
          - Filter by VTOC index status.
          - When C(true), only volumes with an indexed VTOC are returned.
          - When C(false), only volumes without an indexed VTOC are returned.
        type: bool
      unit:
        description:
          - Unit for I(filter.free_space_min) and I(filter.free_space_max)
            filter values.
          - Does B(not) affect the output format. All output space values are
            always expressed in tracks.
          - When C(cylinders), the conversion assumes 15 tracks per cylinder
            (standard for 3390/3380 devices).
        type: str
        choices:
          - tracks
          - cylinders
        default: tracks

attributes:
  action:
    support: none
    description: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
  async:
    support: full
    description: Supports being used with the ``async`` keyword.
  check_mode:
    support: full
    description: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.

notes:
  - This module is read-only and always returns C(changed=false).
  - When querying by I(device_numbers), all volumes are retrieved first and
    then filtered by device number.
  - When both I(volumes) and I(device_numbers) are specified, the module
    returns volumes that match either criterion with automatic deduplication
    by VOLSER.
  - The I(filter.unit) parameter only affects how I(filter.free_space_min)
    and I(filter.free_space_max) are interpreted. All output space values are
    always in tracks.
  - To convert output tracks to cylinders, divide by 15 (for 3390/3380 devices).
  - The simplified C(status) field in the output is derived from
    C(device_status) flags: C(pending) when C(status_changing=true), C(online)
    when C(is_online=true), otherwise C(offline).

seealso:
  - module: ibm.ibm_zos_core.zos_volume_init
  - module: ibm.ibm_zos_core.zos_gather_facts
"""

EXAMPLES = r"""
- name: Query all active DASD volumes.
  ibm.ibm_zos_core.zos_volume_free:
  register: all_volumes

- name: Query specific volumes by VOLSER.
  ibm.ibm_zos_core.zos_volume_free:
    volumes:
      - USER01
      - USER02
      - PROD01
  register: volume_info

- name: Query volumes by device number.
  ibm.ibm_zos_core.zos_volume_free:
    device_numbers:
      - "0A80"
      - "0A81"
  register: device_volumes

- name: Query by both VOLSER and device number (union).
  ibm.ibm_zos_core.zos_volume_free:
    volumes:
      - USER01
    device_numbers:
      - "0A80"
  register: combined_results

- name: Get only online volumes.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      status:
        - online
  register: online_volumes

- name: Get volumes with less than 20 percent free space.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      percent_free_max: 20
      status:
        - online
  register: low_space_volumes

- name: Get volumes with at least 100 cylinders free.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      free_space_min: 100
      unit: cylinders
      status:
        - online
  register: volumes_with_space

- name: Get volumes with an indexed VTOC.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      vtoc_indexed: true
  register: indexed_volumes
"""

RETURN = r"""
volumes:
  description: List of volume information matching the query and filter criteria.
  returned: always
  type: list
  elements: dict
  contains:
    volser:
      description: Volume serial number.
      type: str
      returned: always
      sample: "USER01"
    device_number:
      description: Device number (unit address).
      type: str
      returned: always
      sample: "0A80"
    device_type:
      description: Device type.
      type: str
      returned: always
      sample: "3390"
    status:
      description:
        - Simplified volume status derived from C(device_status) flags.
        - C(pending) when C(status_changing=true).
        - C(online) when C(is_online=true).
        - C(offline) otherwise.
      type: str
      returned: always
      choices:
        - online
        - offline
        - pending
      sample: "online"
    total_space:
      description: Total space on the volume in tracks.
      type: int
      returned: always
      sample: 10016
    free_space:
      description: Free space on the volume in tracks.
      type: int
      returned: always
      sample: 5432
    used_space:
      description: Used space on the volume in tracks.
      type: int
      returned: always
      sample: 4584
    percent_free:
      description: Percentage of the volume that is free.
      type: float
      returned: always
      sample: 54.2
    percent_used:
      description: Percentage of the volume that is used.
      type: float
      returned: always
      sample: 45.8
    total_bytes:
      description: Total space on the volume in bytes.
      type: int
      returned: always
      sample: 567906000
    free_bytes:
      description: Free space on the volume in bytes.
      type: int
      returned: always
      sample: 307609600
    device_status:
      description: Detailed device status information derived from z/OS UCBSTAT flags.
      type: dict
      returned: always
      contains:
        is_online:
          description:
            - Whether the device is online.
            - Derived from the z/OS UCBSTAT C(ucbonli) flag.
          type: bool
          sample: true
        status_changing:
          description:
            - Whether the device status is currently changing.
            - Derived from the z/OS UCBSTAT C(ucbchgs) flag.
          type: bool
          sample: false
        is_reserved:
          description:
            - Whether the device is reserved.
            - Derived from the z/OS UCBSTAT C(ucbresv) flag.
          type: bool
          sample: false
        is_unloaded:
          description:
            - Whether the device is unloaded.
            - Derived from the z/OS UCBSTAT C(ucbunld) flag.
          type: bool
          sample: false
        is_allocated:
          description:
            - Whether the device is allocated to a job or user.
            - Derived from the z/OS UCBSTAT C(ucbaloc) flag.
          type: bool
          sample: false
        is_present:
          description:
            - Whether the device is present and available.
            - Derived from the z/OS UCBSTAT C(ucbpres) flag.
          type: bool
          sample: true
        is_system_residence:
          description:
            - Whether the volume contains system residence (IPL volume).
            - Derived from the z/OS UCBSTAT C(ucbsysr) flag.
          type: bool
          sample: false
        is_dasd:
          description:
            - Whether the device is a DASD device.
            - Derived from the z/OS UCBSTAT C(ucbdadi) flag.
          type: bool
          sample: true
    vtoc_info:
      description: VTOC (Volume Table of Contents) information.
      type: dict
      returned: always
      contains:
        index_vtoc:
          description: Whether the VTOC has an index.
          type: bool
          sample: true
        vtoc_active:
          description: Whether the VTOC index is active.
          type: bool
          sample: true
        is_cylinder_managed:
          description:
            - Whether the volume uses cylinder-managed space allocation.
            - When C(true), the VTOC uses cylinder boundaries for dataset
              allocation.
            - Derived from the ZOAU API C(is_cylinder_managed) field.
          type: bool
          sample: false
changed:
  description: Indicates whether any changes were made. Always false for this module.
  returned: always
  type: bool
  sample: false
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Successfully retrieved volume information for 2 volumes"
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dependency_checker import (
    validate_dependencies,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger

try:
    from zoautil_py import volumes as zoau_volumes
except Exception:
    zoau_volumes = ZOAUImportError(traceback.format_exc())

# Tracks per cylinder constant for 3390/3380 devices.
_TRACKS_PER_CYLINDER = 15
# Bytes per track for 3390 devices (56,664 bytes/track).
_BYTES_PER_TRACK = 56664


def _derive_status(ucb_status):
    """Derive a simplified status string from a ZOAU UCB status dict.

    The ZOAU Volume object exposes ``status`` as a plain dict with uppercase
    keys, e.g. ``{'UCBONLI': True, 'UCBCHGS': False, ...}``.

    Parameters
    ----------
    ucb_status : dict
        ZOAU status dict from ``vol.status``.

    Returns
    -------
    str
        One of 'pending', 'online', or 'offline'.
    """
    if ucb_status.get('UCBCHGS', False):
        return 'pending'
    if ucb_status.get('UCBONLI', False):
        return 'online'
    return 'offline'


def _build_device_status(ucb_status):
    """Map a ZOAU UCB status dict to the module's device_status return dict.

    Parameters
    ----------
    ucb_status : dict
        ZOAU status dict from ``vol.status``, e.g.
        ``{'UCBONLI': True, 'UCBCHGS': False, 'UCBRESV': False, ...}``.

    Returns
    -------
    dict
        Dictionary of boolean device status flags.
    """
    return {
        'is_online': bool(ucb_status.get('UCBONLI', False)),
        'status_changing': bool(ucb_status.get('UCBCHGS', False)),
        'is_reserved': bool(ucb_status.get('UCBRESV', False)),
        'is_unloaded': bool(ucb_status.get('UCBUNLD', False)),
        'is_allocated': bool(ucb_status.get('UCBALOC', False)),
        'is_present': bool(ucb_status.get('UCBPRES', False)),
        'is_system_residence': bool(ucb_status.get('UCBSYSR', False)),
        'is_dasd': bool(ucb_status.get('UCBDADI', False)),
    }


def _build_vtoc_info(vol):
    """Extract VTOC information from a ZOAU Volume object.

    ZOAU 1.4.x exposes VTOC fields as direct attributes on the Volume object:
    ``index_vtoc``, ``vtoc_active``, and ``is_cylinder_managed``.

    Parameters
    ----------
    vol : object
        ZOAU Volume object.

    Returns
    -------
    dict
        Dictionary of VTOC information flags.
    """
    return {
        'index_vtoc': bool(getattr(vol, 'index_vtoc', False)),
        'vtoc_active': bool(getattr(vol, 'vtoc_active', False)),
        'is_cylinder_managed': bool(getattr(vol, 'is_cylinder_managed', False)),
    }


def _volume_to_dict(vol):
    """Convert a ZOAU Volume object to the module's return dictionary.

    ZOAU 1.4.x Volume object attribute reference (from live debug output):
      - ``vol.volser``          -- volume serial number
      - ``vol.unit``            -- device number / unit address
      - ``vol.dev_type``        -- device type string (e.g. '3390')
      - ``vol.status``          -- dict of uppercase UCB flags
                                   {'UCBONLI': bool, 'UCBCHGS': bool, ...}
      - ``vol.total_tracks``    -- total tracks on volume
      - ``vol.free_tracks``     -- free tracks on volume
      - ``vol.index_vtoc``      -- bool, VTOC has an index
      - ``vol.vtoc_active``     -- bool, VTOC index is active
      - ``vol.is_cylinder_managed`` -- bool, cylinder-managed allocation

    Parameters
    ----------
    vol : object
        ZOAU Volume object.

    Returns
    -------
    dict
        Dictionary matching the module's documented return structure.
    """
    ucb_status = getattr(vol, 'status', {}) or {}
    device_status = _build_device_status(ucb_status)
    vtoc_info = _build_vtoc_info(vol)
    status = _derive_status(ucb_status)

    total_space = int(getattr(vol, 'total_tracks', 0) or 0)
    free_space = int(getattr(vol, 'free_tracks', 0) or 0)
    used_space = total_space - free_space

    if total_space > 0:
        percent_free = round((free_space / total_space) * 100, 1)
        percent_used = round(100.0 - percent_free, 1)
    else:
        percent_free = 0.0
        percent_used = 0.0

    total_bytes = total_space * _BYTES_PER_TRACK
    free_bytes = free_space * _BYTES_PER_TRACK

    return {
        'volser': str(getattr(vol, 'volser', '') or '').strip(),
        'device_number': str(getattr(vol, 'unit', '') or '').strip(),
        'device_type': str(getattr(vol, 'dev_type', '') or '').strip(),
        'status': status,
        'total_space': total_space,
        'free_space': free_space,
        'used_space': used_space,
        'percent_free': percent_free,
        'percent_used': percent_used,
        'total_bytes': total_bytes,
        'free_bytes': free_bytes,
        'device_status': device_status,
        'vtoc_info': vtoc_info,
    }


def _apply_filters(volume_list, filter_params):
    """Apply filter criteria to a list of volume dictionaries.

    Parameters
    ----------
    volume_list : list[dict]
        List of volume dictionaries already converted by _volume_to_dict.
    filter_params : dict
        Filter criteria from the module's 'filter' parameter.

    Returns
    -------
    list[dict]
        Filtered list of volume dictionaries.
    """
    if not filter_params:
        return volume_list

    status_filter = filter_params.get('status')
    free_space_min = filter_params.get('free_space_min')
    free_space_max = filter_params.get('free_space_max')
    percent_free_min = filter_params.get('percent_free_min')
    percent_free_max = filter_params.get('percent_free_max')
    vtoc_indexed = filter_params.get('vtoc_indexed')
    unit = filter_params.get('unit', 'tracks')

    # Convert cylinder thresholds to tracks for comparison.
    if unit == 'cylinders':
        if free_space_min is not None:
            free_space_min = free_space_min * _TRACKS_PER_CYLINDER
        if free_space_max is not None:
            free_space_max = free_space_max * _TRACKS_PER_CYLINDER

    result = []
    for vol in volume_list:
        if status_filter and vol['status'] not in status_filter:
            continue
        if free_space_min is not None and vol['free_space'] < free_space_min:
            continue
        if free_space_max is not None and vol['free_space'] > free_space_max:
            continue
        if percent_free_min is not None and vol['percent_free'] < percent_free_min:
            continue
        if percent_free_max is not None and vol['percent_free'] > percent_free_max:
            continue
        if vtoc_indexed is not None and vol['vtoc_info']['index_vtoc'] != vtoc_indexed:
            continue
        result.append(vol)

    return result


def get_volume_info(module):
    """Retrieve and return volume information according to module parameters.

    Parameters
    ----------
    module : AnsibleModule
        The Ansible module object.

    Returns
    -------
    tuple[list[dict], str]
        A tuple of (volume_list, message).

    Raises
    ------
    Exception
        Any error raised by the ZOAU volumes API.
    """
    logger = SingletonLogger().get_logger(module._verbosity)

    requested_volsers = module.params.get('volumes') or []
    requested_devices = module.params.get('device_numbers') or []
    filter_params = module.params.get('filter') or {}

    # Normalize inputs to uppercase for consistent matching.
    requested_volsers = [v.upper() for v in requested_volsers]
    requested_devices = [d.upper() for d in requested_devices]

    query_all = not requested_volsers and not requested_devices

    # ZOAU 1.4.x list_volumes() returns all volumes when called with no args.
    # It does not accept a volumes list — filtering by VOLSER or device number
    # is always done in Python after fetching the full list.
    logger.debug("Calling zoau_volumes.list_volumes() to retrieve all volumes.")
    raw_volumes = zoau_volumes.list_volumes()

    # Convert ZOAU objects to plain dicts.
    all_dicts = [_volume_to_dict(v) for v in (raw_volumes or [])]

    if query_all:
        matched = all_dicts
    elif not requested_devices:
        # VOLSER-only filter: keep only volumes whose volser was requested.
        requested_set = set(requested_volsers)
        matched = [v for v in all_dicts if v['volser'] in requested_set]
    else:
        # Union of VOLSER matches and device number matches, deduplicated by VOLSER.
        requested_volser_set = set(requested_volsers)
        requested_device_set = set(requested_devices)
        seen_volsers = set()
        matched = []
        for vol in all_dicts:
            if vol['volser'] in requested_volser_set or vol['device_number'].upper() in requested_device_set:
                if vol['volser'] not in seen_volsers:
                    seen_volsers.add(vol['volser'])
                    matched.append(vol)

    # Apply filters.
    filtered = _apply_filters(matched, filter_params)

    count = len(filtered)
    unit_word = "volume" if count == 1 else "volumes"
    msg = "Successfully retrieved volume information for {0} {1}".format(count, unit_word)

    return filtered, msg


def run_module():
    """Entry point for the zos_volume_free module."""
    module_args = dict(
        volumes=dict(type='list', elements='str', required=False, default=None),
        device_numbers=dict(type='list', elements='str', required=False, default=None),
        filter=dict(
            type='dict',
            required=False,
            default=None,
            options=dict(
                status=dict(
                    type='list',
                    elements='str',
                    choices=['online', 'offline', 'pending'],
                    required=False,
                ),
                free_space_min=dict(type='int', required=False),
                free_space_max=dict(type='int', required=False),
                percent_free_min=dict(type='int', required=False),
                percent_free_max=dict(type='int', required=False),
                vtoc_indexed=dict(type='bool', required=False),
                unit=dict(
                    type='str',
                    choices=['tracks', 'cylinders'],
                    default='tracks',
                    required=False,
                ),
            ),
        ),
    )

    result = dict(
        changed=False,
        volumes=[],
        msg='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    validate_dependencies(module)

    module_verbosity_level = module._verbosity
    SingletonLogger().get_logger(module_verbosity_level)

    if module.check_mode:
        result['msg'] = 'Check mode: no changes will be made.'
        module.exit_json(**result)

    volume_list = []
    msg = ''
    try:
        volume_list, msg = get_volume_info(module)
    except Exception as err:
        result['msg'] = 'An error occurred while querying volume information: {0}'.format(str(err))
        module.fail_json(**result)

    result['volumes'] = volume_list
    result['msg'] = msg
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
