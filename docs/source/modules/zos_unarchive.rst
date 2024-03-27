
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_unarchive.py

.. _zos_unarchive_module:


zos_unarchive -- Unarchive files and data sets in z/OS.
=======================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The ``zos_unarchive`` module unpacks an archive after optionally transferring it to the remote system.
- For supported archive formats, see option ``format``.
- Supported sources are USS (UNIX System Services) or z/OS data sets.
- Mixing MVS data sets with USS files for unarchiving is not supported.
- The archive is sent to the remote as binary, so no encoding is performed.





Parameters
----------


src
  The remote absolute path or data set of the archive to be uncompressed.

  *src* can be a USS file or MVS data set name.

  USS file paths should be absolute paths.

  MVS data sets supported types are ``SEQ``, ``PDS``, ``PDSE``.

  | **required**: True
  | **type**: str


format
  The compression type and corresponding options to use when archiving data.

  | **required**: True
  | **type**: dict


  name
    The compression format to use.

    | **required**: True
    | **type**: str
    | **choices**: bz2, gz, tar, zip, terse, xmit, pax


  format_options
    Options specific to a compression format.

    | **required**: False
    | **type**: dict


    xmit_log_data_set
      Provide the name of a data set to store xmit log output.

      If the data set provided does not exist, the program will create it.

      If the data set provided exists, the data set must have the following attributes: LRECL=255, BLKSIZE=3120, and RECFM=VB

      When providing the *xmit_log_data_set* name, ensure there is adequate space.

      | **required**: False
      | **type**: str


    use_adrdssu
      If set to true, the ``zos_archive`` module will use Data Facility Storage Management Subsystem data set services (DFSMSdss) program ADRDSSU to uncompress data sets from a portable format after using ``xmit`` or ``terse``.

      | **required**: False
      | **type**: bool
      | **default**: False


    dest_volumes
      When *use_adrdssu=True*, specify the volume the data sets will be written to.

      If no volume is specified, storage management rules will be used to determine the volume where the file will be unarchived.

      If the storage administrator has specified a system default unit name and you do not set a volume name for non-system-managed data sets, then the system uses the volumes associated with the default unit name. Check with your storage administrator to determine whether a default unit name has been specified.

      | **required**: False
      | **type**: list
      | **elements**: str




dest
  The remote absolute path or data set where the content should be unarchived to.

  *dest* can be a USS file, directory or MVS data set name.

  If dest has missing parent directories, they will not be created.

  | **required**: False
  | **type**: str


group
  Name of the group that will own the file system objects.

  When left unspecified, it uses the current group of the current user unless you are root, in which case it can preserve the previous ownership.

  This option is only applicable if ``dest`` is USS, otherwise ignored.

  | **required**: False
  | **type**: str


mode
  The permission of the uncompressed files.

  If ``dest`` is USS, this will act as Unix file mode, otherwise ignored.

  It should be noted that modes are octal numbers. The user must either add a leading zero so that Ansible's YAML parser knows it is an octal number (like ``0644`` or ``01777``)or quote it (like ``'644'`` or ``'1777'``) so Ansible receives a string and can do its own conversion from string into number. Giving Ansible a number without following one of these rules will end up with a decimal number which will have unexpected results.

  The mode may also be specified as a symbolic mode (for example, ``u+rwx`` or ``u=rw,g=r,o=r``) or a special string `preserve`.

  *mode=preserve* means that the file will be given the same permissions as the source file.

  | **required**: False
  | **type**: str


owner
  Name of the user that should own the filesystem object, as would be passed to the chown command.

  When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.

  | **required**: False
  | **type**: str


include
  A list of directories, files or data set names to extract from the archive.

  When ``include`` is set, only those files will we be extracted leaving the remaining files in the archive.

  Mutually exclusive with exclude.

  | **required**: False
  | **type**: list
  | **elements**: str


exclude
  List the directory and file or data set names that you would like to exclude from the unarchive action.

  Mutually exclusive with include.

  | **required**: False
  | **type**: list
  | **elements**: str


list
  Will list the contents of the archive without unpacking.

  | **required**: False
  | **type**: bool
  | **default**: False


dest_data_set
  Data set attributes to customize a ``dest`` data set that the archive will be copied into.

  | **required**: False
  | **type**: dict


  name
    Desired name for destination dataset.

    | **required**: False
    | **type**: str


  type
    Organization of the destination

    | **required**: False
    | **type**: str
    | **default**: SEQ
    | **choices**: SEQ, PDS, PDSE


  space_primary
    If the destination *dest* data set does not exist , this sets the primary space allocated for the data set.

    The unit of space used is set using *space_type*.

    | **required**: False
    | **type**: int


  space_secondary
    If the destination *dest* data set does not exist , this sets the secondary space allocated for the data set.

    The unit of space used is set using *space_type*.

    | **required**: False
    | **type**: int


  space_type
    If the destination data set does not exist, this sets the unit of measurement to use when defining primary and secondary space.

    Valid units of size are ``K``, ``M``, ``G``, ``CYL``, and ``TRK``.

    | **required**: False
    | **type**: str
    | **choices**: K, M, G, CYL, TRK


  record_format
    If the destination data set does not exist, this sets the format of the data set. (e.g ``FB``)

    Choices are case-insensitive.

    | **required**: False
    | **type**: str
    | **choices**: FB, VB, FBA, VBA, U


  record_length
    The length of each record in the data set, in bytes.

    For variable data sets, the length must include the 4-byte prefix area.

    Defaults vary depending on format: If FB/FBA 80, if VB/VBA 137, if U 0.

    | **required**: False
    | **type**: int


  block_size
    The block size to use for the data set.

    | **required**: False
    | **type**: int


  directory_blocks
    The number of directory blocks to allocate to the data set.

    | **required**: False
    | **type**: int


  key_offset
    The key offset to use when creating a KSDS data set.

    *key_offset* is required when *type=KSDS*.

    *key_offset* should only be provided when *type=KSDS*

    | **required**: False
    | **type**: int


  key_length
    The key length to use when creating a KSDS data set.

    *key_length* is required when *type=KSDS*.

    *key_length* should only be provided when *type=KSDS*

    | **required**: False
    | **type**: int


  sms_storage_class
    The storage class for an SMS-managed dataset.

    Required for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str


  sms_data_class
    The data class for an SMS-managed dataset.

    Optional for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str


  sms_management_class
    The management class for an SMS-managed dataset.

    Optional for SMS-managed datasets that do not match an SMS-rule.

    Not valid for datasets that are not SMS-managed.

    Note that all non-linear VSAM datasets are SMS-managed.

    | **required**: False
    | **type**: str



tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the environment variable value ``TMPHLQ`` is used.

  | **required**: False
  | **type**: str


force
  If set to true and the remote file or data set dest exists, the dest will be deleted.

  | **required**: False
  | **type**: bool
  | **default**: False


remote_src
  If set to true, ``zos_unarchive`` retrieves the archive from the remote system.

  If set to false, ``zos_unarchive`` searches the local machine (Ansible controller) for the archive.

  | **required**: False
  | **type**: bool
  | **default**: False




Examples
--------

.. code-block:: yaml+jinja

   
   # Simple extract
   - name: Copy local tar file and unpack it on the managed z/OS node.
     zos_unarchive:
       src: "./files/archive_folder_test.tar"
       format:
         name: tar

   # use include
   - name: Unarchive a bzip file selecting only a file to unpack.
     zos_unarchive:
       src: "/tmp/test.bz2"
       format:
         name: bz2
       include:
         - 'foo.txt'

   # Use exclude
   - name: Unarchive a terse data set and excluding data sets from unpacking.
     zos_unarchive:
       src: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse
       exclude:
         - USER.ARCHIVE.TEST1
         - USER.ARCHIVE.TEST2

   # List option
   - name: List content from XMIT
     zos_unarchive:
       src: "USER.ARCHIVE.RESULT.XMIT"
       format:
         name: xmit
         format_options:
           use_adrdssu: True
       list: True




Notes
-----

.. note::
   VSAMs are not supported.

   This module uses `zos_copy <./zos_copy.html>`_ to copy local scripts to the remote machine which uses SFTP (Secure File Transfer Protocol) for the underlying transfer protocol; SCP (secure copy protocol) and Co:Z SFTP are not supported. In the case of Co:z SFTP, you can exempt the Ansible user id on z/OS from using Co:Z thus falling back to using standard SFTP. If the module detects SCP, it will temporarily use SFTP for transfers, if not available, the module will fail.



See Also
--------

.. seealso::

   - :ref:`zos_archive_module`




Return Values
-------------


src
  File path or data set name unpacked.

  | **returned**: always
  | **type**: str

dest_path
  Destination path where archive was unpacked.

  | **returned**: always
  | **type**: str

targets
  List of files or data sets in the archive.

  | **returned**: success
  | **type**: list
  | **elements**: str

missing
  Any files or data sets not found during extraction.

  | **returned**: success
  | **type**: str

