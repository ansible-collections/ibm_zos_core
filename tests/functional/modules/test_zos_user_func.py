# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2025,2026
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
            assert "TERMUACC" in result.get("cmd", "") and "NOTERMUACC" not in result.get("cmd", "")
        
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