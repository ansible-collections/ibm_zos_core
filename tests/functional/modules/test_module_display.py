# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2023
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

__metaclass__ = type

import pytest
import subprocess


@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", force=True, is_remote=False),
])
def test_display_verbosity_5_in_zos_copy(ansible_zos_module, src):
    "Test the display verbosity, ensure it matches the -v count of 5."

    hosts = ansible_zos_module
    user = hosts["options"]["user"]
    node = hosts["options"]["inventory_manager"].list_hosts()[0]

    cmd = "ansible all -i " + str(node) + ", -u " + user + " -m ibm.ibm_zos_core.zos_copy -a \"src=" + src["src"] + " dest=/tmp encoding={{enc}}\" -e '{\"enc\":{\"from\": \"ISO8859-1\", \"to\": \"IBM-1047\"}}' -e \"ansible_python_interpreter=/allpython/3.9/usr/lpp/IBM/cyp/v3r9/pyz/bin/python3.9\" -vvvvv"
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    output = result.read()
    assert "play context verbosity: 5" in output.decode()

@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", force=True, is_remote=False),
])
def test_display_verbosity_4_not_in_zos_copy(ansible_zos_module, src):
    "Test the display verbosity, ensure it does not match 5."

    hosts = ansible_zos_module
    user = hosts["options"]["user"]
    node = hosts["options"]["inventory_manager"].list_hosts()[0]

    cmd = "ansible all -i " + str(node) + ", -u " + user + " -m ibm.ibm_zos_core.zos_copy -a \"src=" + src["src"] + " dest=/tmp encoding={{enc}}\" -e '{\"enc\":{\"from\": \"ISO8859-1\", \"to\": \"IBM-1047\"}}' -e \"ansible_python_interpreter=/allpython/3.9/usr/lpp/IBM/cyp/v3r9/pyz/bin/python3.9\" -vvvvv"
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    output = result.read()
    assert "play context verbosity: 4" not in output.decode()

@pytest.mark.parametrize("src", [
    dict(src="/etc/profile", force=True, is_remote=False),
])
def test_display_verbosity_not_in_zos_copy(ansible_zos_module, src):
    "Test the display verbosity, ensure it is not present"

    hosts = ansible_zos_module
    user = hosts["options"]["user"]
    node = hosts["options"]["inventory_manager"].list_hosts()[0]

    cmd = "ansible all -i " + str(node) + ", -u " + user + " -m ibm.ibm_zos_core.zos_copy -a \"src=" + src["src"] + " dest=/tmp encoding={{enc}}\" -e '{\"enc\":{\"from\": \"ISO8859-1\", \"to\": \"IBM-1047\"}}' -e \"ansible_python_interpreter=/allpython/3.9/usr/lpp/IBM/cyp/v3r9/pyz/bin/python3.9\""
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
    output = result.read()
    assert "play context verbosity:" not in output.decode()