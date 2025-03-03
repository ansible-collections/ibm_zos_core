
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_stat.py

.. _zos_stat_module:


zos_stat -- Retrieve facts from z/OS
====================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The `zos_stat <./zos_stat.html>`_ module retrieves facts from resources stored in a z/OS system.
- Resources that can be queried are files, data sets and aggregates.





Parameters
----------


name
  Name of a data set or aggregate, or a file path, to query.

  Data sets can be sequential, partitioned (PDS), partitioned extended (PDSE), VSAMs, generation data groups (GDG) or generation data sets (GDS).

  | **required**: True
  | **type**: str


volume
  Name of the volume where the data set will be searched on.

  Required when getting facts from a data set. Ignored otherwise.

  | **required**: False
  | **type**: str


type
  Type of resource to query.

  | **required**: False
  | **type**: str
  | **default**: data_set
  | **choices**: data_set, file, aggregate


sms_managed
  Whether the data set is managed by the Storage Management Subsystem.

  It will cause the module to retrieve additional information, may take longer to query all attributes of a data set.

  If the data set is a PDSE and the Ansible user has RACF READ authority on it, retrieving SMS information will update the last referenced date of the data set.

  If the system finds the data set is not actually managed by SMS, the rest of the attributes will still be queried and this will be noted in the output from the task.

  | **required**: False
  | **type**: bool
  | **default**: True


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary data sets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the environment variable value ``TMPHLQ`` is used.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Get the attributes of a sequential data set on volume '000000'.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set
       volume: "000000"

   - name: Get the attributes of a PDSE managed by SMS.
     zos_stat:
       name: USER.PDSE.DATA
       type: data_set
       volume: "000000"
       sms_managed: true

   - name: Get the attributes of a sequential data set with a non-default temporary HLQ.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set
       volume: "000000"
       tmp_hlq: "RESTRICT"

   - name: Get the attributes of a generation data group.
     zos_stat:
       name: "USER.GDG.DATA"
       type: data_set
       volume: "000000"

   - name: Get the attributes of a generation data set.
     zos_stat:
       name: "USER.GDG.DATA(-1)"
       type: data_set
       volume: "000000"




Notes
-----

.. note::
   When querying data sets, the module will create a temporary data set that requires around 4 kilobytes of available space on the remote host. This data set will be removed before the module finishes execution.

   Sometimes, the system could be unable to properly determine the organization or record format of the data set or the space units used to represent its allocation. When this happens, the values for these fields will be null.

   When querying a partitioned data set (PDS), if the Ansible user has RACF READ authority on it, the last referenced date will be updated by the query operation.



See Also
--------

.. seealso::

   - :ref:`ansible.builtin.stat_module`
   - :ref:`zos_find_module`




Return Values
-------------


stat
  Dictionary containing information about the resource.

  | **returned**: success
  | **type**: dict

  name
    Name of the resource queried.

    For Generation Data Sets (GDSs), this will be the absolute name.

    | **returned**: success
    | **type**: str
    | **sample**: USER.SEQ.DATA.SET

  resource_type
    One of 'data_set', 'file' or 'aggregate'.

    | **returned**: success
    | **type**: str
    | **sample**: data_set

  attributes
    Dictionary containing all the stat data.

    | **returned**: success
    | **type**: dict

    dsorg
      Data set organization.

      | **returned**: success
      | **type**: str
      | **sample**: PS

    type
      Type of the data set.

      | **returned**: success
      | **type**: str
      | **sample**: LIBRARY

    record_format
      Record format of a data set.

      | **returned**: success
      | **type**: str
      | **sample**: VB

    record_length
      Record length of a data set.

      | **returned**: success
      | **type**: int
      | **sample**: 80

    block_size
      Block size of a data set.

      | **returned**: success
      | **type**: int
      | **sample**: 27920

    has_extended_attrs
      Whether a data set has extended attributes set.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    extended_attrs_bits
      Current values of the EATTR bits for a data set.

      | **returned**: success
      | **type**: str
      | **sample**: OPT

    creation_date
      Date a data set was created.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-01-27

    creation_time
      Time at which a data set was created.

      Only available when a data set has extended attributes.

      | **returned**: success
      | **type**: str
      | **sample**: 11:25:52

    expiration_date
      Expiration date of a data set.

      | **returned**: success
      | **type**: str
      | **sample**: 2030-12-31

    last_reference
      Date where the data set was last referenced.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-01-28

    updated_since_backup
      Whether the data set has been updated since its last backup.

      | **returned**: success
      | **type**: bool

    jcl_attrs
      Dictionary containing the names of the JCL job and step that created a data set.

      Only available for data sets with extended attributes.

      | **returned**: success
      | **type**: dict

      creation_job
        JCL job that created the data set.

        | **returned**: success
        | **type**: str

      creation_step
        JCL job step that created the data set.

        | **returned**: success
        | **type**: str


    volser
      Name of the volume containing the data set.

      | **returned**: success
      | **type**: str
      | **sample**: 000000

    num_volumes
      Number of volumes where the data set resides.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    volumes
      Names of the volumes where the data set resides.

      | **returned**: success
      | **type**: list
      | **elements**: str
      | **sample**:

        .. code-block:: json

            [
                "000000",
                "SCR03"
            ]

    device_type
      Generic device type where the data set resides.

      | **returned**: success
      | **type**: str
      | **sample**: 3390

    space_units
      Units used to describe sizes for the data set.

      | **returned**: success
      | **type**: str
      | **sample**: TRACK

    primary_space
      Primary allocation.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 93

    secondary_space
      Secondary allocation.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 56

    allocation_available
      Total allocation of the data set.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 93

    allocation_used
      Total allocation used by the data set.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int

    extents_allocated
      Number of extents allocated for the data set.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    extents_used
      Number of extents used by the data set.

      For PDSEs, this value will be null. See instead pages_used and perc_pages_used.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    blocks_per_track
      Blocks per track for the unit contained in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 2

    tracks_per_cylinder
      Tracks per cylinder for the unit contained in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 15

    sms_data_class
      The SMS data class name.

      Only returned when the data set is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: STANDARD

    sms_mgmt_class
      The SMS management class name.

      Only returned when the data set is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: VSAM

    sms_storage_class
      The SMS storage class name.

      Only returned when the data set is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: FAST

    encrypted
      Whether the data set is encrypted.

      | **returned**: success
      | **type**: bool

    password
      Whether the data set has a password set to read/write.

      Value can be either one of 'NONE', 'READ' or 'WRITE'.

      For VSAMs, the value can also be 'SUPP', when the module is unable to query its security attributes.

      | **returned**: success
      | **type**: str
      | **sample**: NONE

    racf
      Whether there is RACF protection set on the data set.

      Value can be either one of 'NONE', 'GENERIC' or 'DISCRETE' for non-VSAM data sets.

      For VSAMs, the value can be either 'YES' or 'NO'.

      | **returned**: success
      | **type**: str
      | **sample**: NONE

    key_label
      The encryption key label for an encrypted data set.

      | **returned**: success
      | **type**: str
      | **sample**: KEYDSN

    dir_blocks_allocated
      Number of directory blocks allocated for a PDS.

      For PDSEs, this value will be null. See instead pages_used and perc_pages_used.

      | **returned**: success
      | **type**: int
      | **sample**: 5

    dir_blocks_used
      Number of directory blocks used by a PDS.

      For PDSEs, this value will be null. See instead pages_used and perc_pages_used.

      | **returned**: success
      | **type**: int
      | **sample**: 2

    members
      Number of members inside a partitioned data set.

      | **returned**: success
      | **type**: int
      | **sample**: 3

    pages_allocated
      Number of pages allocated to a PDSE.

      | **returned**: success
      | **type**: int
      | **sample**: 1116

    pages_used
      Number of pages used by a PDSE. The pages are 4K in size.

      | **returned**: success
      | **type**: int
      | **sample**: 5

    perc_pages_used
      Percentage of pages used by a PDSE.

      Gets rounded down to the nearest integer value.

      | **returned**: success
      | **type**: int
      | **sample**: 10

    pdse_version
      PDSE data set version.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    max_pdse_generation
      Maximum number of generations of a member that can be maintained in a PDSE.

      | **returned**: success
      | **type**: int

    seq_type
      Type of sequential data set (when it applies).

      Value can be either one of 'BASIC', 'LARGE' or 'EXTENDED'.

      | **returned**: success
      | **type**: str
      | **sample**: BASIC

    data
      Dictionary containing attributes for the DATA part of a VSAM.

      For the rest of the attributes of this data set, query it directly with this module.

      | **returned**: success
      | **type**: dict

      key_length
        Key length for data records, in bytes.

        | **returned**: success
        | **type**: int

      key_offset
        Key offset for data records.

        | **returned**: success
        | **type**: int

      max_record_length
        Maximum length of data records, in bytes.

        | **returned**: success
        | **type**: int

      avg_record_length
        Average length of data records, in bytes.

        | **returned**: success
        | **type**: int

      bufspace
        Minimum buffer space in bytes to be provided by a processing program.

        | **returned**: success
        | **type**: int

      total_records
        Total number of records.

        | **returned**: success
        | **type**: int

      spanned
        Whether the data set allows records to be spanned across control intervals.

        | **returned**: success
        | **type**: bool


    index
      Dictionary containing attributes for the INDEX part of a VSAM.

      For the rest of the attributes of this data set, query it directly with this module.

      | **returned**: success
      | **type**: dict

      key_length
        Key length for index records, in bytes.

        | **returned**: success
        | **type**: int

      key_offset
        Key offset for index records.

        | **returned**: success
        | **type**: int

      max_record_length
        Maximum length of index records, in bytes.

        | **returned**: success
        | **type**: int

      avg_record_length
        Average length of index records, in bytes.

        | **returned**: success
        | **type**: int

      bufspace
        Minimum buffer space in bytes to be provided by a processing program.

        | **returned**: success
        | **type**: int

      total_records
        Total number of records.

        | **returned**: success
        | **type**: int


    limit
      Maximum amount of active generations allowed in a GDG.

      | **returned**: success
      | **type**: int

    scratch
      Whether the GDG has the SCRATCH attribute set.

      | **returned**: success
      | **type**: bool

    empty
      Whether the GDG has the EMPTY attribute set.

      | **returned**: success
      | **type**: bool

    order
      Allocation order of new Generation Data Sets for a GDG.

      Value can be either 'LIFO' or 'FIFO'.

      | **returned**: success
      | **type**: str

    purge
      Whether the GDG has the PURGE attribute set.

      | **returned**: success
      | **type**: bool

    extended
      Whether the GDG has the EXTENDED attribute set.

      | **returned**: success
      | **type**: bool

    active_gens
      List of the names of the currently active generations of a GDG.

      | **returned**: success
      | **type**: list
      | **elements**: str



