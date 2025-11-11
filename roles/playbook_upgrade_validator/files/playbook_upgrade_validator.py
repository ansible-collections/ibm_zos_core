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
__metaclass__ = type

DOCUMENTATION = r'''
---
module: playbook_upgrade_validator
version_added: "2.0.0"
author:
  - "Ravella Surendra Babu (@surendrababuravella)"
short_description: Validates playbooks against ibm_zos_core 2.0.0 and provides migration actions.
description:
  - Scans one or more Ansible playbooks to identify deprecated or renamed parameters
    based on migration rules for IBM z/OS Core collection version 2.0.0.
  - Provides line numbers, affected modules, and suggested corrective actions.
options:
  ignore_response_params:
    description:
      - Indicates whether information about response parameter changes should be included.
    default: false
    type: bool
  migration_map:
    description:
      - A structured set of migration rules that specifies deprecated, renamed, and modified parameters
        to help upgrade playbooks from ibm_zos_core 1.x.x to 2.0.0.
    required: true
    type: dict
  output_path:
    description:
      - Path to the output JSON file where results should be saved.
    required: true
    type: str
  playbook_path:
    description:
      - Path to the directory containing the Ansible playbooks to be validated.
    required: true
    type: str
notes:
  - Designed to assist migration of playbooks from older IBM z/OS core collection versions to 2.0.0.
  - Supports reading tasks, blocks, and nested includes.
'''

EXAMPLES = r'''
- name: execute playbook_upgrade_validator role to list migration changes
  include_role:
    name: ibm.ibm_zos_core.playbook_upgrade_validator
  vars:
    playbook_path: "/path/to/playbooks/*.yml"
    output_path: "/path/to/reports/validation_report.json"
    ignore_response_params: false
'''

RETURN = r'''
changed:
  description:
    - Always false as there are no state changes happening in this process.
  returned: always
  type: bool
output_path:
  description: Path to the output JSON file containing validation results.
  returned: always
  type: str
playbook_path:
  description: The path to the directory containing the Ansible playbooks to be validated.
  returned: always
  type: str
results:
  description: List of issues identified in all scanned playbooks, along with detailed information.
  returned: always
  type: list
  sample:
    [
        {
            "line": 9,
            "migration_actions": [
                "[MUST_FIX] Param 'force_lock' is renamed to 'force' in zos_copy",
                "[MUST_FIX] Param 'is_binary' is renamed to 'binary' in zos_copy",
                "[MUST_FIX] Param 'force' is renamed to 'replace' in zos_copy"
            ],
            "module": "zos_copy",
            "play_name": "Execute z/OS modules",
            "playbook": "/path/to/playbook/copy_file.yml",
            "task_name": "copy file to z/os"
        }
    ]
'''

import os
import argparse
import json
import sys


def load_playbook(path):
    """Load playbook YAML and preserve line numbers."""
    try:
        from ruamel.yaml import YAML
    except ImportError:
        raise ImportError(
            "This module requires 'ruamel.yaml'. Please install it using 'pip install ruamel.yaml'."
        )

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
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
            (
                k for k in task.keys()
                if k not in [
                    "name", "register", "vars", "when", "tags", "args",
                    "block", "rescue", "always", "delegate_to", "environment",
                    "become", "notify", "loop", "with_items", "with_dict"
                ]
            ),
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
        yield from walk_tasks(play.get("tasks", []), play_name)


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
    parser = argparse.ArgumentParser(description="Sample Python script for z/OS Ansible role")
    parser.add_argument("--playbook_path", type=str, required=True)
    parser.add_argument("--migration_map", type=json.loads, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    parser.add_argument("--ignore_response_params", type=bool, default=False)

    args = parser.parse_args()

    playbook_path = args.playbook_path
    migration_map = args.migration_map
    output_path = args.output_path
    ignore_response_params = args.ignore_response_params
    all_results = []
    for root, dirs, files in os.walk(playbook_path):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                path = os.path.join(root, file)
                all_results.extend(validate_tasks(path, migration_map, ignore_response_params))

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as out:
            json.dump(all_results, out, indent=2)
    except Exception as e:
        print(json.dumps({
            "failed": True,
            "msg": f"Failed to write output to file: {str(e)}"
        }), file=sys.stderr)
        sys.exit(1)

    result = {
        "playbook_path": playbook_path,
        "output_path": output_path,
        "results": all_results
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
