
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_volume_init.py

.. _zos_volume_init_module:


zos_volume_init -- Initialize volumes or minidisks.
===================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Initialize a volume or minidisk on z/OS.
- *zos_volume_init* will create the volume label and entry into the volume table of contents (VTOC).
- Volumes are used for storing data and executable programs.
- A minidisk is a portion of a disk that is linked to your virtual machine.
- A VTOC lists the data sets that reside on a volume, their location, size, and other attributes.
- *zos_volume_init* uses the ICKDSF command INIT to initialize a volume. In some cases the command could be protected by facility class `STGADMIN.ICK.INIT`. Protection occurs when the class is active, and the class profile is defined. Ensure the user executing the Ansible task is permitted to execute ICKDSF command INIT, otherwise, any user can use the command.
- ICKDSF is an Authorized Program Facility (APF) program on z/OS, *zos_volume_init* will run in authorized mode but if the program ICKDSF is not APF authorized, the task will end.
- Note that defaults set on target z/OS systems may override ICKDSF parameters.
- If is recommended that data on the volume is backed up as the *zos_volume_init* module will not perform any backups. You can use the `zos_backup_restore <./zos_backup_restore.html>`_ module to backup a volume.





Parameters
----------


address
  *address* is a 3 or 4 digit hexadecimal number that specifies the address of the volume or minidisk.

  *address* can be the number assigned to the device (device number) when it is installed or the virtual address.

  | **required**: True
  | **type**: str


verify_volid
  Verify that the volume serial matches what is on the existing volume or minidisk.

  *verify_volid* must be 1 to 6 alphanumeric characters or ``*NONE*``.

  To verify that a volume serial number does not exist, use *verify_volid=*NONE**.

  If *verify_volid* is specified and the volume serial number does not match that found on the volume or minidisk, initialization does not complete.

  If *verify_volid=*NONE** is specified and a volume serial is found on the volume or minidisk, initialization does not complete.

  Note, this option is **not** a boolean, leave it blank to skip the verification.

  | **required**: False
  | **type**: str


verify_offline
  Verify that the device is not online to any other systems, initialization does not complete.

  | **required**: False
  | **type**: bool
  | **default**: True


volid
  The volume serial number used to initialize a volume or minidisk.

  Expects 1-6 alphanumeric, national ($,#,@) or special characters.

  A *volid* with less than 6 characters will be padded with spaces.

  A *volid* can also be referred to as volser or volume serial number.

  When *volid* is not specified for a previously initialized volume or minidisk, the volume serial number will remain unchanged.

  | **required**: False
  | **type**: str


vtoc_size
  The number of tracks to initialize the volume table of contents (VTOC) with.

  The VTOC will be placed in cylinder 0 head 1.

  If no tracks are specified it will default to the number of tracks in a cylinder minus 1. Tracks in a cylinder vary based on direct-access storage device (DASD) models, for 3390 a cylinder is 15 tracks.

  | **required**: False
  | **type**: int


index
  Create a volume table of contents (VTOC) index.

  The VTOC index enhances the performance of VTOC access.

  When set to *false*, no index will be created.

  | **required**: False
  | **type**: bool
  | **default**: True


sms_managed
  Specifies that the volume be managed by Storage Management System (SMS).

  If *sms_managed* is *true* then *index* must also be *true*.

  | **required**: False
  | **type**: bool
  | **default**: True


verify_volume_empty
  Verify that no data sets other than the volume table of contents (VTOC) index or the VSAM Volume Data Set(VVDS) exist on the target volume.

  | **required**: False
  | **type**: bool
  | **default**: True


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup datasets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the value ``TMPHLQ`` is used.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Initialize target volume with all default options. Target volume address is '1234', set volume name to 'DEMO01'.
           Target volume is checked to ensure it is offline and contains no data sets. Volume is SMS managed, has an index
           and VTOC size defined by the system.
     zos_volume_init:
       address: "1234"
       volid: "DEMO01"

   - name: Initialize target volume with all default options and additionally check the existing volid
           matches the given value 'DEMO02' before re-initializing the volume and renaming it to 'DEMO01'.
     zos_volume_init:
       address: "1234"
       volid: "DEMO01"
       verify_volid: "DEMO02"

   - name: Initialize non-SMS managed target volume with all the default options.
     zos_volume_init:
       address: "1234"
       volid: "DEMO01"
       sms_managed: no

   - name: Initialize non-SMS managed target volume with all the default options and
           override the default high level qualifier (HLQ).
     zos_volume_init:
       address: 1234
       volid: DEMO01
       sms_managed: no
       tmp_hlq: TESTUSR

   - name: Initialize a new SMS managed DASD volume with new volume serial 'e8d8' with 30 track VTOC, an index, as long as
           the existing volume serial is 'ine8d8' and there are no pre-existing data sets on the target. The check to see
           if volume is online before intialization is skipped.
     zos_volume_init:
       address: e8d8
       vtoc_size: 30
       index: yes
       sms_managed: yes
       volid: ine8d8
       verify_volid: ine8d8
       verify_volume_empty: yes
       verify_offline: no

   - name: Initialize 3 new DASD volumes (0901, 0902, 0903) for use on a z/OS system as 'DEMO01', 'DEMO02', 'DEMO03'
           using Ansible loops.
     zos_volume_init:
       address: "090{{ item }}"
       volid: "DEMO0{{ item }}"
     loop: "{{ range(1, 4, 1) }}"






See Also
--------

.. seealso::

   - :ref:`zos_backup_restore_module`




Return Values
-------------


msg
  Failure message returned by module.

  | **returned**: failure
  | **type**: str
  | **sample**: 'Index' cannot be False for SMS managed volumes.

rc
  Return code from ICKDSF init command.

  | **returned**: when ICKDSF program is run.
  | **type**: dict

content
  Raw output from ICKDSF.

  | **returned**: when ICKDSF program is run.
  | **type**: list
  | **elements**: str
  | **sample**:

    .. code-block:: json

        [
            "1ICKDSF - MVS/ESA    DEVICE SUPPORT FACILITIES 17.0                TIME: 18:32:22        01/17/23     PAGE   1",
            "0        ",
            "0 INIT UNIT(0903) NOVERIFY NOVERIFYOFFLINE VOLID(KET678) -",
            "0   NODS NOINDEX",
            "-ICK00700I DEVICE INFORMATION FOR 0903 IS CURRENTLY AS FOLLOWS:",
            "-          PHYSICAL DEVICE = 3390",
            "-          STORAGE CONTROLLER = 2107",
            "-          STORAGE CONTROL DESCRIPTOR = E8",
            "-          DEVICE DESCRIPTOR = 0C",
            "-          ADDITIONAL DEVICE INFORMATION = 4A00003C",
            "-          TRKS/CYL = 15, # PRIMARY CYLS = 100",
            "0ICK04000I DEVICE IS IN SIMPLEX STATE",
            "0ICK00703I DEVICE IS OPERATED AS A MINIDISK",
            " ICK00091I 0903 NED=002107.900.IBM.75.0000000BBA01",
            "-ICK03091I EXISTING VOLUME SERIAL READ = KET987",
            "-ICK03096I EXISTING VTOC IS LOCATED AT CCHH=X\u00270000 0001\u0027 AND IS    14 TRACKS.",
            "0ICK01314I VTOC IS LOCATED AT CCHH=X\u00270000 0001\u0027 AND IS    14 TRACKS.",
            "-ICK00001I FUNCTION COMPLETED, HIGHEST CONDITION CODE WAS 0",
            "0          18:32:22    01/17/23",
            "0        ",
            "-ICK00002I ICKDSF PROCESSING COMPLETE. MAXIMUM CONDITION CODE WAS 0"
        ]

