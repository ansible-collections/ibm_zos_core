# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
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
from ibm_zos_core.tests.helpers.zos_blockinfile_helper import (
    UssGeneral,
    DsGeneral,
    DsNotSupportedHelper,
)
import os
import sys
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

TEST_CONTENT_DEFAULTMARKER = """if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
# END ANSIBLE MANAGED BLOCK
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

TEST_CONTENT_CUSTOMMARKER = """if [ -z STEPLIB ] && tty -s;
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
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/usr/lpp/zoautil/v100
ZOAUTIL_DIR=/usr/lpp/zoautil/v100
# CLOSE IBM MANAGED BLOCK
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
# DS_TYPE = ['SEQ', 'PDS', 'PDSE']
DS_TYPE = ['SEQ']
# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
"""
Note: zos_encode module uses USS cp command for copying from USS file to MVS data set which only supports IBM-1047 charset.
I had to develop and use a new tool for converting and copying to data set in order to set up environment for tests to publish results on Jira.
Until the issue be addressed I disable related tests.
"""
# ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']
ENCODING = ['IBM-1047']
TEST_ENV = dict(
    TEST_CONT=TEST_CONTENT,
    TEST_DIR="/tmp/zos_blockinfile/",
    TEST_FILE="",
    DS_NAME="",
    DS_TYPE="",
    ENCODING="",
)

TEST_INFO = dict(
    test_uss_block_insertafter_regex=dict(
        insertafter="ZOAU_ROOT=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        state="present"),
    test_uss_block_insertbefore_regex=dict(
        insertbefore="ZOAU_ROOT=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present"),
    test_uss_block_insertafter_eof=dict(
        insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present"),
    test_uss_block_insertbefore_bof=dict(
        insertbefore="BOF", block="# this is file is for setting env vars",
        state="present"),
    test_uss_block_absent=dict(block="", state="absent"),
    test_uss_block_replace_insertafter_regex=dict(
        insertafter="PYTHON_HOME=", block="ZOAU_ROOT=/mvsutil-develop_dsed\nZOAU_HOME=\\$ZOAU_ROOT\nZOAU_DIR=\\$ZOAU_ROOT",
        state="present"),
    test_uss_block_replace_insertbefore_regex=dict(
        insertbefore="PYTHON_HOME=", block="unset ZOAU_ROOT\nunset ZOAU_HOME\nunset ZOAU_DIR", state="present"),
    test_uss_block_replace_insertafter_eof=dict(
        insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present"),
    test_uss_block_replace_insertbefore_bof=dict(
        insertbefore="BOF", block="# this is file is for setting env vars",
        state="present"),
    test_uss_block_insert_with_indentation_level_specified=dict(
        insertafter="EOF", block="export ZOAU_ROOT\nexport ZOAU_HOME\nexport ZOAU_DIR", state="present", indentation=16),
    test_ds_block_insertafter_regex=dict(test_name="T1"),
    test_ds_block_insertbefore_regex=dict(test_name="T2"),
    test_ds_block_insertafter_eof=dict(test_name="T3"),
    test_ds_block_insertbefore_bof=dict(test_name="T4"),
    test_ds_block_absent=dict(test_name="T5"),
    test_ds_block_insert_with_indentation_level_specified=dict(test_name="T7"),
    expected=dict(test_uss_block_insertafter_regex_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# END ANSIBLE MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insertbefore_regex_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# END ANSIBLE MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insertafter_eof_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK""",
                  test_uss_block_insertbefore_bof_defaultmarker="""# BEGIN ANSIBLE MANAGED BLOCK
# this is file is for setting env vars
# END ANSIBLE MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insertafter_regex_custommarker="""if [ -z STEPLIB ] && tty -s;
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
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# CLOSE IBM MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insertbefore_regex_custommarker="""if [ -z STEPLIB ] && tty -s;
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
# OPEN IBM MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# CLOSE IBM MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insertafter_eof_custommarker="""if [ -z STEPLIB ] && tty -s;
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
# OPEN IBM MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# CLOSE IBM MANAGED BLOCK""",
                  test_uss_block_insertbefore_bof_custommarker="""# OPEN IBM MANAGED BLOCK
# this is file is for setting env vars
# CLOSE IBM MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_absent="""if [ -z STEPLIB ] && tty -s;
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
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertafter_regex_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
# BEGIN ANSIBLE MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# END ANSIBLE MANAGED BLOCK
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertbefore_regex_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
# BEGIN ANSIBLE MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# END ANSIBLE MANAGED BLOCK
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertafter_eof_defaultmarker="""if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK""",
                  test_uss_block_replace_insertbefore_bof_defaultmarker="""# BEGIN ANSIBLE MANAGED BLOCK
# this is file is for setting env vars
# END ANSIBLE MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertafter_regex_custommarker="""if [ -z STEPLIB ] && tty -s;
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
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
# OPEN IBM MANAGED BLOCK
ZOAU_ROOT=/mvsutil-develop_dsed
ZOAU_HOME=$ZOAU_ROOT
ZOAU_DIR=$ZOAU_ROOT
# CLOSE IBM MANAGED BLOCK
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertbefore_regex_custommarker="""if [ -z STEPLIB ] && tty -s;
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
PYTHONPATH=/usr/lpp/izoda/v110/anaconda/lib:/usr/lpp/zoautil/v100/lib:/lib
PKG_CONFIG_PATH=/usr/lpp/izoda/v110/anaconda/lib/pkgconfig
# OPEN IBM MANAGED BLOCK
unset ZOAU_ROOT
unset ZOAU_HOME
unset ZOAU_DIR
# CLOSE IBM MANAGED BLOCK
PYTHON_HOME=/usr/lpp/izoda/v110/anaconda
_BPXK_AUTOCVT=ON
export ZOAU_ROOT
export ZOAUTIL_DIR
export ZOAUTIL_DIR
export PYTHONPATH
export PKG_CONFIG_PATH
export PYTHON_HOME
export _BPXK_AUTOCVT""",
                  test_uss_block_replace_insertafter_eof_custommarker="""if [ -z STEPLIB ] && tty -s;
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
# OPEN IBM MANAGED BLOCK
export ZOAU_ROOT
export ZOAU_HOME
export ZOAU_DIR
# CLOSE IBM MANAGED BLOCK""",
                  test_uss_block_replace_insertbefore_bof_custommarker="""# OPEN IBM MANAGED BLOCK
# this is file is for setting env vars
# CLOSE IBM MANAGED BLOCK
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
export _BPXK_AUTOCVT""",
                  test_uss_block_insert_with_indentation_level_specified="""if [ -z STEPLIB ] && tty -s;
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
# BEGIN ANSIBLE MANAGED BLOCK
                export ZOAU_ROOT
                export ZOAU_HOME
                export ZOAU_DIR
# END ANSIBLE MANAGED BLOCK""",),
)

#########################
# USS test cases
#########################


@pytest.mark.uss
def test_uss_block_insertafter_regex_defaultmarker(ansible_zos_module):
    UssGeneral(
        "test_uss_block_insertafter_regex_defaultmarker", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertafter_regex"],
        TEST_INFO["expected"]["test_uss_block_insertafter_regex_defaultmarker"])


@pytest.mark.uss
def test_uss_block_insertbefore_regex_defaultmarker(ansible_zos_module):
    UssGeneral(
        "test_uss_block_insertbefore_regex_defaultmarker", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertbefore_regex"],
        TEST_INFO["expected"]["test_uss_block_insertbefore_regex_defaultmarker"])


@pytest.mark.uss
def test_uss_block_insertafter_eof_defaultmarker(ansible_zos_module):
    UssGeneral(
        "test_uss_block_insertafter_eof_defaultmarker", ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_insertafter_eof"],
        TEST_INFO["expected"]["test_uss_block_insertafter_eof_defaultmarker"])


@pytest.mark.uss
def test_uss_block_insertbefore_bof_defaultmarker(ansible_zos_module):
    UssGeneral(
        "test_uss_block_insertbefore_bof_defaultmarker", ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_insertbefore_bof"],
        TEST_INFO["expected"]["test_uss_block_insertbefore_bof_defaultmarker"])


@pytest.mark.uss
def test_uss_block_insertafter_regex_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_insertafter_regex"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    UssGeneral(
        "test_uss_block_insertafter_regex_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_insertafter_regex_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]


@pytest.mark.uss
def test_uss_block_insertbefore_regex_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_insertbefore_regex"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    UssGeneral(
        "test_uss_block_insertbefore_regex_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_insertbefore_regex_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]


@pytest.mark.uss
def test_uss_block_insertafter_eof_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_insertafter_eof"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    UssGeneral(
        "test_uss_block_insertafter_eof_custommarker", ansible_zos_module,
        TEST_ENV, _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_insertafter_eof_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]


@pytest.mark.uss
def test_uss_block_insertbefore_bof_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_insertbefore_bof"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    UssGeneral(
        "test_uss_block_insertbefore_bof_custommarker", ansible_zos_module,
        TEST_ENV, _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_insertbefore_bof_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]


@pytest.mark.uss
def test_uss_block_absent_defaultmarker(ansible_zos_module):
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    UssGeneral(
        "test_uss_block_absent_defaultmarker", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_absent"],
        TEST_INFO["expected"]["test_uss_block_absent"])
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_absent_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_absent"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_absent_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_absent"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_defaultmarker(ansible_zos_module):
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    UssGeneral(
        "test_uss_block_replace_insertafter_regex_defaultmarker", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertafter_regex"],
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_regex_defaultmarker"])
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_defaultmarker(ansible_zos_module):
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    UssGeneral(
        "test_uss_block_replace_insertbefore_regex_defaultmarker", ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertbefore_regex"],
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_regex_defaultmarker"])
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_defaultmarker(ansible_zos_module):
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    UssGeneral(
        "test_uss_block_replace_insertafter_eof_defaultmarker", ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_replace_insertafter_eof"],
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_eof_defaultmarker"])
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_defaultmarker(ansible_zos_module):
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    UssGeneral(
        "test_uss_block_replace_insertbefore_bof_defaultmarker", ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_replace_insertbefore_bof"],
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_bof_defaultmarker"])
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_regex_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_replace_insertafter_regex"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_replace_insertafter_regex_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_regex_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_regex_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_replace_insertbefore_regex"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_replace_insertbefore_regex_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_regex_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertafter_eof_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_replace_insertafter_eof"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_replace_insertafter_eof_custommarker", ansible_zos_module,
        TEST_ENV, _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_eof_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_replace_insertbefore_bof_custommarker(ansible_zos_module):
    _TEST_INFO = TEST_INFO["test_uss_block_replace_insertbefore_bof"]
    _TEST_INFO["marker"] = '# {mark} IBM MANAGED BLOCK'
    _TEST_INFO["marker_begin"] = 'OPEN'
    _TEST_INFO["marker_end"] = 'CLOSE'
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_replace_insertbefore_bof_custommarker", ansible_zos_module,
        TEST_ENV, _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_bof_custommarker"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.uss
def test_uss_block_insert_with_indentation_level_specified(ansible_zos_module):
    UssGeneral(
        "test_uss_block_insert_with_indentation_level_specified", ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_insert_with_indentation_level_specified"],
        TEST_INFO["expected"]["test_uss_block_insert_with_indentation_level_specified"])


#########################
# Dataset test cases
#########################


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_insertafter_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    DsGeneral(
        TEST_INFO["test_ds_block_insertafter_regex"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertafter_regex"],
        TEST_INFO["expected"]["test_uss_block_insertafter_regex_defaultmarker"]
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_insertbefore_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    DsGeneral(
        TEST_INFO["test_ds_block_insertbefore_regex"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertbefore_regex"],
        TEST_INFO["expected"]["test_uss_block_insertbefore_regex_defaultmarker"]
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_insertafter_eof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    DsGeneral(
        TEST_INFO["test_ds_block_insertafter_eof"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertafter_eof"],
        TEST_INFO["expected"]["test_uss_block_insertafter_eof_defaultmarker"]
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_insertbefore_bof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    DsGeneral(
        TEST_INFO["test_ds_block_insertbefore_bof"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertbefore_bof"],
        TEST_INFO["expected"]["test_uss_block_insertbefore_bof_defaultmarker"]
    )


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_replace_insertafter_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_insertafter_regex"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertafter_regex"],
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_regex_defaultmarker"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_replace_insertbefore_regex(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_insertbefore_regex"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertbefore_regex"],
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_regex_defaultmarker"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_replace_insertafter_eof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_insertafter_eof"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertafter_eof"],
        TEST_INFO["expected"]["test_uss_block_replace_insertafter_eof_defaultmarker"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_replace_insertbefore_bof(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_insertbefore_bof"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_replace_insertbefore_bof"],
        TEST_INFO["expected"]["test_uss_block_replace_insertbefore_bof_defaultmarker"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_absent(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_absent"]["test_name"], ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_absent"],
        TEST_INFO["expected"]["test_uss_block_absent"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_insert_with_indentation_level_specified(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    DsGeneral(
        TEST_INFO["test_ds_block_insert_with_indentation_level_specified"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insert_with_indentation_level_specified"],
        TEST_INFO["expected"]["test_uss_block_insert_with_indentation_level_specified"]
    )


#########################
# Negative tests
#########################


@pytest.mark.ds
def test_not_exist_ds_block_insertafter_regex(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO["test_uss_block_insertafter_regex"]
    test_info["path"] = "BIFTEST.NOTEXIST.SEQ"
    results = hosts.all.zos_blockinfile(**test_info)
    for result in results.contacted.values():
        assert "does NOT exist" in result.get("msg")


@pytest.mark.ds
def test_ds_block_insertafter_nomatch_eof_insert(ansible_zos_module):
    TEST_ENV["DS_TYPE"] = 'SEQ'
    TEST_ENV["ENCODING"] = 'IBM-1047'
    TEST_INFO["test_uss_block_insertafter_eof"]["insertafter"] = 'SOME_NON_EXISTING_PATTERN'
    DsGeneral(
        TEST_INFO["test_ds_block_insertafter_eof"]["test_name"],
        ansible_zos_module, TEST_ENV,
        TEST_INFO["test_uss_block_insertafter_eof"],
        TEST_INFO["expected"]["test_uss_block_insertafter_eof_defaultmarker"]
    )


@pytest.mark.ds
def test_ds_block_insertafter_regex_wrongmarker(ansible_zos_module):
    hosts = ansible_zos_module
    test_info = TEST_INFO["test_uss_block_insertafter_regex"]
    test_info["path"] = "BIFTEST.NOTEXIST.SEQ"
    test_info["marker"] = '# MANAGED BLOCK'
    results = hosts.all.zos_blockinfile(**test_info)
    del test_info["marker"]
    for result in results.contacted.values():
        assert "marker should have {mark}" in result.get("msg")


@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    DsNotSupportedHelper(
        TEST_INFO["test_ds_block_insertafter_regex"]["test_name"], ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_insertafter_regex"]
    )
