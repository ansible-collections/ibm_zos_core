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
import time
import re
from shellescape import quote
import pytest
from ibm_zos_core.tests.helpers.dataset import (
    get_tmp_ds_name,
    get_random_q,
)
from ibm_zos_core.tests.helpers.utils import get_random_file_name

__metaclass__ = type


c_pgm="""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char** argv)
{
    char dsname[ strlen(argv[1]) + 4];
    sprintf(dsname, \\\"//'%s'\\\", argv[1]);
    FILE* member;
    member = fopen(dsname, \\\"rb,type=record\\\");
    sleep(300);
    fclose(member);
    return 0;
}
"""

call_c_jcl="""//PDSELOCK JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//LOCKMEM  EXEC PGM=BPXBATCH
//STDPARM DD *
SH {2}pdse-lock '{0}({1})'
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""

TEST_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

TEST_CONTENT_DEFAULTMARKER = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
# END ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

TEST_CONTENT_CUSTOMMARKER = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
# CLOSE IBM MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

TEST_CONTENT_DOUBLEQUOTES = """//BPXSLEEP JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//USSCMD EXEC PGM=BPXBATCH
//STDERR  DD SYSOUT=*
//STDOUT  DD SYSOUT=*
//STDPARM DD *
SH ls -la /;
sleep 30;
/*
//"""

EXPECTED_INSERTAFTER_REGEX = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# END ANSIBLE MANAGED BLOCK
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERTBEFORE_REGEX = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
# BEGIN ANSIBLE MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# END ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERTAFTER_EOF = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT
# BEGIN ANSIBLE MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK"""

EXPECTED_INSERTBEFORE_BOF = """# BEGIN ANSIBLE MANAGED BLOCK
# this is file is for setting env vars
# END ANSIBLE MANAGED BLOCK
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERTAFTER_REGEX_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# CLOSE IBM MANAGED BLOCK
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERTBEFORE_REGEX_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
# OPEN IBM MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# CLOSE IBM MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERTAFTER_EOF_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT
# OPEN IBM MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# CLOSE IBM MANAGED BLOCK"""

EXPECTED_INSERTBEFORE_BOF_CUSTOM = """# OPEN IBM MANAGED BLOCK
# this is file is for setting env vars
# CLOSE IBM MANAGED BLOCK
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_ABSENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_INSERT_WITH_INDENTATION = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT
# BEGIN ANSIBLE MANAGED BLOCK
                export ZOAU_ROOT
                export ZOAU_HOME
                export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK"""

EXPECTED_REPLACE_INSERTAFTER = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# END ANSIBLE MANAGED BLOCK
export ZOAU_ROOT"""

EXPECTED_REPLACE_INSERTBEFORE = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
# BEGIN ANSIBLE MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# END ANSIBLE MANAGED BLOCK
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_REPLACE_EOF_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT
# BEGIN ANSIBLE MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK"""

EXPECTED_REPLACE_BOF_CUSTOM = """# BEGIN ANSIBLE MANAGED BLOCK
# this is file is for setting env vars
# END ANSIBLE MANAGED BLOCK
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_REPLACE_EOF_REGEX_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# CLOSE IBM MANAGED BLOCK
export ZOAU_ROOT"""

EXPECTED_REPLACE_BOF_REGEX_CUSTOM = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
# OPEN IBM MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# CLOSE IBM MANAGED BLOCK
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
export ZOAU_ROOT"""

EXPECTED_DOUBLE_QUOTES = """//BPXSLEEP JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//USSCMD EXEC PGM=BPXBATCH
//STDERR  DD SYSOUT=*
//STDOUT  DD SYSOUT=*
//STDPARM DD *
SH ls -la /;
sleep 30;
// BEGIN ANSIBLE MANAGED BLOCK
cat "//OMVSADMI.CAT"
cat "//OMVSADM.COPYMEM.TESTS" > test.txt
// END ANSIBLE MANAGED BLOCK
/*
//"""

EXPECTED_ENCODING = """SIMPLE LINE TO VERIFY
# BEGIN ANSIBLE MANAGED BLOCK
Insert this string
# END ANSIBLE MANAGED BLOCK"""

"""
Note: zos_encode module uses USS cp command for copying
from USS file to MVS data set which only supports IBM-1047 charset.
I had to develop and use a new tool for converting and copying
to data set in order to set up environment for tests to publish results on Jira.
Until the issue be addressed I disable related tests.
"""
ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']

# supported data set types
DS_TYPE = ['seq', 'pds', 'pdse']

# not supported data set types
NS_DS_TYPE = ['esds', 'rrds', 'lds']

TMP_DIRECTORY = "/tmp/"

BACKUP_OPTIONS = [None, "SEQ", "MEM"]

expected_keys = [
    'changed',
    'cmd',
    'found',
    'stdout',
    'stdout_lines',
    'stderr',
    'stderr_lines',
    'rc'
]


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
    hosts.all.shell(cmd=f"dtouch -t{ds_type} '{ds_name}'")
    # hosts.all.zos_data_set(name=ds_name, type=ds_type)
    if ds_type in ["pds", "pdse"]:
        ds_full_name = ds_name + "(MEM)"
        hosts.all.shell(cmd=f"decho '' '{ds_full_name}'")
        # hosts.all.zos_data_set(name=ds_full_name, state="present", type="member")
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
    else:
        ds_full_name = ds_name
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
    hosts.all.shell(cmd=cmd_str)
    hosts.all.shell(cmd="rm -rf " + temp_file)
    return ds_full_name

def remove_ds_environment(ansible_zos_module, ds_name):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"drm '{ds_name}'")
    # hosts.all.zos_data_set(name=ds_name, state="absent")

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_block_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"ZOAU_ROOT=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)



@pytest.mark.uss
def test_uss_block_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = {
        "insertbefore":"ZOAU_ROOT=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_absent_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "block":"",
        "state":"absent"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_absent_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "block":"",
        "state":"absent"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"PYTHON_HOME=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"PYTHON_HOME=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"PYTHON_HOME=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_EOF_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"PYTHON_HOME=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_BOF_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insert_with_indentation_level_specified(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present",
        "indentation":16
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERT_WITH_INDENTATION
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

# Test case base on bug of dataset.blockifile
# GH Issue #1258
@pytest.mark.uss
def test_uss_block_insert_with_doublequotes(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="sleep 30;", block='cat "//OMVSADMI.CAT"\ncat "//OMVSADM.COPYMEM.TESTS" > test.txt', marker="// {mark} ANSIBLE MANAGED BLOCK", state="present")
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DOUBLEQUOTES
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_DOUBLE_QUOTES
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present",
        "backup":True
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            assert backup_name is not None
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        ansible_zos_module.all.file(path=backup_name, state="absent")
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup_name(ansible_zos_module):
    hosts = ansible_zos_module
    uss_backup_file = get_random_file_name(dir=TMP_DIRECTORY, suffix=".tmp")
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present",
        "backup":True,
        "backup_name":uss_backup_file
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            assert result.get("backup_name") == uss_backup_file
        cmd_str = f"cat {uss_backup_file}"
        results = ansible_zos_module.all.shell(cmd=cmd_str)
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        ansible_zos_module.all.file(path=uss_backup_file, state="absent")
        remove_uss_environment(ansible_zos_module, full_path)


#########################
# Dataset test cases
#########################


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertbefore_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"ZOAU_ROOT=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_eof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertbefore_bof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"PYTHON_HOME=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertbefore_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"PYTHON_HOME=",
        "block":"unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertafter_eof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertbefore_bof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"BOF",
        "block":"# this is file is for setting env vars",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "block":"",
        "state":"absent"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
def test_ds_tmp_hlq_option(ansible_zos_module):
    # This TMPHLQ only works with sequential datasets
    hosts = ansible_zos_module
    ds_type = "seq"
    hlq = get_random_q()
    params={
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\n",
        "state":"present",
        "backup":True,
        "tmp_hlq": hlq
    }
    kwargs = {
        "backup_name":"{0}".format(hlq)
    }
    content = TEST_CONTENT
    try:
        ds_full_name = get_tmp_ds_name()
        temp_file = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.shell(cmd=f"dtouch -t{ds_type} '{ds_full_name}'")
        # hosts.all.zos_data_set(name=ds_full_name, type=ds_type, replace=True)
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
        hosts.all.shell(cmd=cmd_str)
        hosts.all.shell(cmd="rm " + ds_full_name)
        results = hosts.all.shell(cmd=f"cat \"//'{ds_full_name}'\" | wc -l ")
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            for key in kwargs:
                assert kwargs.get(key) in result.get(key)
    finally:
        hosts.all.shell(cmd=f"drm '{ds_full_name}'")
        # hosts.all.zos_data_set(name=ds_full_name, state="absent")
        hosts.all.file(name=temp_file, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insert_with_indentation_level_specified(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present",
        "indentation":16
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERT_WITH_INDENTATION
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("backup_name", BACKUP_OPTIONS)
def test_ds_block_insertafter_eof_with_backup(ansible_zos_module, dstype, backup_name):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present",
        "backup":True
    }
    if backup_name:
        if backup_name == "SEQ":
            params["backup_name"] = get_tmp_ds_name()
        else:
            params["backup_name"] = get_tmp_ds_name() + "(MEM)"
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            backup_ds_name = result.get("backup_name")
            assert backup_ds_name is not None
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
        backup_ds_name = backup_ds_name.replace('$','\$')
        bk_results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup_ds_name))
        if backup_name == "MEM" and dstype == "seq":
            for result in bk_results.contacted.values():
                assert result.get("stdout") == ""
        else:
            for result in bk_results.contacted.values():
                assert result.get("stdout") == TEST_CONTENT
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)
        if backup_ds_name != "":
            hosts.all.shell(cmd=f"drm '{backup_ds_name}'")
            # ansible_zos_module.all.zos_data_set(name=backup_ds_name, state="absent")



@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name =  get_tmp_ds_name()
    params = {
        "path":"",
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present",
        "force":True
    }
    member_1, member_2 = "MEM1", "MEM2"
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    if ds_type == "seq":
        params["path"] = f"{default_data_set_name}.{member_2}"
    else:
        params["path"] = f"{default_data_set_name}({member_2})"
    try:
        hosts.all.shell(cmd=f"dtouch -t{ds_type} '{default_data_set_name}'")
        # set up:
        # hosts.all.zos_data_set(
        #     name=default_data_set_name,
        #     state="present",
        #     type=ds_type,
        #     replace=True
        # )
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        # Create two empty members
        hosts.all.shell(cmd=f"decho '' '{default_data_set_name}({member_1})'")
        hosts.all.shell(cmd=f"decho '' '{params['path']}'")
        # hosts.all.zos_data_set(
        #     batch=[
        #         {
        #             "name": f"{default_data_set_name}({member_1})",
        #             "type": "member",
        #             "state": "present", "replace": True, },
        #         {   "name": params["path"], "type": "member",
        #             "state": "present", "replace": True, },
        #     ]
        # )
        # write memeber to verify cases
        if ds_type in ["pds", "pdse"]:
            cmd_str = "cp -CM {0} \"//'{1}'\"".format(quote(temp_file), params["path"])
        else:
            cmd_str = "cp {0} \"//'{1}'\" ".format(quote(temp_file), params["path"])
        hosts.all.shell(cmd=cmd_str)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(params["path"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        path = get_random_file_name(suffix="/", dir=TMP_DIRECTORY)
        hosts.all.file(path=path, state="directory")
        hosts.all.shell(cmd=f"echo \"{c_pgm}\"  > {path}pdse-lock.c")
        hosts.all.shell(
            cmd=f"echo \"{call_c_jcl.format(default_data_set_name, member_1, path)}\""+
            " > {0}call_c_pgm.jcl".format(path)
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=path)
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=path)
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
        results = hosts.all.shell(cmd=f"""cat "//'{params["path"]}'" """)
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        hosts.all.shell(cmd="rm -rf " + temp_file)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(path))
        hosts.all.shell(cmd=f"drm '{default_data_set_name}'")
        # hosts.all.zos_data_set(name=default_data_set_name, state="absent")


@pytest.mark.ds
def test_gdd_ds_insert_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name(3, 2)
    try:
        # Set environment
        hosts.all.shell(cmd="dtouch -tGDG -L3 {0}".format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))

        params["src"] = ds_name + "(0)"
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["src"]))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

        params["src"] = ds_name + "(-1)"
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["src"]))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

        params_w_bck = dict(insertafter="eof", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True, backup_name=ds_name + "(+1)")
        params_w_bck["src"] = ds_name + "(-1)"
        results = hosts.all.zos_blockinfile(**params_w_bck)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            assert result.get("rc") == 0
        backup = ds_name + "(0)"
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

        params["src"] = ds_name + "(-3)"
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 0
    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)


@pytest.mark.ds
def test_special_characters_ds_insert_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="eof", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name(5, 5, symbols=True)
    backup = get_tmp_ds_name(6, 6, symbols=True)
    try:
        hosts.all.shell(cmd=f"dtouch -tseq '{ds_name}'")
        # result = hosts.all.zos_data_set(name=ds_name, type="seq", state="present")

        params["src"] = ds_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        src = ds_name.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(src))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

        params_w_bck = dict(insertafter="eof", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True, backup_name=backup)
        params_w_bck["src"] = ds_name
        results = hosts.all.zos_blockinfile(**params_w_bck)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            assert result.get("rc") == 0
        backup = backup.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)


#########################
# Encoding tests
#########################
@pytest.mark.uss
@pytest.mark.parametrize("encoding", ENCODING)
def test_uss_encoding(ansible_zos_module, encoding):
    hosts = ansible_zos_module
    insert_data = "Insert this string"
    params = {
        "insertafter":"SIMPLE",
        "block":insert_data,
        "state":"present"
    }
    params["encoding"] = encoding
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.file(path=full_path, state="touch")
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, full_path))
        hosts.all.zos_encode(src=full_path, dest=full_path, from_encoding="IBM-1047", to_encoding=params["encoding"])
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_uss_environment(ansible_zos_module, full_path)



@pytest.mark.ds
def test_special_characters_ds_insert_block(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="eof", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name(5, 5, symbols=True)
    backup = get_tmp_ds_name(6, 6, symbols=True)
    try:
        hosts.all.shell(cmd=f"dtouch -tseq '{ds_name}'")
        # result = hosts.all.zos_data_set(name=ds_name, type="seq", state="present")

        params["src"] = ds_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        src = ds_name.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(src))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

        params_w_bck = dict(insertafter="eof", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True, backup_name=backup)
        params_w_bck["src"] = ds_name
        results = hosts.all.zos_blockinfile(**params_w_bck)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
            assert result.get("rc") == 0
        backup = backup.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == "# BEGIN ANSIBLE MANAGED BLOCK\nZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=$ZOAU_ROOT\nZOAU_DIR=$ZOAU_ROOT\n# END ANSIBLE MANAGED BLOCK"

    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """)


#########################
# Negative tests
#########################


@pytest.mark.ds
def test_not_exist_ds_block_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    params["path"] = "BIFTEST.NOTEXIST.SEQ"
    results = hosts.all.zos_blockinfile(**params)
    for result in results.contacted.values():
        assert "does NOT exist" in result.get("msg")


@pytest.mark.ds
def test_ds_block_insertafter_nomatch_eof_insert(ansible_zos_module):
    hosts = ansible_zos_module
    ds_type = 'seq'
    params={
        "insertafter":"EOF",
        "block":"export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR",
        "state":"present"
    }
    params["insertafter"] = 'SOME_NON_EXISTING_PATTERN'
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert all(key in result for key in expected_keys)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
def test_ds_block_insertafter_regex_wrongmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    params["path"] = "BIFTEST.NOTEXIST.SEQ"
    params["marker"] = '# MANAGED BLOCK'
    results = hosts.all.zos_blockinfile(**params)
    for result in results.contacted.values():
        assert "marker should have {mark}" in result.get("msg")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    try:
        ds_name = ds_name.upper() + "." + ds_type
        hosts.all.shell(cmd=f"dtouch -t{ds_type} '{ds_name}'")
        # results = hosts.all.zos_data_set(name=ds_name, type=ds_type, replace='yes')
        for result in results.contacted.values():
            assert result.get("changed") is True
        params["path"] = ds_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("msg") == "VSAM data set type is NOT supported"
    finally:
        hosts.all.shell(cmd=f"drm '{ds_name}'")
        # hosts.all.zos_data_set(name=ds_name, state="absent")


# Enhancemed #1339
@pytest.mark.ds
@pytest.mark.parametrize("dstype", ["pds","pdse"])
def test_ds_block_insertafter_regex_fail(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name = get_tmp_ds_name()
    params = {
        "path":"",
        "insertafter":"ZOAU_ROOT=",
        "block":"ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        "state":"present",
        "force":False
    }
    member_1, member_2 = "MEM1", "MEM2"
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    params["path"] = f"{default_data_set_name}({member_2})"
    content = TEST_CONTENT
    try:
        hosts.all.shell(cmd=f"dtouch -t{ds_type} '{default_data_set_name}'")
        # set up:
        # hosts.all.zos_data_set(
        #     name=default_data_set_name,
        #     state="present",
        #     type=ds_type,
        #     replace=True
        # )
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        # Create two empty members
        hosts.all.shell(cmd=f"decho '' '{default_data_set_name}({member_1})'")
        hosts.all.shell(cmd=f"decho '' '{params['path']}'")
        # hosts.all.zos_data_set(
        #     batch=[
        #         {
        #             "name": f"{default_data_set_name}({member_1})",
        #             "type": "member",
        #             "state": "present",
        #             "replace": True,
        #         },
        #         {
        #             "name": params["path"],
        #             "type": "member",
        #             "state": "present",
        #             "replace": True,
        #         },
        #     ]
        # )
        cmd_str = "cp -CM {0} \"//'{1}'\"".format(quote(temp_file) ,params["path"])
        hosts.all.shell(cmd=cmd_str)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(params["path"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        path = get_random_file_name(suffix="/", dir=TMP_DIRECTORY)
        hosts.all.file(path=path, state="directory")
        hosts.all.shell(cmd=f"echo \"{c_pgm}\"  > {path}pdse-lock.c")
        hosts.all.shell(
            cmd=f"echo \"{call_c_jcl.format(default_data_set_name, member_1, path)}\""+
            " > {0}call_c_pgm.jcl".format(path)
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=path)
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=path)
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed") is True
    finally:
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(path))
        hosts.all.shell(cmd=f"drm '{default_data_set_name}'")
        # hosts.all.zos_data_set(name=default_data_set_name, state="absent")
