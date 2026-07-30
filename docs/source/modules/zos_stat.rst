
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_stat.py

.. _ibm.ibm_zos_core.zos_stat_module:


zos_stat -- Retrieve facts from MVS datasets, USS files, aggregates and generation data groups
===============================================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The `zos_stat <./zos_stat.html>`_ module retrieves facts from resources stored in a z/OS system.
- Resources that can be queried are UNIX System Services files, datasets, generation data groups, and aggregates.





Parameters
----------


name
  Name of a dataset, generation data group (GDG), aggregate, or UNIX System Services file path to query.

  Datasets can be sequential, partitioned (PDS), partitioned extended (PDSE), VSAMs, or generation datasets (GDS).

  This option doesn't accept the use of wildcards (\? and \*).

  | **required**: True
  | **type**: str


volumes
  Name(s) of the volume(s) where the dataset is searched on.

  If omitted, the module looks up the master catalog to find all volumes where a dataset is allocated.

  When used, if the dataset is not found in at least one volume from the list, the module fails with a "dataset not found" message.

  | **required**: False
  | **type**: list
  | **elements**: str


type
  Type of resource to query.

  | **required**: False
  | **type**: str
  | **default**: data_set
  | **choices**: data_set, file, aggregate, gdg


sms_managed
  Whether the dataset is managed by the Storage Management Subsystem.

  It causes the module to retrieve additional information, may take longer to query all attributes of a dataset.

  If the dataset is a PDSE and the Ansible user has RACF READ authority on it, retrieving SMS information updates the last referenced date of the dataset.

  If the system finds the dataset is not actually managed by SMS, the rest of the attributes are still queried and this is noted in the output from the task.

  | **required**: False
  | **type**: bool
  | **default**: False


recall
  Whether to recall a migrated dataset to fully query its attributes.

  If set to ``false``, the module returns a limited amount of information for a migrated dataset.

  Recalling a dataset makes the module take longer to run.

  Ignored when the dataset is not found to be migrated.

  The dataset is not migrated again afterwards.

  The dataset is not recalled when the module runs in check mode.

  | **required**: False
  | **type**: bool
  | **default**: False


tmp_hlq
  Override the default high-level qualifier (HLQ) for temporary datasets.

  The default HLQ is the Ansible user used to run the module. If that is not available, the value of the ``TMPHLQ`` environment variable is used.

  | **required**: False
  | **type**: str


follow
  Whether to follow symlinks when querying files.

  | **required**: False
  | **type**: bool
  | **default**: False


get_mime
  Whether to get information about the nature of a file, such as the charset and type of media it represents.

  | **required**: False
  | **type**: bool
  | **default**: True


get_checksum
  Whether to compute a file's checksum and return it. Otherwise ignored.

  | **required**: False
  | **type**: bool
  | **default**: True


checksum_algorithm
  Algorithm used to compute a file's checksum.

  Returns an error if the managed node is unable to use the specified algorithm.

  | **required**: False
  | **type**: str
  | **default**: sha1
  | **choices**: md5, sha1, sha224, sha256, sha384, sha512




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

   
   - name: Get the attributes of a sequential dataset.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set

   - name: Get the attributes of a sequential dataset on volume '000000'.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set
       volume: "000000"

   - name: Get the attributes of a sequential dataset allocated on multiple volumes.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set
       volumes:
         - "000000"
         - "222222"

   - name: Get the attributes of a PDSE managed by SMS.
     zos_stat:
       name: USER.PDSE.DATA
       type: data_set
       sms_managed: true

   - name: Get the attributes of a sequential dataset with a non-default temporary HLQ.
     zos_stat:
       name: USER.SEQ.DATA
       type: data_set
       tmp_hlq: "RESTRICT"

   - name: Get the attributes of a generation data group.
     zos_stat:
       name: "USER.GDG.DATA"
       type: gdg

   - name: Get the attributes of a generation dataset.
     zos_stat:
       name: "USER.GDG.DATA(-1)"
       type: data_set

   - name: Get the attributes of an aggregate.
     zos_stat:
       name: "HLQ.USER.ZFS.DATA"
       type: aggregate

   - name: Get the attributes of a file inside UNIX System Services.
     zos_stat:
       name: "/u/user/file.txt"
       type: file
       get_checksum: true




Notes
-----

.. note::
   When querying datasets, the module creates two temporary datasets. One requires around 4 kilobytes of available space on the managed node. The second one, around 1 kilobyte of available space. Both datasets are removed before the module finishes execution.

   Sometimes the system cannot determine the organization, record format, or space allocation units for the dataset. When this happens, these fields are reported as not available.

   When querying a partitioned dataset (PDS), if the Ansible user has RACF READ authority on it, the query operation updates the last referenced date.

   If you need to filter the output from the module by resource type, you can use the zos_stat_by_type filter inside of a playbook.



See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zos_core.zos_find_module`
   - :ref:`ibm.ibm_zos_core.zos_gather_facts_module`
   - :ref:`ibm.ibm_zos_core.zos_stat_by_type_module`




Return Values
-------------


stat
  Dictionary containing information about the resource.

  Attributes that do not apply to the current resource are still present in the dictionary as empty values, so that automation relying on certain fields remains functional.
  | **returned**: success
  | **type**: dict

  name
    Name of the resource queried.

    For Generation Data Sets (GDSs), this is the absolute name.

    | **returned**: success
    | **type**: str
    | **sample**: USER.SEQ.DATA.SET

  resource_type
    One of 'data_set', 'gdg', 'file' or 'aggregate'.

    | **returned**: success
    | **type**: str
    | **sample**: data_set

  exists
    Whether name was found on the managed node.

    | **returned**: success
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  isfile
    Whether name is a UNIX System Services file.

    | **returned**: success
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  isdataset
    Whether name is a dataset.

    | **returned**: success
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  isaggregate
    Whether name is an aggregate.

    | **returned**: success
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  isgdg
    Whether name is a Generation Data Group.

    | **returned**: success
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  attributes
    Dictionary containing all the stat data.

    | **returned**: success
    | **type**: dict

    dsorg
      Data set organization.

      | **returned**: success
      | **type**: str
      | **sample**: ps

    type
      Type of the dataset.

      | **returned**: success
      | **type**: str
      | **sample**: library

    record_format
      Record format of a dataset.

      | **returned**: success
      | **type**: str
      | **sample**: vb

    record_length
      Record length of a dataset.

      | **returned**: success
      | **type**: int
      | **sample**: 80

    block_size
      Block size of a dataset.

      | **returned**: success
      | **type**: int
      | **sample**: 27920

    has_extended_attrs
      Whether a dataset has extended attributes set.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    extended_attrs_bits
      Current values of the EATTR bits for a dataset.

      For files, it shows the current values of the extended attributes bits as a group of 4 characters.

      | **returned**: success
      | **type**: str
      | **sample**: opt

    creation_date
      Date a dataset was created.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-01-27

    creation_time
      Time at which a dataset was created.

      Only available when a dataset has extended attributes.

      | **returned**: success
      | **type**: str
      | **sample**: 11:25:52

    expiration_date
      Expiration date of a dataset.

      | **returned**: success
      | **type**: str
      | **sample**: 2030-12-31

    last_reference
      Date where the dataset was last referenced.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-01-28

    updated_since_backup
      Whether the dataset has been updated since its last backup.

      | **returned**: success
      | **type**: bool

    jcl_attrs
      Dictionary containing the names of the JCL job and step that created a dataset.

      Only available for datasets with extended attributes.

      | **returned**: success
      | **type**: dict

      creation_job
        JCL job that created the dataset.

        | **returned**: success
        | **type**: str
        | **sample**: DSALLOC

      creation_step
        JCL job step that created the dataset.

        | **returned**: success
        | **type**: str
        | **sample**: ALLOC


    volser
      Name of the volume that contains the dataset.

      | **returned**: success
      | **type**: str
      | **sample**: 000000

    num_volumes
      Number of volumes where the dataset resides.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    volumes
      Names of the volumes where the dataset resides.

      | **returned**: success
      | **type**: list
      | **elements**: str
      | **sample**:

        .. code-block:: json

            [
                "000000",
                "SCR03"
            ]

    missing_volumes
      When using the ``volumes`` option, this field contains every volume specified in a task where the dataset was missing. It is an empty list in any other case.

      | **returned**: success
      | **type**: list
      | **elements**: str
      | **sample**:

        .. code-block:: json

            [
                "222222",
                "AUXVOL"
            ]

    device_type
      Generic device type where the dataset resides.

      | **returned**: success
      | **type**: str
      | **sample**: 3390

    space_units
      Units used to describe sizes for the dataset.

      | **returned**: success
      | **type**: str
      | **sample**: track

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
      Total allocation of the dataset.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int
      | **sample**: 93

    allocation_used
      Total allocation used by the dataset.

      Uses the space units defined in space_units.

      | **returned**: success
      | **type**: int

    extents_allocated
      Number of extents allocated for the dataset.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    extents_used
      Number of extents used by the dataset.

      For PDSEs, this value is not available. Refer to the ``pages_used`` and ``perc_pages_used`` fields instead.

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

      Only returned when the dataset is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: standard

    sms_mgmt_class
      The SMS management class name.

      Only returned when the dataset is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: vsam

    sms_storage_class
      The SMS storage class name.

      Only returned when the dataset is managed by SMS and sms_managed is set to true.

      | **returned**: success
      | **type**: str
      | **sample**: fast

    encrypted
      Whether the dataset is encrypted.

      | **returned**: success
      | **type**: bool

    key_status
      Whether the dataset has a password set to read/write.

      Value can be either one of 'none', 'read' or 'write'.

      For VSAMs, the value can also be 'supp', when the module is unable to query its security attributes.

      | **returned**: success
      | **type**: str
      | **sample**: none

    racf
      Whether there is RACF protection set on the dataset.

      Value can be either one of 'none', 'generic' or 'discrete' for non-VSAM datasets.

      For VSAMs, the value can be either 'yes' or 'no'.

      | **returned**: success
      | **type**: str
      | **sample**: none

    key_label
      The encryption key label for an encrypted dataset.

      | **returned**: success
      | **type**: str
      | **sample**: keydsn

    dir_blocks_allocated
      Number of directory blocks allocated for a PDS.

      For PDSEs, this value is not available. Refer to the ``pages_used`` and ``perc_pages_used`` fields instead.

      | **returned**: success
      | **type**: int
      | **sample**: 5

    dir_blocks_used
      Number of directory blocks used by a PDS.

      For PDSEs, this value is not available. Refer to the ``pages_used`` and ``perc_pages_used`` fields instead.

      | **returned**: success
      | **type**: int
      | **sample**: 2

    members
      Number of members inside a partitioned dataset.

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
      PDSE dataset version.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    max_pdse_generation
      Maximum number of generations of a member that can be maintained in a PDSE.

      | **returned**: success
      | **type**: int

    seq_type
      Type of sequential dataset (when it applies).

      Value can be either one of 'basic', 'large' or 'extended'.

      | **returned**: success
      | **type**: str
      | **sample**: basic

    data
      Dictionary containing attributes for the DATA component of a VSAM.

      For the rest of the attributes of this dataset, query it directly with this module.

      | **returned**: success
      | **type**: dict

      key_length
        Key length for data records, in bytes.

        | **returned**: success
        | **type**: int
        | **sample**: 4

      key_offset
        Key offset for data records.

        | **returned**: success
        | **type**: int
        | **sample**: 3

      max_record_length
        Maximum length of data records, in bytes.

        | **returned**: success
        | **type**: int
        | **sample**: 80

      avg_record_length
        Average length of data records, in bytes.

        | **returned**: success
        | **type**: int
        | **sample**: 80

      bufspace
        Minimum buffer space in bytes to be provided by a processing program.

        | **returned**: success
        | **type**: int
        | **sample**: 37376

      total_records
        Total number of records.

        | **returned**: success
        | **type**: int
        | **sample**: 50

      spanned
        Whether the dataset allows records to be spanned across control intervals.

        | **returned**: success
        | **type**: bool

      volser
        Name of the volume containing the DATA component.

        | **returned**: success
        | **type**: str
        | **sample**: 000000

      device_type
        Generic device type where the DATA component resides.

        | **returned**: success
        | **type**: str
        | **sample**: 3390


    index
      Dictionary containing attributes for the INDEX component of a VSAM.

      For the rest of the attributes of this dataset, query it directly with this module.

      | **returned**: success
      | **type**: dict

      key_length
        Key length for index records, in bytes.

        | **returned**: success
        | **type**: int
        | **sample**: 4

      key_offset
        Key offset for index records.

        | **returned**: success
        | **type**: int
        | **sample**: 3

      max_record_length
        Maximum length of index records, in bytes.

        | **returned**: success
        | **type**: int

      avg_record_length
        Average length of index records, in bytes.

        | **returned**: success
        | **type**: int
        | **sample**: 505

      bufspace
        Minimum buffer space in bytes to be provided by a processing program.

        | **returned**: success
        | **type**: int

      total_records
        Total number of records.

        | **returned**: success
        | **type**: int

      volser
        Name of the volume containing the INDEX component.

        | **returned**: success
        | **type**: str
        | **sample**: 000000

      device_type
        Generic device type where the INDEX component resides.

        | **returned**: success
        | **type**: str
        | **sample**: 3390


    limit
      Maximum amount of active generations allowed in a GDG.

      | **returned**: success
      | **type**: int
      | **sample**: 10

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

      Value can be either 'lifo' or 'fifo'.

      | **returned**: success
      | **type**: str
      | **sample**: lifo

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
      | **sample**:

        .. code-block:: json

            [
                "USER.GDG.G0001V00",
                "USER.GDG.G0002V00"
            ]

    auditfid
      File system identification string for an aggregate.

      | **returned**: success
      | **type**: str
      | **sample**: C3C6C3F0 F0F3000E 0000

    bitmap_file_size
      Size in K of an aggregate's bitmap file.

      | **returned**: success
      | **type**: int
      | **sample**: 8

    converttov5
      Value of the converttov5 flag of an aggregate.

      | **returned**: success
      | **type**: bool

    filesystem_table_size
      Size in K of an aggregate's filesystem table.

      | **returned**: success
      | **type**: int
      | **sample**: 16

    free
      Kilobytes still free in an aggregate.

      | **returned**: success
      | **type**: int
      | **sample**: 559

    free_1k_fragments
      Number of free 1-KB fragments in an aggregate.

      | **returned**: success
      | **type**: int
      | **sample**: 7

    free_8k_blocks
      Number of free 8-KB blocks in an aggregate.

      | **returned**: success
      | **type**: int
      | **sample**: 69

    log_file_size
      Size in K of an aggregate's log file.

      | **returned**: success
      | **type**: int
      | **sample**: 112

    sysplex_aware
      Value of the sysplex_aware flag of an aggregate.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    total_size
      Total K available in an aggregate.

      | **returned**: success
      | **type**: int
      | **sample**: 648000

    version
      Version of an aggregate.

      | **returned**: success
      | **type**: str
      | **sample**: 1.5

    quiesced
      Attributes available when an aggregate has been quiesced.

      | **returned**: success
      | **type**: dict

      job
        Name of the job that quiesced the aggregate.

        | **returned**: success
        | **type**: str
        | **sample**: USERJOB

      system
        Name of the system that quiesced the aggregate.

        | **returned**: success
        | **type**: str
        | **sample**: GENSYS

      timestamp
        Timestamp of the quiesce operation.

        | **returned**: success
        | **type**: str
        | **sample**: 2025-02-01T18:02:05


    mode
      Octal representation of a file's permissions.

      | **returned**: success
      | **type**: str
      | **sample**: 0755

    atime
      Time of last access for a file.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-02-23T13:03:45

    mtime
      Time of last modification of a file.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-02-23T13:03:45

    ctime
      Time of last metadata update or creation for a file.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-02-23T13:03:45

    checksum
      Checksum of the file computed by the hashing algorithm specified in ``checksum_algorithm``.

      Not available when ``get_checksum=false``.

      | **returned**: success
      | **type**: str
      | **sample**: 2025-02-23T13:03:45

    uid
      ID of the file's owner.

      | **returned**: success
      | **type**: int

    gid
      ID of the file's group.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    size
      Size of the file in bytes.

      | **returned**: success
      | **type**: int
      | **sample**: 9840

    inode
      Inode number of the path.

      | **returned**: success
      | **type**: int
      | **sample**: 1671

    dev
      Device the inode resides on.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    nlink
      Number of links to the inode.

      | **returned**: success
      | **type**: int
      | **sample**: 1

    isdir
      Whether the path is a directory.

      | **returned**: success
      | **type**: bool

    ischr
      Whether the path is a character device.

      | **returned**: success
      | **type**: bool

    isblk
      Whether the path is a block device.

      | **returned**: success
      | **type**: bool

    isreg
      Whether the path is a regular file.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    isfifo
      Whether the path is a named pipe.

      | **returned**: success
      | **type**: bool

    islnk
      Whether the file is a symbolic link.

      | **returned**: success
      | **type**: bool

    issock
      Whether the file is a Unix domain socket.

      | **returned**: success
      | **type**: bool

    isuid
      Whether the Ansible user's ID matches the owner's ID.

      | **returned**: success
      | **type**: bool

    isgid
      Whether the Ansible user's group matches the owner's group.

      | **returned**: success
      | **type**: bool

    wusr
      Whether the file's owner has write permission.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    rusr
      Whether the file's owner has read permission.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    xusr
      Whether the file's owner has execute permission.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    wgrp
      Whether the file's group has write permission.

      | **returned**: success
      | **type**: bool

    rgrp
      Whether the file's group has read permission.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    xgrp
      Whether the file's group has execute permission.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    woth
      Whether others have write permission over the file.

      | **returned**: success
      | **type**: bool

    roth
      Whether others have read permission over the file.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    xoth
      Whether others have run permission over the file.

      | **returned**: success
      | **type**: bool

    writeable
      Whether the Ansible user can write to the path.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    readable
      Whether the Ansible user can read the path.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    executable
      Whether the Ansible user can run the path.

      | **returned**: success
      | **type**: bool
      | **sample**:

        .. code-block:: json

            true

    pw_name
      User name of the file's owner.

      | **returned**: success
      | **type**: str
      | **sample**: username

    gr_name
      Group name of the file's owner.

      | **returned**: success
      | **type**: str
      | **sample**: group

    lnk_source
      Absolute path to the target of a symlink.

      | **returned**: success
      | **type**: str
      | **sample**: /etc/foobar/file

    lnk_target
      Target of a symlink.

      Preserves relative paths.

      | **returned**: success
      | **type**: str
      | **sample**: ../foobar/file

    charset
      Current encoding tag associated with the file.

      This tag does not necessarily correspond with the actual encoding of the file.

      | **returned**: success
      | **type**: str
      | **sample**: IBM-1047

    mimetype
      Output from the file utility describing the content.

      Not available when ``get_mime=false``.

      | **returned**: success
      | **type**: str
      | **sample**: commands text

    audit_bits
      Audit bits for the file. Contains two sets of 3 bits.

      First 3 bits describe the user-requested audit information.

      Last 3 bits describe the auditor-requested audit information.

      For each set, the bits represent read, write and execute/search audit options.

      An 's' means to audit successful access attempts.

      An 'f' means to audit failed access attempts.

      An 'a' means to audit all access attempts.

      An '-' means to not audit accesses.

      | **returned**: success
      | **type**: str
      | **sample**: fff---

    file_format
      File format (for regular files). One of "null", "bin" or "rec".

      Text data delimiter for a file. One of "nl", "cr", "lf", "crlf", "lfcr" or "crnl".

      | **returned**: success
      | **type**: str
      | **sample**: bin