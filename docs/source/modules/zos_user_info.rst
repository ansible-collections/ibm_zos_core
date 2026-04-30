
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user_info.py

.. _zos_user_info_module:


zos_user_info -- Retrieve user and group profile information from RACF
======================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The \ `zos\_user\_info <./zos_user_info.html>`__ module retrieves detailed information about RACF user and group profiles.
- The module executes RACF LISTUSER or LISTGRP TSO commands and parses the output into structured data.
- This is an info module that does not make any changes to the system.





Parameters
----------


name
  Name of the RACF profile to retrieve information about.

  Can be a user ID or group name depending on the :emphasis:`scope` parameter.

  | **required**: True
  | **type**: str


scope
  Whether to retrieve information about a user or a group profile.

  | **required**: True
  | **type**: str
  | **choices**: user, group


segments
  List of segments to retrieve from the profile.

  If not specified, only base profile information is retrieved.

  For users, valid segments are :literal:`dfp`\ , :literal:`tso`\ , :literal:`omvs`\ , :literal:`operparm`\ , :literal:`lang`\ , :literal:`csdata`.

  For groups, valid segments are :literal:`dfp`\ , :literal:`omvs`\ , :literal:`csdata`.

  :literal:`General` information is always retrieved.

  Invalid segments for the specified scope will be ignored.

  | **required**: False
  | **type**: list
  | **elements**: str
  | **choices**: dfp, tso, omvs, operparm, lang, csdata






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Get basic user profile info
     ibm.ibm_zos_core.zos_user_info:
       name: TESTU01
       scope: user

   - name: Get user profile info with segments
     ibm.ibm_zos_core.zos_user_info:
       name: TESTU01
       scope: user
       segments:
         - dfp
         - tso
         - omvs
         - operparm
         - lang
         - csdata

   - name: Get basic group profile info
     ibm.ibm_zos_core.zos_user_info:
       name: TSTGRP01
       scope: group

   - name: Get group profile info with DFP and OMVS segments
     ibm.ibm_zos_core.zos_user_info:
       name: TSTGRP01
       scope: group
       segments:
         - dfp
         - omvs










Return Values
-------------


cmd
  The TSO command that was executed.

  | **returned**: always
  | **type**: str
  | **sample**: LU TESTU01 TSO OMVS

profile
  Dictionary containing the RACF profile information organized by segments.

  Always includes base profile information (\ :literal:`general` and :literal:`group`\ /\ :literal:`users` sections).

  Additional segments are only included if explicitly requested via the :emphasis:`segments` parameter.

  Each segment is a dictionary with key\-value pairs extracted from RACF output.

  The keys and values within each segment are dynamic and depend on what RACF returns.

  Empty segments (where RACF returns "NO [SEGMENT] INFORMATION") will be empty dictionaries.

  | **returned**: success
  | **type**: dict

  general
    Base profile information that is always returned.

    For user profiles, contains attributes like USER\-ID, NAME, DEFAULT\-GROUP, OWNER, CREATED, PASSDATE, PASS\-INTERVAL, ATTRIBUTES, etc.

    For group profiles, contains attributes like OWNER, CREATED, SUPERIOR GROUP, INSTALLATION DATA, SUBGROUP(S), TERMUACC, UNIVERSAL, etc.

    The exact keys present are dynamic and depend on the profile configuration.

    Some fields like ATTRIBUTES and CLASS AUTHORIZATIONS are returned as lists when they contain multiple values.

    | **returned**: always
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ATTRIBUTES": [
                  "SPECIAL",
                  "OPERATIONS"
              ],
              "CREATED": "2025/01/10",
              "DEFAULT-GROUP": "TSTGRP01",
              "NAME": "TEST USER 01",
              "OWNER": "ADMIN01",
              "PASS-INTERVAL": "90",
              "PASSDATE": "2026/04/15",
              "USER-ID": "TESTU01"
          }

  group
    Group connection information for user profiles.

    Dictionary where each key is a group name and the value contains connection attributes.

    Contains attributes like AUTH, CONNECT\-OWNER, CONNECT\-DATE, LAST\-CONNECT, REVOKE DATE, RESUME DATE, CONNECT ATTRIBUTES, etc.

    Only returned when scope is :literal:`user`.

    | **returned**: when scope is user
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "SYSADM": {
                  "AUTH": "JOIN",
                  "CONNECT-DATE": "2025/02/15",
                  "CONNECT-OWNER": "ADMIN01"
              },
              "TSTGRP01": {
                  "AUTH": "USE",
                  "CONNECT-DATE": "2025/01/10",
                  "CONNECT-OWNER": "ADMIN01",
                  "LAST-CONNECT": "2026/04/29",
                  "RESUME DATE": "NONE",
                  "REVOKE DATE": "NONE"
              }
          }

  users
    Connected user information for group profiles.

    Dictionary where each key is a username and the value contains connection attributes.

    Contains attributes like ACCESS, ACCESS COUNT, UNIVERSAL ACCESS, REVOKE DATE, RESUME DATE, CONNECT ATTRIBUTES, etc.

    Only returned when scope is :literal:`group`.

    | **returned**: when scope is group
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "TESTU01": {
                  "ACCESS": "JOIN",
                  "ACCESS COUNT": "000047",
                  "RESUME DATE": "NONE",
                  "REVOKE DATE": "NONE",
                  "UNIVERSAL ACCESS": "READ"
              },
              "TESTU02": {
                  "ACCESS": "USE",
                  "ACCESS COUNT": "000012",
                  "UNIVERSAL ACCESS": "NONE"
              }
          }

  TSO
    TSO segment information (user profiles only).

    Contains dynamic key\-value pairs such as ACCTNUM, PROC, SIZE, MAXSIZE, JOBCLASS, MSGCLASS, etc.

    The exact keys present depend on the user's TSO configuration.

    Only returned when :literal:`tso` is included in the :emphasis:`segments` parameter.

    | **returned**: when scope is user and tso segment is requested
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ACCTNUM": "33000",
              "COMMAND": "ISPF PANEL(ISR@390)",
              "HOLDCLASS": "H",
              "JOBCLASS": "A",
              "MAXSIZE": "00032768",
              "MSGCLASS": "X",
              "PROC": "IKJACCNT",
              "SIZE": "00016384",
              "SYSOUTCLASS": "A",
              "USERDATA": "E4F1"
          }

  OMVS
    OMVS segment information (user and group profiles).

    Contains dynamic key\-value pairs such as UID, HOME, PROGRAM, CPUTIMEMAX, ASSIZEMAX, etc.

    The exact keys present depend on the OMVS configuration.

    Only returned when :literal:`omvs` is included in the :emphasis:`segments` parameter.

    | **returned**: when omvs segment is requested
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ASSIZEMAX": "NONE",
              "CPUTIMEMAX": "NONE",
              "HOME": "/u/testu01",
              "PROGRAM": "/bin/sh",
              "UID": "0000000201"
          }

  DFP
    DFP (Data Facility Product) segment information.

    Contains dynamic key\-value pairs related to data management such as MGMTCLAS, STORCLAS, DATACLAS, etc.

    The exact keys present depend on the DFP configuration.

    Only returned when :literal:`dfp` is included in the :emphasis:`segments` parameter.

    | **returned**: when dfp segment is requested
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "DATACLAS": "DCEXTL",
              "MGMTCLAS": "STANDARD",
              "STORCLAS": "SCPERM"
          }

  OPERPARM
    OPERPARM segment information (user profiles only).

    Contains operator parameters such as STORAGE, AUTH, ALTGRP, AUTO, HC, INTIDS, LEVEL, etc.

    Some fields like MONITOR, MSCOPE, ROUTCODE are returned as lists when they contain multiple values.

    The exact keys present depend on the operator configuration.

    Only returned when :literal:`operparm` is included in the :emphasis:`segments` parameter.

    | **returned**: when scope is user and operparm segment is requested
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ALTGRP": "YES",
              "AUTO": "NO",
              "HC": "NO",
              "INTIDS": "NO",
              "LEVEL": "00",
              "LOGCMDRESP": "NO",
              "MIGID": "NO",
              "MONITOR": [
                  "JOBNAMES",
                  "SESS",
                  "STATUS"
              ],
              "MSCOPE": [
                  "ALL"
              ],
              "ROUTCODE": [
                  "1:2",
                  "11"
              ],
              "STORAGE": "YES"
          }

  LANGUAGE
    LANGUAGE segment information (user profiles only).

    Contains language\-related settings such as PRIMARY and SECONDARY language codes.

    The exact keys present depend on the language configuration.

    Only returned when :literal:`lang` is included in the :emphasis:`segments` parameter.

    | **returned**: when scope is user and lang segment is requested
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "PRIMARY": "ENU",
              "SECONDARY": "JPN"
          }

  CSDATA
    CSDATA (Custom Data) segment information.

    Contains custom application\-specific data.

    The exact keys present depend on what custom data has been defined.

    Only returned when :literal:`csdata` is included in the :emphasis:`segments` parameter.

    | **returned**: when csdata segment is requested
    | **type**: dict


changed
  Indicates if any changes were made (always false for info modules).

  | **returned**: always
  | **type**: bool

rc
  Return code from the TSO command.

  Returns 0 on success.

  Returns non\-zero on failure (e.g., 8 when profile not found).

  | **returned**: always
  | **type**: int

msg
  Error message describing the failure reason.

  Only present when the module fails.

  | **returned**: failure
  | **type**: str
  | **sample**: Profile 'TESTU01' not found in RACF database

stdout
  Standard output from the TSO command.

  Only present when the module fails.

  | **returned**: failure
  | **type**: str
  | **sample**: NAME NOT FOUND IN RACF DATA SET

stderr
  Standard error from the TSO command.

  Only present when the module fails.

  | **returned**: failure
  | **type**: str

