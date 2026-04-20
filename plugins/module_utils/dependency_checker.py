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
import re
import subprocess
import sys

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.log import SingletonLogger
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import version
logger = SingletonLogger().get_logger(verbosity=3)

__metaclass__ = type


# ------------------------------------------------------------------------------
# Compatibility Matrix by Collection Version
# ------------------------------------------------------------------------------
COMPATIBILITY_MATRIX = {
    "2.0.0":
        {"min_zoau_version": "1.4.0", "min_python_version": "3.12", "min_zos_version": "2.5" },
    "2.1.0":
        {"min_zoau_version": "1.4.1", "min_python_version": "3.12", "min_zos_version": "2.5" },
    "2.2.0":
        {"min_zoau_version": "1.4.2", "min_python_version": "3.12", "min_zos_version": "2.5" },
}


# ------------------------------------------------------------------------------
# Version conversion helper
# ------------------------------------------------------------------------------
def get_version_tuple(ver_str):
    """Convert version string like '1.4.2' to tuple (1,4,2) for comparison."""
    return tuple(int(x) for x in ver_str.split("."))


# ------------------------------------------------------------------------------
# Version Fetchers
# ------------------------------------------------------------------------------
def get_zoau_version_str(module=None):
    try:
        from zoautil_py import ZOAU_API_VERSION
        return ZOAU_API_VERSION
    except ImportError:
        if module:
            module.fail_json(
                msg="Unable to import ZOAU. Please check PYTHONPATH, LIBPATH, ZOAU_HOME and PATH environment variables."
            )
        return None


def get_python_version_str():
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    logger.debug("Found python version: %s", python_version)
    return python_version


def get_zos_version_str():
    """
    Get z/OS version by calling 'uname -Irsv' and parsing the output.

    Expected output format: "z/OS 05.00 02"
    Where the last number (02) is the version and the middle number (05) is the release,
    resulting in z/OS version 2.5.

    Returns:
        str: z/OS version (e.g., "2.5"), or None if unable to determine.
    """
    try:
        # Execute uname -Irsv command
        result = subprocess.run(
            ['uname', '-Irsv'],
            capture_output=True,
            text=True,
            check=True,
            timeout=5
        )
        output = result.stdout.strip()
        logger.debug("uname -Irsv output: %s", output)

        # Parse output format: "z/OS RR.MM VV"
        # Example: "z/OS 05.00 02" -> version 2.5
        # Where: VV (02) = version 2, RR (05) = release 5
        match = re.search(r'z/OS\s+(\d+)\.(\d+)\s+(\d+)', output)

        if match:
            rr = int(match.group(1))  # e.g., 05 (release)
            mm = int(match.group(2))  # e.g., 00 (modification level, not used)
            vv = int(match.group(3))  # e.g., 02 (version)

            # The version is VV (02 = version 2)
            # The release is RR (05 = release 5)
            version_major = vv
            version_minor = rr

            zos_version = f"{version_major}.{version_minor}"
            logger.debug("Parsed z/OS version: %s", zos_version)
            return zos_version
        else:
            logger.warning("Unable to parse z/OS version from uname output: %s", output)
            return None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command 'uname -Irsv' failed with return code {e.returncode}: {e.stderr}"
        logger.warning(error_msg)
        return None
    except Exception as e:
        error_msg = f"Failed to fetch z/OS version: {e}"
        logger.warning(error_msg)
        return None


# ------------------------------------------------------------------------------
# Dependency Validation
# ------------------------------------------------------------------------------
def validate_dependencies(module):
    logger.debug("Starting dependency validation process.")

    collection_version = version.__version__

    warnings = []

    # Find compatibility entry
    compat_dict = COMPATIBILITY_MATRIX.get(collection_version, {})

    if not compat_dict:
        module.fail_json(msg=f"No compatibility information for collection version: {collection_version}")

    # --- z/OS version check ---
    current_zos_ver = get_zos_version_str()
    min_zos_ver = compat_dict["min_zos_version"]
    if current_zos_ver is None:
        warnings.append("Unable to retrieve z/OS version.")
    elif get_version_tuple(current_zos_ver) < get_version_tuple(min_zos_ver):
            warnings.append(f"z/OS {current_zos_ver} is below the minimum tested version {min_zos_ver}.")

    # --- Python version checks ---
    current_python_ver = get_python_version_str()
    min_python_ver = compat_dict["min_python_version"]

    if get_version_tuple(current_python_ver) < get_version_tuple(min_python_ver):
        warnings.append(f"Python {current_python_ver} is below the minimum tested version {min_python_ver}.")

    # --- ZOAU version checks ---
    current_zoau_ver = get_zoau_version_str(module)
    min_zoau_ver = compat_dict["min_zoau_version"]
    if current_zoau_ver is None:
        warnings.append("Unable to retrieve ZOAU version.")
    elif get_version_tuple(current_zoau_ver) < get_version_tuple(min_zoau_ver):
        msg = (
            f"Incompatible ZOAU version: {current_zoau_ver}. "
            f"For collection version {collection_version}, "
            f"the minimum required ZOAU version is {min_zoau_ver}."
        )
        logger.error(msg)
        module.fail_json(msg=msg)


    logger.debug(
        "Detected versions - ZOAU: %s, Python: %s, z/OS: %s, Collection: %s",
        current_zoau_ver,
        current_python_ver,
        current_zos_ver,
        collection_version,
    )

    # --- Warn and continue ---
    for w in warnings:
        logger.warning(w)
        module.warn(w)

    logger.debug("Dependency validation process completed.")
    return  # do not exit, allow module to continue
