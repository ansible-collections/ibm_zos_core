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

# ? should we just use yaml and accept the unordered dict?
# * oyaml is a drop-in replacement for pyyaml that preserves dict
# * ordering, this is useful in our use case since we define environment variables as
# * a list of key:value pairs. This resolves issues reading environment variables
# * that depend other environment variables defined earlier in the environment variable list.
# when using python versions >= 3.7, dict ordering is preserved by default so pyyaml can be used
from oyaml import safe_load

# TODO: Add/enhance error handling


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
        environment_vars.update({'_CEE_RUNOPTS': 'FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)'})
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
