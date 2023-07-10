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

# supported data set types
DS_TYPE = ['SEQ', 'PDS', 'PDSE']
# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
# The encoding will be only use on a few test
ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']


TEST_ENV = dict(
    TEST_CONT="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT""",
    TEST_DIR="/tmp/zos_lineinfile/",
    TEST_FILE="",
    DS_NAME="",
    DS_TYPE="",
    ENCODING="IBM-1047",
)


#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_line_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_insertafter_regex", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_insertbefore_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_insertbefore_regex", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_insertafter_eof(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_insertafter_eof", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
export ZOAU_ROOT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_insertbefore_bof(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_insertbefore_bof", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# this is file is for setting env vars
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertafter="PATH=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_match_insertafter_ignore", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_match_insertbefore_ignore", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_nomatch_insertafter_match", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_nomatch_insertbefore_match", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertafter="xyzijk", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_nomatch_insertafter_nomatch", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
ZOAU_ROOT=/mvsutil-develop_dsed"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_nomatch_insertbefore_nomatch", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
unset ZOAU_ROOT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_absent(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", line="", state="absent")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_absent", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_quoted_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", regexp="ZOAU_ROOT=", line='ZOAU_ROOT=\"/mvsutil-develop_dsed\"', state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_quoted_escaped", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT="/mvsutil-develop_dsed"
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.uss
def test_uss_line_replace_quoted_not_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", regexp="ZOAU_ROOT=", line='ZOAU_ROOT="/mvsutil-develop_dsed"', state="present")
    try:
        set_uss_enviroment(ansible_zos_module, "test_uss_line_replace_quoted_not_escaped", TEST_ENV)
        params["path"] = TEST_ENV["TEST_FILE"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT="/mvsutil-develop_dsed"
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_uss_enviroment(ansible_zos_module, TEST_ENV)


#########################
# Dataset test cases
#########################

# Now force is parameter to change witch function to call in the helper and alter the declaration by add the force or a test name required.
# without change the original description or the other option is that at the end of the test get back to original one.
@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST1", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST2", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_eof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST3", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
export ZOAU_ROOT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_bof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST4", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """# this is file is for setting env vars
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertafter="PATH=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST5", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST6", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST7", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST8", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(regexp="abcxyz", insertafter="xyzijk", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST9", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
ZOAU_ROOT=/mvsutil-develop_dsed"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present")
    try:
        set_ds_enviroment(ansible_zos_module, "DST10", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
unset ZOAU_ROOT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(regexp="ZOAU_ROOT=", line="", state="absent")
    try:
        set_ds_enviroment(ansible_zos_module, "DST11", TEST_ENV)
        params["path"] = TEST_ENV["DS_NAME"]
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(TEST_ENV["DS_NAME"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        remove_ds_enviroment(ansible_zos_module, TEST_ENV)


@pytest.mark.ds
def test_ds_tmp_hlq_option(ansible_zos_module):
    # This TMPHLQ only works with sequential datasets
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = 'SEQ'
    kwargs = dict(backup_name=r"TMPHLQ\..")
    params = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present", backup=True, tmp_hlq="TMPHLQ")
    test_name = "DST12"
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
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            for key in kwargs:
                assert re.match(kwargs.get(key), result.get(key))
    finally:
        ds_name = TEST_ENV["DS_NAME"]
        hosts.all.zos_data_set(name=ds_name, state="absent")


## Non supported test cases
@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    test_name = "DST13"
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
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("msg") == "VSAM data set type is NOT supported"
    finally:
        ds_name = TEST_ENV["DS_NAME"]
        hosts.all.zos_data_set(name=ds_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present", force="True")
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
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == True
        results = hosts.all.shell(cmd=r"""cat "//'{0}'" """.format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""
    finally:
        hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ["PDS","PDSE"])
def test_ds_line_force_fail(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    TEST_ENV["DS_TYPE"] = dstype
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present", force="False")
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
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == False
            assert result.get("failed") == True
    finally:
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")


