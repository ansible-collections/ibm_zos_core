
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


 
     
batch
  Batch can be used to perform operations on multiple data sets in a single module call.


  | **required**: False
  | **type**: list


 
     
  data_class
    The data class name.

    Required for SMS managed data sets.


    | **required**: False
    | **type**: str


 
     
  format
    The format of the data set. (e.g ``FB``)

    Choices are case-insensitive.


    | **required**: False
    | **type**: str
    | **default**: FB
    | **choices**: FB, VB, FBA, VBA, U


 
     
  name
    The name of the data set being managed. (e.g ``USER.TEST``)

    Name field is required unless using batch option.


    | **required**: True
    | **type**: str


 
     
  record_length
    The logical record length. (e.g ``80``)

    For variable data sets, the length must include the 4-byte prefix area.

    Defaults vary depending on format. If FB/FBA 80, if VB/VBA 137, if U 0


    | **required**: False
    | **type**: int


 
     
  replace
    When *replace=True*, and *state=present*, existing data set matching *name* will be replaced.

    Replacement is performed by deleting the existing data set and creating a new data set with the same name and desired attributes. This may lead to an inconsistent state if data set creations fails after the old data set is deleted.


    If *replace=True*, all data in the original data set will be lost.


    | **required**: False
    | **type**: bool


 
     
  size
    The size of the data set (e.g ``5M``)

    Valid units of size are ``K``, ``M``, ``G``, ``CYL``, and ``TRK``

    Note that ``CYL`` and ``TRK`` follow size conventions for 3390 disk types (56,664 bytes/TRK & 849,960 bytes/CYL)

    The ``CYL`` and ``TRK`` units are converted to bytes and rounded up to the nearest ``K`` measurement.

    Ensure there is no space between the numeric size and unit.


    | **required**: False
    | **type**: str
    | **default**: 5M


 
     
  state
    The final state desired for specified data set.

    If *state=absent* and the data set does not exist on the managed node, no action taken, returns successful with *changed=False*.


    If *state=absent* and the data set does exist on the managed node, remove the data set, returns successful with *changed=True*.


    If *state=present* and the data set does not exist on the managed node, create the data set, returns successful with *changed=True*.


    If *state=present* and *replace=True* and the data set is present on the managed node, delete the data set and create the data set with the desired attributes, returns successful with *changed=True*.


    If *state=present* and *replace=False* and the data set is present on the managed node, no action taken, returns successful with *changed=False*.



    | **required**: False
    | **type**: str
    | **default**: present
    | **choices**: present, absent


 
     
  type
    The data set type to be used when creating a data set. (e.g ``pdse``)

    MEMBER expects to be used with an existing partitioned data set.

    Choices are case-insensitive.


    | **required**: False
    | **type**: str
    | **choices**: ESDS, RRDS, LDS, SEQ, PDS, PDSE, MEMBER


 
     
  volume
    The name of the volume where the data set is located. *volume* is not used to specify the volume where a data set should be created.


    If *volume* is provided when *state=present*, and the data set is not found in the catalog, :ref:`zos_data_set <zos_data_set_module>` will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged.


    If *volume* is provided when *state=absent* and the data set is not found in the catalog, :ref:`zos_data_set <zos_data_set_module>` will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged and promptly removed from the system.


    *volume* is required when *state=cataloged*


    | **required**: False
    | **type**: str



 
     
data_class
  The data class name.

  Required for SMS managed data sets.


  | **required**: False
  | **type**: str


 
     
format
  The format of the data set. (e.g ``FB``)

  Choices are case-insensitive.


  | **required**: False
  | **type**: str
  | **default**: FB
  | **choices**: FB, VB, FBA, VBA, U


 
     
name
  The name of the data set being managed. (e.g ``USER.TEST``)

  Name field is required unless using batch option


  | **required**: False
  | **type**: str


 
     
record_length
  The logical record length (e.g ``80``).

  For variable data sets, the length must include the 4-byte prefix area.

  Defaults vary depending on format. If FB/FBA 80, if VB/VBA 137, if U 0


  | **required**: False
  | **type**: int


 
     
replace
  When *replace=True*, and *state=present*, existing data set matching *name* will be replaced.

  Replacement is performed by deleting the existing data set and creating a new data set with the same name and desired attributes. This may lead to an inconsistent state if data set creations fails. after the old data set is deleted.


  If *replace=True*, all data in the original data set will be lost.


  | **required**: False
  | **type**: bool


 
     
size
  The size of the data set (e.g ``5M``).

  Valid units of size are ``K``, ``M``, ``G``, ``CYL``, and ``TRK``.

  Note that ``CYL`` and ``TRK`` follow size conventions for 3390 disk types (56,664 bytes/TRK & 849,960 bytes/CYL).

  The ``CYL`` and ``TRK`` units are converted to bytes and rounded up to the nearest ``K`` measurement.

  Ensure there is no space between the numeric size and unit.


  | **required**: False
  | **type**: str
  | **default**: 5M


 
     
state
  The final state desired for specified data set.

  If *state=absent* and the data set does not exist on the managed node, no action taken, returns successful with *changed=False*.


  If *state=absent* and the data set does exist on the managed node, remove the data set, returns successful with *changed=True*.


  If *state=present* and the data set does not exist on the managed node, create the data set, returns successful with *changed=True*.


  If *state=present* and *replace=True* and the data set is present on the managed node, delete the data set and create the data set with the desired attributes, returns successful with *changed=True*.


  If *state=present* and *replace=False* and the data set is present on the managed node, no action taken, returns successful with *changed=False*.



  | **required**: False
  | **type**: str
  | **default**: present
  | **choices**: present, absent, cataloged, uncataloged


 
     
type
  The data set type to be used when creating a data set. (e.g ``pdse``)

  MEMBER expects to be used with an existing partitioned data set.

  Choices are case-insensitive.


  | **required**: False
  | **type**: str
  | **choices**: ESDS, RRDS, LDS, SEQ, PDS, PDSE, MEMBER


 
     
volume
  The name of the volume where the data set is located. *volume* is not used to specify the volume where a data set should be created.


  If *volume* is provided when *state=present*, and the data set is not found in the catalog, :ref:`zos_data_set <zos_data_set_module>` will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged.


  If *volume* is provided when *state=absent* and the data set is not found in the catalog, :ref:`zos_data_set <zos_data_set_module>` will check the volume table of contents to see if the data set exists. If the data set does exist, it will be cataloged and promptly removed from the system.


  *volume* is required when *state=cataloged*


  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Create a sequential data set if it does not exist
     zos_data_set:
       name: user.private.libs
       type: seq
       state: present

   - name: Create a PDS data set if it does not exist
     zos_data_set:
       name: user.private.libs
       type: pds
       size: 5M
       format: fba
       record_length: 25

   - name: Attempt to replace a data set if it exists
     zos_data_set:
       name: user.private.libs
       type: pds
       size: 5M
       format: u
       record_length: 25
       replace: yes

   - name: Attempt to replace a data set if it exists. If not found in catalog, check if on volume 222222 and catalog if found.
     zos_data_set:
       name: user.private.libs
       type: pds
       size: 5M
       format: u
       record_length: 25
       volume: "222222"
       replace: yes

   - name: Create an ESDS data set is it does not exist
     zos_data_set:
       name: user.private.libs
       type: esds

   - name: Create an RRDS data set with data class MYDATA if it does not exist
     zos_data_set:
       name: user.private.libs
       type: rrds
       data_class: mydata

   - name: Delete a data set if it exists
     zos_data_set:
       name: user.private.libs
       state: absent

   - name: Delete a data set if it exists. If data set not cataloged, check on volume 222222 for the data set, then catalog and delete if found.
     zos_data_set:
       name: user.private.libs
       state: absent
       volume: "222222"

   - name: Write a member to existing PDS, replace if member exists
     zos_data_set:
       name: user.private.libs(mydata)
       type: MEMBER
       replace: yes

   - name: Write a member to existing PDS, do not replace if member exists
     zos_data_set:
       name: user.private.libs(mydata)
       type: MEMBER

   - name: Remove a member from existing PDS if it exists
     zos_data_set:
       name: user.private.libs(mydata)
       state: absent
       type: MEMBER

   - name: Create multiple partitioned data sets and add one or more members to each
     zos_data_set:
       batch:
         - name:  user.private.libs1
           type: PDS
           size: 5M
           format: fb
           replace: yes
         - name: user.private.libs1(member1)
           type: MEMBER
         - name: user.private.libs2(member1)
           type: MEMBER
           replace: yes
         - name: user.private.libs2(member2)
           type: MEMBER

   - name: Catalog a data set present on volume 222222 if it is uncataloged.
     zos_data_set:
       name: user.private.libs
       state: cataloged
       volume: "222222"

   - name: Uncatalog a data set if it is cataloged.
     zos_data_set:
       name: user.private.libs
       state: uncataloged









