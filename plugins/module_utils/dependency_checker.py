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
import sys
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version
from zoautil_py import zsystem

__metaclass__ = type

# ------------------------------
# Compatibility Matrix by Collection Version
# ------------------------------
# Keyed by collection version for easier lookup
COMPATIBILITY_MATRIX = {
    "2.0.0": {  # Update this when collection version changes
        "zoau_version": "1.4.0",
        "python_version": "3.12",
        "min_zos_version": 2.5,
        "max_zos_version": 3.1,
    },
    "1.12.0": {
        "zoau_version": "1.3.5",
        "python_version": "3.12",
        "min_zos_version": 2.5,
        "max_zos_version": 3.1,
    },
}

# ------------------------------
# Version Fetchers
# ------------------------------
def get_zoau_version(module=None):
    """Return ZOAU version as a string, e.g., '1.4.0'"""
    try:
        from zoautil_py import ZOAU_API_VERSION
        return ZOAU_API_VERSION
    except ImportError:
        if module:
            module.fail_json(msg="ZOAU Python API not found")
        return None

def get_python_version_info():
    return sys.version_info.major, sys.version_info.minor

def get_python_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.0"

def get_zos_version(module=None):
    """
    Fetch z/OS version using ZOAU Python API.
    Returns a string like '2.5' or None if unavailable.
    """
    try:
        sys_info = zsystem.zinfo("sys", json_format=True)
        sys_data = sys_info.get("data", {}).get("sys_info", {})
        version = sys_data.get("product_version")
        release = sys_data.get("product_release")
        if version and release:
            return f"{int(version)}.{int(release)}"
    except Exception as e:
        if module:
            module.fail_json(msg=f"Failed to fetch z/OS version: {e}")
        return None

# ------------------------------
# Dependency Validation
# ------------------------------
def validate_dependencies(module):
    zoau_version = get_zoau_version(module)
    python_major, python_minor = get_python_version_info()
    python_version_str = get_python_version()
    zos_version_str = get_zos_version(module)
    collection_version = version.__version__

    # Check if any versions are missing
    if not all([zoau_version, zos_version_str, collection_version]):
        module.fail_json(
            msg=" Missing one or more required versions (ZOAU, Python, z/OS, Collection Version)."
        )

    # Convert z/OS to float for comparison
    try:
        zos_version = float(zos_version_str)
    except Exception:
        module.fail_json(msg=f"Unable to parse z/OS version: {zos_version_str}")

    # Get compatibility info for the current collection version
    compat = COMPATIBILITY_MATRIX.get(collection_version)
    if not compat:
        module.fail_json(msg=f" No compatibility information for collection version: {collection_version}")

    row_py_major, row_py_minor = map(int, compat["python_version"].split("."))

    # Validate compatibility
    if (
        compat["zoau_version"] != zoau_version
        or row_py_major != python_major
        or row_py_minor != python_minor
        or not (compat["min_zos_version"] <= zos_version <= compat["max_zos_version"])
    ):
        module.fail_json(
            msg=(
                f" Incompatible configuration detected:\n"
                f"   ZOAU: {zoau_version} (expected {compat['zoau_version']})\n"
                f"   Python: {python_version_str} (expected {compat['python_version']})\n"
                f"   z/OS: {zos_version_str} (expected {compat['min_zos_version']}-{compat['max_zos_version']})\n"
                f"   Collection Version: {collection_version}"
            )
        )

    module.exit_json(
        msg=(
            f" Dependency compatibility check passed: "
            f"ZOAU {zoau_version}, Python {python_version_str}, "
            f"z/OS {zos_version_str}, Collection Version {collection_version}"
        )
    )
