
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_tso_command.py

.. _zos_tso_command_module:


zos_tso_command -- Execute TSO commands
=======================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Execute TSO commands on the target z/OS system with the provided options and receive a structured response.





Parameters
----------


commands
  One or more TSO commands to execute on the target z/OS system.

  Accepts a single string or list of strings as input.

  If a list of strings is provided, processing will stop at the first failure, based on rc.

  | **required**: True
  | **type**: raw


max_rc
  Specifies the maximum return code allowed for a TSO command.

  If more than one TSO command is submitted, the *max_rc* applies to all TSO commands.

  | **required**: False
  | **type**: int
  | **default**: 0




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Execute TSO commands to allocate a new dataset.
     zos_tso_command:
       commands:
         - alloc da('TEST.HILL3.TEST') like('TEST.HILL3')
         - delete 'TEST.HILL3.TEST'

   - name: Execute TSO command List User (LU) for TESTUSER to obtain TSO information.
     zos_tso_command:
       commands:
         - LU TESTUSER

   - name: Execute TSO command List Dataset (LISTDSD) and allow for maximum return code of 4.
     zos_tso_command:
       commands:
         - LISTDSD DATASET('HLQ.DATA.SET') ALL GENERIC
       max_rc: 4

   - name: Execute TSO command to run a REXX script explicitly from a data set.
     zos_tso_command:
       commands:
         - EXEC HLQ.DATASET.REXX exec

   - name: Chain multiple TSO commands into one invocation using semicolons.
     zos_tso_command:
       commands: >-
         ALLOCATE DDNAME(IN1) DSNAME('HLQ.PDSE.DATA.SRC(INPUT)') SHR;
         ALLOCATE DDNAME(OUT1) DSNAME('HLQ.PDSE.DATA.DEST(OUTPUT)') SHR;
         OCOPY INDD(IN1) OUTDD(OUT1) BINARY;










Return Values
-------------


output
  List of each TSO command output.

  | **returned**: always
  | **type**: list
  | **elements**: dict

  command
    The executed TSO command.

    | **returned**: always
    | **type**: str

  rc
    The return code from the executed TSO command.

    | **returned**: always
    | **type**: int

  max_rc
    Specifies the maximum return code allowed for a TSO command.

    If more than one TSO command is submitted, the *max_rc* applies to all TSO commands.

    | **returned**: always
    | **type**: int

  content
    The response resulting from the execution of the TSO command.

    | **returned**: always
    | **type**: list
    | **sample**:

      .. code-block:: json

          [
              "NO MODEL DATA SET                                                OMVSADM",
              "TERMUACC                                                                ",
              "SUBGROUP(S)= VSAMDSET SYSCTLG  BATCH    SASS     MASS     IMSGRP1       ",
              "             IMSGRP2  IMSGRP3  DSNCAT   DSN120   J42      M63           ",
              "             J91      J09      J97      J93      M82      D67           ",
              "             D52      M12      CCG      D17      M32      IMSVS         ",
              "             DSN210   DSN130   RAD      CATLG4   VCAT     CSP           "
          ]

  lines
    The line number of the content.

    | **returned**: always
    | **type**: int


