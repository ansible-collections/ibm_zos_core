
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
  The command to execute.  This command will be wrapped in quotations to run.

  If the command contains single-quotations, another set of single quotes must be added.

  For example, Change the command "...,P='DSN3EPX,-DBC1,S'" to "...,P=''DSN3EPX,-DBC1,S'' ".

  | **required**: True
  | **type**: str


verbose
  Return diagnostic messages that lists and describes the execution of the operator commands.

  Return security trace messages that help you understand and diagnose the execution of the operator commands

  Return trace instructions displaying how the the command's operation is read, evaluated and executed.

  | **required**: False
  | **type**: bool


wait_time_s
  Set maximum time in seconds to wait for the commands to execute.

  When set to 0, the system default is used.

  This option is helpful on a busy system requiring more time to execute commands.

  Setting *wait* can instruct if execution should wait the full *wait_time_s*.

  | **required**: False
  | **type**: int


wait
  Specify to wait the full *wait_time_s* interval before retrieving responses.

  This option is recommended to ensure that the responses are accessible and captured by logging facilities and the *verbose* option.

  *delay=True* waits the full *wait_time_s* interval.

  *delay=False* returns as soon as the first command executes.

  | **required**: False
  | **type**: bool
  | **default**: True




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Execute an operator command to show active jobs
     zos_operator:
       cmd: 'd u,all'

   - name: Execute an operator command to show active jobs with verbose information
     zos_operator:
       cmd: 'd u,all'
       verbose: true

   - name: Execute an operator command to purge all job logs (requires escaping)
     zos_operator:
       cmd: "\\$PJ(*)"

   - name: Execute operator command to show jobs, waiting up to 5 seconds for response
     zos_operator:
       cmd: 'd u,all'
       wait_time_s: 5
       wait: false

   - name: Execute operator command to show jobs, always waiting 7 seconds for response
     zos_operator:
       cmd: 'd u,all'
       wait_time_s: 7
       wait: true










Return Values
-------------


rc
  Return code of the operator command

  | **returned**: always
  | **type**: int

content
  The text from the command issued, plus verbose messages if *verbose=True*

  | **returned**: on success
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "MV2C      2020039  04:29:57.58             ISF031I CONSOLE XIAOPIN ACTIVATED ",
            "MV2C      2020039  04:29:57.58            -D U,ALL                           ",
            "MV2C      2020039  04:29:57.59             IEE457I 04.29.57 UNIT STATUS 948  ",
            "         UNIT TYPE STATUS        VOLSER     VOLSTATE      SS                 ",
            "          0100 3277 OFFLINE                                 0                ",
            "          0101 3277 OFFLINE                                 0                ",
            "ISF050I USER=OMVSADM GROUP= PROC=REXX TERMINAL=09A3233B",
            "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=GROUP.ISFSPROG.SDSF",
            "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.FILTER.PREFIX",
            "ISF055I ACTION=D Access allowed USERLEVEL=7 REQLEVEL=1",
            "ISF051I SAF Access allowed SAFRC=0 ACCESS=READ CLASS=SDSF RESOURCE=ISFCMD.ODSP.ULOG.JES2",
            "ISF147I REXX variable ISFTIMEOUT fetched, return code 00000001 value is \u0027\u0027.",
            "ISF754I Command \u0027SET DELAY 5\u0027 generated from associated variable ISFDELAY.",
            "ISF769I System command issued, command text: D U,ALL -S.",
            "ISF146I REXX variable ISFDIAG set, return code 00000001 value is \u002700000000 00000000 00000000 00000000 00000000\u0027.",
            "ISF766I Request completed, status: COMMAND ISSUED."
        ]

changed
  Indicates if any changes were made during module operation. Given operator commands may introduce changes that are unknown to the module. True is always returned unless either a module or command failure has occurred.

  | **returned**: always
  | **type**: bool
  | **sample**:

    .. code-block:: json

        true

