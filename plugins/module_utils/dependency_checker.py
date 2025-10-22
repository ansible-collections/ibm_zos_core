# -*- coding: utf-8 -*-
# Copyright (c) IBM Corporation 2025
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, division, print_function
import sys
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version
try:
    from zoautil_py import zsystem
except ImportError:
    zsystem = None


__metaclass__ = type

# ------------------------------------------------------------------------------
# Compatibility Matrix by Collection Version
# ------------------------------------------------------------------------------
# Define compatible versions of Python, ZOAU, and z/OS for each collection version.
COMPATIBILITY_MATRIX = {
    "2.0.0": [
        {"zoau_version": "1.4.0", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
        {"zoau_version": "1.4.1", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
        {"zoau_version": "1.4.2", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
    ],
    "2.1.0": [
        {"zoau_version": "1.4.1", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
        {"zoau_version": "1.4.2", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
    ],
    "2.2.0": [
        {"zoau_version": "1.4.2", "min_python_version": "3.12", "max_python_version": "3.13", "min_zos_version": 2.5, "max_zos_version": 3.1},
    ],
}

# ------------------------------------------------------------------------------
# Version Fetchers
# ------------------------------------------------------------------------------


def get_zoau_version(module=None):
    """Return ZOAU version as a string, e.g. '1.4.0'"""
    try:
        from zoautil_py import ZOAU_API_VERSION
        return ZOAU_API_VERSION
    except ImportError:
        if module:
            module.fail_json(msg="Unable to import ZOAU. Please check PYTHONPATH, LIBPATH, ZOAU_HOME and PATH environment variables.")
        return None


def get_python_version_info():
    """Return Python major and minor version as a tuple."""
    return sys.version_info.major, sys.version_info.minor


def get_python_version():
    """Return full Python version string (e.g. '3.12.0')."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.0"


def get_zos_version(module=None):
    """Fetch z/OS version using ZOAU Python API and return a string like '2.5'."""
    if zsystem is None:
        if module:
            module.fail_json(msg="Unable to import ZOAU. Please check PYTHONPATH, LIBPATH, ZOAU_HOME and PATH environment variables.")
        return None
    try:
        sys_info = zsystem.zinfo("sys", json_format=True)
        sys_data = sys_info.get("data", {}).get("sys_info", {})
        version = sys_data.get("product_version")
        release = sys_data.get("product_release")
        if version and release:
            return f"{int(version)}.{int(release)}"
    except Exception as e:
        if module:
            module.fail_json(msg=f" Failed to fetch z/OS version: {e}")
        return None


# ------------------------------------------------------------------------------
# Dependency Validation
# ------------------------------------------------------------------------------
def validate_dependencies(module):
    """Validate the runtime environment against compatibility requirements."""
    zoau_version = get_zoau_version(module)
    python_major, python_minor = get_python_version_info()
    python_version_str = get_python_version()
    zos_version_str = get_zos_version(module)
    collection_version = version.__version__

    # Ensure all versions are available
    if not all([zoau_version, zos_version_str, collection_version]):
        module.fail_json(
            msg=" Missing one or more required versions (ZOAU, Python, z/OS, Collection Version)."
        )

    # Convert z/OS version to float for comparison
    try:
        zos_version = float(zos_version_str)
    except Exception:
        module.fail_json(msg=f" Unable to parse z/OS version: {zos_version_str}")

    compat_list = COMPATIBILITY_MATRIX.get(collection_version, [])
    if not compat_list:
        module.fail_json(msg=f"No compatibility information for collection version: {collection_version}")

    # Helper to convert Python version string (e.g., '3.12') into tuple (3, 12)
    def parse_py(v):
        return tuple(map(int, v.split(".")))

    current_py = (python_major, python_minor)

    # Check if any entry in the list matches the current environment
    for compat in compat_list:
        min_py = parse_py(compat["min_python_version"])
        max_py = parse_py(compat["max_python_version"])

        if (
            compat["zoau_version"] == zoau_version
            and min_py <= current_py <= max_py
            and compat["min_zos_version"] <= zos_version <= compat["max_zos_version"]
        ):
            module.exit_json(
                msg=(
                    f" Dependency compatibility check passed: "
                    f"ZOAU {zoau_version}, Python {python_version_str}, "
                    f"z/OS {zos_version_str}, Collection Version {collection_version}"
                )
            )
    expected_py_ranges = [
        f"{compat['min_python_version']}-{compat['max_python_version']}"
        for compat in compat_list if compat['zoau_version'] == zoau_version
    ]
    expected_py_str = ", ".join(expected_py_ranges) if expected_py_ranges else "unknown"
    # If no matching entry was found
    module.fail_json(
        msg=(
            f"Incompatible configuration detected:\n"
            f"  ZOAU: {zoau_version}\n"
            f"  Python: {python_version_str} (expected {expected_py_str})\n"
            f"  z/OS: {zos_version_str}\n"
            f"  Collection Version: {collection_version}"
        )
    )

    module.exit_json(
        msg=(
            f" Dependency compatibility check passed: "
            f"ZOAU {zoau_version}, Python {python_version_str}, "
            f"z/OS {zos_version_str}, Collection Version {collection_version}"
        )
    )
