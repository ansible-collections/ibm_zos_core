
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_zfs_resize.py

.. _zos_zfs_resize_module:


zos_zfs_resize -- Resize a zfs data set.
========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The module `zos_zfs_resize. </zos_zfs_resize.html>`_ can resize a zFS aggregate data set.
- The *target* data set must be a unique and a Fully Qualified Name (FQN) of a z/OS zFS aggregate data set.
- The data set must be attached as read-write.
- *size* must be provided.





Parameters
----------


target
  The Fully Qualified Name of the zFS data set that will be resized.

  | **required**: True
  | **type**: str


size
  The desired size of the data set after the resizing is performed.

  | **required**: True
  | **type**: int


space_type
  The unit of measurement to use when defining the size.

  Valid units are ``k`` (kilobytes), ``m`` (megabytes), ``g`` (gigabytes), ``cyl`` (cylinders), and ``trk`` (tracks).

  | **required**: False
  | **type**: str
  | **default**: k
  | **choices**: k, m, g, cyl, trk


no_auto_increase
  Option controls whether the data set size will be automatically increased when performing a shrink operation.

  When set to ``true``, during the shrinking of the zFS aggregate, if more space be needed the total size will not be increased and the module will fail.

  | **required**: False
  | **type**: bool
  | **default**: False


verbose
  Return diagnostic messages that describe the module's execution.

  Verbose includes standard out (stdout) of the module's execution which can be excessive, to avoid writing this to stdout, optionally you can set the ``trace_destination`` instead.

  | **required**: False
  | **type**: bool
  | **default**: False


trace_destination
  Specify a unique USS file name or data set name for ``trace_destination``.

  If the destination ``trace_destination`` is a USS file or path, the ``trace_destination`` must be an absolute path name.

  Support MVS data set type PDS, PDS/E(MEMBER)

  If the destination is an MVS data set name, the ``trace_destination`` provided must meet data set naming conventions of one or more qualifiers, each from one to eight characters long, that are delimited by periods

  Recommended characteristics for MVS data set are record length of 200, record format as vb and space primary 42000 kilobytes.

  | **required**: False
  | **type**: str




Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: none
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Resize an aggregate data set to 2500 kilobytes.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 2500

   - name: Resize an aggregate data set to 20 tracks.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       space_type: trk
       size: 20

   - name: Resize an aggregate data set to 4 megabytes.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       space_type: m
       size: 4

   - name: Resize an aggregate data set to 1000 kilobytes and set no auto increase if it's shrinking.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 1000
       no_auto_increase: true

   - name: Resize an aggregate data set and get verbose output.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 2500
       verbose: true

   - name: Resize an aggregate data set and get the full trace on a file.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 2500
       trace_destination: /tmp/trace.txt

   - name: Resize an aggregate data set and capture the trace into a PDS member.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 2500
       trace_destination: "TEMP.HELPER.STORAGE(RESIZE)"

   - name: Resize an aggregate data set and capture the trace into a file with verbose output.
     zos_zfs_resize:
       target: TEST.ZFS.DATA
       size: 2500
       verbose: true
       trace_destination: /tmp/trace.txt




Notes
-----

.. note::
   If needed, allocate the zFS trace output data set as a PDSE with RECFM=VB, LRECL=133 with a primary allocation of at least 50 cylinders and a secondary allocation of 30 cylinders.

   `zfsadm documentation <https://www.ibm.com/docs/en/zos/latest?topic=commands-zfsadm>`_.







Return Values
-------------


cmd
  The zfsadm command executed on the remote node.

  | **returned**: always
  | **type**: str
  | **sample**: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096

target
  The Fully Qualified Name of the resized zFS data set.

  | **returned**: always
  | **type**: str
  | **sample**: SOMEUSER.VVV.ZFS

mount_target
  The original share/mount of the data set.

  | **returned**: always
  | **type**: str
  | **sample**: /tmp/zfs_agg

size
  The desired size from option ``size`` according to ``space_type``. The resulting size can vary slightly, the actual space utilization is returned in ``new_size``.

  | **returned**: always
  | **type**: int
  | **sample**: 4024

rc
  The return code of the zfsadm command.

  | **returned**: always
  | **type**: int

old_size
  The original data set size according to ``space_type`` before resizing was performed.

  | **returned**: always
  | **type**: float
  | **sample**:

    .. code-block:: json

        3096

old_free_space
  The original data sets free space according to ``space_type`` before resizing was performed.

  | **returned**: always
  | **type**: float
  | **sample**:

    .. code-block:: json

        2.1

new_size
  The data set size according to ``space_type`` after resizing was performed.

  | **returned**: success
  | **type**: float
  | **sample**:

    .. code-block:: json

        4032

new_free_space
  The data sets free space according to ``space_type`` after resizing was performed.

  | **returned**: success
  | **type**: float
  | **sample**:

    .. code-block:: json

        1.5

space_type
  The measurement unit of space used to report all size values.

  | **returned**: always
  | **type**: str
  | **sample**: k

stdout
  The modules standard out (stdout) that is returned.

  | **returned**: always
  | **type**: str
  | **sample**: IOEZ00173I Aggregate TEST.ZFS.DATA.USER successfully grown.

stderr
  The modules standard error (stderr) that is returned. it may have no return value.

  | **returned**: always
  | **type**: str
  | **sample**: IOEZ00181E Could not open trace output dataset.

stdout_lines
  List of strings containing individual lines from standard out (stdout).

  | **returned**: always
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "IOEZ00173I Aggregate TEST.ZFS.DATA.USER successfully grown."
        ]

stderr_lines
  List of strings containing individual lines from standard error (stderr).

  | **returned**: always
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "IOEZ00181E Could not open trace output dataset."
        ]

verbose_output
  If ``verbose=true``, the operation's full traceback will show for this property.

  | **returned**: always
  | **type**: str
  | **sample**: 6FB2F8 print_trace_table printing contents of table Main Trace Table...

