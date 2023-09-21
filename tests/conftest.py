# Copyright (c) IBM Corporation 2019, 2020
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
from ibm_zos_core.tests.helpers.ztest import ZTestHelper
from ibm_zos_core.tests.helpers.volumes import (
    Volume)
import sys
import time
import string
import random
import re
from mock import MagicMock
import importlib


def pytest_addoption(parser):
    """ Add CLI options and modify optons for pytest-ansible where needed. """
    parser.addoption(
        "--zinventory",
        "-Z",
        action="store",
        default="test_config.yml",
        help="Absolute path to YAML file containing inventory info for functional testing.",
    )


@pytest.fixture(scope="session")
def z_python_interpreter(request):
    """ Generate temporary shell wrapper for python interpreter. """
    path = request.config.getoption("--zinventory")
    helper = ZTestHelper.from_yaml_file(path)
    interpreter_str = helper.build_interpreter_string()
    inventory = helper.get_inventory_info()
    python_path = helper.get_python_path()
    yield (interpreter_str, inventory, python_path)


def clean_logs(adhoc):
    """Attempt to clean up logs and messages on the system."""
    # purge logs
    adhoc.all.command(cmd="opercmd '$PJ(*)'")
    # clean up wtor messages
    results = adhoc.all.command(cmd="uname -n")
    system_name = ""
    for result in results.contacted.values():
        system_name = result.get("stdout")
    results = adhoc.all.zos_operator_action_query(system=system_name)
    actions = []
    for result in results.contacted.values():
        actions = result.get("actions", [])
    for action in actions:
        adhoc.all.zos_operator(cmd="{0}cancel".format(action.get("number")))


@pytest.fixture(scope="session")
def ansible_zos_module(request, z_python_interpreter):
    """ Initialize pytest-ansible plugin with values from
    our YAML config and inject interpreter path into inventory. """
    interpreter, inventory, python_path = z_python_interpreter

    # next two lines perform similar action to ansible_adhoc fixture
    plugin = request.config.pluginmanager.getplugin("ansible")
    adhoc = plugin.initialize(request.config, request, **inventory)

    # Inject our environment
    hosts = adhoc["options"]["inventory_manager"]._inventory.hosts

    # Courtesy, pass along the python_path for some test cases need this information
    adhoc["options"]["ansible_python_path"] = python_path

    for host in hosts.values():
        host.vars["ansible_python_interpreter"] = interpreter
        # host.vars["ansible_connection"] = "zos_ssh"
    yield adhoc
    try:
        clean_logs(adhoc)
    except Exception:
        pass

    # Call of the class by the class ls_Volume (volumes.py file) as many times needed
    # one time the array is filled
@pytest.fixture(scope="session")
def get_volumes(ansible_zos_module):
    # Call the pytest-ansible plugin to execute the command d u,dasd,online
    # to full an array of volumes on available with the priority of of actives (A) and storage
    # (STRG) first then online (O) and storage and if is needed the privated ones but actives
    # then to get a flag if is available or not every volumes is a instance of a class to
    # manage the use
    list_volumes = []
    active_storage = []
    storage_online = []
    flag = False
    iteration = 5
    # The first run of the command d u,dasd,online,,n in the system can conclude with empty data
    # to ensure get volumes is why require not more 5 runs and lastly one second of wait.
    while not flag or iteration > 0:
        all_volumes = ansible_zos_module.all.zos_operator(cmd="d u,dasd,online,,65536")
        time.sleep(1)
        for volume in all_volumes.contacted.values():
            all_volumes = volume.get('content')
        flag = True if len(all_volumes) > 5 else False
        iteration -= 1
    # Check if the volume is of storage and is active on prefer but also online as a correct option
    for info in all_volumes:
        vol_w_info = info.split()
        if vol_w_info[2] == 'A' and vol_w_info[4] == "STRG/RSDNT":
            active_storage.append(vol_w_info[3])
        if vol_w_info[2] == 'O' and vol_w_info[4] == "STRG/RSDNT":
            storage_online.append(vol_w_info[3])
    # Insert a volumes for the class ls_Volumes to give flag of in_use and correct manage
    for vol in active_storage:
        list_volumes.append(Volume(vol))
    for vol in storage_online:
        list_volumes.append(Volume(vol))
    return list_volumes

# * We no longer edit sys.modules directly to add zoautil_py mock
# * because automatic teardown is not performed, leading to mock pollution
# * across test files.
@pytest.fixture(scope="function")
def zos_import_mocker(mocker):
    """ A wrapper fixture around the pytest-mock mocker fixture.
    Abstracts the requirements for mocking zoautil_py module, zoautil_py needs to be mocked
    in order to import most Ansible modules designed for z/OS use.
    Returns a tuple containing a mocker object and the perform_imports() function.
    The perform_imports() function accepts an import or a list of imports as arguments.
    Arguments should be provided as a string or a list of strings."""
    mocker.patch.dict("sys.modules", zoautil_py=MagicMock())

    def perform_imports(imports):
        """ The perform_imports() function accepts an import or a list of imports as arguments.
        Arguments should be provided as a string or a list of strings.
        Returns the import(s) for use. """
        if type(imports) == str:
            newimp = importlib.import_module(imports)
        elif type(imports) == list:
            newimp = [importlib.import_module(x) for x in imports]
        return newimp

    yield (mocker, perform_imports)

# Fixture on scope by function or test to ensure random names of datasets
@pytest.fixture(scope='function')
def get_dataset():
    # Functions inside the fixture to call as many times as need in one test
    # Is need the hosts to call the shell in every test and for some cases of
    # long datasets names that will generate problems with jcl the hlq size can
    # change
    def get_dataset(hosts, hlq_size=8):
        # Generate the first random hlq of size pass as parameter
        letters =  string.ascii_uppercase
        hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
        # Ensure the hlq is correct for the dataset naming conventions, until then continue working
        while not re.fullmatch(
        r"^(?:[A-Z$#@]{1}[A-Z0-9$#@-]{0,7})",
                hlq,
                re.IGNORECASE,
            ):
            hlq =  ''.join(random.choice(letters)for iteration in range(hlq_size))
        # Get the second part of the name with the ocmand mvstmp by time is give
        response = hosts.all.command(cmd="mvstmp {0}".format(hlq))
        for dataset in response.contacted.values():
            ds = dataset.get("stdout")
        return ds
    return get_dataset