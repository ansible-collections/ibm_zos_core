
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_started_task.py

.. _zos_started_task_module:


zos_started_task -- Perform operations on started tasks.
========================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- start, display, modify, cancel, force and stop a started task





Parameters
----------


start_task
  Defines options for starting a task.

  | **required**: False
  | **type**: dict


  job_name
    When ``state=started`` **job_name** is a name which should be assigned to a started task while starting it. If job_name is not specified, then member_name is used as job_name.

    | **required**: False
    | **type**: str


  identifier_name
    Option ``identifier_name`` is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

    | **required**: False
    | **type**: str


  device_type
    Option ``device_type`` is the type of the output device (if any) associated with the task.

    Only applicable when ``state=started`` otherwise ignored.

    | **required**: False
    | **type**: str


  device_number
    Option ``device_number`` is the number of the device to be started. A device number is 3 or 4 hexadecimal digits. A slash (/) must precede a 4-digit number but is not before a 3-digit number.

    Only applicable when ``state=started`` otherwise ignored.

    | **required**: False
    | **type**: str


  job_account
    Option ``job_account`` specifies accounting data in the JCL JOB statement for the started task. If the source JCL was a job and has already accounting data, the value that is specified on this parameter overrides the accounting data in the source JCL.

    | **required**: False
    | **type**: str


  keyword_parameters
    Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure. The maximum length of each keyword=option is 66 characters. No individual value within this field can be longer than 44 characters in length.

    Only applicable when ``state=started`` otherwise ignored.

    | **required**: False
    | **type**: str


  member_name
    Option ``member_name`` is a 1 - 8 character name of a member of a partitioned data set that contains the source JCL for the task to be started. The member can be either a job or a cataloged procedure.

    Only applicable when ``state=started`` otherwise ignored.

    | **required**: False
    | **type**: str


  parameters
    Program parameters passed to the started program, which might be a list in parentheses or a string in single quotation marks

    | **required**: False
    | **type**: str


  reuse_asid
    When REUSASID=YES is specified on the START command and REUSASID(YES) is specified in the DIAGxx parmlib member, a reusable ASID is assigned to the address space created by the START command. If REUSASID=YES is not specified on the START command or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.

    | **required**: False
    | **type**: str
    | **choices**: YES, NO


  subsystem
    The name of the subsystem that selects the task for processing. The name must be 1 - 4 characters, which are defined in the IEFSSNxx parmlib member, and the subsystem must be active.

    | **required**: False
    | **type**: str


  volume
    If devicetype is a tape or direct-access device, the volume serial number of the volume is mounted on the device.

    Only applicable when ``state=started`` otherwise ignored.

    | **required**: False
    | **type**: str



cancel_task
  Defines options for canceling a task.

  | **required**: False
  | **type**: dict


  asid
    When ``state`` is ``cancelled``, ``cancelled`` or ``stopped`` **asid**. is the hexadecimal address space identifier of the work unit you want to cancel, stop or force.

    When ``state=displayed`` **asid** is the hexadecimal address space identifier of the work unit of the task you get details from.

    | **required**: False
    | **type**: str


  user_id
    The user ID of the time-sharing user you want to cancel or force.

    Only applicable when ``state=cancelled`` or ``state=forced``, otherwise ignored.

    | **required**: False
    | **type**: str
    | **default**: None


  dump
    A dump is to be taken. The type of dump (SYSABEND, SYSUDUMP, or SYSMDUMP) depends on the JCL for the job.

    Only applicable when ``state=cancelled`` otherwise ignored.

    | **required**: False
    | **type**: str


  identifier_name
    Option ``identifier_name`` is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

    | **required**: False
    | **type**: str


  arm_restart
    Indicates that the batch job or started task should be automatically restarted after the cancel completes, if it is registered as an element of the automatic restart manager. If the job or task is not registered or if you do not specify this parameter, MVS will not automatically restart the job or task.

    Only applicable when ``state=cancelled``, otherwise is ignored.

    | **required**: False
    | **type**: str


  job_name
    When ``state=started`` **job_name** is a name which should be assigned to a started task while starting it. If job_name is not specified, then member_name is used as job_name.

    Otherwise, **job_name** is the started task job name used to find and apply the ``state`` selected.

    | **required**: False
    | **type**: str



display_task
  Defines options for displaying a task.

  | **required**: False
  | **type**: dict


  identifier_name
    Option ``identifier_name`` is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

    | **required**: False
    | **type**: str


  job_name
    When ``state=started`` **job_name** is a name which should be assigned to a started task while starting it. If job_name is not specified, then member_name is used as job_name.

    Otherwise, **job_name** is the started task job name used to find and apply the ``state`` selected.

    | **required**: False
    | **type**: str



stop_task
  Defines options for stoping a task.

  | **required**: False
  | **type**: dict


  identifier_name
    Option ``identifier_name`` is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

    | **required**: False
    | **type**: str


  job_name
    When ``state=started`` **job_name** is a name which should be assigned to a started task while starting it. If job_name is not specified, then member_name is used as job_name.

    Otherwise, **job_name** is the started task job name used to find and apply the ``state`` selected.

    | **required**: False
    | **type**: str


  asid
    When ``state`` is ``cancelled``, ``cancelled`` or ``stopped`` **asid**. is the hexadecimal address space identifier of the work unit you want to cancel, stop or force.

    When ``state=displayed`` **asid** is the hexadecimal address space identifier of the work unit of the task you get details from.

    | **required**: False
    | **type**: str



modify_task
  Defines options for modifying a task.

  | **required**: False
  | **type**: dict


  identifier_name
    Option ``identifier_name`` is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

    | **required**: False
    | **type**: str


  job_name
    When ``state=started`` **job_name** is a name which should be assigned to a started task while starting it. If job_name is not specified, then member_name is used as job_name.

    Otherwise, **job_name** is the started task job name used to find and apply the ``state`` selected.

    | **required**: False
    | **type**: str


  parameters
    Program parameters passed to the started program, which might be a list in parentheses or a string in single quotation marks

    | **required**: False
    | **type**: str



verbose
  When ``verbose=true`` return system logs that describe the task's execution.

  Using this option will can return a big response depending on system's load, also it could surface other programs activity.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_time
  Option ``wait_time`` is the total time that module `zos_started_tak <./zos_started_task.html>`_ will wait for a submitted task. The time begins when the module is executed on the managed node.

  | **required**: False
  | **type**: int
  | **default**: 5




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

   
   - name: Start a started task using member name.
     zos_started_task:
       start_task:
         member: "PROCAPP"
         job_name: "pocapp"

   - name: Cancel a TSO user session.
     zos_started_task:
       cancel_task:
         user_id: "PROCAPP"

   - name: Cancel a started task using the job name.
     zos_started_task:
       cancel_task:
         job_name: "procapp"

   - name: Get details from a started task.
     zos_started_task:
       display_task:
         job_name: "procapp"





Notes
-----

.. note::
   Commands may need to use specific prefixes like $, they can be discovered by issuing the following command ``D OPDATA,PREFIX``.







