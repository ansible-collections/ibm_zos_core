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

from ibm_zos_core.tests.helpers.utils import get_random_file_name

def _get_random_racf_name(prefix):
    return get_random_file_name(prefix=prefix)[:8].upper()

def _run_tso_command(hosts, command):
    return hosts.all.shell(cmd='tsocmd "{0}"'.format(command))

def test_name_with_whitespace_user(ansible_zos_module):
    results = ansible_zos_module.all.zos_user_info(
        name="Hello User",
        profile_type="user"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert "Invalid value for parameter 'name'" in result.get("msg", "")
        assert "Hello User" in result.get("msg", "")
        assert "Expected a single RACF profile name with no spaces or blank characters" in result.get("msg", "")

def test_name_with_whitespace_group(ansible_zos_module):
    results = ansible_zos_module.all.zos_user_info(
        name="Hello Group",
        profile_type="group"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("changed") is False
        assert "Invalid value for parameter 'name'" in result.get("msg", "")
        assert "Hello Group" in result.get("msg", "")
        assert "Expected a single RACF profile name with no spaces or blank characters" in result.get("msg", "")

def test_invalid_profile_type(ansible_zos_module):
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU100",
        profile_type="test_invalid_profile_type"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert "profile_type" in result.get("msg", "").lower()
        assert "value of profile_type must be one of: user, group, got: test_invalid_profile_type"  in result.get("msg", "").lower()

def test_invalid_user_segment(ansible_zos_module):
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU100",
        profile_type="user",
        segments=["dfp", "test_invalid_segment"]
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert "value of segments must be one or more of:" in result.get("msg", "").lower()
        assert "got no match for: test_invalid_segment" in result.get("msg", "").lower()

def test_missing_user_profile(ansible_zos_module):
    # Valid format but user does not exist — RACF returns "UNABLE TO LOCATE USER ENTRY <name>"
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU100",
        profile_type="user"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("rc") == 4
        assert "LISTUSER TSTU100" in result.get("cmd")
        assert result.get("stdout") == ""
        assert "UNABLE TO LOCATE" in result.get("stderr", "").upper()
        assert "Profile 'TSTU100' not found in RACF database" in result.get("msg")


def test_invalid_user_profile_name(ansible_zos_module):
    # Name exceeds 8 characters — RACF returns "INVALID USERID, <name>"
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU001123",
        profile_type="user"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("rc") == 8
        assert "LISTUSER TSTU001123" in result.get("cmd")
        assert result.get("stdout") == ""
        assert "INVALID USERID, TSTU001123" in result.get("stderr", "").upper()
        assert "Profile 'TSTU001123' not found in RACF database" in result.get("msg")


def test_missing_group_profile(ansible_zos_module):
    # Valid format but group does not exist — RACF returns "NAME NOT FOUND IN RACF DATA SET"
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU100",
        profile_type="group"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("rc") == 4
        assert "LISTGRP TSTU100" in result.get("cmd")
        assert result.get("stdout") == ""
        assert "NAME NOT FOUND IN RACF DATA SET" in result.get("stderr", "").upper()
        assert "Profile 'TSTU100' not found in RACF database" in result.get("msg")


def test_invalid_group_profile_name(ansible_zos_module):
    # Name exceeds 8 characters — RACF returns "INVALID GROUP NAME, <name>"
    results = ansible_zos_module.all.zos_user_info(
        name="TSTU001123",
        profile_type="group"
    )

    for result in results.contacted.values():
        assert result.get("failed") is True
        assert result.get("rc") == 8
        assert "LISTGRP TSTU001123" in result.get("cmd")
        assert result.get("stdout") == ""
        assert "INVALID GROUP NAME, TSTU001123" in result.get("stderr", "").upper()
        assert "Profile 'TSTU001123' not found in RACF database" in result.get("msg")


def test_user_tso_omvs_segments(ansible_zos_module):
    hosts = ansible_zos_module
    test_group = _get_random_racf_name("TG")
    test_user = _get_random_racf_name("TU")

    try:
        _run_tso_command(hosts, "ADDGROUP {0}".format(test_group))
        _run_tso_command(
            hosts,
            "ADDUSER ({0}) NAME('TEST USER NAME') DATA('Test User - Installation Data') "
            "OWNER({1}) DFP( DATAAPPL(TESTAPP) DATACLAS(DCLAS001) "
            "MGMTCLAS(MCLAS001) STORCLAS(SCLAS001) ) TSO( ACCTNUM(33000) "
            "COMMAND('ISPF PANEL(ISR@390)') DEST(RMT001) HOLDCLASS(H) JOBCLASS(A) "
            "MSGCLASS(X) SYS(A) SIZE(16384) MAXSIZE(32768) PROC(IKJACCNT) UNIT(SYSDA) "
            "USERDATA(E4F1) ) OMVS( AUTOUID HOME(/u/tstu047) PROGRAM(/bin/bash) "
            "MEMLIMIT(10g) SHMEMMAX(10g) ASSIZEMAX(104857600) MMAPAREAMAX(4096) "
            "PROCUSERMAX(200) THREADSMAX(400) CPUTIMEMAX(7200) FILEPROCMAX(5000) ) "
            "DFLTGRP({1}) CLAUTH( TERMINAL FACILITY ) ROAUDIT NOOIDCARD OPERATIONS".format(
                test_user, test_group
            )
        )

        results = hosts.all.zos_user_info(
            name=test_user,
            profile_type="user",
            segments=["tso", "omvs", "dfp"]
        )

        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("changed") is False
            returned_segments = result.get("segments", {})
            assert "base_segment" in returned_segments
            assert "group" in returned_segments
            assert "DFP" in returned_segments
            assert "TSO" in returned_segments
            assert "OMVS" in returned_segments
            assert len(returned_segments) == 5
    finally:
        hosts.all.shell(cmd='tsocmd "DELUSER {0}"'.format(test_user))
        hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))    

def test_user_operparm_lang_segments(ansible_zos_module):
    hosts = ansible_zos_module
    test_group = _get_random_racf_name("TG")
    test_user = _get_random_racf_name("TV")

    try:
        _run_tso_command(hosts, "ADDGROUP {0}".format(test_group))
        _run_tso_command(
            hosts,
            "ADDUSER ({0}) NAME('TEST USER TWO') DATA('Test User - Operations Data') "
            "OWNER({1}) LANGUAGE( PRIMARY(ENU) SECONDARY(JPN) ) "
            "DFLTGRP({1}) RESTRICTED WHEN( DAYS( monday tuesday wednesday thursday friday ) "
            "TIME(0900:1700) ) OPERPARM( ALTGRP({1}) AUTH(info) CMDSYS(MVS) KEY(TST0705) "
            "MIGID(YES) MONITOR( jobnames sess status ) LEVEL(all) MFORM(m) STORAGE(1000) "
            "MSCOPE( SYS1 SYS2 ) AUTO(YES) DOM(normal) HC(YES) INTIDS(YES) "
            "ROUTCODE( 1 2 11 ) UD(NO) UNKNIDS(NO) LOGCMDRESP(SYSTEM) )".format(
                test_user, test_group
            )
        )

        results = hosts.all.zos_user_info(
            name=test_user,
            profile_type="user",
            segments=["operparm", "lang"]
        )

        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("changed") is False
            returned_segments = result.get("segments", {})
            assert "base_segment" in returned_segments
            assert "group" in returned_segments
            assert "OPERPARM" in returned_segments
            assert "LANGUAGE" in returned_segments
            assert len(returned_segments) == 4
    finally:
        hosts.all.shell(cmd='tsocmd "DELUSER {0}"'.format(test_user))
        hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))

def test_user_dce_cics_kerb_lnotes_workattr_segments(ansible_zos_module):
    hosts = ansible_zos_module
    test_group = _get_random_racf_name("TG")
    test_user = _get_random_racf_name("TW")

    try:
        _run_tso_command(hosts, "ADDGROUP {0}".format(test_group))
        _run_tso_command(
            hosts,
            "ADDUSER ({0}) NAME('TEST USER THREE') DATA('Test User - Operations Data') "
            " OWNER({1}) DFLTGRP({1})".format(test_user, test_group)
        )
        _run_tso_command(
            hosts,
            "ALTUSER {0} DCE(HOMEUUID(12345678-1234-1234-1234-1234567890ab) "
            "AUTOLOGIN(YES) DCENAME(jsmith_principal) HOMECELL(/.../DCE_CELL_01) "
            "UUID(87654321-4321-4321-4321-ba0987654321)) "
            "KERB(ENCRYPT(NODES NODES3 NODESD NOAES128 AES256 NOAES128SHA2 AES256SHA2) "
            "KERBNAME('jsmith') MAXTKTLFE(86400)) "
            "LNOTES(SNAME('NEW-GUY 1')) "
            "WORKATTR(WAACCNT('ACT-9982') WAADDR1('123 Main St')) "
            "CICS(OPCLASS(1 2 5) OPIDENT(JS1) OPPRTY(12) RSLKEY(99) TIMEOUT(0015))".format(
                test_user
            )
        )

        results = hosts.all.zos_user_info(
            name=test_user,
            profile_type="user",
            segments=["dce", "cics", "kerb", "lnotes", "workattr"]
        )

        for result in results.contacted.values():
            returned_segments = result.get("segments", {})
            assert result.get("rc") == 0
            assert result.get("changed") is False
            assert "base_segment" in returned_segments
            assert "group" in returned_segments
            assert "DCE" in returned_segments
            assert "CICS" in returned_segments
            assert "KERB" in returned_segments
            assert "LNOTES" in returned_segments
            assert "WORKATTR" in returned_segments
            assert len(returned_segments) == 7
    finally:
        hosts.all.shell(cmd='tsocmd "DELUSER {0}"'.format(test_user))
        hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))

def test_group_dfp_csdata_omvs_segments(ansible_zos_module):
    hosts = ansible_zos_module
    test_group = _get_random_racf_name("TG")

    try:
        _run_tso_command(
            hosts,
            "ADDGROUP ({0}) DATA('Complete group profile with all attributes') "
            "OWNER(SYS1) "
            "DFP( DATAAPPL(TESTAPP) DATACLAS(DCLAS001) MGMTCLAS(MCLAS001) STORCLAS(SCLAS001) ) "
            "OMVS(AUTOGID) ".format(test_group)
        )

        results = hosts.all.zos_user_info(
            name=test_group,
            profile_type="group",
            segments=["dfp", "omvs", "csdata"]
        )

        for result in results.contacted.values():
            returned_segments = result.get("segments", {})
            assert result.get("rc") == 0
            assert result.get("changed") is False
            assert "base_segment" in returned_segments
            assert "users" in returned_segments
            assert "DFP" in returned_segments
            assert "OMVS" in returned_segments
            assert "CSDATA" in returned_segments
            assert len(returned_segments) == 5
    finally:
        hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))

def test_group_ignores_user_only_segments(ansible_zos_module):
    hosts = ansible_zos_module
    test_group = _get_random_racf_name("TG")

    try:
        _run_tso_command(
            hosts,
            "ADDGROUP ({0}) DATA('Group profile for ignored segment validation') "
            "OWNER(SYS1) "
            "DFP( DATAAPPL(TESTAPP) DATACLAS(DCLAS001) MGMTCLAS(MCLAS001) STORCLAS(SCLAS001) )".format(test_group)
        )

        results = hosts.all.zos_user_info(
            name=test_group,
            profile_type="group",
            segments=["dfp", "lang", "tso"]
        )

        for result in results.contacted.values():
            returned_segments = result.get("segments", {})
            assert result.get("rc") == 0
            assert result.get("changed") is False
            assert "base_segment" in returned_segments
            assert "users" in returned_segments
            assert "DFP" in returned_segments
            assert "LANGUAGE" not in returned_segments
            assert "TSO" not in returned_segments
            assert len(returned_segments) == 3
    finally:
        hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))

def test_user_missing_segment_returns_empty_dict(ansible_zos_module):
      hosts = ansible_zos_module
      test_group = _get_random_racf_name("TG")
      test_user = _get_random_racf_name("TU")

      try:
          _run_tso_command(hosts, "ADDGROUP {0}".format(test_group))
          _run_tso_command(
              hosts,
              "ADDUSER {0} DFLTGRP({1}) OWNER({1})".format(test_user, test_group)
          )

          results = hosts.all.zos_user_info(
              name=test_user,
              profile_type="user",
              segments=["tso"]
          )

          for result in results.contacted.values():
              assert result.get("rc") == 0
              assert result.get("changed") is False
              returned_segments = result.get("segments", {})
              assert "TSO" in returned_segments
              assert returned_segments["TSO"] == {}
      finally:
          hosts.all.shell(cmd='tsocmd "DELUSER {0}"'.format(test_user))
          hosts.all.shell(cmd='tsocmd "DELGROUP {0}"'.format(test_group))        
