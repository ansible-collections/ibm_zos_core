# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: zos_job_output
short_description: Display z/OS job output for a given criteria (Job id/Job name/owner) with or without a data definition name as a filter.
description:
    - Display the z/OS job output for a given criteria (Job id/Job name/owner) with/without a data definition name as a filter.
    - At least provide a job id/job name/owner.
    - The job id can be specific such as "STC02560", or one that uses a pattern such as "STC*" or "*".
    - The job name can be specific such as "TCPIP", or one that uses a pattern such as "TCP*" or "*".
    - The owner can be specific such as "IBMUSER", or one that uses a pattern like "*".
    - If there is no ddname, or if ddname="?", output of all the ddnames under the given job will be displayed.
version_added: "2.9"
author: "Jack Ho <jack.ho@ibm.com>"
options:
    job_id:
        description:
            - job Id. (e.g "STC02560", "STC*")
        type: str
        required: false
        version_added: "2.9"
    job_name:
        description:
            - job name. (e.g "TCPIP", "C*")
        required: false
        version_added: "2.9"
    owner:
        description:
            - The owner who runs job. (e.g "IBMUSER", "*")
        required: false
        version_added: "2.9"
    ddname:
        description:
            - Data definition name. (e.g "JESJCL", "?")
        type: str
        required: false
        version_added: "2.9"
'''
EXAMPLES = r'''
- name: Job output with ddname
  zos_job_output:
    job_id: "STC02560"
    ddname: "JESMSGLG"

- name: JES Job output without ddname
  zos_job_output:
    job_id: "STC02560"

- name: JES Job output with all ddnames
  zos_job_output:
    job_id: "STC*"
    job_name: "*"
    owner: "IBMUSER"
    ddname: "?"
'''
RETURN = '''
zos_job_output:
    description: list of job output.
    returned: success
    type: list[dict]
    contains:
        job_id:
            description: job ID
            type: str
        job_name:
            description: job name
            type: str
        subsystem:
            description: subsystem
            type: str
        class:
            description: class
            type: str
        content-type:
            description: content type
            type: str
        ddnames:
            description: list of data definition name
            type: list[dict]
            contains:
                ddname:
                    description: data definition name
                    type: str
                record-count:
                    description: record count
                    type: int
                id:
                    description: id
                    type: str
                stepname:
                    description: step name
                    type: str
                procstep:
                    description: proc step
                    type: str
                byte-count:
                    description: byte count
                    type: int
                content:
                    description: ddname content
                    type: list[str]
'''

import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.job import job_output
from os import chmod, path, remove
from tempfile import NamedTemporaryFile


def run_module():
    module_args = dict(
        job_id=dict(type='str', required=False),
        job_name=dict(type='str', required=False),
        owner=dict(type='str', required=False),
        ddname=dict(type='str', required=False),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    job_id = module.params.get("job_id") or ""
    job_name = module.params.get("job_name") or ""
    owner = module.params.get("owner") or ""
    ddname = module.params.get("ddname") or ""

    if not job_id and not job_name and not owner:
        module.fail_json(msg="Please provide a job_id or job_name or owner")

    try:
        job_detail_json = job_output(module, job_id, owner, job_name, ddname)
    except Exception as e:
        module.fail_json(msg=str(e))
    module.exit_json(zos_job_output=job_detail_json)


def main():
    run_module()


if __name__ == '__main__':
    main()
