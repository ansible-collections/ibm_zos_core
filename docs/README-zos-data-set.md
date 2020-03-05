Module
============
Name
-----------
zos_data_set


Description 
-----------

The `zos_data_set` module is used to create, delete, and set attributes of data sets.
When forcing data set replacement, contents will not be preserved.

Features
--------
* Create, replace, and delete data sets
* Uses `present` and `absent` to determine desired state
* Maintains idempotence


Usage
=====

Example tasks:  
```
- name: Create a sequential data set if it does not exist
  zos_data_set:
    name: user.private.libs
    type: seq
    state: present
```
```
- name: Create a PDS data set if it does not exist
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: fba
    record_length: 25
```
```
- name: Attempt to replace a data set if it exists
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: u
    record_length: 25
    replace: yes
```
```
- name: Attempt to replace a data set if it exists, allow unsafe_writes
  zos_data_set:
    name: user.private.libs
    type: pds
    size: 5M
    format: fb
    record_length: 25
    replace: yes
    unsafe_writes: yes
```
```
- name: Create an ESDS data set is it does not exist
  zos_data_set:
    name: user.private.libs
    type: esds
```
```
- name: Create an RRDS data set with data class MYDATA if it does not exist
  zos_data_set:
    name: user.private.libs
    type: rrds
    data_class: mydata
```
```
- name: Delete a data set if it exists
  zos_data_set:
    name: user.private.libs
    state: absent
```
```
- name: Write a member to existing PDS, replace if member exists
  zos_data_set:
    name: user.private.libs(mydata)
    type: MEMBER
    replace: yes
```
```
- name: Write a member to existing PDS, do not replace if member exists
  zos_data_set:
    name: user.private.libs(mydata)
    type: MEMBER
```
```
- name: Remove a member from existing PDS if it exists
  zos_data_set:
    name: user.private.libs(mydata)
    state: absent
    type: MEMBER   
```
```
- name: Create multiple partitioned data sets and add one or more members to each
  zos_data_set:
    batch:
      - name:  user.private.libs1
        type: PDS
        size: 5M
        format: fb
        replace: yes
      - name:  user.private.libs2
        type: PDSE
        size: 10CYL
        format: fb
        replace: yes
        unsafe_writes: yes
      - name: user.private.libs1(member1)
        type: MEMBER
      - name: user.private.libs2(member1)
        type: MEMBER
        replace: yes
      - name: user.private.libs2(member2)
        type: MEMBER
```

Return values:

* __original_message__:
  * _description_: The original list of parameters and arguments, plus any defaults used.
  * _returned_: always
  * _type_: dict
* __message__:
  * _description_: The output message that the sample module generates.
  * _type_: complex
  * _returned_: success
  * _contains_:
    * __stdout__:
      * _description_: The output from the module.
      * _type_: str
    * __stderr__: 
      * _description_: Any error text from the module.
      * _type_: str
* __changed__: 
  * _description_: Indicates if any changes were made during module operation.
  * _type_: bool

Variables
=========

Variables available for module zos_ds:

-------

| Variable        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Required |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `name`          | Name of the data set.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | yes      |
| `data_class`    | The data class name (required for SMS-managed data sets)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | no       |
| `format`        | The format of the data set (for example, "FB").                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | no       |
| `record_length` | The logical record length (for example, 80).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | no       |
| `replace`       | When `replace` is `true`, and `state` is `present`, the existing data set matching name will be replaced. Replacement is performed by allocating a new data set with your desired attributes to ensure that space is available. Then, the original data set is removed, and your new data set is moved to the original data set name. In cases where this method of replacement might fail due to lack of space or other issues,  `unsafe_writes` can be specified to force delete and create without the intermediate data set creation. Note that this is more unlikely to leave data sets in an inconsistent state. Use `unsafe_writes` with caution. | no       |
| `size`          | The size of the data set (for example, "5M").                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | no       |
| `state`         | The final state desired for specified data set. If `absent`, it will ensure that the data set is not present on the system. Note that `absent` will not cause the `zos_data_set` to fail if data set does not exist because the state did not change. If `present`, it will ensure that the data set is present on the system. Note that `present` will not replace an existing data set by default even when the attributes do not match your desired data set. If replacement behavior is required, see the options `replace` and `unsafe_writes`.                                                                                                     | no       |
| `type`          | The data set type to be used when creating a data set (for example, "PDSE").                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | no       |

# Copyright
© Copyright IBM Corporation 2020  
