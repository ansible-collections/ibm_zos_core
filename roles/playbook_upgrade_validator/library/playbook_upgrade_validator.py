#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023, 2025
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

DOCUMENTATION = r'''
---
module: playbook_upgrade_validator
version_added: "1.0.0"
author:
  - "Ravella Surendra Babu (@surendrababuravella)"
short_description: Validate playbooks against ibm_zos_core 2.0
description:
  - Scans one or more Ansible playbooks to identify deprecated or renamed parameters
    based on migration rules for IBM z/OS core collection version 2.0.
  - Provides line numbers, affected modules, and suggested corrective actions.
options:
  playbook_path:
    description:
      - List of Ansible playbook file paths to validate.
    required: true
    type: list
    elements: str
  migration_map:
    description:
      - Json which has migration changes for ibm_zos_core 2.0 modules.
    required: true
    type: dict
  output_path:
    description:
      - File path where validation results should be written in JSON format.
    required: true
    type: str
notes:
  - Designed to assist migration of playbooks from older IBM z/OS core collection versions to 2.0.
  - Supports reading tasks, blocks, and nested includes.
'''

EXAMPLES = r'''
- name: Validate all playbooks under test directory
  playbook_upgrade_validator:
    playbook_path: "{{ lookup('fileglob', '/path/to/playbooks/*.yml', wantlist=True) }}"
    migration_map: "<< migrating changes json >>"
    output_path: "{{ role_path }}/reports/validation_report.json"
'''

RETURN = r'''
output_path:
  description: Path where the validation report was written.
  returned: always
  type: str
results:
  description: List of all issues found across all playbooks.
  returned: always
  type: list
'''

from ansible.module_utils.basic import AnsibleModule
import os
import json
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True
yaml.allow_duplicate_keys = True


def load_playbook(path):
    """Load playbook YAML and preserve line numbers."""
    with open(path, "r") as f:
        data = yaml.load(f)
        if isinstance(data, dict):
            data = [data]
        return data


def get_line_number(obj):
    """Return YAML line number if available."""
    try:
        return obj.lc.line + 1
    except Exception:
        return None


def walk_tasks(tasks, play_name):
    """Recursively walk through tasks including block/rescue/always."""
    if not isinstance(tasks, list):
        return
    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_name = task.get("name", "unknown")

        # Identify the module name (skip non-module keys)
        module_name = next(
            (k for k in task.keys()
             if k not in [
                 "name", "register", "vars", "when", "tags", "args",
                 "block", "rescue", "always", "delegate_to", "environment",
                 "become", "notify", "loop", "with_items", "with_dict"
             ]),
            None
        )

        if module_name:
            yield {
                "play_name": play_name,
                "task_name": task_name,
                "module": module_name,
                "params": task.get(module_name, {}),
                "line": get_line_number(task)
            }

        # Recursive sections
        for section in ["block", "rescue", "always"]:
            if section in task:
                yield from walk_tasks(task[section], play_name)


def has_nested_key(data, dotted_key):
    """Check for nested key like param.subparam.name."""
    if not isinstance(data, dict):
        return False
    value = data
    for part in dotted_key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return False
    return True


def get_tasks_from_playbook(playbook_path):
    """Parse a playbook and extract module data."""
    playbook = load_playbook(playbook_path)
    if not isinstance(playbook, list):
        return []

    for play in playbook:
        if not isinstance(play, dict):
            continue
        play_name = play.get("name", "unknown")
        for task in walk_tasks(play.get("tasks", []), play_name):
            yield task


def validate_tasks(playbook_path, migration_map, ignore_response_params):
    """Check tasks for deprecated or renamed params."""
    results = []
    # playbook = load_playbook(playbook_path)

    for mod in get_tasks_from_playbook(playbook_path):
        module_name = mod["module"]
        issues = []
        params = mod.get("params", {})

        if "." in module_name:
            short_name = module_name.split(".")[-1]
        else:
            short_name = module_name
        details = migration_map.get(short_name, {})
        # 🔍 Process only for z/OS modules
        if not short_name.startswith("zos_"):
            continue

        # Deprecated params validation
        for param in details.get("deprecated_params", []):
            if has_nested_key(params, param):
                issues.append(f"[MUST_FIX] Param '{param}' is deprecated in {module_name}")

        # Renamed params validation
        for param, new_name in details.get("renamed_params", {}).items():
            if has_nested_key(params, param):
                issues.append(f"[MUST_FIX] Param '{param}' is renamed to '{new_name}' in {module_name}")

        # Type changed params validation
        for param, value in details.get("type_changed_params", {}).items():
            if has_nested_key(params, param):
                old_type, new_type = value.split("_", 1)
                issues.append(
                    f"[MUST_FIX] Param '{param}' type changed from '{old_type}' to '{new_type}' in {module_name}"
                )
        if not ignore_response_params:
            # Response parameters validation
            for param in details.get("deprecated_response_params", []):
                issues.append(f"[WARNING] Response param '{param}' is deprecated in {module_name}")

            # Renamed response params validation
            for param, new_name in details.get("renamed_response_params", {}).items():
                issues.append(f"[WARNING] Response param '{param}' is renamed to '{new_name}' in {module_name}")

        if issues:
            results.append({
                "playbook": playbook_path,
                "play_name": mod["play_name"],
                "task_name": mod["task_name"],
                "module": module_name,
                "line": mod["line"],
                "migration_actions": issues
            })
    return results


def main():
    module = AnsibleModule(
        argument_spec=dict(
            playbook_path=dict(type="str", required=True),
            migration_map=dict(type="dict", required=True),
            output_path=dict(type="str", required=True),
            ignore_response_params=dict(type="bool", default=False)
        ),
        supports_check_mode=True
    )

    playbook_path = module.params["playbook_path"]
    migration_map = module.params["migration_map"]
    output_path = module.params["output_path"]
    ignore_response_params = module.params["ignore_response_params"]
    all_results = []
    for root, _, files in os.walk(playbook_path):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                path = os.path.join(root, file)
                all_results.extend(validate_tasks(path, migration_map, ignore_response_params))

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as out:
            json.dump(all_results, out, indent=2)
    except Exception as e:
        module.fail_json(msg=f"Failed to write output into file: {str(e)}")

    module.exit_json(changed=False, playbook_path=playbook_path, output_path=output_path, results=all_results)


if __name__ == "__main__":
    main()
