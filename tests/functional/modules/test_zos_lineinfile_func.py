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
from ibm_zos_core.tests.helpers.zos_lineinfile_helper import (
    General_uss_test,
    General_ds_test,
    DsNotSupportedHelper,
    DsGeneralResultKeyMatchesRegex,
    DsGeneralForceFail,
    DsGeneralForce,
)
import pytest

__metaclass__ = type

TEST_CONTENT = """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""

# supported data set types
DS_TYPE = ['SEQ', 'PDS', 'PDSE']
# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
# The encoding will be only use on a few test
# ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']


TEST_ENV = dict(
    TEST_CONT=TEST_CONTENT,
    TEST_DIR="/tmp/zos_lineinfile/",
    TEST_FILE="",
    DS_NAME="",
    DS_TYPE="",
)

TEST_INFO = dict(
    # This new declaration are one for all cases we were testing, before the declaration for dataset was test_ds_line_replace=dict(test_name="T1") and send
    # the same arguments than a USS only for force change a little bit, but still repeat most arguments (my bad, the last one)
    test_line_replace=dict(path="", regexp="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_line_absent=dict(regexp="ZOAU_ROOT=", line="", state="absent"),
    test_line_insertafter_regex=dict(insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_line_insertbefore_regex=dict(insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present"),
    test_line_insertafter_eof=dict(insertafter="EOF", line="export ZOAU_ROOT", state="present"),
    test_line_insertbefore_bof=dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present"),
    test_line_replace_nomatch_insertafter_match=dict(regexp="abcxyz", insertafter="ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_line_replace_nomatch_insertbefore_match=dict(regexp="abcxyz", insertbefore="ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present"),
    test_line_replace_match_insertafter_ignore=dict(regexp="ZOAU_ROOT=", insertafter="PATH=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),    
    test_line_replace_nomatch_insertbefore_nomatch=dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", state="present"),
    test_line_replace_match_insertbefore_ignore=dict(regexp="ZOAU_ROOT=", insertbefore="PATH=", line="unset ZOAU_ROOT", state="present"),
    test_line_replace_nomatch_insertafter_nomatch=dict(regexp="abcxyz", insertafter="xyzijk", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_ds_line_force_fail=dict(path="",insertafter="EOF", line="export ZOAU_ROOT", force=False),
    test_ds_line_tmp_hlq_option=dict(insertafter="EOF", line="export ZOAU_ROOT", state="present", backup=True, tmp_hlq="TMPHLQ"),
    # Remove from expected text not used anymore as well as the parameters the same text for uss is use for DS 
)

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_line_replace(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace",
        ansible_zos_module,
        TEST_ENV,
        TEST_INFO["test_line_replace"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


@pytest.mark.uss
def test_uss_line_insertafter_regex(ansible_zos_module):
    General_uss_test(
        "test_uss_line_insertafter_regex", ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertafter_regex"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")    


@pytest.mark.uss
def test_uss_line_insertbefore_regex(ansible_zos_module):
    General_uss_test(
        "test_uss_line_insertbefore_regex", ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertbefore_regex"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


@pytest.mark.uss
def test_uss_line_insertafter_eof(ansible_zos_module):
    General_uss_test(
        "test_uss_line_insertafter_eof", 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_insertafter_eof"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
export ZOAU_ROOT""")


@pytest.mark.uss
def test_uss_line_insertbefore_bof(ansible_zos_module):
    General_uss_test(
        "test_uss_line_insertbefore_bof", 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_insertbefore_bof"],
        """# this is file is for setting env vars
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


@pytest.mark.uss
def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_match_insertafter_ignore", 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_replace_match_insertafter_ignore"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.uss
def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_match_insertbefore_ignore", 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_replace_match_insertbefore_ignore"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_nomatch_insertafter_match", 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_replace_nomatch_insertafter_match"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_nomatch_insertbefore_match", 
        ansible_zos_module,
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertbefore_match"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_nomatch_insertafter_nomatch",
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertafter_nomatch"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
ZOAU_ROOT=/mvsutil-develop_dsed"""
    )


@pytest.mark.uss
def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    General_uss_test(
        "test_uss_line_replace_nomatch_insertbefore_nomatch",
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertbefore_nomatch"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
unset ZOAU_ROOT""")


@pytest.mark.uss
def test_uss_line_absent(ansible_zos_module):
    General_uss_test(
        "test_uss_line_absent", 
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_absent"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


@pytest.mark.uss
def test_uss_line_replace_quoted_escaped(ansible_zos_module):
    TEST_INFO["test_line_replace"]["line"] = 'ZOAU_ROOT=\"/mvsutil-develop_dsed\"'
    General_uss_test(
        "test_uss_line_replace", 
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT="/mvsutil-develop_dsed"
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


@pytest.mark.uss
def test_uss_line_replace_quoted_not_escaped(ansible_zos_module):
    TEST_INFO["test_line_replace"]["line"] = 'ZOAU_ROOT="/mvsutil-develop_dsed"'
    General_uss_test(
        "test_uss_line_replace", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_line_replace"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT="/mvsutil-develop_dsed"
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""")


#########################
# Dataset test cases
#########################

# Now force is parameter to change witch function to call in the helper and alter the declaration by add the force or a test name required.
# without change the original description or the other option is that at the end of the test get back to original one.
@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_insertafter_regex_name"] = {**TEST_INFO["test_line_insertafter_regex"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_insertafter_regex_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertafter_regex"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_regex(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_insertbefore_regex_name"] = {**TEST_INFO["test_line_insertbefore_regex"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_insertbefore_regex_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertbefore_regex"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertafter_eof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_insertafter_eof_name"] = {**TEST_INFO["test_line_insertafter_eof"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_insertafter_eof_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertafter_eof"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
export ZOAU_ROOT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_insertbefore_bof(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_insertbefore_bof_name"] = {**TEST_INFO["test_line_insertbefore_bof"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_insertbefore_bof_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_insertbefore_bof"],
        """# this is file is for setting env vars
if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_match_insertafter_ignore_name"] = {**TEST_INFO["test_line_replace_match_insertafter_ignore"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_replace_match_insertafter_ignore_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_match_insertafter_ignore"],
"""if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_match_insertbefore_ignore_name"] = {**TEST_INFO["test_line_replace_match_insertbefore_ignore"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_replace_match_insertbefore_ignore_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_match_insertbefore_ignore"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_nomatch_insertafter_match_name"] = {**TEST_INFO["test_line_replace_nomatch_insertafter_match"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_replace_nomatch_insertafter_match_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertafter_match"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_nomatch_insertbefore_match_name"] = {**TEST_INFO["test_line_replace_nomatch_insertbefore_match"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_replace_nomatch_insertbefore_match_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertbefore_match"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
unset ZOAU_ROOT
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_nomatch_insertafter_nomatch_name"] = {**TEST_INFO["test_line_replace_nomatch_insertafter_nomatch"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_replace_nomatch_insertafter_nomatch_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_replace_nomatch_insertafter_nomatch"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
ZOAU_ROOT=/mvsutil-develop_dsed"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_nomatch_insertbefore_nomatch_name"] = {**TEST_INFO["test_line_replace_nomatch_insertbefore_nomatch"], "test_name":"T1"}
    General_ds_test(
    TEST_INFO["test_line_replace_nomatch_insertbefore_nomatch_name"]["test_name"],
    ansible_zos_module, 
    TEST_ENV,
    TEST_INFO["test_line_replace_nomatch_insertbefore_nomatch"],
    """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT
unset ZOAU_ROOT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_absent(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_absent_name"] = {**TEST_INFO["test_line_absent"], "test_name":"T1"}
    General_ds_test(
        TEST_INFO["test_line_absent_name"]["test_name"],
        ansible_zos_module, 
        TEST_ENV,
        TEST_INFO["test_line_absent"],
        """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
def test_ds_tmp_hlq_option(ansible_zos_module, encoding):
    # This TMPHLQ only works with sequential datasets
    TEST_ENV["DS_TYPE"] = 'SEQ'
    test_name = "T12"
    kwargs = dict(backup_name=r"TMPHLQ\..")
    DsGeneralResultKeyMatchesRegex(
        test_name, ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_ds_line_tmp_hlq_option"],
        **kwargs
    )

## Non supported test cases

@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_not_supported"] = {**TEST_INFO["test_line_replace"], "test_name":"T1"}
    DsNotSupportedHelper(
        TEST_INFO["test_line_replace_not_supported"]["test_name"], 
        ansible_zos_module,
        TEST_ENV, 
        TEST_INFO["test_line_replace"]
    )

# Force test case one for success and one for fail 
# Just keep the DS_TYPE on use 
@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_force(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_INFO["test_line_replace_force"] = {**TEST_INFO["test_line_replace"], "force":"True"}
    DsGeneralForce(
    ansible_zos_module, 
    TEST_ENV,
    TEST_CONTENT,
    TEST_INFO["test_line_replace_force"],
    """if [ -z STEPLIB ] && tty -s;
then
    export STEPLIB=none
    exec -a 0 SHELL
fi
TZ=PST8PDT
export TZ
LANG=C
export LANG
readonly LOGNAME
PATH=/usr/lpp/zoautil/v100/bin:/usr/lpp/rsusr/ported/bin:/bin:/var/bin
export PATH
LIBPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
export LIBPATH
NLSPATH=/usr/lib/nls/msg/%L/%N
export NLSPATH
MANPATH=/usr/man/%L
export MANPATH
MAIL=/usr/mail/LOGNAME
export MAIL
umask 022
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT"""
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
def test_ds_line_force_fail(ansible_zos_module, dstype, ):
    TEST_ENV["DS_TYPE"] = dstype
    DsGeneralForceFail(
        ansible_zos_module,
        TEST_INFO["test_ds_line_force_fail"]
    )

# Space for test cases with different encoding
# ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']


