#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2024
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

class zfsadm:
    """Provides an interface to execute zfsadm commands.
    """
    def __init__(self, aggregate_name, module):
        """Initialize a class with its zfs dataset and allow modules to be executed.
        Parameters
        ----------
            aggregate_name : str
                Name of the zfs dataset.
            module : object
                Ansible object to execute commands.
        """
        self.aggregate_name = aggregate_name.upper()
        self.module = module


    def grow_shrink(self, grow, shrink, cmd):
        """Execute grow or shrink operation over a zfs dataset.

        Parameters
        ----------
            grow : bool
                If operation grow will be execute.
            shrink : bool
                If operation shrink will be execute.
            cmd : str
                Arguments to be added to the zfsadm -aggregate command"".

        Returns
        -------
            rc : int
                The rc of the execution of command.
            stdout : str
                The stout of the execution of command.
            stderr : str
                The stderr of the execution of command.
            cmd_str : str
                The full command that was execute.
        """
        execute = "grow" if grow else "shrink" if shrink else self.module.fail_json(msg="Required a size that allow perform an option")

        cmd_str = "zfsadm {0} -aggregate {1} {2}".format(execute, self.aggregate_name, cmd)

        rc, stdout, stderr = self.module.run_command(cmd_str)

        return rc, stdout, stderr, cmd_str


    def get_agg_size(self):
        """Execute a command to get the size of the zfs dataset.

        Returns
        -------
            rc : int
                The rc of the execution of command.
            stdout : str
                The stout of the execution of command
            stderr : str
                The stderr of the execution of command.
        """
        cmd = "zfsadm aggrinfo {0}".format(self.aggregate_name)

        rc, stdout, stderr = self.module.run_command(cmd)

        return rc, stdout, stderr

