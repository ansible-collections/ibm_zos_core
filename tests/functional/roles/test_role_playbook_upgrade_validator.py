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

import tempfile
import os
import shutil
from datetime import datetime
__metaclass__ = type

test_playbook1 = """---
- name: Execute z/OS modules
  hosts: zos_host
  gather_facts: false
  environment: "{{ environment_vars }}"
  collections:
    - ibm.ibm_zos_core
  tasks:
    - name: copy file to z/os
      zos_copy:
        src: "./script.sh"
        dest: "/tmp/local_script.sh"
        force: true
        mode: "0755"
        remote_src: false
        force_lock: true
        encoding:
          from: ISO8859-1
          to: IBM-1047
        is_binary: false
      register: file_content
    - name: Taging script file 
      ansible.builtin.shell: "chtag -tc iso8859-1 /tmp/local_script.sh"
      args:
        executable: /bin/sh
      register: tag_result
    - name: List data sets matching pattern in catalog
      shell: "/tmp/local_script.sh"
      register: output
    - name: debug
      debug:
        var: output
    - name: Execute started task display command
      zos_blockinfile:
        src: "ansible.tester.sampl(mem1)"
        insertafter: 'EOF'
        block: |
          PRODUCT OWNER('IBM CORP')
          NAME('IBM IDz')
          ID(5724-T07)
          VERSION(*)
          RELEASE(*)
          MOD(*)
          FEATURENAME(*)
          STATE(ENABLED)
    - name: Archive data set into a terse, specify pack algorithm and use adrdssu
      zos_archive:
        src: "USER.ARCHIVE.TEST"
        dest: "USER.ARCHIVE.RESULT.TRS"
        format:
          name: terse
          format_options:
            terse_pack: "spack"
            use_adrdssu: true
    - name: Convert local JCL to IBM-037 and submit the job.
      zos_job_submit:
        src: ANSIBLE.TEST.JCLSCR
      register: job_id_test
    - name: Retrieve job output and check for step 34
      ibm.ibm_zos_core.zos_job_output:
        job_id: "JOB123456"
        job_name: "TESTJOB"
      register: job_output
"""

test_playbook2 = """- hosts: zos_host
  collections:
    - ibm.ibm_zos_core
  gather_facts: false
  environment: "{{ environment_vars }}"
  tasks:
      - name: Execute started task display command
        zos_blockinfile:
          src: "ansible.tester.sampl(mem1)"
          insertafter: 'EOF'
          block: |
            PRODUCT OWNER('IBM CORP')
            NAME('IBM IDz')
            ID(5724-T07)
            VERSION(*)
            RELEASE(*)
            MOD(*)
            FEATURENAME(*)
            STATE(ENABLED)
"""

def test_validator_role_with_vars(ansible_zos_module):
    hosts = ansible_zos_module
    playbooks_path = "/tmp/" + datetime.now().strftime("%S%f") + "_pb"
    try:
      os.mkdir(playbooks_path)
      playbook1 = tempfile.NamedTemporaryFile(delete=True, dir=playbooks_path).name + ".yml"
      playbook2 = tempfile.NamedTemporaryFile(delete=True, dir=playbooks_path).name + ".yml"

      with open(playbook1, "w") as f:
        f.write(test_playbook1)
      with open(playbook2, "w") as f:
        f.write(test_playbook2)

      hosts.all.set_fact(playbook_path=playbooks_path)
      hosts.all.set_fact(output_path=playbooks_path + "/migration_reports.json")
      hosts.all.set_fact(ignore_response_params=False)
      results = hosts.all.include_role(name="playbook_upgrade_validator", apply=dict(delegate_to="localhost"))
      for result in results.contacted.values():
          print(result)
          assert result.get("msg").get("changed") is False
          assert result.get("msg").get("playbook_path") is not None
          assert result.get("msg").get("output_path") is not None
          assert len(result.get("msg").get("results")) == 6
    finally:
       shutil.rmtree(playbooks_path)
