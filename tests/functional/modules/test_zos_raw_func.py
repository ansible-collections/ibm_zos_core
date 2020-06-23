# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from pprint import pprint

EXISTING_DATA_SET = "user.private.proclib"
DEFAULT_DATA_SET = "user.private.rawds"
DEFAULT_DATA_SET_WITH_MEMBER = "{0}(mem1)".format(DEFAULT_DATA_SET)
DEFAULT_DD = "MYDD"
SYSIN_DD = "SYSIN"
SYSPRINT_DD = "SYSPRINT"
IDCAMS_STDIN = " LISTCAT ENTRIES('{0}')".format(EXISTING_DATA_SET.upper())
IDCAMS_INVALID_STDIN = " hello world #$!@%!#$!@``~~^$*%"
DEFAULT_VOLUME = "000000"


# ---------------------------------------------------------------------------- #
#                               Data set DD tests                              #
# ---------------------------------------------------------------------------- #


def test_failing_name_format(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_raw(
        program_name="idcams",
        dds=[dict(dd_data_set=dict(dd_name=DEFAULT_DD, data_set_name="!!^&.BAD.NAME"))],
    )
    for result in results.contacted.values():
        pprint(result)
        assert "ValueError" in result.get("msg")


def test_disposition_new(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "disposition", ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set(ansible_zos_module, disposition):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition=disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


# * new data set and append to member in one step not currently supported
def test_new_disposition_for_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET_WITH_MEMBER,
                    disposition="new",
                    type="pds",
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 8
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", True) is False


@pytest.mark.parametrize(
    "disposition", ["shr", "mod", "old"],
)
def test_dispositions_for_existing_data_set_members(ansible_zos_module, disposition):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="pds", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET_WITH_MEMBER,
                    disposition=disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True


@pytest.mark.parametrize(
    "normal_disposition,changed",
    [("keep", True), ("delete", True), ("catalog", True), ("uncatalog", True)],
)
def test_normal_dispositions_data_set(ansible_zos_module, normal_disposition, changed):
    hosts = ansible_zos_module
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET,
        type="seq",
        state="present",
        replace=True,
        volumes=[DEFAULT_VOLUME],
    )
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    disposition_normal=normal_disposition,
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, state="absent", volumes=[DEFAULT_VOLUME]
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", not changed) is changed


@pytest.mark.parametrize(
    "abnormal_disposition,changed",
    [("keep", True), ("delete", False), ("catalog", True)],
)
def test_abnormal_dispositions_data_set(
    ansible_zos_module, abnormal_disposition, changed
):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(
        name=DEFAULT_DATA_SET, type="seq", state="present", replace=True
    )
    results = hosts.all.zos_raw(
        program_name="IGYCRCTL",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="shr",
                    disposition_abnormal=abnormal_disposition,
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_INVALID_STDIN)),
        ],
    )
    # for result in results.contacted.values():
    #     pprint(result)
    #     assert result.get("ret_code", {}).get("code", 0) != 0
    #     assert len(result.get("dd_names", [])) > 0
    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", not changed) is changed


@pytest.mark.parametrize(
    "space_type,primary,secondary,expected",
    [
        ("trk", 3, 1, 169992),
        ("cyl", 3, 1, 2549880),
        ("b", 3, 1, 56664),
        ("k", 3, 1, 56664),
        ("m", 3, 1, 2889864),
    ],
)
def test_space_types(ansible_zos_module, space_type, primary, secondary, expected):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    results = hosts.all.zos_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(
                dd_data_set=dict(
                    dd_name=SYSPRINT_DD,
                    data_set_name=DEFAULT_DATA_SET,
                    disposition="new",
                    type="seq",
                    space_primary=primary,
                    space_secondary=secondary,
                    space_type=space_type,
                    volumes=[DEFAULT_VOLUME],
                    return_content=dict(type="text"),
                ),
            ),
            dict(dd_input=dict(dd_name=SYSIN_DD, content=IDCAMS_STDIN)),
        ],
    )
    for result in results.contacted.values():
        pprint(result)
        assert result.get("ret_code", {}).get("code", -1) == 0
        assert len(result.get("dd_names", [])) > 0
    results = hosts.all.command(cmd="dls -l -s {0}".format(DEFAULT_DATA_SET))
    for result in results.contacted.values():
        pprint(result)
        assert str(expected) in result.get("stdout", "")

    results = hosts.all.zos_data_set(name=DEFAULT_DATA_SET, state="absent")
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed", False) is True
