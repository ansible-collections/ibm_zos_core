# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2024
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
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from shellescape import quote
import time
import re
import pytest
import inspect
import os

__metaclass__ = type

TEST_FOLDER_BLOCKINFILE = "/tmp/ansible-core-tests/zos_blockinfile/"

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
SH /tmp/disp_shr/pdse-lock '{0}({1})'
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
Note: zos_encode module uses USS cp command for copying from USS file to MVS data set which only supports IBM-1047 charset.
I had to develop and use a new tool for converting and copying to data set in order to set up environment for tests to publish results on Jira.
Until the issue be addressed I disable related tests.
"""
ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']

# supported data set types
DS_TYPE = ['SEQ', 'PDS', 'PDSE']

# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']

USS_BACKUP_FILE = "/tmp/backup.tmp"
BACKUP_OPTIONS = [None, "BLOCKIF.TEST.BACKUP", "BLOCKIF.TEST.BACKUP(BACKUP)"]

def set_uss_environment(ansible_zos_module, CONTENT, FILE):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="mkdir -p {0}".format(TEST_FOLDER_BLOCKINFILE))
    hosts.all.file(path=FILE, state="touch")
    hosts.all.shell(cmd="echo \"{0}\" > {1}".format(CONTENT, FILE))

def remove_uss_environment(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="rm -rf" + TEST_FOLDER_BLOCKINFILE)

def set_ds_environment(ansible_zos_module, TEMP_FILE, DS_NAME, DS_TYPE, CONTENT):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="echo \"{0}\" > {1}".format(CONTENT, TEMP_FILE))
    hosts.all.zos_data_set(name=DS_NAME, type=DS_TYPE)
    if DS_TYPE in ["PDS", "PDSE"]:
        DS_FULL_NAME = DS_NAME + "(MEM)"
        hosts.all.zos_data_set(name=DS_FULL_NAME, state="present", type="member")
        cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), DS_FULL_NAME)
    else:
        DS_FULL_NAME = DS_NAME
        cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), DS_FULL_NAME)
    hosts.all.shell(cmd=cmdStr)
    hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
    return DS_FULL_NAME

def remove_ds_environment(ansible_zos_module, DS_NAME):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=DS_NAME, state="absent")

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_block_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)



@pytest.mark.uss
def test_uss_block_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_absent_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(block="", state="absent")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_absent_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(block="", state="absent")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_EOF_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_BOF_REGEX_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_CUSTOMMARKER
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF_CUSTOM
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insert_with_indentation_level_specified(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", indentation=16)
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERT_WITH_INDENTATION
    finally:
        remove_uss_environment(ansible_zos_module)

# Test case base on bug of dataset.blockifile
# GH Issue #1258
@pytest.mark.uss
def test_uss_block_insert_with_doublequotes(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="sleep 30;", block='cat "//OMVSADMI.CAT"\ncat "//OMVSADM.COPYMEM.TESTS" > test.txt', marker="// {mark} ANSIBLE MANAGED BLOCK", state="present")
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT_DOUBLEQUOTES
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_DOUBLE_QUOTES
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True)
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
            assert result.get("changed") == 1
            assert backup_name is not None
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        ansible_zos_module.all.file(path=backup_name, state="absent")
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup_name(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True, backup_name=USS_BACKUP_FILE)
    full_path = TEST_FOLDER_BLOCKINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert result.get("backup_name") == USS_BACKUP_FILE
        cmdStr = "cat {0}".format(USS_BACKUP_FILE)
        results = ansible_zos_module.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        ansible_zos_module.all.file(path=USS_BACKUP_FILE, state="absent")
        remove_uss_environment(ansible_zos_module)


#########################
# Dataset test cases
#########################


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    params = dict(block="", state="absent")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT_DEFAULTMARKER
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
def test_ds_tmp_hlq_option(ansible_zos_module):
    # This TMPHLQ only works with sequential datasets
    hosts = ansible_zos_module
    ds_type = "SEQ"
    params=dict(insertafter="EOF", block="export ZOAU_ROOT\n", state="present", backup=True, tmp_hlq="TMPHLQ")
    kwargs = dict(backup_name=r"TMPHLQ\..")
    content = TEST_CONTENT
    try:
        ds_full_name = get_tmp_ds_name()
        temp_file = "/tmp/" + ds_full_name
        hosts.all.zos_data_set(name=ds_full_name, type=ds_type, replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, temp_file))
        cmdStr = "cp {0} \"//'{1}'\" ".format(quote(temp_file), ds_full_name)
        hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + "/tmp/zos_lineinfile/")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(ds_full_name))
        for result in results.contacted.values():
            print(result)
            assert int(result.get("stdout")) != 0
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            for key in kwargs:
                assert re.match(kwargs.get(key), result.get(key))
    finally:
        hosts.all.zos_data_set(name=ds_full_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insert_with_indentation_level_specified(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", indentation=16)
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
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
    backup_ds_name = ""
    params = dict(block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True)
    if backup_name:
        params["backup_name"] = backup_name
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            backup_ds_name = result.get("backup_name")
            assert backup_ds_name is not None
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)
        if backup_name:
            ansible_zos_module.all.zos_data_set(name="BLOCKIF.TEST.BACKUP", state="absent")
        if backup_ds_name != "":
            ansible_zos_module.all.zos_data_set(name=backup_ds_name, state="absent")



@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name =  get_tmp_ds_name()
    params = dict(path="",insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present", force=True)
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    content = TEST_CONTENT
    if ds_type == "SEQ":
        params["path"] = default_data_set_name+".{0}".format(MEMBER_2)
    else:
        params["path"] = default_data_set_name+"({0})".format(MEMBER_2)
    try:
        # set up:
        hosts.all.zos_data_set(name=default_data_set_name, state="present", type=ds_type, replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": default_data_set_name + "({0})".format(MEMBER_1),
                    "type": "member", "state": "present", "replace": True, },
                {   "name": params["path"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
        # write memeber to verify cases
        if ds_type in ["PDS", "PDSE"]:
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), params["path"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), params["path"])
        hosts.all.shell(cmd=cmdStr)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(params["path"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.file(path="/tmp/disp_shr/", state="directory")
        hosts.all.shell(cmd="echo \"{0}\"  > {1}".format(c_pgm, '/tmp/disp_shr/pdse-lock.c'))
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(
            call_c_jcl.format(default_data_set_name, MEMBER_1),
            '/tmp/disp_shr/call_c_pgm.jcl'))
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
        results = hosts.all.shell(cmd=r"""cat "//'{0}'" """.format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")

#########################
# Encoding tests
#########################
@pytest.mark.uss
@pytest.mark.parametrize("encoding", ENCODING)
def test_uss_encoding(ansible_zos_module, encoding):
    hosts = ansible_zos_module
    insert_data = "Insert this string"
    params = dict(insertafter="SIMPLE", block=insert_data, state="present")
    params["encoding"] = encoding
    full_path = TEST_FOLDER_BLOCKINFILE + encoding
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.shell(cmd="mkdir -p {0}".format(TEST_FOLDER_BLOCKINFILE))
        hosts.all.file(path=full_path, state="touch")
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, full_path))
        hosts.all.zos_encode(src=full_path, dest=full_path, from_encoding="IBM-1047", to_encoding=params["encoding"])
        params["path"] = full_path
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ["IBM-1047"])
def test_ds_encoding(ansible_zos_module, encoding, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    insert_data = "Insert this string"
    params = dict(insertafter="SIMPLE", block=insert_data, state="present")
    params["encoding"] = encoding
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, temp_file))
        hosts.all.zos_encode(src=temp_file, dest=temp_file, from_encoding="IBM-1047", to_encoding=params["encoding"])
        hosts.all.zos_data_set(name=ds_name, type=ds_type)
        if ds_type in ["PDS", "PDSE"]:
            ds_full_name = ds_name + "(MEM)"
            hosts.all.zos_data_set(name=ds_full_name, state="present", type="member")
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(temp_file), ds_full_name)
        else:
            ds_full_name = ds_name
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(temp_file), ds_full_name)
        hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + temp_file)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        hosts.all.zos_encode(src=ds_full_name, dest=ds_full_name, from_encoding=params["encoding"], to_encoding="IBM-1047")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


#########################
# Negative tests
#########################


@pytest.mark.ds
def test_not_exist_ds_block_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    params["path"] = "BIFTEST.NOTEXIST.SEQ"
    results = hosts.all.zos_blockinfile(**params)
    for result in results.contacted.values():
        assert "does NOT exist" in result.get("msg")


@pytest.mark.ds
def test_ds_block_insertafter_nomatch_eof_insert(ansible_zos_module):
    hosts = ansible_zos_module
    ds_type = 'SEQ'
    params=dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["insertafter"] = 'SOME_NON_EXISTING_PATTERN'
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
def test_ds_block_insertafter_regex_wrongmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
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
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    try:
        ds_name = ds_name.upper() + "." + ds_type
        results = hosts.all.zos_data_set(name=ds_name, type=ds_type, replace='yes')
        for result in results.contacted.values():
            assert result.get("changed") is True
        params["path"] = ds_name
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("msg") == "VSAM data set type is NOT supported"
    finally:
        hosts.all.zos_data_set(name=ds_name, state="absent")


# Enhancemed #1339
@pytest.mark.ds
@pytest.mark.parametrize("dstype", ["PDS","PDSE"])
def test_ds_block_insertafter_regex_fail(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name = get_tmp_ds_name()
    params = dict(path="", insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present", force=False)
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    params["path"] = default_data_set_name+"({0})".format(MEMBER_2)
    content = TEST_CONTENT
    try:
        # set up:
        hosts.all.zos_data_set(name=default_data_set_name, state="present", type=ds_type, replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": default_data_set_name + "({0})".format(MEMBER_1),
                    "type": "member", "state": "present", "replace": True, },
                {   "name": params["path"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
        cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), params["path"])
        hosts.all.shell(cmd=cmdStr)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(params["path"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.file(path="/tmp/disp_shr/", state="directory")
        hosts.all.shell(cmd="echo \"{0}\"  > {1}".format(c_pgm, '/tmp/disp_shr/pdse-lock.c'))
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(
            call_c_jcl.format(default_data_set_name, MEMBER_1),
        '/tmp/disp_shr/call_c_pgm.jcl'))
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == False
            assert result.get("failed") == True
    finally:
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")
