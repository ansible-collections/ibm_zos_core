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
---
module: zos_resize
author:
    - "Rich Parker (@richp405)"
    - "Marcel Gutierrez (@andre.marcel.gutierre)"
short_description: Resize a zfs data set.
description:
  - The module M(zos_resize) can resize a zfs aggregate data set.
  - The I(target) data set must be either:
    - A unique and a Fully Qualified Name (FQN) of a 1-OS zfs aggregate data set.
    - A full path of a mount point, which will be used to look up the data set's FQDN.
  - The data set must be attached read-write, and contain only one Operating system.
  - I(size) in K must be provided.
options:
  target:
    description:
      - The Fully Qualified Name of zfs data set that is to be resized.
    type: str
    required: true
  size:
    description:
      - The approximate size of the data set after the resizing is performed.
    type: int
    required: True
  space_type:
    description:
      - The unit of measurement to use when defining the size.
      - Valid units of size are C(k), C(m), C(g), C(cyl), and C(trk).
    type: str
    choices:
      - k
      - m
      - g
      - cyl
      - trk
    required: false
    default: k
  no_auto_increment:
    description:
      - Option to not allow auto increase on shrinking process.
      - If set to C(true), in the process of shrinking a zfs data set if a new file or
        folder is create or added to the point and its over the new size the process will fail.
    type: bool
    required: false
    default: false
  verbose:
    description:
      - Determines if verbose output should be returned from the underlying utility used by this module.
      - When I(verbose=true) verbose output is returned on module failure.
    required: false
    type: bool
    default: false
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
    description:
        - The Fully Qualified Name of the resized zfs data set.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_target:
    description:
        - The original share/mount name provided.
    returned: always
    type: str
    sample: /tmp/zfs_agg
size:
    description:
        - The approximate size, in Kilobytes, of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
old_size:
    description:
        - The reported size, in Kilobytes, of the data set before the resizing is performed.
    returned: always
    type: int
    sample: 3096
old_free:
    description:
        - The reported size, in Kilobytes, of the free space in the data set before the resizing is performed.
    returned: always
    type: int
    sample: 108
new_size:
    description:
        - The reported size, in Kilobytes, of the data set after the resizing is performed.
    returned: success
    type: int
    sample: 4032
new_free:
    description:
        - The reported size, in Kilobytes, of the free space in the data set after the resizing is performed.
    returned: success
    type: int
    sample: 48
verbose_output:
    description:
        - If C(verbose=true) the full traceback of operation will show on this variable.
    returned: C(verbose=true) and success
    type: str
    sample: 6FB2F8 print_trace_table: printing contents of table: Main Trace Table
"""

import os
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.zfsadm import zfsadm
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
)


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
        size *= 849960
    if space_type == "trk":
        size *= 56664
    return size


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

    os.remove(file)

    return output


def get_size_and_free(string):
    """Function to parsing the response of get aggregation size.

    Parameters
    ----------
        string : str
            stout of the get aggregation size function

    Returns
    -------
        numbers[1] : int
            Size on kilobytes of the zfs

        numbers[0] : int
            Total free on kilobytes of the zfs
    """
    numbers = [int(word) for word in string.split() if word.isdigit()]
    return numbers[1], numbers[0]


def found_mount_target(module, target):
    """Execute df command to access the information of mount points.

    Parameters
    ----------
        module : object
            Ansible object to execute commands.
        target : str
            ZFZ to check

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
            module.fail_json(msg="Resize: could not locate {0}".format(target),
                stderr="No error reported: string not found." )
    return mount_point


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

    res_args = dict()
    target = module.params.get("target")
    size = module.params.get("size")
    space_type = module.params.get("space_type")
    noai = module.params.get("no_auto_increment")
    verbose = module.params.get("verbose")
    changed = False

    #Validation to found target on the system and also get the mount_point
    mount_target = found_mount_target(module=module, target=target)

    #Initialize the class with the target
    aggregate_name = zfsadm(aggregate_name=target, module=module)

    rc, stdout, stderr = aggregate_name.get_aggregate_size()

    if rc == 0:
        old_size, old_free = get_size_and_free(string=stdout)

    res_args.update(
        dict(
            target=target,
            mount_target=mount_target,
            old_size=old_size,
            old_free=old_free,
            size=size,
            cmd="",
            changed=changed,
            rc=0,
            stdout="",
            stderr="",
        )
    )

    if space_type != "k":
        size = calculate_size_on_k(size=size, space_type=space_type)

    #Validations to know witch function will be execute
    operation = ""
    minimum_size_t_shrink = old_size - old_free

    if size == old_size:
        module.fail_json(msg="Same size declared with the size of the zfz")
    elif size > old_size:
        operation = "grow"
    elif size >= minimum_size_t_shrink and size < old_size:
        operation = "shrink"
    else:
        module.fail_json(msg="Error code 119 not enough space to shrink")

    noai = " -noai " if noai else ""

    if verbose:
        temp = tempfile.NamedTemporaryFile(dir=module._remote_tmp, delete=False)
        tmp_file = temp.name
        trace = " -trace '{0}'".format(tmp_file)
    else:
        trace = ""
        tmp_file = ""

    #Execute the function
    rc, stdout, stderr, cmd = aggregate_name.execute_resizing(operation=operation, size=size, noai=noai, verbose=trace)

    if rc == 0:
        changed = True

        rc_size, stdout_size, stderr_size = aggregate_name.get_aggregate_size()
        if rc_size == 0:
            new_size, new_free = get_size_and_free(string=stdout_size)

        if verbose:
            output = get_full_output(file=tmp_file, module=module)
            res_args.update(
                verbose_output=output,
            )
    else:
        if verbose:
            os.remove(tmp_file)
        module.fail_json(
            msg="Resize: resize command returned non-zero code: rc=" +
            str(rc) + ".",
            stderr=str(stderr)
        )

    res_args.update(
        dict(
            cmd=cmd,
            rc=rc,
            stdout=stdout,
            stderr=stderr,
            changed=changed,
            new_size=new_size,
            new_free=new_free,
        )
    )

    module.exit_json(**res_args)

def main():
    run_module()


if __name__ == '__main__':
    main()
