
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
- Uses owner to filter the jobs by the job owner.
- Uses system to filter the jobs by system where the job is running (or ran) on.
- Uses job_id to filter the jobs by the job id.





Parameters
----------


job_name
  The job name to query.

  | **required**: False
  | **type**: str
  | **default**: *


owner
  Identifies the owner of the job.

  If no owner is set, the default set is 'none' and all jobs will be queried.

  | **required**: False
  | **type**: str


job_id
  The job number that has been assigned to the job. These normally begin with STC, JOB, TSU and are followed by 5 digits. When job are potentially greater than 99,999, the job number format will begin with S, J, T and are followed by 7 digits.

  | **required**: False
  | **type**: str




Examples
--------

.. code-block:: yaml+jinja

   
   - name: list zos jobs with a jobname 'IYK3ZNA1'
     zos_job_query:
       job_name: "IYK3ZNA1"

   - name: list the jobs matching jobname 'IYK3*'
     zos_job_query:
       job_name: "IYK3*"

   - name: list the job with a jobname 'IYK3ZNA*' and jobid as JOB01427
     zos_job_query:
       job_name: IYK3ZNA*
       job_id: JOB01427

   - name: list the job with a jobname 'IYK3ZNA*' and owner as BROWNAD
     zos_job_query:
       job_name: IYK3ZNA*
       owner: BROWNAD










Return Values
-------------


changed
  True if the state was changed, otherwise False.

  | **returned**: always
  | **type**: bool

jobs
  The output information for a list of jobs matching specified criteria. If no job status is found, this will return an empty job code with msg=JOB NOT FOUND.

  | **returned**: success
  | **type**: list
  | **elements**: dict
  | **sample**:

    .. code-block:: json

        [
            {
                "job_id": "JOB01427",
                "job_name": "IYK3ZNA1",
                "owner": "BROWNAD",
                "ret_code": "null"
            },
            {
                "job_id": "JOB16577",
                "job_name": "IYK3ZNA2",
                "owner": "BROWNAD",
                "ret_code": {
                    "code": "null",
                    "msg": "CANCELED"
                }
            }
        ]

  job_name
    The name of the batch job.

    | **type**: str
    | **sample**: IYK3ZNA2

  owner
    The owner who ran the job.

    | **type**: str
    | **sample**: BROWNAD

  job_id
    Unique job id assigned to the job by JES.

    | **type**: str
    | **sample**: JOB01427

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
                          "step_cc": "0000",
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

        | **type**: str
        | **sample**: 00




message
  Message returned on failure.

  | **returned**: failure
  | **type**: str
  | **sample**: {'msg': 'List FAILED! no such job been found: IYK3Z0R9'}

