
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


arm
  *arm* indicates to execute normal task termination routines without causing address space destruction.

  Only applicable when *state* is ``forced``, otherwise ignored.

  | **required**: False
  | **type**: bool


armrestart
  Indicates that the batch job or started task should be automatically restarted after CANCEL or FORCE completes, if it is registered as an element of the automatic restart manager. If the job or task is not registered or if you do not specify this parameter, MVS will not automatically restart the job or task.

  Only applicable when *state* is ``cancelled`` or ``forced``, otherwise ignored.

  | **required**: False
  | **type**: bool


asid
  When *state* is ``cancelled``, ``stopped`` or ``forced``, *asid* is the hexadecimal address space identifier of the work unit you want to cancel, stop or force.

  Only applicable when *state* is ``stopped``, ``cancelled``, or ``forced``, otherwise ignored.

  | **required**: False
  | **type**: str


device_type
  Type of the output device (if any) associated with the task.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


device_number
  Number of the device to be started. A device number is 3 or 4 hexadecimal digits. A slash (/) must precede a 4-digit number but is not before a 3-digit number.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


dump
  Whether to perform a dump. The type of dump (SYSABEND, SYSUDUMP, or SYSMDUMP) depends on the JCL for the job.

  Only applicable when *state* is ``cancelled``, otherwise ignored.

  | **required**: False
  | **type**: bool


identifier_name
  Option *identifier_name* is the name that identifies the task. This name can be up to 8 characters long. The first character must be alphabetical.

  | **required**: False
  | **type**: str


job_account
  Specifies accounting data in the JCL JOB statement for the started task. If the source JCL already had accounting data, the value that is specified on this parameter overrides it.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


job_name
  When *state* is started, this is the name which should be assigned to a started task while starting it. If *job_name* is not specified, then *member_name* is used as job's name.

  When *state* is ``displayed``, ``modified``, ``cancelled``, ``stopped``, or ``forced``, *job_name* is the started task name.

  | **required**: False
  | **type**: str


keyword_parameters
  Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure. The maximum length of each keyword=option pair is 66 characters. No individual value within this field can be longer than 44 characters in length.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: dict


member_name
  Name of a member of a partitioned data set that contains the source JCL for the task to be started. The member can be either a job or a cataloged procedure.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


parameters
  Program parameters passed to the started program.

  Only applicable when *state* is ``started`` or ``modified``, otherwise ignored.

  | **required**: False
  | **type**: list
  | **elements**: str


retry_force
  Indicates whether retry will be attempted on ABTER:ref:`abnormal termination <abnormal termination_module>`.

  *tcb_address* is mandatory to use *retry_force*.

  Only applicable when *state* is ``forced``, otherwise ignored.

  | **required**: False
  | **type**: bool


reus_asid
  When *reus_asid* is ``True`` and REUSASID(YES) is specified in the DIAGxx parmlib member, a reusable ASID is assigned to the address space created by the START command. If *reus_asid* is not specified or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: bool


state
  *state* should be the desired state of the started task after the module is executed.

  If *state* is ``started`` and the respective member is not present on the managed node, then error will be thrown with ``rc=1``, ``changed=false`` and *stderr* which contains error details.

  If *state* is ``cancelled``, ``modified``, ``displayed``, ``stopped`` or ``forced`` and the started task is not running on the managed node, then error will be thrown with ``rc=1``, ``changed=false`` and *stderr* contains error details.

  If *state* is ``displayed`` and the started task is running, then the module will return the started task details along with ``changed=true``.

  | **required**: True
  | **type**: str
  | **choices**: started, displayed, modified, cancelled, stopped, forced


subsystem
  The name of the subsystem that selects the task for processing. The name must be 1-4 characters long, which are defined in the IEFSSNxx parmlib member, and the subsystem must be active.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


tcb_address
  6-digit hexadecimal TCB address of the task to terminate.

  Only applicable when *state* is ``forced``, otherwise ignored.

  | **required**: False
  | **type**: str


volume
  If *device_type* is a tape or direct-access device, the serial number of the volume, mounted on the device.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


userid
  The user ID of the time-sharing user you want to cancel or force.

  Only applicable when *state* is ``cancelled`` or ``forced``, otherwise ignored.

  | **required**: False
  | **type**: str


verbose
  When ``verbose=true``, the module will return system logs that describe the task's execution. This option can return a big response depending on system load, also it could surface other program's activity.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_time
  Total time that the module will wait for a submitted task, measured in seconds. The time begins when the module is executed on the managed node. Default value of 0 means to wait the default amount of time supported by the opercmd utility.

  | **required**: False
  | **type**: int
  | **default**: 0




Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
async
  | **support**: full
  | **description**: Supports being used with the ``async`` keyword.
check_mode
  | **support**: full
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Start a started task using a member in a partitioned data set.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
   - name: Start a started task using a member name and giving it an identifier.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       identifier: "SAMPLE"
   - name: Start a started task using both a member and a job name.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       job_name: "SAMPLE"
   - name: Start a started task and enable verbose output.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       job_name: "SAMPLE"
       verbose: True
   - name: Start a started task specifying the subsystem and enabling a reusable ASID.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       subsystem: "MSTR"
       reus_asid: "YES"
   - name: Display a started task using a started task name.
     zos_started_task:
       state: "displayed"
       task_name: "PROCAPP"
   - name: Display all started tasks that begin with an s using a wildcard.
     zos_started_task:
       state: "displayed"
       task_name: "s*"
   - name: Display all started tasks.
     zos_started_task:
       state: "displayed"
       task_name: "all"
   - name: Cancel a started task using task name.
     zos_started_task:
       state: "cancelled"
       task_name: "SAMPLE"
   - name: Cancel a started task using it's task name and ASID.
     zos_started_task:
       state: "cancelled"
       task_name: "SAMPLE"
       asid: 0014
   - name: Modify a started task's parameters.
     zos_started_task:
       state: "modified"
       task_name: "SAMPLE"
       parameters: ["XX=12"]
   - name: Stop a started task using it's task name.
     zos_started_task:
       state: "stopped"
       task_name: "SAMPLE"
   - name: Stop a started task using it's task name, identifier and ASID.
     zos_started_task:
       state: "stopped"
       task_name: "SAMPLE"
       identifier: "SAMPLE"
       asid: 00A5
   - name: Force a started task using it's task name.
     zos_started_task:
       state: "forced"
       task_name: "SAMPLE"










Return Values
-------------


changed
  True if the state was changed, otherwise False.

  | **returned**: always
  | **type**: bool

cmd
  Command executed via opercmd.

  | **returned**: changed
  | **type**: str
  | **sample**: S SAMPLE

msg
  Failure or skip message returned by the module.

  | **returned**: failure or skipped
  | **type**: str
  | **sample**: Command parameters are invalid.

rc
  The return code is 0 when command executed successfully.

  The return code is 1 when opercmd throws any error.

  The return code is 5 when any parameter validation failed.

  | **returned**: changed
  | **type**: int

state
  The final state of the started task, after execution.

  | **returned**: changed
  | **type**: str
  | **sample**: S SAMPLE

stderr
  The STDERR from the command, may be empty.

  | **returned**: changed
  | **type**: str
  | **sample**: An error has occurred.

stderr_lines
  List of strings containing individual lines from STDERR.

  | **returned**: changed
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "An error has occurred"
        ]

stdout
  The STDOUT from the command, may be empty.

  | **returned**: changed
  | **type**: str
  | **sample**: ISF031I CONSOLE OMVS0000 ACTIVATED.

stdout_lines
  List of strings containing individual lines from STDOUT.

  | **returned**: changed
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "Allocation to SYSEXEC completed."
        ]

tasks
  The output information for a list of started tasks matching specified criteria.

  If no started task is found then this will return empty.

  | **returned**: success
  | **type**: list
  | **elements**: dict

  address_space_second_table_entry
    The control block used to manage memory for a started task

    | **type**: str
    | **sample**: 03E78500

  affinity
    The identifier of the processor, for up to any four processors, if the job requires the services of specific processors.

    affinity=NONE means the job can run on any processor.

    | **type**: str
    | **sample**: NONE

  asid
    Address space identifier (ASID), in hexadecimal.

    | **type**: str
    | **sample**: 44

  cpu_time
    The processor time used by the address space, including the initiator. This time does not include SRB time.

    cpu_time has one of these below formats, where ttt is milliseconds, sss or ss is seconds, mm is minutes, and hh or hhhhh is hours. sss.tttS when time is less than 1000 seconds hh.mm.ss when time is at least 1000 seconds, but less than 100 hours hhhhh.mm when time is at least 100 hours ******** when time exceeds 100000 hours NOTAVAIL when the TOD clock is not working

    | **type**: str
    | **sample**: 000.008S

  dataspaces
    The started task data spaces details.

    | **returned**: success
    | **type**: list
    | **elements**: dict

    data_space_address_entry
      Central address of the data space ASTE.

      | **type**: str
      | **sample**: 058F2180

    data_space_name
      Data space name associated with the address space.

      | **type**: str
      | **sample**: CIRRGMAP


  domain_number
    The z/OS system or sysplex domain where started task is running.

    domain_number=N/A if the system is operating in goal mode.

    | **type**: str
    | **sample**: N/A

  elapsed_time
    For address spaces other than system address spaces, the elapsed time since job select time.

    For system address spaces created before master scheduler initialization, the elapsed time since master scheduler initialization.

    For system address spaces created after master scheduler initialization, the elapsed time since system address space creation.

    elapsed_time has one of following formats, where ttt is milliseconds, sss or ss is seconds, mm is minutes, and hh or hhhhh is hours. sss.tttS when time is less than 1000 seconds hh.mm.ss when time is at least 1000 seconds, but less than 100 hours hhhhh.mm when time is at least 100 hours ******** when time exceeds 100000 hours NOTAVAIL when the TOD clock is not working

    | **type**: str
    | **sample**: 812.983S

  priority
    Priority of a started task, as determined by the Workload Manager (WLM), based on the service class and importance assigned to it.

    | **type**: str
    | **sample**: 1

  proc_step_name
    For APPC-initiated transactions, the user ID requesting the transaction.

    The name of a step within a cataloged procedure that was called by the step specified in field sss.

    Blank, if there is no cataloged procedure.

    The identifier of the requesting transaction program.

    | **type**: str
    | **sample**: VLF

  program_event_recording
    YES if A PER trap is active in the address space.

    NO if No PER trap is active in the address space.

    | **type**: str

  program_name
    The name of the program(load module) that created or is running in the started task's address space.

    program_name=N/A if the system is operating in goal mode.

    | **type**: str
    | **sample**: N/A

  queue_scan_count
    YES if the address space has been quiesced.

    NO if the address space is not quiesced.

    | **type**: str

  resource_group
    The name of the resource group currently associated with the service class. It can also be N/A if there is no resource group association.

    | **type**: str
    | **sample**: N/A

  server
    YES if the address space is a server.

    No if the address space is not a server.

    | **type**: str

  started_class_list
    The name of the service class currently associated with the address space.

    | **type**: str
    | **sample**: SYSSTC

  started_time
    The time when the started task started.

    | **type**: str
    | **sample**: 2025-09-11 18:21:50.293644+00:00

  system_management_control
    Number of outstanding step-must-complete requests.

    | **type**: str

  task_identifier
    The name of a system address space.

    The name of a step, for a job or attached APPC transaction program attached by an initiator.

    The identifier of a task created by the START command.

    The name of a step that called a cataloged procedure.

    ``STARTING`` if initiation of a started job, system task, or attached APPC transaction program is incomplete.

    ``*MASTER*`` for the master address space.

    The name of an initiator address space.

    | **type**: str
    | **sample**: SPROC

  task_name
    The name of the started task.

    | **type**: str
    | **sample**: SAMPLE

  task_status
    ``IN`` for swapped in.

    ``OUT`` for swapped out, ready to run.

    ``OWT`` for swapped out, waiting, not ready to run.

    ``OU*`` for in process of being swapped out.

    ``IN*`` for in process of being swapped in.

    ``NSW`` for non-swappable.

    | **type**: str
    | **sample**: NSW

  task_type
    ``S`` for started task.

    ``A`` for an attached APPC transaction program.

    ``I`` for initiator address space.

    ``J`` for job

    ``M`` for mount

    ``*`` for system address space

    | **type**: str
    | **sample**: S

  workload_manager
    The name of the workload currently associated with the address space.

    | **type**: str
    | **sample**: SYSTEM


verbose_output
  If ``verbose=true``, the system log related to the started task executed state will be shown.

  | **returned**: changed
  | **type**: list
  | **sample**:

    .. code-block:: json

        "NC0000000 ZOSMACHINE 25240 12:40:30.15 OMVS0000 00000210...."

