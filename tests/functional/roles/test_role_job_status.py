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

def test_my_role_with_vars(ansible_zos_module):
    hosts = ansible_zos_module

    jobs = hosts.all.zos_job_query(job_id="*", owner="*")
    for job in jobs.contacted.values():
        job_id = job.get("jobs")[0].get("job_id")

    hosts.all.set_fact(job_id=job_id)
    results = hosts.all.include_role(name="job_status")
    for result in results.contacted.values():
        assert result.get("msg").get("job_active") is not None
        assert result.get("msg").get("job_status") is not None
