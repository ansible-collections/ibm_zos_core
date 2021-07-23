#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: zos_job_query
short_description: Query job status
description:
  - List z/OS job(s) and the current status of the job(s).
  - Uses owner to filter the jobs by the job owner.
  - Uses system to filter the jobs by system where the job is running (or ran) on.
  - Uses job_id to filter the jobs by the job id.
author:
  - "Ping Xiao (@xiaopingBJ)"
  - "Demetrios Dimatos (@ddimatos)"
options:
  job_name:
    description:
       - The job name to query.
    type: str
    required: False
    default: "*"
  owner:
    description:
      - Identifies the owner of the job.
      - If no owner is set, the default set is 'none' and all jobs will be
        queried.
    type: str
    required: False
  job_id:
    description:
      - The job number that has been assigned to the job. These normally begin
        with STC, JOB, TSU and are followed by 5 digits. When job are
        potentially greater than 99,999, the job number format will begin with
        S, J, T and are followed by 7 digits.
    type: str
    required: False
"""

EXAMPLES = r"""
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
"""

RETURN = r"""
changed:
  description:
    True if the state was changed, otherwise False.
  returned: always
  type: bool
jobs:
  description:
    The output information for a list of jobs matching specified criteria.
    If no job status is found, this will return an empty job code with msg=JOB NOT FOUND.
  returned: success
  type: list
  elements: dict
  contains:
    job_name:
      description:
         The name of the batch job.
      type: str
      sample: IYK3ZNA2
    owner:
      description:
         The owner who ran the job.
      type: str
      sample: BROWNAD
    job_id:
      description:
         Unique job id assigned to the job by JES.
      type: str
      sample: JOB01427
    ret_code:
      description:
         Return code output collected from job log.
      type: dict
      contains:
        msg:
          description:
            Return code or abend resulting from the job submission.
          type: str
          sample: CC 0000
        msg_code:
          description:
            Return code extracted from the `msg` so that it can be evaluated.
            For example, ABEND(S0C4) would yield "S0C4".
          type: str
          sample: S0C4
        msg_txt:
          description:
             Returns additional information related to the job.
          type: str
          sample: "No job can be located with this job name: HELLO"
        code:
          description:
             Return code converted to integer value (when possible).
          type: int
          sample: 00
        steps:
          description:
            Series of JCL steps that were executed and their return codes.
          type: list
          elements: dict
          contains:
            step_name:
              description:
                Name of the step shown as "was executed" in the DD section.
              type: str
              sample: "STEP0001"
            step_cc:
              description:
                The CC returned for this step in the DD section.
              type: str
              sample: "00"

      sample:
        ret_code: {
         "msg": "CC 0000",
         "msg_code": "0000",
         "msg_txt": "",
         "code": 0,
         "steps": [
            { "step_name": "STEP0001",
              "step_cc": "0000"
            }
          ]
        }
  sample:
    [
        {
            "job_name": "IYK3ZNA1",
            "owner": "BROWNAD",
            "job_id": "JOB01427",
            "ret_code": "null",
        },
        {
            "job_name": "IYK3ZNA2",
            "owner": "BROWNAD",
            "job_id": "JOB16577",
            "ret_code": { "msg": "CANCELED", "code": "null" },
        },
    ]
message:
  description:
     Message returned on failure.
  type: str
  returned: failure
  sample:
     msg: "List FAILED! no such job been found: IYK3Z0R9"
"""

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.job import job_status

from ansible.module_utils.basic import AnsibleModule
import re


def run_module():

    module_args = dict(
        job_name=dict(type="str", required=False, default="*"),
        owner=dict(type="str", required=False),
        job_id=dict(type="str", required=False),
    )

    result = dict(changed=False, message="")

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        return result

    try:
        validate_arguments(module.params)
        jobs_raw = query_jobs(module.params)
        jobs = parsing_jobs(jobs_raw)
    except Exception as e:
        module.fail_json(msg=e, **result)
    result["jobs"] = jobs
    module.exit_json(**result)


def validate_arguments(params):
    job_name_in = params.get("job_name")
    job_id = params.get("job_id")
    owner = params.get("owner")
    if job_name_in or job_id:
        if job_name_in and job_name_in != "*":
            job_name_pattern = re.compile(r"^[a-zA-Z$#@%][0-9a-zA-Z$#@%]{0,7}$")
            job_name_pattern_with_star = re.compile(
                r"^[a-zA-Z$#@%][0-9a-zA-Z$#@%]{0,6}\*$"
            )
            m = job_name_pattern.search(job_name_in)
            n = job_name_pattern_with_star.search(job_name_in)
            if m or n:
                pass
            else:
                raise RuntimeError("Failed to validate the job name: " + job_name_in)
        if job_id:
            job_id_pattern = re.compile("(JOB|TSU|STC)[0-9]{5}|(J|T|S)[0-9]{7}$")
            if not job_id_pattern.search(job_id):
                raise RuntimeError("Failed to validate the job id: " + job_id)
    else:
        raise RuntimeError("Argument Error:Either job name(s) or job id is required")
    if job_id and owner:
        raise RuntimeError("Argument Error:job id can not be co-exist with owner")


def query_jobs(params):
    job_name_in = params.get("job_name")
    job_id = params.get("job_id")
    owner = params.get("owner")
    jobs = []
    if job_id:
        jobs = job_status(job_id=job_id)
    elif owner:
        jobs = job_status(owner=owner, job_name=job_name_in)
    else:
        jobs = job_status(job_name=job_name_in)
    if not jobs:
        raise RuntimeError("List FAILED! no such job was found.")
    return jobs


def parsing_jobs(jobs_raw):
    jobs = []
    ret_code = {}
    for job in jobs_raw:
        status_raw = job.get("ret_code").get("msg", "")
        if "AC" in status_raw:
            # the job is active
            ret_code = None
        elif "CC" in status_raw:
            # status = 'Completed normally'
            ret_code = {
                "msg": status_raw,
                "code": job.get("ret_code").get("code"),
            }
        elif "ABEND" in status_raw:
            # status = 'Ended abnormally'
            ret_code = {
                "msg": status_raw,
                "code": job.get("ret_code").get("code"),
            }
        elif "ABENDU" in status_raw:
            # status = 'Ended abnormally'
            ret_code = {"msg": status_raw, "code": job.get("ret_code").get("code")}
        elif "CANCELED" or "JCLERR" or "JCL ERROR" or "JOB NOT FOUND" in status_raw:
            # status = status_raw
            ret_code = {"msg": status_raw, "code": None}
        else:
            # status = 'Unknown'
            ret_code = {"msg": status_raw, "code": job.get("ret_code").get("code")}
        job_dict = {
            "job_name": job.get("job_name"),
            "owner": job.get("owner"),
            "job_id": job.get("job_id"),
            "system": job.get("system"),
            "subsystem": job.get("subsystem"),
            "ret_code": ret_code,
        }
        jobs.append(job_dict)
    return jobs


def main():
    run_module()


if __name__ == "__main__":
    main()
