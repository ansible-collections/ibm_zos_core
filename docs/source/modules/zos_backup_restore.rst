
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_backup_restore.py

.. _zos_backup_restore_module:


zos_backup_restore -- Backup and restore data sets and volumes
==============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create and restore from backups of data sets and volumes.
- Data set backups are performed using logical dumps, volume backups are performed using physical dumps.
- Backups are compressed using AMATERSE.
- Backups are created by first dumping data sets with ADRDSSU, followed by compression with AMATERSE.
- Restoration is performed by first decompressing an archive with AMATERSE, then restoring with ADRDSSU.
- Since ADRDSSU and AMATERSE are used to create and restore backups, backups can be restored to systems where Ansible and ZOAU are not available. Conversely, dumps created with ADRDSSU and AMATERSE can be restored using this module.





Parameters
----------


operation
  Used to specify the operation to perform.

  | **required**: True
  | **type**: str
  | **choices**: backup, restore


data_sets
  Determines which data sets to include in the backup.

  | **required**: False
  | **type**: dict


  include
    When *operation=backup*, specifies a list of data sets or data set patterns to include in the backup.

    When *operation=restore*, specifies a list of data sets or data set patterns to include when restoring from a backup.

    The single asterisk, ``*``, is used in place of exactly one qualifier. In addition, it can be used to indicate to DFSMSdss that only part of a qualifier has been specified.

    When used with other qualifiers, the double asterisk, ``**``, indicates either the nonexistence of leading, trailing, or middle qualifiers, or the fact that they play no role in the selection process.

    Two asterisks are the maximum permissible in a qualifier. If there are two asterisks in a qualifier, they must be the first and last characters.

    A question mark ``?`` or percent sign ``%`` matches a single character.

    | **required**: False
    | **type**: raw


  exclude
    When *operation=backup*, specifies a list of data sets or data set patterns to exclude from the backup.

    When *operation=restore*, specifies a list of data sets or data set patterns to exclude when restoring from a backup.

    The single asterisk, ``*``, is used in place of exactly one qualifier. In addition, it can be used to indicate that only part of a qualifier has been specified."

    When used with other qualifiers, the double asterisk, ``**``, indicates either the nonexistence of leading, trailing, or middle qualifiers, or the fact that they play no role in the selection process.

    Two asterisks are the maximum permissible in a qualifier. If there are two asterisks in a qualifier, they must be the first and last characters.

    A question mark ``?`` or percent sign ``%`` matches a single character.

    | **required**: False
    | **type**: raw



volume
  This applies to both data set restores and volume restores.

  When *operation=backup* and *data_sets* are provided, specifies the volume that contains the data sets to backup.

  When *operation=restore*, specifies the volume the backup should be restored to.

  *volume* is required when restoring a full volume backup.

  | **required**: False
  | **type**: str


full_volume
  When *operation=backup* and *full_volume=True*, specifies that the entire volume provided to *volume* should be backed up.

  When *operation=restore* and *full_volume=True*, specifies that the volume should be restored (default is dataset).

  *volume* must be provided when *full_volume=True*.

  | **required**: False
  | **type**: bool
  | **default**: False


temp_volume
  Specifies a particular volume on which the temporary data sets should be created during the backup and restore process.

  When *operation=backup* and *backup_name* is a data set, specifies the volume the backup should be placed in.

  | **required**: False
  | **type**: str


backup_name
  When *operation=backup*, the destination data set or UNIX file to hold the backup.

  When *operation=restore*, the destination data set or UNIX file backup to restore.

  There are no enforced conventions for backup names. However, using a common extension like ``.dzp`` for UNIX files and ``.DZP`` for data sets will improve readability.

  | **required**: True
  | **type**: str


recover
  Specifies if potentially recoverable errors should be ignored.

  | **required**: False
  | **type**: bool
  | **default**: False


overwrite
  When *operation=backup*, specifies if an existing data set or UNIX file matching *backup_name* should be deleted.

  When *operation=restore*, specifies if the module should overwrite existing data sets with matching name on the target device.

  | **required**: False
  | **type**: bool
  | **default**: False


sms_storage_class
  When *operation=restore*, specifies the storage class to use. The storage class will also be used for temporary data sets created during restore process.

  When *operation=backup*, specifies the storage class to use for temporary data sets created during backup process.

  If neither of *sms_storage_class* or *sms_management_class* are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.

  | **required**: False
  | **type**: str


sms_management_class
  When *operation=restore*, specifies the management class to use. The management class will also be used for temporary data sets created during restore process.

  When *operation=backup*, specifies the management class to use for temporary data sets created during backup process.

  If neither of *sms_storage_class* or *sms_management_class* are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.

  | **required**: False
  | **type**: str


space
  If *operation=backup*, specifies the amount of space to allocate for the backup. Please note that even when backing up to a UNIX file, backup contents will be temporarily held in a data set.

  If *operation=restore*, specifies the amount of space to allocate for data sets temporarily created during the restore process.

  The unit of space used is set using *space_type*.

  When *full_volume=True*, *space* defaults to ``1``, otherwise default is ``25``

  | **required**: False
  | **type**: int


space_type
  The unit of measurement to use when defining data set space.

  Valid units of size are ``K``, ``M``, ``G``, ``CYL``, and ``TRK``.

  When *full_volume=True*, *space_type* defaults to ``G``, otherwise default is ``M``

  | **required**: False
  | **type**: str
  | **choices**: K, M, G, CYL, TRK


hlq
  Specifies the new HLQ to use for the data sets being restored.

  Defaults to running user's username.

  | **required**: False
  | **type**: str


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup data sets.

  The default HLQ is the Ansible user that executes the module and if that is not available, then the value of ``TMPHLQ`` is used.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Backup all data sets matching the pattern USER.** to data set MY.BACKUP.DZP
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       backup_name: MY.BACKUP.DZP

   - name: Backup all data sets matching the patterns USER.** or PRIVATE.TEST.*
       excluding data sets matching the pattern USER.PRIVATE.* to data set MY.BACKUP.DZP
     zos_backup_restore:
       operation: backup
       data_sets:
         include:
           - user.**
           - private.test.*
         exclude: user.private.*
       backup_name: MY.BACKUP.DZP

   - name: Backup all datasets matching the pattern USER.** to UNIX file /tmp/temp_backup.dzp, ignore recoverable errors.
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       backup_name: /tmp/temp_backup.dzp
       recover: yes

   - name: Backup all datasets matching the pattern USER.** to data set MY.BACKUP.DZP,
       allocate 100MB for data sets used in backup process.
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       backup_name: MY.BACKUP.DZP
       space: 100
       space_type: M

   - name:
       Backup all datasets matching the pattern USER.** that are present on the volume MYVOL1 to data set MY.BACKUP.DZP,
       allocate 100MB for data sets used in the backup process.
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       volume: MYVOL1
       backup_name: MY.BACKUP.DZP
       space: 100
       space_type: M

   - name: Backup an entire volume, MYVOL1, to the UNIX file /tmp/temp_backup.dzp,
       allocate 1GB for data sets used in backup process.
     zos_backup_restore:
       operation: backup
       backup_name: /tmp/temp_backup.dzp
       volume: MYVOL1
       full_volume: yes
       space: 1
       space_type: G

   - name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
       Use z/OS username as new HLQ.
     zos_backup_restore:
       operation: restore
       backup_name: /tmp/temp_backup.dzp

   - name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
       Only restore data sets whose last, or only qualifier is TEST.
       Use MYHLQ as the new HLQ for restored data sets.
     zos_backup_restore:
       operation: restore
       data_sets:
         include: "**.TEST"
       backup_name: /tmp/temp_backup.dzp
       hlq: MYHLQ

   - name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
       Only restore data sets whose last, or only qualifier is TEST.
       Use MYHLQ as the new HLQ for restored data sets. Restore data sets to volume MYVOL2.
     zos_backup_restore:
       operation: restore
       data_sets:
         include: "**.TEST"
       volume: MYVOL2
       backup_name: /tmp/temp_backup.dzp
       hlq: MYHLQ

   - name: Restore data sets from backup stored in the data set MY.BACKUP.DZP.
       Use MYHLQ as the new HLQ for restored data sets.
     zos_backup_restore:
       operation: restore
       backup_name: MY.BACKUP.DZP
       hlq: MYHLQ

   - name: Restore volume from backup stored in the data set MY.BACKUP.DZP.
       Restore to volume MYVOL2.
     zos_backup_restore:
       operation: restore
       volume: MYVOL2
       full_volume: yes
       backup_name: MY.BACKUP.DZP
       space: 1
       space_type: G

   - name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
       Specify DB2SMS10 for the SMS storage and management classes to use for the restored
       data sets.
     zos_backup_restore:
       operation: restore
       volume: MYVOL2
       backup_name: /tmp/temp_backup.dzp
       sms_storage_class: DB2SMS10
       sms_management_class: DB2SMS10










