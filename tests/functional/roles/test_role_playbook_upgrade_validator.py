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
import json
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

test_playbook3 = """---
- name: Submit job with deprecated location parameter
  zos_job_submit:
    src: SAMPLE.SEQ.DATA.SET
    location: data_set
    wait_time_s: 100
    volume: 222222
  register: job_result

- name: Copy file with deprecated parameters
  zos_copy:
    src: /etc/config.txt
    dest: USER.DATA.SET
    is_binary: true
    force_lock: true
    force: true
  register: copy_result

- name: Add library to APF list
  zos_apf:
    library: CEE.SCEERUN
    force_dynamic: true
    persistent:
      data_set_name: USER.SYS1.PARMLIB(IEAAPF00)

- name: Mount filesystem with deprecated parameters
  zos_mount:
    src: USER.DATA.SET
    path: /mnt/data
    persistent:
      data_store: BPXPRM
      comment: "Test mount"
      addDataset: present

- name: Insert lines with deprecated parameter
  zos_lineinfile:
    src: USER.CONFIG.FILE
    line: "NEW_CONFIG=value"
    insertafter: "EOF"
  register: lineinfile_result
"""


def test_validator_role_with_vars(ansible_zos_module):
    hosts = ansible_zos_module
    playbooks_path = "/tmp/" + datetime.now().strftime("%S%f") + "_pb"
    report_file = playbooks_path + "/migration_reports.json"

    try:
        os.mkdir(playbooks_path)
        playbook1 = tempfile.NamedTemporaryFile(delete=True, dir=playbooks_path).name + ".yml"
        playbook2 = tempfile.NamedTemporaryFile(delete=True, dir=playbooks_path).name + ".yml"

        with open(playbook1, "w") as f:
            f.write(test_playbook1)
        with open(playbook2, "w") as f:
            f.write(test_playbook2)

        hosts.all.set_fact(playbook_path=playbooks_path)
        hosts.all.set_fact(output_path=report_file)
        hosts.all.set_fact(ignore_response_params=False)
        results = hosts.all.include_role(name="playbook_upgrade_validator", apply=dict(delegate_to="localhost"))

        # Validate role execution results
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("msg") is not None

        # Validate report file was created
        assert os.path.exists(report_file), f"Report file {report_file} was not created"

        # Validate report file content
        with open(report_file, "r") as f:
            report_data = json.load(f)

        # Assert report is a list
        assert isinstance(report_data, list), "Report should be a list of issues"

        # Assert report contains expected issues from test_playbook1
        assert len(report_data) > 0, "Report should contain at least one migration issue"

        # Validate structure of each issue
        for issue in report_data:
            assert "playbook" in issue, "Each issue should have 'playbook' field"
            assert "play_name" in issue, "Each issue should have 'play_name' field"
            assert "task_name" in issue, "Each issue should have 'task_name' field"
            assert "module" in issue, "Each issue should have 'module' field"
            assert "line" in issue, "Each issue should have 'line' field"
            assert "migration_actions" in issue, "Each issue should have 'migration_actions' field"
            assert isinstance(issue["migration_actions"], list), "migration_actions should be a list"
            assert len(issue["migration_actions"]) > 0, "migration_actions should not be empty"

        # Validate specific expected issues from test_playbook1
        zos_copy_issues = [i for i in report_data if i["module"] == "zos_copy"]
        assert len(zos_copy_issues) > 0, "Should detect zos_copy issues"

        # Check for specific parameter issues in zos_copy
        zos_copy_actions = []
        for issue in zos_copy_issues:
            zos_copy_actions.extend(issue["migration_actions"])

        # Verify expected deprecated/renamed parameters are detected
        assert any("force" in action for action in zos_copy_actions), "Should detect 'force' parameter issue"
        assert any("force_lock" in action for action in zos_copy_actions), "Should detect 'force_lock' parameter issue"
        assert any("is_binary" in action for action in zos_copy_actions), "Should detect 'is_binary' parameter issue"

        # Validate zos_blockinfile issues
        zos_blockinfile_issues = [i for i in report_data if i["module"] == "zos_blockinfile"]
        assert len(zos_blockinfile_issues) > 0, "Should detect zos_blockinfile issues"

        # Validate zos_archive issues
        zos_archive_issues = [i for i in report_data if i["module"] == "zos_archive"]
        assert len(zos_archive_issues) > 0, "Should detect zos_archive issues"

        print("\n Report validation successful!")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   zos_copy issues: {len(zos_copy_issues)}")
        print(f"   zos_blockinfile issues: {len(zos_blockinfile_issues)}")
        print(f"   zos_archive issues: {len(zos_archive_issues)}")

    finally:
        shutil.rmtree(playbooks_path)


def test_validator_role_with_taskfile(ansible_zos_module):
    """Test validator with a taskfile (direct task list without play structure)."""
    hosts = ansible_zos_module
    playbooks_path = "/tmp/" + datetime.now().strftime("%S%f") + "_pb_taskfile"
    report_file = playbooks_path + "/taskfile_report.json"

    try:
        os.mkdir(playbooks_path)
        taskfile = os.path.join(playbooks_path, "tasks.yml")

        # Create a taskfile with direct task list (no hosts/play structure)
        with open(taskfile, "w") as f:
            f.write(test_playbook3)

        # Test with taskfile
        hosts.all.set_fact(playbook_path=taskfile)
        hosts.all.set_fact(output_path=report_file)
        hosts.all.set_fact(ignore_response_params=False)
        results = hosts.all.include_role(name="playbook_upgrade_validator", apply=dict(delegate_to="localhost"))

        # Validate role execution results
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("msg") is not None

        # Validate report file was created
        assert os.path.exists(report_file), f"Report file {report_file} was not created"

        # Validate report file content
        with open(report_file, "r") as f:
            report_data = json.load(f)

        # Assert report is a list
        assert isinstance(report_data, list), "Report should be a list of issues"

        # Assert report contains issues from taskfile
        assert len(report_data) > 0, "Report should contain migration issues from taskfile"

        # Validate specific modules and their issues
        zos_job_submit_issues = [i for i in report_data if i["module"] == "zos_job_submit"]
        assert len(zos_job_submit_issues) > 0, "Should detect zos_job_submit issues"

        # Check for specific deprecated parameters in zos_job_submit
        job_submit_actions = []
        for issue in zos_job_submit_issues:
            job_submit_actions.extend(issue["migration_actions"])

        assert any("location" in action for action in job_submit_actions), "Should detect 'location' parameter"
        assert any("wait_time_s" in action for action in job_submit_actions), "Should detect 'wait_time_s' parameter"

        # Validate zos_copy issues
        zos_copy_issues = [i for i in report_data if i["module"] == "zos_copy"]
        assert len(zos_copy_issues) > 0, "Should detect zos_copy issues"

        copy_actions = []
        for issue in zos_copy_issues:
            copy_actions.extend(issue["migration_actions"])

        assert any("is_binary" in action for action in copy_actions), "Should detect 'is_binary' parameter"
        assert any("force_lock" in action for action in copy_actions), "Should detect 'force_lock' parameter"

        # Validate zos_mount issues
        zos_mount_issues = [i for i in report_data if i["module"] == "zos_mount"]
        assert len(zos_mount_issues) > 0, "Should detect zos_mount issues"

        # Validate zos_lineinfile issues
        zos_lineinfile_issues = [i for i in report_data if i["module"] == "zos_lineinfile"]
        assert len(zos_lineinfile_issues) > 0, "Should detect zos_lineinfile issues"

        lineinfile_actions = []
        for issue in zos_lineinfile_issues:
            lineinfile_actions.extend(issue["migration_actions"])

        assert any("insertafter" in action for action in lineinfile_actions), "Should detect 'insertafter' parameter"

        print("\n Taskfile validation successful!")
        print(f"   File tested: {taskfile}")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   zos_job_submit issues: {len(zos_job_submit_issues)}")
        print(f"   zos_copy issues: {len(zos_copy_issues)}")
        print(f"   zos_mount issues: {len(zos_mount_issues)}")
        print(f"   zos_lineinfile issues: {len(zos_lineinfile_issues)}")

    finally:
        shutil.rmtree(playbooks_path)


def test_validator_role_with_single_file(ansible_zos_module):
    """Test validator with a single playbook file path instead of directory."""
    hosts = ansible_zos_module
    playbooks_path = "/tmp/" + datetime.now().strftime("%S%f") + "_pb_single"
    report_file = playbooks_path + "/single_file_report.json"

    try:
        os.mkdir(playbooks_path)
        playbook_file = os.path.join(playbooks_path, "test_playbook.yml")

        # Create a single playbook file with known issues
        with open(playbook_file, "w") as f:
            f.write(test_playbook1)

        # Test with single file path instead of directory
        hosts.all.set_fact(playbook_path=playbook_file)
        hosts.all.set_fact(output_path=report_file)
        hosts.all.set_fact(ignore_response_params=False)
        results = hosts.all.include_role(name="playbook_upgrade_validator", apply=dict(delegate_to="localhost"))

        # Validate role execution results
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("msg") is not None

        # Validate report file was created
        assert os.path.exists(report_file), f"Report file {report_file} was not created"

        # Validate report file content
        with open(report_file, "r") as f:
            report_data = json.load(f)

        # Assert report is a list
        assert isinstance(report_data, list), "Report should be a list of issues"

        # Assert report contains issues from the single file
        assert len(report_data) > 0, "Report should contain migration issues from single file"

        # Validate all issues are from the single playbook file
        for issue in report_data:
            assert issue["playbook"] == playbook_file, f"Issue should be from {playbook_file}"
            assert "migration_actions" in issue
            assert len(issue["migration_actions"]) > 0

        # Validate specific modules are detected
        modules_found = set(issue["module"] for issue in report_data)
        assert "zos_copy" in modules_found, "Should detect zos_copy in single file"
        assert "zos_blockinfile" in modules_found, "Should detect zos_blockinfile in single file"
        assert "zos_archive" in modules_found, "Should detect zos_archive in single file"

        print("\n Single file validation successful!")
        print(f"   File tested: {playbook_file}")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   Modules with issues: {', '.join(sorted(modules_found))}")

    finally:
        shutil.rmtree(playbooks_path)
