# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025
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

import pytest
__metaclass__ = type

def test_job_status_setting_vars(ansible_zos_module):
    hosts = ansible_zos_module

    jobs = hosts.all.zos_job_query(job_id="*", owner="*")
    for job in jobs.contacted.values():
        job_id = job.get("jobs")[0].get("job_id")

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") is not None
        assert result.get("msg").get("job_status") is not None

def test_job_status_CC(ansible_zos_module):
    hosts = ansible_zos_module

    jobs = hosts.all.zos_job_query(job_id="*", owner="*")
    for job in jobs.contacted.values():
        jobs = job.get("jobs")
    
    for job in jobs:
        rc = job.get("ret_code")
        if rc.get("msg_txt") == "CC":
            job_id = job.get("job_id")
            break

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") is False
        assert result.get("msg").get("job_status") == "CC"

def test_job_status_AC(ansible_zos_module):
    hosts = ansible_zos_module

    jobs = hosts.all.zos_job_query(job_id="*", owner="*")
    for job in jobs.contacted.values():
        jobs = job.get("jobs")
    
    for job in jobs:
        rc = job.get("ret_code")
        if rc.get("msg_txt") == "AC":
            job_id = job.get("job_id")
            break

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") is True
        assert result.get("msg").get("job_status") == "AC"

def test_job_status_NOEXEC(ansible_zos_module):
    hosts = ansible_zos_module

    jobs = hosts.all.zos_job_query(job_id="*", owner="*")
    for job in jobs.contacted.values():
        jobs = job.get("jobs")
    
    for job in jobs:
        rc = job.get("ret_code")
        if rc.get("msg_txt") == "NOEXEC":
            job_id = job.get("job_id")
            break

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") is False
        assert result.get("msg").get("job_status") == "NOEXEC"

def test_job_status_job_id_does_not_exist(ansible_zos_module):
    hosts = ansible_zos_module

    job_id = "NOJOBID"

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") == "JOB_NOT_FOUND"
        assert result.get("msg").get("job_status") == "JOB_NOT_FOUND" 
