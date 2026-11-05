
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_find.py

.. _ibm.ibm_zos_core.zos_find_module:


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

  Age is determined by the date selected with ``age_stamp`` (default ``creation_date``).

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

  To exclude members, the regular expression or pattern must be enclosed in parentheses. This expression can be used alongside a pattern to exclude data set names.

  When using ``resource_type=alias``, non-parenthesised patterns match against the ALIAS data set name itself and remove the entire alias entry from the results. Parenthesised patterns match against the PDS/PDSE member names of the data set the alias points to; matching members are removed from the returned ``members`` list. The actual alias entries on the z/OS system are not deleted; only the result set is filtered.

  | **required**: False
  | **type**: list
  | **elements**: str


patterns
  One or more data set or member patterns.

  The patterns restrict the list of data sets or members to be returned to those names that match at least one of the patterns specified. Multiple patterns can be specified using a list.

  This parameter expects a list, which can be either comma separated or YAML.

  When searching for members within a PDS/PDSE, pattern can be a regular expression.

  | **required**: True
  | **type**: list
  | **elements**: str


size
  Select data sets whose size is equal to or greater than the specified size.

  Use a negative size to find files equal to or less than the specified size.

  Unqualified values are in bytes but b, k, m, g, and t can be appended to specify bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.

  Filtering by size is currently only valid for sequential and partitioned data sets.

  | **required**: False
  | **type**: str


resource_type
  The types of resources to search.

  ``nonvsam`` refers to one of SEQ, LIBRARY (PDSE), PDS, LARGE, BASIC, EXTREQ, or EXTPREF.

  ``cluster`` refers to a VSAM cluster. The ``data`` and ``index`` are the data and index components of a VSAM cluster.

  ``gdg`` refers to Generation Data Groups. The module searches based on the GDG base name.

  ``migrated`` refers to listing migrated datasets. Only ``excludes`` and ``migrated_type`` options can be used along with this option. The module only searches based on dataset patterns.

  ``alias`` refers to MVS catalog alias entries. The module returns the alias name and the real dataset name it points to (returned as ``alias_of`` in each result).

  The ``patterns``, ``excludes``, ``volume``, ``age``, ``age_stamp``, ``size``, and ``contains`` options are applicable when using ``alias`` resource type. The ``volume``, ``age``, ``age_stamp``, ``size``, and ``contains`` filters are applied against the target dataset (``alias_of``), not the alias entry itself.

  | **required**: False
  | **type**: list
  | **elements**: str
  | **default**: nonvsam
  | **choices**: nonvsam, cluster, data, index, gdg, migrated, alias


migrated_type
  A migrated data set related attribute, only valid when ``resource_type=migrated``.

  If provided, will search for only those types of migrated datasets.

  | **required**: False
  | **type**: list
  | **elements**: str
  | **default**: ['cluster', 'data', 'index', 'nonvsam']
  | **choices**: nonvsam, cluster, data, index


volume
  If provided, only the data sets allocated in the specified list of volumes will be searched.

  | **required**: False
  | **type**: list
  | **elements**: str


empty
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *empty* attribute set as provided.

  | **required**: False
  | **type**: bool


extended
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *extended* attribute set as provided.

  | **required**: False
  | **type**: bool


fifo
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *fifo* attribute set as provided.

  | **required**: False
  | **type**: bool


limit
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *limit* attribute set as provided.

  | **required**: False
  | **type**: int


purge
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *purge* attribute set as provided.

  | **required**: False
  | **type**: bool


scratch
  A GDG attribute, only valid when ``resource_type=gdg``.

  If provided, will search for data sets with *scratch* attribute set as provided.

  | **required**: False
  | **type**: bool




Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: none
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Exclude all members starting with characters 'TE' in a given list datasets patterns
     zos_find:
       excludes: '(^te.*)'
       patterns:
         - IMSTEST.TEST.*
         - IMSTEST.USER.*
         - USER.*.LIB

   - name: Exclude datasets that includes 'DATA' and members starting with characters 'MEM' in a given list datasets patterns
     zos_find:
       excludes: '^.*DATA.*(^MEM.*)'
       patterns:
         - IMSTEST.*.TEST
         - IMSTEST.*.*
         - USER.*.LIB

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
       excludes: '.*TEST'

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
       resource_type:
         - 'cluster'

   - name: Find all Generation Data Groups starting with the word 'USER' and specific GDG attributes.
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - 'gdg'
       limit: 30
       scratch: true
       purge: true

   - name: Find all migrated and nonvsam data sets starting with the word 'USER'
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - 'migrated'
       migrated_type:
         - 'nonvsam'

   - name: Find all data set aliases starting with 'USER'
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - alias

   - name: Find aliases matching a pattern but excluding specific entries
     zos_find:
       patterns:
         - MYHLQ.*
       resource_type:
         - alias
       excludes:
         - '.*TEMP.*'

   - name: Find all PDS/PDSE aliases excluding members whose name starts with 'TMP'
     zos_find:
       patterns:
         - ANSIBLE.ALIAS.TEST.*
       resource_type:
         - alias
       excludes: '(^TMP.*)'

   - name: Find aliases whose target dataset resides on specific volumes
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - alias
       volumes:
         - VOL001
         - VOL002

   - name: Find aliases whose target dataset was created within the last 30 days
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - alias
       age: -30d
       age_stamp: creation_date

   - name: Find aliases whose target dataset is larger than 1MB
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - alias
       size: 1m

   - name: Find aliases whose target dataset contains the string 'hello'
     zos_find:
       patterns:
         - USER.*
       resource_type:
         - alias
       contains: 'hello'




Notes
-----

.. note::
   Only cataloged data sets will be searched. If an uncataloged data set needs to be searched, it should be cataloged first. The `zos_data_set <./zos_data_set.html>`_ module can be used to catalog uncataloged data sets.

   The `zos_find <./zos_find.html>`_ module currently does not support wildcards for high level qualifiers. For example, ``SOME.*.DATA.SET`` is a valid pattern, but ``*.DATA.SET`` is not.

   If a data set pattern is specified as ``USER.*``, the matching data sets will have two name segments such as ``USER.ABC``, ``USER.XYZ`` etc. If a wildcard is specified as ``USER.*.ABC``, the matching data sets will have three name segments such as ``USER.XYZ.ABC``, ``USER.TEST.ABC`` etc.

   The time taken to execute the module is proportional to the number of data sets present on the system and how large the data sets are.

   When searching for content within data sets, only non-binary content is considered.

   As a migrated data set's information can't be retrieved without recalling it first, other options besides ``excludes`` and ``migrated_type`` are not supported.

   When using ``resource_type=alias``, the ``contains`` option searches the content of the target dataset (``alias_of``). Only alias entries whose target dataset contains the specified string are returned. The ``age``, ``age_stamp``, ``size``, and ``volume`` options are also supported and are applied against the target dataset.

   Parenthesised exclude patterns (e.g. ``(^MEM1$``)) match against PDS/PDSE member names. Members whose name matches the pattern are removed from the ``members`` list of the matched data set or alias entry. The data set or alias entry itself is kept, even if all its members are removed.

   PDS/PDSE entries always include a ``members`` key, which is an empty list when the data set has no members (or all of them were excluded). For ``alias`` entries, ``members`` is a list of dicts with the member name and its in-directory alias names, whereas for ``nonvsam`` entries ``members`` is a list of member name strings.



See Also
--------

.. seealso::

   - :ref:`ibm.ibm_zos_core.zos_data_set_module`




Return Values
-------------


data_sets
  All matches found with the specified criteria.

  For ``alias`` resource types, each entry includes an ``alias_of`` field containing the real dataset name the alias points to.

  PDS/PDSE entries always include a ``members`` list, which is empty when the data set has no members. For ``alias`` entries pointing to a PDS/PDSE, each item is a dict with a ``name`` key (the member name) and an ``aliases`` key (a list of alias names for that member, empty when the member has none). Note that for ``alias`` entries ``members`` is a list of dicts, whereas for ``nonvsam`` entries ``members`` is a list of member name strings.

  | **returned**: success
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            {
                "members": [
                    "COBU",
                    "MC2CNAM",
                    "TINAD"
                ],
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
            },
            {
                "alias_of": "USER.REAL.DATASET",
                "name": "USER.ALIAS.NAME",
                "type": "ALIAS"
            },
            {
                "alias_of": "USER.REAL.PDS",
                "members": [
                    {
                        "aliases": [
                            "ALIAS1",
                            "ALIAS2"
                        ],
                        "name": "MEM1"
                    },
                    {
                        "aliases": [
                            "ALIAS3"
                        ],
                        "name": "MEM2"
                    },
                    {
                        "aliases": [],
                        "name": "MEM3"
                    }
                ],
                "name": "USER.PDS.ALIAS",
                "type": "ALIAS"
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

