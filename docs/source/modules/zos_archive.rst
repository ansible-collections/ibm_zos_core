
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_archive.py

.. _zos_archive_module:


zos_archive -- Archive files and data sets on z/OS.
===================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create or extend an archive on a remote z/OS system.
- Sources for archiving must be on the remote z/OS system.
- Supported sources are USS (UNIX System Services) or z/OS data sets.
- The archive remains on the remote z/OS system.
- For supported archive formats, see option ``format``.





Parameters
----------


src
  List of names or globs of UNIX System Services (USS) files, PS (sequential data sets), PDS, PDSE to compress or archive.

  USS file paths should be absolute paths.

  MVS data sets supported types are: ``SEQ``, ``PDS``, ``PDSE``.

  VSAMs are not supported.

  | **required**: True
  | **type**: list
  | **elements**: str


format
  The compression type and corresponding options to use when archiving data.

  | **required**: False
  | **type**: dict


  name
    The compression format to use.

    | **required**: False
    | **type**: str
    | **default**: gz
    | **choices**: bz2, gz, tar, zip, terse, xmit, pax


  format_options
    Options specific to a compression format.

    | **required**: False
    | **type**: dict


    terse_pack
      Compression option for use with the terse format, *name=terse*.

      Pack will compress records in a data set so that the output results in lossless data compression.

      Spack will compress records in a data set so the output results in complex data compression.

      Spack will produce smaller output and take approximately 3 times longer than pack compression.

      | **required**: False
      | **type**: str
      | **choices**: PACK, SPACK


    xmit_log_data_set
      Provide the name of a data set to store xmit log output.

      If the data set provided does not exist, the program will create it.

      If the data set provided exists, the data set must have the following attributes: LRECL=255, BLKSIZE=3120, and RECFM=VB

      When providing the *xmit_log_data_set* name, ensure there is adequate space.

      | **required**: False
      | **type**: str


    use_adrdssu
      If set to true, the ``zos_archive`` module will use Data Facility Storage Management Subsystem data set services (DFSMSdss) program ADRDSSU to compress data sets into a portable format before using ``xmit`` or ``terse``.

      | **required**: False
      | **type**: bool
      | **default**: False




dest
  The remote absolute path or data set where the archive should be created.

  *dest* can be a USS file or MVS data set name.

  If *dest* has missing parent directories, they will be created.

  If *dest* is a nonexistent USS file, it will be created.

  If *dest* is an existing file or data set and *force=true*, the existing *dest* will be deleted and recreated with attributes defined in the *dest_data_set* option or computed by the module.

  If *dest* is an existing file or data set and *force=false* or not specified, the module exits with a note to the user.

  Destination data set attributes can be set using *dest_data_set*.

  Destination data set space will be calculated based on space of source data sets provided and/or found by expanding the pattern name. Calculating space can impact module performance. Specifying space attributes in the *dest_data_set* option will improve performance.

  | **required**: True
  | **type**: str


exclude
  Remote absolute path, glob, or list of paths, globs or data set name patterns for the file, files or data sets to exclude from src list and glob expansion.

  Patterns (wildcards) can contain one of the following, `?`, `*`.

  * matches everything.

  ? matches any single character.

  | **required**: False
  | **type**: list
  | **elements**: str


group
  Name of the group that will own the archive file.

  When left unspecified, it uses the current group of the current use unless you are root, in which case it can preserve the previous ownership.

  This option is only applicable if ``dest`` is USS, otherwise ignored.

  | **required**: False
  | **type**: str


mode
  The permission of the destination archive file.

  If ``dest`` is USS, this will act as Unix file mode, otherwise ignored.

  It should be noted that modes are octal numbers. The user must either add a leading zero so that Ansible's YAML parser knows it is an octal number (like ``0644`` or ``01777``)or quote it (like ``'644'`` or ``'1777'``) so Ansible receives a string and can do its own conversion from string into number. Giving Ansible a number without following one of these rules will end up with a decimal number which will have unexpected results.

  The mode may also be specified as a symbolic mode (for example, 'u+rwx' or 'u=rw,g=r,o=r') or a special string 'preserve'.

  *mode=preserve* means that the file will be given the same permissions as the src file.

  | **required**: False
  | **type**: str


owner
  Name of the user that should own the archive file, as would be passed to the chown command.

  When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.

  This option is only applicable if ``dest`` is USS, otherwise ignored.

  | **required**: False
  | **type**: str


remove
  Remove any added source files , trees or data sets after module `zos_archive <./zos_archive.html>`_ adds them to the archive. Source files, trees and data sets are identified with option *src*.

  | **required**: False
  | **type**: bool
  | **default**: False


dest_data_set
  Data set attributes to customize a ``dest`` data set to be archived into.

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
    | **choices**: SEQ


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
  If set to ``true`` and the remote file or data set ``dest`` will be deleted. Otherwise it will be created with the ``dest_data_set`` attributes or default values if ``dest_data_set`` is not specified.

  If set to ``false``, the file or data set will only be copied if the destination does not exist.

  If set to ``false`` and destination exists, the module exits with a note to the user.

  | **required**: False
  | **type**: bool
  | **default**: False




Examples
--------

.. code-block:: yaml+jinja

   
   # Simple archive
   - name: Archive file into a tar
     zos_archive:
       src: /tmp/archive/foo.txt
       dest: /tmp/archive/foo_archive_test.tar
       format:
         name: tar

   # Archive multiple files
   - name: Compress list of files into a zip
     zos_archive:
       src:
         - /tmp/archive/foo.txt
         - /tmp/archive/bar.txt
       dest: /tmp/archive/foo_bar_archive_test.zip
       format:
       name: zip

   # Archive one data set into terse
   - name: Compress data set into a terse
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse

   # Use terse with different options
   - name: Compress data set into a terse, specify pack algorithm and use adrdssu
     zos_archive:
       src: "USER.ARCHIVE.TEST"
       dest: "USER.ARCHIVE.RESULT.TRS"
       format:
         name: terse
         format_options:
           terse_pack: "SPACK"
           use_adrdssu: True

   # Use a pattern to store
   - name: Compress data set pattern using xmit
     zos_archive:
       src: "USER.ARCHIVE.*"
       exclude_sources: "USER.ARCHIVE.EXCLUDE.*"
       dest: "USER.ARCHIVE.RESULT.XMIT"
       format:
         name: xmit




Notes
-----

.. note::
   This module does not perform a send or transmit operation to a remote node. If you want to transport the archive you can use zos_fetch to retrieve to the controller and then zos_copy or zos_unarchive for copying to a remote or send to the remote and then unpack the archive respectively.

   When packing and using ``use_adrdssu`` flag the module will take up to two times the space indicated in ``dest_data_set``.

   tar, zip, bz2 and pax are archived using python ``tarfile`` library which uses the latest version available for each format, for compatibility when opening from system make sure to use the latest available version for the intended format.



See Also
--------

.. seealso::

   - :ref:`zos_fetch_module`
   - :ref:`zos_unarchive_module`




Return Values
-------------


state
  The state of the input ``src``.

  ``absent`` when the source files or data sets were removed.

  ``present`` when the source files or data sets were not removed.

  ``incomplete`` when ``remove`` was true and the source files or data sets were not removed.

  | **returned**: always
  | **type**: str

dest_state
  The state of the *dest* file or data set.

  ``absent`` when the file does not exist.

  ``archive`` when the file is an archive.

  ``compress`` when the file is compressed, but not an archive.

  ``incomplete`` when the file is an archive, but some files under *src* were not found.

  | **returned**: success
  | **type**: str

missing
  Any files or data sets that were missing from the source.

  | **returned**: success
  | **type**: list

archived
  Any files or data sets that were compressed or added to the archive.

  | **returned**: success
  | **type**: list

arcroot
  If ``src`` is a list of USS files, this returns the top most parent folder of the list of files, otherwise is empty.

  | **returned**: always
  | **type**: str

expanded_sources
  The list of matching paths from the src option.

  | **returned**: always
  | **type**: list

expanded_exclude_sources
  The list of matching exclude paths from the exclude option.

  | **returned**: always
  | **type**: list

