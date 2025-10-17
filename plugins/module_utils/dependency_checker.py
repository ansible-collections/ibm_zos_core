# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0

from __future__ import absolute_import, division, print_function
import re
import subprocess
import sys
import json

__metaclass__ = type

# ------------------------------
# Compatibility Matrix
# ------------------------------
COMPATIBILITY_MATRIX = [
    {"zoau_version": "1.3.5", "python_version": "3.12", "galaxy_core_version": "1.12.0", "zos_range": "2.5-3.1"},
    {"zoau_version": "1.3.5.1", "python_version": "3.10", "galaxy_core_version": "1.12.0", "zos_range": "2.5-3.1"},
    {"zoau_version": "1.3.6.0", "python_version": "3.10", "galaxy_core_version": "1.10.1", "zos_range": "2.5-3.1"},
    {"zoau_version": "1.4.0", "python_version": "3.11", "galaxy_core_version": "1.11.0", "zos_range": "2.5-3.1"},
    {"zoau_version": "1.4.0", "python_version": "3.11", "galaxy_core_version": "1.12.0", "zos_range": "2.5-3.1"},
]

# ------------------------------
# Helpers
# ------------------------------
def run_command(module, cmd):
    rc, out, err = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg=f"Command failed: {cmd}", stdout=out, stderr=err)
    return out.strip()

# ------------------------------
# Version Fetchers
# ------------------------------
def get_zoau_version(module):
    output = run_command(module, "zoaversion")
    match = re.search(r'v(\d+\.\d+\.\d+(?:\.\d+)?)', output)
    return match.group(1) if match else None

def get_python_version_info():
    return sys.version_info.major, sys.version_info.minor

def get_python_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.0"

def get_zos_version(module):
    output = run_command(module, "zinfo -t sys -j")
    try:
        data = json.loads(output)
        sys_info = data.get("data", {}).get("sys_info", {})
        version = sys_info.get("product_version")
        release = sys_info.get("product_release")
        if version and release:
            return f"{int(version)}.{int(release)}"
    except json.JSONDecodeError:
        match_ver = re.search(r'"product_version":"(\d+)"', output)
        match_rel = re.search(r'"product_release":"(\d+)"', output)
        if match_ver and match_rel:
            return f"{int(match_ver.group(1))}.{int(match_rel.group(1))}"
    return None

def get_galaxy_core_version():
    try:
        result = subprocess.run(
            ["ansible-galaxy", "collection", "list", "ibm.ibm_zos_core"],
            capture_output=True,
            text=True,
            check=True
        )
        match = re.search(r'ibm\.ibm_zos_core\s+([0-9.]+)', result.stdout)
        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        return None
    return None

# ------------------------------
# Validation
# ------------------------------
def validate_dependencies(module):
    zoau_version = get_zoau_version(module)
    python_major, python_minor = get_python_version_info()
    python_version_str = get_python_version()
    zos_version = get_zos_version(module)
    galaxy_core_version = get_galaxy_core_version()

    if not all([zoau_version, zos_version, galaxy_core_version]):
        module.fail_json(msg=" Missing one or more required versions (ZOAU, Python, z/OS, Galaxy Core).")

    try:
        current_zos = float(zos_version)
    except (ValueError, TypeError):
        module.fail_json(msg=f"Unable to parse z/OS version: {zos_version}")

    for row in COMPATIBILITY_MATRIX:
        if "zos_range" in row:
            try:
                zos_min, zos_max = map(float, row["zos_range"].split("-"))
            except ValueError:
                continue
            if not (zos_min <= current_zos <= zos_max):
                continue

        row_py_major, row_py_minor = map(int, row["python_version"].split("."))
        if (row["zoau_version"].strip() == zoau_version.strip() and
            row_py_major == python_major and
            row_py_minor == python_minor and
            str(row["galaxy_core_version"]).strip() == str(galaxy_core_version).strip()):
            module.exit_json(
                msg=f" Dependency compatibility check passed: "
                f"ZOAU {zoau_version}, Python {python_version_str}, z/OS {zos_version}, Galaxy Core {galaxy_core_version}"
           )


    module.fail_json(
        msg=(
            f" Incompatible configuration detected:\n"
            f"   ZOAU: {zoau_version}\n"
            f"   Python: {python_version_str}\n"
            f"   z/OS: {zos_version}\n"
            f"   Galaxy Core: {galaxy_core_version}"
        )
    )
