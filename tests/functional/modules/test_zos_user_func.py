# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2026
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

import pytest
import random
import string
import re
from datetime import datetime, timedelta


# ============================================================================
# Helper Functions
# ============================================================================

def generate_random_name(prefix="TEST", length=8):
    """Generate a random name for RACF profiles (users/groups)."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length - len(prefix)))
    return prefix + suffix


def cleanup_user(hosts, username):
    """Clean up a test user from RACF."""
    try:
        hosts.all.shell(cmd=f"tsocmd 'DELUSER {username}'")
    except Exception:
        pass  # User may not exist


def cleanup_group(hosts, groupname):
    """Clean up a test group from RACF."""
    try:
        hosts.all.shell(cmd=f"tsocmd 'DELGROUP {groupname}'")
    except Exception:
        pass  # Group may not exist


def verify_user_exists(hosts, username):
    """Verify that a user exists in RACF."""
    result = hosts.all.shell(cmd=f"tsocmd 'LISTUSER {username}'")
    for res in result.contacted.values():
        return res.get("rc") == 0
    return False


def verify_group_exists(hosts, groupname):
    """Verify that a group exists in RACF."""
    result = hosts.all.shell(cmd=f"tsocmd 'LISTGRP {groupname}'")
    for res in result.contacted.values():
        return res.get("rc") == 0
    return False

# ============================================================================
# GROUP CREATE Tests
# ============================================================================

def test_group_create_basic(ansible_zos_module):
    """Test: Create new group profile with RACF defaults."""
    hosts = ansible_zos_module
    group_name = generate_random_name("TG")
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
    
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            assert result.get("cmd") == f"ADDGROUP ({group_name})"

        assert verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_create_with_model(ansible_zos_module):
    """Test: Create new group profile using another group as model"""
    hosts = ansible_zos_module
    group_name_model = generate_random_name("TG")
    group_name = generate_random_name("TG")
    
    try:
        results = hosts.all.zos_user(
            name=group_name_model,
            operation="create",
            scope="group",
            general={"model":"SYS1"}
        )
    
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert group_name_model in result.get("entities_modified", [])

        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"model": group_name_model}
        )
    
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            assert f"MODEL({group_name_model})" in result.get("cmd", "")

        assert verify_group_exists(hosts, group_name)
    finally:
        cleanup_group(hosts, group_name_model)
        cleanup_group(hosts, group_name)


def test_group_create_with_all_attributes_comprehensive(ansible_zos_module):
    """
    Test: Create group with maximum attributes configured.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGF")
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={
                "owner": "SYS1",
                "installation_data": "Full configuration test group"
            },
            group={
                "superior_group": "SYS1",
                "terminal_access": True,
                "universal_group": True
            },
            dfp={
                "data_app_id": "FULLAPP",
                "data_class": "DCFULL",
                "management_class": "MCFULL",
                "storage_class": "SCFULL"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            
            # Validate command contains all parameters
            cmd = result.get("cmd", "")
            assert "OWNER(SYS1)" in cmd
            assert "DATA('Full configuration test group')" in cmd
            assert "SUPGROUP(SYS1)" in cmd
            assert (("TERMUACC" in cmd) and ("NOTERMUACC" not in cmd))
            assert "UNIVERSAL" in cmd
            assert "DATAAPPL(FULLAPP)" in cmd
            assert "DATACLAS(DCFULL)" in cmd
            assert "MGMTCLAS(MCFULL)" in cmd
            assert "STORCLAS(SCFULL)" in cmd    
        
        assert verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)


def test_group_create_omvs_auto_gid_validation(ansible_zos_module):
    """
    Test: Create group with OMVS auto GID and validate GID assignment.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGO")
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            omvs={
                "uid": "auto"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "OMVS(AUTOGID)" in result.get("cmd", "")
            
            stdout = result.get("stdout", "")
            assert "was assigned an OMVS GID value" in stdout or result.get("rc") == 0
        
    finally:
        cleanup_group(hosts, group_name)


def test_group_create_omvs_custom_gid_specific(ansible_zos_module):
    """
    Test: Create group with specific custom GID value.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGC")
    custom_gid = 2500
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            omvs={
                "uid": "custom",
                "custom_uid": custom_gid
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert f"OMVS(GID({custom_gid}))" in result.get("cmd", "")
        
        
    finally:
        cleanup_group(hosts, group_name)


def test_group_create_omvs_shared_gid(ansible_zos_module):
    """
    Test: Create group with shared GID mode.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGS")
    shared_gid = 2600
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            omvs={
                "uid": "shared",
                "custom_uid": shared_gid
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert f"GID({shared_gid})SHARED" in cmd
        
    finally:
        cleanup_group(hosts, group_name)


def test_group_create_terminal_access_variations(ansible_zos_module):
    """
    Test: Validate both terminal access enabled and disabled scenarios.
    """
    hosts = ansible_zos_module
    group_enabled = generate_random_name("TGT")
    group_disabled = generate_random_name("TGT")
    
    try:
        # Test with terminal access enabled
        results_enabled = hosts.all.zos_user(
            name=group_enabled,
            operation="create",
            scope="group",
            group={"terminal_access": True}
        )
        
        for result in results_enabled.contacted.values():
            assert result.get("changed") is True
            assert "TERMUACC" in result.get("cmd", "")
    
        
        # Test with terminal access disabled
        results_disabled = hosts.all.zos_user(
            name=group_disabled,
            operation="create",
            scope="group",
            group={"terminal_access": False}
        )
        
        for result in results_disabled.contacted.values():
            assert result.get("changed") is True
            assert "NOTERMUACC" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_enabled)
        cleanup_group(hosts, group_disabled)


def test_group_create_universal_group_variations(ansible_zos_module):
    """
    Test: Validate universal and non-universal group creation.
    """
    hosts = ansible_zos_module
    group_universal = generate_random_name("TGU")
    group_non_universal = generate_random_name("TGU")
    
    try:
        # Test universal group
        results_universal = hosts.all.zos_user(
            name=group_universal,
            operation="create",
            scope="group",
            group={"universal_group": True}
        )
        
        for result in results_universal.contacted.values():
            assert result.get("changed") is True
            assert "UNIVERSAL" in result.get("cmd", "")
        
        
        # Test non-universal group (default behavior)
        results_non_universal = hosts.all.zos_user(
            name=group_non_universal,
            operation="create",
            scope="group",
            group={"universal_group": False}
        )
        
        for result in results_non_universal.contacted.values():
            assert result.get("changed") is True
            # Non-universal is default, so UNIVERSAL should not be in command
            assert "UNIVERSAL" not in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_universal)
        cleanup_group(hosts, group_non_universal)


def test_group_create_dfp_combinations(ansible_zos_module):
    """
    Test: Various combinations of DFP attributes.
    """
    hosts = ansible_zos_module
    group_name_1 = generate_random_name("TGD")
    group_name_2 = generate_random_name("TGD")
    
    try:
        # Test data class and management class only
        results1 = hosts.all.zos_user(
            name=group_name_1,
            operation="create",
            scope="group",
            dfp={
                "data_class": "DCPART",
                "management_class": "MCPART"
            }
        )
        
        for result in results1.contacted.values():
            assert result.get("changed") is True
            cmd = result.get("cmd", "")
            assert "DATACLAS(DCPART)" in cmd
            assert "MGMTCLAS(MCPART)" in cmd
        
        # Test storage class and data app ID only
        results2 = hosts.all.zos_user(
            name=group_name_2,
            operation="create",
            scope="group",
            dfp={
                "storage_class": "SCPART",
                "data_app_id": "PARTAPP"
            }
        )
        
        for result in results2.contacted.values():
            assert result.get("changed") is True
            cmd = result.get("cmd", "")
            assert "STORCLAS(SCPART)" in cmd
            assert "DATAAPPL(PARTAPP)" in cmd
        
    finally:
        cleanup_group(hosts, group_name_1)
        cleanup_group(hosts, group_name_2)


def test_group_create_error_already_exists(ansible_zos_module):
    """
    Test: Attempt to create a group that already exists.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGE")
    
    try:
        # Create the group first
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
        
        # Attempt to create again (should fail)
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
        
        for result in results.contacted.values():
            assert result.get("rc") != 0, "Expected failure when creating duplicate group"
            assert result.get("changed") is False
            stdout = result.get("stdout", "")
            assert "INVALID GROUP" in stdout or result.get("rc") == 8
        
    finally:
        cleanup_group(hosts, group_name)


def test_group_create_error_invalid_name(ansible_zos_module):
    """
    Test: Attempt to create group with invalid naming convention(> 8 characters).
    """
    hosts = ansible_zos_module
    invalid_group_name = "TESTGRP0123"  
    
    try:
        results = hosts.all.zos_user(
            name=invalid_group_name,
            operation="create",
            scope="group"
        )
        
        for result in results.contacted.values():
            assert result.get("rc") != 0, "Expected failure with invalid group name"
            assert result.get("changed") is False
            stdout = result.get("stdout", "")
            assert "INVALID GROUP" in stdout or result.get("rc") == 8
        
    finally:
        cleanup_group(hosts, invalid_group_name)


def test_group_create_error_custom_uid_missing(ansible_zos_module):
    """
    Test: Attempt to create group with custom UID but no custom_uid value.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGM")
    
    try:
        results = hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            omvs={
                "uid": "custom"
                # Missing custom_uid parameter
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is False
            msg = result.get("msg", "")
            assert "missing: custom_uid" in msg.lower() and result.get("rc") != 0
        
    finally:
        cleanup_group(hosts, group_name)


# ============================================================================
# END OF CREATE GROUP TESTS
# ============================================================================

# ============================================================================
# GROUP UPDATE Tests
# ============================================================================

def test_group_update_general_attributes(ansible_zos_module):
    """
    Test: Update group general attributes (owner, installation_data).
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"installation_data": "Initial data"}
        )
        
        # Update owner and installation data
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            general={
                "owner": "SYS1",
                "installation_data": "Updated installation data"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OWNER(SYS1)" in cmd
            assert "DATA('Updated installation data')" in cmd
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_clear_general_attributes(ansible_zos_module):
    """
    Test: Clear general group attributes using empty strings.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group with data
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"installation_data": "Data to clear"}
        )
        
        # Clear installation data
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            general={"installation_data": ""}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NODATA" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_terminal_access(ansible_zos_module):
    """
    Test: Update group terminal access (enable/disable).
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group with terminal access disabled
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            group={"terminal_access": False}
        )
        
        # Enable terminal access
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            group={"terminal_access": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TERMUACC" in cmd and "NOTERMUACC" not in cmd
        
        # Disable terminal access
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            group={"terminal_access": False}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NOTERMUACC" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_dfp_individual_attributes(ansible_zos_module):
    """
    Test: Update individual DFP attributes.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group with initial DFP
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            dfp={
                "data_app_id": "OLDAPP",
                "data_class": "DCOLD"
            }
        )
        
        # Update data app ID
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            dfp={"data_app_id": "NEWAPP"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "DATAAPPL(NEWAPP)" in result.get("cmd", "")
        
        # Update data class
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            dfp={"data_class": "DCNEW"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "DATACLAS(DCNEW)" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_all_dfp_attributes(ansible_zos_module):
    """
    Test: Update all DFP attributes together.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group with initial DFP
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            dfp={
                "data_app_id": "OLDAPP",
                "data_class": "DCOLD",
                "management_class": "MCOLD",
                "storage_class": "SCOLD"
            }
        )
        
        # Update all DFP attributes
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            dfp={
                "data_app_id": "NEWAPP",
                "data_class": "DCNEW",
                "management_class": "MCNEW",
                "storage_class": "SCNEW"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DATAAPPL(NEWAPP)" in cmd
            assert "DATACLAS(DCNEW)" in cmd
            assert "MGMTCLAS(MCNEW)" in cmd
            assert "STORCLAS(SCNEW)" in cmd
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_delete_dfp_block(ansible_zos_module):
    """
    Test: Delete entire DFP block from group.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group with DFP
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            dfp={
                "data_class": "DCTEST",
                "storage_class": "SCTEST"
            }
        )
        
        # Delete DFP block
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            dfp={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NODFP" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_combined_attributes(ansible_zos_module):
    """
    Test: Update multiple attribute types together (general + group + DFP).
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
        
        # Update multiple attribute types
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            general={
                "owner": "SYS1",
                "installation_data": "Combined update test"
            },
            group={
                "terminal_access": True
            },
            dfp={
                "data_class": "DCTEST",
                "storage_class": "SCTEST"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OWNER(SYS1)" in cmd
            assert "DATA('Combined update test')" in cmd
            assert "TERMUACC" in cmd
            assert "DATACLAS(DCTEST)" in cmd
            assert "STORCLAS(SCTEST)" in cmd
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_update_omvs_and_delete(ansible_zos_module):
    """
    Test: OMVS segment deletion and error scenarios.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGU")
    nonexistent_group = "NONEXIST99"
    
    try:
        # Update non-existent group
        results = hosts.all.zos_user(
            name=nonexistent_group,
            operation="update",
            scope="group",
            general={"owner": "SYS1"}
        )
        
        for result in results.contacted.values():
            assert result.get("rc") != 0, "Expected failure for non-existent group"
            assert result.get("changed") is False
        
        # Create group with auto gid
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            omvs={"uid": "auto"}
        )
        
        # Delete OMVS segment
        results = hosts.all.zos_user(
            name=group_name,
            operation="update",
            scope="group",
            omvs={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NOOMVS" in result.get("cmd", "")
        
    finally:
        cleanup_group(hosts, group_name)

# ============================================================================
# END OF GROUP UPDATE TESTS
# ============================================================================

# ============================================================================
# GROUP DELETE AND PURGE TESTS
# ============================================================================
def test_group_delete_standard(ansible_zos_module):
    """
    Test: Delete a standard group profile with no subgroups.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGD")
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
        
        # Verify group exists
        assert verify_group_exists(hosts, group_name)
        
        # Delete group
        results = hosts.all.zos_user(
            name=group_name,
            operation="delete",
            scope="group"
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            assert f"DELGROUP ({group_name})" in result.get("cmd", "")
        
        # Verify group no longer exists
        assert not verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_delete_with_subgroups_error(ansible_zos_module):
    """
    Test: Delete superior group that has subgroups (should fail).
    """
    hosts = ansible_zos_module
    superior_group = generate_random_name("TGS")
    sub_group = generate_random_name("TGS")
    
    try:
        # Create superior group
        hosts.all.zos_user(
            name=superior_group,
            operation="create",
            scope="group"
        )
        
        # Create subgroup
        hosts.all.zos_user(
            name=sub_group,
            operation="create",
            scope="group",
            group={"superior_group": superior_group}
        )
        
        # Attempt to delete superior group (should fail)
        results = hosts.all.zos_user(
            name=superior_group,
            operation="delete",
            scope="group"
        )
        
        for result in results.contacted.values():
            assert result.get("rc") == 8
            assert result.get("changed") is False
            stdout = result.get("stdout", "")
            assert "INVALID GROUP" in stdout
        
        # Verify superior group still exists
        assert verify_group_exists(hosts, superior_group)
        
    finally:
        cleanup_group(hosts, sub_group)
        cleanup_group(hosts, superior_group)

def test_group_delete_nonexistent_error(ansible_zos_module):
    """
    Test: Attempt to delete a group that doesn't exist.
    """
    hosts = ansible_zos_module
    nonexistent_group = "NOEXST99"
    
    # Attempt to delete non-existent group
    results = hosts.all.zos_user(
        name=nonexistent_group,
        operation="delete",
        scope="group"
    )
    
    for result in results.contacted.values():
        assert result.get("rc") == 8
        assert result.get("changed") is False
        assert result.get("num_entities_modified") == 0
        stdout = result.get("stdout", "")
        assert "INVALID GROUP" in stdout

def test_group_purge_default_options(ansible_zos_module):
    """
    Test: Purge group with default options (keep_dump=false, optimize_dump=true).
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGP")
    racf_database = "SYS1.RACF"
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"owner": "SYS1"}
        )
        
        # Verify group exists
        assert verify_group_exists(hosts, group_name)
        
        # Purge group with default options
        results = hosts.all.zos_user(
            name=group_name,
            operation="purge",
            scope="group",
            database=racf_database,
            keep_dump=False,
            optimize_dump=True
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("database_dumped") is True
            assert result.get("dump_kept") is False
            assert result.get("dump_name") is None
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            assert result.get("invocation").get("module_args").get("optimize_dump") is True
        
        # Verify group no longer exists
        assert not verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_purge_keep_dump(ansible_zos_module):
    """
    Test: Purge group with keep_dump=true.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGP")
    racf_database = "SYS1.RACF"
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"owner": "SYS1"}
        )
        
        # Purge group with keep_dump=true
        results = hosts.all.zos_user(
            name=group_name,
            operation="purge",
            scope="group",
            database=racf_database,
            keep_dump=True,
            optimize_dump=True
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("database_dumped") is True
            assert result.get("dump_kept") is True
            # dump_name should be not none
            assert result.get("dump_name") is not None
            assert result.get("num_entities_modified") == 1
            assert result.get("invocation").get("module_args").get("optimize_dump") is True
            
            # Verify dump dataset name is returned
            dump_name = result.get("dump_name")
            assert dump_name, "Dump dataset name should not be empty"
        
        # Verify group no longer exists
        assert not verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)

def test_group_purge_lockinput_mode(ansible_zos_module):
    """
    Test: Purge group with optimize_dump=false (LOCKINPUT mode).
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGP")
    racf_database = "SYS1.RACF"
    
    try:
        # Create group
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={"owner": "SYS1"}
        )
        
        # Purge group with optimize_dump=false (LOCKINPUT)
        results = hosts.all.zos_user(
            name=group_name,
            operation="purge",
            scope="group",
            database=racf_database,
            keep_dump=False,
            optimize_dump=False
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("database_dumped") is True
            assert result.get("dump_kept") is False
            assert result.get("dump_name") is None
            assert result.get("num_entities_modified") == 1
            assert result.get("invocation").get("module_args").get("optimize_dump") is False
        
        # Verify group no longer exists
        assert not verify_group_exists(hosts, group_name)
        
    finally:
        # Cleanup if purge failed
        cleanup_group(hosts, group_name)

def test_group_purge_comprehensive_with_attributes(ansible_zos_module):
    """
    Test: Purge group with various attributes.
    """
    hosts = ansible_zos_module
    group_name = generate_random_name("TGP")
    racf_database = "SYS1.RACF"
    
    try:
        # Create group with multiple attributes
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group",
            general={
                "owner": "SYS1",
                "installation_data": "Group to be purged"
            },
            group={
                "terminal_access": True
            },
            dfp={
                "data_class": "DCTEST",
                "storage_class": "SCTEST"
            },
            omvs={
                "uid": "auto"
            }
        )
        
        # verify group exists
        assert verify_group_exists(hosts, group_name)
        
        # Purge group completely
        results = hosts.all.zos_user(
            name=group_name,
            operation="purge",
            scope="group",
            database=racf_database,
            keep_dump=False,
            optimize_dump=True
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("database_dumped") is True
            assert result.get("num_entities_modified") == 1
            assert group_name in result.get("entities_modified", [])
            assert result.get("dump_kept") is False
            assert result.get("dump_name") is None
        
        assert not verify_group_exists(hosts, group_name)
        
    finally:
        cleanup_group(hosts, group_name)

# ============================================================================
# END OF GROUP DELETE AND PURGE TESTS
# ============================================================================

# ============================================================================
# USER CREATE TESTS
# ============================================================================

def test_user_create_basic_racf_defaults(ansible_zos_module):
    """
    Test: Create new user profile with RACF defaults.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user"
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
            assert result.get("cmd") == f"ADDUSER ({user_name})"
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_owner(ansible_zos_module):
    """
    Test: Create new user profile with specific owner.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    owner = "SYS1"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            general={"owner": owner}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert f"OWNER({owner})" in result.get("cmd", "")
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_model(ansible_zos_module):
    """
    Test: Create new user profile using another user as model.
    """
    hosts = ansible_zos_module
    model_user = generate_random_name("TSTU")
    user_name = generate_random_name("TSTU")
    
    try:
        # Create model user first
        hosts.all.zos_user(
            name=model_user,
            operation="create",
            scope="user"
        )
        
        # Create user with model
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            general={"model": model_user}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert f"MODEL({model_user})" in result.get("cmd", "")
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)
        cleanup_user(hosts, model_user)


def test_user_create_with_installation_data(ansible_zos_module):
    """
    Test: Create new user profile with installation data.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    install_data = "Test User - Installation Data"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            general={"installation_data": install_data}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DATA(" in cmd
            assert "Test User - Installation Data" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_dfp_attributes(ansible_zos_module):
    """
    Test: Create user with DFP attributes -data_app_id, data_class, management_class, storage_class.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            dfp={
                "data_app_id": "APPID001",
                "data_class": "DCLAS001",
                "management_class": "MCLAS001",
                "storage_class": "SCLAS001"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DATAAPPL(APPID001)" in cmd
            assert "DATACLAS(DCLAS001)" in cmd
            assert "MGMTCLAS(MCLAS001)" in cmd
            assert "STORCLAS(SCLAS001)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_language_settings(ansible_zos_module):
    """
    Test: Create user with language settings -primary and secondary.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            language={
                "primary": "ENU",
                "secondary": "JPN"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            pattern = r"LANGUAGE\s*\((?=.*PRIMARY\(ENU\))(?=.*SECONDARY\(JPN\)).*\)"
            assert re.search(pattern, cmd)
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_tso_basic_settings(ansible_zos_module):
    """
    Test: Create user with TSO class settings -account_num, job_class, hold_class, msg_class, sysout_class.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            tso={
                "account_num": 30000,
                "job_class": "A",
                "hold_class": "H",
                "msg_class": "X",
                "sysout_class": "A"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TSO(" in cmd
            assert "ACCTNUM(30000)" in cmd
            assert "JOBCLASS(A)" in cmd
            assert "HOLDCLASS(H)" in cmd
            assert "MSGCLASS(X)" in cmd
            assert "SYS(A)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_tso_region_sizes(ansible_zos_module):
    """
    Test: Create user with TSO region sizes -region_size, max_region_size.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            tso={
                "account_num": 32000,
                "region_size": 8192,
                "max_region_size": 16384
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TSO(" in cmd
            assert "SIZE(8192)" in cmd
            assert "MAXSIZE(16384)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_tso_multiple_parameters(ansible_zos_module):
    """
    Test: Create user with multiple TSO parameters combined.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            tso={
                "account_num": 33000,
                "logon_proc": "IKJACCNT",
                "region_size": 16384,
                "max_region_size": 32768,
                "job_class": "A",
                "msg_class": "X",
                "sysout_class": "A",
                "hold_class": "H"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TSO(" in cmd
            assert "ACCTNUM(33000)" in cmd
            assert "PROC(IKJACCNT)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_omvs_auto_uid(ansible_zos_module):
    """
    Test: Create user with auto-assigned UID.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={
                "uid": "auto",
                "home": home_dir,
                "program": "/bin/sh"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert "AUTOUID" in cmd
            assert f"HOME({home_dir})" in cmd
            assert "PROGRAM(/bin/sh)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_omvs_custom_uid(ansible_zos_module):
    """
    Test: Create user with custom UID.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    custom_uid = 5041
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={
                "uid": "custom",
                "custom_uid": custom_uid,
                "home": home_dir,
                "program": "/bin/bash"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert f"UID({custom_uid})" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_omvs_memory_limits(ansible_zos_module):
    """
    Test: Create user with memory limits configured- addr_space_size, map_size, nonshared_size, shared_size.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={
                "uid": "auto",
                "home": home_dir,
                "program": "/bin/sh",
                "addr_space_size": 10485760,
                "map_size": 2048,
                "nonshared_size": "7g",
                "shared_size": "5g"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert "ASSIZEMAX(10485760)" in cmd
            assert "MMAPAREAMAX(2048)" in cmd
            assert "SHMEMMAX(5g)" in cmd
            assert "MEMLIMIT(7g)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_omvs_process_limits(ansible_zos_module):
    """
    Test: Create user with process limits - max_cpu_time, max_files, max_threads, max_procs.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={
                "uid": "auto",
                "home": home_dir,
                "program": "/bin/bash",
                "max_cpu_time": 3600,
                "max_files": 2000,
                "max_threads": 200,
                "max_procs": 100
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert "CPUTIMEMAX(3600)" in cmd
            assert "FILEPROCMAX(2000)" in cmd
            assert "THREADSMAX(200)" in cmd
            assert "PROCUSERMAX(100)" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_default_group_and_clauth(ansible_zos_module):
    """
    Test: Create new user profile with default group assignment and clauth.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    group_name = generate_random_name("TG")
    
    try:
        # Create group first
        hosts.all.zos_user(
            name=group_name,
            operation="create",
            scope="group"
        )
        
        # Create user with default group
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            access={
                "default_group": group_name,
                "clauth": {"add": ["TERMINAL"]}
                }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert f"DFLTGRP({group_name})" in cmd
            assert result.get("num_entities_modified") == 1
            assert user_name in result.get("entities_modified", [])
            assert "CLAUTH( TERMINAL )" in cmd
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)
        cleanup_group(hosts, group_name)


def test_user_create_with_access_attributes(ansible_zos_module):
    """
    Test: Create user with various access attributes- roaudit, operator_card, maintenance_access, restricted.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            access={
                "roaudit": False,
                "operator_card": False,
                "maintenance_access": False,
                "restricted": False
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOROAUDIT" in cmd
            assert "NOOIDCARD" in cmd
            assert "NORESTRICTED" in cmd
            assert "NOOPERATIONS" in cmd
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_login_restrictions(ansible_zos_module):
    """
    Test: Create user with login restrictions - days, time.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            restrictions={
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "time": "0900:1700"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "WHEN(" in cmd
            assert "DAYS( monday tuesday wednesday thursday friday )" in cmd
            assert "TIME(0900:1700)" in cmd
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_operator_authority(ansible_zos_module):
    """
    Test: Create user with operator authority parameter like all, info, master, sys.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM" in cmd
            assert "AUTH(info)" in cmd
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_error_already_exists(ansible_zos_module):
    """
    Test: Attempt to create user that already exists.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user first time
        results1 = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user"
        )
        
        for result in results1.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
        
        # Attempt to create same user again (should fail)
        results2 = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user"
        )
        
        for result in results2.contacted.values():
            assert result.get("rc") != 0
            assert result.get("changed") is False
            assert "INVALID USER" in result.get("stdout")
        
    finally:
        cleanup_user(hosts, user_name)

def test_user_create_with_operator_cmd_and_search_settings(ansible_zos_module):
    """
    Test: Create user with operator command system and search key.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        results = hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "cmd_system": "MVS",
                "search_key": "TST0705"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "AUTH(info)" in cmd
            assert "CMDSYS(MVS)" in cmd
            assert "KEY(TST0705)" in cmd
        
        assert verify_user_exists(hosts, user_name)
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_create_with_operator_migration_and_display(ansible_zos_module):
    """
    Test: Create user with operator migration ID(enabled/disabled) and display settings.
    """
    hosts = ansible_zos_module
    user_enabled = generate_random_name("TSTU")
    user_disabled = generate_random_name("TSTU")
    
    try:
        # Test with migration ID enabled and display settings
        results_enabled = hosts.all.zos_user(
            name=user_enabled,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "migration_id": True,
                "display": ["jobnames", "sess"]
            }
        )
        
        for result in results_enabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "MIGID(YES)" in cmd
            assert "MONITOR( jobnames sess ) " in cmd
        
        # Test with migration ID disabled
        results_disabled = hosts.all.zos_user(
            name=user_disabled,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "migration_id": False
            }
        )
        
        for result in results_disabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "MIGID(NO)" in cmd
        
        assert verify_user_exists(hosts, user_enabled)
        assert verify_user_exists(hosts, user_disabled)
        
    finally:
        cleanup_user(hosts, user_enabled)
        cleanup_user(hosts, user_disabled)


def test_user_create_with_operator_message_settings(ansible_zos_module):
    """
    Test: Create user with operator message settings - msg_level, msg_format, msg_storage.
    """
    hosts = ansible_zos_module
    user_all = generate_random_name("TSTU")
    user_info = generate_random_name("TSTU")
    
    try:
        # Test with msg_level=all
        results_all = hosts.all.zos_user(
            name=user_all,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "msg_level": "all",
                "msg_format": "m",
                "msg_storage": 1000
            }
        )
        
        for result in results_all.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "LEVEL(all)" in cmd
            assert "MFORM(m)" in cmd
            assert "STORAGE(1000)" in cmd
        
        # Test with msg_level=i (info)
        results_info = hosts.all.zos_user(
            name=user_info,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "msg_level": "i",
                "msg_format": "m",
                "msg_storage": 2000
            }
        )
        
        for result in results_info.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "LEVEL(i)" in cmd
            assert "MFORM(m)" in cmd
            assert "STORAGE(2000)" in cmd
        
        assert verify_user_exists(hosts, user_all)
        assert verify_user_exists(hosts, user_info)
        
    finally:
        cleanup_user(hosts, user_all)
        cleanup_user(hosts, user_info)


def test_user_create_with_operator_automated_and_hardcopy_msgs(ansible_zos_module):
    """
    Test: Create user with automated and hardcopy message settings.
    """
    hosts = ansible_zos_module
    user_auto_hc = generate_random_name("TSTU")
    user_no_auto_no_hc = generate_random_name("TSTU")
    
    try:
        # Test with automated and hardcopy enabled
        results_enabled = hosts.all.zos_user(
            name=user_auto_hc,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "automated_msgs": True,
                "hardcopy_msgs": True
            }
        )
        
        for result in results_enabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "AUTO(YES)" in cmd
            assert "HC(YES)" in cmd
        
        # Test with automated and hardcopy disabled
        results_disabled = hosts.all.zos_user(
            name=user_no_auto_no_hc,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "automated_msgs": False,
                "hardcopy_msgs": False
            }
        )
        
        for result in results_disabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "AUTO(NO)" in cmd
            assert "HC(NO)" in cmd
        
        assert verify_user_exists(hosts, user_auto_hc)
        assert verify_user_exists(hosts, user_no_auto_no_hc)
        
    finally:
        cleanup_user(hosts, user_auto_hc)
        cleanup_user(hosts, user_no_auto_no_hc)


def test_user_create_with_operator_unknown_and_undelivered_msgs(ansible_zos_module):
    """
    Test: Create user with unknown and undelivered message settings.
    """
    hosts = ansible_zos_module
    user_enabled = generate_random_name("TSTU")
    user_disabled = generate_random_name("TSTU")
    
    try:
        # Test with unknown and undelivered messages enabled
        results_enabled = hosts.all.zos_user(
            name=user_enabled,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "unknown_msgs": True,
                "undelivered_msgs": True
            }
        )
        
        for result in results_enabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "UNKNIDS(YES)" in cmd
            assert "UD(YES)" in cmd
        
        # Test with unknown and undelivered messages disabled
        results_disabled = hosts.all.zos_user(
            name=user_disabled,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "unknown_msgs": False,
                "undelivered_msgs": False
            }
        )
        
        for result in results_disabled.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "UNKNIDS(NO)" in cmd
            assert "UD(NO)" in cmd
        
        assert verify_user_exists(hosts, user_enabled)
        assert verify_user_exists(hosts, user_disabled)
        
    finally:
        cleanup_user(hosts, user_enabled)
        cleanup_user(hosts, user_disabled)


def test_user_create_with_operator_internal_msgs_and_routing_msg(ansible_zos_module):
    """
    Test: Create user with internal messages and routing settings -internal_msgs (enabled/disabled), 
    routing_msgs (single/multiple codes).
    """
    hosts = ansible_zos_module
    user_internal_single = generate_random_name("TSTU")
    user_no_internal_multi = generate_random_name("TSTU")
    
    try:
        # Test with internal messages enabled and single routing code
        results_single = hosts.all.zos_user(
            name=user_internal_single,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "internal_msgs": True,
                "routing_msgs": ["1"]
            }
        )
        
        for result in results_single.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "INTIDS(YES)" in cmd
            assert "ROUTCODE( 1 )" in cmd

        # Test with internal messages disabled and multiple routing codes
        results_multi = hosts.all.zos_user(
            name=user_no_internal_multi,
            operation="create",
            scope="user",
            operator={
                "authority": "info",
                "internal_msgs": False,
                "routing_msgs": ["1", "2", "11"]
            }
        )
        
        for result in results_multi.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "INTIDS(NO)" in cmd
            assert "ROUTCODE( 1 2 11 )" in cmd
        
        assert verify_user_exists(hosts, user_internal_single)
        assert verify_user_exists(hosts, user_no_internal_multi)
        
    finally:
        cleanup_user(hosts, user_internal_single)
        cleanup_user(hosts, user_no_internal_multi)        
        
# ============================================================================
# END OF USER CREATE TESTS
# ============================================================================        

# ============================================================================
# USER UPDATE TESTS
# ============================================================================

def test_user_update_basic_attributes(ansible_zos_module):
    """
    Test: Update basic user attributes - owner, installation_data.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    group_name = generate_random_name("TG")
    
    try:
        # Create group for owner
        hosts.all.zos_user(name=group_name, operation="create", scope="group")
        
        # Create user
        hosts.all.zos_user(name=user_name, operation="create", scope="user")
        
        # Update owner
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            general={"owner": group_name}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert f"OWNER({group_name})" in cmd
        
        # Update installation data
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            general={"installation_data": "Updated Installation Data"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DATA(" in cmd
            assert "Updated Installation Data" in cmd
        
    finally:
        cleanup_user(hosts, user_name)
        cleanup_group(hosts, group_name)


def test_user_update_model_dataset(ansible_zos_module):
    """
    Test: Update user with MODEL parameter (dataset name).
    For user update, MODEL expects a dataset name.
    RACF will issue RC=4 warning if the dataset profile doesn't exist.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    model_dsname = generate_random_name("MDLS")  # Dataset name for MODEL
    
    try:
        # Create user
        hosts.all.zos_user(name=user_name, operation="create", scope="user")
        
        # Update with model (dataset name does not exists)
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            general={"model": model_dsname}
        )
        
        for result in results.contacted.values():
            # Expect RC=4 with warning about unable to locate model profile
            assert result.get("failed") is True
            assert result.get("rc") == 4
            cmd = result.get("cmd", "")
            assert f"MODEL({model_dsname})" in cmd
            stdout = result.get("stdout", "")
            assert f"WARNING, UNABLE TO LOCATE THE MODEL PROFILE FOR {user_name}.{model_dsname}" in stdout
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_dfp_attributes(ansible_zos_module):
    """
    Test: Update DFP attributes - data_app_id, data_class, management_class, storage_class, delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with DFP attributes
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            dfp={
                "data_app_id": "APPID001",
                "data_class": "DCLAS001"
            }
        )
        
        # Update individual DFP attributes
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            dfp={
                "data_app_id": "APPID999",
                "data_class": "DCLAS999",
                "management_class": "MCLAS999",
                "storage_class": "SCLAS999"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DATAAPPL(APPID999)" in cmd
            assert "DATACLAS(DCLAS999)" in cmd
            assert "MGMTCLAS(MCLAS999)" in cmd
            assert "STORCLAS(SCLAS999)" in cmd
        
        # Delete DFP block
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            dfp={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NODFP" in result.get("cmd","")
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_language_settings(ansible_zos_module):
    """
    Test: Update language settings - primary, secondary, delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with language
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            language={"primary": "ENU"}
        )
        
        # Update primary language
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            language={"primary": "JPN"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "PRIMARY(JPN)" in cmd
        
        # Add secondary language
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            language={"secondary": "DEU"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "LANGUAGE(" in cmd
            assert "SECONDARY(DEU)" in cmd
        
        # Update both languages
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            language={"primary": "FRA", "secondary": "ENU"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "LANGUAGE(" in cmd
            assert "PRIMARY(FRA)" in cmd
            assert "SECONDARY(ENU)" in cmd
        
        # Delete language block
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            language={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOLANGUAGE" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_tso_basic_settings(ansible_zos_module):
    """
    Test: Update TSO basic settings - account_num, job_class, hold_class, msg_class, sysout_class, logon_proc.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with TSO
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            tso={"account_num": 30000, "job_class": "A"}
        )
        
        # Update account number
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={"account_num": 30999}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "ACCTNUM(30999)" in result.get("cmd", "")
        
        # Update class settings
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={
                "job_class": "B",
                "hold_class": "X",
                "msg_class": "Y",
                "sysout_class": "B"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "JOBCLASS(B)" in cmd
            assert "HOLDCLASS(X)" in cmd
            assert "MSGCLASS(Y)" in cmd
            assert "SYS(B)" in cmd
        
        # Update logon procedure
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={"logon_proc": "ISPFPROC"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "PROC(ISPFPROC)" in result.get("cmd", "")
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_tso_advanced_settings(ansible_zos_module):
    """
    Test: Update TSO advanced settings and delete -region_size, max_region_size, logon_cmd, dest_id, 
    security_label, unit_name, delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with TSO
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            tso={"account_num": 32000, "region_size": 8192}
        )
        
        # Update region sizes
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={"region_size": 16384, "max_region_size": 32768}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "SIZE(16384)" in cmd
            assert "MAXSIZE(32768)" in cmd
        
        # Update multiple TSO attributes
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={
                "dest_id": "DEST999",
                "security_label": "SECRET",
                "unit_name": "SYSALLDA"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "DEST(DEST999)" in cmd
            assert "SECLABEL(SECRET)" in cmd
            assert "UNIT(SYSALLDA)" in cmd
        
        # Delete TSO segment
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            tso={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOTSO" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_omvs_basic_settings(ansible_zos_module):
    """
    Test: Update OMVS basic settings - home, program, uid (custom/shared).
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        # Create user with OMVS
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={"uid": "auto", "home": home_dir, "program": "/bin/sh"}
        )
        
        # Update home directory
        new_home = f"/home/{user_name.lower()}"
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={"home": new_home}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "OMVS(" in result.get("cmd","")
            assert f"HOME({new_home})" in result.get("cmd", "")
        
        # Update program
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={"program": "/bin/bash"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "OMVS(" in result.get("cmd","")
            assert "PROGRAM(/bin/bash)" in result.get("cmd", "")
        
        # Update UID to custom
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={"uid": "custom", "custom_uid": 5999}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "OMVS(" in result.get("cmd","")
            assert "UID(5999)" in result.get("cmd", "")
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_omvs_limits_and_delete(ansible_zos_module):
    """
    Test: Update OMVS limits and delete segment - memory limits, omvs process limits, delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    home_dir = f"/u/{user_name.lower()}"
    
    try:
        # Create user with OMVS
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            omvs={"uid": "auto", "home": home_dir, "program": "/bin/sh"}
        )
        
        # Update memory limits
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={
                "addr_space_size": 10485760,
                "map_size": 2048,
                "nonshared_size": "7g",
                "shared_size": "5g"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert "SHMEMMAX(5g)" in cmd
            assert "MEMLIMIT(7g)" in cmd
            assert "ASSIZEMAX(10485760)" in cmd
            assert "MMAPAREAMAX(2048)" in cmd
        
        # Update process limits
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={
                "max_cpu_time": 3600,
                "max_files": 2000,
                "max_threads": 200,
                "max_procs": 100
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OMVS(" in cmd
            assert "PROCUSERMAX(100)" in cmd
            assert "THREADSMAX(200)" in cmd
            assert "CPUTIMEMAX(3600)" in cmd
            assert "FILEPROCMAX(2000)" in cmd
        
        # Delete OMVS segment
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            omvs={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOOMVS" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_access_clauth(ansible_zos_module):
    """
    Test: Update CLAUTH - access.clauth.add, access.clauth.delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
        )
        
        # Add CLAUTH
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            access={"clauth": {"add": ["TERMINAL", "CONSOLE"]}}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "CLAUTH( TERMINAL CONSOLE )" in cmd
        
        # Remove CLAUTH
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            access={"clauth": {"delete": ["TERMINAL"]}}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOCLAUTH( TERMINAL )" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_access_security_attributes(ansible_zos_module):
    """
    Test: Update access security attributes - roaudit, category, operator_card, maintenance_access, restricted, security_level.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user
        hosts.all.zos_user(name=user_name, operation="create", scope="user")
        
        # Enable ROAUDIT
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            access={"roaudit": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "ROAUDIT" in result.get("cmd", "")
        
        # Disable ROAUDIT
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            access={"roaudit": False}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NOROAUDIT" in result.get("cmd", "")
        
        # Update operator card, maintenance access, restricted
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            access={
                "operator_card": False,
                "maintenance_access": False,
                "restricted": False
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "NOOIDCARD" in cmd
            assert "NORESTRICTED" in cmd
            assert "OPERATIONS" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_login_restrictions(ansible_zos_module):
    """
    Test: Update login restrictions - days, time, revoke, resume.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    # Generate future dates dynamically (MM/DD/YY format)
    revoke_date = datetime.now() + timedelta(days=10)
    resume_date = datetime.now() + timedelta(days=15)
    revoke_date_str = revoke_date.strftime("%m/%d/%y")
    resume_date_str = resume_date.strftime("%m/%d/%y")
    
    try:
        # Create user
        hosts.all.zos_user(name=user_name, operation="create", scope="user")
        
        # Update login days to weekdays
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            restrictions={"days": ["weekdays"]}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "WHEN( DAYS( weekdays )" in cmd
        
        # Update login time
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            restrictions={"time": "0900:1700"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TIME(0900:1700)" in cmd
        
        # Update both days and time
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            restrictions={
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                "time": "0800:1800"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "TIME(0800:1800)" in cmd
            assert "DAYS( monday tuesday wednesday thursday friday )" in cmd
        
        # Revoke restrictions
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            restrictions={"revoke": revoke_date_str}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert f"REVOKE({revoke_date_str})" in cmd
        
        # Resume restrictions
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            restrictions={"resume": resume_date_str}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert f"RESUME({resume_date_str})" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_operator_authority_and_settings(ansible_zos_module):
    """
    Test: Update operator authority and basic settings -authority, cmd_system, search_key, migration_id, display.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with operator
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        # Update authority to MASTER
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"authority": "master"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "AUTH(master)" in cmd

        # Update authority to SYS
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"authority": "sys"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "AUTH(sys)" in cmd
        
        # Update command system and search key
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={
                "cmd_system": "JES2",
                "search_key": "NEWSRCH"
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "CMDSYS(JES2)" in cmd
            assert "KEY(NEWSRCH)" in cmd
        
        # Update migration ID and display
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={
                "migration_id": True,
                "display": ["status", "jobnames"]
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "MONITOR( status jobnames )" in cmd
            assert "MIGID(YES)" in cmd

    finally:
        cleanup_user(hosts, user_name)


def test_user_update_operator_message_settings(ansible_zos_module):
    """
    Test: Update operator message settings - msg_level, msg_format, msg_storage
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with operator
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        # Update message level
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"msg_level": "all"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "LEVEL(all)" in cmd
        
        # Update message format
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"msg_format": "m"}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "MFORM(m)" in cmd
        
        # Update message storage
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"msg_storage": 2000}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "STORAGE(2000)" in cmd
        
    finally:
        cleanup_user(hosts, user_name)

def test_user_update_operator_message_scope(ansible_zos_module):
    """
    Test: Update operator message scope (add and delete).
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with operator
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        # Update operator message scope - add ALL
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"msg_scope": {"add": ["ALL"]}}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "ADDMSCOPE( ALL )" in cmd
        
        # Update operator message scope - delete ALL
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"msg_scope": {"delete": ["ALL"]}}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "OPERPARM(" in cmd
            assert "DELMSCOPE( ALL )" in cmd
        
    finally:
        cleanup_user(hosts, user_name)



def test_user_update_operator_message_flags(ansible_zos_module):
    """
    Test: Update operator message flags -automated_msgs, hardcopy_msgs, unknown_msgs, 
    undelivered_msgs, internal_msgs (all enabled/disabled).
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with operator
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        # Enable all message types
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={
                "automated_msgs": True,
                "hardcopy_msgs": True,
                "unknown_msgs": True,
                "undelivered_msgs": True,
                "internal_msgs": True
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "AUTO(YES)" in cmd
            assert "HC(YES)" in cmd
            assert "UNKNIDS(YES)" in cmd
            assert "UD(YES)" in cmd
            assert "INTIDS(YES)" in cmd
        
        # Disable all message types
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={
                "automated_msgs": False,
                "hardcopy_msgs": False,
                "unknown_msgs": False,
                "undelivered_msgs": False,
                "internal_msgs": False
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "AUTO(NO)" in cmd
            assert "HC(NO)" in cmd
            assert "UNKNIDS(NO)" in cmd
            assert "UD(NO)" in cmd
            assert "INTIDS(NO)" in cmd
        
    finally:
        cleanup_user(hosts, user_name)


def test_user_update_operator_routing_and_delete(ansible_zos_module):
    """
    Test: Update operator routing messages and delete segment - routing_msgs (single/multiple), delete.
    """
    hosts = ansible_zos_module
    user_name = generate_random_name("TSTU")
    
    try:
        # Create user with operator
        hosts.all.zos_user(
            name=user_name,
            operation="create",
            scope="user",
            operator={"authority": "info"}
        )
        
        # Update routing messages - single code
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"routing_msgs": ["1"]}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "ROUTCODE( 1" in result.get("cmd", "")
        
        # Update routing messages - multiple codes
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"routing_msgs": ["1", "2", "11"]}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "ROUTCODE( 1 2 11 )" in result.get("cmd", "")
        
        # Update with multiple operator attributes
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={
                "authority": "all",
                "automated_msgs": True,
                "routing_msgs": ["1", "2", "3"]
            }
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            cmd = result.get("cmd", "")
            assert "ROUTCODE( 1 2 3" in cmd
            assert "AUTH(all)" in cmd
            assert "AUTO(YES)" in cmd
        
        # Delete operator segment
        results = hosts.all.zos_user(
            name=user_name,
            operation="update",
            scope="user",
            operator={"delete": True}
        )
        
        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("rc") == 0
            assert "NOOPERPARM"  in result.get("cmd", "")
        
    finally:
        cleanup_user(hosts, user_name)

# ============================================================================
# END OF USER UPDATE TESTS
# ============================================================================
