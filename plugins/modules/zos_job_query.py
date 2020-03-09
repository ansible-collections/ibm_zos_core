#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: zos_job_query
short_description: The module allows you to list z/OS job(s) and the current status of the job(s).
description:
  - List z/OS job(s) and the current status of the job(s).
  - Uses owner to filter the jobs by the job owner.
  - Uses system to filter the jobs by system where the job is running (or ran) on.
  - Uses job_id to filter the jobs by the job id.

author: "Ping Xiao (@xiaopingBJ)"
options:
  job_name:
    description: The job name to query
    type: str
    required: False
    default: "*"
  owner:
    description:
      - Identifies the owner of the job.
      - Defaults to the current user
    type: str
    required: False
  job_id:
    description:
      - The job number that has been assigned to the job. These normally begin with STC, JOB, TSU and are followed by 5 digits.
    type: str
    required: False
seealso: []
notes:
  - check_mode is supported but in the case of this module, it never changes the system state so always return False
"""

EXAMPLES = """
- name: list zos jobs with a jobname 'IYK3ZNA1'
  zos_job_query:
    job_name: "IYK3ZNA1"

- Sample result('jobs' field):
    [
      {
        "job_name": "IYK3ZNA1",
        "owner": "BROWNAD",
        "job_id": "JOB01427",
        "ret_code": "null",
      },
    ]

- name: list the jobs matching jobname 'IYK3*'
  zos_job_query:
    job_name: "IYK3*"

- Sample result('jobs' field):
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

- name: list the job with a jobname 'IYK3ZNA*' and jobid as JOB01427
  zos_job_query:
    job_name: IYK3ZNA*
    job_id: JOB01427

- Sample result('jobs' field):
    [
      {
        "job_name": "IYK3ZNA1",
        "owner": "BROWNAD",
        "job_id": "JOB01427",
        "ret_code": "null",
      },
    ]

- name: list the job with a jobname 'IYK3ZNA*' and owner as BROWNAD
  zos_job_query:
    job_name: IYK3ZNA*
    owner: BROWNAD

- Sample result('jobs' field):
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
"""

RETURN = """
changed:
  description: True if the state was changed, otherwise False
  returned: always
  type: bool
failed:
  description: True if zos_job_query failed, otherwise False
  returned: always
  type: bool
jobs:
  description: The list z/OS job(s) and the current status of the job(s)
  returned: success
  type: list
  elements: dict
  contains:
    job_name:
      description: The name of the job
      type: str
    owner:
      description: The owner of the job
      type: str
    job_id:
      description: The ID of the job
      type: str
    ret_code:
      description: The return code information for the job
      type: dict
      contains:
        msg:
          description: Holds the return code (eg. "CC 0000")
          type: str
        code:
          description: Holds the return code string (eg. "00", "S0C4")
          type: str
message:
  description: Message returned on failure
  type: str
  returned: failure
  sample:
    - changed: false,
    - failed: false,
    - msg: "List FAILED! no such job been found: IYK3Z0R9"
original_message:
  description: The original input parameters
  type: str
  returned: always
"""

try:
    from zoautil_py import Jobs
except Exception:
    Jobs = ""
from ansible.module_utils.basic import AnsibleModule
import re


def run_module():

    module_args = dict(
        job_name=dict(type="str", required=False, default="*"),
        owner=dict(type="str", required=False),
        job_id=dict(type="str", required=False),
    )

    result = dict(changed=False, original_message="", message="")

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if module.check_mode:
        return result

    try:
        validate_arguments(module.params)
        jobs_raw = query_jobs(module.params)
        jobs = parsing_jobs(jobs_raw)
    except Exception as e:
        module.fail_json(msg=e, **result)
    result["original_message"] = module.params["job_name"]
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
            job_id_pattern = re.compile("(JOB|TSU|STC)[0-9]{5}$")
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
        jobs = Jobs.list(job_id=job_id)
    elif owner:
        jobs = Jobs.list(owner=owner, job_name=job_name_in)
    else:
        jobs = Jobs.list(job_name=job_name_in)
    if not jobs:
        raise RuntimeError("List FAILED! no such job name been found: " + job_name_in)
    return jobs


def parsing_jobs(jobs_raw):
    jobs = []
    status = ""
    ret_code = {}
    for job in jobs_raw:
        status_raw = job.get("status")
        if "AC" in status_raw:
            # the job is active
            ret_code = "null"
        elif "CC" in status_raw:
            # status = 'Completed normally'
            ret_code = {
                "msg": status_raw + " " + job.get("return"),
                "code": job.get("return"),
            }
        elif status_raw == "ABEND":
            # status = 'Ended abnormally'
            ret_code = {
                "msg": status_raw + " " + job.get("return"),
                "code": job.get("return"),
            }
        elif "ABENDU" in status_raw:
            # status = 'Ended abnormally'
            if job.get("return") == "?":
                ret_code = {"msg": status_raw, "code": status_raw[5:]}
            else:
                ret_code = {"msg": status_raw, "code": job.get("return")}
        elif "CANCELED" or "JCLERR" in status_raw:
            # status = status_raw
            ret_code = {"msg": status_raw, "code": "null"}
        else:
            # status = 'Unknown'
            ret_code = {"msg": status_raw, "code": job.get("return")}
        job_dict = {
            "job_name": job.get("name"),
            "owner": job.get("owner"),
            "job_id": job.get("id"),
            # 'job_status':status,
            "ret_code": ret_code,
        }
        jobs.append(job_dict)
    return jobs


def main():
    run_module()


if __name__ == "__main__":
    main()
