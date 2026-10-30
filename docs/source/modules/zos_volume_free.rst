
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_volume_free.py

.. _ibm.ibm_zos_core.zos_volume_free_module:


zos_volume_free -- Query space and status information for z/OS DASD volumes
===========================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The *zos_volume_free* module retrieves space and status information for one or more z/OS DASD volumes.
- Volumes can be queried by volume serial number (VOLSER), by device number, or both. When neither is specified, all active DASD volumes are queried.
- When both *volumes* and *device_numbers* are specified, the module returns volumes that match **either** criterion (union), with automatic deduplication by VOLSER.
- Results can be filtered by volume status, free space thresholds, percentage free space, VTOC index status, and space allocation mode (cylinder-managed or track-managed).
- This module does not make any changes to the z/OS system and always returns ``changed`` as false.





Parameters
----------


volumes
  List of volume serial numbers (VOLSERs) to query.

  Can be a single volume or a list of volumes.

  When combined with *device_numbers*, returns volumes matching **either** criterion.

  If neither *volumes* nor *device_numbers* is specified, all active DASD volumes are queried.

  | **required**: False
  | **type**: list
  | **elements**: str


device_numbers
  List of device numbers (unit addresses) to query.

  When specified, the module queries all volumes and filters by device number.

  When combined with *volumes*, returns volumes matching **either** criterion, deduplicated by VOLSER.

  | **required**: False
  | **type**: list
  | **elements**: str


verbose
  Return additional diagnostic information for the volume query operation.

  This option is useful when troubleshooting volume discovery or query issues.

  | **required**: False
  | **type**: bool
  | **default**: False


filter
  Dictionary of filter criteria to apply to the volume results.

  Criteria include device status flags, free space thresholds, percentage free space, VTOC index status, and space allocation mode.

  All specified criteria are applied together (AND logic). Only volumes matching every criterion are returned.

  | **required**: False
  | **type**: dict


  status
    List of UCB device status flags to filter by.

    The matching behavior is controlled by *filter.status_match*.

    When *filter.status_match* is ``all`` (default), only volumes where **every** listed flag is ``true`` are returned.

    When *filter.status_match* is ``any``, only volumes where **at least one** listed flag is ``true`` are returned.

    ``online`` - device is online (``ucbonli``).

    ``offline_pending`` - device is transitioning from online to offline (``ucbchgs``).

    ``mount_reserved`` - mount status of the volume is reserved, which prevents the volume from unmounting when a job finishes (``ucbresv``).

    ``unload_pending`` - unload command addressed but device not yet unloaded (``ucbunld``).

    ``allocated`` - an active job is assigned to the device (``ucbaloc``).

    ``permanently_resident`` - mount status of the volume is permanently resident, which indicates that the volume cannot be physically demounted unless the device is offline (``ucbpres``).

    ``system_residence`` - device is a system residence device, primary console, or active console (``ucbsysr``).

    ``status_indicator`` - for tape volumes, standard tape labels have been verified to ensure the correct volume is mounted; for console devices, secondary console or console status is changing (``ucbdadi``).

    | **required**: False
    | **type**: list
    | **elements**: str
    | **choices**: online, offline_pending, mount_reserved, unload_pending, allocated, permanently_resident, system_residence, status_indicator


  status_match
    Controls how *filter.status* flags are matched.

    ``all`` — every flag listed in *filter.status* must be ``true`` on the volume (AND logic). This is the default.

    ``any`` — at least one flag listed in *filter.status* must be ``true`` on the volume (OR logic).

    Has no effect when *filter.status* is not specified or is empty.

    | **required**: False
    | **type**: str
    | **default**: all
    | **choices**: all, any


  free_space_min
    Minimum free space threshold.

    Value is in the unit specified by *filter.unit* (default tracks).

    Volumes with free space below this threshold are excluded.

    | **required**: False
    | **type**: int


  free_space_max
    Maximum free space threshold.

    Value is in the unit specified by *filter.unit* (default tracks).

    Volumes with free space above this threshold are excluded.

    | **required**: False
    | **type**: int


  percent_free_min
    Minimum percentage of free space (0–100).

    Volumes with a lower percentage of free space are excluded.

    | **required**: False
    | **type**: int


  percent_free_max
    Maximum percentage of free space (0–100).

    Volumes with a higher percentage of free space are excluded.

    | **required**: False
    | **type**: int


  vtoc_indexed
    Filter by VTOC index status.

    When ``true``, only volumes with an indexed VTOC are returned.

    When ``false``, only volumes without an indexed VTOC are returned.

    | **required**: False
    | **type**: bool


  cylinder_managed
    Filter by space allocation mode.

    When ``true``, only cylinder-managed volumes are returned.

    When ``false``, only track-managed volumes are returned.

    | **required**: False
    | **type**: bool


  unit
    Unit for *filter.free_space_min* and *filter.free_space_max* filter values.

    Does **not** affect the output format. All output space values are always expressed in tracks.

    When ``cylinders``, the conversion assumes 15 tracks per cylinder (standard for 3390/3380 devices).

    | **required**: False
    | **type**: str
    | **default**: tracks
    | **choices**: tracks, cylinders





Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: full
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
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

   - name: Get only online volumes (status_match defaults to all).
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         status:
           - online
     register: online_volumes

   - name: Get volumes with less than 20 percent free space that are online.
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         percent_free_max: 20
         status:
           - online
     register: low_space_volumes

   - name: Get volumes with at least 100 cylinders free that are online.
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

   - name: Get volumes that are online and allocated (both flags must be true — status_match all).
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         status:
           - online
           - allocated
         status_match: all
     register: online_allocated_volumes

   - name: Get volumes that are online and permanently resident (both flags must be true).
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         status:
           - online
           - permanently_resident
         status_match: all
     register: resident_volumes

   - name: Get volumes that are allocated or permanently resident (at least one — status_match any).
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         status:
           - allocated
           - permanently_resident
         status_match: any
     register: alloc_or_resident_volumes

   - name: Get cylinder-managed (EAV) volumes.
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         cylinder_managed: true
     register: eav_volumes

   - name: Get track-managed volumes that are online.
     ibm.ibm_zos_core.zos_volume_free:
       filter:
         cylinder_managed: false
         status:
           - online
     register: track_managed_online_volumes




Notes
-----

.. note::
   This module is read-only and always returns ``changed`` as ``false``.

   When a single VOLSER is specified with no *device_numbers*, the module performs an efficient direct lookup for that volume.

   When a single VOLSER is not found or not active, the module returns an empty ``volumes`` list with ``rc=0``. The missing VOLSER is listed in both ``msg`` and ``skipped_volumes``.

   When multiple VOLSERs or any *device_numbers* are specified, all active volumes are retrieved first and then filtered. Any VOLSERs not found are listed in ``skipped_volumes``; any device numbers not found are listed in ``skipped_device_numbers``.

   The *filter.unit* parameter only affects how *filter.free_space_min* and *filter.free_space_max* are interpreted. All output space values are always in tracks.

   To convert output tracks to cylinders, divide by 15 (for 3390/3380 devices).

   Space is reported in both tracks (``total_space``, ``free_space``) and kilobytes (``total_kilobytes``, ``free_kilobytes``).



See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zos_core.zos_volume_init_module`




Return Values
-------------


volumes
  List of volume information matching the query and filter criteria.

  | **returned**: always
  | **type**: list
  | **elements**: dict

  volser
    Volume serial number.

    | **returned**: always
    | **type**: str
    | **sample**: USER01

  device_number
    Device number (unit address).

    | **returned**: always
    | **type**: str
    | **sample**: 0A80

  total_space
    Total space on the volume in tracks.

    | **returned**: always
    | **type**: int
    | **sample**: 467460

  free_space
    Free space on the volume in tracks.

    | **returned**: always
    | **type**: int
    | **sample**: 32747

  used_space
    Used space on the volume in tracks.

    Calculated as ``total_space - free_space``.

    | **returned**: always
    | **type**: int
    | **sample**: 434713

  percent_free
    Percentage of the volume that is free.

    | **returned**: always
    | **type**: float
    | **sample**:

      .. code-block:: json

          7.0

  percent_used
    Percentage of the volume that is used.

    | **returned**: always
    | **type**: float
    | **sample**:

      .. code-block:: json

          93.0

  total_kilobytes
    Total space on the volume in kilobytes.

    | **returned**: always
    | **type**: int
    | **sample**: 25867337

  free_kilobytes
    Free space on the volume in kilobytes.

    | **returned**: always
    | **type**: int
    | **sample**: 1812085

  status
    Device status flags derived from z/OS UCB status bits.

    | **returned**: always
    | **type**: dict

    online
      Device is online.

      Derived from the z/OS UCB ``ucbonli`` flag.

      | **returned**: always
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    offline_pending
      Device status is transitioning from online to offline, and either allocation is enqueued on the device or the device is currently allocated (``ucbonli`` bit is also set).

      Derived from the z/OS UCB ``ucbchgs`` flag.

      | **returned**: always
      | **type**: bool

    mount_reserved
      The mount status of the volume on this device is reserved.

      Derived from the z/OS UCB ``ucbresv`` flag.

      | **returned**: always
      | **type**: bool

    unload_pending
      An unload operator command has been addressed to this device. The device has not yet been unloaded.

      Derived from the z/OS UCB ``ucbunld`` flag.

      | **returned**: always
      | **type**: bool

    allocated
      Device is allocated. For auto-switchable devices in a SYSPLEX, indicates the device was allocated by some system in the SYSPLEX at the time allocation last obtained the SYSPLEX allocation status.

      Derived from the z/OS UCB ``ucbaloc`` flag.

      | **returned**: always
      | **type**: bool

    permanently_resident
      The mount status of the volume on this device is permanently resident.

      Derived from the z/OS UCB ``ucbpres`` flag.

      | **returned**: always
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    system_residence
      Device is a system residence device, primary console, or active console.

      Derived from the z/OS UCB ``ucbsysr`` flag.

      | **returned**: always
      | **type**: bool

    status_indicator
      For tape volumes, indicates that standard tape labels have been verified. For console devices, indicates a secondary console or that console status is changing.

      Derived from the z/OS UCB ``ucbdadi`` flag.

      | **returned**: always
      | **type**: bool


  cylinder_managed
    Whether the volume uses cylinder-managed space allocation.

    When ``true``, space is allocated on cylinder boundaries rather than track boundaries. Typical of Extended Address Volumes (EAV) and some SMS-managed volumes.

    | **returned**: always
    | **type**: bool

  vtoc_info
    VTOC (Volume Table of Contents) information.

    | **returned**: always
    | **type**: dict

    index_vtoc
      Whether the VTOC has an index.

      | **returned**: always
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    vtoc_active
      Whether the VTOC index is active.

      | **returned**: always
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true



skipped_volumes
  VOLSERs that were requested but not found or inaccessible on the system.

  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "222224"
        ]

skipped_device_numbers
  Device numbers that were requested but not found or inaccessible on the system.

  | **returned**: always
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "0A80"
        ]

changed
  Indicates whether any changes were made. Always false for this module.

  | **returned**: always
  | **type**: bool

rc
  The return code from the ZOAU ``vf`` utility execution.

  ``0`` when the query executes successfully, including when a requested VOLSER is not found (which returns ``rc=0`` with an empty ``volumes`` list).

  Non-zero integer (such as ``8``, ``12``, ``16``) when the underlying ZOAU ``vf`` utility encounters an error.

  Otherwise ``null`` (None).

  | **returned**: always
  | **type**: int

msg
  Message describing the result.

  | **returned**: always
  | **type**: str
  | **sample**: Found 2 matching volumes.

stdout
  Always an empty string on success.

  On failure, contains the standard output from the failed operation.

  | **returned**: always
  | **type**: str

stderr
  Always an empty string on success.

  On failure, contains the error output or exception message.

  | **returned**: always
  | **type**: str

