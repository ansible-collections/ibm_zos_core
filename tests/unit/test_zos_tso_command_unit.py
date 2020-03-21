# Copyright (c) 2019, 2020 Xiao Yuan Ma <bjmaxy@cn.ibm.com>
# Copyright (c) 2020 Blake Becker <blake.becker@ibm.com>
# Copyright (c) IBM Corporation 2020
# LICENSE: [GNU General Public License version 3](https://opensource.org/licenses/GPL-3.0)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


import sys
from ansible.module_utils import basic
from unittest.mock import MagicMock, Mock
import pytest

IMPORT_NAME = 'ansible_collections_ibm_zos_core.plugins.modules.zos_tso_command'


class DummyModule(object):

    def __init__(self, rc, stdout, stderr):
        self.rc = 0
        self.stdout = stdout
        self.stderr = stderr

    def run_command(self, **kwargs):
        return (self.rc, self.stdout, self.stderr)


test_data_success = [
    ("delete da('bjmaxy.hill3.test') like('bjmaxy.hill3')",
    'IDC0550I ENTRY (A) BJMAXY.HILL3.TEST DELETED\\n0\\n',
    "delete 'BJMAXY.HILL3.TEST'\\n\" ",0,True),
]

@pytest.mark.parametrize("command, stdout, stderr,rc, expected", test_data_success)
def test_run_tso_command_success(zos_import_mocker, command, stdout, stderr,rc, expected):
    mocker, importer = zos_import_mocker
    tso_cmd = importer(IMPORT_NAME)
    module = DummyModule(rc, stdout, stderr)
    module.run_command = Mock(return_value=(rc, stdout, stderr))
    passed = True
    try:
        tso_cmd.run_tso_command(command, module)
    except Exception as e:
        print(e)
        passed = False
    assert passed == expected

test_data_failure1 = [
    ("alloc da('bjmaxy.hill3.test') like('bjmaxy.hill3')",
    "IKJ56893I DATA SET BJMAXY.HILL3.TEST NOT ALLOCATED+\nIGD17101I DATA SET BJMAXY.HILL3.TEST\nNOT DEFINED BECAUSE DUPLICATE NAME EXISTS IN CATALOG\nRETURN CODE IS 8 REASON CODE IS 38 IGG0CLEH\n12\n",
    "alloc da('bjmaxy.hill3.test') like('bjmaxy.hill3')\nRC(12)\n",12,True),
]
@pytest.mark.parametrize("command, stdout, stderr,rc, expected", test_data_failure1)
def test_run_tso_command_failure1(mocker, command, stdout, stderr,rc, expected):
    mocker, importer = zos_import_mocker
    tso_cmd = importer(IMPORT_NAME)
    module = DummyModule(rc, stdout, stderr)
    module.run_command = Mock(return_value=(rc, stdout, stderr))
    passed = True

    try:
        tso_cmd.run_tso_command(command, module)

    except Exception as e:
        print(e)
        passed = False
    assert passed == expected


test_data_failure = [
    ("LISTGRP", "NOT AUTHORIZED TO LIST BASE INFORMATION FOR GROUP TSOUSER","",4,False),
]
@pytest.mark.parametrize("command, stdout, stderr,rc, expected", test_data_failure)
def test_run_tso_command_failure(mocker, command, stdout, stderr,rc, expected):
    mocker, importer = zos_import_mocker
    tso_cmd = importer(IMPORT_NAME)
    module = DummyModule(rc, stdout, stderr)
    module.run_command = Mock(return_value=(rc, stdout, stderr))
    passed = False

    try:
        tso_cmd.run_tso_command(command, module)
    except Exception as e:
        print(e)
        passed = True
    assert passed == expected