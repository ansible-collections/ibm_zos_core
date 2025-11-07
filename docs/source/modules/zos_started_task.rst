
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


asidx
  When *state* is ``cancelled``, ``stopped`` or ``forced``, *asidx* is the hexadecimal address space identifier of the work unit you want to cancel, stop or force.

  Only applicable when *state* is ``stopped``, ``cancelled``, or ``forced``, otherwise ignored.

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


system_logs
  When ``system_logs=true``, the module will return system logs that describe the task's execution. This option can return a big response depending on system load, also it could surface other program's activity.

  It is not recommended to have this option on all the time, but rather use it as a debugging option.

  | **required**: False
  | **type**: bool
  | **default**: False


job_account
  Specifies accounting data in the JCL JOB statement for the started task. If the source JCL already had accounting data, the value that is specified on this parameter overrides it.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


job_name
  When *state* is started, this is the name which will be assigned to a started task while starting it. If *job_name* is not specified, then *member_name* is used as job's name.

  When *state* is ``displayed``, ``modified``, ``cancelled``, ``stopped``, or ``forced``, *job_name* is the started task name used to query the system.

  | **required**: False
  | **type**: str


keyword_parameters
  Any appropriate keyword parameter that you specify to override the corresponding parameter in the cataloged procedure. The maximum length of each keyword=option pair is 66 characters. No individual value within this field can be longer than 44 characters in length.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: dict


member_name
  Name of a member of a partitioned data set that contains the source JCL for the task to be started. The member can be either a job or a cataloged procedure.

  *member_name* is mandatory and only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: str


parameters
  Program parameters passed to the started program.

  Only applicable when *state* is ``started`` or ``modified``, otherwise ignored.

  For example, REFRESH or REPLACE parameters can be passed while modifying a started task.

  | **required**: False
  | **type**: list
  | **elements**: str


reusable_asid
  When *reusable_asid* is ``True`` and REUSASID(YES) is specified in the DIAGxx parmlib member, a reusable ASID is assigned to the address space created by the START command. If *reusable_asid* is not specified or REUSASID(NO) is specified in DIAGxx, an ordinary ASID is assigned.

  Only applicable when *state* is ``started``, otherwise ignored.

  | **required**: False
  | **type**: bool


state
  *state* is the desired state of the started task after the module is executed.

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


task_id
  A unique system-generated identifier that represents a specific started task running in z/OS. This id starts with STC.

  Only applicable when *state* is ``displayed``, ``modified``, ``cancelled``, ``stopped``, or ``forced``, otherwise ignored.

  | **required**: False
  | **type**: str


user_id
  The user ID of the time-sharing user you want to cancel or force.

  Only applicable when *state* is ``cancelled`` or ``forced``, otherwise ignored.

  | **required**: False
  | **type**: str


verbose
  When ``verbose=true``, the module will return the started task execution logs.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_full_time
  For a started task that takes time to initialize, *wait_time* with ``wait_full_time=true`` ensures the started task completes initialization and JES updates the system control blocks.

  If ``wait_full_time=false``, the module polls every 5 seconds to check the status of the started task and returns immediately once the task is successfully validated.

  When ``wait_full_time=true``, the module waits for the duration specified in *wait_time*, even after the started task operation has been successfully validated.

  | **required**: False
  | **type**: bool
  | **default**: False


wait_time
  Total time that the module will wait for a submitted task, measured in seconds. The time begins when the module is executed on the managed node. Default value of 0 means to wait the default amount of time.

  The default value is 10 seconds if this value is not specified, or if the specified value is less than 10.

  | **required**: False
  | **type**: int
  | **default**: 10




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

   - name: Start a started task and wait for 30 seconds before fetching task details.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       verbose: True
       wait_time: 30
       wait_full_time: True

   - name: Start a started task specifying the subsystem and enabling a reusable ASID.
     zos_started_task:
       state: "started"
       member: "PROCAPP"
       subsystem: "MSTR"
       reusable_asid: "YES"

   - name: Display a started task using a started task name.
     zos_started_task:
       state: "displayed"
       task_name: "PROCAPP"

   - name: Display a started task using a started task id.
     zos_started_task:
       state: "displayed"
       task_id: "STC00012"

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

   - name: Cancel a started task using a started task id.
     zos_started_task:
       state: "cancelled"
       task_id: "STC00093"

   - name: Cancel a started task using it's task name and ASID.
     zos_started_task:
       state: "cancelled"
       task_name: "SAMPLE"
       asidx: 0014

   - name: Modify a started task's parameters.
     zos_started_task:
       state: "modified"
       task_name: "SAMPLE"
       parameters: ["XX=12"]

   - name: Modify a started task's parameters using a started task id.
     zos_started_task:
       state: "modified"
       task_id: "STC00034"
       parameters: ["XX=12"]

   - name: Stop a started task using it's task name.
     zos_started_task:
       state: "stopped"
       task_name: "SAMPLE"

   - name: Stop a started task using a started task id.
     zos_started_task:
       state: "stopped"
       task_id: "STC00087"

   - name: Stop a started task using it's task name, identifier and ASID.
     zos_started_task:
       state: "stopped"
       task_name: "SAMPLE"
       identifier: "SAMPLE"
       asidx: 00A5

   - name: Force a started task using it's task name.
     zos_started_task:
       state: "forced"
       task_name: "SAMPLE"

   - name: Force a started task using it's task id.
     zos_started_task:
       state: "forced"
       task_id: "STC00065"










Return Values
-------------


changed
  True if the state was changed, otherwise False.

  | **returned**: always
  | **type**: bool

cmd
  Command executed via opercmd to achieve the desired state.

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

  The return code is 4 when task_id format is invalid.

  The return code is 5 when any parameter validation failed.

  The return code is 8 when started task is not found using task_id.

  | **returned**: changed
  | **type**: int

state
  The final state of the started task, after execution.

  | **returned**: success
  | **type**: str
  | **sample**: S SAMPLE

stderr
  The STDERR from the command, may be empty.

  | **returned**: failure
  | **type**: str
  | **sample**: An error has occurred.

stderr_lines
  List of strings containing individual lines from STDERR.

  | **returned**: failure
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "An error has occurred"
        ]

stdout
  The STDOUT from the command, may be empty.

  | **returned**: success
  | **type**: str
  | **sample**: ISF031I CONSOLE OMVS0000 ACTIVATED.

stdout_lines
  List of strings containing individual lines from STDOUT.

  | **returned**: success
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

  asidx
    Address space identifier (ASID), in hexadecimal.

    | **type**: str
    | **sample**: 44

  cpu_time
    The processor time used by the address space, including the initiator. This time does not include SRB time.

    *cpu_time* format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).

    ``********`` when time exceeds 100000 hours.

    ``NOTAVAIL`` when the TOD clock is not working.

    | **type**: str
    | **sample**: 00000.00.00.003

  elapsed_time
    For address spaces other than system address spaces, this value represents the elapsed time since the task was selected for execution.

    For system address spaces created before master scheduler initialization, this value represents the elapsed time since the master scheduler was initialized.

    For system address spaces created after master scheduler initialization, this value represents the elapsed time since the system address space was created.

    *elapsed_time* format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).

    ``********`` when time exceeds 100000 hours.

    ``NOTAVAIL`` when the TOD clock is not working.

    | **type**: str
    | **sample**: 00003.20.23.013

  started_time
    The time when the started task started.

    ``********`` when time exceeds 100000 hours.

    ``NOTAVAIL`` when the TOD clock is not working.

    | **type**: str
    | **sample**: 2025-09-11 18:21:50.293644+00:00

  task_id
    The started task id.

    | **type**: str
    | **sample**: STC00018

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


verbose_output
  If ``verbose=true``, the system logs related to the started task executed state will be shown.

  | **returned**: success
  | **type**: str
  | **sample**: 04.33.04 STC00077 ---- SUNDAY,    12 OCT 2025 ----....

