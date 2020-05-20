# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../helpers'))
from test_zos_lineinfile_helper import test_uss_general

__metaclass__ = type

TEST_ENV = dict(
    USS_FILE = "/etc/profile",
    TEST_DIR = "/tmp/zos_lineinfile/",
    TEST_FILE = "",
)

TEST_INFO = dict(
    test_uss_line_replace = dict(path="", regexp="^ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_insertafter_regex = dict(insertafter="^ZOAU_ROOT=", line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_insertbefore_regex = dict(insertbefore="^ZOAU_ROOT=", line="unset ZOAU_ROOT", state="present"),
    test_uss_line_insertafter_eof = dict(insertafter="EOF", line="export ZOAU_ROOT", state="present"),
    test_uss_line_insertbefore_bof = dict(insertbefore="BOF", line="# this is file is for setting env vars", state="present"),
    test_uss_line_replace_match_insertafter_ignore = dict(regexp="^ZOAU_ROOT=", insertafter="^PATH=", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_match_insertbefore_ignore = dict(regexp="^ZOAU_ROOT=", insertbefore="^PATH=", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_replace_nomatch_insertafter_match = dict(regexp="abcxyz", insertafter="^ZOAU_ROOT=", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_nomatch_insertbefore_match = dict(regexp="abcxyz", insertbefore="^ZOAU_ROOT=", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_replace_nomatch_insertafter_nomatch = dict(regexp="abcxyz", insertafter="xyzijk", 
                                            line="ZOAU_ROOT=/mvsutil-develop_dsed", state="present"),
    test_uss_line_replace_nomatch_insertbefore_nomatch = dict(regexp="abcxyz", insertbefore="xyzijk", line="unset ZOAU_ROOT", 
                                            state="present"),
    test_uss_line_absent = dict(regexp="^ZOAU_ROOT=", state="absent"),
)


def test_uss_line_replace(ansible_zos_module):
    test_uss_general("test_uss_line_replace", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace"])

def test_uss_line_insertafter_regex(ansible_zos_module):
    test_uss_general("test_uss_line_insertafter_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_regex"])

def test_uss_line_insertbefore_regex(ansible_zos_module):
    test_uss_general("test_uss_line_insertbefore_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_regex"])

def test_uss_line_insertafter_eof(ansible_zos_module):
    test_uss_general("test_uss_line_insertafter_eof", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertafter_eof"])

def test_uss_line_insertbefore_bof(ansible_zos_module):
    test_uss_general("test_uss_line_insertbefore_bof", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_insertbefore_bof"])

def test_uss_line_replace_match_insertafter_ignore(ansible_zos_module):
    test_uss_general("test_uss_line_replace_match_insertafter_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertafter_ignore"])

def test_uss_line_replace_match_insertbefore_ignore(ansible_zos_module):
    test_uss_general("test_uss_line_replace_match_insertbefore_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_match_insertbefore_ignore"])

def test_uss_line_replace_nomatch_insertafter_match(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertafter_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_match"])

def test_uss_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertbefore_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_match"])

def test_uss_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertafter_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertafter_nomatch"])

def test_uss_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    test_uss_general("test_uss_line_replace_nomatch_insertbefore_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_replace_nomatch_insertbefore_nomatch"])

def test_uss_line_absent(ansible_zos_module):
    test_uss_general("test_uss_line_absent", ansible_zos_module, TEST_ENV, TEST_INFO["test_uss_line_absent"])

"""
def test_ds_line_replace(ansible_zos_module):
    test_ds_general("test_ds_line_replace", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace"])

def test_ds_line_insertafter_regex(ansible_zos_module):
    test_ds_general("test_ds_line_insertafter_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_insertafter_regex"])

def test_ds_line_insertbefore_regex(ansible_zos_module):
    test_ds_general("test_ds_line_insertbefore_regex", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_insertbefore_regex"])

def test_ds_line_insertafter_eof(ansible_zos_module):
    test_ds_general("test_ds_line_insertafter_eof", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_insertafter_eof"])

def test_ds_line_insertbefore_bof(ansible_zos_module):
    test_ds_general("test_ds_line_insertbefore_bof", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_insertbefore_bof"])

def test_ds_line_replace_match_insertafter_ignore(ansible_zos_module):
    test_ds_general("test_ds_line_replace_match_insertafter_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_match_insertafter_ignore"])

def test_ds_line_replace_match_insertbefore_ignore(ansible_zos_module):
    test_ds_general("test_ds_line_replace_match_insertbefore_ignore", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_match_insertbefore_ignore"])

def test_ds_line_replace_nomatch_insertafter_match(ansible_zos_module):
    test_ds_general("test_ds_line_replace_nomatch_insertafter_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_nomatch_insertafter_match"])

def test_ds_line_replace_nomatch_insertbefore_match(ansible_zos_module):
    test_ds_general("test_ds_line_replace_nomatch_insertbefore_match", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_nomatch_insertbefore_match"])

def test_ds_line_replace_nomatch_insertafter_nomatch(ansible_zos_module):
    test_ds_general("test_ds_line_replace_nomatch_insertafter_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_nomatch_insertafter_nomatch"])

def test_ds_line_replace_nomatch_insertbefore_nomatch(ansible_zos_module):
    test_ds_general("test_ds_line_replace_nomatch_insertbefore_nomatch", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_replace_nomatch_insertbefore_nomatch"])

def test_ds_line_absent(ansible_zos_module):
    test_ds_general("test_ds_line_absent", ansible_zos_module, TEST_ENV, TEST_INFO["test_ds_line_absent"])
"""