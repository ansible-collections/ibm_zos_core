# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

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

TEST_CONTENT_ABSENT_DEFAULTMARKER = """if [ -z STEPLIB ] && tty -s;
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

TEST_CONTENT_ABSENT_CUSTOMMARKER = """if [ -z STEPLIB ] && tty -s;
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
DS_TYPE = ['SEQ', 'PDS', 'PDSE']
# not supported data set types
NS_DS_TYPE = ['ESDS', 'RRDS', 'LDS']
ENCODING = ['IBM-1047', 'ISO8859-1', 'UTF-8']

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
    test_ds_block_insertafter_regex=dict(test_name="T1"),
    test_ds_block_insertbefore_regex=dict(test_name="T2"),
    test_ds_block_insertafter_eof=dict(test_name="T3"),
    test_ds_block_insertbefore_bof=dict(test_name="T4"),
    test_ds_block_absent=dict(test_name="T5"),
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
export _BPXK_AUTOCVT"""),
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
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_ABSENT_DEFAULTMARKER
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
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_ABSENT_CUSTOMMARKER
    UssGeneral(
        "test_uss_block_absent_custommarker", ansible_zos_module, TEST_ENV,
        _TEST_INFO,
        TEST_INFO["expected"]["test_uss_block_absent"])
    del _TEST_INFO["marker"]
    del _TEST_INFO["marker_begin"]
    del _TEST_INFO["marker_end"]
    TEST_ENV["TEST_CONT"] = TEST_CONTENT



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

"""
@pytest.mark.ds
@pytest.mark.parametrize("dstype", DS_TYPE)
@pytest.mark.parametrize("encoding", ENCODING)
def test_ds_block_absent(ansible_zos_module, dstype, encoding):
    TEST_ENV["DS_TYPE"] = dstype
    TEST_ENV["ENCODING"] = encoding
    TEST_ENV["TEST_CONT"] = TEST_CONTENT_ABSENT_DEFAULTMARKER
    DsGeneral(
        TEST_INFO["test_ds_block_absent"]["test_name"], ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_absent"],
        TEST_INFO["expected"]["test_uss_block_absent"]
    )
    TEST_ENV["TEST_CONT"] = TEST_CONTENT


@pytest.mark.ds
@pytest.mark.parametrize("dstype", NS_DS_TYPE)
def test_ds_not_supported(ansible_zos_module, dstype):
    TEST_ENV["DS_TYPE"] = dstype
    DsNotSupportedHelper(
        TEST_INFO["test_ds_block_insertafter_regex"]["test_name"], ansible_zos_module,
        TEST_ENV, TEST_INFO["test_uss_block_insertafter_regex"]
    )
"""
