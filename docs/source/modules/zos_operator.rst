
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_operator.py

.. _zos_operator_module:


zos_operator -- Execute operator command
========================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Execute an operator command and receive the output.





Parameters
----------


cmd
  The command to execute.

  If the command contains single-quotations, another set of single quotes must be added.

  For example, change the command "...,P='DSN3EPX,-DBC1,S'" to "...,P=''DSN3EPX,-DBC1,S'' ".

  If the command contains any special characters ($, &, etc), they must be escaped using double backslashes like \\\\\\$.

  For example, to display job by job name the command would be ``cmd:"\\$dj''HELLO''"``

  By default, the command will be converted to uppercase before execution, to control this behavior, see the *case_sensitive* option below.

  | **required**: True
  | **type**: str


verbose
  Return diagnostic messages that describes the commands execution, options, buffer and response size.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_time_s
  Set maximum time in seconds to wait for the commands to execute.

  When set to 0, the system default is used.

  This option is helpful on a busy system requiring more time to execute commands.

  Setting *wait* can instruct if execution should wait the full *wait_time_s*.

  | **required**: False
  | **type**: int
  | **default**: 1


case_sensitive
  If ``true``, the command will not be converted to uppercase before execution. Instead, the casing will be preserved just as it was written in a task.

  | **required**: False
  | **type**: bool
  | **default**: False




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

   
   - name: Execute an operator command to show device status and allocation
     zos_operator:
       cmd: 'd u'

   - name: Execute an operator command to show device status and allocation with verbose information
     zos_operator:
       cmd: 'd u'
       verbose: true

   - name: Execute an operator command to purge all job logs (requires escaping)
     zos_operator:
       cmd: "\\$PJ(*)"

   - name: Execute operator command to show jobs, always waiting 5 seconds for response
     zos_operator:
       cmd: 'd a,all'
       wait_time_s: 5

   - name: Display the system symbols and associated substitution texts.
     zos_operator:
       cmd: 'D SYMBOLS'




Notes
-----

.. note::
   Commands may need to use specific prefixes like $, they can be discovered by issuing the following command ``D OPDATA,PREFIX``.







Return Values
-------------


rc
  Return code for the submitted operator command.

  | **returned**: always
  | **type**: int

cmd
  Operator command submitted.

  | **returned**: always
  | **type**: str
  | **sample**: d u,all

elapsed
  The number of seconds that elapsed waiting for the command to complete.

  | **returned**: always
  | **type**: float
  | **sample**:

    .. code-block:: json

        51.53

wait_time_s
  The maximum time in seconds to wait for the commands to execute.

  | **returned**: always
  | **type**: int
  | **sample**: 5

content
  The resulting text from the command submitted.

  | **returned**: on success
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "EC33017A   2022244  16:00:49.00             ISF031I CONSOLE OMVS0000 ACTIVATED",
            "EC33017A   2022244  16:00:49.00            -D U,ALL ",
            "EC33017A   2022244  16:00:49.00             IEE457I 16.00.49 UNIT STATUS 645",
            "                                           UNIT TYPE STATUS        VOLSER     VOLSTATE      SS",
            "                                           0000 3390 F-NRD                        /RSDNT     0",
            "                                           0001 3211 OFFLINE                                 0",
            "                                           0002 3211 OFFLINE                                 0",
            "                                           0003 3211 OFFLINE                                 0",
            "                                           0004 3211 OFFLINE                                 0",
            "                                           0005 3211 OFFLINE                                 0",
            "                                           0006 3211 OFFLINE                                 0",
            "                                           0007 3211 OFFLINE                                 0",
            "                                           0008 3211 OFFLINE                                 0",
            "                                           0009 3277 OFFLINE                                 0",
            "                                           000C 2540 A                                       0",
            "                                           000D 2540 A                                       0",
            "                                           000E 1403 A                                       0",
            "                                           000F 1403 A                                       0",
            "                                           0010 3211 A                                       0",
            "                                           0011 3211 A                                       0"
        ]

changed
  Indicates if any changes were made during module operation. Given operator commands may introduce changes that are unknown to the module. True is always returned unless either a module or command failure has occurred.

  | **returned**: always
  | **type**: bool
  | **sample**:

    .. code-block:: json

        true

