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
    - A unique and a Fully Qualified Name (FQN) of a 1-OS zfs aggregate data set, or
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
      - The approximate size, of the data set after the resizing is performed.
    type: int
    required: True
    size_type:
  size_type:
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
  noai:
    description:
      - Option to not allow automatic increase on shrinking process.
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
- name: Resize an aggregate data set to 4 megabytes (4,096 Kb).
  zos_resize:
    target: SOMEUSER.VVV.ZFS
    size: 4096
"""

RETURN = r"""
target:
    description:
        - The Fully Qualified Name of zfs data set that is to be resized.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
mount_target:
    description:
        - The original share/mount name provided.
    returned: always
    type: str
    sample: SOMEUSER.VVV.ZFS
size:
    description:
        - The approximate size, in Kilobytes, of the data set after the resizing is performed.
    returned: always
    type: int
    sample: 4024
cmd:
    description: The actual zosadm command that was attempted.
    returned: always
    type: str
    sample: zfsadm grow -aggregate SOMEUSER.VVV.ZFS -size 4096
rc:
    description: The return code of the zfsadm command.
    returned: always
    type: int
    sample: 0
oldsize:
    description:
        - The reported size, in Kilobytes, of the data set before the resizing is performed.
    returned: always
    type: int
    sample: 3096
oldfree:
    description:
        - The reported size, in 8K blocks, of the free space in the data set before the resizing is performed.
    returned: always
    type: int
    sample: 108
newsize:
    description:
        - The reported size, in Kilobytes, of the data set after the resizing is performed.
    returned: success
    type: int
    sample: 4032
newfree:
    description:
        - The reported size, in 8K blocks, of the free space in the data set after the resizing is performed.
    returned: success
    type: int
    sample: 48
"""

import re
import os
import tempfile
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils.import_handler import (
    ZOAUImportError,
)
from ansible_collections.ibm.ibm_zos_core.plugins.module_utils import (
    better_arg_parser,
    data_set,
)

try:
    from zoautil_py import MVSCmd as mvscmd
except Exception:
    mvscmd = ZOAUImportError(traceback.format_exc())


def get_agg_size(data_set, module):
    size = 0
    free = 0
    cmd = "zfsadm aggrinfo {0}".format(data_set.upper())

    rc, stdout, stderr = module.run_command(cmd)

    if rc == 0:
        searchstr = r"^\s*Size:\s*([0-9]*)K\s*Free\s8K\sBlocks:\s*([0-9]*)"
        found = re.search(searchstr, stdout, re.MULTILINE | re.DOTALL)
        if found is not None:
            size = found.group(1).strip()
            free = found.group(2).strip()

    return(size, free)


def calculate_size_on_k(size, size_type):
    if size_type == "m":
        size *= 1000
    if size_type == "g":
        size *= 1000000
    if size_type == "cyl":
        size *= 720
    if size_type == "trk":
        size *= 48
    return size


def execute_zfsadm(dataset, module, size, grow=False, shrink=False, noai=False, verbose=False):
    output = ""

    execute = "grow" if grow else "shrink" if shrink else module.fail_json(msg="Required a size that allow perform an option")
    noai = "-noai" if noai else ""

    if verbose:
        temp = tempfile.NamedTemporaryFile(delete=False)
        trace = "-trace {0}".format(temp.name)
    else:
        trace = ""

    cmd = "zfsadm {0} -aggregate {1} -size {2} {3} {4}".format(execute, dataset.upper(), size, noai, trace)
    if verbose:
        cmd_verbose = "cat {0}".format(temp.name)
        rc_cat, output, stderr_cat = module.run_command(cmd_verbose)
        os.unlink(temp.name)

    rc, stdout, stderr = module.run_command(cmd)

    return rc, stdout, stderr, output, cmd


def found_mount_target(module, target):
    rc, stdout, stderr = module.run_command("df")
    found = False
    if rc == 0:
        stdout_lines = stdout.split("\n")
        #module.fail_json(msg="{0} \n {1}".format(target, str(stdout_lines)))
        for line in stdout_lines:
            if len(line) > 2:
                columns = line.split()
                if target in columns[1]:
                    new_target = columns[1].strip("\t\n\r\')(")
                    target = new_target
                    mount_point = columns[0]
                    found = True
                    break
        if found is False:
            module.fail_json(msg="Resize: could not locate {0}".format(target),
                stderr="No error reported: string not found." )
    return target, mount_point


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            target=dict(type="str", required=True),
            size=dict(type="int", required=True),
            size_type=dict(
                    type="str",
                    required=False,
                    choices=["k", "m", "g", "cyl", "trk"],
                    default="k",
                ),
            noai=dict(type="bool", required=False, default=False),
            verbose=dict(type="bool", required=False, default=False),
        ),
        supports_check_mode=False
    )
    args_def = dict(
        target=dict(type="data_set", required=True),
        size=dict(type="int", required=True),
        size_type=dict(
                type="str",
                required=False,
                choices=["k", "m", "g", "cyl", "trk"],
                default="k",
            ),
        noai=dict(type="bool", required=False, default=False),
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
    size_type = module.params.get("size_type")
    noai = module.params.get("noai")
    verbose = module.params.get("verbose")
    changed = False

    target, mount_target = found_mount_target(module=module, target=target)

    old_size, old_free = get_agg_size(data_set=target, module=module)
    old_size, old_free = int(old_size), int(old_free)

    res_args.update(
        dict(
            target=target,
            mount_target=mount_target,
            size=size,
            cmd="",
            changed=changed,
            rc=0,
            stdout="",
            stderr="",
        )
    )

    if size_type != "k":
        size = calculate_size_on_k(size=size, size_type=size_type)

    grow, shrink = False, False
    minimum_size_t_shrink = old_size - old_free

    if size == old_size:
        module.fail_json(msg="Same size declared with the size of the zfz")
    elif size > old_size:
        grow, shrink = True, False
    elif size >= minimum_size_t_shrink and size < old_size:
        shrink, grow = True, False
    else:
        module.fail_json(msg="Error code 119 not enough space to shrink")

    rc, stdout, stderr, output, cmd = execute_zfsadm(dataset=target, module=module, size=size, grow=grow,
                                                shrink=shrink, noai=noai, verbose=verbose)

    if rc == 0:
        new_size, new_free = get_agg_size(data_set=target, module=module)
        new_size, new_free = int(new_size), int(new_free)
        changed = True
    else:
        module.fail_json(
            msg="Resize: resize command returned non-zero code: rc=" +
            str(rc) + ".",
            stderr=str(res_args)
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
