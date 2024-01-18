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
import inspect
import os

from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name

__metaclass__ = type

TEST_FOLDER_LINEINFILE = "/tmp/ansible-core-tests/zos_lineinfile/"

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

TEST_CONTENT="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_REPLACE="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_INSERTAFTER_REGEX="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_INSERTBEFORE_REGEX="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_INSERTAFTER_EOF="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
export 'ZOAU_ROOT'"""

EXPECTED_INSERTBEFORE_BOF="""# this is file is for setting env vars
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

EXPECTED_REPLACE_INSERTAFTER_IGNORE="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/mvsutil-develop_dsed
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_REPLACE_INSERTBEFORE_IGNORE="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
unset ZOAU_ROOT
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_REPLACE_NOMATCH_INSERTAFTER="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_REPLACE_NOMATCH_INSERTBEFORE="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_REPLACE_NOMATCH_INSERTAFTER_NOMATCH="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_REPLACE_NOMATCH_INSERTBEFORE_NOMATCH="""if [ -z STEPLIB ] && tty -s;
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

EXPECTED_ABSENT="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_QUOTED="""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT="/mvsutil-develop_dsed"
export ZOAU_ROOT
export _BPXK_AUTOCVT"""

EXPECTED_ENCODING="""SIMPLE LINE TO VERIFY
Insert this string"""
def set_uss_environment(ansible_zos_module, CONTENT, FILE):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="mkdir -p {0}".format(TEST_FOLDER_LINEINFILE))
    hosts.all.file(path=FILE, state="touch")
    hosts.all.shell(cmd="echo \"{0}\" > {1}".format(CONTENT, FILE))

def remove_uss_environment(ansible_zos_module):
    hosts = ansible_zos_module
    hosts.all.shell(cmd="rm -rf " + TEST_FOLDER_LINEINFILE)

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
# supported data set types
DS_TYPE = ['SEQ', 'PDS', 'PDSE']
# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
# The encoding will be only use on a few test
ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_line_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_insertbefore_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_insertafter_eof(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="EOF", line="export 'ZOAU_ROOT'", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_insertbefore_bof(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertafter="PATH=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER_IGNORE
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE_IGNORE
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertafter="xyzijk", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER_NOMATCH
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE_NOMATCH
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_absent(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(regexp="ZOAU_ROOT=", line="", state="absent")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_quoted_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", regexp="ZOAU_ROOT=", line='ZOAU_ROOT=\"/mvsutil-develop_dsed\"', state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_QUOTED
    finally:
        remove_uss_environment(ansible_zos_module)


@pytest.mark.uss
def test_uss_line_replace_quoted_not_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", regexp="ZOAU_ROOT=", line='ZOAU_ROOT="/mvsutil-develop_dsed"', state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_QUOTED
    finally:
        remove_uss_environment(ansible_zos_module)

@pytest.mark.uss
def test_uss_line_does_not_insert_repeated(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(path="", line='ZOAU_ROOT=/usr/lpp/zoautil/v100', state="present")
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
        # Run lineinfle module with same params again, ensure duplicate entry is not made into file
        hosts.all.zos_lineinfile(**params)
        results = hosts.all.shell(cmd="""grep -c 'ZOAU_ROOT=/usr/lpp/zoautil/v10' {0} """.format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == '1'
    finally:
        remove_uss_environment(ansible_zos_module)

#########################
# Dataset test cases
#########################

# Now force is parameter to change witch function to call in the helper and alter the declaration by add the force or a test name required.
# without change the original description or the other option is that at the end of the test get back to original one.
@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_eof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertafter="EOF", line="export 'ZOAU_ROOT'", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_bof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="ZOAU_ROOT=", insertafter="PATH=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER_IGNORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE_IGNORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="abcxyz", insertafter="xyzijk", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER_NOMATCH
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE_NOMATCH
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(regexp="ZOAU_ROOT=", line="", state="absent")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
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
    kwargs = dict(backup_name=r"TMPHLQ\..")
    params = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present", backup=True, tmp_hlq="TMPHLQ")
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
            assert int(result.get("stdout")) != 0
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            for key in kwargs:
                assert re.match(kwargs.get(key), result.get(key))
    finally:
        hosts.all.zos_data_set(name=ds_full_name, state="absent")


## Non supported test cases
@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    try:
        ds_name = get_tmp_ds_name() + "." + ds_type
        results = hosts.all.zos_data_set(name=ds_name, type=ds_type, replace='yes')
        for result in results.contacted.values():
            assert result.get("changed") is True
        params["path"] = ds_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("msg") == "VSAM data set type is NOT supported"
    finally:
        hosts.all.zos_data_set(name=ds_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    DEFAULT_DATA_SET_NAME = get_tmp_ds_name()
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present", force="True")
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    content = TEST_CONTENT
    if ds_type == "SEQ":
        params["path"] = DEFAULT_DATA_SET_NAME+".{0}".format(MEMBER_2)
    else:
        params["path"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
    try:
        # set up:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=ds_type, replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
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
            assert result.get("stdout") == EXPECTED_REPLACE
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
    ds_type = dstype
    DEFAULT_DATA_SET_NAME = get_tmp_ds_name()
    params = dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present", force="False")
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    params["path"] = DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_2)
    content = TEST_CONTENT
    try:
        # set up:
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=ds_type, replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, TEMP_FILE))
        hosts.all.zos_data_set(
            batch=[
                {   "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
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


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_does_not_insert_repeated(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = dict(line='ZOAU_ROOT=/usr/lpp/zoautil/v100', state="present")
    ds_name = get_tmp_ds_name()
    temp_file = "/tmp/" + ds_name
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
        # Run lineinfle module with same params again, ensure duplicate entry is not made into file
        hosts.all.zos_lineinfile(**params)
        results = hosts.all.shell(cmd="""dgrep -c 'ZOAU_ROOT=/usr/lpp/zoautil/v10' "{0}" """.format(params["path"]))
        response = params["path"] + " " + "1"
        for result in results.contacted.values():
            assert result.get("stdout") == response
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

#########################
# Encoding tests
#########################

@pytest.mark.uss
@pytest.mark.parametrize("encoding", ENCODING)
def test_uss_encoding(ansible_zos_module, encoding):
    hosts = ansible_zos_module
    insert_data = "Insert this string"
    params = dict(insertafter="SIMPLE", line=insert_data, state="present")
    params["encoding"] = encoding
    full_path = TEST_FOLDER_LINEINFILE + inspect.stack()[0][3]
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.shell(cmd="mkdir -p {0}".format(TEST_FOLDER_LINEINFILE))
        hosts.all.file(path=full_path, state="touch")
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(content, full_path))
        hosts.all.zos_encode(src=full_path, dest=full_path, from_encoding="IBM-1047", to_encoding=params["encoding"])
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
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
    params = dict(insertafter="SIMPLE", line=insert_data, state="present")
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
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
        hosts.all.zos_encode(src=ds_full_name, dest=ds_full_name, from_encoding=params["encoding"], to_encoding="IBM-1047")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)