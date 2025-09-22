# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2025
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

from ibm_zos_core.tests.helpers.users import ManagedUserType, ManagedUser
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

DATASET = ""
EXISTING_DATA_SET = "user.private.proclib"
DEFAULT_PATH = "/tmp/testdir"
DEFAULT_PATH_WITH_FILE = f"{DEFAULT_PATH}/testfile"
DEFAULT_DD = "MYDD"
SYSIN_DD = "SYSIN"
SYSPRINT_DD = "SYSPRINT"
IDCAMS_INVALID_STDIN = " hello world #$!@%!#$!@``~~^$*%"


def get_temp_idcams_dataset(hosts):
    """Returns IDCAMS args that use a newly created PDS.
    """
    dataset_name = get_tmp_ds_name()

    hosts.all.shell(f"""dtouch -tPDS -l80 -rFB '{dataset_name}' """)
    hosts.all.shell(f"""decho 'A record' '{dataset_name}(MEMBER)' """)

    return dataset_name, f" LISTCAT ENTRIES('{dataset_name.upper()}')"

# ---------------------------------------------------------------------------- #
#                               Data set DD tests                              #
# ---------------------------------------------------------------------------- #

def test_adrdssu_volume_dump_with_raw_dd(ansible_zos_module, volumes_on_systems):
    """
    Tests a full volume dump using the ADRDSSU utility, replicating the
    exact command-line example. The output dump dataset (DUMPDD) is
    allocated using the 'raw' parameter, allowing ADRDSSU to determine
    the necessary DCB attributes.
    """
    hosts = ansible_zos_module
    dump_dataset = get_tmp_ds_name()
    volume_handler = Volume_Handler(volumes_on_systems)
    # Get a real, available volume from the test system to use.
    test_volume = volume_handler.get_available_vol()

    try:
        # EXECUTION: Call zos_mvs_raw with parameters matching the command.
        results = hosts.all.zos_mvs_raw(
            program_name="ADRDSSU",
            auth=True,
            verbose=True,
            dds=[
                {
                    "dd_data_set": {
                        "dd_name": "DUMPDD",
                        "data_set_name": dump_dataset,
                        "raw": True,
                    }
                },
                {
                    "dd_volume": {
                        "dd_name": "VOLDD",
                        "volume_name": test_volume,
                        "unit": "3390",
                        "disposition": "old",
                    }
                },
                {
                    "dd_input": {
                        "dd_name": "SYSIN",
                        "content": "  DUMP FULL INDDNAME(VOLDD) OUTDDNAME(DUMPDD)"
                    }
                },
                {
                    "dd_output": {
                        "dd_name": "SYSPRINT",
                        "return_content": {
                            "type": "text"
                        }
                    }
                },
            ],
        )
        for result in results.contacted.values():
            print("\nVerbose output from stderr:")
            print(result.get("stderr"))

            assert result.get("ret_code", {}).get("code", -1) == 0
            assert result.get("changed", False) is True
            sysprint_content = "".join(result.get("dd_names")[0].get("content", []))
            assert "ADR101I" in sysprint_content
            assert "ADR006I" in sysprint_content

    finally:
        hosts.all.zos_data_set(name=dump_dataset, state="absent")

def test_full_volume_dump_with_custom_dd_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    dump_dataset = get_tmp_ds_name()
    volume_handler = Volume_Handler(volumes_on_systems)
    test_volume = volume_handler.get_available_vol()
    try:
        results = hosts.all.zos_mvs_raw(
            program_name="ADRDSSU",
            auth=True,
            verbose=True,
            dds=[
                {
                    "dd_data_set": {
                        "dd_name": "DUMPDD",
                        "data_set_name": dump_dataset,
                        "disposition": "new",
                        "disposition_normal": "catalog",
                        "disposition_abnormal": "delete",
                        "space_type": "cyl",
                        "space_primary": 10,
                        "space_secondary": 2,
                        "record_format": "u",
                        "record_length": 0,
                        "block_size": 32760,
                        "type": "seq",
                    }
                },
                {
                    "dd_volume": {
                        "dd_name": "VOLDD",
                        "volume_name": test_volume,
                        "unit": "3390",
                        "disposition": "old",
                    }
                },
                {
                    "dd_input": {
                        "dd_name": "SYSIN",
                        "content": "  DUMP FULL INDDNAME(VOLDD) OUTDDNAME(DUMPDD)"
                    }
                },
                {
                    "dd_output":{
                        "dd_name":"SYSPRINT",
                        "return_content":{
                            "type":"text"
                        }
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert result.get("changed", False) is True
    finally:
        hosts.all.zos_data_set(name=dump_dataset, state="absent")

def test_failing_name_format(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_mvs_raw(
        program_name="idcams",
        dds=[{
            "dd_data_set":{
                "dd_name":DEFAULT_DD,
                "data_set_name":"!!^&.BAD.NAME"
            }
        }],
    )
    for result in results.contacted.values():
        assert "ValueError" in result.get("msg")

@pytest.mark.parametrize(
        # Added this verbose to test issue https://github.com/ansible-collections/ibm_zos_core/issues/1359
        # Where a program will fail if rc != 0 only if verbose was True.
        "verbose",
        [True, False],
)
def test_disposition_new(ansible_zos_module, verbose):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            verbose=verbose,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert result.get("failed", False) is False
            if verbose:
                assert result.get("stderr") is not None
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")

@pytest.mark.parametrize(
        # Added this verbose to test issue https://github.com/ansible-collections/ibm_zos_core/issues/1359
        # Where a program will fail if rc != 0 only if verbose was True.
        "columns",
        [0, 2],
)
def test_dd_content_reserved_columns(ansible_zos_module, columns):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        idcams_listcat_dataset_cmd = idcams_listcat_dataset_cmd.lstrip()

        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "reserved_cols": columns,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            if columns > 0:
                assert result.get("ret_code", {}).get("code", -1) == 0
                assert len(result.get("dd_names", [])) > 0
                assert result.get("failed", False) is False
            else:
                assert result.get("ret_code", {}).get("code", -1) == 12
                assert len(result.get("dd_names", [])) > 0
                assert result.get("failed", False) is True
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")

@pytest.mark.parametrize(
    "disposition",
    ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set(ansible_zos_module, disposition):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(
            name=default_data_set, type="seq", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":disposition,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_list_cat_for_existing_data_set_with_tmp_hlq_option(ansible_zos_module, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        tmphlq = "TMPHLQ"
        volumes = Volume_Handler(volumes_on_systems)
        default_volume = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()[:25]
        hosts.all.zos_data_set(
            name=default_data_set, type="seq", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            tmp_hlq=tmphlq,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "return_content":{
                            "type":"text"
                        },
                        "replace":True,
                        "backup":True,
                        "type":"seq",
                        "space_primary":5,
                        "space_secondary":1,
                        "space_type":"m",
                        "volumes":default_volume,
                        "record_format":"fb"
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            for backup in result.get("backups"):
                assert backup.get("backup_name")[:6] == tmphlq
        for result in results.contacted.values():
            assert result.get("changed", False) is True
    finally:
        results = hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_list_cat_for_existing_data_set_with_tmp_hlq_option_restricted_user(ansible_zos_module, z_python_interpreter):
    """
    This tests the error message when a user cannot create data sets with a given HLQ.
    """
    managed_user = None
    managed_user_test_case_name = "managed_user_list_cat_for_existing_data_set_with_restricted_tmp_hlq_option"
    try:
        # Initialize the Managed user API from the pytest fixture.
        managed_user = ManagedUser.from_fixture(ansible_zos_module, z_python_interpreter)

        # Important: Execute the test case with the managed users execution utility.
        managed_user.execute_managed_user_test(
            managed_user_test_case = managed_user_test_case_name, debug = True,
            verbose = True, managed_user_type=ManagedUserType.ZOS_LIMITED_HLQ)

    finally:
        # Delete the managed user on the remote host to avoid proliferation of users.
        managed_user.delete_managed_user()

def managed_user_list_cat_for_existing_data_set_with_restricted_tmp_hlq_option(ansible_zos_module, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        # IMPORTANT: Do not replace this HLQ unless it changes in the users utility, since this is the HLQ that
        # the restricted hlq user don't have access to.
        tmphlq = "NOPERMIT"
        volumes = Volume_Handler(volumes_on_systems)
        default_volume = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()[:25]
        hosts.all.zos_data_set(
            name=default_data_set, type="seq", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            tmp_hlq=tmphlq,
            dds=[
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            print(result)
            assert result.get("ret_code", {}).get("code", -1) == 8
            assert len(result.get("dd_names", [])) == 0
            assert result.get("changed", False) is False
            assert result.get("failed", False) is True
    finally:
        results = hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# * new data set and append to member in one step not currently supported
def test_new_disposition_for_data_set_members(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        default_data_set_with_member = default_data_set + '(MEM)'
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set_with_member,
                        "disposition":"new",
                        "type":"pds",
                        "directory_blocks":15,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 8
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "disposition",
    ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set_members(ansible_zos_module, disposition):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        default_data_set_with_member = default_data_set + '(MEM)'
        hosts.all.zos_data_set(
            name=default_data_set, type="pds", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set_with_member,
                        "disposition":disposition,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "normal_disposition,changed",
    [("keep", True), ("delete", True), ("catalog", True), ("uncatalog", True)],
)
def test_normal_dispositions_data_set(
    ansible_zos_module,
    normal_disposition,
    changed,
    volumes_on_systems
):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_data_set(
            name=default_data_set,
            type="seq",
            state="present",
            replace=True,
            volumes=[volume_1],
        )
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"shr",
                        "disposition_normal":normal_disposition,
                        "volumes":[volume_1],
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "space_type,primary,secondary,expected",
    [
        ("trk", 3, 1, 169992),
        ("cyl", 3, 1, 2549880),
        ("b", 3, 1, 56664),
        ("k", 3, 1, 56664),
        ("m", 3, 1, 3173184),
    ],
)
def test_space_types(ansible_zos_module, space_type, primary, secondary, expected):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "space_primary":primary,
                        "space_secondary":secondary,
                        "space_type":space_type,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        results2 = hosts.all.command(cmd=f"dls -l -s {default_data_set}")

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0

        for result in results2.contacted.values():
            assert str(expected) in result.get("stdout", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "data_set_type",
    ["pds", "pdse", "large", "basic", "seq"],
)
def test_data_set_types_non_vsam(ansible_zos_module, data_set_type, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":data_set_type,
                        "volumes":[volume_1],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        results = hosts.all.command(cmd=f"dls {default_data_set}")

        for result in results.contacted.values():
            assert "BGYSC1103E" not in result.get("stderr", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "data_set_type",
    ["ksds", "rrds", "lds", "esds"],
)
def test_data_set_types_vsam(ansible_zos_module, data_set_type, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                # * ksds requires additional parameters
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":data_set_type,
                        "volumes":[volume_1],
                    },
                }
                if data_set_type != "ksds"
                else {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":data_set_type,
                        "key_length":5,
                        "key_offset":0,
                        "volumes":[volume_1],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        # * we hope to see EDC5041I An error was detected at the system level when opening a file.
        # * because that means data set exists and is VSAM so we can't read it
        results = hosts.all.command(cmd=f"head \"//'{default_data_set}'\"")
        for result in results.contacted.values():
            assert "EDC5041I" in result.get("stderr", "") or "EDC5049I" in result.get("stderr", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "record_format",
    ["u", "vb", "vba", "fb", "fba"],
)
def test_record_formats(ansible_zos_module, record_format, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "record_format":record_format,
                        "volumes":[volume_1],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        results = hosts.all.command(cmd=f"dls -l {default_data_set}")

        for result in results.contacted.values():
            assert str(f" {record_format.upper()} ") in result.get("stdout", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "return_content_type,expected",
    [
        ("text", "IDCAMS  SYSTEM"),
        (
            "base64",
            "8cnEw8HU4kBA4uji48XUQOLF2eXJw8Xi"
            # the above corresponds to the following bytes:
            # f1 c9 c4 c3 c1 d4 e2 40 40 e2 e8 e2 e3 c5 d4 40 e2 c5 d9 e5 c9 c3 c5 e2
            # which translate in ebdic to: "1IDCAMS  SYSTEM SERVICE"
        ),
    ],
)
def test_return_content_type(ansible_zos_module, return_content_type, expected, volumes_on_systems):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        default_data_set = get_tmp_ds_name()
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        results = hosts.all.zos_data_set(
            name=default_data_set,
            type="seq",
            state="present",
            replace=True,
            volumes=[volume_1],
        )

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"shr",
                        "volumes":[volume_1],
                        "return_content":{
                            "type":return_content_type
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent", volumes=[volume_1])
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "src_encoding,response_encoding,expected",
    [
        ("iso8859-1", "ibm-1047", "qcfe�B||BTBFg�|Bg�GqfgB||"),
        (
            "ibm-1047",
            "iso8859-1",
            "IDCAMS  SYSTEM",
        ),
    ],
)
def test_return_text_content_encodings(
    ansible_zos_module, src_encoding, response_encoding, expected, volumes_on_systems
):
    idcams_dataset = None
    try:
        volumes = Volume_Handler(volumes_on_systems)
        volume_1 = volumes.get_available_vol()
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        results = hosts.all.zos_data_set(
            name=default_data_set,
            type="seq",
            state="present",
            replace=True,
            volumes=[volume_1],
        )
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"shr",
                        "volumes":[volume_1],
                        "return_content":{
                            "type":"text",
                            "src_encoding":src_encoding,
                            "response_encoding":response_encoding,
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent", volumes=[volume_1])
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_reuse_existing_data_set(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(
            name=default_data_set, type="seq", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="IDCAMS",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "reuse":True,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", 0) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_replace_existing_data_set(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(
            name=default_data_set, type="seq", state="present", replace=True
        )
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="IDCAMS",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "replace":True,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", 0) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_replace_existing_data_set_make_backup(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        hosts.all.zos_mvs_raw(
            program_name="IDCAMS",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "replace":True,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        results = hosts.all.zos_mvs_raw(
            program_name="IDCAMS",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "replace":True,
                        "backup":True,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", 0) == 0
            assert len(result.get("dd_names", [])) > 0
            assert len(result.get("backups", [])) > 0
            assert result.get("backups")[0].get("backup_name") is not None
            results2 = hosts.all.command(
                cmd=f"head \"//'{result.get('backups')[0].get('backup_name')}'\""#.format()
            )
            hosts.all.zos_data_set(
                name=result.get("backups")[0].get("backup_name"), state="absent"
            )
            assert (
                result.get("backups")[0].get("original_name").lower()
                == default_data_set.lower()
            )
        for result in results2.contacted.values():
            assert "IDCAMS" in result.get("stdout", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_data_set_name_gdgs(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name(3, 3)
        hosts.all.shell(cmd="dtouch -tGDG -L4 {0}".format(default_data_set))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(default_data_set))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(default_data_set))
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                dict(
                    dd_data_set=dict(
                        dd_name=SYSPRINT_DD,
                        data_set_name=default_data_set + "(0)",
                        return_content=dict(type="text"),
                    ),
                ),
                dict(dd_input=dict(dd_name=SYSIN_DD, content=idcams_listcat_dataset_cmd)),
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
        # Generation minus 1
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                dict(
                    dd_data_set=dict(
                        dd_name=SYSPRINT_DD,
                        data_set_name=default_data_set + "(-1)",
                        return_content=dict(type="text"),
                    ),
                ),
                dict(dd_input=dict(dd_name=SYSIN_DD, content=idcams_listcat_dataset_cmd)),
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
        # Create a new one
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                dict(
                    dd_data_set=dict(
                        dd_name=SYSPRINT_DD,
                        data_set_name=default_data_set + "(+1)",
                        disposition="new",
                        return_content=dict(type="text"),
                    ),
                ),
                dict(dd_input=dict(dd_name=SYSIN_DD, content=idcams_listcat_dataset_cmd)),
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
        # Negative case
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                dict(
                    dd_data_set=dict(
                        dd_name=SYSPRINT_DD,
                        data_set_name=default_data_set + "(-4)",
                        disposition="new",
                        return_content=dict(type="text"),
                    ),
                ),
                dict(dd_input=dict(dd_name=SYSIN_DD, content=idcams_listcat_dataset_cmd)),
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 8
    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_data_set_name_special_characters(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name(5, 6, symbols=True)
        hosts.all.zos_data_set(name=default_data_set, type="seq", state="present")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                dict(
                    dd_data_set=dict(
                        dd_name=SYSPRINT_DD,
                        data_set_name=default_data_set,
                        return_content=dict(type="text"),
                    ),
                ),
                dict(dd_input=dict(dd_name=SYSIN_DD, content=idcams_listcat_dataset_cmd)),
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")

@pytest.mark.parametrize("max_rc", [4, 8])
def test_new_disposition_for_data_set_members_max_rc(ansible_zos_module, max_rc):
    hosts = ansible_zos_module
    results = hosts.all.zos_mvs_raw(
        program_name="idcams",
        auth=True,
        max_rc=max_rc,
        dds=[
            {
                "dd_output":{
                    "dd_name":"sysprint",
                    "return_content":{
                        "type":"text"
                    }
                }
            },
            {
                "dd_input":{
                    "dd_name":"sysin",
                    "content":" DELETE THIS.DATASET.DOES.NOT.EXIST"
                }
            },
        ],
    )
    for result in results.contacted.values():
        assert result.get("changed") is False
        assert result.get("ret_code", {}).get("code", -1) == 8
        if max_rc != 8:
            assert result.get("msg") is not None
            assert result.get("failed") is True

# ---------------------------------------------------------------------------- #
#                                 Input DD Tests                                #
# ---------------------------------------------------------------------------- #


def test_input_empty(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":""
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")


def test_input_large(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        contents = ""
        for i in range(50000):
            contents += f"this is line {i}\n"
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":contents
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 12
            assert len(result.get("dd_names", [])) > 0
            assert len(result.get("dd_names", [{}])[0].get("content")) > 100000
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")


def test_input_provided_as_list(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        contents = []
        for i in range(10):
            contents.append(idcams_listcat_dataset_cmd)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":contents
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert len(result.get("dd_names", [{}])[0].get("content")) > 100
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "return_content_type,expected",
    [
        ("text", "LISTCAT ENTRIES"),
        (
            "base64",
            "QEBA08ni48PB40DF1ePZycX",
            # the above corresponds to the following bytes:
            # 40 d3 c9 e2 e3 c3 c1 e3 40 c5 d5 e3 d9 c9 c5 e2
            # which translate in ebdic to: " LISTCAT ENTRIES"
        ),
    ],
)
def test_input_return_content_types(ansible_zos_module, return_content_type, expected):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                        "return_content":{
                            "type":return_content_type
                        },
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names", [{}])[0].get("content"))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "src_encoding,response_encoding,expected",
    [
        (
            "iso8859-1",
            "ibm-1047",
            "|�qBFfeF|g�F�qgB��",
        ),
        (
            "ibm-1047",
            "iso8859-1",
            "LISTCAT ENTRIES",
        ),
    ],
)
def test_input_return_text_content_encodings(
    ansible_zos_module, src_encoding, response_encoding, expected
):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_data_set":{
                        "dd_name":SYSPRINT_DD,
                        "data_set_name":default_data_set,
                        "disposition":"new",
                        "type":"seq",
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                        "return_content":{
                            "type":"text",
                            "src_encoding":src_encoding,
                            "response_encoding":response_encoding,
                        },
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names", [{}])[0].get("content"))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                              Unix file DD Tests                              #
# ---------------------------------------------------------------------------- #


def test_failing_path_name(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":"1dfa3f4rafwer/f2rfsd",
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 8
            assert "ValueError" in result.get("msg", "")
    finally:
        if idcams_dataset:
            results = hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_create_new_file(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_write_to_existing_file(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="present")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "normal_disposition,expected", [("keep", True), ("delete", False)]
)
def test_file_normal_disposition(ansible_zos_module, normal_disposition, expected):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="present")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "disposition_normal":normal_disposition,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.stat(path=DEFAULT_PATH_WITH_FILE)
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert result.get("stat", {}).get("exists", not expected) is expected
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize("mode,expected", [(644, "0644"), (755, "0755")])
def test_file_modes(ansible_zos_module, mode, expected):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "mode":mode,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.stat(path=DEFAULT_PATH_WITH_FILE)
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert result.get("stat", {}).get("mode", "") == expected
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "access_group,status_group",
    [
        ("rw", ["ocreat", "oexcl"]),
        ("w", ["ocreat", "oexcl"]),
        ("rw", ["ocreat", "oappend"]),
    ],
)
def test_file_path_options(ansible_zos_module, access_group, status_group):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "access_group":access_group,
                        "status_group":status_group,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "block_size",
    [10, 20, 50, 80, 120],
)
def test_file_block_size(ansible_zos_module, block_size):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "block_size":block_size,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "record_length",
    [10, 20, 50, 80, 120],
)
def test_file_record_length(ansible_zos_module, record_length):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "record_length":record_length,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "record_format",
    ["u", "vb", "vba", "fb", "fba"],
)
def test_file_record_format(ansible_zos_module, record_format):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "record_format":record_format,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.command(cmd=f"cat {DEFAULT_PATH_WITH_FILE}")
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
        for result in results2.contacted.values():
            assert "IDCAMS  SYSTEM" in result.get("stdout", "")
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "return_content_type,expected",
    [
        ("text", "IDCAMS  SYSTEM"),
        (
            "base64",
            "8cnEw8HU4kBA4uji48XUQOLF2eXJw8Xi",
            # the above corresponds to the following bytes:
            # f1 c9 c4 c3 c1 d4 e2 40 40 e2 e8 e2 e3 c5 d4 40 e2 c5 d9 e5 c9 c3 c5 e2
            # which translate in ebdic to: "1IDCAMS  SYSTEM SERVICES"
        ),
    ],
)
def test_file_return_content(ansible_zos_module, return_content_type, expected):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "return_content":{
                            "type":return_content_type
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "src_encoding,response_encoding,expected",
    [
        ("iso8859-1", "ibm-1047", "qcfe�B||BTBFg�|Bg�GqfgB|"),
        (
            "ibm-1047",
            "iso8859-1",
            "IDCAMS  SYSTEM",
        ),
    ],
)
def test_file_return_text_content_encodings(
    ansible_zos_module, src_encoding, response_encoding, expected
):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_unix":{
                        "dd_name":SYSPRINT_DD,
                        "path":DEFAULT_PATH_WITH_FILE,
                        "return_content":{
                            "type":"text",
                            "src_encoding":src_encoding,
                            "response_encoding":response_encoding,
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert expected in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                                Dummy DD Tests                                #
# ---------------------------------------------------------------------------- #


def test_dummy(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_dummy":{
                        "dd_name":SYSPRINT_DD,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) == 0
    finally:
        hosts.all.file(path=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                            Concatenation DD Tests                            #
# ---------------------------------------------------------------------------- #


def test_concatenation_with_data_set_dd_and_response(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        default_data_set_2 = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set,
                                    "disposition":"new",
                                    "type":"seq",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set_2,
                                    "disposition":"new",
                                    "type":"seq",
                                }
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_concatenation_with_data_set_dd_with_replace_and_backup(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        default_data_set_2 = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="present", type="seq")
        hosts.all.zos_data_set(name=default_data_set_2, state="present", type="seq")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set,
                                    "disposition":"new",
                                    "type":"seq",
                                    "replace":True,
                                    "backup":True,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set_2,
                                    "disposition":"new",
                                    "type":"seq",
                                    "replace":True,
                                    "backup":True,
                                }
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )

        for result in results.contacted.values():
            hosts.all.zos_data_set(
                name=result.get("backups")[0].get("backup_name"), state="absent"
            )
            hosts.all.zos_data_set(
                name=result.get("backups")[1].get("backup_name"), state="absent"
            )
            assert (
                result.get("backups")[0].get("original_name").lower()
                == default_data_set.lower()
            )
            assert (
                result.get("backups")[1].get("original_name").lower()
                == default_data_set_2.lower()
            )
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_concatenation_with_data_set_member(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        default_data_set_2 = get_tmp_ds_name()
        default_data_set_with_member = default_data_set + '(MEM)'
        hosts.all.zos_data_set(name=default_data_set, state="present", type="pds")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set_with_member,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set_2,
                                    "disposition":"new",
                                    "type":"seq",
                                }
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        results2 = hosts.all.shell(
            cmd=f"cat \"//'{default_data_set_with_member}'\""
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
        for result in results2.contacted.values():
            assert "IDCAMS" in result.get("stdout", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_concatenation_with_unix_dd_and_response_datasets(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        default_data_set_2 = get_tmp_ds_name()
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_unix":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":default_data_set_2,
                                    "disposition":"new",
                                    "type":"seq",
                                }
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
    finally:
        hosts.all.file(name=DEFAULT_PATH, state="absent")
        hosts.all.zos_data_set(name=default_data_set_2, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_concatenation_with_unix_dd_and_response_uss(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_unix":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_input":{
                                    "content":"Hello world!",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 1
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
            assert "Hello world!" in "\n".join(result.get("dd_names")[1].get("content", []))
    finally:
        hosts.all.file(name=DEFAULT_PATH, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


def test_concatenation_fail_with_unsupported_dd_type(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_dummy":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                },
                                "dd_concat":{},
                            },
                        ],
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd,
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == -1
            assert "Unsupported parameters" in result.get("msg", "")
    finally:
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


@pytest.mark.parametrize(
    "dds,input_pos,input_content",
    [
        (
            [
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_unix":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":"ANSIBLE.USER.PRIVATE.TEST",
                                    "disposition":"shr",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_input":{
                                    "content":"Hello world!",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                        ],
                    },
                },
            ],
            2,
            "Hello world!",
        ),
        (
            [
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_data_set":{
                                    "data_set_name":"ANSIBLE.USER.PRIVATE.TEST",
                                    "disposition":"shr",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_unix":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_input":{
                                    "content":"Hello world!",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                        ],
                    },
                },
            ],
            2,
            "Hello world!",
        ),
        (
            [
                {
                    "dd_concat":{
                        "dd_name":SYSPRINT_DD,
                        "dds":[
                            {
                                "dd_input":{
                                    "content":"Hello world!",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_data_set":{
                                    "data_set_name":"ANSIBLE.USER.PRIVATE.TEST",
                                    "disposition":"shr",
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                            {
                                "dd_unix":{
                                    "path":DEFAULT_PATH_WITH_FILE,
                                    "return_content":{
                                        "type":"text"
                                    },
                                }
                            },
                        ],
                    },
                },
            ],
            0,
            "IDCAMS",
        ),
    ],
)
def test_concatenation_all_dd_types(ansible_zos_module, dds, input_pos, input_content):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module

        default_data_set = "ANSIBLE.USER.PRIVATE.TEST"
        hosts.all.zos_data_set(name=default_data_set, state="present", type="seq")

        hosts.all.file(path=DEFAULT_PATH, state="directory")
        hosts.all.file(path=DEFAULT_PATH_WITH_FILE, state="absent")

        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        dds.append(
            {
                'dd_input': {
                    "dd_name": SYSIN_DD,
                    "content": idcams_listcat_dataset_cmd
                }
            }
        )

        results = hosts.all.zos_mvs_raw(program_name="idcams", auth=True, dds=dds)
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 2
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
            assert input_content in "\n".join(
                result.get("dd_names")[input_pos].get("content", [])
            )
    finally:
        hosts.all.file(name=DEFAULT_PATH, state="absent")
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                                Execution Tests                               #
# ---------------------------------------------------------------------------- #


def test_authorized_program_run_unauthorized(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=False,
            dds=[],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 36
            assert len(result.get("dd_names", [])) == 0
            assert "BGYSC0236E" in result.get("msg", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")


def test_unauthorized_program_run_authorized(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="DSPURX00",
            auth=True,
            dds=[],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 15
            assert len(result.get("dd_names", [])) == 0
            assert "BGYSC0215E" in result.get("msg", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")

@pytest.mark.parametrize(
        # Added this verbose to test issue https://github.com/ansible-collections/ibm_zos_core/issues/1359
        # Where a program will fail if rc != 0 only if verbose was True.
        # Where previously a program would NOT fail when rc != 0 unless verbose was True.
        "verbose",
        [True, False],
)
def test_authorized_program_run_authorized(ansible_zos_module, verbose):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            verbose=verbose,
            dds=[
                {
                    "dd_output":{
                        "dd_name":SYSPRINT_DD,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 16
            assert len(result.get("dd_names", [])) == 1
            assert "BGYSC0236E" not in result.get("msg", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")


def test_unauthorized_program_run_unauthorized(ansible_zos_module):
    try:
        hosts = ansible_zos_module
        default_data_set = get_tmp_ds_name()
        hosts.all.zos_data_set(name=default_data_set, state="absent")
        results = hosts.all.zos_mvs_raw(
            program_name="IEFBR14",
            auth=False,
            dds=[],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) == 0
            assert "BGYSC0215E" not in result.get("msg", "")
    finally:
        hosts.all.zos_data_set(name=default_data_set, state="absent")


def test_missing_program_name(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_mvs_raw(
        auth=False,
        dds=[],
    )
    for result in results.contacted.values():
        assert result.get("ret_code", {}).get("code", -1) == -1
        assert len(result.get("dd_names", [])) == 0
        assert "missing required arguments" in result.get("msg", "")


def test_with_parms(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_mvs_raw(
        pgm="iefbr14",
        auth=False,
        parm="P1,123,P2=5",
        dds=[],
    )
    for result in results.contacted.values():
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) == 0


def test_with_multiple_of_same_dd_name(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)
        results = hosts.all.zos_mvs_raw(
            pgm="idcams",
            auth=True,
            dds=[
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 8
            assert len(result.get("dd_names", [])) == 0
            assert "BGYSC0228E" in result.get("msg", "")
    finally:
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                                 VIO DD Tests                                 #
# ---------------------------------------------------------------------------- #


def test_vio_as_output(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_vio":{
                        "dd_name":SYSPRINT_DD,
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )
        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", 0) == 0
            assert len(result.get("dd_names", [])) == 0
    finally:
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")


# ---------------------------------------------------------------------------- #
#                                Output DD Tests                               #
# ---------------------------------------------------------------------------- #


def test_output_dd(ansible_zos_module):
    idcams_dataset = None
    try:
        hosts = ansible_zos_module
        data_set_name = None
        idcams_dataset, idcams_listcat_dataset_cmd = get_temp_idcams_dataset(hosts)

        results = hosts.all.zos_mvs_raw(
            program_name="idcams",
            auth=True,
            dds=[
                {
                    "dd_output":{
                        "dd_name":SYSPRINT_DD,
                        "return_content":{
                            "type":"text"
                        },
                    },
                },
                {
                    "dd_input":{
                        "dd_name":SYSIN_DD,
                        "content":idcams_listcat_dataset_cmd
                    }
                },
            ],
        )

        for result in results.contacted.values():
            assert result.get("ret_code", {}).get("code", -1) == 0
            assert len(result.get("dd_names", [])) > 0
            assert "IDCAMS" in "\n".join(result.get("dd_names")[0].get("content", []))
            data_set_name = result.get("dd_names")[0].get("name", "")
            assert data_set_name != ""
    finally:
        if data_set_name:
            hosts.all.zos_data_set(name=data_set_name, state="absent")
        if idcams_dataset:
            hosts.all.zos_data_set(name=idcams_dataset, state="absent")
