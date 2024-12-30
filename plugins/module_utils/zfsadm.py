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

    def execute_resizing(self, operation, size, noai, verbose):
        """Execute a grow or shrink operation on a zfs dataset.

        Parameters
        ----------
            operation : str
                Whether the operation to execute is grow or shrink
            size : int
                Size to be assigned to the zfs
            noai : str
                Command str if there will be activate no auto increase option
            verbose : str
                Command str with the file to get traceback

        Returns
        -------
            rc : int
                The rc of the execution of command.
            stdout : str
                The stdout of the execution of command.
            stderr : str
                The stderr of the execution of command.
            cmd_str : str
                The full command that was executed.
        """
        cmd = "-size {0}{1}{2}".format(size, noai, verbose)
        cmd_str = "zfsadm {0} -aggregate {1} {2}".format(operation, self.aggregate_name, cmd)

        rc, stdout, stderr = self.module.run_command(cmd_str)

        return rc, stdout, stderr, cmd_str

    @staticmethod
    def get_aggregate_size(aggregate_name, module):
        """Execute a command to get the size of the zfs dataset.

        Returns
        -------
            rc : int
                The rc of the execution of command.
            stdout : str
                The stdout of the execution of command
            stderr : str
                The stderr of the execution of command.
        """
        cmd = "zfsadm aggrinfo {0}".format(aggregate_name)

        rc, stdout, stderr = module.run_command(cmd)

        return rc, stdout, stderr
