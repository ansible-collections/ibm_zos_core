# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020, 2022, 2023
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
from shellescape import quote
import time
import re
import pytest

__metaclass__ = type

DEFAULT_DATA_SET_NAME = "USER.PRIVATE.TESTDS"

c_pgm="""#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc, char** argv)
{
    char dsname[ strlen(argv[1]) + 4];
    sprintf(dsname, "//'%s'", argv[1]);
    FILE* member;
    member = fopen(dsname, "rb,type=record");
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

# supported data set types
DS_TYPE = ['SEQ', 'PDS', 'PDSE']

# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
"""
Note: zos_encode module uses USS cp command for copying from USS file to MVS data set which only supports IBM-1047 charset.
I had to develop and use a new tool for converting and copying to data set in order to set up environment for tests to publish results on Jira.
Until the issue be addressed I disable related tests.
"""
USS_BACKUP_FILE = "/tmp/backup.tmp"
BACKUP_OPTIONS = [None, "BLOCKIF.TEST.BACKUP", "BLOCKIF.TEST.BACKUP(BACKUP)"]
TEST_ENV = dict(
    TEST_CONT=TEST_CONTENT,
    TEST_DIR="/tmp/zos_blockinfile/",
    TEST_FILE="",
    DS_NAME="",
    DS_TYPE="",
    ENCODING="IBM-1047",
)

def set_uss_enviroment(ansible_zos_module, test_name, test_env):
    hosts = ansible_zos_module
    test_env["TEST_FILE"] = test_env["TEST_DIR"] + test_name
    hosts.all.shell(cmd="mkdir -p {0}".format(test_env["TEST_DIR"]))
    hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], test_env["TEST_FILE"]))

def remove_uss_enviroment(ansible_zos_module, test_env):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="rm -rf " + test_env["TEST_DIR"])

def set_ds_enviroment(ansible_zos_module,test_name, test_env):
    hosts = ansible_zos_module
    TEMP_FILE = "/tmp/{0}".format(test_name)
    test_env["DS_NAME"] = test_name.upper() + "." + test_env["DS_TYPE"]
    hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], TEMP_FILE))
    hosts.all.zos_data_set(name=test_env["DS_NAME"], type=test_env["DS_TYPE"])
    if test_env["DS_TYPE"] in ["PDS", "PDSE"]:
        test_env["DS_NAME"] = test_env["DS_NAME"] + "(MEM)"
        hosts.all.zos_data_set(name=test_env["DS_NAME"], state="present", type="member")
        cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), test_env["DS_NAME"])
    else:
        cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), test_env["DS_NAME"])
    hosts.all.shell(cmd=cmdStr)
    hosts.all.shell(cmd="rm -rf " + TEMP_FILE)

def remove_ds_enviroment(ansible_zos_module, test_env):
    hosts = ansible_zos_module
    ds_name = test_env["DS_NAME"]
    hosts.all.zos_data_set(name=ds_name, state="absent")

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_block_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_regex_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertbefore_regex_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_eof_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertbefore_bof_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# BEGIN ANSIBLE MANAGED BLOCK
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_regex_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)



@pytest.mark.uss
def test_uss_block_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertbefore_regex_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_eof_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    # Set special parameters for the test as marker
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertbefore_bof_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# OPEN IBM MANAGED BLOCK
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_absent_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(block="", state="absent")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_absent_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_absent_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    params = dict(block="", state="absent")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_absent_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertafter_regex_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertbefore_regex_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertafter_eof_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_defaultmarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertbefore_bof_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# BEGIN ANSIBLE MANAGED BLOCK
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertafter_regex_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertbefore_regex_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertafter_eof_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_custommarker(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    params["marker"] = '# {mark} IBM MANAGED BLOCK'
    params["marker_begin"] = 'OPEN'
    params["marker_end"] = 'CLOSE'
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_replace_insertbefore_bof_custommarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# OPEN IBM MANAGED BLOCK
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_insert_with_indentation_level_specified(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", indentation=16)
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insert_with_indentation_level_specified", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insert_with_doublequotes(ansible_zos_module):
    hosts = ansible_zos_module
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DOUBLEQUOTES
    params = dict(insertafter="sleep 30;", block='cat \"//OMVSADMI.CAT\"\ncat \"//OMVSADM.COPYMEM.TESTS\" > test.txt', marker="// {mark} ANSIBLE MANAGED BLOCK", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_regex_defaultmarker", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """//BPXSLEEP JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
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
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True)
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_eof_with_backup", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            backup_name = result.get("backup_name")
            assert result.get("changed") == 1
            assert backup_name is not None
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        ansible_zos_module.all.file(path=backup_name, state="absent")
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_block_insertafter_eof_with_backup_name(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True, backup_name=USS_BACKUP_FILE)
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_block_insertafter_eof_with_backup_name", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert result.get("backup_name") == USS_BACKUP_FILE
        cmdStr = "cat {0}".format(USS_BACKUP_FILE)
        results = ansible_zos_module.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_ENV["TEST_CONT"]
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        ansible_zos_module.all.file(path=USS_BACKUP_FILE, state="absent")
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


#########################
# Dataset test cases
#########################


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST1", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertbefore_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST2", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_eof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST3", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertbefore_bof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST4", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# BEGIN ANSIBLE MANAGED BLOCK
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST5", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertbefore_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST6", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertafter_eof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST7", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_replace_insertbefore_bof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(insertbefore="BOF", block="# this is file is for setting env vars", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST8", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# BEGIN ANSIBLE MANAGED BLOCK
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    params = dict(block="", state="absent")
    try:
        set_ds_enviroment(ansible_zos_module, "DST9", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
def test_ds_tmp_hlq_option(ansible_zos_module):
    # This TMPHLQ only works with sequential datasets
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = "SEQ"
    params=dict(insertafter="EOF", block="export ZOAU_ROOT\n", state="present", backup=True, tmp_hlq="TMPHLQ")
    kwargs = dict(backup_name=r"TMPHLQ\..")
    test_name = "DST10"
    TEMP_FILE = "/tmp/" + test_name
    TEMP_FILE = TEST_ENV["TEST_DIR"] + test_name
    try:
        hosts.all.shell(cmd="mkdir -p {0}".format(TEST_ENV["TEST_DIR"]))
        results = hosts.all.shell(cmd='hlq')
        for result in results.contacted.values():
            hlq = result.get("stdout")
        if len(hlq) > 8:
            hlq = hlq[:8]
        TEST_ENV["DS_NAME"] = hlq + "." + test_name.upper() + "." + TEST_ENV["DS_TYPE"]
        hosts.all.zos_data_set(name=TEST_ENV["DS_NAME"], type=TEST_ENV["DS_TYPE"], replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(TEST_ENV["TEST_CONT"], TEMP_FILE))
        cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), TEST_ENV["DS_NAME"])
        hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + TEST_ENV["TEST_DIR"])
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            for key in kwargs:
                assert re.match(kwargs.get(key), result.get(key))
    finally:
        ds_name = TEST_ENV["DS_NAME"]
        hosts.all.zos_data_set(name=ds_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insert_with_indentation_level_specified(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", indentation=16)
    try:
        set_ds_enviroment(ansible_zos_module, "DST11", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("backup_name", BACKUP_OPTIONS)
def test_ds_block_insertafter_eof_with_backup(ansible_zos_module, dstype, backup_name):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", backup=True)
    if backup_name:
        params["backup_name"] = backup_name
    try:
        set_ds_enviroment(ansible_zos_module, "DST12", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            if backup_name:
                backup_ds_name = result.get("backup_name")
                assert backup_ds_name is not None
            else:
                backup_ds_name = result.get("backup_name")
                assert backup_ds_name is not None
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)
        if backup_name:
            ansible_zos_module.all.zos_data_set(name="BLOCKIF.TEST.BACKUP", state="absent")
            ansible_zos_module.all.zos_data_set(name=backup_ds_name, state="absent")
        else:
            ansible_zos_module.all.zos_data_set(name=backup_ds_name, state="absent")



@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_block_insertafter_regex_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(path="",insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present", force=True)
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    if TEST_ENV["DS_TYPE"] == "SEQ":
        TEST_ENV["DS_NAME"] = DEFAULT_DATA_SET_NAME+".{0}".format(MEMBER_2)
        params["path"] = DEFAULT_DATA_SET_NAME+".{0}".format(MEMBER_2)
    else:
        TEST_ENV["DS_NAME"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
        params["path"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
    try:
        # set up:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=TEST_ENV["DS_TYPE"], replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(TEST_ENV["TEST_CONT"], TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
                    "type": "member", "state": "present", "replace": True, },
                {   "name": TEST_ENV["DS_NAME"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
        # write memeber to verify cases
        if TEST_ENV["DS_TYPE"] in ["PDS", "PDSE"]:
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), TEST_ENV["DS_NAME"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), TEST_ENV["DS_NAME"])
        hosts.all.shell(cmd=cmdStr)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.zos_copy(content=c_pgm, dest='/tmp/disp_shr/pdse-lock.c', force=True)
        hosts.all.zos_copy(
            content=call_c_jcl.format(DEFAULT_DATA_SET_NAME, MEMBER_1),
            dest='/tmp/disp_shr/call_c_pgm.jcl',
            force=True
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
        results = hosts.all.shell(cmd=r"""cat "//'{0}'" """.format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


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
    TEST_ENV["DS_TYPE"] = 'SEQ'
    TEST_ENV["ENCODING"] = 'IBM-1047'
    params=dict(insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present")
    params["insertafter"] = 'SOME_NON_EXISTING_PATTERN'
    try:
        set_ds_enviroment(ansible_zos_module, "DST13", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
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
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


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
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present")
    test_name = "DST14"
    try:
        results = hosts.all.shell(cmd='hlq')
        for result in results.contacted.values():
            hlq = result.get("stdout")
        assert len(hlq) <= 8 or hlq != ''
        TEST_ENV["DS_NAME"] = test_name.upper() + "." + TEST_ENV["DS_TYPE"]
        results = hosts.all.zos_data_set(name=TEST_ENV["DS_NAME"], type=TEST_ENV["DS_TYPE"], replace='yes')
        for result in results.contacted.values():
            assert result.get("changed") is True
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_blockinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("msg") == "VSAM data set type is NOT supported"
    finally:
        ds_name = TEST_ENV["DS_NAME"]
        hosts.all.zos_data_set(name=ds_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ["PDS","PDSE"])
def test_ds_block_insertafter_regex_fail(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(path="", insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT", state="present", force=False)
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    TEST_ENV["DS_NAME"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
    params["path"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
    try:
        # set up:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=TEST_ENV["DS_TYPE"], replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(TEST_ENV["TEST_CONT"], TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
                    "type": "member", "state": "present", "replace": True, },
                {   "name": TEST_ENV["DS_NAME"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
        cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), TEST_ENV["DS_NAME"])
        hosts.all.shell(cmd=cmdStr)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.zos_copy(content=c_pgm, dest='/tmp/disp_shr/pdse-lock.c', force=True)
        hosts.all.zos_copy(
            content=call_c_jcl.format(DEFAULT_DATA_SET_NAME, MEMBER_1),
            dest='/tmp/disp_shr/call_c_pgm.jcl',
            force=True
        )
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
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")