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

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_volume_free
version_added: '2.2.0'
author:
  - "Ravella Surendra Babu (@surendrababuravella)"
short_description: Query space and status information for z/OS DASD volumes
description:
  - The I(zos_volume_free) module retrieves space and status information for
    one or more z/OS DASD volumes.
  - Volumes can be queried by volume serial number (VOLSER), by device number,
    or both. When neither is specified, all active DASD volumes are queried.
  - When both I(volumes) and I(device_numbers) are specified, the module
    returns volumes that match B(either) criterion (union), with automatic
    deduplication by VOLSER.
  - Results can be filtered by volume status, free space thresholds, percentage
    free space, and VTOC index status.
  - This module does not make any changes to the z/OS system and always returns
    C(changed) as false.
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
          - Filter by one or more UCB device status flags.
          - Only volumes where B(all) listed flags are C(true) in the
            C(status) return field are included.
          - C(is_online) - device is online (C(ucbonli)).
          - C(is_offline_pending) - device is transitioning from online to offline
            (C(ucbchgs)).
          - C(is_mount_reserved) - mount status of the volume is reserved (C(ucbresv)).
          - C(is_unload_pending) - unload command addressed but device not yet
            unloaded (C(ucbunld)).
          - C(is_allocated) - device is allocated (C(ucbaloc)).
          - C(is_permanently_resident) - mount status of the volume is permanently resident
            (C(ucbpres)).
          - C(is_system_residence) - system residence device, primary console,
            or active console (C(ucbsysr)).
        type: list
        elements: str
        choices:
          - is_online
          - is_offline_pending
          - is_mount_reserved
          - is_unload_pending
          - is_allocated
          - is_permanently_resident
          - is_system_residence
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
          - Minimum percentage of free space (0–100).
          - Volumes with a lower percentage of free space are excluded.
        type: int
      percent_free_max:
        description:
          - Maximum percentage of free space (0–100).
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
  - This module is read-only and always returns C(changed) as false.
  - When a single VOLSER is specified with no I(device_numbers), the module
    uses C(list_volumes(volume_serial=)) for an efficient direct lookup.
  - When multiple VOLSERs or any I(device_numbers) are specified, all active
    volumes are retrieved first and then filtered in Python.
  - When both I(volumes) and I(device_numbers) are specified, the module
    returns volumes that match either criterion with automatic deduplication
    by VOLSER.
  - The I(filter.unit) parameter only affects how I(filter.free_space_min)
    and I(filter.free_space_max) are interpreted. All output space values are
    always in tracks.
  - To convert output tracks to cylinders, divide by 15 (for 3390/3380 devices).
  - Space is reported in both tracks (C(total_space), C(free_space)) and
    kilobytes (C(total_kilobytes), C(free_kilobytes)) as provided by the
    ZOAU API. No device type field is available from the ZOAU Volume API.

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
        - is_online
  register: online_volumes

- name: Get volumes with less than 20 percent free space that are online.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      percent_free_max: 20
      status:
        - is_online
  register: low_space_volumes

- name: Get volumes with at least 100 cylinders free that are online.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      free_space_min: 100
      unit: cylinders
      status:
        - is_online
  register: volumes_with_space

- name: Get volumes with an indexed VTOC.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      vtoc_indexed: true
  register: indexed_volumes

- name: Get volumes that are online and allocated.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      status:
        - is_online
        - is_allocated
  register: online_allocated_volumes

- name: Get volumes that are online and permanently resident.
  ibm.ibm_zos_core.zos_volume_free:
    filter:
      status:
        - is_online
        - is_permanently_resident
  register: resident_volumes
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
    total_space:
      description: Total space on the volume in tracks.
      type: int
      returned: always
      sample: 467460
    free_space:
      description: Free space on the volume in tracks.
      type: int
      returned: always
      sample: 32747
    used_space:
      description:
        - Used space on the volume in tracks.
        - Calculated as C(total_space - free_space). Clamped to C(0) if ZOAU
          reports C(free_tracks) greater than C(total_tracks) due to
          corrupt or in-motion VTOC data.
      type: int
      returned: always
      sample: 434713
    percent_free:
      description: Percentage of the volume that is free.
      type: float
      returned: always
      sample: 7.0
    percent_used:
      description: Percentage of the volume that is used.
      type: float
      returned: always
      sample: 93.0
    total_kilobytes:
      description: Total space on the volume in kilobytes (derived from C(vol.total_bytes / 1024)).
      type: int
      returned: always
      sample: 25867337
    free_kilobytes:
      description: Free space on the volume in kilobytes (derived from C(vol.free_bytes / 1024)).
      type: int
      returned: always
      sample: 1812085
    status:
      description: Device status flags derived from z/OS UCB status bits.
      type: dict
      returned: always
      contains:
        is_online:
          description:
            - Device is online.
            - Derived from the z/OS UCB C(ucbonli) flag.
          type: bool
          sample: true
        is_offline_pending:
          description:
            - Device status is transitioning from online to offline, and either
              allocation is enqueued on the device or the device is currently
              allocated (C(ucbonli) bit is also set).
            - Derived from the z/OS UCB C(ucbchgs) flag.
          type: bool
          sample: false
        is_mount_reserved:
          description:
            - The mount status of the volume on this device is reserved.
            - Derived from the z/OS UCB C(ucbresv) flag.
          type: bool
          sample: false
        is_unload_pending:
          description:
            - An unload operator command has been addressed to this device.
              The device has not yet been unloaded.
            - Derived from the z/OS UCB C(ucbunld) flag.
          type: bool
          sample: false
        is_allocated:
          description:
            - Device is allocated. For auto-switchable devices in a SYSPLEX,
              indicates the device was allocated by some system in the SYSPLEX
              at the time allocation last obtained the SYSPLEX allocation status.
            - Derived from the z/OS UCB C(ucbaloc) flag.
          type: bool
          sample: false
        is_permanently_resident:
          description:
            - The mount status of the volume on this device is permanently
              resident.
            - Derived from the z/OS UCB C(ucbpres) flag.
          type: bool
          sample: true
        is_system_residence:
          description:
            - Device is a system residence device, primary console, or active
              console.
            - Derived from the z/OS UCB C(ucbsysr) flag.
          type: bool
          sample: false
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
rc:
  description:
    - The return code is C(0) when the command executes successfully.
    - The return code is mapped from C(ZOAUException.response.rc) when a ZOAU
      error occurs.
    - The return code is C(5) when parameter validation fails.
    - The return code is C(8) when a JSON decode error occurs (e.g. BGYSC6606E).
    - The return code is C(1) when any other unexpected error occurs.
  returned: always
  type: int
  sample: 0
msg:
  description: Message describing the result.
  returned: always
  type: str
  sample: "Successfully retrieved volume information for 2 volumes"
stdout:
  description:
    - Always an empty string on success.
    - On a ZOAU failure, contains C(ZOAUException.response.stdout_response).
  returned: always
  type: str
  sample: ""
stderr:
  description:
    - Error output returned on failure. Empty string on success.
    - On a ZOAU failure, contains C(ZOAUException.response.stderr_response).
    - On any other failure, contains the Python exception message.
  returned: always
  type: str
  sample: ""
"""

import json
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.dependency_checker import (
    validate_dependencies,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger

try:
    from zoautil_py import volumes
    from zoautil_py import exceptions as zoau_exceptions
except Exception:
    volumes = ZOAUImportError(traceback.format_exc())
    zoau_exceptions = ZOAUImportError(traceback.format_exc())

class VolumeUCBError(Exception):
    """Raised when ZOAU cannot obtain UCB data for a volume serial (BGYSC6606E).

    Carries rc=8 so run_module can distinguish this specific failure
    from all other exceptions (rc=1) without catching bare JSONDecodeError,
    which could originate from unrelated code paths.
    """
    rc: int = 8


# Tracks per cylinder constant for 3390/3380 devices.
_TRACKS_PER_CYLINDER = 15


def _build_device_status(ucb_status):
    """Map a ZOAU UCB status dict to the module's status return dict.

    The ZOAU Python API exposes ``vol.status`` as a plain Python ``dict``
    with lowercase string keys (``ucbonli``, ``ucbchgs``, etc.).

    UCB flag semantics
    ------------------
    ucbonli : Device is online.
    ucbchgs : Device status is transitioning from online to offline, and either
              allocation is enqueued on the device or the device is allocated.
              (ucbonli bit is also set.)
    ucbresv : The mount status of the volume on this device is reserved.
    ucbunld : An unload operator command has been addressed to this device;
              the device has not yet been unloaded.
    ucbaloc : Device is allocated. For auto-switchable SYSPLEX devices,
              indicates the device was allocated by some system in the SYSPLEX
              at the time allocation last obtained the SYSPLEX allocation status.
    ucbpres : The mount status of the volume on this device is permanently
              resident.
    ucbsysr : System residence device, primary console, or active console.

    Parameters
    ----------
    ucb_status : dict or None
        ZOAU status dict from ``vol.status``.

    Returns
    -------
    dict
        Dictionary of boolean device status flags.
    """
    if not ucb_status:
        ucb_status = {}
    return {
        'is_online': bool(ucb_status.get('ucbonli', False)),
        'is_offline_pending': bool(ucb_status.get('ucbchgs', False)),
        'is_mount_reserved': bool(ucb_status.get('ucbresv', False)),
        'is_unload_pending': bool(ucb_status.get('ucbunld', False)),
        'is_allocated': bool(ucb_status.get('ucbaloc', False)),
        'is_permanently_resident': bool(ucb_status.get('ucbpres', False)),
        'is_system_residence': bool(ucb_status.get('ucbsysr', False)),
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

    ZOAU Volume constructor parameters (zoautil_py.volumes.Volume):
      - ``vol.volser``              -- str, volume serial number
      - ``vol.unit``                -- str, four-character device number
      - ``vol.status``              -- dict with lowercase UCB flag keys:
                                       ucbonli, ucbchgs, ucbresv, ucbunld,
                                       ucbaloc, ucbpres, ucbsysr, ucbdadi
      - ``vol.free_bytes``          -- int, available volume space in bytes (divide by 1024 for KB)
      - ``vol.total_bytes``         -- int, total volume space in bytes (divide by 1024 for KB)
      - ``vol.percentage_used``     -- float, volume space in use as a percentage
      - ``vol.free_tracks``         -- int, number of free tracks
      - ``vol.total_tracks``        -- int, total number of tracks
      - ``vol.is_cylinder_managed`` -- bool, True for cylinder-managed space
      - ``vol.index_vtoc``          -- bool, index exists for VTOC
      - ``vol.vtoc_active``         -- bool, index VTOC active

    Parameters
    ----------
    vol : object
        ZOAU Volume object.

    Returns
    -------
    dict
        Dictionary matching the module's documented return structure.
    """
    ucb_status = getattr(vol, 'status', None)
    status = _build_device_status(ucb_status)
    vtoc_info = _build_vtoc_info(vol)

    total_space = int(getattr(vol, 'total_tracks', 0) or 0)
    free_space = int(getattr(vol, 'free_tracks', 0) or 0)
    # Clamp to 0: corrupt or in-motion VTOC data can report free_tracks > total_tracks.
    used_space = max(0, total_space - free_space)

    if total_space > 0:
        percent_free = round((free_space / total_space) * 100, 1)
        percent_used = round(100.0 - percent_free, 1)
    else:
        percent_free = 0.0
        percent_used = 0.0

    # ZOAU stores space in bytes as vol.free_bytes / vol.total_bytes.
    # The constructor parameter names (free_kilobytes, total_kilobytes) differ
    # from the live attribute names confirmed by debug output. Divide by 1024.
    total_kilobytes = int(getattr(vol, 'total_bytes', 0) or 0) // 1024
    free_kilobytes = int(getattr(vol, 'free_bytes', 0) or 0) // 1024

    return {
        'volser': str(getattr(vol, 'volser', '') or '').strip(),
        'device_number': str(getattr(vol, 'unit', '') or '').strip(),
        'total_space': total_space,
        'free_space': free_space,
        'used_space': used_space,
        'percent_free': percent_free,
        'percent_used': percent_used,
        'total_kilobytes': total_kilobytes,
        'free_kilobytes': free_kilobytes,
        'status': status,
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

    status_flags = filter_params.get('status') or []
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
        # All listed UCB flags must be True in status.
        if any(not vol['status'].get(flag) for flag in status_flags):
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
    zoau_exceptions.ZOAUException
        Raised by ZOAU if the list_volumes() call fails.
    Exception
        Any other unexpected error.
    """
    logger = SingletonLogger().get_logger(module._verbosity)

    requested_volsers = module.params.get('volumes') or []
    requested_devices = module.params.get('device_numbers') or []
    filter_params = module.params.get('filter') or {}

    # Normalize inputs to uppercase for consistent matching.
    requested_volsers = [v.upper() for v in requested_volsers]
    requested_devices = [d.upper() for d in requested_devices]

    query_all = not requested_volsers and not requested_devices

    single_volser_lookup = len(requested_volsers) == 1 and not requested_devices
    try:
        if query_all:
            # No criteria: retrieve all active DASD volumes.
            logger.debug("Calling volumes.list_volumes() to retrieve all volumes.")
            raw_volumes = volumes.list_volumes()
            matched = [_volume_to_dict(v) for v in (raw_volumes or [])]
        elif single_volser_lookup:
            # Single VOLSER, no devices: direct lookup.
            # list_volumes(volume_serial=) raises ZOAUException or
            # json.JSONDecodeError when the volume does not exist or is not
            # active (ZOAU receives empty output, e.g. BGYSC6606E).
            # ZOAUException is re-raised as-is; JSONDecodeError is converted
            # to an Exception with the BGYSC6606E message.
            logger.debug("Calling volumes.list_volumes(volume_serial=%r).", requested_volsers[0])
            try:
                raw_volumes = volumes.list_volumes(volume_serial=requested_volsers[0])
                matched = [_volume_to_dict(v) for v in (raw_volumes or [])]
            except zoau_exceptions.ZOAUException:
                raise
            except json.JSONDecodeError:
                raise VolumeUCBError(
                    "BGYSC6606E Could not obtain UCB for volume serial {0}".format(requested_volsers[0])
                )
        elif not requested_devices:
            # Multiple VOLSERs, no devices: fetch all and filter by VOLSER set.
            logger.debug("Calling volumes.list_volumes() for multi-VOLSER query.")
            raw_volumes = volumes.list_volumes()
            requested_set = set(requested_volsers)
            all_dicts = [_volume_to_dict(v) for v in (raw_volumes or [])]
            matched = [v for v in all_dicts if v['volser'] in requested_set]
        else:
            # Device numbers present (VOLSERs may also be present): union match.
            logger.debug("Calling volumes.list_volumes() for device query.")
            raw_volumes = volumes.list_volumes()
            requested_volser_set = set(requested_volsers)
            requested_device_set = set(requested_devices)
            all_dicts = [_volume_to_dict(v) for v in (raw_volumes or [])]
            seen_volsers = set()
            matched = []
            for vol in all_dicts:
                if vol['volser'] in requested_volser_set or vol['device_number'].upper() in requested_device_set:
                    if vol['volser'] not in seen_volsers:
                        seen_volsers.add(vol['volser'])
                        matched.append(vol)
    except zoau_exceptions.ZOAUException:
        raise

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
                    choices=[
                        'is_online', 'is_offline_pending', 'is_mount_reserved',
                        'is_unload_pending', 'is_allocated', 'is_permanently_resident',
                        'is_system_residence',
                    ],
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

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    validate_dependencies(module)

    args_def = dict(
        volumes=dict(
            arg_type='list',
            elements='volume',
            required=False,
        ),
        device_numbers=dict(
            arg_type='list',
            elements='str',
            required=False,
        ),
        filter=dict(
            arg_type='dict',
            required=False,
            options=dict(
                status=dict(arg_type='list', elements='str', required=False),
                free_space_min=dict(arg_type='int', required=False),
                free_space_max=dict(arg_type='int', required=False),
                percent_free_min=dict(arg_type='int', required=False),
                percent_free_max=dict(arg_type='int', required=False),
                vtoc_indexed=dict(arg_type='bool', required=False),
                unit=dict(arg_type='str', required=False),
            ),
        ),
    )

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            changed=False,
            volumes=[],
            rc=5,
            msg='Parameter verification failed.',
            stdout='',
            stderr=str(err),
        )

    module_verbosity_level = module._verbosity
    SingletonLogger().get_logger(module_verbosity_level)

    result = dict(
        changed=False,
        volumes=[],
        msg='',
        rc=0,
        stdout='',
        stderr='',
    )

    volume_list = []
    msg = ''
    try:
        volume_list, msg = get_volume_info(module)
    except zoau_exceptions.ZOAUException as err:
        result['rc'] = err.response.rc
        result['msg'] = err.message
        result['stdout'] = err.response.stdout_response
        result['stderr'] = err.response.stderr_response
        module.fail_json(**result)
    except Exception as err:
        result['rc'] = getattr(err, 'rc', 1)
        result['msg'] = 'An unexpected error occurred while querying volume information: {0}'.format(str(err))
        result['stderr'] = str(err)
        module.fail_json(**result)

    result['volumes'] = volume_list
    result['msg'] = msg
    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
