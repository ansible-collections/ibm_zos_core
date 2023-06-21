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
from pprint import pprint
import time
import re


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


def set_uss_test_env(test_name, hosts, test_env):
    test_env["TEST_FILE"] = test_env["TEST_DIR"] + test_name
    try:
        hosts.all.shell(cmd="mkdir -p {0}".format(test_env["TEST_DIR"]))
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], test_env["TEST_FILE"]))
    except Exception:
        clean_uss_test_env(test_env["TEST_DIR"], hosts)
        assert 1 == 0, "Failed to set the test env"


def clean_uss_test_env(test_dir, hosts):
    try:
        hosts.all.shell(cmd="rm -rf " + test_dir)
    except Exception:
        assert 1 == 0, "Failed to clean the test env"


def UssGeneral(test_name, ansible_zos_module, test_env, test_info, expected):
    hosts = ansible_zos_module
    set_uss_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["TEST_FILE"]
    blockinfile_results = hosts.all.zos_blockinfile(**test_info)
    for result in blockinfile_results.contacted.values():
        assert result.get("changed") == 1
    cmdStr = "cat {0}".format(test_info["path"])
    results = hosts.all.shell(cmd=cmdStr)
    for result in results.contacted.values():
        assert result.get("stdout") == expected
    clean_uss_test_env(test_env["TEST_DIR"], hosts)
    return blockinfile_results


def set_ds_test_env(test_name, hosts, test_env):
    TEMP_FILE = test_env["TEST_DIR"] + test_name
    hosts.all.shell(cmd="mkdir -p {0}".format(test_env["TEST_DIR"]))
    results = hosts.all.shell(cmd='hlq')
    for result in results.contacted.values():
        hlq = result.get("stdout")
    if len(hlq) > 8:
        hlq = hlq[:8]
    test_env["DS_NAME"] = hlq + "." + test_name.upper() + "." + test_env["DS_TYPE"]
    try:
        hosts.all.zos_data_set(name=test_env["DS_NAME"], type=test_env["DS_TYPE"], replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], TEMP_FILE))
        if test_env["DS_TYPE"] in ["PDS", "PDSE"]:
            test_env["DS_NAME"] = test_env["DS_NAME"] + "(MEM)"
            hosts.all.zos_data_set(name=test_env["DS_NAME"], state="present", type="member")
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), test_env["DS_NAME"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), test_env["DS_NAME"])

        if test_env["ENCODING"] != "IBM-1047":
            hosts.all.zos_encode(
                src=TEMP_FILE,
                dest=test_env["DS_NAME"],
                encoding={
                    "from": "IBM-1047",
                    "to": test_env["ENCODING"],
                },
            )
        else:
            hosts.all.shell(cmd=cmdStr)
        hosts.all.shell(cmd="rm -rf " + test_env["TEST_DIR"])
        cmdStr = "cat \"//'{0}'\" | wc -l ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
    except Exception:
        clean_ds_test_env(test_env["DS_NAME"], hosts)
        assert 1 == 0, "Failed to set the test env"


def clean_ds_test_env(ds_name, hosts):
    ds_name = ds_name.replace("(MEM)", "")
    try:
        hosts.all.zos_data_set(name=ds_name, state="absent")
    except Exception:
        assert 1 == 0, "Failed to clean the test env"


def DsGeneral(test_name, ansible_zos_module, test_env, test_info, expected):
    hosts = ansible_zos_module
    set_ds_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["DS_NAME"]
    if test_env["ENCODING"]:
        test_info["encoding"] = test_env["ENCODING"]
    blockinfile_results = hosts.all.zos_blockinfile(**test_info)
    for result in blockinfile_results.contacted.values():
        pprint(result)
        assert result.get("changed") == 1
    if test_env["ENCODING"] == 'IBM-1047':
        cmdStr = "cat \"//'{0}'\" ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        for result in results.contacted.values():
            pprint(result)
            #assert result.get("stdout") == expected
            assert result.get("stdout").replace('\n', '').replace(' ', '') == expected.replace('\n', '').replace(' ', '')
    clean_ds_test_env(test_env["DS_NAME"], hosts)
    return blockinfile_results


def DsNotSupportedHelper(test_name, ansible_zos_module, test_env, test_info):
    hosts = ansible_zos_module
    results = hosts.all.shell(cmd='hlq')
    for result in results.contacted.values():
        hlq = result.get("stdout")
    assert len(hlq) <= 8 or hlq != ''
    test_env["DS_NAME"] = hlq + "." + test_name.upper() + "." + test_env["DS_TYPE"]
    results = hosts.all.zos_data_set(name=test_env["DS_NAME"], type=test_env["DS_TYPE"], replace='yes')
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed") is True
    test_info["path"] = test_env["DS_NAME"]
    results = hosts.all.zos_blockinfile(**test_info)
    for result in results.contacted.values():
        pprint(result)
        assert result.get("changed") is False
        assert result.get("msg") == "VSAM data set type is NOT supported"
    clean_ds_test_env(test_env["DS_NAME"], hosts)


def DsGeneralResultKeyMatchesRegex(test_name, ansible_zos_module, test_env, test_info, **kwargs):
    hosts = ansible_zos_module
    set_ds_test_env(test_name, hosts, test_env)
    test_info["path"] = test_env["DS_NAME"]
    if test_env["ENCODING"]:
        test_info["encoding"] = test_env["ENCODING"]
    results = hosts.all.zos_blockinfile(**test_info)
    for result in results.contacted.values():
        pprint(result)
        for key in kwargs:
            assert re.match(kwargs.get(key), result.get(key))
    clean_ds_test_env(test_env["DS_NAME"], hosts)


def DsGeneralForce(ansible_zos_module, test_env, test_info, expected):
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    TEMP_FILE = "/tmp/{0}".format(MEMBER_2)
    if test_env["DS_TYPE"] == "SEQ":
        test_env["DS_NAME"] = DEFAULT_DATA_SET_NAME+".{0}".format(MEMBER_2)
        test_info["path"] = DEFAULT_DATA_SET_NAME+".{0}".format(MEMBER_2)
    else:
        test_env["DS_NAME"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
        test_info["path"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2) 
    hosts = ansible_zos_module
    try:
        # set up:
        # create pdse
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type=test_env["DS_TYPE"], replace=True)
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], TEMP_FILE))
        # add members
        hosts.all.zos_data_set(
            batch=[
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": test_env["DS_NAME"],
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
            ]
        )
        # write memeber to verify cases
        # print(test_env["TEST_CONT"])
        if test_env["DS_TYPE"] in ["PDS", "PDSE"]:
            cmdStr = "cp -CM {0} \"//'{1}'\"".format(quote(TEMP_FILE), test_env["DS_NAME"])
        else:
            cmdStr = "cp {0} \"//'{1}'\" ".format(quote(TEMP_FILE), test_env["DS_NAME"])
        if test_env["ENCODING"]:
            test_info["encoding"] = test_env["ENCODING"]
        hosts.all.shell(cmd=cmdStr)
        cmdStr = "cat \"//'{0}'\" | wc -l ".format(test_env["DS_NAME"])
        results = hosts.all.shell(cmd=cmdStr)
        pprint(vars(results))
        for result in results.contacted.values():
            assert int(result.get("stdout")) != 0
        if test_env["ENCODING"] != 'IBM-1047':
            hosts.all.zos_encode(
                src=TEMP_FILE,
                dest=test_env["DS_NAME"],
                encoding={
                    "from": "IBM-1047",
                    "to": test_env["ENCODING"],
                },
            )
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.zos_copy(content=c_pgm, dest='/tmp/disp_shr/pdse-lock.c', force=True)
        hosts.all.zos_copy(
            content=call_c_jcl.format(DEFAULT_DATA_SET_NAME, MEMBER_1),
            dest='/tmp/disp_shr/call_c_pgm.jcl',
            force=True
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")

        # submit jcl
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")

        # pause to ensure c code acquires lock
        time.sleep(5)
    
        blockinfile_results = hosts.all.zos_blockinfile(**test_info)
        for result in blockinfile_results.contacted.values():
            assert result.get("changed") == True


        if test_env["ENCODING"] == 'IBM-1047':
            cmdStr = "cat \"//'{0}'\" ".format(test_info["path"])
            results = hosts.all.shell(cmd=cmdStr)
            for result in results.contacted.values():
                assert result.get("stdout").replace('\n', '').replace(' ', '') == expected.replace('\n', '').replace(' ', '')
        else:
            cmdStr =r"""cat "//'{0}'" """.format(test_info["path"])
            results = hosts.all.shell(cmd=cmdStr)

            for result in results.contacted.values():
                assert result.get("changed") == True
    finally:
        hosts.all.shell(cmd="rm -rf " + TEMP_FILE)
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        # remove pdse
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")    
    return blockinfile_results


def DsGeneralForceFail(ansible_zos_module, test_env, test_info):
    MEMBER_1, MEMBER_2 = "MEM1", "MEM2"
    hosts = ansible_zos_module
    test_info["path"] = DEFAULT_DATA_SET_NAME+"({0})".format(MEMBER_2)
    try:
        # set up:
        # create pdse
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="present", type="pdse", replace=True)
        # add members
        hosts.all.zos_data_set(
            batch=[
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_1),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
                {
                    "name": DEFAULT_DATA_SET_NAME + "({0})".format(MEMBER_2),
                    "type": "member",
                    "state": "present",
                    "replace": True,
                },
            ]
        )
        # write memeber to verify cases
        hosts.all.shell(cmd="echo \"{0}\" > {1}".format(test_env["TEST_CONT"], test_info["path"]))
        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        hosts.all.zos_copy(content=c_pgm, dest='/tmp/disp_shr/pdse-lock.c', force=True)
        hosts.all.zos_copy(
            content=call_c_jcl.format(DEFAULT_DATA_SET_NAME, MEMBER_1),
            dest='/tmp/disp_shr/call_c_pgm.jcl',
            force=True
        )
        hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir="/tmp/disp_shr/")

        # submit jcl
        hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir="/tmp/disp_shr/")

        # pause to ensure c code acquires lock
        time.sleep(5)
    
        blockinfile_results = hosts.all.zos_blockinfile(**test_info)
        for result in blockinfile_results.contacted.values():
            pprint(result)
            assert result.get("changed") == False
            assert result.get("failed") == True
    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        hosts.all.shell(cmd='rm -r /tmp/disp_shr')
        # remove pdse
        hosts.all.zos_data_set(name=DEFAULT_DATA_SET_NAME, state="absent")  