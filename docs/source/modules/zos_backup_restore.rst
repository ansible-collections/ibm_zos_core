
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
    When \ :emphasis:`operation=backup`\ , specifies a list of data sets or data set patterns to include in the backup.

    When \ :emphasis:`operation=restore`\ , specifies a list of data sets or data set patterns to include when restoring from a backup.

    The single asterisk, \ :literal:`\*`\ , is used in place of exactly one qualifier. In addition, it can be used to indicate to DFSMSdss that only part of a qualifier has been specified.

    When used with other qualifiers, the double asterisk, \ :literal:`\*\*`\ , indicates either the nonexistence of leading, trailing, or middle qualifiers, or the fact that they play no role in the selection process.

    Two asterisks are the maximum permissible in a qualifier. If there are two asterisks in a qualifier, they must be the first and last characters.

    A question mark \ :literal:`?`\  or percent sign \ :literal:`%`\  matches a single character.

    | **required**: False
    | **type**: raw


  exclude
    When \ :emphasis:`operation=backup`\ , specifies a list of data sets or data set patterns to exclude from the backup.

    When \ :emphasis:`operation=restore`\ , specifies a list of data sets or data set patterns to exclude when restoring from a backup.

    The single asterisk, \ :literal:`\*`\ , is used in place of exactly one qualifier. In addition, it can be used to indicate that only part of a qualifier has been specified."

    When used with other qualifiers, the double asterisk, \ :literal:`\*\*`\ , indicates either the nonexistence of leading, trailing, or middle qualifiers, or the fact that they play no role in the selection process.

    Two asterisks are the maximum permissible in a qualifier. If there are two asterisks in a qualifier, they must be the first and last characters.

    A question mark \ :literal:`?`\  or percent sign \ :literal:`%`\  matches a single character.

    | **required**: False
    | **type**: raw



volume
  This applies to both data set restores and volume restores.

  When \ :emphasis:`operation=backup`\  and \ :emphasis:`data\_sets`\  are provided, specifies the volume that contains the data sets to backup.

  When \ :emphasis:`operation=restore`\ , specifies the volume the backup should be restored to.

  \ :emphasis:`volume`\  is required when restoring a full volume backup.

  | **required**: False
  | **type**: str


full_volume
  When \ :emphasis:`operation=backup`\  and \ :emphasis:`full\_volume=True`\ , specifies that the entire volume provided to \ :emphasis:`volume`\  should be backed up.

  When \ :emphasis:`operation=restore`\  and \ :emphasis:`full\_volume=True`\ , specifies that the volume should be restored (default is dataset).

  \ :emphasis:`volume`\  must be provided when \ :emphasis:`full\_volume=True`\ .

  | **required**: False
  | **type**: bool
  | **default**: False


temp_volume
  Specifies a particular volume on which the temporary data sets should be created during the backup and restore process.

  When \ :emphasis:`operation=backup`\  and \ :emphasis:`backup\_name`\  is a data set, specifies the volume the backup should be placed in.

  | **required**: False
  | **type**: str


backup_name
  When \ :emphasis:`operation=backup`\ , the destination data set or UNIX file to hold the backup.

  When \ :emphasis:`operation=restore`\ , the destination data set or UNIX file backup to restore.

  There are no enforced conventions for backup names. However, using a common extension like \ :literal:`.dzp`\  for UNIX files and \ :literal:`.DZP`\  for data sets will improve readability.

  | **required**: True
  | **type**: str


recover
  Specifies if potentially recoverable errors should be ignored.

  | **required**: False
  | **type**: bool
  | **default**: False


overwrite
  When \ :emphasis:`operation=backup`\ , specifies if an existing data set or UNIX file matching \ :emphasis:`backup\_name`\  should be deleted.

  When \ :emphasis:`operation=restore`\ , specifies if the module should overwrite existing data sets with matching name on the target device.

  | **required**: False
  | **type**: bool
  | **default**: False


sms_storage_class
  When \ :emphasis:`operation=restore`\ , specifies the storage class to use. The storage class will also be used for temporary data sets created during restore process.

  When \ :emphasis:`operation=backup`\ , specifies the storage class to use for temporary data sets created during backup process.

  If neither of \ :emphasis:`sms\_storage\_class`\  or \ :emphasis:`sms\_management\_class`\  are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.

  | **required**: False
  | **type**: str


sms_management_class
  When \ :emphasis:`operation=restore`\ , specifies the management class to use. The management class will also be used for temporary data sets created during restore process.

  When \ :emphasis:`operation=backup`\ , specifies the management class to use for temporary data sets created during backup process.

  If neither of \ :emphasis:`sms\_storage\_class`\  or \ :emphasis:`sms\_management\_class`\  are specified, the z/OS system's Automatic Class Selection (ACS) routines will be used.

  | **required**: False
  | **type**: str


space
  If \ :emphasis:`operation=backup`\ , specifies the amount of space to allocate for the backup. Please note that even when backing up to a UNIX file, backup contents will be temporarily held in a data set.

  If \ :emphasis:`operation=restore`\ , specifies the amount of space to allocate for data sets temporarily created during the restore process.

  The unit of space used is set using \ :emphasis:`space\_type`\ .

  When \ :emphasis:`full\_volume=True`\ , \ :emphasis:`space`\  defaults to \ :literal:`1`\ , otherwise default is \ :literal:`25`\ 

  | **required**: False
  | **type**: int


space_type
  The unit of measurement to use when defining data set space.

  Valid units of size are \ :literal:`k`\ , \ :literal:`m`\ , \ :literal:`g`\ , \ :literal:`cyl`\ , and \ :literal:`trk`\ .

  When \ :emphasis:`full\_volume=True`\ , \ :emphasis:`space\_type`\  defaults to \ :literal:`g`\ , otherwise default is \ :literal:`m`\ 

  | **required**: False
  | **type**: str
  | **choices**: k, m, g, cyl, trk


hlq
  Specifies the new HLQ to use for the data sets being restored.

  Defaults to running user's username.

  | **required**: False
  | **type**: str


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup data sets.

  The default HLQ is the Ansible user that executes the module and if that is not available, then the value of \ :literal:`TMPHLQ`\  is used.

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
       recover: true

   - name: Backup all datasets matching the pattern USER.** to data set MY.BACKUP.DZP,
       allocate 100MB for data sets used in backup process.
     zos_backup_restore:
       operation: backup
       data_sets:
         include: user.**
       backup_name: MY.BACKUP.DZP
       space: 100
       space_type: m

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
       space_type: m

   - name: Backup an entire volume, MYVOL1, to the UNIX file /tmp/temp_backup.dzp,
       allocate 1GB for data sets used in backup process.
     zos_backup_restore:
       operation: backup
       backup_name: /tmp/temp_backup.dzp
       volume: MYVOL1
       full_volume: true
       space: 1
       space_type: g

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
       full_volume: true
       backup_name: MY.BACKUP.DZP
       space: 1
       space_type: g

   - name: Restore data sets from backup stored in the UNIX file /tmp/temp_backup.dzp.
       Specify DB2SMS10 for the SMS storage and management classes to use for the restored
       data sets.
     zos_backup_restore:
       operation: restore
       volume: MYVOL2
       backup_name: /tmp/temp_backup.dzp
       sms_storage_class: DB2SMS10
       sms_management_class: DB2SMS10










