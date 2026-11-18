
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_started_task_info.py

.. _ibm.ibm_zos_core.zos_started_task_info_module:


zos_started_task_info -- Retrieve information on started tasks.
===============================================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- Retrieve detailed status information for long-running started tasks on a single LPAR.





Parameters
----------


job_name
  The started task name used to query the system.

  The name must be a single continuous string with no spaces or blank characters.

  An asterisk wildcard pattern can be used to query multiple started tasks.

  A trailing asterisk (`*`) wildcard pattern can be used to filter for multiple started tasks. The pattern will apply to all started tasks matching the leading character string in *job_name*.

  An asterisk (`*`) wildcard cannot be specified in any other character positions in the *job_name* besides a trailing asterisk.

  Specify (`*`) to query all active started tasks. Note that if (`*`) is specified, all system activity status information will be displayed. This may include batch jobs, started tasks, mounted tasks, attached APPC transaction programs, system address spaces, active TSO/E users, and initiator address spaces.

  The name is case-insensitive and is normalized to uppercase before execution.

  If a *job_name* is specified, *task_id* should not be specified as the parameters are mutually exclusive for retrieving started task information.

  | **required**: False
  | **type**: str


task_id
  A unique system-generated identifier that represents a specific started task running in the z/OS system.

  The ``task_id`` for a started task typically starts with the 'STC' job ID prefix.

  If a *task_id* is specified, *job_name* should not be specified as the parameters are mutually exclusive for retrieving started task information.

  If a *task_id* is specified, *identifier_name* should not be specified as the parameters are mutually exclusive for retrieving started task information.

  Asterisk (`*`) wildcards cannot be used in the *task_id* parameter.

  | **required**: False
  | **type**: str


identifier_name
  The name that identifies the task. It can be paired with *job_name* to display information about a specific active started task if multiple started tasks have the same *job_name*.

  An asterisk (`*`) wildcard cannot be specified in the *identifier_name*.

  If an *identifier_name* is specified, *task_id* should not be specified as the parameters are mutually exclusive for querying started tasks.

  If *identifier_name* is specified, *job_name* must be specified as well.

  | **required**: False
  | **type**: str


verbose
  When ``verbose=true``, the module will return the started task execution logs. Only started tasks with an associated task ID are able to return execution logs.

  | **required**: False
  | **type**: bool
  | **default**: False




Attributes
----------
action
  | **support**: none
  | **description**: Indicates this has a corresponding action plugin so some parts of the options can be executed on the controller.
check_mode
  | **support**: full
  | **description**: Can run in check_mode and return changed status prediction without modifying target. If not supported, the action will be skipped.



Examples
--------

.. code-block:: yaml+jinja

   
   - name: Display a started task using a started task name.
     zos_started_task_info:
       job_name: "PROCAPP"

   - name: Display a started task using a started task name and identifier.
     zos_started_task_info:
       job_name: "PROCAPP.SAMPLE"

   - name: Display a started task using a started task id.
     zos_started_task_info:
       task_id: "STC00012"

   - name: Display all started tasks that begin with an s using a wildcard.
     zos_started_task_info:
       job_name: "s*"

   - name: Display all started tasks.
     zos_started_task_info:
       job_name: "*"




Notes
-----

.. note::
   Either ``job_name`` or ``task_id`` is mandatory to display started task status information.







Return Values
-------------


changed
  Indicates whether any changes were made to the system. Always ``false`` for info modules.

  | **returned**: always
  | **type**: bool

cmd
  Operator DISPLAY command executed via ZOAU ``opercmd`` utility to retrieve started task information.

  | **returned**: success
  | **type**: str
  | **sample**: D A,ICSF

msg
  Failure or skip message returned by the module. An empty string will be returned when no error occurs.

  | **returned**: always
  | **type**: str
  | **sample**: No started task is active with the given name.

rc
  The return code from running the underlying ZOAU utilities in the module.

  The return code is ``0`` when command executed successfully.

  The return code is a non-zero integer when an underlying ZOAU utility encounters an error.

  The return code is ``null`` when parameter validation fails prior to the execution of a ZOAU utility.

  | **returned**: always
  | **type**: int

stderr
  The standard error from command execution. An empty string will be returned when no error occurs.

  | **returned**: always
  | **type**: str
  | **sample**: An error has occurred.

stderr_lines
  List of strings containing individual lines from STDERR.

  | **returned**: always
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "An error has occurred"
        ]

stdout
  The standard output from command execution. This return field may be empty when an error occurs.

  | **returned**: success
  | **type**: str
  | **sample**: EC00000A   2026287  12:14:28.00             ISF031I CONSOLE OMVS0000 ACTIVATED...

stdout_lines
  List of strings containing individual lines from STDOUT.

  | **returned**: success
  | **type**: list
  | **sample**:

    .. code-block:: json

        [
            "EC00000A   2026287  12:14:28.00             ISF031I CONSOLE OMVS0000 ACTIVATED"
        ]

tasks
  A list containing the status information for each started tasks matching the specified criteria. An empty list will be returned if no started tasks can be found that match the specified criteria.

  | **returned**: success
  | **type**: list
  | **elements**: dict

  address_space_aste
    The central address space of the address space second table entry (ASTE).

    | **returned**: always
    | **type**: str
    | **sample**: 03E99440

  address_space_type
    The type of work that owns the address space, which will be either ``A`` (attached APPC transaction program), ``I`` (initiator address space), ``J`` (job), ``M`` (mount), ``S`` (started task), or ``*`` (system address space)

    | **returned**: always
    | **type**: str
    | **sample**: S

  asidx
    Address space identifier (ASID), in hexadecimal.

    | **returned**: always
    | **type**: str
    | **sample**: 0054

  cpu_time
    The processor time used by the address space, including the initiator. This time does not include system request block (SRB) time.

    The *cpu_time* format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).

    The *cpu_time* will be ``********`` when time exceeds 100000 hours.

    The *cpu_time* will be ``NOTAVAIL`` when the TOD clock is not working.

    | **returned**: always
    | **type**: str
    | **sample**: 00000.00.00.003

  data_spaces
    The data spaces associated with the address space.

    The *data_spaces* list will be empty if there are no data spaces associated with the address space or if the system could not return the data space information.

    | **returned**: always
    | **type**: list
    | **elements**: dict

    data_space_name
      The data space name associated with the address space.

      | **returned**: always
      | **type**: str
      | **sample**: 00000IEF

    data_space_aste
      The central address space of the data space address space second table entry (ASTE).

      | **returned**: always
      | **type**: str
      | **sample**: 0594D600


  elapsed_time
    For address spaces other than system address spaces, this value represents the elapsed time since the task was selected for execution.

    For system address spaces created before master scheduler initialization, this value represents the elapsed time since the master scheduler was initialized.

    For system address spaces created after master scheduler initialization, this value represents the elapsed time since the system address space was created.

    The *elapsed_time* format is hhhhh.mm.ss.SSS(hours.minutes.seconds.milliseconds).

    The *elapsed_time* will be ``********`` when time exceeds 100000 hours.

    The *elapsed_time* will be ``NOTAVAIL`` when the TOD clock is not working.

    | **returned**: always
    | **type**: str
    | **sample**: 00003.20.23.013

  per_trap
    Whether a program event recording (PER) trap is active in the address space.

    | **returned**: always
    | **type**: bool

  quiesced
    Whether the address space has be quiesced.

    | **returned**: always
    | **type**: bool

  resource_group
    The resource group associated with the address space.

    May be ``N/A`` if there is no resource group associated with the address space.

    | **returned**: always
    | **type**: str
    | **sample**: N/A

  server
    Whether the address space is a server.

    | **returned**: always
    | **type**: bool

  service_class
    The service class currently associated with the address space.

    | **returned**: always
    | **type**: str
    | **sample**: SYSSTC

  service_class_period
    The service class period currently associated with the address space.

    | **returned**: always
    | **type**: str
    | **sample**: 1

  smc_requests
    The number of outstanding step-must-complete requests.

    | **returned**: always
    | **type**: str
    | **sample**: 000

  started_time
    The time when the started task started, including the UTC offset of the local system time zone.

    The *started_time* format is YYYY-MM-DD hh:mm:ss.SSSSSS±hh:mm (year-month-day hours.minutes.seconds.milliseconds±hours:minutes).

    The started time will return an empty string if the value is unable to be calculated.

    | **returned**: always
    | **type**: str
    | **sample**: 2025-09-11 18:21:50.293644+00:00

  step_name
    For started tasks, the name of the active step within a cataloged procedure that was called by the *task_identifier*.

    *step_name* will return an empty string if there is no cataloged procedure called by the *task_identifier*.

    For APPC-initiated transactions, the user ID requesting the transaction.

    | **returned**: always
    | **type**: str
    | **sample**: IEFPROC

  task_id
    The started task id, also known as the work unit identifier (WUID).

    An empty string will be returned if the started task has no *task_id*.

    | **returned**: always
    | **type**: str
    | **sample**: STC00018

  task_identifier
    For a started task, the identifier of a task created by the START command.

    The *task_identifier* may also be the name of a step that called a cataloged procedure, the name of a step for a job or attached APPC transaction program, or the name of a system or initiator address space.

    The task identifier will be ``STARTING`` if initiation of a started job or system task is incomplete.

    The task identifier will be ``*MASTER*`` for the master address space.

    | **returned**: always
    | **type**: str
    | **sample**: SPROC

  task_name
    For a task created by the START or MOUNT command, the procedure name of the task.

    The *task_name* may also be the name of a system address space, job, attached APPC transaction program, or initiator address space.

    The *task_name* will be ``STARTING`` if initiation of a started job or system task is incomplete.

    The *task_name* will be ``*MASTER*`` for the master address space.

    | **returned**: always
    | **type**: str
    | **sample**: SAMPLE

  task_status
    The status of the started task, which will be either ``IN`` (swapped in), ``OUT`` (swapped out, ready to run), ``OWT`` (swapped out, waiting, not ready to run), ``OU*`` (in process of being swapped out), ``IN*`` (in process of being swapped in), or ``NSW`` (non-swappable)

    | **returned**: always
    | **type**: str
    | **sample**: NSW

  unix_address_space
    Whether the address space is a z/OS Unix System Services dubbed address space.

    | **returned**: always
    | **type**: bool
    | **sample**:

      .. code-block:: json

          true

  user_id
    The user ID associated with the unit of work.

    | **returned**: always
    | **type**: str
    | **sample**: USRT001

  workload_name
    The name of the workload currently associated with the address space.

    | **returned**: always
    | **type**: str
    | **sample**: SYSTEM


verbose_output
  If ``verbose=true``, the the started task system logs will be shown if the matched started task has a *task_id*.

  When querying all started tasks or querying with wildcards, only the system logs for the first matched task will be displayed. If the first matched task does not have a *task_id*, no logs will be displayed.

  | **returned**: success
  | **type**: str
  | **sample**: 04.33.04 STC00077 ---- SUNDAY,    12 OCT 2025 ----....

