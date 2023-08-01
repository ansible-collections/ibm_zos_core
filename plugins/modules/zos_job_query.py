#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020, 2023
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
module: zos_job_query
version_added: '1.0.0'
short_description: Query job status
description:
  - List z/OS job(s) and the current status of the job(s).
  - Uses job_name to filter the jobs by the job name.
  - Uses job_id to filter the jobs by the job identifier.
  - Uses owner to filter the jobs by the job owner.
  - Uses system to filter the jobs by system where the job is running (or ran) on.
author:
  - "Ping Xiao (@xiaopingBJ)"
  - "Demetrios Dimatos (@ddimatos)"
  - "Rich Parker (@richp405)"
options:
  job_name:
    description:
       - The job name to query.
       - A job name can be up to 8 characters long.
       - The I(job_name) can contain include multiple wildcards.
       - The asterisk (`*`) wildcard will match zero or more specified characters.
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
      - The job id that has been assigned to the job.
      - A job id must begin with `STC`, `JOB`, `TSU` and are
        followed by up to 5 digits.
      - When a job id is greater than 99,999, the job id format will begin
        with `S`, `J`, `T` and are followed by 7 digits.
      - The I(job_id) can contain include multiple wildcards.
      - The asterisk (`*`) wildcard will match zero or more specified characters.
    type: str
    required: False
"""

EXAMPLES = r"""
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
    If no job status is found, this will return ret_code dictionary with
    parameter msg_txt = The job could not be found.
  returned: success
  type: list
  elements: dict
  contains:
    job_name:
      description:
         The name of the batch job.
      type: str
      sample: LINKJOB
    owner:
      description:
         The owner who ran the job.
      type: str
      sample: ADMIN
    job_id:
      description:
         Unique job identifier assigned to the job by JES.
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
              type: int
              sample: 0

      sample:
        ret_code: {
         "msg": "CC 0000",
         "msg_code": "0000",
         "msg_txt": "",
         "code": 0,
         "steps": [
            { "step_name": "STEP0001",
              "step_cc": 0
            }
          ]
        }
    job_class:
      description:
        Job class for this job.
      type: str
      sample: A
    svc_class:
      description:
        Service class for this job.
      type: str
      sample: C
    priority:
      description:
        A numeric indicator of the job priority assigned through JES.
      type: int
      sample: 4
    asid:
      description:
        The address Space Identifier (ASID) that is a unique descriptor for the job address space.
        Zero if not active.
      type: int
      sample: 0
    creation_date:
      description:
        Date, local to the target system, when the job was created.
      type: str
      sample: "2023-05-04"
    creation_time:
      description:
        Time, local to the target system, when the job was created.
      type: str
      sample: "14:15:00"
    queue_position:
      description:
        The position within the job queue where the jobs resides.
      type: int
      sample: 3
    program_name:
      description:
        The name of the program found in the job's last completed step found in the PGM parameter.
        Returned when Z Open Automation Utilities (ZOAU) is 1.2.4 or later.
      type: str
      sample: "IEBGENER"

  sample:
    [
        {
            "job_name": "LINKJOB",
            "owner": "ADMIN",
            "job_id": "JOB01427",
            "ret_code": "null",
            "job_class": "K",
            "svc_class": "?",
            "priority": 1,
            "asid": 0,
            "creation_date": "2023-05-03",
            "creation_time": "12:13:00",
            "queue_position": 3,
        },
        {
            "job_name": "LINKCBL",
            "owner": "ADMIN",
            "job_id": "JOB16577",
            "ret_code": { "msg": "CANCELED", "code": "null" },
            "job_class": "A",
            "svc_class": "E",
            "priority": 0,
            "asid": 4,
            "creation_date": "2023-05-03",
            "creation_time": "12:14:00",
            "queue_position": 0,
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

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.job import (
    job_status,
)

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
        name, id, owner = validate_arguments(module.params)
        jobs_raw = query_jobs(name, id, owner)
        if jobs_raw:
            jobs = parsing_jobs(jobs_raw)
        else:
            jobs = None

    except Exception as e:
        module.fail_json(msg=e, **result)
    result["jobs"] = jobs
    module.exit_json(**result)


# validate_arguments returns a tuple, so we don't have to rebuild the job_name string
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
            test_basic = job_name_pattern.search(job_name_in)
            test_star = job_name_pattern_with_star.search(job_name_in)
            # logic twist: test_result should be a non-null value from test_basic or test_star
            test_result = test_basic
            if test_star:
                test_result = test_star

            job_name_short = "unused"
            # if neither test_basic nor test_star were non-null, check if the string needed to be truncated to the first *
            if not test_result:
                ix = job_name_in.find("*")
                if ix >= 0:
                    job_name_short = job_name_in[0:ix + 1]
                    test_result = job_name_pattern.search(job_name_short)
                    if not test_result:
                        test_result = job_name_pattern_with_star.search(job_name_short)

            # so now, fail if neither test_basic, test_star or test_base from job_name_short found a match
            if not test_result:
                raise RuntimeError("Unable to locate job name {0}.".format(job_name_in))

        if job_id:
            job_id_pattern = re.compile("(JOB|TSU|STC)[0-9]{5}|(J|T|S)[0-9]{7}$")
            test_basic = job_id_pattern.search(job_id)
            test_result = None

            if not test_basic:
                ix = job_id.find("*")
                if ix > 0:
                    # this differs from job_name, in that we'll drop the star for the search
                    job_id_short = job_id[0:ix]

                    if job_id_short[0:3] in ['JOB', 'TSU', 'STC'] or job_id_short[0:1] in ['J', 'T', 'S']:
                        test_result = job_id_short

            if not test_basic and not test_result:
                raise RuntimeError("Failed to validate the job id: " + job_id)
    else:
        raise RuntimeError("Argument Error:Either job name(s) or job id is required")
    if job_id and owner:
        raise RuntimeError("Argument Error:job id can not be co-exist with owner")

    return job_name_in, job_id, owner


def query_jobs(job_name, job_id, owner):

    jobs = []
    if job_id:
        jobs = job_status(job_id=job_id)
    elif owner:
        jobs = job_status(owner=owner, job_name=job_name)
    else:
        jobs = job_status(job_name=job_name)
    if not jobs:
        raise RuntimeError("List FAILED! no such job was found.")
    return jobs


def parsing_jobs(jobs_raw):
    jobs = []
    ret_code = {}
    for job in jobs_raw:
        # Easier to see than checking for an empty string, JOB NOT FOUND was
        # replaced with None in the jobs.py and msg_txt field describes the job query instead
        if job.get("ret_code") is None:
            status_raw = "JOB NOT FOUND"
        elif job.get("ret_code").get("msg", "JOB NOT FOUND") is None:
            status_raw = "JOB NOT FOUND"
        else:
            status_raw = job.get("ret_code").get("msg", "JOB NOT FOUND")

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

        elif "CANCELED" in status_raw or "JCLERR" in status_raw or "JCL ERROR" in status_raw or "JOB NOT FOUND" in status_raw:
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
            "job_class": job.get("job_class"),
            "svc_class": job.get("svc_class"),
            "priority": job.get("priority"),
            "asid": job.get("asid"),
            "creation_date": job.get("creation_date"),
            "creation_time": job.get("creation_time"),
            "queue_position": job.get("queue_position"),
            "program_name": job.get("program_name"),
        }
        jobs.append(job_dict)
    return jobs


def main():
    run_module()


if __name__ == "__main__":
    main()
