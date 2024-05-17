
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_data_set.py

.. _zos_data_set_module:


zos_data_set -- Manage data sets
================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Create, delete and set attributes of data sets.
- When forcing data set replacement, contents will not be preserved.





Parameters
----------


name
  The name of the data set being managed. (e.g \ :literal:`USER.TEST`\ )

  If \ :emphasis:`name`\  is not provided, a randomized data set name will be generated with the HLQ matching the module-runners username.

  Required if \ :emphasis:`type=member`\  or \ :emphasis:`state!=present`\  and not using \ :emphasis:`batch`\ .

  | **required**: False
  | **type**: str


state
  The final state desired for specified data set.

  If \ :emphasis:`state=absent`\  and the data set does not exist on the managed node, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=absent`\  and the data set does exist on the managed node, remove the data set, module completes successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=absent`\  and \ :emphasis:`type=member`\  and \ :emphasis:`force=True`\ , the data set will be opened with \ :emphasis:`DISP=SHR`\  such that the entire data set can be accessed by other processes while the specified member is deleted.


  If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is not found in the catalog, the module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog is successful, then the data set is removed. Module completes successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is not found in the catalog, the module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog fails, then no action is taken. Module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is found in the catalog, the module compares the catalog volume attributes to the provided \ :emphasis:`volumes`\ . If the volume attributes are different, the cataloged data set will be uncataloged temporarily while the requested data set be deleted is cataloged. The module will catalog the original data set on completion, if the attempts to catalog fail, no action is taken. Module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=absent`\  and \ :emphasis:`type=gdg`\  and the GDG base has active generations the module will complete successfully with \ :emphasis:`changed=False`\ . To remove it option \ :emphasis:`force`\  needs to be used. If the GDG base does not have active generations the module will complete successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=present`\  and the data set does not exist on the managed node, create and catalog the data set, module completes successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=present`\  and \ :emphasis:`replace=True`\  and the data set is present on the managed node the existing data set is deleted, and a new data set is created and cataloged with the desired attributes, module completes successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=present`\  and \ :emphasis:`replace=False`\  and the data set is present on the managed node, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=present`\  and \ :emphasis:`type=member`\  and the member does not exist in the data set, create a member formatted to store data, module completes successfully with \ :emphasis:`changed=True`\ . Note, a PDSE does not allow a mixture of formats such that there is executables (program objects) and data. The member created is formatted to store data, not an executable.


  If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is already cataloged, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is not cataloged, module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog is successful, module completes successfully with \ :emphasis:`changed=True`\ .


  If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is not cataloged, module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog fails, returns failure with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=uncataloged`\  and the data set is not found, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


  If \ :emphasis:`state=uncataloged`\  and the data set is found, the data set is uncataloged, module completes successfully with \ :emphasis:`changed=True`\ .


  | **required**: False
  | **type**: str
  | **default**: present
  | **choices**: present, absent, cataloged, uncataloged


type
  The data set type to be used when creating a data set. (e.g \ :literal:`pdse`\ ).

  \ :literal:`member`\  expects to be used with an existing partitioned data set.

  Choices are case-sensitive.

  | **required**: False
  | **type**: str
  | **default**: pds
  | **choices**: ksds, esds, rrds, lds, seq, pds, pdse, library, basic, large, member, hfs, zfs, gdg


space_primary
  The amount of primary space to allocate for the dataset.

  The unit of space used is set using \ :emphasis:`space\_type`\ .

  | **required**: False
  | **type**: int
  | **default**: 5


space_secondary
  The amount of secondary space to allocate for the dataset.

  The unit of space used is set using \ :emphasis:`space\_type`\ .

  | **required**: False
  | **type**: int
  | **default**: 3


space_type
  The unit of measurement to use when defining primary and secondary space.

  Valid units of size are \ :literal:`k`\ , \ :literal:`m`\ , \ :literal:`g`\ , \ :literal:`cyl`\ , and \ :literal:`trk`\ .

  | **required**: False
  | **type**: str
  | **default**: m
  | **choices**: k, m, g, cyl, trk


record_format
  The format of the data set. (e.g \ :literal:`FB`\ )

  Choices are case-sensitive.

  When \ :emphasis:`type=ksds`\ , \ :emphasis:`type=esds`\ , \ :emphasis:`type=rrds`\ , \ :emphasis:`type=lds`\  or \ :emphasis:`type=zfs`\  then \ :emphasis:`record\_format=None`\ , these types do not have a default \ :emphasis:`record\_format`\ .

  | **required**: False
  | **type**: str
  | **default**: fb
  | **choices**: fb, vb, fba, vba, u, f


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


record_length
  The length, in bytes, of each record in the data set.

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

  \ :emphasis:`key\_offset`\  is required when \ :emphasis:`type=ksds`\ .

  \ :emphasis:`key\_offset`\  should only be provided when \ :emphasis:`type=ksds`\ 

  | **required**: False
  | **type**: int


key_length
  The key length to use when creating a KSDS data set.

  \ :emphasis:`key\_length`\  is required when \ :emphasis:`type=ksds`\ .

  \ :emphasis:`key\_length`\  should only be provided when \ :emphasis:`type=ksds`\ 

  | **required**: False
  | **type**: int


empty
  Sets the \ :emphasis:`empty`\  attribute for Generation Data Groups.

  If false, removes only the oldest GDS entry when a new GDS is created that causes GDG limit to be exceeded.

  If true, removes all GDS entries from a GDG base when a new GDS is created that causes the GDG limit to be exceeded.

  Default is false.

  | **required**: False
  | **type**: bool


extended
  Sets the \ :emphasis:`extended`\  attribute for Generation Data Groups.

  If false, allow up to 255 generation data sets (GDSs) to be associated with the GDG.

  If true, allow up to 999 generation data sets (GDS) to be associated with the GDG.

  Default is false.

  | **required**: False
  | **type**: bool


fifo
  Sets the \ :emphasis:`fifo`\  attribute for Generation Data Groups.

  If false, the order is the newest GDS defined to the oldest GDS. This is the default value.

  If true, the order is the oldest GDS defined to the newest GDS.

  Default is false.

  | **required**: False
  | **type**: bool


limit
  Sets the \ :emphasis:`limit`\  attribute for Generation Data Groups.

  Specifies the maximum number, from 1 to 255(up to 999 if extended), of GDS that can be associated with the GDG being defined.

  \ :emphasis:`limit`\  is required when \ :emphasis:`type=gdg`\ .

  | **required**: False
  | **type**: int


purge
  Sets the \ :emphasis:`purge`\  attribute for Generation Data Groups.

  Specifies whether to override expiration dates when a generation data set (GDS) is rolled off and the \ :literal:`scratch`\  option is set.

  | **required**: False
  | **type**: bool


scratch
  Sets the \ :emphasis:`scratch`\  attribute for Generation Data Groups.

  Specifies what action is to be taken for a generation data set located on disk volumes when the data set is uncataloged from the GDG base as a result of EMPTY/NOEMPTY processing.

  | **required**: False
  | **type**: bool


volumes
  If cataloging a data set, \ :emphasis:`volumes`\  specifies the name of the volume(s) where the data set is located.


  If creating a data set, \ :emphasis:`volumes`\  specifies the volume(s) where the data set should be created.


  If \ :emphasis:`volumes`\  is provided when \ :emphasis:`state=present`\ , and the data set is not found in the catalog, \ `zos\_data\_set <./zos_data_set.html>`__\  will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged.


  If \ :emphasis:`volumes`\  is provided when \ :emphasis:`state=absent`\  and the data set is not found in the catalog, \ `zos\_data\_set <./zos_data_set.html>`__\  will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged and promptly removed from the system.


  \ :emphasis:`volumes`\  is required when \ :emphasis:`state=cataloged`\ .

  Accepts a string when using a single volume and a list of strings when using multiple.

  | **required**: False
  | **type**: raw


replace
  When \ :emphasis:`replace=True`\ , and \ :emphasis:`state=present`\ , existing data set matching \ :emphasis:`name`\  will be replaced.

  Replacement is performed by deleting the existing data set and creating a new data set with the same name and desired attributes. Since the existing data set will be deleted prior to creating the new data set, no data set will exist if creation of the new data set fails.


  If \ :emphasis:`replace=True`\ , all data in the original data set will be lost.

  | **required**: False
  | **type**: bool
  | **default**: False


tmp_hlq
  Override the default high level qualifier (HLQ) for temporary and backup datasets.

  The default HLQ is the Ansible user used to execute the module and if that is not available, then the value \ :literal:`TMPHLQ`\  is used.

  | **required**: False
  | **type**: str


force
  Specifies that the data set can be shared with others during a member delete operation which results in the data set you are updating to be simultaneously updated by others.

  This is helpful when a data set is being used in a long running process such as a started task and you are wanting to delete a member.

  The \ :emphasis:`force=True`\  option enables sharing of data sets through the disposition \ :emphasis:`DISP=SHR`\ .

  The \ :emphasis:`force=True`\  only applies to data set members when \ :emphasis:`state=absent`\  and \ :emphasis:`type=member`\  and when removing a GDG base with active generations.

  If \ :emphasis:`force=True`\ , \ :emphasis:`type=gdg`\  and \ :emphasis:`state=absent`\  it will force remove a GDG base with active generations.

  | **required**: False
  | **type**: bool
  | **default**: False


batch
  Batch can be used to perform operations on multiple data sets in a single module call.

  | **required**: False
  | **type**: list
  | **elements**: dict


  name
    The name of the data set being managed. (e.g \ :literal:`USER.TEST`\ )

    If \ :emphasis:`name`\  is not provided, a randomized data set name will be generated with the HLQ matching the module-runners username.

    Required if \ :emphasis:`type=member`\  or \ :emphasis:`state!=present`\ 

    | **required**: False
    | **type**: str


  state
    The final state desired for specified data set.

    If \ :emphasis:`state=absent`\  and the data set does not exist on the managed node, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=absent`\  and the data set does exist on the managed node, remove the data set, module completes successfully with \ :emphasis:`changed=True`\ .


    If \ :emphasis:`state=absent`\  and \ :emphasis:`type=member`\  and \ :emphasis:`force=True`\ , the data set will be opened with \ :emphasis:`DISP=SHR`\  such that the entire data set can be accessed by other processes while the specified member is deleted.


    If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is not found in the catalog, the module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog is successful, then the data set is removed. Module completes successfully with \ :emphasis:`changed=True`\ .


    If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is not found in the catalog, the module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog fails, then no action is taken. Module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=absent`\  and \ :emphasis:`volumes`\  is provided, and the data set is found in the catalog, the module compares the catalog volume attributes to the provided \ :emphasis:`volumes`\ . If they volume attributes are different, the cataloged data set will be uncataloged temporarily while the requested data set be deleted is cataloged. The module will catalog the original data set on completion, if the attempts to catalog fail, no action is taken. Module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=present`\  and the data set does not exist on the managed node, create and catalog the data set, module completes successfully with \ :emphasis:`changed=True`\ .


    If \ :emphasis:`state=present`\  and \ :emphasis:`replace=True`\  and the data set is present on the managed node the existing data set is deleted, and a new data set is created and cataloged with the desired attributes, module completes successfully with \ :emphasis:`changed=True`\ .


    If \ :emphasis:`state=present`\  and \ :emphasis:`replace=False`\  and the data set is present on the managed node, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=present`\  and \ :emphasis:`type=member`\  and the member does not exist in the data set, create a member formatted to store data, module completes successfully with \ :emphasis:`changed=True`\ . Note, a PDSE does not allow a mixture of formats such that there is executables (program objects) and data. The member created is formatted to store data, not an executable.


    If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is already cataloged, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is not cataloged, module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog is successful, module completes successfully with \ :emphasis:`changed=True`\ .


    If \ :emphasis:`state=cataloged`\  and \ :emphasis:`volumes`\  is provided and the data set is not cataloged, module attempts to perform catalog using supplied \ :emphasis:`name`\  and \ :emphasis:`volumes`\ . If the attempt to catalog the data set catalog fails, returns failure with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=uncataloged`\  and the data set is not found, no action taken, module completes successfully with \ :emphasis:`changed=False`\ .


    If \ :emphasis:`state=uncataloged`\  and the data set is found, the data set is uncataloged, module completes successfully with \ :emphasis:`changed=True`\ .


    | **required**: False
    | **type**: str
    | **default**: present
    | **choices**: present, absent, cataloged, uncataloged


  type
    The data set type to be used when creating a data set. (e.g \ :literal:`pdse`\ )

    \ :literal:`member`\  expects to be used with an existing partitioned data set.

    Choices are case-sensitive.

    | **required**: False
    | **type**: str
    | **default**: pds
    | **choices**: ksds, esds, rrds, lds, seq, pds, pdse, library, basic, large, member, hfs, zfs, gdg


  space_primary
    The amount of primary space to allocate for the dataset.

    The unit of space used is set using \ :emphasis:`space\_type`\ .

    | **required**: False
    | **type**: int
    | **default**: 5


  space_secondary
    The amount of secondary space to allocate for the dataset.

    The unit of space used is set using \ :emphasis:`space\_type`\ .

    | **required**: False
    | **type**: int
    | **default**: 3


  space_type
    The unit of measurement to use when defining primary and secondary space.

    Valid units of size are \ :literal:`k`\ , \ :literal:`m`\ , \ :literal:`g`\ , \ :literal:`cyl`\ , and \ :literal:`trk`\ .

    | **required**: False
    | **type**: str
    | **default**: m
    | **choices**: k, m, g, cyl, trk


  record_format
    The format of the data set. (e.g \ :literal:`FB`\ )

    Choices are case-sensitive.

    When \ :emphasis:`type=ksds`\ , \ :emphasis:`type=esds`\ , \ :emphasis:`type=rrds`\ , \ :emphasis:`type=lds`\  or \ :emphasis:`type=zfs`\  then \ :emphasis:`record\_format=None`\ , these types do not have a default \ :emphasis:`record\_format`\ .

    | **required**: False
    | **type**: str
    | **default**: fb
    | **choices**: fb, vb, fba, vba, u, f


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


  record_length
    The length, in bytes, of each record in the data set.

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

    \ :emphasis:`key\_offset`\  is required when \ :emphasis:`type=ksds`\ .

    \ :emphasis:`key\_offset`\  should only be provided when \ :emphasis:`type=ksds`\ 

    | **required**: False
    | **type**: int


  key_length
    The key length to use when creating a KSDS data set.

    \ :emphasis:`key\_length`\  is required when \ :emphasis:`type=ksds`\ .

    \ :emphasis:`key\_length`\  should only be provided when \ :emphasis:`type=ksds`\ 

    | **required**: False
    | **type**: int


  empty
    Sets the \ :emphasis:`empty`\  attribute for Generation Data Groups.

    If false, removes only the oldest GDS entry when a new GDS is created that causes GDG limit to be exceeded.

    If true, removes all GDS entries from a GDG base when a new GDS is created that causes the GDG limit to be exceeded.

    Default is false.

    | **required**: False
    | **type**: bool


  extended
    Sets the \ :emphasis:`extended`\  attribute for Generation Data Groups.

    If false, allow up to 255 generation data sets (GDSs) to be associated with the GDG.

    If true, allow up to 999 generation data sets (GDS) to be associated with the GDG.

    Default is false.

    | **required**: False
    | **type**: bool


  fifo
    Sets the \ :emphasis:`fifo`\  attribute for Generation Data Groups.

    If false, the order is the newest GDS defined to the oldest GDS. This is the default value.

    If true, the order is the oldest GDS defined to the newest GDS.

    Default is false.

    | **required**: False
    | **type**: bool


  limit
    Sets the \ :emphasis:`limit`\  attribute for Generation Data Groups.

    Specifies the maximum number, from 1 to 255(up to 999 if extended), of GDS that can be associated with the GDG being defined.

    \ :emphasis:`limit`\  is required when \ :emphasis:`type=gdg`\ .

    | **required**: False
    | **type**: int


  purge
    Sets the \ :emphasis:`purge`\  attribute for Generation Data Groups.

    Specifies whether to override expiration dates when a generation data set (GDS) is rolled off and the \ :literal:`scratch`\  option is set.

    | **required**: False
    | **type**: bool


  scratch
    Sets the \ :emphasis:`scratch`\  attribute for Generation Data Groups.

    Specifies what action is to be taken for a generation data set located on disk volumes when the data set is uncataloged from the GDG base as a result of EMPTY/NOEMPTY processing.

    | **required**: False
    | **type**: bool


  volumes
    If cataloging a data set, \ :emphasis:`volumes`\  specifies the name of the volume(s) where the data set is located.


    If creating a data set, \ :emphasis:`volumes`\  specifies the volume(s) where the data set should be created.


    If \ :emphasis:`volumes`\  is provided when \ :emphasis:`state=present`\ , and the data set is not found in the catalog, \ `zos\_data\_set <./zos_data_set.html>`__\  will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged.


    If \ :emphasis:`volumes`\  is provided when \ :emphasis:`state=absent`\  and the data set is not found in the catalog, \ `zos\_data\_set <./zos_data_set.html>`__\  will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged and promptly removed from the system.


    \ :emphasis:`volumes`\  is required when \ :emphasis:`state=cataloged`\ .

    Accepts a string when using a single volume and a list of strings when using multiple.

    | **required**: False
    | **type**: raw


  replace
    When \ :emphasis:`replace=True`\ , and \ :emphasis:`state=present`\ , existing data set matching \ :emphasis:`name`\  will be replaced.

    Replacement is performed by deleting the existing data set and creating a new data set with the same name and desired attributes. Since the existing data set will be deleted prior to creating the new data set, no data set will exist if creation of the new data set fails.


    If \ :emphasis:`replace=True`\ , all data in the original data set will be lost.

    | **required**: False
    | **type**: bool
    | **default**: False


  force
    Specifies that the data set can be shared with others during a member delete operation which results in the data set you are updating to be simultaneously updated by others.

    This is helpful when a data set is being used in a long running process such as a started task and you are wanting to delete a member.

    The \ :emphasis:`force=True`\  option enables sharing of data sets through the disposition \ :emphasis:`DISP=SHR`\ .

    The \ :emphasis:`force=True`\  only applies to data set members when \ :emphasis:`state=absent`\  and \ :emphasis:`type=member`\ .

    | **required**: False
    | **type**: bool
    | **default**: False





Examples
--------

.. code-block:: yaml+jinja

   
   - name: Create a sequential data set if it does not exist
     zos_data_set:
       name: someds.name.here
       type: seq
       state: present

   - name: Create a PDS data set if it does not exist
     zos_data_set:
       name: someds.name.here
       type: pds
       space_primary: 5
       space_type: m
       record_format: fba
       record_length: 25

   - name: Attempt to replace a data set if it exists
     zos_data_set:
       name: someds.name.here
       type: pds
       space_primary: 5
       space_type: m
       record_format: u
       record_length: 25
       replace: true

   - name: Attempt to replace a data set if it exists. If not found in the catalog, check if it is available on volume 222222, and catalog if found.
     zos_data_set:
       name: someds.name.here
       type: pds
       space_primary: 5
       space_type: m
       record_format: u
       record_length: 25
       volumes: "222222"
       replace: true

   - name: Create an ESDS data set if it does not exist
     zos_data_set:
       name: someds.name.here
       type: esds

   - name: Create a KSDS data set if it does not exist
     zos_data_set:
       name: someds.name.here
       type: ksds
       key_length: 8
       key_offset: 0

   - name: Create an RRDS data set with storage class MYDATA if it does not exist
     zos_data_set:
       name: someds.name.here
       type: rrds
       sms_storage_class: mydata

   - name: Delete a data set if it exists
     zos_data_set:
       name: someds.name.here
       state: absent

   - name: Delete a data set if it exists. If data set not cataloged, check on volume 222222 for the data set, and then catalog and delete if found.
     zos_data_set:
       name: someds.name.here
       state: absent
       volumes: "222222"

   - name: Write a member to an existing PDS; replace if member exists
     zos_data_set:
       name: someds.name.here(mydata)
       type: member
       replace: true

   - name: Write a member to an existing PDS; do not replace if member exists
     zos_data_set:
       name: someds.name.here(mydata)
       type: member

   - name: Remove a member from an existing PDS
     zos_data_set:
       name: someds.name.here(mydata)
       state: absent
       type: member

   - name: Remove a member from an existing PDS/E by opening with disposition DISP=SHR
     zos_data_set:
       name: someds.name.here(mydata)
       state: absent
       type: member
       force: true

   - name: Create multiple partitioned data sets and add one or more members to each
     zos_data_set:
       batch:
         - name: someds.name.here1
           type: pds
           space_primary: 5
           space_type: m
           record_format: fb
           replace: true
         - name: someds.name.here1(member1)
           type: member
         - name: someds.name.here2(member1)
           type: member
           replace: true
         - name: someds.name.here2(member2)
           type: member

   - name: Catalog a data set present on volume 222222 if it is uncataloged.
     zos_data_set:
       name: someds.name.here
       state: cataloged
       volumes: "222222"

   - name: Uncatalog a data set if it is cataloged.
     zos_data_set:
       name: someds.name.here
       state: uncataloged

   - name: Create a data set on volumes 000000 and 222222 if it does not exist.
     zos_data_set:
       name: someds.name.here
       state: present
       volumes:
         - "000000"
         - "222222"










Return Values
-------------


names
  The data set names, including temporary generated data set names, in the order provided to the module.

  | **returned**: always
  | **type**: list
  | **elements**: str

