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

DOCUMENTATION = r"""
module: zos_resize
short_description: Resize a zfs data set.
description:
  - The module M(zos_resize) can resize a zfs aggregate data set.
  - The I(target) data set must be a unique and a Fully Qualified Name (FQN) of a 1-OS zfs aggregate data set.
  - The data set must be attached read-write, and contain only one Operating system.
  - I(size) must be provided.
author:
  - "Rich Parker (@richp405)"
  - "Marcel Gutierrez (@andre.marcel.gutierre)"
options:
  target:
    description:
      - The Fully Qualified Name of zfs data set that is to be resized.
    required: true
    type: str
  size:
    description:
      - The approximate size of the data set after the resizing is performed.
    required: True
    type: int
  space_type:
    description:
      - The unit of measurement to use when defining the size.
      - Valid units of size are C(k), C(m), C(g), C(cyl), and C(trk).
      - k for kilobytes, m for megabytes, g for gigabytes, cyl for cylinder and trk for track
    required: false
    type: str
    choices:
      - k
      - m
      - g
      - cyl
      - trk
    default: k
  no_auto_increment:
    description:
      - Option to not allow auto increase on shrinking process.
      - When set to C(true), If during the shrinking process of a zfs aggregate more space is needed
        the new total size is not to be increased and the module will fail.
    required: false
    type: bool
    default: false
  verbose:
    description:
      - Determines if verbose output should be returned from the underlying utility used by this module.
      - When I(verbose=true) verbose output is returned on module failure.
    required: false
    type: bool
    default: false
  trace_destination:
    description:
      - Determines the uss path or dataset to insert the full trace of operation.
      - Expected file created
      - Required verbose=true
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Resize an aggregate data set to 2500 Kilobytes.
  zos_zfs_resize:
    target: TEST.ZFS.DATA
    size: 2500
"""

RETURN = r"""
cmd:
    description: The zfsadm command executed on the remote node.
    returned: always
    type: str
    sample: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096
target:
    description: The Fully Qualified Name of the resized zfs data set.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_target:
    description: The original share/mount.
    returned: always
    type: str
    sample: /tmp/zfs_agg
size:
    description: The approximate size, of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
old_size:
    description: The reported size, in space_type, of the data set before the resizing is performed.
    returned: always
    type: int
    sample: 3096
old_free:
    description: The reported size, in space_type, of the free space in the data set before the resizing is performed.
    returned: always
    type: int
    sample: 108
new_size:
    description: The reported size, in space_type, of the data set after the resizing is performed.
    returned: success
    type: int
    sample: 4032
new_free:
    description: The reported size, in space_type, of the free space in the data set after the resizing is performed.
    returned: success
    type: int
    sample: 48
verbose_output:
    description: If C(verbose=true) the full traceback of operation will show on this variable. If C(trace) will return the data set or path name.
    returned: C(verbose=true) and success
    type: str
    sample: 6FB2F8 print_trace_table printing contents of table Main Trace Table
"""

import os
import tempfile
import math
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
)

from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zfsadm import zfsadm


def calculate_size_on_k(size, space_type):
    """Function to convert size depending on the space_type.

    Parameters
    ----------
        size : int
            Size to grow or shrink the zfs
        space_type : str
            Type of space to be use

    Returns
    -------
        size : int
            Size on kilobytes
    """
    if space_type == "m":
        size *= 1024
    if space_type == "g":
        size *= 1048576
    if space_type == "cyl":
        size *= 830
    if space_type == "trk":
        size *= 55
    return math.ceil(size)


def get_full_output(file, module):
    """Function to get the verbose output and delete the tmp file

    Parameters
    ----------
        file : str
            Name of the tmp file where the full verbose output is store
        module : object
            Ansible object to execute commands.

    Returns
    -------
        output : str
            Verbose output
    """
    output = ""
    cmd = "cat '{0}'".format(file)
    rc, output, stderr = module.run_command(cmd)
    if rc != 0:
        output = "Unable to obtain full output for verbose mode."


    return output


def get_size_and_free(line):
    """Function to parsing the response of get aggregation size.

    Parameters
    ----------
        line : str
            stout of the get aggregation size function

    Returns
    -------
        numbers[1] : int
            Size on kilobytes of the zfs

        numbers[0] : int
            Total free on kilobytes of the zfs
    """
    numbers = [int(word) for word in line.split() if word.isdigit()]
    return numbers[1], numbers[0]


def find_mount_target(module, target):
    """Execute df command to access the information of mount points.

    Parameters
    ----------
        module : object
            Ansible object to execute commands.
        target : str
            ZFS to check.

    Returns
    -------
        mount_point : str
            The folder where the zfs is mount
    """
    rc, stdout, stderr = module.run_command("df")
    found = False
    if rc == 0:
        stdout_lines = stdout.split("\n")
        for line in stdout_lines:
            if len(line) > 2:
                columns = line.split()
                if target in columns[1]:
                    mount_point = columns[0]
                    found = True
                    break
        if found is False:
            module.fail_json(msg="No mount points were found in the following output: {0}".format(stdout))
    return mount_point


def convert_size(size, space_type):
    """Function to convert size from kb to the space_type.

    Parameters
    ----------
        size : int
            Size to grow or shrink the zfs
        space_type : str
            Type of space to be use

    Returns
    -------
        size : int
            Size on kilobytes
    """
    if space_type == "m":
        size /= 1024
    if space_type == "g":
        size /= 1048576
    if space_type == "cyl":
        size /= 830
    if space_type == "trk":
        size /= 55
    return size


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            target=dict(type="str", required=True),
            size=dict(type="int", required=True),
            space_type=dict(
                    type="str",
                    required=False,
                    choices=["k", "m", "g", "cyl", "trk"],
                    default="k",
                ),
            no_auto_increment=dict(type="bool", required=False, default=False),
            verbose=dict(type="bool", required=False, default=False),
            trace_destination=dict(type="str", required=False),
        ),
        supports_check_mode=False
    )
    args_def = dict(
        target=dict(type="data_set", required=True),
        size=dict(type="int", required=True),
        space_type=dict(
                type="str",
                required=False,
                choices=["k", "m", "g", "cyl", "trk"],
                default="k",
            ),
        no_auto_increment=dict(type="bool", required=False, default=False),
        verbose=dict(type="bool", required=False, default=False),
        trace_destination=dict(type="data_set_or_path", required=False
            ),
    )

    try:
        parser = better_arg_parser.BetterArgParser(args_def)
        parsed_args = parser.parse_args(module.params)
        module.params = parsed_args
    except ValueError as err:
        module.fail_json(
            msg='Parameter verification failed.',
            stderr=str(err)
        )

    result = dict()
    target = module.params.get("target")
    size = module.params.get("size")
    space_type = module.params.get("space_type")
    noai = module.params.get("no_auto_increment")
    verbose = module.params.get("verbose")
    trace_destination = module.params.get("trace_destination")

    if not(verbose) and trace_destination is not None:
        raise ResizingOperationError(msg="If you want the full traceback on a file or dataset required verbose=True")

    changed = False
    #Variables to return the value on the space_type by the user
    size_on_type = ""
    free_on_type = ""

    #Validation to found target on the system and also get the mount_point
    mount_target = find_mount_target(module=module, target=target)

    #Initialize the class with the target
    zfsadm_obj = zfsadm(aggregate_name=target, module=module)

    rc, stdout, stderr = zfsadm_obj.get_aggregate_size()

    if rc == 0:
        old_size, old_free = get_size_and_free(line=stdout)

    if space_type != "k":
        space = calculate_size_on_k(size=size, space_type=space_type)
    else:
        space = size

    #Validations to know witch function will be execute
    operation = ""
    minimum_size_t_shrink = old_size - old_free

    if space_type != "k":
        size_on_type = convert_size(size=old_size, space_type=space_type)
        free_on_type = convert_size(size=old_size, space_type=space_type)

    str_old_size = old_size if space_type == "k" else size_on_type
    str_old_size = "{:.1f}".format(str_old_size) + " {0}".format(space_type)
    str_old_free = old_free if space_type == "k" else free_on_type
    str_old_free = "{:.1f}".format(str_old_free) + " {0}".format(space_type)

    result.update(
        dict(
            target=target,
            mount_target=mount_target,
            old_size=str_old_size,
            old_free=str_old_free,
            size=size,
            cmd="",
            changed=changed,
            rc=0,
            stdout="",
            stderr="",
        )
    )

    if space == old_size:
        result.update(
        dict(
            cmd="",
            rc=0,
            stdout="Same size as size of the file {0}".format(target),
            stderr="",
            changed=False,
            size=size,
            new_size=str_old_size,
            new_free=str_old_free,
            )
        )
        module.exit_json(**result)

    elif space > old_size:
        operation = "grow"

    elif space >= minimum_size_t_shrink and space < old_size:
        operation = "shrink"

    else:
        raise ResizingOperationError(msg="Not enough space to grow.")

    noai = " -noai " if noai else ""

    if verbose:
        if trace_destination is None:
            tmp_fld = os.path.expanduser(module._remote_tmp)
            temp = tempfile.NamedTemporaryFile(dir=tmp_fld, delete=False)
            tmp_file = temp.name
            trace = " -trace '{0}'".format(tmp_file)
        else:
            if "/" in trace_destination:
                if not(os.path.exists(trace_destination)):
                    raise ResizingOperationError(msg="Destination file does not exist")
            else:
                if not(data_set.DataSet.data_set_exists(trace_destination)):
                    raise ResizingOperationError(msg="Destination dataset does not exist")
            tmp_file = trace_destination
            trace = " -trace '{0}'".format(trace_destination)
    else:
        trace = ""
        tmp_file = ""

    #Execute the function
    rc, stdout, stderr, cmd = zfsadm_obj.execute_resizing(operation=operation, size=space, noai=noai, verbose=trace)

    if rc == 0:
        changed = True

        rc_size, stdout_size, stderr_size = zfsadm_obj.get_aggregate_size()
        if rc_size == 0:
            new_size, new_free = get_size_and_free(line=stdout_size)

        if space_type != "k":
            size_on_type = convert_size(size=new_size, space_type=space_type)
            free_on_type = convert_size(size=new_free, space_type=space_type)

        if verbose:
            if trace_destination is None:
                output = get_full_output(file=tmp_file, module=module)
                result.update(
                    verbose_output=output,
                )
                os.remove(tmp_file)
            else:
                result.update(
                    verbose_output=trace_destination,
                )

    else:
        if verbose and trace_destination is None:
            os.remove(tmp_file)

        raise ResizingOperationError(
            msg="Resize: resize command returned non-zero code",
            target=target,
            mount_target=mount_target,
            cmd=cmd,
            rc=rc,
            size=size,
            stdout=stdout,
            stderr=stderr,
            changed=False,
            old_size=str_old_size,
            old_free=str_old_free,
        )

    str_new_size = new_size if space_type == "k" else size_on_type
    str_new_size = "{:.1f}".format(str_new_size) + " {0}".format(space_type)
    str_new_free = new_free if space_type == "k" else free_on_type
    str_new_free = "{:.1f}".format(str_new_free) + " {0}".format(space_type)

    result.update(
        dict(
            cmd=cmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            changed=changed,
            new_size=str_new_size,
            new_free=str_new_free,
        )
    )

    module.exit_json(**result)


class ResizingOperationError(Exception):
    def __init__(
            self,
            msg,
            target="",
            mount_target="",
            size="",
            cmd="",
            rc="",
            stdout="",
            stderr="",
            changed=False,
            old_size="",
            old_free="",
        ):
        """Error in a copy operation.

        Parameters
        ----------
        msg : str
            Human readable string describing the exception.
        target : str
            The Fully Qualified Name of the resized zfs data set
        mount_target : str
            The original share/mount
        size : str
            The approximate size of the target
        rc : int
            Result code.
        stdout : str
            Standart output.
        stderr : str
            Standart error.
        cmd : str
            The zfsadm command try to execute on the remote node.
        changed : bool
            If the operation was executed.
        old_size : list
            The reported size, of the data set before the resizing is performed.
        old_free : list
            The reported size, of the free space in the data set before the resizing is performed.
        """
        self.json_args = dict(
            msg=msg,
            target=target,
            mount_target=mount_target,
            cmd=cmd,
            rc=rc,
            size=size,
            stdout=stdout,
            stderr=stderr,
            changed=changed,
            old_size=old_size,
            old_free=old_free,
        )
        super().__init__(self.msg)


def main():
    run_module()


if __name__ == '__main__':
    main()
