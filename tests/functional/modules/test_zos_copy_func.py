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

from ibm_zos_core.tests.helpers.users import ManagedUserType, ManagedUser
import pytest
import os
import shutil
import re
import time
import yaml
import tempfile
import subprocess
from shellescape import quote
from ibm_zos_core.tests.helpers.volumes import Volume_Handler
from ibm_zos_core.tests.helpers.dataset import get_tmp_ds_name
from ibm_zos_core.tests.helpers.utils import get_random_file_name
__metaclass__ = type


# Test temporary folder
TMP_DIRECTORY = '/tmp/'
DUMMY_DATA = """DUMMY DATA ---- LINE 001 ------
DUMMY DATA ---- LINE 002 ------
DUMMY DATA ---- LINE 003 ------
DUMMY DATA ---- LINE 004 ------
DUMMY DATA ---- LINE 005 ------
DUMMY DATA ---- LINE 006 ------
DUMMY DATA ---- LINE 007 ------"""

DUMMY_DATA_SPECIAL_CHARS = """DUMMY DATA ---- LINE 001 ------
DUMMY DATA ---- LINE ÁÁÁ------
DUMMY DATA ---- LINE ÈÈÈ ------
DUMMY DATA ---- LINE 004 ------
DUMMY DATA ---- LINE 005 ------
DUMMY DATA ---- LINE 006 ------
DUMMY DATA ---- LINE 007 ------
"""

DUMMY_DATA_CRLF = b"00000001 DUMMY DATA\r\n00000002 DUMMY DATA\r\n"
DUMMY_DATA_CRLF_POUND = "00000001 DUMMY DATA\r\n00000002££ DUMMY DATA\r\n"

# FD is outside of the range of UTF-8, so it should be useful when testing
# that binary data is not getting converted.
DUMMY_DATA_BINARY = b"\xFD\xFD\xFD\xFD"
DUMMY_DATA_BINARY_ESCAPED = "\\xFD\\xFD\\xFD\\xFD"

VSAM_RECORDS = """00000001A record
00000002A record
00000003A record
"""

TEMPLATE_CONTENT = """
This is a Jinja2 test: {{ var }}

{# This is a comment. #}

If:
{% if if_var is divisibleby 5 %}
Condition is true.
{% endif %}

Inside a loop:
{% for i in array %}
Current element: {{ i }}
{% endfor %}
"""

TEMPLATE_CONTENT_NON_DEFAULT_MARKERS = """
This is a Jinja2 test: (( var ))

#% This is a comment. %#

If:
{% if if_var is divisibleby 5 %}
Condition is true.
{% endif %}

Inside a loop:
{% for i in array %}
Current element: (( i ))
{% endfor %}
"""

# Text that will be used for the ASA control chars tests.
# It contains at least one instance of each control char.
ASA_SAMPLE_CONTENT = """ Space, do not advance.
0Newline before printing this line.
 This line is not going to be seen.
+This line will overwrite the previous one.
 This line will be partially seen because it will be longer than the next line.
+This line will partially overwrite the previous line.
-Three newlines before this one.
1This is a new page.
"""

ASA_SAMPLE_RETURN = "\nSpace, do not advance.\n\nNewline before printing this line.\nThis line is not going to be seen.\rThis line will overwrite the previous one.\nThis line will be partially seen because it will be longer than the next line.\rThis line will partially overwrite the previous line.\n\n\nThree newlines before this one.\fThis is a new page."

ASA_COPY_CONTENT = """  Space, do not advance.
 0Newline before printing this line.
  This line is not going to be seen.
 +This line will overwrite the previous one.
  This line will be partially seen because it will be longer than the next line.
 +This line will partially overwrite the previous line.
 -Three newlines before this one.
 1This is a new page."""

# SHELL_EXECUTABLE = "/usr/lpp/rsusr/ported/bin/bash"
SHELL_EXECUTABLE = "/bin/sh"

COBOL_PRINT_STR = "HELLO WORLD ONE"
COBOL_PRINT_STR2 = "HELLO WORLD TWO"

COBOL_SRC = """
       IDENTIFICATION DIVISION.\n
       PROGRAM-ID. HELLOWRD.\n
\n
       PROCEDURE DIVISION.\n
           DISPLAY "{0}".\n
           STOP RUN.\n
"""

# format params for LINK_JCL:
# {0} - cobol src pds dsn
# {1} - cobol src pds member
# {2} - candidate loadlib dsn
# {3} - candidate loadlib member
# {4} - alias member name
LINK_JCL = """
//COMPLINK  JOB MSGCLASS=H,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//STEP1     EXEC PGM=IGYCRCTL
//STEPLIB   DD DSN=IGYV5R10.SIGYCOMP,DISP=SHR
//          DD DSN=IGYV5R10.SIGYMAC,DISP=SHR
//SYSIN     DD DISP=SHR,DSN={0}({1})
//SYSPRINT  DD SYSOUT=*
//SYSLIN   DD  UNIT=SYSDA,DISP=(MOD),
//             SPACE=(CYL,(1,1)),
//             DCB=(RECFM=FB,LRECL=80,BLKSIZE=27920),
//             DSN=&&LOADSET
//SYSUT1    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT2    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT3    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT4    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT5    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT6    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT7    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT8    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT9    DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT10   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT11   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT12   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT13   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT14   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSUT15   DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//SYSMDECK  DD SPACE=(80,(10,10),,,ROUND),UNIT=SYSDA
//*
//LKED     EXEC PGM=IEWL,REGION=0M
//SYSPRINT DD  SYSOUT=*
//SYSLIB   DD  DSN=CEE.SCEELKED,DISP=SHR
//         DD  DSN=CEE.SCEELKEX,DISP=SHR
//SYSLMOD  DD  DSN={2}({3}),
//             DISP=SHR
//SYSUT1   DD  UNIT=SYSDA,DCB=BLKSIZE=1024,
//             SPACE=(TRK,(3,3))
//SYSTERM  DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSLIN   DD  DSN=&&LOADSET,DISP=(OLD,KEEP)
//         DD  *
  ALIAS    {4}
  NAME     {3}
//*
//SYSIN    DD  DUMMY

"""

hello_world = """#include <stdio.h>
int main()
{
   printf("Hello World!");
   return 0;
}
"""

call_c_hello_jcl="""//PDSELOCK JOB MSGCLASS=A,MSGLEVEL=(1,1),NOTIFY=&SYSUID,REGION=0M
//LOCKMEM  EXEC PGM=BPXBATCH
//STDPARM DD *
SH {0}/hello_world
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""

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
SH {0}/pdse-lock '{1}'
//STDIN  DD DUMMY
//STDOUT DD SYSOUT=*
//STDERR DD SYSOUT=*
//"""

PLAYBOOK_ASYNC_TEST = """- hosts: zvm
  collections:
    - ibm.ibm_zos_core
  gather_facts: False
  environment:
    _BPXK_AUTOCVT: "ON"
    ZOAU_HOME: "{0}"
    PYTHONPATH: "{0}/lib/{2}"
    LIBPATH: "{0}/lib:{1}/lib:/lib:/usr/lib:."
    PATH: "{0}/bin:/bin:/usr/lpp/rsusr/ported/bin:/var/bin:/usr/lpp/rsusr/ported/bin:/usr/lpp/java/java180/J8.0_64/bin:{1}/bin:"
    _CEE_RUNOPTS: "FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)"
    _TAG_REDIR_ERR: "txt"
    _TAG_REDIR_IN: "txt"
    _TAG_REDIR_OUT: "txt"
    LANG: "C"
    PYTHONSTDINENCODING: "cp1047"

  tasks:
    - name: Create a copy
      zos_copy:
            src: /etc/profile
            remote_src: True
            replace: True
            dest: {3}
      async: 50
      poll: 0
      register: copy_output

    - name: Query async task.
      async_status:
        jid: "{{{{ copy_output.ansible_job_id }}}}"
      register: job_result
      until: job_result.finished | bool
      retries: 10
      delay: 30

    - name: Echo copy_output.
      debug:
        msg: "{{ job_result }}"
"""

INVENTORY_ASYNC_TEST = """all:
  hosts:
    zvm:
      ansible_host: {0}
      ansible_ssh_private_key_file: {1}
      ansible_user: {2}
      ansible_python_interpreter: {3}"""

def populate_dir(dir_path):
    for i in range(5):
        with open(dir_path + "/" + "file" + str(i + 1), "w") as infile:
            infile.write(DUMMY_DATA)


def create_template_file(dir_path, use_default_markers=True, encoding="utf-8"):
    content = TEMPLATE_CONTENT if use_default_markers else TEMPLATE_CONTENT_NON_DEFAULT_MARKERS
    template_path = os.path.join(dir_path, "template")

    with open(template_path, "w", encoding=encoding) as infile:
        infile.write(content)

    return template_path


def populate_dir_crlf_endings(dir_path):
    for i in range(5):
        with open(os.path.join(dir_path, "file{0}".format(i)), "wb") as infile:
            infile.write(DUMMY_DATA_CRLF)


def populate_partitioned_data_set(hosts, name, ds_type, members=None):
    """Creates a new partitioned data set and inserts records into various
    members of it.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the data set.
        ds_type (str) -- Type of the data set (either pds or pdse).
        members (list, optional) -- List of member names to create.
    """
    if not members:
        members = ["MEMBER1", "MEMBER2", "MEMBER3"]
    ds_list = ["{0}({1})".format(name, member) for member in members]

    hosts.all.shell(cmd=f"dtouch -t{ds_type} {name}")

    for member in ds_list:
        hosts.all.shell(
            cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
            executable=SHELL_EXECUTABLE
        )


def get_listcat_information(hosts, name, ds_type):
    """Runs IDCAMS to get information about a data set.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the data set.
        ds_type (str) -- Type of data set ("seq", "pds", "pdse", "ksds").
    """
    if ds_type == "ksds":
        idcams_input = " LISTCAT ENT('{0}') DATA ALL".format(name)
    else:
        idcams_input = " LISTCAT ENTRIES('{0}')".format(name)

    return hosts.all.zos_mvs_raw(
        program_name="idcams",
        auth=True,
        dds=[
            dict(dd_output=dict(
                dd_name="sysprint",
                return_content=dict(type="text")
            )),
            dict(dd_input=dict(
                dd_name="sysin",
                content=idcams_input
            ))
        ]
    )


def create_vsam_data_set(hosts, name, ds_type, add_data=False, key_length=None, key_offset=None):
    """Creates a new VSAM on the system.

    Arguments:
        hosts (object) -- Ansible instance(s) that can call modules.
        name (str) -- Name of the VSAM data set.
        type (str) -- Type of the VSAM (ksds, esds, rrds, lds)
        add_data (bool, optional) -- Whether to add records to the VSAM.
        key_length (int, optional) -- Key length (only for KSDS data sets).
        key_offset (int, optional) -- Key offset (only for KSDS data sets).
    """
    params = dict(
        name=name,
        type=ds_type,
        state="present"
    )
    if ds_type == "ksds":
        params["key_length"] = key_length
        params["key_offset"] = key_offset

    hosts.all.zos_data_set(**params)

    if add_data:
        record_src = get_random_file_name(dir=TMP_DIRECTORY)

        hosts.all.shell(cmd=f"echo '{VSAM_RECORDS}' > '{record_src}' ")
        hosts.all.zos_encode(src=record_src, dest=name, encoding={"from": "ISO8859-1", "to": "IBM-1047"})
        hosts.all.file(path=record_src, state="absent")


def validate_loadlib_pgm(hosts, steplib, pgm_name, expected_output_str):

    mvscmd_str = "mvscmd --steplib='{0}' --pgm='{1}' --sysout='*' --sysprint='*'"
    verify_copy_exec_pgm = hosts.all.shell(
        cmd=mvscmd_str.format(steplib, pgm_name)
    )

    for v_cp_pgm in verify_copy_exec_pgm.contacted.values():
        assert v_cp_pgm.get("rc") == 0
        assert v_cp_pgm.get("stdout").strip() == expected_output_str


def link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mem, loadlib_pds, loadlib_mem, loadlib_alias_mem='ALIAS1'):
    """
    Given a PDSE, links a cobol program (allocated in a temp ds) resulting in a loadlib.

    Arguments:
        cobol_src_pds (str) - cobol src pds dsn containing members containing cobol src code.
        cobol_src_mem (str) - cobol src pds member containing cobol src code.
        loadlib_pds (str) - candidate loadlib dsn
        loadlib_mem (str) - candidate loadlib member
        loadlib_alias_mem (str) - alias member name
    """
    temp_jcl_uss_path = get_random_file_name(dir=TMP_DIRECTORY)
    rc = 0
    try:
        # Copy over the Link program to USS
        cp_res = hosts.all.zos_copy(
            content=LINK_JCL.format(cobol_src_pds, cobol_src_mem, loadlib_pds, loadlib_mem, loadlib_alias_mem),
            dest=temp_jcl_uss_path,
            replace=True,
        )
        # Submit link JCL.
        job_result = hosts.all.zos_job_submit(
            src=temp_jcl_uss_path,
            remote_src=True,
            wait_time=60
        )
        for result in job_result.contacted.values():
            print(result)
            rc = result.get("jobs")[0].get("ret_code").get("code")
    finally:
        hosts.all.file(path=temp_jcl_uss_path, state="absent")
    return rc


def generate_executable_ds(hosts, cobol_src_pds, cobol_src_mem, loadlib_pds, loadlib_mem, loadlib_alias_mem="ALIAS1"):

    # copy COBOL src string to pds.
    hosts.all.zos_copy(content=COBOL_SRC.format(COBOL_PRINT_STR), dest='{0}({1})'.format(cobol_src_pds, cobol_src_mem))

    # run link-edit to create loadlib.
    link_rc = link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mem, loadlib_pds, loadlib_mem, loadlib_alias_mem)
    assert link_rc == 0

    # execute pgm to test loadlib
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_mem, expected_output_str=COBOL_PRINT_STR)
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_alias_mem, expected_output_str=COBOL_PRINT_STR)


def generate_loadlib(hosts, cobol_src_pds, cobol_src_mems, loadlib_pds, loadlib_mems, loadlib_alias_mems):
    # copy cobol src
    hosts.all.zos_copy(content=COBOL_SRC.format(COBOL_PRINT_STR), dest='{0}({1})'.format(cobol_src_pds, cobol_src_mems[0]))
    # copy cobol2 src
    hosts.all.zos_copy(content=COBOL_SRC.format(COBOL_PRINT_STR2), dest='{0}({1})'.format(cobol_src_pds, cobol_src_mems[1]))

    # run link-edit for pgm1
    link_rc = link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mems[0], loadlib_pds, loadlib_mems[0], loadlib_alias_mems[0])
    assert link_rc == 0
    # run link-edit for pgm2
    link_rc = link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mems[1], loadlib_pds, loadlib_mems[1], loadlib_alias_mems[1])
    assert link_rc == 0

    # execute pgm to test pgm1
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_mems[0], expected_output_str=COBOL_PRINT_STR)
    # execute pgm to test alias of pgm1
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_alias_mems[0], expected_output_str=COBOL_PRINT_STR)
    # execute pgm to test pgm2
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_mems[1], expected_output_str=COBOL_PRINT_STR2)
    # execute pgm to test alias of pgm2
    validate_loadlib_pgm(hosts, steplib=loadlib_pds, pgm_name=loadlib_alias_mems[1], expected_output_str=COBOL_PRINT_STR2)


def generate_executable_uss(hosts, dir, src, src_jcl_call):
    hosts.all.zos_copy(content=hello_world, dest=src, replace=True)
    hosts.all.zos_copy(content=call_c_hello_jcl.format(dir), dest=src_jcl_call, replace=True)
    hosts.all.shell(cmd="xlc -o hello_world hello_world.c", chdir=dir)
    hosts.all.shell(cmd="submit {0}".format(src_jcl_call))
    verify_exe_src = hosts.all.shell(cmd="{0}/hello_world".format(dir))
    for res in verify_exe_src.contacted.values():
        assert res.get("rc") == 0
        stdout = res.get("stdout")
        assert  "Hello World" in str(stdout)


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_uss_file(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.file(path=dest_path, state="absent")

        if src["is_file"]:
            copy_res = hosts.all.zos_copy(src=src["src"], dest=dest_path, binary=src["binary"], remote_src=src["is_remote"])
        else:
            copy_res = hosts.all.zos_copy(content=src["src"], dest=dest_path, binary=src["binary"])

        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            print(result)
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=False, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=True),
])
def test_copy_file_to_existing_uss_file(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.file(path=dest_path, state="touch")
        stat_res = list(hosts.all.stat(path=dest_path).contacted.values())
        timestamp = stat_res[0].get("stat").get("atime")
        assert timestamp is not None

        if src["is_file"]:
            copy_res = hosts.all.zos_copy(src=src["src"], dest=dest_path, replace=src["replace"], remote_src=src["is_remote"])
        else:
            copy_res = hosts.all.zos_copy(content=src["src"], dest=dest_path, replace=src["replace"])

        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            if src["replace"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_path
                assert result.get("state") == "file"
                assert result.get("src") is not None
                assert result.get("dest_created") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", binary=False, is_remote=False),
    dict(src="/etc/profile", binary=True, is_remote=False),
    dict(src="/etc/profile", binary=False, is_remote=True),
    dict(src="/etc/profile", binary=True, is_remote=True),
])
def test_copy_file_to_uss_dir(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = get_random_file_name(suffix='/', dir=TMP_DIRECTORY)
    # This name is kept because we copy from /etc/profile file and keep the original file name.
    dest_path = dest + "profile"

    try:

        copy_res = hosts.all.zos_copy(src=src["src"], dest=dest, binary=src["binary"], remote_src=src["is_remote"])

        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for st in stat_res.contacted.values():
            assert st.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
def test_copy_file_to_uss_dir_missing_parents(ansible_zos_module):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest_dir = get_random_file_name(dir=TMP_DIRECTORY)
    dest = "{0}/subdir/profile".format(dest_dir)

    try:
        hosts.all.file(path=dest_dir, state="absent")
        copy_res = hosts.all.zos_copy(src=src, dest=dest)
        stat_res = hosts.all.stat(path=dest)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for st in stat_res.contacted.values():
            assert st.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
def test_copy_local_symlink_to_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_lnk = get_random_file_name(dir=TMP_DIRECTORY)
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    try:
        try:
            os.symlink("/etc/profile", src_lnk)
        except FileExistsError:
            pass
        copy_res = hosts.all.zos_copy(src=src_lnk, dest=dest_path, local_follow=True)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest_path), executable=SHELL_EXECUTABLE
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("state") == "file"
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest_path, state="absent")
        os.remove(src_lnk)


@pytest.mark.uss
def test_copy_local_file_to_uss_file_convert_encoding(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY) + "/profile"
    try:
        copy_res = hosts.all.zos_copy(
            src="/etc/profile",
            dest=dest_path,
            encoding={"from": "ISO8859-1", "to": "IBM-1047"},
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_local_file_to_uss_file_with_absent_remote_tmp_dir(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY) + "/profile"
    try:
        hosts.all.shell(cmd="rm -rf ~/.ansible/tmp")
        copy_res = hosts.all.zos_copy(
            src="/etc/profile",
            dest=dest_path,
            encoding={"from": "ISO8859-1", "to": "IBM-1047"},
        )
        stat_res = hosts.all.stat(path=dest_path)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("state") == "file"
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
def test_copy_inline_content_to_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    dest_path = dest + "inline_copy"

    try:
        copy_res = hosts.all.zos_copy(content="Inline content", dest=dest)
        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
def test_copy_dir_to_existing_uss_dir_not_forced(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    src_file = "{0}profile".format(src_dir)
    dest_dir = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    dest_old_content = "{0}/old_dir".format(dest_dir)

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")
        hosts.all.file(path=dest_old_content, state="directory")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True,
            replace=False
        )

        for result in copy_result.contacted.values():
            assert result.get("msg") is not None
            assert result.get("changed") is False
            assert "Error" in result.get("msg")
            assert "EDC5117I" in result.get("stdout")
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
def test_copy_subdirs_folders_and_validate_recursive_encoding(ansible_zos_module):
    hosts = ansible_zos_module

    # Remote path
    path = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')

    # Remote src path with original files
    src_path = path + "/src"

    # Nested src dirs
    src_dir_one = src_path + "/dir_one"
    src_dir_two = src_dir_one + "/dir_two"
    src_dir_three = src_dir_two + "/dir_three"

    # Nested src IBM-1047 files
    src_file_one = src_path + "/dir_one/one.txt"
    src_file_two = src_dir_one + "/dir_two/two.txt"
    src_file_three = src_dir_two + "/dir_three/three.txt"

    # Remote dest path to encoded files placed
    dest_path = path + "/dest"

    # Nested dest UTF-8 files
    dst_file_one = dest_path + "/dir_one/one.txt"
    dst_file_two = dest_path + "/dir_one/dir_two/two.txt"
    dst_file_three = dest_path + "/dir_one/dir_two//dir_three/three.txt"

    # Strings echo'd to files on USS
    str_one = "This is file one."
    str_two = "This is file two."
    str_three = "This is file three."

    # Hex values for expected results, expected used beause pytest-ansible does not allow for delegate_to
    # and depending on where the `od` runs, you may face big/little endian issues, so using expected utf-8
    str_one_big_endian_hex="""0000000000      5468    6973    2069    7320    6669    6C65    206F    6E65
0000000020      2E0A
0000000022"""

    str_two_big_endian_hex="""0000000000      5468    6973    2069    7320    6669    6C65    2074    776F
0000000020      2E0A
0000000022"""

    str_three_big_endian_hex="""0000000000      5468    6973    2069    7320    6669    6C65    2074    6872
0000000020      6565    2E0A
0000000024"""

    try:
        # Ensure clean slate
        results = hosts.all.file(path=path, state="absent")

        # Create nested directories
        hosts.all.file(path=src_dir_three, state="directory", mode="0755")

        # Touch empty files
        hosts.all.file(path=src_file_one, state = "touch")
        hosts.all.file(path=src_file_two, state = "touch")
        hosts.all.file(path=src_file_three, state = "touch")

        # Echo contents into files (could use zos_lineinfile or zos_copy), echo'ing will
        # result in managed node's locale which currently is IBM-1047
        hosts.all.raw("echo '{0}' > '{1}'".format(str_one, src_file_one))
        hosts.all.raw("echo '{0}' > '{1}'".format(str_two, src_file_two))
        hosts.all.raw("echo '{0}' > '{1}'".format(str_three, src_file_three))

        # Lets stat the deepest nested directory, not necessary to stat all of them
        results = hosts.all.stat(path=src_file_three)
        for result in results.contacted.values():
            assert result.get("stat").get("exists") is True

        # Nested zos_copy from IBM-1047 to UTF-8
        # Testing src ending in / such that the contents of the src directory will be copied
        copy_res = hosts.all.zos_copy(src=src_path+"/", dest=dest_path, encoding={"from": "IBM-1047", "to": "UTF-8"}, remote_src=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

        # File z/OS dest is now UTF-8, dump the hex value and compare it to an
        # expected big-endian version, can't run delegate_to local host so expected
        # value is the work around for now.
        str_one_od_dst = hosts.all.shell(cmd="od -x {0}".format(dst_file_one))
        str_two_od_dst = hosts.all.shell(cmd="od -x {0}".format(dst_file_two))
        str_three_od_dst = hosts.all.shell(cmd="od -x {0}".format(dst_file_three))

        for result in str_one_od_dst.contacted.values():
            assert result.get("stdout") == str_one_big_endian_hex

        for result in str_two_od_dst.contacted.values():
            assert result.get("stdout") == str_two_big_endian_hex

        for result in str_three_od_dst.contacted.values():
            assert result.get("stdout") == str_three_big_endian_hex

    finally:
        hosts.all.file(path=path, state="absent")


@pytest.mark.uss
def test_copy_subdirs_folders_and_validate_recursive_encoding_local(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')

    try:
        source_1 = tempfile.TemporaryDirectory(prefix="level_", suffix="_1")
        source = source_1.name
        source_2 = tempfile.TemporaryDirectory(dir = source, prefix="level_", suffix="_2")
        full_source = source_2.name
        populate_dir(source)
        populate_dir(full_source)
        level_1 = os.path.basename(source)
        level_2 = os.path.basename(full_source)

        copy_res = hosts.all.zos_copy(src=source, dest=dest_path, encoding={"from": "ISO8859-1", "to": "IBM-1047"})

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

        full_outer_file= "{0}/{1}/file3".format(dest_path, level_1)
        full_iner_file= "{0}/{1}/{2}/file3".format(dest_path, level_1, level_2)
        verify_copy_1 = hosts.all.shell(cmd="cat {0}".format(full_outer_file))
        verify_copy_2 = hosts.all.shell(cmd="cat {0}".format(full_iner_file))

        for result in verify_copy_1.contacted.values():
            assert result.get("stdout") == DUMMY_DATA
        for result in verify_copy_2.contacted.values():
            assert result.get("stdout") == DUMMY_DATA
    finally:
        hosts.all.file(name=dest_path, state="absent")
        source_1.cleanup()


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_to_non_existing_dir(ansible_zos_module, copy_directory):
    """
    This test evaluates the behavior of testing copy of a directory when src ends
    with '/' versus only the dir name. Expectation is that when only dir name is provided
    that directory is also created on the remote, when directory name ends with '/'
    this means we only copy that directory contents without creating it on the remote.
    """
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    temp_path = tempfile.mkdtemp()
    src_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(temp_path, src_basename)

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        copy_result = hosts.all.zos_copy(src=source_path, dest=dest_path)

        stat_source_res = hosts.all.stat(path="{0}/{1}".format(dest_path, src_basename))
        if copy_directory:
            stat_file_res = hosts.all.stat(path="{0}/{1}/file3".format(dest_path, src_basename))
        else:
            stat_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_path, src_basename)
            else:
                assert result.get("dest") == dest_path

        for result in stat_source_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(temp_path)


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_to_non_existing_dir(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    src_basename = "source_dir" if copy_directory else "source_dir/"
    src_dir = get_random_file_name(dir=TMP_DIRECTORY) + "/" + src_basename
    src_file = os.path.normpath("{0}/profile".format(src_dir))
    dest_dir = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True
        )

        stat_dir_res = hosts.all.stat(path="{0}/{1}".format(dest_dir, src_basename))
        if copy_directory:
            stat_file_res = hosts.all.stat(path="{0}/{1}/profile".format(dest_dir, src_basename))
        else:
            stat_file_res = hosts.all.stat(path="{0}/profile".format(dest_dir))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_dir, src_basename)
            else:
                assert result.get("dest") == dest_dir

        for result in stat_dir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_to_existing_dir_forced(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    dest_file = "{0}/profile".format(dest_path)

    temp_path = tempfile.mkdtemp()
    source_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(temp_path, source_basename)

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        hosts.all.file(path=dest_path, state="directory")
        hosts.all.file(path=dest_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            replace=True
        )

        stat_source_res = hosts.all.stat(path="{0}/{1}".format(dest_path, source_basename))
        stat_old_file_res = hosts.all.stat(path=dest_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/{1}/file3".format(dest_path, source_basename))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_path, source_basename)
            else:
                assert result.get("dest") == dest_path

        for result in stat_source_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        shutil.rmtree(temp_path)
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_to_existing_dir_forced(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module
    src_basename = get_random_file_name() if copy_directory else get_random_file_name(suffix='/')
    src_parent = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    src_dir = src_parent + src_basename
    src_file = os.path.normpath("{0}/profile".format(src_dir))
    dest_dir = get_random_file_name(dir=TMP_DIRECTORY)
    dest_file = "{0}/file".format(dest_dir)

    try:
        hosts.all.file(path=src_dir, state="directory")
        hosts.all.file(path=src_file, state="touch")

        hosts.all.file(path=dest_dir, state="directory")
        hosts.all.file(path=dest_file, state="touch")

        copy_result = hosts.all.zos_copy(
            src=src_dir,
            dest=dest_dir,
            remote_src=True,
            replace=True
        )

        stat_dir_res = hosts.all.stat(path="{0}/{1}".format(dest_dir, src_basename))
        stat_old_file_res = hosts.all.stat(path=dest_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/{1}/profile".format(dest_dir, src_basename))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/profile".format(dest_dir))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == "{0}/{1}".format(dest_dir, src_basename)
            else:
                assert result.get("dest") == dest_dir

        for result in stat_dir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False

    finally:
        hosts.all.file(path=src_parent, state="absent")
        hosts.all.file(path=dest_dir, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("create_dest", [False, True])
def test_copy_local_nested_dir_to_uss(ansible_zos_module, create_dest):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    source_path = tempfile.mkdtemp()
    if not source_path.endswith("/"):
        source_path = "{0}/".format(source_path)
    subdir_a_path = "{0}subdir_a".format(source_path)
    subdir_b_path = "{0}subdir_b".format(source_path)

    try:
        os.mkdir(subdir_a_path)
        os.mkdir(subdir_b_path)
        populate_dir(subdir_a_path)
        populate_dir(subdir_b_path)

        if create_dest:
            hosts.all.file(path=dest_path, state="directory")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            replace=create_dest
        )

        stat_subdir_a_res = hosts.all.stat(path="{0}/subdir_a".format(dest_path))
        stat_subdir_b_res = hosts.all.stat(path="{0}/subdir_b".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_subdir_a_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
        for result in stat_subdir_b_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(source_path)


@pytest.mark.uss
@pytest.mark.parametrize("create_dest", [False, True])
def test_copy_uss_nested_dir_to_uss(ansible_zos_module, create_dest):
    hosts = ansible_zos_module
    source_path = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    subdir_a_path = "{0}subdir_a".format(source_path)
    subdir_b_path = "{0}subdir_b".format(source_path)

    try:
        hosts.all.file(path=subdir_a_path, state="directory")
        hosts.all.file(path=subdir_b_path, state="directory")
        if create_dest:
            hosts.all.file(path=dest_path, state="directory")

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            remote_src=True,
            replace=create_dest
        )

        stat_subdir_a_res = hosts.all.stat(path="{0}/subdir_a".format(dest_path))
        stat_subdir_b_res = hosts.all.stat(path="{0}/subdir_b".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_path
            assert result.get("src") is not None
            assert result.get("dest_created") is not None
        for result in stat_subdir_a_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
        for result in stat_subdir_b_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

    finally:
        hosts.all.file(path=source_path, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_local_dir_and_change_mode(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module

    source_parent_path = tempfile.mkdtemp()
    source_basename = "source" if copy_directory else "source/"
    source_path = "{0}/{1}".format(source_parent_path, source_basename)
    mode = "0755"

    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    dest_profile = "{0}/profile".format(dest_path)
    dest_subdir = "{0}/{1}".format(dest_path, source_basename)
    if copy_directory:
        dest_old_file = "{0}/file1".format(dest_subdir)
    else:
        dest_old_file = "{0}/file1".format(dest_path)
    dest_mode = "0644"

    try:
        os.mkdir(source_path)
        populate_dir(source_path)

        if copy_directory:
            hosts.all.file(path=dest_subdir, state="directory", mode=dest_mode)
        else:
            hosts.all.file(path=dest_path, state="directory", mode=dest_mode)
        hosts.all.file(path=dest_profile, state="touch", mode=dest_mode)
        hosts.all.file(path=dest_old_file, state="touch", mode=dest_mode)

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            replace=True,
            mode=mode
        )

        stat_dir_res = hosts.all.stat(path=dest_path)
        stat_subdir_res = hosts.all.stat(path=dest_subdir)
        stat_old_file_res = hosts.all.stat(path=dest_profile)
        stat_overwritten_file_res = hosts.all.stat(path=dest_old_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_subdir))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == dest_subdir
            else:
                assert result.get("dest") == dest_path

        for result in stat_dir_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

            if copy_directory:
                assert result.get("stat").get("mode") == dest_mode
            else:
                assert result.get("stat").get("mode") == mode

        for result in stat_subdir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
                assert result.get("stat").get("mode") == mode
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_overwritten_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(source_parent_path)


@pytest.mark.uss
@pytest.mark.parametrize("copy_directory", [False, True])
def test_copy_uss_dir_and_change_mode(ansible_zos_module, copy_directory):
    hosts = ansible_zos_module

    source_basename = get_random_file_name() if copy_directory else get_random_file_name(suffix='/')
    source_path = "/{0}/{1}".format(TMP_DIRECTORY, source_basename)
    mode = "0755"

    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    dest_subdir = "{0}/{1}".format(dest_path, source_basename)
    dest_profile = "{0}/profile".format(dest_path)
    if copy_directory:
        dest_old_file = "{0}/file1".format(dest_subdir)
    else:
        dest_old_file = "{0}/file1".format(dest_path)
    dest_mode = "0644"

    try:
        hosts.all.file(path=source_path, state="directory")
        for i in range(1, 4):
            current_file_path = os.path.normpath("{0}/file{1}".format(source_path, i))
            hosts.all.file(path=current_file_path, state="touch")

        if copy_directory:
            hosts.all.file(path=dest_subdir, state="directory", mode=dest_mode)
        else:
            hosts.all.file(path=dest_path, state="directory", mode=dest_mode)
        hosts.all.file(path=dest_profile, state="touch", mode=dest_mode)
        hosts.all.file(path=dest_old_file, state="touch", mode=dest_mode)

        copy_result = hosts.all.zos_copy(
            src=source_path,
            dest=dest_path,
            replace=True,
            remote_src=True,
            mode=mode
        )

        stat_dir_res = hosts.all.stat(path=dest_path)
        stat_subdir_res = hosts.all.stat(path=dest_subdir)
        stat_old_file_res = hosts.all.stat(path=dest_profile)
        stat_overwritten_file_res = hosts.all.stat(path=dest_old_file)
        if copy_directory:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_subdir))
        else:
            stat_new_file_res = hosts.all.stat(path="{0}/file3".format(dest_path))

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if copy_directory:
                assert result.get("dest") == dest_subdir
            else:
                assert result.get("dest") == dest_path

        for result in stat_dir_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True

            if copy_directory:
                assert result.get("stat").get("mode") == dest_mode
            else:
                assert result.get("stat").get("mode") == mode

        for result in stat_subdir_res.contacted.values():
            if copy_directory:
                assert result.get("stat").get("exists") is True
                assert result.get("stat").get("isdir") is True
                assert result.get("stat").get("mode") == mode
            else:
                assert result.get("stat").get("exists") is False

        for result in stat_old_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == dest_mode

        for result in stat_overwritten_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

        for result in stat_new_file_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is False
            assert result.get("stat").get("mode") == mode

    finally:
        hosts.all.file(path=source_path, state="absent")
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.uss
@pytest.mark.parametrize("backup", [False, True])
def test_backup_uss_file(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest_dir = get_random_file_name(dir=TMP_DIRECTORY)
    dest = f"{dest_dir}/profile"
    backup_name = None

    try:
        hosts.all.file(path=dest_dir, state="directory")
        hosts.all.file(path=dest, state="touch")

        if backup:
            backup_name = get_random_file_name(dir=TMP_DIRECTORY)
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True, backup_name=backup_name)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            backup_name_result = result.get("backup_name")
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("src") is not None
            assert result.get("dest_created") is not None

            if backup:
                assert backup_name_result == backup_name
            else:
                assert backup_name_result is not None

        stat_res = hosts.all.stat(path=backup_name_result)
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True

    finally:
        hosts.all.file(path=dest_dir, state="absent")
        if backup_name_result:
            hosts.all.file(path=backup_name_result, state="absent")

# [Enabler] zos_copy test case failing in SPS test_copy_file_insufficient_read_permission_fails #2366
# @pytest.mark.uss
# def test_copy_file_insufficient_read_permission_fails(ansible_zos_module):
#     hosts = ansible_zos_module
#     src_path = get_random_file_name(dir=TMP_DIRECTORY)
#     dest = "/tmp"
#     try:
#         open(src_path, "w").close()
#         os.chmod(src_path, 0)
#         copy_res = hosts.all.zos_copy(src=src_path, dest=dest)
#         for result in copy_res.contacted.values():
#             assert result.get("msg") is not None
#             assert "read permission" in result.get("msg")
#     finally:
#         if os.path.exists(src_path):
#             os.remove(src_path)


@pytest.mark.uss
@pytest.mark.parametrize("is_remote", [False, True])
def test_copy_non_existent_file_fails(ansible_zos_module, is_remote):
    hosts = ansible_zos_module
    src_path = "/tmp/non_existent_src"
    dest = TMP_DIRECTORY

    copy_res = hosts.all.zos_copy(src=src_path, dest=dest, remote_src=is_remote)
    for result in copy_res.contacted.values():
        assert result.get("msg") is not None
        assert "does not exist" in result.get("msg")


@pytest.mark.uss
@pytest.mark.template
@pytest.mark.parametrize("encoding", ["utf-8", "iso8859-1"])
def test_copy_template_file(ansible_zos_module, encoding):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    temp_dir = tempfile.mkdtemp()

    try:
        temp_template = create_template_file(
            temp_dir,
            use_default_markers=True,
            encoding=encoding
        )
        dest_template = os.path.join(dest_path, os.path.basename(temp_template))

        hosts.all.file(path=dest_path, state="directory")

        # Adding the template vars to each host.
        template_vars = dict(
            var="This should be rendered with 'quotes'.",
            if_var=5,
            array=[1, 2, 3]
        )
        for host in hosts["options"]["inventory_manager"]._inventory.hosts.values():
            host.vars.update(template_vars)

        copy_result = hosts.all.zos_copy(
            src=temp_template,
            dest=dest_path,
            use_template=True,
            template_parameters={
                # This should make sure that we don't get stuff like '&#39' when
                # rendering quotes.
                "autoescape": False
            },
            encoding={
                "from": encoding,
                "to": "IBM-1047"
            }
        )

        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest_template),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_template
            assert cp_res.get("src") is not None
            assert cp_res.get("dest_created") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            # Checking that all markers got replaced.
            assert "{{" not in v_cp.get("stdout")
            assert "{%" not in v_cp.get("stdout")
            # Checking comments didn't get rendered.
            assert "{#" not in v_cp.get("stdout")
            # Checking that the vars where substituted.
            assert template_vars["var"] in v_cp.get("stdout")
            assert "Condition is true." in v_cp.get("stdout")
            assert "Current element: 2" in v_cp.get("stdout")
    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(temp_dir)


@pytest.mark.uss
@pytest.mark.template
def test_copy_template_dir(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)

    # Ensuring there's a traling slash to copy the contents of the directory.
    temp_dir = os.path.normpath(tempfile.mkdtemp())
    temp_dir = "{0}/".format(temp_dir)

    temp_subdir_a = os.path.join(temp_dir, "subdir_a")
    temp_subdir_b = os.path.join(temp_dir, "subdir_b")
    os.makedirs(temp_subdir_a)
    os.makedirs(temp_subdir_b)

    try:
        temp_template_a = create_template_file(temp_subdir_a, use_default_markers=True)
        temp_template_b = create_template_file(temp_subdir_b, use_default_markers=True)
        dest_template_a = os.path.join(
            dest_path,
            "subdir_a",
            os.path.basename(temp_template_a)
        )
        dest_template_b = os.path.join(
            dest_path,
            "subdir_b",
            os.path.basename(temp_template_b)
        )

        hosts.all.file(path=dest_path, state="directory")

        # Adding the template vars to each host.
        template_vars = dict(
            var="This should be rendered",
            if_var=5,
            array=[1, 2, 3]
        )
        for host in hosts["options"]["inventory_manager"]._inventory.hosts.values():
            host.vars.update(template_vars)

        copy_result = hosts.all.zos_copy(
            src=temp_dir,
            dest=dest_path,
            use_template=True,
            replace=True
        )

        verify_copy_a = hosts.all.shell(
            cmd="cat {0}".format(dest_template_a),
            executable=SHELL_EXECUTABLE,
        )
        verify_copy_b = hosts.all.shell(
            cmd="cat {0}".format(dest_template_b),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_path
            assert cp_res.get("src") is not None
            assert cp_res.get("dest_created") is not None
        for v_cp in verify_copy_a.contacted.values():
            assert v_cp.get("rc") == 0
            # Checking that all markers got replaced.
            assert "{{" not in v_cp.get("stdout")
            assert "{%" not in v_cp.get("stdout")
            # Checking comments didn't get rendered.
            assert "{#" not in v_cp.get("stdout")
            # Checking that the vars where substituted.
            assert template_vars["var"] in v_cp.get("stdout")
            assert "Condition is true." in v_cp.get("stdout")
            assert "Current element: 2" in v_cp.get("stdout")
        for v_cp in verify_copy_b.contacted.values():
            assert v_cp.get("rc") == 0
            # Checking that all markers got replaced.
            assert "{{" not in v_cp.get("stdout")
            assert "{%" not in v_cp.get("stdout")
            # Checking comments didn't get rendered.
            assert "{#" not in v_cp.get("stdout")
            # Checking that the vars where substituted.
            assert template_vars["var"] in v_cp.get("stdout")
            assert "Condition is true." in v_cp.get("stdout")
            assert "Current element: 2" in v_cp.get("stdout")
    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(temp_dir)


@pytest.mark.uss
@pytest.mark.template
def test_copy_template_file_with_non_default_markers(ansible_zos_module):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY)
    temp_dir = tempfile.mkdtemp()

    try:
        temp_template = create_template_file(temp_dir, use_default_markers=False)
        dest_template = os.path.join(dest_path, os.path.basename(temp_template))

        hosts.all.file(path=dest_path, state="directory")

        # Adding the template vars to each host.
        template_vars = dict(
            var="This should be rendered",
            if_var=5,
            array=[1, 2, 3]
        )
        for host in hosts["options"]["inventory_manager"]._inventory.hosts.values():
            host.vars.update(template_vars)

        copy_result = hosts.all.zos_copy(
            src=temp_template,
            dest=dest_path,
            use_template=True,
            template_parameters=dict(
                variable_start_string="((",
                variable_end_string="))",
                comment_start_string="#%",
                comment_end_string="%#"
            )
        )

        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest_template),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_template
            assert cp_res.get("src") is not None
            assert cp_res.get("dest_created") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            # Checking that all markers got replaced.
            assert "((" not in v_cp.get("stdout")
            assert "{%" not in v_cp.get("stdout")
            # Checking comments didn't get rendered.
            assert "#%" not in v_cp.get("stdout")
            # Checking that the vars where substituted.
            assert template_vars["var"] in v_cp.get("stdout")
            assert "Condition is true." in v_cp.get("stdout")
            assert "Current element: 2" in v_cp.get("stdout")
    finally:
        hosts.all.file(path=dest_path, state="absent")
        shutil.rmtree(temp_dir)


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.template
def test_copy_template_file_to_dataset(ansible_zos_module):
    hosts = ansible_zos_module
    dest_dataset = get_tmp_ds_name()
    temp_dir = tempfile.mkdtemp()

    try:
        temp_template = create_template_file(temp_dir, use_default_markers=True)

        # Adding the template vars to each host.
        template_vars = dict(
            var="This should be rendered",
            if_var=5,
            array=[1, 2, 3]
        )
        for host in hosts["options"]["inventory_manager"]._inventory.hosts.values():
            host.vars.update(template_vars)

        copy_result = hosts.all.zos_copy(
            src=temp_template,
            dest=dest_dataset,
            use_template=True
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_dataset),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_dataset
            assert cp_res.get("src") is not None
            assert cp_res.get("dest_created") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            # Checking that all markers got replaced.
            assert "{{" not in v_cp.get("stdout")
            assert "{%" not in v_cp.get("stdout")
            # Checking comments didn't get rendered.
            assert "{#" not in v_cp.get("stdout")
            # Checking that the vars where substituted.
            assert template_vars["var"] in v_cp.get("stdout")
            assert "Condition is true." in v_cp.get("stdout")
            assert "Current element: 2" in v_cp.get("stdout")
    finally:
        hosts.all.zos_data_set(name=dest_dataset, state="absent")
        shutil.rmtree(temp_dir)


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.asa
def test_copy_asa_file_to_asa_sequential(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$#@"
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=dest,
            remote_src=False,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.asa
def test_copy_asa_file_to_asa_partitioned(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        dest = get_tmp_ds_name()
        hosts.all.zos_data_set(name=dest, state="absent")
        full_dest = "{0}(TE$@#)".format(dest)

        copy_result = hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=full_dest,
            remote_src=False,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = full_dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == full_dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            print(v_cp)
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.asa
def test_copy_seq_data_set_to_seq_asa(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$#@"
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="seq",
            replace=True
        )

        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$#@"
        hosts.all.zos_data_set(name=dest, state="absent")

        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=src,
            remote_src=False
        )

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.asa
def test_copy_seq_data_set_to_partitioned_asa(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$#@"
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="seq",
            replace=True
        )

        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$#@"
        full_dest = "{0}(MEMB$#@)".format(dest)
        hosts.all.zos_data_set(name=dest, state="absent")

        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=src,
            remote_src=False
        )

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=full_dest,
            remote_src=True,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = full_dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == full_dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.asa
def test_copy_partitioned_data_set_to_seq_asa(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$#@"
        full_src = "{0}(MEM$#@)".format(src)
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="pdse",
            replace=True
        )

        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$#@"
        hosts.all.zos_data_set(name=dest, state="absent")

        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=full_src,
            remote_src=False
        )

        copy_result = hosts.all.zos_copy(
            src=full_src,
            dest=dest,
            remote_src=True,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.asa
def test_copy_partitioned_data_set_to_partitioned_asa(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$#@"
        full_src = "{0}(MEMBER)".format(src)
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="pdse",
            replace=True
        )

        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$#@"
        full_dest = "{0}(MEM$#@)".format(dest)
        hosts.all.zos_data_set(name=dest, state="absent")

        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=full_src,
            remote_src=False
        )

        copy_result = hosts.all.zos_copy(
            src=full_src,
            dest=full_dest,
            remote_src=True,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = full_dest.replace('$', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == full_dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.asa
def test_copy_asa_data_set_to_text_file(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$#@"
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="seq",
            record_format="fba",
            record_length=80,
            block_size=27920,
            replace=True
        )
        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=src,
            remote_src=False
        )

        dest = get_random_file_name(dir=TMP_DIRECTORY)
        dest = f"{dest}$#@"

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            asa_text=True
        )

        verify_copy = hosts.all.shell(
            cmd="cat '{0}'".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            # Since OPUT preserves all blank spaces associated
            # with a record, we strip them before comparing to
            # what we expect.
            for cp_line, content_line in zip(v_cp.get("stdout_lines"), ASA_COPY_CONTENT.splitlines()):
                assert cp_line.rstrip() == content_line
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_remote=False),
    dict(src="/etc/profile", is_remote=True),])
def test_ensure_copy_file_does_not_change_permission_on_dest(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest_path = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    mode = "750"
    other_mode = "744"
    mode_overwrite = "0777"
    full_path = "{0}/profile".format(dest_path)
    try:
        hosts.all.file(path=dest_path, state="directory", mode=mode)
        permissions_before = hosts.all.stat(path=dest_path)
        cp_bef_result = hosts.all.zos_copy(src=src["src"], dest=dest_path, mode=other_mode)
        permissions = hosts.all.stat(path=dest_path)

        for cp_res in cp_bef_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") is not None
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None

        for before in permissions_before.contacted.values():
            permissions_be_copy = before.get("stat").get("mode")

        for after in permissions.contacted.values():
            permissions_af_copy = after.get("stat").get("mode")

        assert permissions_be_copy == permissions_af_copy

        # Extra asserts to ensure change mode rewrite a copy
        af_bef_result = hosts.all.zos_copy(src=src["src"], dest=dest_path, mode=mode_overwrite)

        for cp_res in af_bef_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is False
            assert cp_res.get("dest") is not None
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None

        permissions_overwriten = hosts.all.stat(path = full_path)
        for over in permissions_overwriten.contacted.values():
            assert over.get("stat").get("mode") == mode_overwrite
    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("ds_type, force",[
    ("pds", True),   # Success path, pds locked, force_lock enabled and user authorized
    ("pdse", True),  # Success path, pdse locked, force_lock enabled and user authorized
    ("seq", True),   # Success path, seq locked, force_lock enabled and user authorized
    ("pds", False),  # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
    ("pdse", False), # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
    ("seq", False),  # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
])
def test_copy_dest_lock_wrapper(ansible_zos_module, ds_type, force):
    retries = 0
    max_retries = 5
    success = False

    # Not adding a try/except block here so a real exception can bubble up
    # and stop pytest immediately (if using -x or --stop).
    while retries < max_retries:
        print(f'Trying dest lock for {ds_type}. Expecting success? {force}. Retry: {retries}.')
        result = copy_dest_lock(ansible_zos_module, ds_type, force)

        if result:
            success = True
            break

        retries += 1

    assert success is True


def copy_dest_lock(ansible_zos_module, ds_type, force):
    hosts = ansible_zos_module
    assert_msg = ""

    temp_dir = None
    data_set_1 = get_tmp_ds_name()
    data_set_2 = get_tmp_ds_name(llq_size=4)
    data_set_2 = f"{data_set_2}$#@"
    member_1 = "MEM1"
    if ds_type == "pds" or ds_type == "pdse":
        src_data_set = data_set_1 + "({0})".format(member_1)
        dest_data_set = data_set_2 + "({0})".format(member_1)
    else:
        src_data_set = data_set_1
        dest_data_set = data_set_2

    try:
        ds_creation_result = hosts.all.zos_data_set(
            name=data_set_1,
            state="present",
            type=ds_type,
            replace=True
        )
        for result in ds_creation_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        ds_creation_result = hosts.all.zos_data_set(
            name=data_set_2,
            state="present",
            type=ds_type,
            replace=True
        )
        for result in ds_creation_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        if ds_type == "pds" or ds_type == "pdse":
            member_creation_result = hosts.all.zos_data_set(
                name=src_data_set,
                state="present",
                type="member",
                replace=True
            )
            for result in member_creation_result.contacted.values():
                assert_msg = result.get("stdout", "")
                print(result)
                assert result.get("changed") is True
                assert result.get("failed", False) is False

            member_creation_result = hosts.all.zos_data_set(
                name=dest_data_set,
                state="present",
                type="member",
                replace=True
            )
            for result in member_creation_result.contacted.values():
                assert_msg = result.get("stdout", "")
                print(result)
                assert result.get("changed") is True
                assert result.get("failed", False) is False

        # copy text_in source
        decho_result = hosts.all.shell(cmd="decho \"{0}\" \"{1}\"".format(DUMMY_DATA, src_data_set))
        for result in decho_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        temp_dir = get_random_file_name(dir=TMP_DIRECTORY)
        c_src_result = hosts.all.zos_copy(content=c_pgm, dest=f'{temp_dir}/pdse-lock.c', replace=True)
        for result in c_src_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("msg") is None
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        jcl_result = hosts.all.zos_copy(
            content=call_c_jcl.format(temp_dir, dest_data_set),
            dest=f'{temp_dir}/call_c_pgm.jcl',
            replace=True
        )
        for result in jcl_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("failed", False) is False
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        subproc_result = hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=f"{temp_dir}/")
        for result in subproc_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # submit jcl
        job_result = hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=f"{temp_dir}/")
        for result in job_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # pause to ensure c code acquires lock
        time.sleep(5)
        results = hosts.all.zos_copy(
            src = src_data_set,
            dest = dest_data_set,
            remote_src = True,
            replace=True,
            force=force,
        )

        for result in results.contacted.values():
            assert_msg = result.get("stdout", "")
            if force: #and apf_auth_user:
                print(result)
                assert result.get("changed") == True
                assert result.get("msg") is None
                assert result.get("dest") is not None
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
                # verify that the content is the same
                verify_copy = hosts.all.shell(
                    cmd="dcat \'{0}\'".format(dest_data_set),
                    executable=SHELL_EXECUTABLE,
                )
                for vp_result in verify_copy.contacted.values():
                    verify_copy_2 = hosts.all.shell(
                        cmd="dcat \'{0}\'".format(src_data_set),
                        executable=SHELL_EXECUTABLE,
                    )
                    for vp_result_2 in verify_copy_2.contacted.values():
                        print(vp_result_2)
                        assert vp_result_2.get("stdout") == vp_result.get("stdout")
            elif not force:
                assert result.get("failed") is True
                assert result.get("changed") == False
                assert "because a task is accessing the data set" in result.get("msg")
                assert result.get("rc") is None

        return True
    except AssertionError:
        # Checking for the error code from when the system thinks both data sets
        # are identical.
        if "FSUM8977" in str(assert_msg):
            return False
        else:
            raise
    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        if temp_dir is not None:
            hosts.all.shell(cmd=f'rm -r {temp_dir}')
        # remove pdse
        hosts.all.zos_data_set(name=data_set_1, state="absent")
        hosts.all.zos_data_set(name=data_set_2, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.asa
@pytest.mark.parametrize("ds_type, force",[
    ("pds", True),   # Success path, pds locked, force_lock enabled and user authorized
    ("pdse", True),  # Success path, pdse locked, force_lock enabled and user authorized
    ("seq", True),   # Success path, seq locked, force_lock enabled and user authorized
    ("pds", False),  # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
    ("pdse", False), # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
    ("seq", False),  # Module exits with: Unable to write to dest '{0}' because a task is accessing the data set."
])
def test_copy_dest_lock_wrapper_asa(ansible_zos_module, ds_type, force):
    retries = 0
    max_retries = 5
    success = False

    # Not adding a try/except block here so a real exception can bubble up
    # and stop pytest immediately (if using -x or --stop).
    while retries < max_retries:
        print(f'Trying dest lock for {ds_type}. Expecting success? {force}. Retry: {retries}.')
        result = copy_asa_dest_lock(ansible_zos_module, ds_type, force)

        if result:
            success = True
            break

        retries += 1

    assert success is True


def copy_asa_dest_lock(ansible_zos_module, ds_type, force):
    hosts = ansible_zos_module
    assert_msg = ""

    temp_dir = None
    data_set = get_tmp_ds_name(llq_size=4)
    data_set = f"{data_set}$#@"
    member_name = "MEM1"

    if ds_type == "pds" or ds_type == "pdse":
        dest_data_set = f"{data_set}({member_name})"
    else:
        dest_data_set = data_set

    try:
        ds_creation_result = hosts.all.zos_data_set(
            name=data_set,
            state="present",
            type=ds_type,
            replace=True,
            record_format="fba"
        )
        for result in ds_creation_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        if ds_type == "pds" or ds_type == "pdse":
            member_creation_result = hosts.all.zos_data_set(
                name=dest_data_set,
                state="present",
                type="member",
                replace=True
            )
            for result in member_creation_result.contacted.values():
                assert_msg = result.get("stdout", "")
                print(result)
                assert result.get("changed") is True
                assert result.get("failed", False) is False

        # copy/compile c program and copy jcl to hold data set lock for n seconds in background(&)
        temp_dir = get_random_file_name(dir=TMP_DIRECTORY)
        c_src_result = hosts.all.zos_copy(content=c_pgm, dest=f'{temp_dir}/pdse-lock.c', replace=True)
        for result in c_src_result.contacted.values():
            assert_msg = result.get("stdout", "")
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("msg") is None
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        jcl_result = hosts.all.zos_copy(
            content=call_c_jcl.format(temp_dir, dest_data_set),
            dest=f'{temp_dir}/call_c_pgm.jcl',
            replace=True
        )
        for result in jcl_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False
            assert result.get("msg") is None
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        subproc_result = hosts.all.shell(cmd="xlc -o pdse-lock pdse-lock.c", chdir=f"{temp_dir}/")
        for result in subproc_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # submit jcl
        job_result = hosts.all.shell(cmd="submit call_c_pgm.jcl", chdir=f"{temp_dir}/")
        for result in job_result.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            assert result.get("changed") is True
            assert result.get("failed", False) is False

        # pause to ensure c code acquires lock
        time.sleep(5)

        results = hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=dest_data_set,
            remote_src=False,
            asa_text=True,
            replace=True,
            force=force
        )

        for result in results.contacted.values():
            assert_msg = result.get("stdout", "")
            print(result)
            if force: #and apf_auth_user:
                assert result.get("changed") is True
                assert result.get("msg") is None
                assert result.get("dest") is not None
                assert result.get("dest_created") is not None
                assert result.get("src") is not None

                # We need to escape the data set name because we are using cat, using dcat will
                # bring the trailing empty spaces according to the data set record length.
                # We only need to escape $ character in this notation
                dest_escaped = dest_data_set.replace('$', '\\$')
                verify_copy = hosts.all.shell(
                    cmd="cat \"//'{0}'\"".format(dest_escaped),
                    executable=SHELL_EXECUTABLE,
                )

                for v_cp in verify_copy.contacted.values():
                    assert v_cp.get("rc") == 0
                    assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
            else:
                assert result.get("failed") is True
                assert result.get("changed") is False
                assert "because a task is accessing the data set" in result.get("msg")
                assert result.get("rc") is None

        return True
    except AssertionError:
        # Checking for the error code from when the system thinks both data sets
        # are identical.
        if "FSUM8977" in assert_msg:
            return False
        else:
            raise
    finally:
        # extract pid
        ps_list_res = hosts.all.shell(cmd="ps -e | grep -i 'pdse-lock'")
        # kill process - release lock - this also seems to end the job
        pid = list(ps_list_res.contacted.values())[0].get('stdout').strip().split(' ')[0]
        hosts.all.shell(cmd="kill 9 {0}".format(pid.strip()))
        # clean up c code/object/executable files, jcl
        if temp_dir is not None:
            hosts.all.shell(cmd=f'rm -r {temp_dir}')
        # remove destination data set.
        hosts.all.zos_data_set(name=data_set, state="absent")


@pytest.mark.uss
@pytest.mark.seq
def test_copy_file_record_length_to_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "w") as infile:
        infile.write(DUMMY_DATA)

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            binary=False
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        verify_recl = hosts.all.shell(
            cmd="dls -l {0}".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
        for v_recl in verify_recl.contacted.values():
            assert v_recl.get("rc") == 0
            stdout = v_recl.get("stdout").split()
            assert len(stdout) == 5
            # Verifying the dataset type (sequential).
            assert stdout[1] == "PS"
            # Verifying the record format is Fixed Block.
            assert stdout[2] == "FB"
            # Verifying the record length is 31. The dummy data has 31
            # characters per line.
            assert stdout[3] == "31"
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)


@pytest.mark.uss
@pytest.mark.seq
def test_copy_file_crlf_endings_to_sequential_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "wb") as infile:
        infile.write(DUMMY_DATA_CRLF)

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            binary=False
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        verify_recl = hosts.all.shell(
            cmd="dls -l {0}".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert len(v_cp.get("stdout_lines")) == 2
        for v_recl in verify_recl.contacted.values():
            assert v_recl.get("rc") == 0
            stdout = v_recl.get("stdout").split()
            assert len(stdout) == 5
            # Verifying the dataset type (sequential).
            assert stdout[1] == "PS"
            # Verifying the record format is Fixed Block.
            assert stdout[2] == "FB"
            # Verifying the record length is 19. The dummy data has 19
            # characters per line.
            assert stdout[3] == "19"
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)

@pytest.mark.uss
@pytest.mark.seq
def test_copy_file_crlf_endings_and_pound_to_seq_data_set(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "wb") as infile:
        infile.write(DUMMY_DATA_CRLF_POUND.encode('utf-8'))

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            encoding={
                "from": "UTF-8",
                "to": "IBM-285"
            },
            remote_src=False,
            binary=False
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        verify_recl = hosts.all.shell(
            cmd="dls -l {0}".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            print(cp_res)
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            print(v_cp)
            assert v_cp.get("rc") == 0
            assert len(v_cp.get("stdout_lines")) == 2
        for v_recl in verify_recl.contacted.values():
            assert v_recl.get("rc") == 0
            stdout = v_recl.get("stdout").split()
            assert len(stdout) == 5
            # Verifying the dataset type (sequential).
            assert stdout[1] == "PS"
            # Verifying the record format is Fixed Block.
            assert stdout[2] == "FB"
            # Verifying the record length is 19. The dummy data has 19
            # characters per line.
            assert stdout[3] == "21"
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)

# The following two tests are to address the bugfix for issue #807.
@pytest.mark.uss
@pytest.mark.seq
def test_copy_local_binary_file_without_encoding_conversion(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    fd, src = tempfile.mkstemp()
    os.close(fd)
    with open(src, "wb") as infile:
        infile.write(DUMMY_DATA_BINARY)

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            binary=True
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        os.remove(src)


@pytest.mark.uss
@pytest.mark.seq
def test_copy_remote_binary_file_without_encoding_conversion(ansible_zos_module):
    hosts = ansible_zos_module
    src = get_random_file_name(dir=TMP_DIRECTORY)
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        # Creating a binary file on the remote system through Python
        # to avoid encoding issues if we were to copy a local file
        # or use the shell directly.
        python_cmd = """python3 -c 'with open("{0}", "wb") as f: f.write(b"{1}")'""".format(
            src,
            DUMMY_DATA_BINARY_ESCAPED
        )
        python_result = hosts.all.shell(python_cmd)
        for result in python_result.contacted.values():
            assert result.get("msg") is None or result.get("msg") == ""
            assert result.get("stderr") is None or result.get("stderr") == ""

        # Because the original bug report used a file tagged as 'binary'
        # on z/OS, we'll recreate that use case here.
        hosts.all.shell("chtag -b {0}".format(src))

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            binary=True
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        hosts.all.file(path=src, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], binary=src["binary"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, remote_src=src["is_remote"], binary=src["binary"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=True),
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=True),
])
def test_copy_file_to_empty_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], replace=src["replace"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, remote_src=src["is_remote"], replace=src["replace"])

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", replace=False, is_remote=False),
    dict(src="/etc/profile", replace=True, is_remote=False),
    dict(src="/etc/profile", replace=False, is_remote=True),
    dict(src="/etc/profile", replace=True, is_remote=True),
])
def test_copy_file_to_non_empty_sequential_data_set(ansible_zos_module, src):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="absent")
        hosts.all.zos_copy(content="Inline content", dest=dest)

        copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, remote_src=src["is_remote"], replace=src["replace"])

        for result in copy_result.contacted.values():
            if src["replace"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
def test_copy_ps_to_non_existing_uss_file(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.shell(cmd=f"decho '{DUMMY_DATA_SPECIAL_CHARS}' '{src_ds}' ")
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest, state="absent")
        hosts.all.zos_data_set(name=src_ds, state="absent")


@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.parametrize("replace", [False, True])
def test_copy_ps_to_existing_uss_file(ansible_zos_module, replace):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_random_file_name(dir=TMP_DIRECTORY)

    hosts = ansible_zos_module
    try:
        hosts.all.file(path=dest, state="touch")
        hosts.all.shell(cmd=f"decho 'test line' '{src_ds}' ")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, replace=replace)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if replace:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
    finally:
        hosts.all.shell(cmd=f"drm '{src_ds}' ")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.seq
def test_copy_ps_to_existing_uss_dir(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_random_file_name(dir=TMP_DIRECTORY)
    dest_path = dest + "/" + src_ds

    try:
        hosts.all.shell(cmd=f"decho 'test line' '{src_ds}' " )
        hosts.all.file(path=dest, state="directory")
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)
        verify_copy = hosts.all.shell(
            cmd="cat {0}".format(dest_path), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.file(path=dest, state="absent")


@pytest.mark.seq
def test_copy_ps_to_non_existing_ps(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_tmp_ds_name()

    try:
        hosts.all.shell(cmd=f"decho 'this is a test line' '{src_ds}'")
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is True
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("replace", [False, True])
def test_copy_ps_to_empty_ps(ansible_zos_module, replace):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_tmp_ds_name()

    try:
        hosts.all.shell(cmd=f"decho 'test line ' '{src_ds}'")
        hosts.all.shell(cmd=f"dtouch -tseq '{src_ds}'")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, replace=replace)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("replace", [False, True])
def test_copy_ps_to_non_empty_ps(ansible_zos_module, replace):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_tmp_ds_name()

    try:
        hosts.all.shell(cmd=f"decho 'This is a test ' '{src_ds}' ")
        hosts.all.shell(cmd=f"decho 'This is a test ' '{dest}' ")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, replace=replace)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if replace:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.shell(cmd='rm -r /tmp/c')
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("replace", [False, True])
def test_copy_ps_to_non_empty_ps_with_special_chars(ansible_zos_module, replace):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_tmp_ds_name()

    try:
        hosts.all.shell(cmd=f"decho '{DUMMY_DATA_SPECIAL_CHARS}' '{src_ds}' ")
        hosts.all.shell(cmd=f"decho '{DUMMY_DATA_SPECIAL_CHARS}' '{dest}' ")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, replace=replace)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if replace:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.parametrize("backup", [None, True])
def test_backup_sequential_data_set(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")

        if backup:
            backup_name = get_tmp_ds_name()
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True, backup_name=backup_name)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("backup_name") is not None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
            result_backup_name = result.get("backup_name")
            if backup:
                assert backup_name == result.get("backup_name")

        stat_res = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(result_backup_name),
            executable=SHELL_EXECUTABLE,
        )
        for result in stat_res.contacted.values():
            assert result.get("rc") == 0
            assert "NOT IN CATALOG" not in result.get("stdout")
            assert "NOT IN CATALOG" not in result.get("stderr")

    finally:
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=False, is_remote=False),
    dict(src="Example inline content", is_file=False, binary=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, binary=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, binary=True, is_remote=True),
])
def test_copy_file_to_non_existing_member(ansible_zos_module, src):
    hosts = ansible_zos_module
    data_set = get_tmp_ds_name()
    dest = "{0}(PROFILE)".format(data_set)

    try:
        hosts.all.zos_data_set(
            name=data_set,
            type="pdse",
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
            replace=True
        )

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, binary=src["binary"], remote_src=src["is_remote"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, binary=src["binary"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")


# Test related to issue #774: https://github.com/ansible-collections/ibm_zos_core/issues/774.
@pytest.mark.uss
@pytest.mark.pdse
def test_copy_file_to_non_existing_member_implicit(ansible_zos_module):
    hosts = ansible_zos_module
    dest_data_set = get_tmp_ds_name()
    dest_member = f"{dest_data_set}(PROFILE)"

    try:
        hosts.all.zos_data_set(
            name=dest_data_set,
            type="pdse",
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
            replace=True
        )

        copy_result = hosts.all.zos_copy(
            src="/etc/profile",
            dest=dest_data_set,
            remote_src=True
        )

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest_member),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_member
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=False, is_remote=False),
    dict(src="Example inline content", is_file=False, replace=True, is_remote=False),
    dict(src="/etc/profile", is_file=True, replace=False, is_remote=True),
    dict(src="/etc/profile", is_file=True, replace=True, is_remote=True)
])
def test_copy_file_to_existing_member(ansible_zos_module, src):
    hosts = ansible_zos_module
    data_set = get_tmp_ds_name()
    dest = "{0}(PROFILE)".format(data_set)

    try:
        hosts.all.zos_data_set(
            name=data_set,
            type="pdse",
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
            replace=True
        )
        hosts.all.zos_data_set(name=dest, type="member", state="present")

        if src["is_file"]:
            copy_result = hosts.all.zos_copy(src=src["src"], dest=dest, replace=src["replace"], remote_src=src["is_remote"])
        else:
            copy_result = hosts.all.zos_copy(content=src["src"], dest=dest, replace=src["replace"])

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            if src["replace"]:
                assert cp_res.get("msg") is None
                assert cp_res.get("changed") is True
                assert cp_res.get("dest") == dest
                assert cp_res.get("dest_created") is not None
                assert cp_res.get("src") is not None
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="seq", binary=False),
    dict(type="seq", binary=True),
    dict(type="pds", binary=False),
    dict(type="pds", binary=True),
    dict(type="pdse", binary=False),
    dict(type="pdse", binary=True)
])
def test_copy_data_set_to_non_existing_member(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_data_set = get_tmp_ds_name()
    src = src_data_set if args["type"] == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = get_tmp_ds_name()
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=args["type"])
        if args["type"] != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, type="pdse", replace=True)
        copy_result = hosts.all.zos_copy(src=src, dest=dest, binary=args["binary"], remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="seq", replace=False),
    dict(type="seq", replace=True),
    dict(type="pds", replace=False),
    dict(type="pds", replace=True),
    dict(type="pdse", replace=False),
    dict(type="pdse", replace=True)
])
def test_copy_data_set_to_existing_member(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_data_set = get_tmp_ds_name()
    src = src_data_set if args["type"] == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = get_tmp_ds_name()
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=args["type"])
        if args["type"] != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, type="pdse", replace=True)
        hosts.all.zos_data_set(name=dest, type="member")
        copy_result = hosts.all.zos_copy(src=src, dest=dest, replace=args["replace"], remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            if args["replace"]:
                assert cp_res.get("msg") is None
                assert cp_res.get("changed") is True
                assert cp_res.get("dest") == dest
                assert cp_res.get("dest_created") is not None
                assert cp_res.get("src") is not None
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            if args["replace"]:
                assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("is_remote", [False, True])
def test_copy_file_to_non_existing_pdse(ansible_zos_module, is_remote):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()
    dest_path = "{0}(PROFILE)".format(dest)
    src_file = "/etc/profile"

    try:
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(src=src_file, dest=dest_path, remote_src=is_remote)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest_path),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest_path
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
def test_copy_dir_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    src_dir = get_random_file_name(dir=TMP_DIRECTORY)
    dest = get_tmp_ds_name()

    try:
        hosts.all.file(path=src_dir, state="directory")
        for i in range(5):
            hosts.all.file(path=src_dir + "/" + "file" + str(i), state="touch")

        copy_res = hosts.all.zos_copy(src=src_dir, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is True
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
def test_copy_dir_crlf_endings_to_non_existing_pdse(ansible_zos_module):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()

    temp_path = tempfile.mkdtemp()
    src_basename = "source/"
    source_path = "{0}/{1}".format(temp_path, src_basename)

    try:
        os.mkdir(source_path)
        populate_dir_crlf_endings(source_path)

        copy_res = hosts.all.zos_copy(src=source_path, dest=dest)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}({1})'\"".format(dest, "FILE2"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is True
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert len(result.get("stdout_lines")) == 2
    finally:
        shutil.rmtree(temp_path)
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_dir_to_existing_pdse(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_dir = get_random_file_name(dir=TMP_DIRECTORY)
    dest = get_tmp_ds_name()

    try:
        hosts.all.file(path=src_dir, state="directory")
        for i in range(5):
            hosts.all.file(path=src_dir + "/" + "file" + str(i), state="touch")

        hosts.all.zos_data_set(
            name=dest,
            type=src_type,
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=80,
        )

        copy_result = hosts.all.zos_copy(src=src_dir, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest + "(FILE2)"),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
    finally:
        hosts.all.file(path=src_dir, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["seq", "pds", "pdse"])
def test_copy_data_set_to_non_existing_pdse(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_data_set = get_tmp_ds_name()
    src = src_data_set if src_type == "seq" else "{0}(TEST)".format(src_data_set)
    dest_data_set = get_tmp_ds_name()
    dest = "{0}(MEMBER)".format(dest_data_set)

    try:
        hosts.all.zos_data_set(name=src_data_set, type=src_type)
        if src_type != "seq":
            hosts.all.zos_data_set(name=src, type="member")

        hosts.all.shell(
            "decho 'Records for test' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        hosts.all.zos_data_set(name=dest_data_set, state="absent")
        copy_result = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)

        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(src_type="pds", dest_type="pds"),
    dict(src_type="pds", dest_type="pdse"),
    dict(src_type="pdse", dest_type="pds"),
    dict(src_type="pdse", dest_type="pdse"),
])
def test_copy_pds_to_existing_pds(ansible_zos_module, args):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()
    dest = get_tmp_ds_name()

    try:
        populate_partitioned_data_set(hosts, src, args["src_type"])
        hosts.all.zos_data_set(name=dest, type=args["dest_type"])

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 3
    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.parametrize("is_created", ["true", "false"])
def test_copy_pds_loadlib_member_to_pds_loadlib_member(ansible_zos_module, is_created):
    hosts = ansible_zos_module
    # This dataset and member should be available on any z/OS system.
    mlq_size = 3
    cobol_src_pds = get_tmp_ds_name(mlq_size)
    cobol_src_mem = "HELLOCBL"
    src_lib = get_tmp_ds_name(mlq_size)
    dest_lib = get_tmp_ds_name(mlq_size)
    dest_lib_aliases = get_tmp_ds_name(mlq_size)
    pgm_mem = "HELLO"
    pgm_mem_alias = "ALIAS1"
    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # generate loadlib into src_pds
        generate_executable_ds(hosts, cobol_src_pds, cobol_src_mem, src_lib, pgm_mem, pgm_mem_alias)

        # tests existent/non-existent destination data set code path.
        if not is_created:
            # ensure dest data sets NOT present
            hosts.all.zos_data_set(name=dest_lib, state="absent")
            hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
        else:
            # pre-allocate dest loadlib to copy over without an alias.
            hosts.all.zos_data_set(
                name=dest_lib,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )
            # pre-allocate dest loadlib to copy over with an alias.
            hosts.all.zos_data_set(
                name=dest_lib_aliases,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )

        # zos_copy w an executable:
        copy_res = hosts.all.zos_copy(
            src="{0}({1})".format(src_lib, pgm_mem),
            dest="{0}({1})".format(dest_lib, pgm_mem),
            remote_src=True,
            executable=True,
            aliases=False
        )
        # zos_copy w an executables and its alias:
        copy_res_aliases = hosts.all.zos_copy(
            src="{0}({1})".format(src_lib, pgm_mem),
            dest="{0}({1})".format(dest_lib_aliases, pgm_mem),
            remote_src=True,
            executable=True,
            aliases=True
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib, pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for result in copy_res_aliases.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib_aliases, pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib_aliases),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            mls_alias_str = "ALIAS({0})".format(pgm_mem_alias)
            assert mls_alias_str not in stdout

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, pgm_mem)
            assert expected_mls_str in stdout

        # execute pgms to validate copy
        validate_loadlib_pgm(hosts, steplib=dest_lib, pgm_name=pgm_mem, expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib_aliases, pgm_name=pgm_mem, expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib_aliases, pgm_name=pgm_mem_alias, expected_output_str=COBOL_PRINT_STR)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")

@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.uss
def test_copy_pds_loadlib_member_to_uss_to_loadlib(ansible_zos_module):
    hosts = ansible_zos_module
    mlq_s=3
    cobol_src_pds = get_tmp_ds_name(mlq_s)
    cobol_src_mem = "HELLOCBL"
    src_lib = get_tmp_ds_name(mlq_s)
    dest_lib = get_tmp_ds_name(mlq_s)
    pgm_mem = "HELLO"

    dest_lib_aliases = get_tmp_ds_name(mlq_s)
    pgm_mem_alias = "ALIAS1"

    uss_dest = get_random_file_name(dir=TMP_DIRECTORY)
    try:
        # allocate data sets
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        hosts.all.zos_data_set(
            name=dest_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )
        hosts.all.zos_data_set(
            name=dest_lib_aliases,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # generate loadlib into src_pds
        generate_executable_ds(hosts, cobol_src_pds, cobol_src_mem, src_lib, pgm_mem, pgm_mem_alias)

        # zos_copy an executable to USS file:
        copy_uss_res = hosts.all.zos_copy(
            src="{0}({1})".format(src_lib, pgm_mem),
            dest=uss_dest,
            remote_src=True,
            executable=True,
            replace=True)
        for result in copy_uss_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # run executable on USS
        verify_exe_uss = hosts.all.shell(
            cmd="{0}".format(uss_dest)
        )
        for v_cp_u in verify_exe_uss.contacted.values():
            assert v_cp_u.get("rc") == 0
            assert COBOL_PRINT_STR == v_cp_u.get("stdout").strip()


        # zos_copy from USS file w an executable:
        copy_res = hosts.all.zos_copy(
            src="{0}".format(uss_dest),
            dest="{0}({1})".format(dest_lib, pgm_mem),
            remote_src=True,
            executable=True,
            aliases=False
        )
        # zos_copy from USS file w an executables and its alias:
        copy_res_aliases = hosts.all.zos_copy(
            src="{0}".format(uss_dest),
            dest="{0}({1})".format(dest_lib_aliases, pgm_mem),
            remote_src=True,
            executable=True,
            aliases=True
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib, pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in copy_res_aliases.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib_aliases, pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib_aliases),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            mls_alias_str = "ALIAS({0})".format(pgm_mem_alias)
            assert mls_alias_str not in stdout

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, pgm_mem)
            assert expected_mls_str in stdout

        # execute pgms to validate copy
        validate_loadlib_pgm(hosts, steplib=dest_lib, pgm_name=pgm_mem, expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib, pgm_name=pgm_mem, expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib_aliases, pgm_name=pgm_mem_alias, expected_output_str=COBOL_PRINT_STR)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
        hosts.all.file(name=uss_dest, state="absent")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.parametrize("is_created", ["false", "true"])
def test_copy_pds_loadlib_to_pds_loadlib(ansible_zos_module, is_created):

    hosts = ansible_zos_module
    mlq_size = 3
    cobol_src_pds = get_tmp_ds_name(mlq_size)
    cobol_src_mem = "HELLOCBL"
    cobol_src_mem2 = "HICBL2"
    src_lib = get_tmp_ds_name(mlq_size)
    dest_lib = get_tmp_ds_name(mlq_size)
    dest_lib_aliases = get_tmp_ds_name(mlq_size)
    pgm_mem = "HELLO"
    pgm2_mem = "HELLO2"
    pgm_mem_alias = "ALIAS1"
    pgm2_mem_alias = "ALIAS2"
    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # generate loadlib w 2 members w 1 alias each
        generate_loadlib(
            hosts=hosts,
            cobol_src_pds=cobol_src_pds,
            cobol_src_mems=[cobol_src_mem, cobol_src_mem2],
            loadlib_pds=src_lib,
            loadlib_mems=[pgm_mem, pgm2_mem],
            loadlib_alias_mems=[pgm_mem_alias, pgm2_mem_alias]
        )

        if not is_created:
            # ensure dest data sets absent for this variation of the test case.
            hosts.all.zos_data_set(name=dest_lib, state="absent")
            hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
        else:
            # allocate dest loadlib to copy over without an alias.
            hosts.all.zos_data_set(
                name=dest_lib,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )
            # allocate dest loadlib to copy over with an alias.
            hosts.all.zos_data_set(
                name=dest_lib_aliases,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )

        if not is_created:
            # dest data set does not exist, specify it in dest_dataset param.
            # copy src loadlib to dest library pds w/o aliases
            copy_res = hosts.all.zos_copy(
                src="{0}".format(src_lib),
                dest="{0}".format(dest_lib),
                remote_src=True,
                executable=True,
                aliases=False,
                dest_data_set={
                    'type': "library",
                    'record_format': "u",
                    'record_length': 0,
                    'block_size': 32760,
                    'space_primary': 2,
                    'space_type': "m",
                }
            )
            # copy src loadlib to dest library pds w aliases
            copy_res_aliases = hosts.all.zos_copy(
                src="{0}".format(src_lib),
                dest="{0}".format(dest_lib_aliases),
                remote_src=True,
                executable=True,
                aliases=True,
                dest_data_set={
                    'type': "library",
                    'record_format': "u",
                    'record_length': 0,
                    'block_size': 32760,
                    'space_primary': 2,
                    'space_type': "m",
                }
            )

        else:
            # copy src loadlib to dest library pds w/o aliases
            copy_res = hosts.all.zos_copy(
                src="{0}".format(src_lib),
                dest="{0}".format(dest_lib),
                remote_src=True,
                executable=True,
                aliases=False
            )
            # copy src loadlib to dest library pds w aliases
            copy_res_aliases = hosts.all.zos_copy(
                src="{0}".format(src_lib),
                dest="{0}".format(dest_lib_aliases),
                remote_src=True,
                executable=True,
                aliases=True
            )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for result in copy_res_aliases.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib_aliases)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib_aliases),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            mls_alias_str = "ALIAS({0})".format(pgm_mem_alias)
            mls_alias_str2 = "ALIAS({0})".format(pgm2_mem_alias)
            assert mls_alias_str not in stdout
            assert mls_alias_str2 not in stdout

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, pgm_mem)
            expected_mls_str2 = "{0}   alias  {1}".format(pgm2_mem_alias, pgm2_mem)
            assert expected_mls_str in stdout
            assert expected_mls_str2 in stdout

        # verify pgms remain executable
        pgm_output_map = {
            (dest_lib, pgm_mem, COBOL_PRINT_STR),
            (dest_lib_aliases, pgm_mem, COBOL_PRINT_STR),
            (dest_lib_aliases, pgm_mem_alias, COBOL_PRINT_STR),
            (dest_lib, pgm2_mem, COBOL_PRINT_STR2),
            (dest_lib_aliases, pgm2_mem, COBOL_PRINT_STR2),
            (dest_lib_aliases, pgm2_mem_alias, COBOL_PRINT_STR2)
        }
        for steplib, pgm, output in pgm_output_map:
            validate_loadlib_pgm(hosts, steplib=steplib, pgm_name=pgm, expected_output_str=output)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.parametrize("is_created", [False, True])
def test_copy_local_pds_loadlib_to_pds_loadlib(ansible_zos_module, is_created):
    hosts = ansible_zos_module
    mlq_s = 3
    cobol_src_pds = get_tmp_ds_name(mlq_s)
    cobol_src_mem = "HELLOCBL"
    cobol_src_mem2 = "HICBL2"
    src_lib = get_tmp_ds_name(mlq_s)
    dest_lib = get_tmp_ds_name(mlq_s)
    pgm_mem = "HELLO"
    pgm2_mem = "HELLO2"
    uss_location = get_random_file_name(dir=TMP_DIRECTORY)


    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # copy cobol src
        hosts.all.zos_copy(content=COBOL_SRC.format(COBOL_PRINT_STR), dest='{0}({1})'.format(cobol_src_pds, cobol_src_mem))
        # copy cobol2 src
        hosts.all.zos_copy(content=COBOL_SRC.format(COBOL_PRINT_STR2), dest='{0}({1})'.format(cobol_src_pds, cobol_src_mem2))

        # run link-edit for pgm1
        link_rc = link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mem, src_lib, pgm_mem)
        assert link_rc == 0
        # run link-edit for pgm2
        link_rc = link_loadlib_from_cobol(hosts, cobol_src_pds, cobol_src_mem2, src_lib, pgm2_mem, loadlib_alias_mem="ALIAS2")
        assert link_rc == 0

        # execute pgm to test pgm1
        validate_loadlib_pgm(hosts, steplib=src_lib, pgm_name=pgm_mem, expected_output_str=COBOL_PRINT_STR)

        # fetch loadlib into local
        # Copying the loadlib to USS.
        hosts.all.file(name=uss_location, state='directory')
        hosts.all.shell(
            cmd=f"dcp -X -I \"{src_lib}\" {uss_location}",
            executable=SHELL_EXECUTABLE
        )

        # Copying the remote loadlibs in USS to a local dir.
        # This section ONLY handles ONE host, so if we ever use multiple hosts to
        # test, we will need to update this code.
        remote_user = hosts["options"]["user"]
        # Removing a trailing comma because the framework saves the hosts list as a
        # string instead of a list.
        remote_host = hosts["options"]["inventory"].replace(",", "")

        tmp_folder =  tempfile.TemporaryDirectory(prefix="tmpfetch")
        cmd = [
            "sftp",
            "-r",
            f"{remote_user}@{remote_host}:{uss_location}",
            f"{tmp_folder.name}"
        ]
        with subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE) as sftp_proc:
            result = sftp_proc.stdout.read()

        source_path = os.path.join(tmp_folder.name, os.path.basename(uss_location))

        if not is_created:
            # ensure dest data sets absent for this variation of the test case.
            hosts.all.zos_data_set(name=dest_lib, state="absent")
        else:
            # allocate dest loadlib to copy over without an alias.
            hosts.all.zos_data_set(
                name=dest_lib,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )

        if not is_created:
            # dest data set does not exist, specify it in dest_dataset param.
            # copy src loadlib to dest library pds w/o aliases
            copy_res = hosts.all.zos_copy(
                src=source_path,
                dest="{0}".format(dest_lib),
                executable=True,
                aliases=False,
                dest_data_set={
                    'type': "pdse",
                    'record_format': "u",
                    'record_length': 0,
                    'block_size': 32760,
                    'space_primary': 2,
                    'space_type': "m",
                }
            )
        else:
            # copy src loadlib to dest library pds w/o aliases
            copy_res = hosts.all.zos_copy(
                src=source_path,
                dest="{0}".format(dest_lib),
                executable=True,
                aliases=False
            )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
        # verify pgms remain executable
        pgm_output_map = {
            (dest_lib, pgm_mem, COBOL_PRINT_STR),
            (dest_lib, pgm2_mem, COBOL_PRINT_STR2),
        }
        for steplib, pgm, output in pgm_output_map:
            validate_loadlib_pgm(hosts, steplib=steplib, pgm_name=pgm, expected_output_str=output)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.file(name=uss_location, state="absent")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.uss
def test_copy_pds_loadlib_to_uss_to_pds_loadlib(ansible_zos_module):

    hosts = ansible_zos_module
    mlq_s=3
    cobol_src_pds = get_tmp_ds_name(mlq_s)
    cobol_src_mem = "HELLOCBL"
    cobol_src_mem2 = "HICBL2"
    src_lib = get_tmp_ds_name(mlq_s)
    dest_lib = get_tmp_ds_name(mlq_s)
    dest_lib_aliases = get_tmp_ds_name(mlq_s)
    pgm_mem = "HELLO"
    pgm2_mem = "HELLO2"
    pgm_mem_alias = "ALIAS1"
    pgm2_mem_alias = "ALIAS2"

    # note - aliases for executables  are implicitly copied over (by module design) for USS targets.
    uss_dir_path = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # generate loadlib w 2 members w 1 alias each
        generate_loadlib(
            hosts=hosts,
            cobol_src_pds=cobol_src_pds,
            cobol_src_mems=[cobol_src_mem, cobol_src_mem2],
            loadlib_pds=src_lib,
            loadlib_mems=[pgm_mem, pgm2_mem],
            loadlib_alias_mems=[pgm_mem_alias, pgm2_mem_alias]
        )

        # make dest USS dir
        hosts.all.file(path=uss_dir_path, state="directory")
        # allocate dest loadlib to copy over without an alias.
        hosts.all.zos_data_set(
            name=dest_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )
        # allocate dest loadlib to copy over with an alias.
        hosts.all.zos_data_set(
            name=dest_lib_aliases,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # copy src lib to USS dir
        copy_res_uss = hosts.all.zos_copy(
            src="{0}".format(src_lib),
            dest="{0}".format(uss_dir_path),
            remote_src=True,
            executable=True,
        )
        for result in copy_res_uss.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(uss_dir_path)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # inspect USS dir contents
        verify_exe_uss_ls = hosts.all.shell(
            cmd='ls {0}/{1}'.format(uss_dir_path, src_lib.upper())
        )
        for v_exe_u_ls in verify_exe_uss_ls.contacted.values():
            assert v_exe_u_ls.get("rc") == 0
            assert "{0}\n{1}".format(src_lib.upper(), pgm_mem)

        # run executables on USS
        verify_exe_uss = hosts.all.shell(
            cmd="{0}/{1}/{2}".format(uss_dir_path, src_lib.upper(), pgm_mem.lower())
        )
        for v_cp_u in verify_exe_uss.contacted.values():
            assert v_cp_u.get("rc") == 0
            assert v_cp_u.get("stdout").strip() == COBOL_PRINT_STR

        verify_exe_uss = hosts.all.shell(
            cmd="{0}/{1}/{2}".format(uss_dir_path, src_lib.upper(), pgm2_mem.lower())
        )
        for v_cp_u in verify_exe_uss.contacted.values():
            assert v_cp_u.get("rc") == 0
            assert v_cp_u.get("stdout").strip() == COBOL_PRINT_STR2


        # copy USS dir to dest library pds w/o aliases
        copy_res = hosts.all.zos_copy(
            src="{0}/{1}".format(uss_dir_path, src_lib.upper()),
            dest="{0}".format(dest_lib),
            remote_src=True,
            executable=True,
            aliases=False
        )
        # copy USS dir to dest library pds w aliases
        copy_res_aliases = hosts.all.zos_copy(
            src="{0}/{1}".format(uss_dir_path, src_lib.upper()),
            dest="{0}".format(dest_lib_aliases),
            remote_src=True,
            executable=True,
            aliases=True
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for result in copy_res_aliases.contacted.values():
            print(result)
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib_aliases)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib_aliases),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            mls_alias_str = "ALIAS({0})".format(pgm_mem_alias)
            mls_alias_str2 = "ALIAS({0})".format(pgm2_mem_alias)
            assert mls_alias_str not in stdout
            assert mls_alias_str2 not in stdout

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, pgm_mem)
            expected_mls_str2 = "{0}   alias  {1}".format(pgm2_mem_alias, pgm2_mem)
            assert expected_mls_str in stdout
            assert expected_mls_str2 in stdout

        # verify pgms remain executable
        pgm_output_map = {
            (dest_lib, pgm_mem, COBOL_PRINT_STR),
            (dest_lib_aliases, pgm_mem, COBOL_PRINT_STR),
            (dest_lib_aliases, pgm_mem_alias, COBOL_PRINT_STR),
            (dest_lib, pgm2_mem, COBOL_PRINT_STR2),
            (dest_lib_aliases, pgm2_mem, COBOL_PRINT_STR2),
            (dest_lib_aliases, pgm2_mem_alias, COBOL_PRINT_STR2)
        }

        for steplib, pgm, output in pgm_output_map:
            validate_loadlib_pgm(hosts, steplib=steplib, pgm_name=pgm, expected_output_str=output)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
        hosts.all.file(path=uss_dir_path, state="absent")

#Special case to call a program
@pytest.mark.uss
def test_copy_executables_uss_to_uss(ansible_zos_module):
    hosts= ansible_zos_module
    c_dir = get_random_file_name(dir=TMP_DIRECTORY)
    src= f"{c_dir}/hello_world.c"
    src_jcl_call= f"{c_dir}/call_hw_pgm.jcl"
    dest_uss=f"{c_dir}/hello_world_2"
    try:
        generate_executable_uss(hosts, c_dir, src, src_jcl_call)
        copy_uss_res = hosts.all.zos_copy(
            src=f"{c_dir}/hello_world",
            dest=dest_uss,
            remote_src=True,
            executable=True,
            replace=True
        )
        verify_exe_dst = hosts.all.shell(cmd=f"{c_dir}/hello_world_2")
        for result in copy_uss_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for res in verify_exe_dst.contacted.values():
            assert res.get("rc") == 0
            stdout = res.get("stdout")
            assert  "Hello World" in str(stdout)
    finally:
        hosts.all.shell(cmd=f'rm -r {c_dir}')


@pytest.mark.pdse
@pytest.mark.uss
@pytest.mark.parametrize("is_created", ["true", "false"])
def test_copy_executables_uss_to_member(ansible_zos_module, is_created):
    hosts= ansible_zos_module
    c_dir = get_random_file_name(dir=TMP_DIRECTORY)
    src= f"{c_dir}/hello_world.c"
    mlq_size = 3
    src_jcl_call= f"{c_dir}/call_hw_pgm.jcl"
    dest = get_tmp_ds_name(mlq_size)
    member = "HELLOSRC"
    try:
        generate_executable_uss(hosts, c_dir, src, src_jcl_call)
        if is_created:
            hosts.all.zos_data_set(
                name=dest,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )
        copy_uss_to_mvs_res = hosts.all.zos_copy(
            src=f"{c_dir}/hello_world",
            dest="{0}({1})".format(dest, member),
            remote_src=True,
            executable=True,
            replace=True
        )
        cmd = "mvscmd --pgm={0}  --steplib={1} --sysprint=* --stderr=* --stdout=*"
        exec_res = hosts.all.shell(
            cmd=cmd.format(member, dest)
        )
        for result in copy_uss_to_mvs_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for res in exec_res.contacted.values():
            assert res.get("rc") == 0
            stdout = res.get("stdout")
            assert  "Hello World" in str(stdout)
    finally:
        hosts.all.shell(cmd=f'rm -r {c_dir}')
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_pds_member_with_system_symbol(ansible_zos_module):
    """This test is for bug #543 in GitHub. In some versions of ZOAU,
    datasets.listing can't handle system symbols in volume names and
    therefore fails to get details from a dataset.

    Note: `listcat ent('SYS1.SAMPLIB') all` will display 'volser = ******'
    and `D SYMBOLS` will show you that `&SYSR2. = "RES80A"` where
    the symbols for this volume correspond to volume `RES80A`
    """
    hosts = ansible_zos_module
    # The volume for this dataset should use a system symbol.
    # This dataset and member should be available on any z/OS system.
    src = "SYS1.SAMPLIB(IZUPRM00)"
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(
            name=dest,
            state="present",
            type="pdse",
            replace=True
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 1

    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_multiple_data_set_members(ansible_zos_module):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()
    src_wildcard = "{0}(ABC*)".format(src)

    dest = get_tmp_ds_name()
    member_list = ["MEMBER1", "ABCXYZ", "ABCASD"]
    ds_list = ["{0}({1})".format(src, member) for member in member_list]

    try:
        hosts.all.zos_data_set(name=src, type="pds")
        hosts.all.zos_data_set(name=dest, type="pds")

        for member in ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
                executable=SHELL_EXECUTABLE
            )

        copy_res = hosts.all.zos_copy(src=src_wildcard, dest=dest, remote_src=True)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 2

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
def test_copy_multiple_data_set_members_in_loop(ansible_zos_module):
    """
    This test case was included in case the module is called inside a loop,
    issue was discovered in https://github.com/ansible-collections/ibm_zos_core/issues/560.
    """
    hosts = ansible_zos_module
    src = get_tmp_ds_name()

    dest = get_tmp_ds_name()
    member_list = ["MEMBER1", "ABCXYZ", "ABCASD"]
    src_ds_list = ["{0}({1})".format(src, member) for member in member_list]
    dest_ds_list = ["{0}({1})".format(dest, member) for member in member_list]

    try:
        hosts.all.zos_data_set(name=src, type="pds")
        hosts.all.zos_data_set(name=dest, type="pds")

        for src_member in src_ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, src_member),
                executable=SHELL_EXECUTABLE
            )

        for src_member, dest_member in zip(src_ds_list, dest_ds_list):
            copy_res = hosts.all.zos_copy(src=src_member, dest=dest_member, remote_src=True)
            for result in copy_res.contacted.values():
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_member
                assert result.get("dest_created") is not None
                assert result.get("src") is not None

        verify_copy = hosts.all.shell(
            cmd="mls {0}".format(dest),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            assert len(stdout.splitlines()) == 3

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("ds_type", ["pds", "pdse"])
def test_copy_member_to_non_existing_uss_file(ansible_zos_module, ds_type):
    hosts = ansible_zos_module
    data_set = get_tmp_ds_name()
    src = "{0}(MEMBER)".format(data_set)
    dest = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.file(path=dest, state="absent")
        hosts.all.zos_data_set(name=data_set, state="present", type=ds_type)
        hosts.all.shell(
            cmd="decho 'Record for data set' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(path=data_set, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(ds_type="pds", replace=False),
    dict(ds_type="pds", replace=True),
    dict(ds_type="pdse", replace=False),
    dict(ds_type="pdse", replace=True)
])
def test_copy_member_to_existing_uss_file(ansible_zos_module, args):
    hosts = ansible_zos_module
    data_set = get_tmp_ds_name()
    src = "{0}(MEMBER)".format(data_set)
    dest = get_random_file_name(dir=TMP_DIRECTORY)

    try:
        hosts.all.file(path=dest, state="touch")
        hosts.all.zos_data_set(name=data_set, state="present", type=args["ds_type"])
        hosts.all.shell(
            cmd="decho 'Record for data set' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True, replace=args["replace"])
        stat_res = hosts.all.stat(path=dest)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if args["replace"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            if args["replace"]:
                assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=data_set, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.aliases
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_pdse_to_uss_dir(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest = get_random_file_name(dir=TMP_DIRECTORY)
    dest_path = "{0}/{1}".format(dest, src_ds)

    try:
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        members = ["MEMBER1", "MEMBER2", "MEMBER3"]
        ds_list = ["{0}({1})".format(src_ds, member) for member in members]
        for member in ds_list:
            hosts.all.shell(
                cmd="decho '{0}' '{1}'".format(DUMMY_DATA, member),
                executable=SHELL_EXECUTABLE
            )

        hosts.all.file(path=dest_path, state="directory")

        # ensure aliases:True errors out for non-text member copy
        copy_aliases_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, aliases=True)
        for result in copy_aliases_res.contacted.values():
            error_msg = "Alias support for text-based data sets is not available"
            assert result.get("failed") is True
            assert result.get("changed") is False
            assert error_msg in result.get("msg")

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
            assert result.get("stat").get("isdir") is True
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.aliases
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_member_to_uss_dir(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    src = "{0}(MEMBER)".format(src_ds)
    dest = get_random_file_name(dir=TMP_DIRECTORY, suffix='/')
    dest_path = f"{dest}MEMBER"

    try:
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        hosts.all.shell(
            cmd="decho '{0}' '{1}'".format(DUMMY_DATA, src),
            executable=SHELL_EXECUTABLE
        )

        # ensure aliases:True errors out for non-text member copy
        copy_aliases_res = hosts.all.zos_copy(src=src_ds, dest=dest, remote_src=True, aliases=True)
        for result in copy_aliases_res.contacted.values():
            error_msg = "Alias support for text-based data sets is not available"
            assert result.get("failed") is True
            assert result.get("changed") is False
            assert error_msg in result.get("msg")

        hosts.all.file(path=dest, state="directory")
        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        stat_res = hosts.all.stat(path=dest_path)
        verify_copy = hosts.all.shell(
            cmd="head {0}".format(dest_path),
            executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in stat_res.contacted.values():
            assert result.get("stat").get("exists") is True
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        # hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.file(path=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["pds", "pdse"])
def test_copy_member_to_non_existing_seq_data_set(ansible_zos_module, src_type):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    src = "{0}(MEMBER)".format(src_ds)
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, state="absent")
        hosts.all.zos_data_set(name=src_ds, type=src_type, state="present")
        hosts.all.shell(
            cmd="decho 'A record' '{0}'".format(src),
            executable=SHELL_EXECUTABLE
        )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is True
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="pds", replace=False),
    dict(type="pds", replace=True),
    dict(type="pdse", replace=False),
    dict(type="pdse", replace=True),
])
def test_copy_member_to_existing_seq_data_set(ansible_zos_module, args):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    src = "{0}(MEMBER)".format(src_ds)
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present", replace=True)
        hosts.all.zos_data_set(name=src_ds, type=args["type"], state="present")

        for data_set in [src, dest]:
            hosts.all.shell(
                cmd="decho 'A record' '{0}'".format(data_set),
                executable=SHELL_EXECUTABLE
            )

        copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=args["replace"], remote_src=True)
        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest), executable=SHELL_EXECUTABLE
        )

        for result in copy_res.contacted.values():
            if args["replace"]:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            if args["replace"]:
                assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.uss
@pytest.mark.pdse
@pytest.mark.parametrize("dest_type", ["pds", "pdse"])
def test_copy_file_to_member_convert_encoding(ansible_zos_module, dest_type):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = get_tmp_ds_name()

    try:
        hosts.all.zos_data_set(
            type=dest_type,
            space_primary=5,
            space_type="m",
            record_format="fba",
            record_length=25,
        )

        copy_res = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=False,
            encoding={
                "from": "UTF-8",
                "to": "IBM-1047"
            },
        )

        verify_copy = hosts.all.shell(
            cmd="head \"//'{0}'\"".format(dest + "(PROFILE)"),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("rc") == 0
            assert result.get("stdout") != ""
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
@pytest.mark.parametrize("args", [
    dict(type="pds", backup=False),
    dict(type="pds", backup=True),
    dict(type="pdse", backup=False),
    dict(type="pdse", backup=True),
])
def test_backup_pds(ansible_zos_module, args):
    hosts = ansible_zos_module
    src = tempfile.mkdtemp()
    dest = get_tmp_ds_name()
    members = ["FILE1", "FILE2", "FILE3", "FILE4", "FILE5"]
    backup_name = None

    try:
        populate_dir(src)
        populate_partitioned_data_set(hosts, dest, args["type"], members)

        if args["backup"]:
            backup_name = get_tmp_ds_name()
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True, backup_name=backup_name)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, replace=True, backup=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

            result_backup_name = result.get("backup_name")
            assert result_backup_name is not None
            if args["backup"]:
                assert result_backup_name == backup_name

        verify_copy = get_listcat_information(hosts, result_backup_name, args["type"])

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output

    finally:
        shutil.rmtree(src)
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup_name:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.seq
@pytest.mark.pdse
@pytest.mark.parametrize("src_type", ["seq", "pds", "pdse"])
def test_copy_data_set_to_volume(ansible_zos_module, volumes_on_systems, src_type):
    hosts = ansible_zos_module
    source = get_tmp_ds_name()
    source_member = f"{source}(MEM)"
    dest = get_tmp_ds_name()
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()

    if volume_1 == "SCR03":
        volume = volumes.get_available_vol()
        volumes.free_vol(volume_1)
        volume_1 = volume

    try:
        hosts.all.zos_data_set(name=source, type=src_type, state='present')
        if src_type != "seq":
            hosts.all.zos_data_set(name=source_member, type="member", state='present')

        copy_res = hosts.all.zos_copy(
            src=source,
            dest=dest,
            remote_src=True,
            volume=volume_1
        )

        for cp in copy_res.contacted.values():
            assert cp.get('msg') is None
            assert cp.get('changed') is True
            assert cp.get('dest') == dest
            assert cp.get("dest_created") is not None
            assert cp.get("src") is not None

        check_vol = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for cv in check_vol.contacted.values():
            assert cv.get('rc') == 0
            assert volume_1 in cv.get('stdout')
    finally:
        hosts.all.zos_data_set(name=source, state='absent')
        hosts.all.zos_data_set(name=dest, state='absent')


@pytest.mark.vsam
def test_copy_ksds_to_non_existing_ksds(ansible_zos_module):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest_ds = get_tmp_ds_name()
    create_vsam_data_set(hosts, src_ds, "ksds", add_data=True, key_length=12, key_offset=0)

    try:
        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest_ds, remote_src=True)
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest_ds
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
    finally:
        hosts.all.zos_data_set(
            batch=[
                {"name": dest_ds, "state": "absent"},
                {"name": src_ds, "state": "absent"}
            ]
        )

@pytest.mark.vsam
@pytest.mark.parametrize("replace", [False, True])
def test_copy_ksds_to_existing_ksds(ansible_zos_module, replace):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    dest_ds = get_tmp_ds_name()

    try:
        create_vsam_data_set(hosts, src_ds, "ksds", add_data=True, key_length=12, key_offset=0)
        create_vsam_data_set(hosts, dest_ds, "ksds", add_data=True, key_length=12, key_offset=0)

        copy_res = hosts.all.zos_copy(src=src_ds, dest=dest_ds, remote_src=True, replace=replace)
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            if replace:
                assert result.get("msg") is None
                assert result.get("changed") is True
                assert result.get("dest") == dest_ds
                assert result.get("dest_created") is not None
                assert result.get("src") is not None
            else:
                assert result.get("msg") is not None
                assert result.get("changed") is False

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
    finally:
        hosts.all.zos_data_set(name=src_ds, state="absent")
        hosts.all.zos_data_set(name=dest_ds, state="absent")


@pytest.mark.vsam
@pytest.mark.parametrize("backup", [False, True])
def test_backup_ksds(ansible_zos_module, backup):
    hosts = ansible_zos_module
    src = get_tmp_ds_name()
    dest = get_tmp_ds_name()
    backup_name = None

    try:
        create_vsam_data_set(hosts, src, "ksds", add_data=True, key_length=12, key_offset=0)
        create_vsam_data_set(hosts, dest, "ksds", add_data=True, key_length=12, key_offset=0)

        if backup:
            backup_name = get_tmp_ds_name()
            copy_res = hosts.all.zos_copy(src=src, dest=dest, backup=True, backup_name=backup_name, remote_src=True, replace=True)
        else:
            copy_res = hosts.all.zos_copy(src=src, dest=dest, backup=True, remote_src=True, replace=True)

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
            result_backup_name = result.get("backup_name")
            assert result_backup_name is not None

            if backup:
                assert result_backup_name == backup_name

        verify_copy = get_listcat_information(hosts, dest, "ksds")
        verify_backup = get_listcat_information(hosts, result_backup_name, "ksds")

        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
        for result in verify_backup.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)

    finally:
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")
        if backup_name:
            hosts.all.zos_data_set(name=backup_name, state="absent")


@pytest.mark.vsam
def test_copy_ksds_to_volume(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    src_ds = get_tmp_ds_name()
    create_vsam_data_set(hosts, src_ds, "ksds", add_data=True, key_length=12, key_offset=0)
    dest_ds = get_tmp_ds_name()
    volumes = Volume_Handler(volumes_on_systems)
    volume_1 = volumes.get_available_vol()

    try:
        copy_res = hosts.all.zos_copy(
            src=src_ds,
            dest=dest_ds,
            remote_src=True,
            volume=volume_1
        )
        verify_copy = get_listcat_information(hosts, dest_ds, "ksds")

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            assert result.get("dd_names") is not None
            dd_names = result.get("dd_names")
            assert len(dd_names) > 0
            output = "\n".join(dd_names[0]["content"])
            assert "IN-CAT" in output
            assert re.search(r"\bINDEXED\b", output)
            assert re.search(r"\b{0}\b".format(volume_1), output)
    finally:
        hosts.all.zos_data_set(
            batch=[
                {"name": dest_ds, "state": "absent"},
                {"name": src_ds, "state": "absent"}
            ]
        )


def test_dest_data_set_parameters(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = get_tmp_ds_name()
    volumes = Volume_Handler(volumes_on_systems)
    volume = volumes.get_available_vol()
    space_primary = 3
    space_secondary = 2
    space_type = "k"
    record_format = "vb"
    record_length = 100
    block_size = 21000

    try:
        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            volume=volume,
            dest_data_set=dict(
                type="seq",
                space_primary=space_primary,
                space_secondary=space_secondary,
                space_type=space_type,
                record_format=record_format,
                record_length=record_length,
                block_size=block_size
            )
        )

        verify_copy = hosts.all.shell(
            cmd="tsocmd \"LISTDS '{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )

        for result in copy_result.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == dest
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        for result in verify_copy.contacted.values():
            # The tsocmd returns 5 lines like this:
            # USER.TEST.DEST
            # --RECFM-LRECL-BLKSIZE-DSORG
            #   VB    100   21000   PS
            # --VOLUMES--
            #   000000
            assert result.get("rc") == 0
            output_lines = result.get("stdout").split("\n")
            assert len(output_lines) == 5
            data_set_attributes = output_lines[2].strip().split()
            assert len(data_set_attributes) == 4
            assert data_set_attributes[0] == record_format.upper()
            assert data_set_attributes[1] == str(record_length)
            assert data_set_attributes[2] == str(block_size)
            assert data_set_attributes[3] == "PS"
            assert volume in output_lines[4]
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")


def test_ensure_tmp_cleanup(ansible_zos_module):
    hosts = ansible_zos_module
    src = "/etc/profile"
    dest = "/tmp"
    dest_path = "/tmp/profile"

    temp_files_patterns = [
        re.compile(r"\bansible-zos-copy-payload"),
        re.compile(r"\bconverted"),
        re.compile(r"\bansible-zos-copy-data-set-dump")
    ]

    try:
        copy_res = hosts.all.zos_copy(src=src, dest=dest)
        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        stat_dir = hosts.all.shell(
            cmd="ls",
            executable=SHELL_EXECUTABLE,
            chdir="/tmp/"
        )

        for result in stat_dir.contacted.values():
            tmp_files = result.get("stdout")
            for pattern in temp_files_patterns:
                assert not pattern.search(tmp_files)

    finally:
        hosts.all.file(path=dest_path, state="absent")


@pytest.mark.vsam
@pytest.mark.parametrize("replace", [False, True])
def test_copy_uss_file_to_existing_sequential_data_set_twice_with_tmphlq_option(ansible_zos_module, replace):
    hosts = ansible_zos_module
    dest = get_tmp_ds_name()
    src_file = "/etc/profile"
    tmphlq = "TMPHLQ"
    try:
        hosts.all.zos_data_set(name=dest, type="seq", state="present")
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest, remote_src=True, replace=replace)
        copy_result = hosts.all.zos_copy(src=src_file, dest=dest, remote_src=True, backup=True, tmp_hlq=tmphlq, replace=replace)

        verify_copy = None
        if replace:
            verify_copy = hosts.all.shell(
                cmd="cat \"//'{0}'\" > /dev/null 2>/dev/null".format(dest),
                executable=SHELL_EXECUTABLE,
            )

        for cp_res in copy_result.contacted.values():
            if replace:
                assert cp_res.get("msg") is None
                assert cp_res.get("backup_name")[:6] == tmphlq
                assert cp_res.get("changed") is True
                assert cp_res.get("dest") is not None
                assert cp_res.get("dest_created") is not None
                assert cp_res.get("src") is not None
            else:
                assert cp_res.get("msg") is not None
                assert cp_res.get("changed") is False
        if replace:
            for v_cp in verify_copy.contacted.values():
                assert v_cp.get("rc") == 0
    finally:
        hosts.all.zos_data_set(name=dest, state="absent")



@pytest.mark.parametrize("options", [
    dict(src="/etc/profile",
         replace=True, is_remote=False, verbosity="-vvvvv", verbosity_level=5),
    dict(src="/etc/profile", replace=True,
         is_remote=False, verbosity="-vvvv", verbosity_level=4),
    dict(src="/etc/profile",
         replace=True, is_remote=False, verbosity="", verbosity_level=0),
])
def test_display_verbosity_in_zos_copy_plugin(ansible_zos_module, options):
    """Test the display verbosity, ensure it matches the verbosity_level.
     This test requires access to verbosity and pytest-ansbile provides no
     reasonable handle for this so for now subprocess is used. This test
     results in no actual copy happening, the interest is in the verbosity"""

    try:
        hosts = ansible_zos_module
        user = hosts["options"]["user"]
        # Optionally hosts["options"]["inventory_manager"].list_hosts()[0]
        node = hosts["options"]["inventory"].rstrip(',')
        python_path = hosts["options"]["ansible_python_path"]

        dest_path = get_random_file_name(dir=TMP_DIRECTORY)
        # This is an adhoc command, because there was no
        cmd = "ansible all -i " + str(node) + ", -u " + user + " -m ibm.ibm_zos_core.zos_copy -a \"src=" + options["src"] + " dest=" + dest_path + " is_remote=" + str(
            options["is_remote"]) + " encoding={{enc}} \" -e '{\"enc\":{\"from\": \"ISO8859-1\", \"to\": \"IBM-1047\"}}' -e \"ansible_python_interpreter=" + python_path + "\" " + options["verbosity"] + ""

        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
        output = result.read().decode()

        if options["verbosity_level"] != 0:
            assert ("play context verbosity: "+ str(options["verbosity_level"])+"" in output)
        else:
            assert ("play context verbosity:" not in output)

    finally:
        hosts.all.file(path=dest_path, state="absent")

# All gds test cases is commented out due to issues with GDS #2280
# @pytest.mark.parametrize("generation", ["0", "+1"])
# def test_copy_seq_gds_inexistent_src(ansible_zos_module, generation):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_data_set}")

#         copy_results = hosts.all.zos_copy(
#             src=f"{src_data_set}({generation})",
#             dest=dest_data_set,
#             remote_src=True
#         )

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is not None
#             assert cp_res.get("changed") is False
#             assert cp_res.get("failed") is True
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")


# def test_copy_seq_gds_to_data_set(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=f"{src_data_set}(0)",
#             dest=dest_data_set,
#             remote_src=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}" """)

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert cp_res.get("dest") == dest_data_set
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_data_set_to_new_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=f"{dest_data_set}(+1)",
#             remote_src=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_uss_file_to_new_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_file = "/etc/profile"
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")

#         copy_results = hosts.all.zos_copy(
#             src=src_file,
#             dest=f"{dest_data_set}(+1)",
#             remote_src=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_pds_to_new_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         member_src = f"{src_data_set}(MEMBER)"
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tPDS {src_data_set}")
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{member_src}" """)

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=f"{dest_data_set}(+1)",
#             remote_src=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""mls "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_data_set_to_previous_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)

#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}" """)
#         hosts.all.shell(cmd=f"""decho "A record." "{dest_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=f"{dest_data_set}(0)",
#             remote_src=True,
#             replace=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_uss_file_to_previous_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_file = "/etc/profile"
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "A record." "{dest_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_file,
#             dest=f"{dest_data_set}(0)",
#             remote_src=True,
#             replace=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_pds_member_to_previous_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         member_src = f"{src_data_set}(MEMBER)"
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tPDS {src_data_set}")
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{member_src}" """)

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "A record." "{dest_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=member_src,
#             dest=f"{dest_data_set}(0)",
#             remote_src=True,
#             replace=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""dcat "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_pds_to_previous_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         member_src = f"{src_data_set}(MEMBER)"
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tPDSE {src_data_set}")
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{member_src}" """)

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tPDS "{dest_data_set}(+1)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=f"{dest_data_set}(0)",
#             remote_src=True,
#             replace=True
#         )

#         verify_copy = hosts.all.shell(cmd=f"""mls "{dest_data_set}(0)" """)

#         # Checking that we got a source of the form: ANSIBLE.DATA.SET.G0001V01.
#         gds_pattern = r"G[0-9]+V[0-9]+"

#         for cp_res in copy_results.contacted.values():
#             dest = cp_res.get("dest", "")

#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert re.fullmatch(gds_pattern, dest.split(".")[-1])
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_cp in verify_copy.contacted.values():
#             assert v_cp.get("rc") == 0
#             assert v_cp.get("stdout") != ""
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_data_set_to_previous_gds_no_force(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)

#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}" """)
#         hosts.all.shell(cmd=f"""decho "A record." "{dest_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=f"{dest_data_set}(0)",
#             remote_src=True,
#             replace=False
#         )

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is not None
#             assert cp_res.get("changed") is False
#             assert cp_res.get("failed") is True
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# @pytest.mark.parametrize("generation", [0, -1])
# def test_copy_data_set_to_previous_non_existent_gds(ansible_zos_module, generation):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#         if generation < 0:
#             hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)

#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             # Copying to a previous generation that doesn't exist.
#             dest=f"{dest_data_set}({generation})",
#             remote_src=True,
#             replace=True
#         )

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is not None
#             assert "generation data set is not allocated" in cp_res.get("msg")
#             assert cp_res.get("changed") is False
#             assert cp_res.get("failed") is True
#     finally:
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_copy_gdg_to_uss_dir(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest = get_random_file_name(dir=TMP_DIRECTORY)

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)

#         hosts.all.file(path=dest, state="directory")

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=dest,
#             remote_src=True
#         )

#         verify_dest = hosts.all.shell(cmd=f"ls {dest}/{src_data_set}")

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert cp_res.get("dest") is not None
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#         for v_res in verify_dest.contacted.values():
#             assert v_res.get("rc") == 0
#             assert len(v_res.get("stdout_lines", [])) > 0
#     finally:
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {src_data_set}")
#         hosts.all.file(path=dest, state="absent")


# @pytest.mark.parametrize("new_gdg", [True, False])
# def test_copy_gdg_to_gdg(ansible_zos_module, new_gdg):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)

#         if not new_gdg:
#             hosts.all.shell(cmd=f"dtouch -tGDG -L3 {dest_data_set}")
#             hosts.all.shell(cmd=f"""dtouch -tSEQ "{dest_data_set}(+1)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=dest_data_set,
#             remote_src=True
#         )

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert cp_res.get("dest") is not None
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#     finally:
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(-1)" """)
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {src_data_set}")

#         if not new_gdg:
#             hosts.all.shell(cmd=f"""drm "{dest_data_set}(-2)" """)
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(-1)" """)
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")

# def test_identical_gdg_copy(ansible_zos_module):
#    hosts = ansible_zos_module
#    try:
#        src_data_set = get_tmp_ds_name()
#        dest_data_set = get_tmp_ds_name()
#        # Create source GDG base
#        hosts.all.shell(cmd=f"dtouch -tGDG -L5 {src_data_set}")
#        # Create 5 generations in source GDG
#        hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#        hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#        hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#        hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#        hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)

#        # Delete first two generations: (-4) and (-3)
#        hosts.all.shell(cmd=f"""drm "{src_data_set}(-4)" """)
#        hosts.all.shell(cmd=f"""drm "{src_data_set}(-3)" """)
#        # Copy with identical_gdg_copy: true
#        copy_results = hosts.all.zos_copy(
#            src=src_data_set,
#            dest=dest_data_set,
#            remote_src=True,
#            identical_gdg_copy=True
#        )
#        for result in copy_results.contacted.values():
#            assert result.get("msg") is None
#            assert result.get("changed") is True
#            assert result.get("dest") is not None
#            assert result.get("dest_created") is not None
#            assert result.get("src") is not None
#    finally:
#        src_gdg_result = hosts.all.shell(cmd=f"dls {src_data_set}.*")
#        src_gdgs = []
#        for result in src_gdg_result.contacted.values():
#            src_gdgs.extend(result.get("stdout_lines", []))
#        # List destination generations
#        dest_gdg_result = hosts.all.shell(cmd=f"dls {dest_data_set}.*")
#        dest_gdgs = []
#        for result in dest_gdg_result.contacted.values():
#            dest_gdgs.extend(result.get("stdout_lines", []))
#            expected_dest_gdgs = [
#                ds_name.replace(src_data_set,dest_data_set) for ds_name in src_gdgs
#            ]
#            assert sorted(dest_gdgs) == sorted(expected_dest_gdgs), f"Absolute names mismatch.\nExpected: {expected_dest_gdgs}\nFound: {dest_gdgs}"
#            print("Abssolute GDG names copied correctly.")
#            for name in dest_gdgs:
#                print(name)
#        # Clean up both source and destination
#        hosts.all.shell(cmd=f"drm {src_data_set}*")
#        hosts.all.shell(cmd=f"drm {dest_data_set}*")


# def test_copy_gdg_to_gdg_dest_attributes(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {src_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{src_data_set}(+1)" """)
#         hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_data_set}(0)" """)

#         copy_results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=dest_data_set,
#             remote_src=True,
#             dest_data_set={
#                 "type": "gdg",
#                 "limit": 5,
#                 "empty": False,
#                 "scratch": True,
#                 "purge": True,
#                 "extended": False,
#                 "fifo": False
#             }
#         )

#         for cp_res in copy_results.contacted.values():
#             assert cp_res.get("msg") is None
#             assert cp_res.get("changed") is True
#             assert cp_res.get("dest") is not None
#             assert cp_res.get("dest_created") is not None
#             assert cp_res.get("src") is not None
#     finally:
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(-1)" """)
#         hosts.all.shell(cmd=f"""drm "{src_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {src_data_set}")

#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(-1)" """)
#         hosts.all.shell(cmd=f"""drm "{dest_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {dest_data_set}")


# def test_backup_gds(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()
#         backup_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tSEQ {dest_data_set}")
#         hosts.all.shell(cmd=f"decho \"{DUMMY_DATA}\" \"{src_data_set}\"")
#         hosts.all.shell(cmd=f"decho \"A record\" \"{dest_data_set}\"")

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {backup_data_set}")

#         results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=dest_data_set,
#             remote_src=True,
#             replace=True,
#             backup=True,
#             backup_name=f"{backup_data_set}(+1)",
#         )

#         backup_check = hosts.all.shell(
#             cmd=f"""dcat "{backup_data_set}(0)" | wc -l """
#         )

#         for result in results.contacted.values():
#             assert result.get("changed") is True
#             assert result.get("msg") is None
#             assert result.get("dest") is not None
#             assert result.get("dest_created") is not None
#             assert result.get("src") is not None

#         for result in backup_check.contacted.values():
#             assert result.get("rc") == 0
#             assert int(result.get("stdout")) > 0

#     finally:
#         hosts.all.shell(cmd=f"""drm "{backup_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {backup_data_set}")
#         hosts.all.shell(cmd=f"drm {dest_data_set}")
#         hosts.all.shell(cmd=f"drm {src_data_set}")


# def test_backup_gds_invalid_generation(ansible_zos_module):
#     hosts = ansible_zos_module

#     try:
#         src_data_set = get_tmp_ds_name()
#         dest_data_set = get_tmp_ds_name()
#         backup_data_set = get_tmp_ds_name()

#         hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
#         hosts.all.shell(cmd=f"dtouch -tSEQ {dest_data_set}")

#         hosts.all.shell(cmd=f"decho \"{DUMMY_DATA}\" \"{src_data_set}\"")
#         hosts.all.shell(cmd=f"decho \"{DUMMY_DATA}\" \"{dest_data_set}\"")

#         hosts.all.shell(cmd=f"dtouch -tGDG -L3 {backup_data_set}")
#         hosts.all.shell(cmd=f"""dtouch -tSEQ "{backup_data_set}(+1)" """)

#         results = hosts.all.zos_copy(
#             src=src_data_set,
#             dest=dest_data_set,
#             remote_src=True,
#             replace=True,
#             backup=True,
#             backup_name=f"{backup_data_set}(0)",
#         )

#         for result in results.contacted.values():
#             assert result.get("failed") is True
#             assert result.get("changed") is False
#             assert result.get("msg") is not None
#             assert "cannot be used" in result.get("msg")

#     finally:
#         hosts.all.shell(cmd=f"""drm "{backup_data_set}(0)" """)
#         hosts.all.shell(cmd=f"drm {backup_data_set}")
#         hosts.all.shell(cmd=f"drm {dest_data_set}")
#         hosts.all.shell(cmd=f"drm {src_data_set}")


def test_copy_to_dataset_with_special_symbols(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src_data_set = get_tmp_ds_name()
        dest_data_set = get_tmp_ds_name(symbols=True)

        hosts.all.shell(cmd=f"dtouch -tSEQ {src_data_set}")
        hosts.all.shell(cmd=f"decho \"{DUMMY_DATA}\" \"{src_data_set}\"")

        results = hosts.all.zos_copy(
            src=src_data_set,
            dest=dest_data_set,
            remote_src=True
        )

        for result in results.contacted.values():
            assert result.get("changed") is True
            assert result.get("msg") is None
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

    finally:
        hosts.all.zos_data_set(name=src_data_set, state="absent")
        hosts.all.zos_data_set(name=dest_data_set, state="absent")


def test_job_script_async(ansible_zos_module, get_config):
    try:
        ds_name = get_tmp_ds_name()
        path = get_config
        with open(path, 'r') as file:
            enviroment = yaml.safe_load(file)

        ssh_key = enviroment["ssh_key"]
        hosts = enviroment["host"].upper()
        user = enviroment["user"].upper()
        python_path = enviroment["python_path"]
        cut_python_path = python_path[:python_path.find('/bin')].strip()
        zoau = enviroment["environment"]["ZOAU_ROOT"]
        python_version = cut_python_path.split('/')[2]

        playbook = tempfile.NamedTemporaryFile(delete=True)
        inventory = tempfile.NamedTemporaryFile(delete=True)

        os.system("echo {0} > {1}".format(
            quote(PLAYBOOK_ASYNC_TEST.format(
                zoau,
                cut_python_path,
                python_version,
                ds_name
            )),
            playbook.name
        ))

        os.system("echo {0} > {1}".format(
            quote(INVENTORY_ASYNC_TEST.format(
                hosts,
                ssh_key,
                user,
                python_path
            )),
            inventory.name
        ))

        command = "ansible-playbook -i {0} {1}".format(
            inventory.name,
            playbook.name
        )

        result = subprocess.run(
            command,
            capture_output=True,
            shell=True,
            timeout=120,
            encoding='utf-8'
        )
        assert result.returncode == 0
        assert "ok=3" in result.stdout
        assert "changed=2" in result.stdout
        assert result.stderr == ""
    finally:
        ansible_zos_module.all.zos_data_set(name=ds_name, state="absent")

def test_copy_data_set_seq_with_aliases(ansible_zos_module, volumes_on_systems):
    hosts = ansible_zos_module
    src = get_tmp_ds_name(mlq_size=3, llq_size=3)
    src_alias = get_tmp_ds_name(mlq_size=3, llq_size=3)
    src = f'{src[:7]}.{src[13:]}'
    src_alias = f'{src_alias[:7]}.{src_alias[13:]}'
    dest = get_tmp_ds_name(mlq_size=3, llq_size=3)
    dest_alias = get_tmp_ds_name(mlq_size=3, llq_size=3)
    dest = f'{dest[:7]}.{dest[13:]}'
    dest_alias = f'{dest_alias[:7]}.{dest_alias[13:]}'
    volumes = Volume_Handler(volumes_on_systems)
    available_vol = volumes.get_available_vol()
    try:
        data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -tseq -V{available_vol} {src}'
        )
        hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src}" """)
        for result in data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
        dest_data_set_creation_result = hosts.all.shell(
            cmd=f'dtouch -tseq {dest}'
        )
        for result in dest_data_set_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
        alias_creation_result = hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({src_alias}) RELATE({src}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )
        for result in alias_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
        dest_alias_creation_result = hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({dest_alias}) RELATE({dest}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )
        for result in dest_alias_creation_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
        zos_copy_result = hosts.all.zos_copy(
            src=src_alias,
            dest=dest_alias,
            remote_src=True
        )
        for result in zos_copy_result.contacted.values():
            assert result.get('changed') is True
            assert result.get('failed', False) is False
            assert result.get("msg") is None
            assert result.get("dest") is not None
            assert result.get("dest_created") is not None
            assert result.get("src") is not None
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest),
            executable=SHELL_EXECUTABLE,
        )
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == DUMMY_DATA
    finally:
        hosts.all.shell(cmd=f'drm {src_alias}')
        hosts.all.shell(cmd=f'drm {dest_alias}')
        hosts.all.shell(cmd=f'drm {src}')
        hosts.all.shell(cmd=f'drm {dest}')

def test_copy_pds_to_pds_using_dest_alias(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src_pds = get_tmp_ds_name(mlq_size=3, llq_size=3)
        src_pds = f'{src_pds[:7]}.{src_pds[13:]}'
        dest_pds = get_tmp_ds_name(mlq_size=3, llq_size=3)
        dest_pds = f'{dest_pds[:7]}.{dest_pds[13:]}'
        dest_pds_alias = get_tmp_ds_name(mlq_size=3, llq_size=3)
        dest_pds_alias = f'{dest_pds_alias[:7]}.{dest_pds_alias[13:]}'

        hosts.all.shell(cmd=f"dtouch -tPDS {src_pds}")
        hosts.all.shell(cmd=f"""decho "{DUMMY_DATA}" "{src_pds}(MEMBER)" """)
        hosts.all.shell(cmd=f"dtouch -tPDS {dest_pds}")
        hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({dest_pds_alias}) RELATE({dest_pds}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )

        copy_results = hosts.all.zos_copy(
            src=src_pds,
            dest=dest_pds_alias,
            remote_src=True
        )

        for cp_res in copy_results.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") is not None
            assert cp_res.get("dest_created") is not None
            assert cp_res.get("src") is not None

        verify_dest = hosts.all.shell(
            cmd=f"""dcat "{dest_pds}(MEMBER)" """,
            executable=SHELL_EXECUTABLE,
        )
        for v_res in verify_dest.contacted.values():
            assert v_res.get("rc") == 0
            assert len(v_res.get("stdout_lines")) > 0
    finally:
        hosts.all.shell(cmd=f"drm {src_pds}")
        hosts.all.shell(cmd=f"drm {dest_pds}")
        hosts.all.shell(cmd=f"drm {dest_pds_alias}")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
def test_copy_pdse_loadlib_to_pdse_loadlib_using_aliases(ansible_zos_module):

    hosts = ansible_zos_module
    mlq_size = 3
    cobol_src_pds = get_tmp_ds_name(mlq_size)
    cobol_src_mem = "HELLOCBL"
    cobol_src_mem2 = "HICBL2"
    src_lib = get_tmp_ds_name(mlq_size=3, llq_size=3)
    src_lib = f'{src_lib[:7]}.{src_lib[13:]}'
    src_lib_aliases = get_tmp_ds_name(mlq_size=3, llq_size=3)
    src_lib_aliases = f'{src_lib_aliases[:7]}.{src_lib_aliases[13:]}'
    dest_lib = get_tmp_ds_name(mlq_size=3, llq_size=3)
    dest_lib = f'{dest_lib[:7]}.{dest_lib[13:]}'
    dest_lib_aliases = get_tmp_ds_name(mlq_size=3, llq_size=3)
    dest_lib_aliases = f'{dest_lib_aliases[:7]}.{dest_lib_aliases[13:]}'
    pgm_mem = "HELLO"
    pgm2_mem = "HELLO2"
    pgm_mem_alias = "ALIAS1"
    pgm2_mem_alias = "ALIAS2"
    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        hosts.all.zos_data_set(
                name=dest_lib,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
        )

        # generate loadlib w 2 members w 1 alias each
        generate_loadlib(
            hosts=hosts,
            cobol_src_pds=cobol_src_pds,
            cobol_src_mems=[cobol_src_mem, cobol_src_mem2],
            loadlib_pds=src_lib,
            loadlib_mems=[pgm_mem, pgm2_mem],
            loadlib_alias_mems=[pgm_mem_alias, pgm2_mem_alias]
        )

        hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({src_lib_aliases}) RELATE({src_lib}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )

        hosts.all.shell(
            cmd=f'echo "  DEFINE ALIAS (NAME({dest_lib_aliases}) RELATE({dest_lib}))" | mvscmdauth --pgm=idcams --sysin=stdin --sysprint=*'
        )

        # copy src loadlib to dest library pds w aliases
        copy_res_aliases = hosts.all.zos_copy(
                src="{0}".format(src_lib_aliases),
                dest="{0}".format(dest_lib_aliases),
                remote_src=True,
                executable=True,
                aliases=True,
                dest_data_set={
                    'type': "library",
                    'record_format': "u",
                    'record_length': 0,
                    'block_size': 32760,
                    'space_primary': 2,
                    'space_type': "m",
                }
        )

        for result in copy_res_aliases.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}".format(dest_lib_aliases)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, pgm_mem)
            expected_mls_str2 = "{0}   alias  {1}".format(pgm2_mem_alias, pgm2_mem)
            assert expected_mls_str in stdout
            assert expected_mls_str2 in stdout

        # verify pgms remain executable
        pgm_output_map = {
            (dest_lib, pgm_mem, COBOL_PRINT_STR),
            (dest_lib, pgm2_mem, COBOL_PRINT_STR2)
        }
        for steplib, pgm, output in pgm_output_map:
            validate_loadlib_pgm(hosts, steplib=steplib, pgm_name=pgm, expected_output_str=output)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=src_lib_aliases, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")

@pytest.mark.uss
@pytest.mark.seq
@pytest.mark.asa
def test_copy_asa_file_to_asa_sequential_with_pound(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}£#@"
        hosts.all.zos_data_set(name=dest, state="absent")

        copy_result = hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=dest,
            remote_src=False,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = dest.replace('£', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        dest = dest.replace("£", "$")
        hosts.all.zos_data_set(name=dest, state="absent")

@pytest.mark.seq
@pytest.mark.asa
def test_copy_seq_data_set_to_seq_asa_with_pounds(ansible_zos_module):
    hosts = ansible_zos_module

    try:
        src = get_tmp_ds_name(llq_size=4)
        src = f"{src}$£@"
        hosts.all.zos_data_set(
            name=src,
            state="present",
            type="seq",
            replace=True
        )

        dest = get_tmp_ds_name(llq_size=4)
        dest = f"{dest}$£@"
        hosts.all.zos_data_set(name=dest, state="absent")

        hosts.all.zos_copy(
            content=ASA_SAMPLE_CONTENT,
            dest=src,
            remote_src=False
        )

        copy_result = hosts.all.zos_copy(
            src=src,
            dest=dest,
            remote_src=True,
            asa_text=True
        )

        # We need to escape the data set name because we are using cat, using dcat will
        # bring the trailing empty spaces according to the data set record length.
        # We only need to escape $ character in this notation
        dest_escaped = dest.replace('$', '\\$').replace('£', '\\$')
        verify_copy = hosts.all.shell(
            cmd="cat \"//'{0}'\"".format(dest_escaped),
            executable=SHELL_EXECUTABLE,
        )

        for cp_res in copy_result.contacted.values():
            assert cp_res.get("msg") is None
            assert cp_res.get("changed") is True
            assert cp_res.get("dest") == dest
            assert cp_res.get("dest_created") is True
            assert cp_res.get("src") is not None
        for v_cp in verify_copy.contacted.values():
            assert v_cp.get("rc") == 0
            assert v_cp.get("stdout") == ASA_SAMPLE_RETURN
    finally:
        src = src.replace("£", "$")
        dest = dest.replace("£", "$")
        hosts.all.zos_data_set(name=src, state="absent")
        hosts.all.zos_data_set(name=dest, state="absent")


@pytest.mark.pdse
@pytest.mark.loadlib
@pytest.mark.aliases
@pytest.mark.parametrize("is_created", ["true", "false"])
def test_copy_pds_loadlib_member_to_pds_loadlib_member_with_pound(ansible_zos_module, is_created):
    hosts = ansible_zos_module
    # This dataset and member should be available on any z/OS system.
    mlq_size = 3
    cobol_src_pds = get_tmp_ds_name(mlq_size)
    cobol_src_mem = "HELLOCBL"
    src_lib = get_tmp_ds_name(mlq_size)
    dest_lib = get_tmp_ds_name(mlq_size)
    dest_lib_aliases = get_tmp_ds_name(mlq_size)
    pgm_mem = "HELLO"
    dest_pgm_mem = "HELLO£"
    pgm_mem_alias = "ALIAS1"
    try:
        # allocate pds for cobol src code
        hosts.all.zos_data_set(
            name=cobol_src_pds,
            state="present",
            type="pds",
            space_primary=2,
            record_format="fb",
            record_length=80,
            block_size=3120,
            replace=True,
        )
        # allocate pds for src loadlib
        hosts.all.zos_data_set(
            name=src_lib,
            state="present",
            type="pdse",
            record_format="u",
            record_length=0,
            block_size=32760,
            space_primary=2,
            space_type="m",
            replace=True
        )

        # generate loadlib into src_pds
        generate_executable_ds(hosts, cobol_src_pds, cobol_src_mem, src_lib, pgm_mem, pgm_mem_alias)

        # tests existent/non-existent destination data set code path.
        if not is_created:
            # ensure dest data sets NOT present
            hosts.all.zos_data_set(name=dest_lib, state="absent")
            hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
        else:
            # pre-allocate dest loadlib to copy over without an alias.
            hosts.all.zos_data_set(
                name=dest_lib,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )
            # pre-allocate dest loadlib to copy over with an alias.
            hosts.all.zos_data_set(
                name=dest_lib_aliases,
                state="present",
                type="pdse",
                record_format="u",
                record_length=0,
                block_size=32760,
                space_primary=2,
                space_type="m",
                replace=True
            )

        # zos_copy w an executable:
        copy_res = hosts.all.zos_copy(
            src="{0}({1})".format(src_lib, pgm_mem),
            dest="{0}({1})".format(dest_lib, dest_pgm_mem),
            remote_src=True,
            executable=True,
            aliases=False
        )
        # zos_copy w an executables and its alias:
        copy_res_aliases = hosts.all.zos_copy(
            src="{0}({1})".format(src_lib, pgm_mem),
            dest="{0}({1})".format(dest_lib_aliases, dest_pgm_mem),
            remote_src=True,
            executable=True,
            aliases=True
        )

        for result in copy_res.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib, dest_pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        for result in copy_res_aliases.contacted.values():
            assert result.get("msg") is None
            assert result.get("changed") is True
            assert result.get("dest") == "{0}({1})".format(dest_lib_aliases, dest_pgm_mem)
            assert result.get("dest_created") is not None
            assert result.get("src") is not None

        # check ALIAS keyword and name in mls output
        verify_copy_mls = hosts.all.shell(
            cmd="mls {0}".format(dest_lib),
            executable=SHELL_EXECUTABLE
        )
        verify_copy_mls_aliases = hosts.all.shell(
            cmd="mls -A {0}".format(dest_lib_aliases),
            executable=SHELL_EXECUTABLE
        )

        for v_cp in verify_copy_mls.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            mls_alias_str = "ALIAS({0})".format(pgm_mem_alias)
            assert mls_alias_str not in stdout

        for v_cp in verify_copy_mls_aliases.contacted.values():
            assert v_cp.get("rc") == 0
            stdout = v_cp.get("stdout")
            assert stdout is not None
            expected_mls_str = "{0}   alias  {1}".format(pgm_mem_alias, dest_pgm_mem.replace("£", "$"))
            assert expected_mls_str in stdout

        # execute pgms to validate copy
        validate_loadlib_pgm(hosts, steplib=dest_lib, pgm_name=dest_pgm_mem.replace("£", "$"), expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib_aliases, pgm_name=dest_pgm_mem.replace("£", "$"), expected_output_str=COBOL_PRINT_STR)
        validate_loadlib_pgm(hosts, steplib=dest_lib_aliases, pgm_name=pgm_mem_alias, expected_output_str=COBOL_PRINT_STR)

    finally:
        hosts.all.zos_data_set(name=cobol_src_pds, state="absent")
        hosts.all.zos_data_set(name=src_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib, state="absent")
        hosts.all.zos_data_set(name=dest_lib_aliases, state="absent")
