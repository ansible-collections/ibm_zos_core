#!/usr/bin/python
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

import pytest
from shellescape import quote

from ibm_zos_core.tests.helpers.dataset import (
    get_tmp_ds_name,
    get_random_q,
)

from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type

TEST_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_LITERAL_CONTENT = """IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
*DEALLOC SYSRES
IEF479I SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
IEF456I JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_AFTER = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
=/usr/lpp/zoautil/v100
export
export _BPXK_AUTOCVT"""

TEST_AFTER_REPLACE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
HOME_ROOT=/usr/lpp/zoautil/v100
export HOME_ROOT
export _BPXK_AUTOCVT"""

TEST_AFTER_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100"""

TEST_AFTER_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export TMP=tmp/etc
export TMP=tmp/etc"""

TEST_BEFORE = """if [ -z  ] && tty -s;
then
    export =none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_REPLACE = """if [ -z STAND ] && tty -s;
then
    export STAND=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER = """if [ -z STEPLIB ] && tty -s;
then
    port STEPLIB=none
    ec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_REPLACE = """if [ -z STEPLIB ] && tty -s;
then
    ixport STEPLIB=none
    ixec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_LINE = """if [ -z STEPLIB ] && tty -s;
then
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

TEST_BEFORE_AFTER_REPLACE_LINE = """if [ -z STEPLIB ] && tty -s;
then
    export SHELL
    export SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

SRC_INVALID_UTF8 = """MOUNT FILESYSTEM('TEST.ZFS.DATA.USER')
MOUNTPOINT('/tmp/src/somedirectory') 0xC1
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
MOUNTPOINT('/tmp/zfs_aggr1')
TYPE('ZFS')
SECURITY
"""

SRC_INVALID_UTF8_REPLACE = """MOUNT FILESYSTEM('TEST.ZFS.DATA.USER')
MOUNTPOINT('/tmp/src/somedirectory') 0xC1
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
('/tmp/zfs_aggr1')
TYPE('ZFS')
SECURITY"""

TEST_LITERAL_CONTENT_AFTER="""IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
*DEALLOC SYSRES
IEF479I SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
 JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_LITERAL_CONTENT_BEFORE = """IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
*DEALLOC SYSRES
 SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
IEF456I JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_LITERAL_CONTENT_REGEXP = """IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
*DEALLOC SYSRES
IEF479I SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
IEF456I JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_LITERAL_CONTENT_BEFORE_AFTER="""IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
*DEALLOC SYSRES
IEF479I SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_LITERAL_CONTENT_AFTER_REGEXP = """IEE131I TRACE REPORT:
   STEP1 - MEMORY USAGE 85%
   STEP2 - IO UTILIZATION 60%
   STEP3 - CPU TIME 5.4 SEC
*TRACE OFF
IEE134I TRACE DISABLED - MONITORING STOPPED
IEF479I SYSTEM RESOURCES DEALLOCATED - MEMORY FREED
*CANCEL JOB56789
//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv
IEF456I JOB56789 CANCELLED SUCCESSFULLY - TIME=17.24.12
IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED"""

TEST_MULTIPLE_LINES = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
ZOAU_ROOT=/usr/lpp/zoautil/v100"""

TEST_BACKREF = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export NEW_PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export NEW_ZOAU_ROOT
export NEW__BPXK_AUTOCVT"""

TEST_MATCH_MULTIPLE_LINES = """### REPLACED MULTILINE TEXT ###
export STEPLIB=custom
exec -a 0 /bin/bash
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

#####################
#  Set up testing
#####################

TMP_DIRECTORY = "/tmp/"

ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']

DS_TYPE = ['seq', 'pds', 'pdse']

BACKUP_OPTIONS = ["SEQ", "MEM"]

def set_uss_environment(ansible_zos_module, content, file):
    hosts = ansible_zos_module
    hosts.all.file(path=file, state="touch")
    hosts.all.shell(cmd=f"echo \"{content}\" > {file}")

def remove_uss_environment(ansible_zos_module, file):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="rm " + file)

def set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
    hosts.all.shell(cmd=f"dtouch {ds_name} -t {ds_type}")
    if ds_type in ["pds", "pdse"]:
        ds_full_name = ds_name + "(MEM)"
        hosts.all.shell(cmd=f"decho '' '{ds_full_name}' ")
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
    else:
        ds_full_name = ds_name
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
    hosts.all.shell(cmd=cmd_str)
    hosts.all.shell(cmd="rm -rf " + temp_file)
    return ds_full_name

def remove_ds_environment(ansible_zos_module, ds_name):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"drm -F {ds_name}")

#####################
# Testing
#####################

#########################
# USS test cases
#########################

def test_uss_after(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "replace":"HOME_ROOT",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
        "replace":"export TMP=tmp/etc",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"STEPLIB",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"STEPLIB",
        "replace":"STAND",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
        "replace":"PATH=/usr/lpp/zoautil/v100/bin",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
        "replace":"ix",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_replace_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
        "replace":"    export SHELL",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_REPLACE_LINE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_backup_no_name(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "backup":True,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
            backup_name = result.get("backup_name")
            assert result.get("backup_name") is not None
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER
        results = hosts.all.shell(cmd="cat {0}".format(backup_name))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)
        remove_uss_environment(ansible_zos_module, backup_name)

def test_uss_backup_name(ansible_zos_module):
    hosts = ansible_zos_module
    uss_backup_file = get_random_file_name(dir=TMP_DIRECTORY, suffix=".tmp")
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "backup":True,
        "backup_name":uss_backup_file
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 2
            assert result.get("backup_name") == uss_backup_file
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER
        results = hosts.all.shell(cmd="cat {0}".format(uss_backup_file))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)
        remove_uss_environment(ansible_zos_module, uss_backup_file)

def test_uss_after_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["after"]
    params = {
        "regexp":"IEF456I",
        "after":"IEF479I SYSTEM RESOURCES DEALLOCATED",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["before"]
    params = {
        "regexp":"IEF479I",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_BEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_regexp_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["regexp"]
    params = {
        "regexp":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_REGEXP
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_before_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["after", "before"]
    params = {
        "regexp":"^IEF456I *",
        "after":"*CANCEL JOB56789",
        "before":"IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_BEFORE_AFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_after_regexp_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["after", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "after":"   STEP3 - CPU TIME 5.4 SEC",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_regexp_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["before", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_before_after_regexp_literal(ansible_zos_module):
    hosts = ansible_zos_module
    literal = ["after", "before", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "after":"*TRACE OFF",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_remove_multiple_lines(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^export\s+(ZOAU_ROOT|_BPXK_AUTOCVT|PATH)*",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 3
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_MULTIPLE_LINES
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_backref(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"^(export\s+)(PATH|ZOAU_ROOT|_BPXK_AUTOCVT)*",
        "replace": r"\1NEW_\2",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 3
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BACKREF
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_uss_match_replace_multiple_lines(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"(?s)^(if .*?\nthen\n.*?\n.*?\n.*?\n)",
        "replace":"""### REPLACED MULTILINE TEXT ###
export STEPLIB=custom
exec -a 0 /bin/bash
""",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_MATCH_MULTIPLE_LINES
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

#########################
# Dataset test cases
#########################

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_replace(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "replace":"HOME_ROOT",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_REPLACE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_replace_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^export \w+",
        "after":"export PATH",
        "replace":"export TMP=tmp/etc",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER_REPLACE_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"STEPLIB",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_replace(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"STEPLIB",
        "replace":"STAND",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_REPLACE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_replace_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^PATH=\/[\w\/]+(:\/[\w\/]+)*",
        "before":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
        "replace":"PATH=/usr/lpp/zoautil/v100/bin",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_REPLACE_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_before(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_before_replace(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ex",
        "after":"then",
        "before":"fi",
        "replace":"ix",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_REPLACE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_before_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_before_replace_line(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^\s*(export \w+=\w+|exec -a \d+ \w+)",
        "after":"then",
        "before":"fi",
        "replace":"    export SHELL",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BEFORE_AFTER_REPLACE_LINE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["after"]
    params = {
        "regexp":"IEF456I",
        "after":"IEF479I SYSTEM RESOURCES DEALLOCATED",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["before"]
    params = {
        "regexp":"IEF479I",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_BEFORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["regexp"]
    params = {
        "regexp":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_REGEXP
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_before_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["after", "before"]
    params = {
        "regexp":"^IEF456I *",
        "after":"*CANCEL JOB56789",
        "before":"IEA999I SYSTEM IDLE - NO ACTIVE JOBS DETECTED",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_BEFORE_AFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_regexp_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["after", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "after":"   STEP3 - CPU TIME 5.4 SEC",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_regexp_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["before", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_before_after_regexp_literal(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    literal = ["after", "before", "regexp"]
    params = {
        "regexp":"*DEALLOC SYSRES",
        "before":"//*SMPTLIB  DD UNIT=SYSALLDA,SPACE=(TRK,(1,1)),VOL=SER=vvvvvv",
        "after":"*TRACE OFF",
        "literal":literal,
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_LITERAL_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_LITERAL_CONTENT_AFTER_REGEXP
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_remove_multiple_lines(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^export\s+(ZOAU_ROOT|_BPXK_AUTOCVT|PATH)*",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 3
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_MULTIPLE_LINES
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_backref(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"^(export\s+)(PATH|ZOAU_ROOT|_BPXK_AUTOCVT)*",
        "replace": r"\1NEW_\2",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 3
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_BACKREF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_match_replace_multiple_lines(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"(?s)^(if .*?\nthen\n.*?\n.*?\n.*?\n)",
        "replace":"""### REPLACED MULTILINE TEXT ###
export STEPLIB=custom
exec -a 0 /bin/bash
""",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_MATCH_MULTIPLE_LINES
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

# @pytest.mark.ds
# @pytest.mark.parametrize("dstype", DS_TYPE)
# def test_ds_backup_no_name(ansible_zos_module, dstype):
#     hosts = ansible_zos_module
#     ds_type = dstype
#     params = {
#         "regexp":"ZOAU_ROOT",
#         "after":"export PATH",
#         "backup":True,
#     }
#     ds_name = get_tmp_ds_name()
#     temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#     content = TEST_CONTENT
#     try:
#         ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#         params["target"] = ds_full_name
#         results = hosts.all.zos_replace(**params)
#         for result in results.contacted.values():
#             assert result.get("changed") == True
#             assert result.get("target") == ds_full_name
#             assert result.get("found") == 2
#             backup_name = result.get("backup_name")
#             assert result.get("backup_name") is not None
#         results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
#         for result in results.contacted.values():
#             assert result.get("stdout") == TEST_AFTER
#         results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup_name))
#         for result in results.contacted.values():
#             assert result.get("stdout") == TEST_CONTENT
#     finally:
#         remove_ds_environment(ansible_zos_module, ds_name)
#         remove_ds_environment(ansible_zos_module, backup_name)

@pytest.mark.ds
@pytest.mark.parametrize("backup_name", BACKUP_OPTIONS)
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_backup_name(ansible_zos_module, dstype, backup_name):
    hosts = ansible_zos_module
    ds_type = dstype
    if backup_name:
        if backup_name == "SEQ":
            ds_backup_file = get_tmp_ds_name()
        else:
            ds_backup_file = get_tmp_ds_name() + "(MEM)"
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
        "backup":True,
        "backup_name":ds_backup_file
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 2
            if ds_type != "seq":
                if backup_name == "SEQ":
                    assert result.get("backup_name") is not None
            else:
                assert result.get("backup_name") == ds_backup_file
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(ds_backup_file))
        for result in results.contacted.values():
            if ds_type == "seq":
                if backup_name == "MEM":
                    assert result.get("stdout") == ""
                else:
                    assert result.get("stdout") == TEST_CONTENT
            else:
                if backup_name == "SEQ":
                    assert result.get("stdout") == ""
                else:
                    assert result.get("stdout") == TEST_CONTENT
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)
        if "(" in ds_backup_file:
            position = ds_backup_file.find("(")
            ds_backup_file = ds_backup_file[:position]
        remove_ds_environment(ansible_zos_module, ds_backup_file)

@pytest.mark.ds
def test_gdg_ds(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export PATH",
    }
    ds_name = get_tmp_ds_name(3, 2)
    try:
        # Set environment
        temp_file = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.shell(cmd="dtouch -tGDG -L3 {0}".format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))
        hosts.all.shell(cmd=f"echo \"{TEST_CONTENT}\" > {temp_file}")
        ds_full_name = ds_name + "(0)"
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
        hosts.all.shell(cmd=cmd_str)
        ds_full_name = ds_name + "(-1)"
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
        hosts.all.shell(cmd=cmd_str)
        hosts.all.shell(cmd="rm -rf " + temp_file)

        params["target"] = ds_name + "(0)"
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_name + "(0)"
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER

        params["target"] = ds_name + "(-1)"
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_name + "(-1)"
            assert result.get("found") == 2
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER

        params_w_bck = {
            "regexp":"ZOAU_ROOT",
            "after":"export PATH",
            "backup":True,
            "backup_name": ds_name + "(+1)",
        }
        params_w_bck["target"] = ds_name + "(-1)"
        backup = ds_name + "(0)"
        results = hosts.all.zos_replace(**params_w_bck)
        for result in results.contacted.values():
            assert result.get("found") == 0
            assert result.get("changed") == False
            assert result.get("target") == ds_name + "(-1)"
            assert result.get("backup_name") is not None
        backup = ds_name + "(0)"
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_AFTER

        params["target"] = ds_name + "(-3)"
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("failed") == True
            assert result.get("changed") == False
    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)

#########################
# No UTF-8 Characters
#########################

def test_uss_after_no_utf_8_char(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"MOUNTPOINT",
        "after":"export PATH",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = SRC_INVALID_UTF8
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == full_path
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == SRC_INVALID_UTF8_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_after_no_utf_8_char(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"MOUNTPOINT",
        "after":"export PATH",
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = SRC_INVALID_UTF8
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["target"] = ds_full_name
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
            assert result.get("target") == ds_full_name
            assert result.get("found") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["target"]))
        for result in results.contacted.values():
            assert result.get("stdout") == SRC_INVALID_UTF8_REPLACE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

#########################
# Negative test cases
#########################

def test_do_not_match_pattern(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"This is not in the file",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("failed") == True
            assert result.get("changed") == False
            assert result.get("msg") == "Pattern for before/after params did not match the given file."
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_no_match_found(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT",
        "after":"export ZOAU_ROOT",
        "before":"PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin",
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("target") == full_path
            assert result.get("changed") == False
            assert result.get("found") == 0
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_bad_use_after_literalp(ansible_zos_module):
    hosts = ansible_zos_module
    literal = "after"
    params = {
        "regexp":"ZOAU_ROOT",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("failed") == True
            assert result.get("target") == full_path
            assert result.get("changed") == False
            assert result.get("msg") == "Use of literal requires the use of the after option too."
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

def test_bad_use_before_literalp(ansible_zos_module):
    hosts = ansible_zos_module
    literal = "before"
    params = {
        "regexp":"ZOAU_ROOT",
        "literal":literal,
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["target"] = full_path
        results = hosts.all.zos_replace(**params)
        for result in results.contacted.values():
            assert result.get("failed") == True
            assert result.get("target") == full_path
            assert result.get("changed") == False
            assert result.get("msg") == "Use of literal requires the use of the before option too."
    finally:
        remove_uss_environment(ansible_zos_module, full_path)
