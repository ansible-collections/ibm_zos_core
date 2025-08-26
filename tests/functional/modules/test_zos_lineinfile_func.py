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
import time
import re
import inspect
import pytest
from shellescape import quote

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
}"""

call_c_jcl="""//PDSELOCK JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//LOCKMEM  EXEC PGM=BPXBATCH
//STDPARM DD *
SH {0}pdse-lock '{1}({2})'
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

TEST_PARSING_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
/*  End Ansible Block Insert */"""

EXPECTED_TEST_PARSING_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
ZOAU_ROOT=/usr/lpp/zoautil/v100
export ZOAU_ROOT
export _BPXK_AUTOCVT
SYMDEF(&IPVSRV1='IPL')
/*  End Ansible Block Insert */"""

TEST_CONTENT_ADVANCED_REGULAR_EXPRESSION="""if [ -z STEPLIB ] && tty -s;
then
    D160882
    D160882
    ED160882
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
def set_uss_environment(ansible_zos_module, content, file):
    hosts = ansible_zos_module
    hosts.all.file(path=file, state="touch")
    hosts.all.shell(cmd=f"echo \"{content}\" > {file}")

def remove_uss_environment(ansible_zos_module, file):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"rm '{file}'")

def set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content):
    hosts = ansible_zos_module
    hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
    hosts.all.zos_data_set(name=ds_name, type=ds_type)
    if ds_type in ["pds", "pdse"]:
        ds_full_name = ds_name + "(MEM)"
        hosts.all.zos_data_set(name=ds_full_name, state="present", type="member")
        cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
    else:
        ds_full_name = ds_name
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
    hosts.all.shell(cmd=cmd_str)
    hosts.all.shell(cmd="rm -rf " + temp_file)
    return ds_full_name

def remove_ds_environment(ansible_zos_module, ds_name):
    hosts = ansible_zos_module
    hosts.all.zos_data_set(name=ds_name, state="absent")

# supported data set types
ds_type = ['seq', 'pds', 'pdse']
# not supported data set types
NS_DS_TYPE = ['esds', 'rrds', 'lds']
# The encoding will be only use on a few test
ENCODING = [ 'ISO8859-1', 'UTF-8']

TMP_DIRECTORY = "/tmp/"

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_line_replace(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_insertbefore_regex(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"ZOAU_ROOT=",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_insertafter_eof(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertafter":"EOF",
        "line":"export 'ZOAU_ROOT'",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_insertbefore_bof(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "insertbefore":"BOF",
        "line":"# this is file is for setting env vars",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT=",
        "insertafter":"PATH=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER_IGNORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT=",
        "insertbefore":"PATH=",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE_IGNORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"abcxyz",
        "insertafter":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"abcxyz",
        "insertbefore":"ZOAU_ROOT=",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"abcxyz",
        "insertafter":"xyzijk",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER_NOMATCH
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"abcxyz",
        "insertbefore":"xyzijk",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE_NOMATCH
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_absent(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
        "state":"absent"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ABSENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_advanced_regular_expression_absent(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "regexp":"[A-Za-z][0-9]{6}",
        "state":"absent"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT_ADVANCED_REGULAR_EXPRESSION
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_quoted_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "path":"",
        "regexp":"ZOAU_ROOT=",
        "line":'ZOAU_ROOT=\"/mvsutil-develop_dsed\"',
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_QUOTED
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.uss
def test_uss_line_replace_quoted_not_escaped(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "path":"",
        "regexp":"ZOAU_ROOT=",
        "line":'ZOAU_ROOT="/mvsutil-develop_dsed"',
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_QUOTED
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

@pytest.mark.uss
def test_uss_line_does_not_insert_repeated(ansible_zos_module):
    hosts = ansible_zos_module
    params = {
        "path":"",
        "line":'ZOAU_ROOT=/usr/lpp/zoautil/v100',
        "state":"present"
    }
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        set_uss_environment(ansible_zos_module, content, full_path)
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat {0}".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == TEST_CONTENT
        # Run lineinfle module with same params again, ensure duplicate entry is not made into file
        hosts.all.zos_lineinfile(**params)
        results = hosts.all.shell(cmd="grep -c 'ZOAU_ROOT=/usr/lpp/zoautil/v10' {0} ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == '1'
    finally:
        remove_uss_environment(ansible_zos_module, full_path)

#########################
# Dataset test cases
#########################

# Now force is parameter to change witch function
# to call in the helper and alter the declaration by add the force or a test name required.
# without change the original description or the other option
# is that at the end of the test get back to original one.
@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_insertafter_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_insert_before_ansible_block(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype

    params = {
        "insertbefore": "/\*  End Ansible Block Insert \*/",
        "line": "SYMDEF(&IPVSRV1='IPL')",
        "state": "present"
    }

    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_PARSING_CONTENT

    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name

        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_TEST_PARSING_CONTENT
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_insertbefore_regex(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"ZOAU_ROOT=",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_REGEX
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_insertafter_eof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertafter":"EOF",
        "line":"export 'ZOAU_ROOT'",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTAFTER_EOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)

@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_insertbefore_bof(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "insertbefore":"BOF",
        "line":"# this is file is for setting env vars",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_INSERTBEFORE_BOF
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT=",
        "insertafter":"PATH=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTAFTER_IGNORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT=",
        "insertbefore":"PATH=",
        "line":"unset ZOAU_ROOT",
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE_INSERTBEFORE_IGNORE
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
def test_gds_ds_insert_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="eof", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name(3, 2)
    try:
        # Set environment
        hosts.all.shell(cmd="dtouch -tGDG -L3 {0}".format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))
        hosts.all.shell(cmd="""dtouch -tseq "{0}(+1)" """.format(ds_name))

        params["src"] = ds_name + "(0)"
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
            cmd = result.get("cmd").split()
        for cmd_p in cmd:
            if ds_name in cmd_p:
                dataset = cmd_p
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(dataset))
        for result in results.contacted.values():
            assert result.get("stdout") == "ZOAU_ROOT=/mvsutil-develop_dsed"

        params["src"] = ds_name + "(-1)"
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
            cmd = result.get("cmd").split()
        for cmd_p in cmd:
            if ds_name in cmd_p:
                dataset = cmd_p
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(dataset))
        for result in results.contacted.values():
            assert result.get("stdout") == "ZOAU_ROOT=/mvsutil-develop_dsed"

        params_w_bck = dict(insertafter="eof", line="export ZOAU_ROOT", state="present", backup=True, backup_name=ds_name + "(+1)")
        params_w_bck["src"] = ds_name + "(-1)"
        results = hosts.all.zos_lineinfile(**params_w_bck)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert result.get("rc") == 0
            assert "return_content" in result
        backup = ds_name + "(0)"
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == "ZOAU_ROOT=/mvsutil-develop_dsed"

        params["src"] = ds_name + "(-2)"
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result       
    finally:
        hosts.all.shell(cmd="""drm "{0}*" """.format(ds_name))


@pytest.mark.ds
def test_special_characters_ds_insert_line(ansible_zos_module):
    hosts = ansible_zos_module
    params = dict(insertafter="eof", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
    ds_name = get_tmp_ds_name(5, 5, symbols=True)
    backup = get_tmp_ds_name(6, 6, symbols=True)
    try:
        # Set environment
        result = hosts.all.zos_data_set(name=ds_name, type="seq", state="present")

        params["src"] = ds_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        src = ds_name.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(src))
        for result in results.contacted.values():
            assert result.get("stdout") == "ZOAU_ROOT=/mvsutil-develop_dsed"

        params_w_bck = dict(insertafter="eof", line="export ZOAU_ROOT", state="present", backup=True, backup_name=backup)
        params_w_bck["src"] = ds_name
        results = hosts.all.zos_lineinfile(**params_w_bck)
        for result in results.contacted.values():
            print(result)
            assert result.get("changed") == 1
            assert result.get("rc") == 0
            assert "return_content" in result
        backup = backup.replace('$', "\$")
        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(backup))
        for result in results.contacted.values():
            assert result.get("stdout") == "ZOAU_ROOT=/mvsutil-develop_dsed"

    finally:
        hosts.all.shell(cmd="""drm "ANSIBLE.*" """.format(ds_name))


#GH Issue #1244
#@pytest.mark.ds
#@pytest.mark.parametrize("dstype", ds_type)
#def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module, dstype):
#    hosts = ansible_zos_module
#    ds_type = dstype
#    params = dict(
#       regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed",
#       state="present")
#    ds_name = get_tmp_ds_name()
#    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#    content = TEST_CONTENT
#    try:
#        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#        params["path"] = ds_full_name
#        results = hosts.all.zos_lineinfile(**params)
#        for result in results.contacted.values():
#            print(result)
#            assert result.get("changed") == 1
#        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
#        for result in results.contacted.values():
#            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER
#    finally:
#        remove_ds_environment(ansible_zos_module, ds_name)

#GH Issue #1244 / JIRA NAZARE-10439
#@pytest.mark.ds
#@pytest.mark.parametrize("dstype", ds_type)
#def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module, dstype):
#    hosts = ansible_zos_module
#    ds_type = dstype
#    params = dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=",
# line="unset ZOAU_ROOT", state="present")
#    ds_name = get_tmp_ds_name()
#    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#    content = TEST_CONTENT
#    try:
#        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#        params["path"] = ds_full_name
#        results = hosts.all.zos_lineinfile(**params)
#        for result in results.contacted.values():
#            print(result)
#            assert result.get("changed") == 1
#        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
#        for result in results.contacted.values():
#            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE
#    finally:
#        remove_ds_environment(ansible_zos_module, ds_name)

#GH Issue #1244 / JIRA NAZARE-10439
#@pytest.mark.ds
#@pytest.mark.parametrize("dstype", ds_type)
#def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module, dstype):
#    hosts = ansible_zos_module
#    ds_type = dstype
#    params = dict(regexp="abcxyz", insertafter="xyzijk",
# line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present")
#    ds_name = get_tmp_ds_name()
#    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#    content = TEST_CONTENT
#    try:
#        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#        params["path"] = ds_full_name
#        results = hosts.all.zos_lineinfile(**params)
#        for result in results.contacted.values():
#            print(result)
#            assert result.get("changed") == 1
#        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
#        for result in results.contacted.values():
#            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTAFTER_NOMATCH
#    finally:
#        remove_ds_environment(ansible_zos_module, ds_name)

#GH Issue #1244 / JIRA NAZARE-10439
#@pytest.mark.ds
#@pytest.mark.parametrize("dstype", ds_type)
#def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module, dstype):
#    hosts = ansible_zos_module
#    ds_type = dstype
#    params = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present")
#    ds_name = get_tmp_ds_name()
#    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
#    content = TEST_CONTENT
#    try:
#        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
#        params["path"] = ds_full_name
#        results = hosts.all.zos_lineinfile(**params)
#        for result in results.contacted.values():
#            print(result)
#            assert result.get("changed") == 1
#        results = hosts.all.shell(cmd="cat \"//'{0}'\" ".format(params["path"]))
#        for result in results.contacted.values():
#            assert result.get("stdout") == EXPECTED_REPLACE_NOMATCH_INSERTBEFORE_NOMATCH
#    finally:
#        remove_ds_environment(ansible_zos_module, ds_name)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_absent(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/usr/lpp/zoautil/v100",
        "state":"absent"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    try:
        ds_full_name = set_ds_environment(ansible_zos_module, temp_file, ds_name, ds_type, content)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
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
    kwargs = {
        "backup_name": hlq
    }
    params = {
        "insertafter":"EOF",
        "line":"export ZOAU_ROOT",
        "state":"present",
        "backup":True,
        "tmp_hlq": hlq
    }
    content = TEST_CONTENT
    try:
        ds_full_name = get_tmp_ds_name()
        temp_file = get_random_file_name(dir=TMP_DIRECTORY)
        hosts.all.zos_data_set(name=ds_full_name, type=ds_type, replace=True)
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
        hosts.all.shell(cmd=cmd_str)
        hosts.all.shell(cmd="rm -rf " + "/tmp/zos_lineinfile/")
        results = hosts.all.shell(cmd=f"cat \"//'{ds_full_name}'\" | wc -l ")
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert "return_content" in result
            for key in kwargs:
                assert kwargs.get(key) in result.get(key)
    finally:
        hosts.all.zos_data_set(name=ds_full_name, state="absent")


## Non supported test cases
@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "path":"",
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present"
    }
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
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_force(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name = get_tmp_ds_name()
    params = {
        "path":"",
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present",
        "force":"True"
    }
    member_1, member_2 = "MEM1", "MEM2"
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = TEST_CONTENT
    if ds_type == "seq":
        params["path"] = f"{default_data_set_name}.{member_2}"
    else:
        params["path"] = f"{default_data_set_name}({member_2})"
    try:
        # set up:
        hosts.all.zos_data_set(
            name=default_data_set_name,
            state="present",
            type=ds_type,
            replace=True
        )
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        hosts.all.zos_data_set(
            batch=[
                {   "name": f"{default_data_set_name}({member_1})",
                    "type": "member", "state": "present", "replace": True, },
                {   "name": params["path"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
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
            cmd=f"echo \"{call_c_jcl.format(path, default_data_set_name, member_1)}\""+
            " > {0}call_c_pgm.jcl".format(path)
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=path)
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=path)
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is True
        results = hosts.all.shell(cmd=r"""cat "//'{0}'" """.format(params["path"]))
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_REPLACE
    finally:
        hosts.all.shell(cmd="rm -rf " + temp_file)
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(path))
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ["pds","pdse"])
def test_ds_line_force_fail(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    default_data_set_name = get_tmp_ds_name()
    params = {
        "path":"",
        "regexp":"ZOAU_ROOT=",
        "line":"ZOAU_ROOT=/mvsutil-develop_dsed",
        "state":"present",
        "force":False
    }
    member_1, member_2 = "MEM1", "MEM2"
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    params["path"] = f"{default_data_set_name}({member_2})"
    content = TEST_CONTENT
    try:
        # set up:
        hosts.all.zos_data_set(
            name=default_data_set_name,
            state="present",
            type=ds_type,
            replace=True
        )
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        hosts.all.zos_data_set(
            batch=[
                {   "name": f"{default_data_set_name}({member_1})",
                    "type": "member", "state": "present", "replace": True, },
                {   "name": params["path"], "type": "member",
                    "state": "present", "replace": True, },
            ]
        )
        cmd_str = "cp -CM {0} \"//'{1}'\"".format(quote(temp_file), params["path"])
        hosts.all.shell(cmd=cmd_str)
        results = hosts.all.shell(cmd="cat \"//'{0}'\" | wc -l ".format(params["path"]))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        path = get_random_file_name(suffix="/", dir=TMP_DIRECTORY)
        hosts.all.file(path=path, state="directory")
        hosts.all.shell(cmd=f"echo \"{c_pgm}\"  > {path}pdse-lock.c")
        hosts.all.shell(
            cmd=f"echo \"{call_c_jcl.format(path, default_data_set_name, member_1)}\""+
            " > {0}call_c_pgm.jcl".format(path)
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=path)
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=path)
        time.sleep(5)
        # call lineinfile to see results
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") is False
            assert result.get("failed") is True
    finally:
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd=f"kill 9 {pid.strip()}")
        hosts.all.shell(cmd='rm -r {0}'.format(path))
        hosts.all.zos_data_set(name=default_data_set_name, state="absent")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
def test_ds_line_does_not_insert_repeated(ansible_zos_module, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    params = {
        "line":'ZOAU_ROOT=/usr/lpp/zoautil/v100',
        "state":"present"
    }
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
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
        results = hosts.all.shell(
            cmd="dgrep -c 'ZOAU_ROOT=/usr/lpp/zoautil/v10' '{0}' ".format(params["path"])
            )
        response = params["path"] + "          " + "1"
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
    params = {
        "insertafter":"SIMPLE",
        "line":insert_data,
        "state":"present",
        "encoding":{
            "from":"IBM-1047",
            "to":encoding
        }
    }
    params["encoding"] = encoding
    full_path = get_random_file_name(dir=TMP_DIRECTORY)
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.file(path=full_path, state="touch")
        hosts.all.shell(cmd=f"echo \"{content}\" > {full_path}")
        params["path"] = full_path
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        results = hosts.all.shell(cmd=f"iconv -f IBM-1047 -t {encoding} {full_path}")
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_uss_environment(ansible_zos_module, full_path)


@pytest.mark.ds
@pytest.mark.parametrize("dstype", ds_type)
@pytest.mark.parametrize("encoding", ["IBM-1047"])
def test_ds_encoding(ansible_zos_module, encoding, dstype):
    hosts = ansible_zos_module
    ds_type = dstype
    insert_data = "Insert this string"
    params = {
        "insertafter":"SIMPLE",
        "line":insert_data,
        "state":"present",
        "encoding":{
            "from":"IBM-1047",
            "to":encoding
        }
    }
    params["encoding"] = encoding
    ds_name = get_tmp_ds_name()
    temp_file = get_random_file_name(dir=TMP_DIRECTORY)
    content = "SIMPLE LINE TO VERIFY"
    try:
        hosts.all.shell(cmd=f"echo \"{content}\" > {temp_file}")
        hosts.all.shell(cmd=f"iconv -f IBM-1047 -t {params['encoding']} temp_file > temp_file ")
        hosts.all.zos_data_set(name=ds_name, type=ds_type)
        if ds_type in ["pds", "pdse"]:
            ds_full_name = ds_name + "(MEM)"
            hosts.all.zos_data_set(name=ds_full_name, state="present", type="member")
            cmd_str = f"cp -CM {quote(temp_file)} \"//'{ds_full_name}'\""
        else:
            ds_full_name = ds_name
            cmd_str = f"cp {quote(temp_file)} \"//'{ds_full_name}'\" "
        hosts.all.shell(cmd=cmd_str)
        hosts.all.shell(cmd="rm -rf " + temp_file)
        params["path"] = ds_full_name
        results = hosts.all.zos_lineinfile(**params)
        for result in results.contacted.values():
            assert result.get("changed") == 1
            assert "return_content" in result
        hosts.all.shell(
            cmd=f"iconv -f {encoding} -t IBM-1047 \"{ds_full_name}\" > \"{ds_full_name}\" "
        )
        results = hosts.all.shell(cmd=f"cat \"//'{ds_full_name}'\" ")
        for result in results.contacted.values():
            assert result.get("stdout") == EXPECTED_ENCODING
    finally:
        remove_ds_environment(ansible_zos_module, ds_name)
        # ds_full_name gets converted to a file too
        remove_uss_environment(ansible_zos_module, ds_full_name)
