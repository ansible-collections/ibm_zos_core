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
from packaging import version as v  # for version comparison

try:
    from zoautil_py import zsystem
except ImportError:
    zsystem = None

__metaclass__ = type

# ------------------------------------------------------------------------------
# Compatibility Matrix
# ------------------------------------------------------------------------------
COMPATIBILITY_MATRIX = {
    "2.0.0": [
        {"min_zoau_version": "1.4.0", "min_python_version": "3.12", "min_zos_version": 2.5},
    ],
    "2.1.0": [
        {"min_zoau_version": "1.4.1", "min_python_version": "3.12", "min_zos_version": 2.5},
    ],
    "2.2.0": [
        {"min_zoau_version": "1.4.2", "min_python_version": "3.12", "min_zos_version": 2.5},
    ],
}


# ------------------------------------------------------------------------------
# Version Fetchers
# ------------------------------------------------------------------------------
def get_zoau_version(module=None):
    try:
        from zoautil_py import ZOAU_API_VERSION
        return ZOAU_API_VERSION
    except ImportError:
        if module:
            module.fail_json(
                msg="Unable to import ZOAU. Please check PYTHONPATH, LIBPATH, ZOAU_HOME, and PATH environment variables."
            )
        return None


def get_python_version_info():
    return sys.version_info.major, sys.version_info.minor


def get_python_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.0"


def get_zos_version(module=None):
    if zsystem is None:
        if module:
            module.warn("Unable to import ZOAU zsystem module.")
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
            module.warn(f"Failed to fetch z/OS version: {e}")
        return None


# ------------------------------------------------------------------------------
# Dependency Validation
# ------------------------------------------------------------------------------
def validate_dependencies(module):
    """Validate that ZOAU, Python, and z/OS versions meet minimum requirements."""

    zoau_version = get_zoau_version(module)
    python_major, python_minor = get_python_version_info()
    python_version_str = get_python_version()
    zos_version_str = get_zos_version(module)
    collection_version = version.__version__

    if not all([zoau_version, zos_version_str, python_version_str, collection_version]):
        module.fail_json(
            msg="Unable to fetch one or more required dependencies. Dependencies checked are ZOAU, Python, z/OS."
        )

    # Convert z/OS version to float
    zos_version = None
    if zos_version_str:
        try:
            zos_version = float(zos_version_str)
        except Exception:
            module.warn(f"Unable to parse z/OS version: {zos_version_str}")

    compat_list = COMPATIBILITY_MATRIX.get(collection_version, [])
    if not compat_list:
        module.fail_json(msg=f"No compatibility information for collection version: {collection_version}")

    def parse_python_version(vs):
        return tuple(map(int, vs.split(".")))

    current_py = (python_major, python_minor)
    min_py = None
    min_zos = None
    matched_compat = None

    for compat in compat_list:
        if v.parse(zoau_version) >= v.parse(compat["min_zoau_version"]):
            matched_compat = compat
            min_py = parse_python_version(compat["min_python_version"])
            min_zos = compat["min_zos_version"]
            break

    if not min_py or not min_zos:
        required_zoau = compat_list[0]["min_zoau_version"]
        module.fail_json(
            msg=(
                f"Incompatible ZOAU version: {zoau_version}. "
                f"The minimum required version for this collection ({collection_version}) is {required_zoau}."
            )
        )

    # --- Validation thresholds ---
    warnings = []
    max_py = (3, 13)
    max_zos = 3.1

    # --- ZOAU check (hard fail if below min) ---
    if v.parse(zoau_version) < v.parse(matched_compat["min_zoau_version"]):
        module.fail_json(
            msg=f"Incompatible ZOAU version: {zoau_version}. Minimum supported is {matched_compat['min_zoau_version']}."
        )

    # --- Python checks ---
    if current_py < min_py:
        warnings.append(
            f"Python {python_version_str} is below the minimum tested version {matched_compat['min_python_version']}."
        )
    elif current_py > max_py:
        warnings.append(
            f"Python {python_version_str} exceeds the maximum tested version {max_py[0]}.{max_py[1]}."
        )

    # --- z/OS checks ---
    if zos_version is not None:
        if zos_version < min_zos:
            warnings.append(f"z/OS {zos_version_str} is below the minimum tested version {min_zos}.")
        elif zos_version > max_zos:
            warnings.append(f"z/OS {zos_version_str} exceeds the maximum tested version {max_zos}.")

    # --- Handle results ---
    if warnings:
        for w in warnings:
            module.warn(w)
        module.warn("Dependency check completed with warnings.")
    else:
        module.warn("Dependency compatibility check passed.")

    # Do not exit — allow module execution to continue
    return
