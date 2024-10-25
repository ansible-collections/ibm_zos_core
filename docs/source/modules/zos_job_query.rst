
:github_url: https://github.com/ansible-collections/ibm_zos_core/blob/dev/plugins/modules/zos_job_query.py

.. _zos_job_query_module:


zos_job_query -- Query job status
=================================



.. contents::
   :local:
   :depth: 1


Synopsis
--------
- List z/OS job(s) and the current status of the job(s).
- Uses job_name to filter the jobs by the job name.
- Uses job_id to filter the jobs by the job identifier.
- Uses owner to filter the jobs by the job owner.
- Uses system to filter the jobs by system where the job is running (or ran) on.





Parameters
----------


job_name
  The job name to query.

  A job name can be up to 8 characters long.

  The *job_name* can contain include multiple wildcards.

  The asterisk (`*`) wildcard will match zero or more specified characters.

  | **required**: False
  | **type**: str
  | **default**: *


owner
  Identifies the owner of the job.

  If no owner is set, the default set is 'none' and all jobs will be queried.

  | **required**: False
  | **type**: str


job_id
  The job id that has been assigned to the job.

  A job id must begin with `STC`, `JOB`, `TSU` and are followed by up to 5 digits.

  When a job id is greater than 99,999, the job id format will begin with `S`, `J`, `T` and are followed by 7 digits.

  The *job_id* can contain include multiple wildcards.

  The asterisk (`*`) wildcard will match zero or more specified characters.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: Query a job with a job name of 'JOB12345'
     zos_job_query:
       job_name: "JOB12345"

   - name: Query jobs using a wildcard to match any job id begging with 'JOB12'
     zos_job_query:
       job_id: "JOB12*"

   - name: Query jobs using wildcards to match any job name begging with 'H' and ending in 'O'.
     zos_job_query:
       job_name: "H*O"

   - name: Query jobs using a wildcards to match a range of job id(s) that include 'JOB' and '014'.
     zos_job_query:
       job_id: JOB*014*

   - name: Query all job names beginning wih 'H' that match job id that includes '14'.
     zos_job_query:
       job_name: "H*"
       job_id: "JOB*14*"

   - name: Query all jobs names beginning with 'LINK' for owner 'ADMIN'.
     zos_job_query:
       job_name: "LINK*"
       owner: ADMIN










Return Values
-------------


changed
  True if the state was changed, otherwise False.

  | **returned**: always
  | **type**: bool

jobs
  The output information for a list of jobs matching specified criteria. If no job status is found, this will return ret_code dictionary with parameter msg_txt = The job could not be found.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "asid": 0,
                "content_type": "JOB",
                "creation_date": "2023-05-03",
                "creation_time": "12:13:00",
                "job_class": "K",
                "job_id": "JOB01427",
                "job_name": "LINKJOB",
                "owner": "ADMIN",
                "priority": 1,
                "queue_position": 3,
                "ret_code": "null",
                "svc_class": "?"
            },
            {
                "asid": 4,
                "content_type": "JOB",
                "creation_date": "2023-05-03",
                "creation_time": "12:14:00",
                "job_class": "A",
                "job_id": "JOB16577",
                "job_name": "LINKCBL",
                "owner": "ADMIN",
                "priority": 0,
                "queue_position": 0,
                "ret_code": {
                    "code": "null",
                    "msg": "CANCELED"
                },
                "svc_class": "E"
            }
        ]

  job_name
    The name of the batch job.

    | **type**: str
    | **sample**: LINKJOB

  owner
    The owner who ran the job.

    | **type**: str
    | **sample**: ADMIN

  job_id
    Unique job identifier assigned to the job by JES.

    | **type**: str
    | **sample**: JOB01427

  content_type
    Type of address space used by the job, can be one of the following types.

    APPC for a APPC Initiator.

    JGRP for a JOBGROUP.

    JOB for a Batch job.

    STC for a Started task.

    TSU for a Time sharing user.

    \? for an unknown or pending.

    | **type**: str
    | **sample**: STC

  system
    The job entry system that MVS uses to do work.

    | **type**: str
    | **sample**: STL1

  subsystem
    The job entry subsystem that MVS uses to do work.

    | **type**: str
    | **sample**: STL1

  ret_code
    Return code output collected from job log.

    | **type**: dict
    | **sample**:

      .. code-block:: json

          {
              "ret_code": {
                  "code": 0,
                  "msg": "CC 0000",
                  "msg_code": "0000",
                  "msg_txt": "",
                  "steps": [
                      {
                          "step_cc": 0,
                          "step_name": "STEP0001"
                      }
                  ]
              }
          }

    msg
      Return code or abend resulting from the job submission.

      | **type**: str
      | **sample**: CC 0000

    msg_code
      Return code extracted from the `msg` so that it can be evaluated. For example, ABEND(S0C4) would yield "S0C4".

      | **type**: str
      | **sample**: S0C4

    msg_txt
      Returns additional information related to the job.

      | **type**: str
      | **sample**: No job can be located with this job name: HELLO

    code
      Return code converted to integer value (when possible).

      | **type**: int

    steps
      Series of JCL steps that were executed and their return codes.

      | **type**: list
      | **elements**: dict

      step_name
        Name of the step shown as "was executed" in the DD section.

        | **type**: str
        | **sample**: STEP0001

      step_cc
        The CC returned for this step in the DD section.

        | **type**: int



  job_class
    Job class for this job.

    | **type**: str
    | **sample**: A

  svc_class
    Service class for this job.

    | **type**: str
    | **sample**: C

  priority
    A numeric indicator of the job priority assigned through JES.

    | **type**: int
    | **sample**: 4

  asid
    The address Space Identifier (ASID) that is a unique descriptor for the job address space. Zero if not active.

    | **type**: int

  creation_date
    Date, local to the target system, when the job was created.

    | **type**: str
    | **sample**: 2023-05-04

  creation_time
    Time, local to the target system, when the job was created.

    | **type**: str
    | **sample**: 14:15:00

  queue_position
    The position within the job queue where the jobs resides.

    | **type**: int
    | **sample**: 3

  program_name
    The name of the program found in the job's last completed step found in the PGM parameter. Returned when Z Open Automation Utilities (ZOAU) is 1.2.4 or later.

    | **type**: str
    | **sample**: IEBGENER


message
  Message returned on failure.

  | **returned**: failure
  | **type**: str
  | **sample**: {'msg': 'List FAILED! no such job been found: IYK3Z0R9'}

