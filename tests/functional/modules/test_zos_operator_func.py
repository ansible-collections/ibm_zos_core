# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2025
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

import os
import yaml
from shellescape import quote
from ibm_zos_core.tests.helpers.version import is_zoau_version_higher_than

__metaclass__ = type

PARALLEL_RUNNING = """- hosts : zvm
  collections :
    - ibm.ibm_zos_core
  gather_facts: False
  vars:
    ZOAU: "{0}"
    PYZ: "{1}"
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
      - name: zos_operator
        zos_operator:
          cmd: 'd a,all'
          wait_time: 3
          verbose: true
        register: output

      - name: print output
        debug:
          var: output"""

INVENTORY = """all:
  hosts:
    zvm:
      ansible_host: {0}
      ansible_ssh_private_key_file: {1}
      ansible_user: {2}
      ansible_python_interpreter: {3}"""


def test_zos_operator_various_command(ansible_zos_module):
    test_data = [
        ("d a", 0, True),
        ("k s", 0, True),
        ("d r,l", 0, True),
        ("d parmlib", 0, True),
        ("SEND 'list ready',NOW", 0, True),
    ]
    for item in test_data:
        command = item[0]
        expected_rc = item[1]
        changed = item[2]
        hosts = ansible_zos_module
        results = hosts.all.zos_operator(cmd=command)
        for result in results.contacted.values():
            assert result.get("rc") == expected_rc
            assert result.get("changed") is changed
            assert result.get("msg", False) is False
            assert result.get("cmd") == command
            assert result.get("elapsed") is not None
            assert result.get("wait_time") is not None
            assert result.get("time_unit") == "s"
            assert result.get("content") is not None


def test_zos_operator_invalid_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="invalid,command", verbose=False)
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") != 0
        assert result.get("msg") is not None
        assert result.get("cmd") is not None
        assert result.get("elapsed") is not None
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None


def test_zos_operator_invalid_command_to_ensure_transparency(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="DUMP COMM=('ERROR DUMP')", verbose=False)
    for result in results.contacted.values():
        assert result.get("changed") is True
        assert result.get("rc") != 0
        assert result.get("cmd") is not None
        assert result.get("elapsed") is not None
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None
        transparency = False
        if any('DUMP COMMAND' in str for str in result.get("content")):
            transparency = True
        assert transparency


def test_zos_operator_positive_path(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="d u,all", verbose=False)
    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") is not None
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None


def test_zos_operator_positive_path_verbose(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="d u,all", verbose=True)
    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") is not None
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None
        # Traverse the content list for a known verbose keyword and track state
        is_verbose = False
        if any('BGYSC0804I' in str for str in result.get("content")):
            is_verbose = True
        assert is_verbose


def test_zos_operator_positive_verbose_with_full_delay(ansible_zos_module):
    "Long running command should take over 30 seconds"
    hosts = ansible_zos_module
    wait_time = 10
    results = hosts.all.zos_operator(
        cmd="RO *ALL,LOG 'dummy syslog message'", verbose=True, wait_time=wait_time
    )

    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") > wait_time
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None


def test_zos_operator_positive_verbose_with_quick_delay(ansible_zos_module):
    hosts = ansible_zos_module
    wait_time=10
    results = hosts.all.zos_operator(
        cmd="d u,all", verbose=True, wait_time=wait_time
    )

    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") <= (2 * wait_time)
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None


def test_zos_operator_positive_verbose_blocking(ansible_zos_module):
    hosts = ansible_zos_module
    if is_zoau_version_higher_than(hosts,"1.2.4.5"):
        wait_time=5
        results = hosts.all.zos_operator(
            cmd="d u,all", verbose=True, wait_time=wait_time
        )

        for result in results.contacted.values():
            assert result.get("rc") == 0
            assert result.get("changed") is True
            assert result.get("msg", False) is False
            assert result.get("cmd") is not None
            assert result.get("elapsed") >= wait_time
            assert result.get("wait_time") is not None
            assert result.get("time_unit") == "s"
            assert result.get("content") is not None


def test_zos_operator_positive_path_preserve_case(ansible_zos_module):
    hosts = ansible_zos_module
    command = "D U,all"
    results = hosts.all.zos_operator(
        cmd=command,
        verbose=False,
        case_sensitive=True
    )

    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") >= wait_time
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None
        # Making sure the output from opercmd logged the command
        # exactly as it was written.
        assert len(result.get("content")) > 1
        assert command in result.get("content")[1]


def test_response_come_back_complete(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="\\$dspl")
    res = {}
    res["stdout"] = []
    for result in results.contacted.values():
        assert result.get("rc") == 0
        assert result.get("changed") is True
        assert result.get("msg", False) is False
        assert result.get("cmd") is not None
        assert result.get("elapsed") >= wait_time
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None
        stdout = result.get('content')
        # HASP646 Only appears in the last line that before did not appears
        last_line = len(stdout)
        assert "HASP646" in stdout[last_line - 1]


def test_operator_sentiseconds(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_operator(cmd="d a", time_unit="cs", wait_time=100)
    for result in results.contacted.values():
        assert result.get("rc") == expected_rc
        assert result.get("changed") is changed
        assert result.get("msg", False) is False
        assert result.get("cmd") == command
        assert result.get("elapsed") is not None
        assert result.get("wait_time") is not None
        assert result.get("time_unit") == "s"
        assert result.get("content") is not None


def test_zos_operator_parallel_terminal(get_config):
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

    try:
        playbook = "playbook.yml"
        inventory = "inventory.yml"
        os.system("echo {0} > {1}".format(quote(PARALLEL_RUNNING.format(
            zoau,
            cut_python_path,
            python_version
        )), playbook))
        os.system("echo {0} > {1}".format(quote(INVENTORY.format(
            hosts,
            ssh_key,
            user,
            python_path
        )), inventory))
        command = "(ansible-playbook -i {0} {1}) & (ansible-playbook -i {0} {1})".format(
            inventory,
            playbook,
        )
        stdout = os.system(command)
        assert stdout == 0
    finally:
        os.remove("inventory.yml")
        os.remove("playbook.yml")
