
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_user_info.py

.. _ibm.ibm_zos_core.zos_user_info_module:


zos_user_info -- Retrieve user and group profile information from RACF
======================================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Retrieve detailed information about RACF user and group profiles.
- The module runs the RACF LISTUSER or LISTGRP TSO commands and parses the output into structured data.
- This module does not make any changes to the system.





Parameters
----------


name
  The RACF profile name to retrieve.

  For :emphasis:`profile\_type=user`\ , this must be a single user ID.

  For :emphasis:`profile\_type=group`\ , this must be a single group name.

  The name is case\-insensitive and is normalized to uppercase before execution.

  The name is a single continuous string with no spaces or blank characters.

  | **required**: True
  | **type**: str


profile_type
  Specifies the type of RACF profile to retrieve information about.

  When :emphasis:`profile\_type=user`\ , retrieves user profile information using the LISTUSER command.

  When :emphasis:`profile\_type=group`\ , retrieves group profile information using the LISTGRP command.

  | **required**: True
  | **type**: str
  | **choices**: user, group


segments
  List of RACF segments to retrieve from the profile.

  If not specified, only the base profile information (\ :literal:`base\_segment`\ ) is retrieved.

  When :emphasis:`profile\_type=user`\ , valid segments are :literal:`dfp`\ , :literal:`tso`\ , :literal:`omvs`\ , :literal:`operparm`\ , :literal:`lang`\ , :literal:`csdata`\ , :literal:`cics`\ , :literal:`dce`\ , :literal:`eim`\ , :literal:`ovm`\ , :literal:`netview`\ , :literal:`nds`\ , :literal:`lnotes`\ , :literal:`workattr`\ , :literal:`proxy`\ , and :literal:`kerb`.

  When :emphasis:`profile\_type=group`\ , valid segments are :literal:`dfp`\ , :literal:`omvs`\ , :literal:`ovm`\ , and :literal:`csdata`.

  The :literal:`base\_segment` section is always retrieved regardless of this parameter.

  Segments that do not apply to the requested :emphasis:`profile\_type` are ignored.

  For example, user\-only segments are ignored for group profiles.

  | **required**: False
  | **type**: list
  | **elements**: str
  | **choices**: dfp, tso, omvs, operparm, lang, csdata, cics, dce, eim, ovm, netview, nds, lnotes, workattr, proxy, kerb






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Get basic user profile information
     ibm.ibm_zos_core.zos_user_info:
       name: TESTU01
       profile_type: user

   - name: Get user profile information with TSO and OMVS segment
     ibm.ibm_zos_core.zos_user_info:
       name: "TESTU01"
       profile_type: user
       segments:
         - tso
         - omvs

   - name: Get user profile with multiple segments
     ibm.ibm_zos_core.zos_user_info:
       name: "TESTU01"
       profile_type: user
       segments:
         - tso
         - omvs
         - dfp
         - lang
         - operparm

   - name: Get user profile with all segments
     ibm.ibm_zos_core.zos_user_info:
       name: TESTU01
       profile_type: user
       segments:
         - dfp
         - tso
         - omvs
         - operparm
         - lang
         - csdata
         - cics
         - dce
         - eim
         - ovm
         - netview
         - nds
         - lnotes
         - workattr
         - proxy
         - kerb

   - name: Get basic group profile information
     ibm.ibm_zos_core.zos_user_info:
       name: TSTGRP01
       profile_type: group

   - name: Get group profile with multiple segments
     ibm.ibm_zos_core.zos_user_info:
       name: TSTGRP01
       profile_type: group
       segments:
         - dfp
         - omvs
         - ovm
         - csdata










Return Values
-------------


changed
  Indicates whether any changes were made to the system. Always :literal:`false` for info modules.

  | **returned**: always
  | **type**: bool

cmd
  The RACF command that was run with the tsocmd command.

  | **returned**: always
  | **type**: str
  | **sample**: LISTUSER TESTU01 TSO OMVS

rc
  Return code from the RACF command execution. Returns 0 on success, or a non\-zero value on failure (for example, 8 when the profile is not found).

  | **returned**: always
  | **type**: int

stdout
  Standard output from the RACF command execution.

  | **returned**: always
  | **type**: str
  | **sample**: USER=TESTU01  NAME=TEST USER 01  OWNER=ADMIN01  CREATED=2025/01/10

stderr
  Standard error from the RACF command execution. The TSO command itself is not included; it is available in the :literal:`cmd` field.

  | **returned**: always
  | **type**: str

msg
  Error message describing the failure.

  | **returned**: failure
  | **type**: str
  | **sample**: Profile 'TESTU01' not found in RACF database

segments
  Dictionary of RACF profile information organized by segment.

  Always includes :literal:`base\_segment` and :literal:`group` or :literal:`users`. Additional segments are only present if specified in the :emphasis:`segments` option.

  Keys and values are dynamic based on RACF output. Segments with no data are returned as empty dictionaries.

  | **returned**: success
  | **type**: dict

  base_segment
    Base profile information, always returned regardless of the :emphasis:`segments` parameter.

    When :emphasis:`profile\_type=user`\ , contains user attributes such as :literal:`USER\-ID`\ , :literal:`NAME`\ , :literal:`DEFAULT\-GROUP`\ , :literal:`OWNER`\ , :literal:`CREATED`\ , :literal:`PASSDATE`\ , :literal:`PASS\-INTERVAL`\ , and :literal:`ATTRIBUTES`.

    When :emphasis:`profile\_type=group`\ , contains group attributes such as :literal:`OWNER`\ , :literal:`CREATED`\ , :literal:`SUPERIOR GROUP`\ , :literal:`INSTALLATION DATA`\ , :literal:`SUBGROUP(S`\ ), :literal:`TERMUACC`\ , and :literal:`UNIVERSAL`.

    The exact keys present depend on the profile's RACF configuration.

    :literal:`ATTRIBUTES` and :literal:`CLASS AUTHORIZATIONS` are always returned as lists.

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
              "USER": "TESTU01"
          }

  group
    Group connection information for user profiles, keyed by group name.

    Each value contains connection attributes such as :literal:`AUTH`\ , :literal:`CONNECT\-OWNER`\ , :literal:`CONNECT\-DATE`\ , :literal:`LAST\-CONNECT`\ , :literal:`REVOKE DATE`\ , :literal:`RESUME DATE`\ , and :literal:`CONNECT ATTRIBUTES`.

    Only returned when :emphasis:`profile\_type=user`.

    | **returned**: when profile_type=user
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "TSTGRP01": {
                  "CONNECT-DATE": "2025/01/10",
                  "CONNECT-OWNER": "ADMIN01",
                  "LAST-CONNECT": "2026/04/29",
                  "RESUME DATE": "NONE",
                  "REVOKE DATE": "NONE"
              }
          }

  users
    Connected user information for group profiles, keyed by username.

    Each value contains connection attributes such as :literal:`ACCESS`\ , :literal:`ACCESS COUNT`\ , :literal:`UNIVERSAL ACCESS`\ , :literal:`REVOKE DATE`\ , :literal:`RESUME DATE`\ , and :literal:`CONNECT ATTRIBUTES`.

    Only returned when :emphasis:`profile\_type=group`.

    | **returned**: when profile_type=group
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
    TSO segment information for user profiles.

    Contains dynamic key\-value pairs such as :literal:`ACCTNUM`\ , :literal:`PROC`\ , :literal:`SIZE`\ , :literal:`MAXSIZE`\ , :literal:`JOBCLASS`\ , :literal:`MSGCLASS`\ , :literal:`SYSOUTCLASS`\ , :literal:`USERDATA`\ , :literal:`COMMAND`\ , etc.

    The exact keys present depend on the user's TSO configuration in RACF.

    Only returned when :emphasis:`profile\_type=user` and :literal:`tso` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies tso
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ACCTNUM": "33000",
              "HOLDCLASS": "H",
              "JOBCLASS": "A",
              "MSGCLASS": "X"
          }

  OMVS
    OMVS segment information for user and group profiles.

    Contains dynamic key\-value pairs such as :literal:`UID`\ , :literal:`HOME`\ , :literal:`PROGRAM`\ , :literal:`CPUTIMEMAX`\ , :literal:`ASSIZEMAX`\ , :literal:`FILEPROCMAX`\ , :literal:`PROCUSERMAX`\ , etc.

    The exact keys present depend on the OMVS configuration in RACF.

    Only returned when :literal:`omvs` is included in the :emphasis:`segments` parameter.

    | **returned**: when segments specifies omvs
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
    DFP (Data Facility Product) segment information for user and group profiles.

    Contains dynamic key\-value pairs related to data management such as :literal:`MGMTCLAS`\ , :literal:`STORCLAS`\ , :literal:`DATACLAS`\ , etc.

    The exact keys present depend on the DFP configuration in RACF.

    Only returned when :literal:`dfp` is included in the :emphasis:`segments` parameter.

    | **returned**: when segments specifies dfp
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "DATACLAS": "DCEXTL",
              "MGMTCLAS": "STANDARD",
              "STORCLAS": "SCPERM"
          }

  OPERPARM
    OPERPARM segment information for user profiles.

    Contains operator parameters such as :literal:`STORAGE`\ , :literal:`AUTH`\ , :literal:`ALTGRP`\ , :literal:`AUTO`\ , :literal:`HC`\ , :literal:`INTIDS`\ , :literal:`LEVEL`\ , :literal:`LOGCMDRESP`\ , :literal:`MIGID`\ , etc.

    :literal:`MONITOR`\ , :literal:`MSCOPE`\ , :literal:`MFORM`\ , and :literal:`ROUTCODE` are always returned as lists.

    The exact keys present depend on the operator configuration in RACF.

    Only returned when :emphasis:`profile\_type=user` and :literal:`operparm` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies operparm
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ALTGRP": "YES",
              "MFORM": [
                  "M",
                  "T"
              ],
              "MIGID": "NO",
              "MONITOR": [
                  "JOBNAMES",
                  "SESS"
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
    LANGUAGE segment information for user profiles.

    Contains language\-related settings such as :literal:`PRIMARY` and :literal:`SECONDARY` language codes.

    The exact keys present depend on the language configuration in RACF.

    Only returned when :emphasis:`profile\_type=user` and :literal:`lang` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies lang
    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "PRIMARY LANGUAGE": "ENU",
              "SECONDARY LANGUAGE": "JPN"
          }

  CSDATA
    CSDATA (Custom Data) segment information for user and group profiles.

    Contains custom application\-specific data defined in RACF.

    The exact keys present depend on what custom data has been configured for the profile.

    Only returned when :literal:`csdata` is included in the :emphasis:`segments` parameter.

    | **returned**: when segments specifies csdata
    | **type**: dict

  CICS
    CICS segment information for user profiles.

    Contains CICS\-related configuration and resource limits.

    Only returned when :emphasis:`profile\_type=user` and :literal:`cics` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies cics
    | **type**: dict

  DCE
    DCE (Distributed Computing Environment) segment information for user profiles.

    Contains DCE\-related configuration and identifiers.

    Only returned when :emphasis:`profile\_type=user` and :literal:`dce` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies dce
    | **type**: dict

  EIM
    EIM (Enterprise Identity Mapping) segment information for user profiles.

    Contains EIM\-related configuration and mappings.

    Only returned when :emphasis:`profile\_type=user` and :literal:`eim` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies eim
    | **type**: dict

  OVM
    OVM (OpenExtensions VM) segment information for user and group profiles.

    Contains OVM\-related configuration and settings.

    Only returned when :literal:`ovm` is included in the :emphasis:`segments` parameter.

    | **returned**: when segments specifies ovm
    | **type**: dict

  NETVIEW
    NETVIEW segment information for user profiles.

    Contains NetView\-related configuration and authorities.

    Only returned when :emphasis:`profile\_type=user` and :literal:`netview` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies netview
    | **type**: dict

  NDS
    NDS (Network Directory Services) segment information for user profiles.

    Contains NDS\-related configuration and identifiers.

    Only returned when :emphasis:`profile\_type=user` and :literal:`nds` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies nds
    | **type**: dict

  LNOTES
    LNOTES (Lotus Notes) segment information for user profiles.

    Contains Lotus Notes\-related configuration and settings.

    Only returned when :emphasis:`profile\_type=user` and :literal:`lnotes` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies lnotes
    | **type**: dict

  WORKATTR
    WORKATTR (Work Attributes) segment information for user profiles.

    Contains work\-related attributes and organizational information.

    Only returned when :emphasis:`profile\_type=user` and :literal:`workattr` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies workattr
    | **type**: dict

  PROXY
    PROXY segment information for user profiles.

    Contains proxy\-related configuration and authorities.

    Only returned when :emphasis:`profile\_type=user` and :literal:`proxy` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies proxy
    | **type**: dict

  KERB
    KERB (Kerberos) segment information for user profiles.

    Contains Kerberos\-related configuration, principals, and encryption settings.

    Only returned when :emphasis:`profile\_type=user` and :literal:`kerb` is included in the :emphasis:`segments` parameter.

    | **returned**: when profile_type is user and segments specifies kerb
    | **type**: dict


