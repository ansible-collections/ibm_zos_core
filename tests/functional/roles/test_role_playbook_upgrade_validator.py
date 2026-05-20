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
    - name: Tag script file
      ansible.builtin.shell: "chtag -tc iso8859-1 /tmp/local_script.sh"
      args:
        executable: /bin/sh
      register: tag_result
    - name: Run local script
      shell: "/tmp/local_script.sh"
      register: output
    - name: print local script output.
      debug:
        var: output
    - name: Mount filesystem with old persistent options
      zos_mount:
        src: USER.ZFS.DATASET
        path: /mnt/myfs
        fs_type: zfs
        state: mounted
        persistent:
          data_store: USER.PARMLIB(BPXPRM00)
          comment: "My filesystem mount"
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
      - name: Mount filesystem with old persistent options
        zos_mount:
          src: USER.ZFS.DATASET
          path: /mnt/myfs
          fs_type: zfs
          state: mounted
          persistent:
            data_store: USER.PARMLIB(BPXPRM00)
            comment: "My filesystem mount"
"""

test_playbook3 = """---
- name: Submit job with removed location parameter
  zos_job_submit:
    src: SAMPLE.SEQ.DATA.SET
    location: data_set
    wait_time_s: 100
    volume: 222222
  register: job_result

- name: Copy file with removed parameters
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

- name: Mount filesystem with removed parameters
  zos_mount:
    src: USER.DATA.SET
    path: /mnt/data
    persistent:
      data_store: BPXPRM
      comment: "Test mount"
      addDataset: present

- name: Find data sets with removed parameter
  zos_find:
    patterns: "USER.*.DATA"
    pds_pattern: "MEM*"
    age: "2d"
  register: find_result
"""

test_playbook4 = """---
- name: Exercise remaining migration mappings
  hosts: zos_host
  gather_facts: false
  environment: "{{ environment_vars }}"
  collections:
    - ibm.ibm_zos_core
  tasks:
    - name: Backup restore with old nested option names
      zos_backup_restore:
        operation: backup
        data_sets:
          include:
            - USER.TEST.DATA
        backup_name: USER.TEST.BACKUP
        sms_storage_class: TESTSC
        sms_management_class: TESTMC
        hlq: USERHLQ

    - name: Fetch with old binary option
      zos_fetch:
        src: USER.DATA.SET
        dest: /tmp/
        is_binary: true
        flat: true

    - name: Query job output with old ddname option
      zos_job_output:
        job_id: "JOB12345"
        ddname: "JESMSGLG"

    - name: Run operator command with old wait_time_s
      zos_operator:
        cmd: "D A,L"
        wait_time_s: 5

    - name: Query operator actions with old option names
      zos_operator_action_query:
        job_name: "MYJOB*"
        message_id: "IEE*"
        message_filter:
          filter: ".*ERROR.*"
          use_regex: true

    - name: Unarchive with old nested format options
      zos_unarchive:
        src: USER.ARCHIVE.TRS
        dest: USER.RESTORED.DATA
        format:
          name: terse
          format_options:
            use_adrdssu: true
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
            assert "task_line" in issue, "Each issue should have 'task_line' field"
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

        # Verify expected removed/renamed parameters are detected
        assert any("force" in action for action in zos_copy_actions), "Should detect 'force' parameter issue"
        assert any("force_lock" in action for action in zos_copy_actions), "Should detect 'force_lock' parameter issue"
        assert any("is_binary" in action for action in zos_copy_actions), "Should detect 'is_binary' parameter issue"

        # Validate zos_mount issues
        zos_mount_issues = [i for i in report_data if i["module"] == "zos_mount"]
        assert len(zos_mount_issues) > 0, "Should detect zos_mount issues"

        # Validate zos_archive issues
        zos_archive_issues = [i for i in report_data if i["module"] == "zos_archive"]
        assert len(zos_archive_issues) > 0, "Should detect zos_archive issues"

        print("\n Report validation successful!")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   zos_copy issues: {len(zos_copy_issues)}")
        print(f"   zos_mount issues: {len(zos_mount_issues)}")
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

        # Check for specific removed parameters in zos_job_submit
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

        # Validate zos_find issues
        zos_find_issues = [i for i in report_data if i["module"] == "zos_find"]
        assert len(zos_find_issues) > 0, "Should detect zos_find issues"

        find_actions = []
        for issue in zos_find_issues:
            find_actions.extend(issue["migration_actions"])

        assert any("pds_pattern" in action for action in find_actions), "Should detect 'pds_pattern' parameter"

        print("\n Taskfile validation successful!")
        print(f"   File tested: {taskfile}")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   zos_job_submit issues: {len(zos_job_submit_issues)}")
        print(f"   zos_copy issues: {len(zos_copy_issues)}")
        print(f"   zos_mount issues: {len(zos_mount_issues)}")
        print(f"   zos_find issues: {len(zos_find_issues)}")

    finally:
        shutil.rmtree(playbooks_path)


def test_validator_role_with_other_modules_playbook(ansible_zos_module):
    """Test validator with another playbook covering other configured modules."""
    hosts = ansible_zos_module
    playbooks_path = "/tmp/" + datetime.now().strftime("%S%f") + "_pb_other"
    report_file = playbooks_path + "/other_modules_report.json"

    try:
        os.mkdir(playbooks_path)
        playbook_file = os.path.join(playbooks_path, "other_modules_playbook.yml")

        with open(playbook_file, "w") as f:
            f.write(test_playbook4)

        hosts.all.set_fact(playbook_path=playbook_file)
        hosts.all.set_fact(output_path=report_file)
        hosts.all.set_fact(ignore_response_params=False)
        results = hosts.all.include_role(name="playbook_upgrade_validator", apply=dict(delegate_to="localhost"))

        for result in results.contacted.values():
            print(result)
            assert result.get("changed") is False
            assert result.get("msg") is not None

        assert os.path.exists(report_file), f"Report file {report_file} was not created"

        with open(report_file, "r") as f:
            report_data = json.load(f)

        assert isinstance(report_data, list), "Report should be a list of issues"
        assert len(report_data) > 0, "Report should contain migration issues from other modules playbook"

        modules_found = set(issue["module"] for issue in report_data)
        expected_modules = {
            "zos_backup_restore",
            "zos_fetch",
            "zos_job_output",
            "zos_operator",
            "zos_operator_action_query",
            "zos_unarchive",
        }
        assert expected_modules.issubset(modules_found), (
            "Should detect all expected other-module coverage: "
            f"{sorted(expected_modules - modules_found)}"
        )

        backup_restore_actions = []
        for issue in report_data:
            if issue["module"] == "zos_backup_restore":
                backup_restore_actions.extend(issue["migration_actions"])
        assert any("hlq" in action for action in backup_restore_actions), "Should detect 'hlq' parameter"
        assert any("sms_storage_class" in action for action in backup_restore_actions), "Should detect 'sms_storage_class' parameter"
        assert any("sms_management_class" in action for action in backup_restore_actions), "Should detect 'sms_management_class' parameter"

        fetch_actions = []
        for issue in report_data:
            if issue["module"] == "zos_fetch":
                fetch_actions.extend(issue["migration_actions"])
        assert any("is_binary" in action for action in fetch_actions), "Should detect 'is_binary' parameter"

        job_output_actions = []
        for issue in report_data:
            if issue["module"] == "zos_job_output":
                job_output_actions.extend(issue["migration_actions"])
        assert any("ddname" in action for action in job_output_actions), "Should detect 'ddname' parameter"

        operator_actions = []
        for issue in report_data:
            if issue["module"] == "zos_operator":
                operator_actions.extend(issue["migration_actions"])
        assert any("wait_time_s" in action for action in operator_actions), "Should detect 'wait_time_s' parameter"

        operator_action_query_actions = []
        for issue in report_data:
            if issue["module"] == "zos_operator_action_query":
                operator_action_query_actions.extend(issue["migration_actions"])
        assert any("message_id" in action for action in operator_action_query_actions), "Should detect 'message_id' parameter"
        assert any("message_filter" in action for action in operator_action_query_actions), "Should detect 'message_filter' parameter"
        assert any("use_regex" in action for action in operator_action_query_actions), "Should detect 'use_regex' parameter"

        unarchive_actions = []
        for issue in report_data:
            if issue["module"] == "zos_unarchive":
                unarchive_actions.extend(issue["migration_actions"])
        assert any("format.name" in action for action in unarchive_actions), "Should detect 'format.name' parameter"
        assert any("format.format_options" in action for action in unarchive_actions), "Should detect 'format.format_options' parameter"
        assert any("use_adrdssu" in action for action in unarchive_actions), "Should detect 'use_adrdssu' parameter"


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
        assert "zos_mount" in modules_found, "Should detect zos_mount in single file"
        assert "zos_archive" in modules_found, "Should detect zos_archive in single file"

        print("\n Single file validation successful!")
        print(f"   File tested: {playbook_file}")
        print(f"   Total issues found: {len(report_data)}")
        print(f"   Modules with issues: {', '.join(sorted(modules_found))}")

    finally:
        shutil.rmtree(playbooks_path)
