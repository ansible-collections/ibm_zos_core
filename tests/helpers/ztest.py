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
            src - (dictionary) with keywords {'host': 'required', 'user': 'required', 'zoau': 'required', 'pyz': 'required'}"
                host - z/OS managed node
                user - user/omvs segment authorized to run ansible playbooks
                zoau - home directory where z Open Automation Utilities is installed
                pyz - python home

        Code Example:
            if request.config.getoption("--zinventory-raw"):
                src = request.config.getoption("--zinventory-raw")
                helper = ZTestHelper.from_args(src)
                interpreter_str = helper.build_interpreter_string()
                inventory = helper.get_inventory_info()
                python_path = helper.get_python_path()
        Shell example with pytest:
            pytest tests/functional/modules/test_zos_operator_func.py --host-pattern=all --zinventory-raw='{"host": "some.host.location.ibm.com", "user": "ibmuser", "zoau": "/zoau/v1.3.1", "pyz": "/allpython/3.10/usr/lpp/IBM/cyp/v3r10/pyz"}'
        """

        #TODO: add support for extra_args
        #TODO: add support for a positional string, eg "host,user,zoau,pyz" then convert it as needed
        #TODO: add some exception handling
        #TODO: Consider a template for the below content instead of hard coded template, something that
        #      will be easy to align to wheels and precompiled binaries.

        src = json.loads(src)
        host = src.get("host")
        user = src.get("user")
        zoau = src.get("zoau")
        pyz = src.get("pyz")

        environment_vars = dict()
        environment_vars.update({'_BPXK_AUTOCVT': 'ON'})
        environment_vars.update({'_CEE_RUNOPTS': '\'FILETAG(AUTOCVT,AUTOTAG) POSIX(ON)\''})
        environment_vars.update({'_TAG_REDIR_IN': 'txt'})
        environment_vars.update({'_TAG_REDIR_OUT': 'txt'})
        environment_vars.update({'LANG': 'C'})
        environment_vars.update({'ZOAU_HOME': zoau})
        environment_vars.update({'LIBPATH': f"{zoau}/lib:{pyz}/lib:/lib:/usr/lib:."})
        environment_vars.update({'PYTHONPATH': f"{zoau}/lib"})
        environment_vars.update({'PATH': f"{zoau}/bin:{pyz}/bin:/bin:/usr/sbin:/var/bin"})
        environment_vars.update({'PYTHONSTDINENCODING': 'cp1047'})

        testvars = dict()
        testvars.update({'host': host})
        testvars.update({'user': user})
        testvars.update({'python_path': f"{pyz}/bin/python3"})
        testvars.update({'environment': environment_vars})
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
