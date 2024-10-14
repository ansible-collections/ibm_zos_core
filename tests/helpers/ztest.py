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

import json
import os
import stat
import uuid
from collections import OrderedDict
# Imports for z_dispatcher_run
import sys
from ansible.cli.adhoc import AdHocCLI
from ansible.playbook.play import Play
from ansible.plugins.loader import init_plugin_loader
from ansible.constants import COLLECTIONS_PATHS
from ansible.executor.task_queue_manager import TaskQueueManager
from pytest_ansible.module_dispatcher.v213 import ModuleDispatcherV213, ResultAccumulator, HAS_CUSTOM_LOADER_SUPPORT
from pytest_ansible.results import AdHocResult

# ? should we just use yaml and accept the unordered dict?
# * oyaml is a drop-in replacement for pyyaml that preserves dict
# * ordering, this is useful in our use case since we define environment variables as
# * a list of key:value pairs. This resolves issues reading environment variables
# * that depend other environment variables defined earlier in the environment variable list.
# when using python versions >= 3.7, dict ordering is preserved by default so pyyaml can be used
from oyaml import safe_load

# TODO: Add/enhance error handling


def z_dispatcher_run(self, *module_args, **complex_args):
    """Basically the same code from pytest_ansible, but adding a dict with environment
    variables to the playbook definition."""
    # Assemble module argument string
    if module_args:
        complex_args.update({"_raw_params": " ".join(module_args)})

    # Assert hosts matching the provided pattern exist
    hosts = self.options["inventory_manager"].list_hosts()
    if self.options.get("extra_inventory_manager", None):
        extra_hosts = self.options["extra_inventory_manager"].list_hosts()
    else:
        extra_hosts = []
    no_hosts = False
    if len(hosts + extra_hosts) == 0:
        no_hosts = True
        warnings.warn("provided hosts list is empty, only localhost is available")  # noqa: B028

    self.options["inventory_manager"].subset(self.options.get("subset"))
    hosts = self.options["inventory_manager"].list_hosts(
        self.options["host_pattern"],
    )
    if self.options.get("extra_inventory_manager", None):
        self.options["extra_inventory_manager"].subset(self.options.get("subset"))
        extra_hosts = self.options["extra_inventory_manager"].list_hosts()
    else:
        extra_hosts = []
    if len(hosts + extra_hosts) == 0 and not no_hosts:
        msg = "Specified hosts and/or --limit does not match any hosts."
        raise ansible.errors.AnsibleError(
            msg,
        )

    # Pass along cli options
    args = ["pytest-ansible"]
    verbosity = None
    for verbosity_syntax in ("-v", "-vv", "-vvv", "-vvvv", "-vvvvv"):
        if verbosity_syntax in sys.argv:
            verbosity = verbosity_syntax
            break
    if verbosity is not None:
        args.append(verbosity_syntax)
    args.extend([self.options["host_pattern"]])
    for argument in (
        "connection",
        "user",
        "become",
        "become_method",
        "become_user",
        "module_path",
    ):
        arg_value = self.options.get(argument)
        argument = argument.replace("_", "-")  # noqa: PLW2901

        if arg_value in (None, False):
            continue

        if arg_value is True:
            args.append(f"--{argument}")
        else:
            args.append(f"--{argument}={arg_value}")

    # Use Ansible's own adhoc cli to parse the fake command line we created and then save it
    # into Ansible's global context
    adhoc = AdHocCLI(args)
    adhoc.parse()

    # And now we'll never speak of this again
    del adhoc

    # Initialize callbacks to capture module JSON responses
    callback = ResultAccumulator()

    kwargs = {
        "inventory": self.options["inventory_manager"],
        "variable_manager": self.options["variable_manager"],
        "loader": self.options["loader"],
        "stdout_callback": callback,
        "passwords": {"conn_pass": None, "become_pass": None},
    }

    kwargs_extra = {}
    # If we have an extra inventory, do the same that we did for the inventory
    if self.options.get("extra_inventory_manager", None):
        callback_extra = ResultAccumulator()

        kwargs_extra = {
            "inventory": self.options["extra_inventory_manager"],
            "variable_manager": self.options["extra_variable_manager"],
            "loader": self.options["extra_loader"],
            "stdout_callback": callback_extra,
            "passwords": {"conn_pass": None, "become_pass": None},
        }

    # create a pseudo-play to execute the specified module via a single task
    play_ds = {
        "name": "pytest-ansible",
        "hosts": self.options["host_pattern"],
        "become": self.options.get("become"),
        "become_user": self.options.get("become_user"),
        "gather_facts": "no",
        "tasks": [
            {
                "action": {
                    "module": self.options["module_name"],
                    "args": complex_args,
                },
            },
        ],
        # THE REALLY IMPORTANT PART TO BE ABLE TO RUN IN ANSIBLE >=2.17.1.
        "environment": self.environment_vars
    }

    play = Play().load(
        play_ds,
        variable_manager=self.options["variable_manager"],
        loader=self.options["loader"],
    )
    play_extra = None
    if self.options.get("extra_inventory_manager", None):
        play_extra = Play().load(
            play_ds,
            variable_manager=self.options["extra_variable_manager"],
            loader=self.options["extra_loader"],
        )

    if HAS_CUSTOM_LOADER_SUPPORT:
        # Load the collection finder, unsupported, may change in future
        init_plugin_loader(COLLECTIONS_PATHS)

    # now create a task queue manager to execute the play
    tqm = None
    try:
        tqm = TaskQueueManager(**kwargs)
        tqm.run(play)
    finally:
        if tqm:
            tqm.cleanup()

    if self.options.get("extra_inventory_manager", None):
        tqm_extra = None
        try:
            tqm_extra = TaskQueueManager(**kwargs_extra)
            tqm_extra.run(play_extra)
        finally:
            if tqm_extra:
                tqm_extra.cleanup()

    # Raise exception if host(s) unreachable
    if callback.unreachable:
        msg = "Host unreachable in the inventory"
        raise AnsibleConnectionFailure(
            msg,
            dark=callback.unreachable,
            contacted=callback.contacted,
        )
    if self.options.get("extra_inventory_manager", None) and callback_extra.unreachable:
        raise AnsibleConnectionFailure(  # noqa: TRY003
            "Host unreachable in the extra inventory",  # noqa: EM101
            dark=callback_extra.unreachable,
            contacted=callback_extra.contacted,
        )

    return AdHocResult(
        contacted=(
            {**callback.contacted, **callback_extra.contacted}
            if self.options.get("extra_inventory_manager", None)
            else callback.contacted
        ),
    )


class ZTestHelper(object):
    """ ZTestHelper provides helper methods to deal with added complexities when testing against a z/OS system. """

    def __init__(self, host, user, python_path, environment, **extra_args):
        self._host = host
        self._user = user
        self._python_path = python_path
        self._environment = environment
        self._extra_args = extra_args

    @classmethod
    def from_yaml_file(cls, path):
        """ Reads arguments from a YAML file to create an instance of ZTestHelper.  """
        testvars = {}
        with open(path, "r") as varfile:
            testvars = safe_load(varfile)
        return cls(**testvars)

    @classmethod
    def from_args(cls, src):
        """
        ZTestHelper provides helper methods to deal with added complexities when testing against a z/OS system.
        Similar to method `from_yaml_file(path)`, this method takes a dictionary of required keywords instead
        of dictionary from a file so to increase performance.

        Args:
            src - (dictionary) with keywords {'host': 'required', 'user': 'required', 'zoau': 'required', 'pyz': 'required', 'pythonpath': 'required', 'extra_args': 'optional'}"
                host - z/OS managed node
                user - user/omvs segment authorized to run ansible playbooks
                zoau - home directory where z Open Automation Utilities is installed
                pyz - python home
                pythonpath - environment variable that is used to specify the location of Python libraries, eg ZOAU python modules
                extra_args - dictionary used to include properties such as 'volumes' or other dynamic content.

        Code Example:
            if request.config.getoption("--zinventory-raw"):
                src = request.config.getoption("--zinventory-raw")
                helper = ZTestHelper.from_args(src)
                interpreter_str = helper.build_interpreter_string()
                inventory = helper.get_inventory_info()
                python_path = helper.get_python_path()
        Shell example with pytest:
            pytest tests/functional/modules/test_zos_mount_func.py::test_basic_mount --host-pattern=all -s -v --zinventory-raw='{"host": "zvm.ibm.com", "user": "ibmuser", "zoau": "/zoau/v1.3.1", "pyz": "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz", "pythonpath": "/zoau/v1.3.1/lib/3.10", "extra_args":{"volumes":["222222","000000"],"other":"something else"}}' -s

        {
            "host":"zvm.ibm.com",
            "user":"ibmuser",
            "zoau":"/zoau/v1.3.1",
            "pyz":"/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz",
            "pythonpath": "/zoau/v1.3.1/lib/3.10",
            "extra_args":{
                "volumes":[
                    "vol1",
                    "vol2"
                ],
                "other": "something else" }
        }
        """
        #TODO: add support for a positional string, eg "host,user,zoau,pyz" then convert it as needed

        host, user, zoau, pyz, pythonpath, extra_args = None, None, None, None, None, None

        src = json.loads(src)
        # Traverse the src here , can we trow an exception?
        for key, value in src.items():
            if key == "host":
                host = value
            elif key == "user":
                user = value
            elif key == "zoau":
                zoau = value
            elif key == "pyz":
                pyz = value
            elif key == "pythonpath":
                pythonpath = value
            elif key == "extra_args":
                extra = value

        for prop in [host, user, zoau, pyz, pythonpath]:
            if prop is None:
                message = f"Invalid value for use with keyword, the value must not be None"
                raise ValueError(message)

        environment_vars = dict()
        environment_vars.update({'_BPXK_AUTOCVT': 'ON'})
        environment_vars.update({'_CEE_RUNOPTS': '\'FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)\''})
        environment_vars.update({'_TAG_REDIR_IN': 'txt'})
        environment_vars.update({'_TAG_REDIR_OUT': 'txt'})
        environment_vars.update({'LANG': 'C'})
        environment_vars.update({'ZOAU_HOME': zoau})
        environment_vars.update({'LIBPATH': f"{zoau}/lib:{pyz}/lib:/lib:/usr/lib:."})
        environment_vars.update({'PYTHONPATH': f"{pythonpath}"}) # type: ignore
        environment_vars.update({'PATH': f"{zoau}/bin:{pyz}/bin:/bin:/usr/sbin:/var/bin"})
        environment_vars.update({'PYTHONSTDINENCODING': 'cp1047'})

        testvars = dict()
        testvars.update({'host': host})
        testvars.update({'user': user})
        testvars.update({'python_path': f"{pyz}/bin/python3"})
        testvars.update({'environment': environment_vars})

        if(extra):
            extra_args = dict()
            extra_args.update(extra)
            testvars.update(extra_args)

        return cls(**testvars)

    def get_inventory_info(self):
        """ Returns dictionary containing basic info needed to generate a single-host inventory file. """
        inventory_info = {
            "user": self._user,
            "inventory": "{0},".format(self._host),
        }
        inventory_info.update(self._extra_args)
        return inventory_info

    def build_interpreter_string(self):
        """ Builds wrapper to be used for python calls in pytest fixtures with needed environment variables.
        This is useful in situations where no environment variables are assumed to be set. """
        interpreter_string = ""
        for key, value in self._environment.items():
            interpreter_string += "export {0}={1} ; ".format(key, value)
        interpreter_string += self._python_path
        return interpreter_string

    def get_python_path(self):
        """ Returns python path """
        return self._python_path

    def get_extra_args(self) -> dict:
        """ Extra args dictionary """
        return self._extra_args

    def get_extra_args(self, key: str):
        """ Extra args dictionary """
        return self._extra_args.get(key) or self._extra_args.get(key.lower())

    def get_volumes_list(self) -> list[str]:
        """ Get volumes as a list if its been defined in extra args"""
        for key, value in self._extra_args.items():
            if key.lower() == "volumes":
                if not isinstance(value, list):
                    message = f"Invalid value for use with property [{key}], value must be type list[]."
                    raise ValueError(message)
                return value
