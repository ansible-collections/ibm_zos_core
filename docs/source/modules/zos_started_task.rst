
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_started_task.py

.. _zos_started_task_module:


zos_started_task -- Perform operations on started tasks.
========================================================


.. contents::
   :local:
   :depth: 1


Synopsis
--------
- The following operations can be performed using the module on the started tasks:
  - start
  - display 
  - modify
  - cancel
  - force and stop 


Parameters
----------


asid
  *asid* is an unique address space identifier which gets assigned to each running started task.

  | **required**: False
  | **type**: str


device_type
  *device_type* is the type of the output device (if any) associated with the task.

  | **required**: False
  | **type**: str


device_number
  *device_number* is the number of the device that is started. A device number is 3 or 4 hexadecimal digits. Ensure that you must precede a slash (/) for a 4-digit number but not for a 3-digit number.

  | **required**: False
  | **type**: str


identifier_name
  *identifier_name* is the name that identifies the task to be started. This name can be up to 8 characters long. Ensure that the first character is alphabetical.

  | **required**: False
  | **type**: str


job_account
  *job_account* specifies the accounting data in the JCL JOB statement for the started task. If the source JCL was a job and has already accounting data, the value that is specified on this parameter overrides the accounting data in the source JCL.

  | **required**: False
  | **type**: str


job_name
  *job_name* is a name that is assigned to a started task when you start the task. If job_name is not specified, then member_name is used as job_name.

  | **required**: False
  | **type**: str


keyword_parameters
  Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure. The maximum length of each keyword=option is 66 characters. No individual value within this field can be longer than 44 characters in length.

  | **required**: False
  | **type**: str


member_name
  *member_name* is a 1 - 8 character name of a member of a partitioned data set that contains the source JCL for the task to be started. The member can be either a job or a cataloged procedure.

  | **required**: False
  | **type**: str


operation
  The started task operation which needs to be performed.

  If *operation=start* and the data set does not exist on the managed node, no action taken, module completes successfully with *changed=False*.


  | **required**: True
  | **type**: str
  | **choices**: start, stop, modify, display, force, cancel


parameters
  The program parameters are passed to the started program, which can be a list in parentheses or a string in single quotation marks.

  | **required**: False
  | **type**: str


reus_asid
  When REUSASID=YES is specified on the START command and REUSASID(YES) is specified in the DIAGxx parmlib member, a reusable ASID is assigned to the address space created by the START command. If REUSASID=YES is not specified on the START command or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.

  | **required**: False
  | **type**: str
  | **choices**: YES, NO


subsystem_name
  The name of the subsystem that selects the task for processing. The name must be 1 - 4 characters, which are defined in the IEFSSNxx parmlib member, and the subsystem must be active.

  | **required**: False
  | **type**: str


volume_serial
  If device type is a tape or direct-access device, the volume serial number of the volume is mounted on the device.

  | **required**: False
  | **type**: str


verbose
  The generated system logs contains information about the steps performed by the task.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_time_s
  The option *wait_time_s* is the total time that the module `zos_started_tak <./zos_started_task.html>`_ waits for a submitted task. The time begins when the module is ran on the managed node.

  | **required**: False
  | **type**: int
  | **default**: 5






Examples
--------

.. code-block:: yaml+jinja

   
   - name: Start a started task using member name.
     zos_started_task:
       member: "PROCAPP"
       operation: "start"










