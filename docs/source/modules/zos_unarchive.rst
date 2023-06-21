
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_unarchive.py

.. _zos_unarchive_module:


zos_unarchive -- Unarchive a dataset or file in z/OS.
=====================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The ``zos_unarchive`` module unpacks an archive after optionally sending it to the remote.






Parameters
----------


path
  Local or remote absolute path or data set name of the archive to be unpacked on the remote.

  | **required**: True
  | **type**: str


format
  The type of compression to use.

  | **required**: True
  | **type**: dict


  name
    The name of the format to use.

    | **required**: True
    | **type**: str
    | **choices**: bz2, gz, tar, zip, terse, xmit, pax


  format_options
    Options specific to each format.

    | **required**: False
    | **type**: dict


    xmit_log_dataset
      Provide a name of data set to store xmit log output.

      | **required**: False
      | **type**: str


    use_adrdssu
      If set to true, after unpacking a data set in ``xmit`` or c(terse) format it will perform a single DFSMSdss ADRDSSU RESTORE step.

      | **required**: False
      | **type**: bool


    dest_volumes
      When using ADRDSSU select on which volume the datasets will be placed first.

      | **required**: False
      | **type**: list
      | **elements**: str




dest
  Remote absolute path where the archive should be unpacked.

  The given path must exist. Base directory is not created by this module.

  | **required**: False
  | **type**: str


group
  Name of the group that should own the filesystem object, as would be fed to chown.

  When left unspecified, it uses the current group of the current user unless you are root, in which case it can preserve the previous ownership.

  | **required**: False
  | **type**: str


mode
  The permissions the resulting filesystem object should have.

  | **required**: False
  | **type**: str


owner
  Name of the user that should own the filesystem object, as would be fed to chown.

  When left unspecified, it uses the current user unless you are root, in which case it can preserve the previous ownership.

  | **required**: False
  | **type**: str


include
  List of directory and file or data set names that you would like to extract from the archive.

  If include is not empty, only files listed here will be extracted.

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
  Set to true to only list the archive content without unpacking.

  | **required**: False
  | **type**: bool


dest_data_set
  Data set attributes to customize a ``dest`` data set to be copied into.

  | **required**: False
  | **type**: dict


  name
    Desired name for destination dataset.

    | **required**: False
    | **type**: str


  type
    Organization of the destination

    | **required**: True
    | **type**: str
    | **choices**: KSDS, ESDS, RRDS, LDS, SEQ, PDS, PDSE, MEMBER, BASIC


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
  High Level Qualifier used for temporary datasets created during the module execution.

  | **required**: False
  | **type**: str


force
  Replace existing files or data sets if files or data sets to unarchive have conflicting paths.

  | **required**: False
  | **type**: bool


remote_src
  Set to true to indicate the archive file is already on the remote system and not local to the Ansible controller.

  | **required**: False
  | **type**: bool


is_binary
  Set to true if archive file is to be treated as binary when sending to remote.

  | **required**: False
  | **type**: bool




Examples
--------

.. code-block:: yaml+jinja

   
   # Simple extract
   - name: Send tar file and unpack in managed node
     zos_unarchive:
       path: "./files/archive_folder_test.tar"
       format:
         name: tar

   # use include
   - name: List content from TRS
     zos_unarchive:
       path: "/tmp/test.bz2"
       format:
         name: bz2
       include:
         - 'foo.txt'

   # Use exclude
   - name: Unarchive from terse data set excluding some from unpacking
       zos_unarchive:
         path: "USER.ARCHIVE.RESULT.TRS"
         format:
           name: terse
         exclude:
           - USER.ARCHIVE.TEST1
           - USER.ARCHIVE.TEST2

   # List option
   - name: List content from XMIT
       zos_unarchive:
         path: "OMVSADM.ARCHIVE.RESULT.XMIT"
         format:
           name: xmit
           format_options:
             use_adrdssu: True
         list: True










Return Values
-------------


path
  File path or data set name unarchived.

  | **returned**: always
  | **type**: str

dest_path
  Destination path where archive was extracted.

  | **returned**: always
  | **type**: str

targets
  List of files or data sets in the archive.

  | **returned**: success
  | **type**: str

missing
  Any files or data sets not found during extraction.

  | **returned**: success
  | **type**: str

