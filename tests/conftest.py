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
import pytest
from ibm_zos_core.tests.helpers.ztest import ZTestHelper
from ibm_zos_core.tests.helpers.volumes import get_volumes, get_volumes_with_vvds, get_volume_and_unit, get_volumes_sms_mgmt_class
from ansible.plugins.action import ActionBase
import sys
from mock import MagicMock
import importlib


def add_vars_to_compute_environment(env_vars):
    """This decorator injects the environment variables defined in a config
    file to the Ansible method responsible for constructing the environment
    string used by the SSH connection plugin."""
    def wrapper_compute_env(compute_environment_string):
        def wrapped_compute_environment_string(self, *args, **kwargs):
            self._task.environment = env_vars
            env_string = compute_environment_string(self, *args, **kwargs)
            return env_string
        return wrapped_compute_environment_string
    return wrapper_compute_env


def pytest_addoption(parser):
    """
    Add CLI options and modify options for pytest-ansible where needed.
    Note: Set the default to to None, otherwise when evaluating with `request.config.getoption("--zinventory"):`
    will always return true because a default will be returned.
    """
    parser.addoption(
        "--zinventory",
        "-Z",
        action="store",
        default=None,
        help="Absolute path to YAML file containing inventory info for functional testing.",
    )
    parser.addoption(
        "--zinventory-raw",
        "-R",
        action="store",
        default=None,
        help="Str - dictionary with values {'host': 'ibm.com', 'user': 'root', 'zoau': '/usr/lpp/zoau', 'pyz': '/usr/lpp/IBM/pyz'}",
    )


@pytest.fixture(scope="session")
def z_python_interpreter(request):
    """ Generate temporary shell wrapper for python interpreter. """
    src = None
    helper = None
    if request.config.getoption("--zinventory"):
        src = request.config.getoption("--zinventory")
        helper = ZTestHelper.from_yaml_file(src)
    elif request.config.getoption("--zinventory-raw"):
        src = request.config.getoption("--zinventory-raw")
        helper = ZTestHelper.from_args(src)

    interpreter_str = helper.build_interpreter_string()
    inventory = helper.get_inventory_info()
    python_path = helper.get_python_path()
    yield (helper._environment, interpreter_str, inventory, python_path)


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
    env_vars, interpreter, inventory, python_path = z_python_interpreter

    # next two lines perform similar action to ansible_adhoc fixture
    plugin = request.config.pluginmanager.getplugin("ansible")
    adhoc = plugin.initialize(request.config, request, **inventory)

    # Inject our environment
    hosts = adhoc["options"]["inventory_manager"]._inventory.hosts

    # Courtesy, pass along the python_path for some test cases need this information
    adhoc["options"]["ansible_python_path"] = python_path

    # Adding the environment variables decorator to the Ansible engine.
    ActionBase._compute_environment_string = add_vars_to_compute_environment(env_vars)(ActionBase._compute_environment_string)

    for host in hosts.values():
        host.vars["ansible_python_interpreter"] = python_path
    yield adhoc
    try:
        clean_logs(adhoc)
    except Exception:
        pass

    # Call of the class by the class ls_Volume (volumes.py file) as many times needed
    # one time the array is filled
@pytest.fixture(scope="session")
def volumes_on_systems(ansible_zos_module, request):
    """ Call the pytest-ansible plugin to check volumes on the system and work properly a list by session."""
    path = request.config.getoption("--zinventory")
    list_volumes = None

    # If path is None, check if zinventory-raw is used instead and if so, extract the
    # volumes dictionary and pass it along.
    if path is None:
        src = request.config.getoption("--zinventory-raw")
        helper = ZTestHelper.from_args(src)
        list_volumes = helper.get_volumes_list()
    else:
        list_volumes = get_volumes(ansible_zos_module, path)
    yield list_volumes


@pytest.fixture(scope="session")
def volumes_with_vvds(ansible_zos_module, request):
    """ Return a list of volumes that have a VVDS. If no volume has a VVDS
    then it will try to create one for each volume found and return volumes only
    if a VVDS was successfully created for it."""
    path = request.config.getoption("--zinventory")
    list_volumes = None

    # If path is None, check if zinventory-raw is used instead and if so, extract the
    # volumes dictionary and pass it along.
    if path is None:
        src = request.config.getoption("--zinventory-raw")
        helper = ZTestHelper.from_args(src)
        list_volumes = helper.get_volumes_list()
    else:
        list_volumes = get_volumes(ansible_zos_module, path)

    volumes_with_vvds = get_volumes_with_vvds(ansible_zos_module, list_volumes)
    yield volumes_with_vvds


@pytest.fixture(scope="session")
def volumes_unit_on_systems(ansible_zos_module, request):
    """ Call the pytest-ansible plugin to check volumes on the system and work properly a list by session."""
    path = request.config.getoption("--zinventory")
    list_volumes = None

    if path is None:
        src = request.config.getoption("--zinventory-raw")
        helper = ZTestHelper.from_args(src)
        list_volumes = helper.get_volumes_list()
    else:
        list_volumes = get_volume_and_unit(ansible_zos_module)

    yield list_volumes


@pytest.fixture(scope="session")
def volumes_sms_systems(ansible_zos_module, request):
    """ Call the pytest-ansible plugin to check volumes on the system and work properly a list by session."""
    path = request.config.getoption("--zinventory")
    list_volumes = None

    if path is None:
        src = request.config.getoption("--zinventory-raw")
        helper = ZTestHelper.from_args(src)
        list_volumes = helper.get_volumes_list()
    else:
        list_volumes = get_volumes(ansible_zos_module, path)

    volumes_with_sms = get_volumes_sms_mgmt_class(ansible_zos_module, list_volumes)
    yield volumes_with_sms


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


@pytest.fixture(scope="function")
def get_config(request):
    """ Call the pytest-ansible plugin to check volumes on the system and work properly a list by session."""
    path = request.config.getoption("--zinventory")
    yield path
