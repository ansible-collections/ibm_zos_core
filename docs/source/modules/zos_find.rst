
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_find.py

.. _zos_find_module:


zos_find -- Find matching data sets
===================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Return a list of data sets based on specific criteria.
- Multiple criteria can be added (AND'd) together.
- The ``zos_find`` module can only find MVS data sets. Use the `find <https://docs.ansible.com/ansible/latest/modules/find_module.html>`_ module to find USS files.





Parameters
----------


age
  Select data sets whose age is equal to or greater than the specified time.

  Use a negative age to find data sets equal to or less than the specified time.

  You can choose days, weeks, months or years by specifying the first letter of any of those words (e.g., "1w"). The default is days.

  Age is determined by using the 'referenced date' of the data set.

  | **required**: False
  | **type**: str


age_stamp
  Choose the age property against which to compare age.

  ``creation_date`` is the date the data set was created and ``ref_date`` is the date the data set was last referenced.

  ``ref_date`` is only applicable to sequential and partitioned data sets.

  | **required**: False
  | **type**: str
  | **default**: creation_date
  | **choices**: creation_date, ref_date


contains
  A string which should be matched against the data set content or data set member content.

  | **required**: False
  | **type**: str


excludes
  Data sets whose names match an excludes pattern are culled from patterns matches. Multiple patterns can be specified using a list.

  The pattern can be a regular expression.

  If the pattern is a regular expression, it must match the full data set name.

  | **required**: False
  | **type**: list


patterns
  One or more data set or member patterns.

  The patterns restrict the list of data sets or members to be returned to those names that match at least one of the patterns specified. Multiple patterns can be specified using a list.

  This parameter expects a list, which can be either comma separated or YAML.

  If ``pds_patterns`` is provided, ``patterns`` must be member patterns.

  When searching for members within a PDS/PDSE, pattern can be a regular expression.

  | **required**: True
  | **type**: list


size
  Select data sets whose size is equal to or greater than the specified size.

  Use a negative size to find files equal to or less than the specified size.

  Unqualified values are in bytes but b, k, m, g, and t can be appended to specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.

  Filtering by size is currently only valid for sequential and partitioned data sets.

  | **required**: False
  | **type**: str


pds_patterns
  List of PDS/PDSE to search. Wildcard is possible.

  Required when searching for data set members.

  Valid only for ``nonvsam`` resource types. Otherwise ignored.

  | **required**: False
  | **type**: list


resource_type
  The type of resource to search.

  ``nonvsam`` refers to one of SEQ, LIBRARY (PDSE), PDS, LARGE, BASIC, EXTREQ, or EXTPREF.

  ``cluster`` refers to a VSAM cluster. The ``data`` and ``index`` are the data and index components of a VSAM cluster.

  | **required**: False
  | **type**: str
  | **default**: nonvsam
  | **choices**: nonvsam, cluster, data, index


volume
  If provided, only the data sets allocated in the specified list of volumes will be searched.

  | **required**: False
  | **type**: list




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Find all data sets with HLQ 'IMS.LIB' or 'IMSTEST.LIB' that contain the word 'hello'
     zos_find:
       patterns:
         - IMS.LIB.*
         - IMSTEST.LIB.*
       contains: 'hello'
       age: 2d

   - name: Search for 'rexx' in all datasets matching IBM.TSO.*.C??
     zos_find:
       patterns:
         - IBM.TSO.*.C??
       contains: 'rexx'

   - name: Exclude data sets that have a low level qualifier 'TEST'
     zos_find:
       patterns: 'IMS.LIB.*'
       contains: 'hello'
       excludes: '*.TEST'

   - name: Find all members starting with characters 'TE' in a given list of PDS patterns
     zos_find:
       patterns: '^te.*'
       pds_patterns:
         - IMSTEST.TEST.*
         - IMSTEST.USER.*
         - USER.*.LIB

   - name: Find all data sets greater than 2MB and allocated in one of the specified volumes
     zos_find:
       patterns: 'USER.*'
       size: 2m
       volumes:
         - SCR03
         - IMSSUN

   - name: Find all VSAM clusters starting with the word 'USER'
     zos_find:
       patterns:
         - USER.*
       resource_type: cluster




Notes
-----

.. note::
   Only cataloged data sets will be searched. If an uncataloged data set needs to be searched, it should be cataloged first. The :ref:`zos_data_set <zos_data_set_module>` module can be used to catalog uncataloged data sets.

   The :ref:`zos_find <zos_find_module>` module currently does not support wildcards for high level qualifiers. For example, ``SOME.*.DATA.SET`` is a valid pattern, but ``*.DATA.SET`` is not.

   If a data set pattern is specified as ``USER.*``, the matching data sets will have two name segments such as ``USER.ABC``, ``USER.XYZ`` etc. If a wildcard is specified as ``USER.*.ABC``, the matching data sets will have three name segments such as ``USER.XYZ.ABC``, ``USER.TEST.ABC`` etc.

   The time taken to execute the module is proportional to the number of data sets present on the system and how large the data sets are.

   When searching for content within data sets, only non-binary content is considered.



See Also
--------

.. seealso::

   - :ref:`zos_data_set_module`




Return Values
-------------


data_sets
  All matches found with the specified criteria.

  | **returned**: success
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            {
                "members": {
                    "COBU": null,
                    "MC2CNAM": null,
                    "TINAD": null
                },
                "name": "IMS.CICS13.USERLIB",
                "type": "NONVSAM"
            },
            {
                "name": "SAMPLE.DATA.SET",
                "type": "CLUSTER"
            },
            {
                "name": "SAMPLE.VSAM.DATA",
                "type": "DATA"
            }
        ]

matched
  The number of matched data sets found.

  | **returned**: success
  | **type**: int
  | **sample**: 49

examined
  The number of data sets searched.

  | **returned**: success
  | **type**: int
  | **sample**: 158

msg
  Failure message returned by the module.

  | **returned**: failure
  | **type**: str
  | **sample**: Error while gathering data set information

stdout
  The stdout from a USS command or MVS command, if applicable.

  | **returned**: failure
  | **type**: str
  | **sample**: Searching dataset IMSTESTL.COMNUC

stderr
  The stderr of a USS command or MVS command, if applicable.

  | **returned**: failure
  | **type**: str
  | **sample**: No such file or directory "/tmp/foo"

rc
  The return code of a USS or MVS command, if applicable.

  | **returned**: failure
  | **type**: int
  | **sample**: 8

